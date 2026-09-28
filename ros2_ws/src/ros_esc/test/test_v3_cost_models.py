"""Model-unit and numerical regression checks; these are not physical calibration."""

import math

import numpy as np
import pytest

# Normal object construction loads the shared parser before built-in modules.
from ros_esc.config_parsing import parse_object_config
from ros_esc.cost_function_node.cost_function_objects.cost_function_objects import (
    Multi_Light_Source_Cost, Photoresistor_Interpolated_Map, Position_Based_Sympy_Expression,
)
from ros_esc.cost_function_node.light_brightness import brightness_percent_to_lumens


def sensor_pose(x, y, angle):
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.array([[cosine, -sine, 0, x], [sine, cosine, 0, y],
                     [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)


@pytest.mark.parametrize("percent", [0.0, 0.2, 25.0, 33.333, 50.0, 100.0])
@pytest.mark.parametrize("mode", ["Voltage", "Resistance"])
def test_percentage_cost_matches_legacy_lumens_at_multiple_poses(percent, mode):
    """Nominal 16 lm/% changes input units, not the fitted sensor response."""
    def model(key, value):
        return Multi_Light_Source_Cost({"mode": mode, "light_sources": [{"x": 1., "y": .5, key: value}]})
    current, legacy = model("brightness_percent", percent), model("intensity_lumens", 16 * percent)
    for x, y, angle in [(0, 0, 0), (2, -1, 1.3), (.5, .2, math.pi)]:
        pose = sensor_pose(x, y, angle)
        assert current.cost_output(0., pose) == legacy.cost_output(0., pose)
    if percent == 0:
        dark = Multi_Light_Source_Cost({"mode": mode, "light_sources": []})
        assert current.cost_output(0., np.eye(4)) == dark.cost_output(0., np.eye(4))


@pytest.mark.parametrize("value", [-1, 100.001, float("nan"), float("inf"), float("-inf"), True, None, "bad"])
def test_invalid_percentage_rejected(value):
    with pytest.raises(ValueError, match="brightness_percent"):
        brightness_percent_to_lumens(value)


def test_ambiguous_units_rejected_and_high_legacy_lumens_preserved():
    with pytest.raises(ValueError, match="not both"):
        Multi_Light_Source_Cost({"light_sources": [{"x": 0, "y": 0, "brightness_percent": 25,
                                                  "intensity_lumens": 400}]})
    legacy = Multi_Light_Source_Cost({"light_sources": [{"x": 0, "y": 0, "intensity_lumens": 3000}]})
    assert legacy.light_sources[0]["intensity_lumens"] == 3000


@pytest.mark.parametrize("mode", ["Resistance", "Voltage"])
def test_photoresistor_score_uses_model_endpoints_and_rejects_nonfinite(mode):
    model = Photoresistor_Interpolated_Map({"mode": mode, "x_optimal": 1., "y_optimal": 2.})
    dark, near = float(model.max_value), float(model.min_value)
    if mode == "Voltage":
        dark, near = model.convert_resistance_to_voltage(dark), model.convert_resistance_to_voltage(near)
    assert model.source_score(dark) == pytest.approx(0.)
    assert model.source_score(near) == pytest.approx(1.)
    assert model.source_score((dark + near) / 2) == pytest.approx(.5)
    assert model.source_score(near + 10 * (near - dark)) == pytest.approx(1.)
    assert np.isnan(model.source_score(float("nan")))


def test_multi_light_score_does_not_use_source_positions_or_intensities():
    first = Multi_Light_Source_Cost({"light_sources": [{"x": 1., "y": 2., "intensity_lumens": 500.}]})
    second = Multi_Light_Source_Cost({"light_sources": [{"x": 9., "y": -4., "intensity_lumens": 5000.}]})
    cost = first._convert_resistance_to_voltage(1000.)
    assert first.source_score(cost) == second.source_score(cost)


@pytest.mark.parametrize(("lumens", "expected"), [(450., .7785034367102063), (800., .945004139473373),
                                                    (1200., 1.), (2500., 1.)])
def test_retained_multi_light_best_case_score_numerics(lumens, expected):
    model = Multi_Light_Source_Cost({"mode": "Voltage", "reference_intensity_lumens": 1000.,
                                   "light_sources": [{"x": 0., "y": 0., "intensity_lumens": lumens}]})
    assert model.source_score(model.cost_output(0., np.eye(4))) == pytest.approx(expected)


@pytest.mark.parametrize(("mode", "adc", "expected"), [
    ("Resistance", False, [29060.624686374733, 85270.21318970795, 216805.33437130036]),
    ("Resistance", True, [29060.624686374733, 85270.21318970795, 112199.44065183881]),
    ("Voltage", False, [-.05614035147626268, -.019275652927911, -.007598947471066631]),
    ("Voltage", True, [-.05614035147626268, -.019275652927911, -.014662829482153281]),
])
def test_original_main_photoresistor_numerics(mode, adc, expected):
    """Golden values from acb5902, including its inherited ADC approximation.

    Matching these values preserves old experiments; it does not validate
    that approximation as an Arduino transfer function.
    """
    model = Photoresistor_Interpolated_Map({"mode": mode, "x_optimal": 1., "y_optimal": .5, "apply_adc": adc})
    poses = [(0., 0., 0.), (2., -1., 1.3), (.5, .2, math.pi)]
    np.testing.assert_allclose([model.cost_output(.2, sensor_pose(*pose)) for pose in poses], expected,
                               rtol=1e-13, atol=1e-14)


def test_voltage_is_negative_cost_in_volts_and_resistance_is_positive_ohms():
    parameters = {"light_sources": [{"x": 1., "y": 0., "intensity_lumens": 1000.}]}
    resistance = Multi_Light_Source_Cost({**parameters, "mode": "Resistance"})
    voltage = Multi_Light_Source_Cost({**parameters, "mode": "Voltage"})
    facing, away = sensor_pose(0, 0, 0), sensor_pose(0, 0, math.pi)
    for pose in (facing, away):
        ohms = resistance.cost_output(0., pose)
        cost_volts = voltage.cost_output(0., pose)
        assert ohms > 0 and -5 <= cost_volts < 0
        assert cost_volts == pytest.approx(-5 / (ohms / 330 + 1))
    assert resistance.cost_output(0., facing) < resistance.cost_output(0., away)
    assert voltage.cost_output(0., facing) < voltage.cost_output(0., away)


def test_position_cost_retains_symbolic_value_and_unavailable_score():
    config = {"module": "ros_esc.cost_function_node.cost_function_objects.cost_function_objects",
              "object_name": "Position_Based_Sympy_Expression",
              "params": {"function": "x**2 + y**2", "symbols": ["t", "x", "y", "z"]}}
    model = parse_object_config(config)
    assert isinstance(model, Position_Based_Sympy_Expression)
    assert model.cost_output(7., sensor_pose(3., 4., .7)) == pytest.approx(25.)
    assert np.isnan(model.source_score(0.))
