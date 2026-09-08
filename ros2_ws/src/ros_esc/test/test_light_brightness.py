"""Percentage brightness is equivalent across simulation input paths."""

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

from builtin_interfaces.msg import Time
import numpy as np
import pytest
import yaml

from ros_esc.cost_function_node.cost_function_node_script import CostFunction
from ros_esc.cost_function_node.cost_function_objects.cost_function_objects import (
    Multi_Light_Source_Cost,
)
from ros_esc.cost_function_node.light_brightness import (
    brightness_percent_to_lumens,
)
from ros_esc.plotting_scripts import cost_surface_plotter as plotter
from ros_esc.scenario_runner.run_scenario import (
    build_launch_command,
    build_metadata,
)
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite


PACKAGE = Path(__file__).resolve().parents[1]
EXAMPLE = PACKAGE / (
    'ros_esc/scenario_runner/scenarios/brightness_percent_example.yaml'
)


@pytest.mark.parametrize('percent', [0.0, 0.2, 25.0, 33.333, 50.0, 100.0])
@pytest.mark.parametrize('mode', ['Voltage', 'Resistance'])
def test_percentage_cost_matches_legacy_at_multiple_poses(percent, mode):
    """Changing input units must not change the fitted sensor response."""
    def model(key, value):
        return Multi_Light_Source_Cost({
            'mode': mode,
            'light_sources': [{'x': 1.0, 'y': 0.5, key: value}],
        })
    new = model('brightness_percent', percent)
    old = model('intensity_lumens', 16.0 * percent)
    for x, y, angle in [(0, 0, 0), (2, -1, 1.3), (0.5, 0.2, 3.14)]:
        pose = plotter._create_transform(x, y, angle)
        assert new.cost_output(0.0, pose) == old.cost_output(0.0, pose)
    if percent == 0.0:
        dark = Multi_Light_Source_Cost({'mode': mode, 'light_sources': []})
        assert new.cost_output(0.0, np.eye(4)) == dark.cost_output(0.0, np.eye(4))


@pytest.mark.parametrize('value', [-1, 100.001, float('nan'), float('inf'),
                                  float('-inf'), True, None, 'bad'])
def test_invalid_percentage_rejected(value):
    with pytest.raises(ValueError, match='brightness_percent'):
        brightness_percent_to_lumens(value)


def test_config_rejects_dual_units_and_preserves_high_legacy_inputs():
    with pytest.raises(ValueError, match='not both'):
        Multi_Light_Source_Cost({'light_sources': [{
            'x': 0, 'y': 0, 'brightness_percent': 25, 'intensity_lumens': 400,
        }]})
    old = Multi_Light_Source_Cost({'light_sources': [{
        'x': 0, 'y': 0, 'intensity_lumens': 3000,
    }]})
    assert old.light_sources[0]['intensity_lumens'] == 3000


def test_cli_cost_event_and_plot_agree_on_percentage_override():
    args = plotter.build_parser().parse_args([
        str(PACKAGE / 'paper_recreations/heavy_ball_PDE_ESC/'
                       'cost_function/multi_light_source_photoresistor.json'),
        '--light_source_count', '1',
        '--light_source_1_x', '1.0', '--light_source_1_y', '0.5',
        '--light_source_1_intensity_lumens', '2500',
        '--light_source_1_brightness_percent', '25',
    ])
    plotted = plotter._load_cost_function(args.config, args)
    events = []
    sensor = SimpleNamespace(
        cost_function=Multi_Light_Source_Cost({}),
        observability_source_mode=1,
        cost_model_name='Multi_Light_Source_Cost',
        algorithm_event_publisher=SimpleNamespace(publish=events.append),
    )
    CostFunction.configure_light_source_cost(sensor, args)
    assert sensor.cost_function.light_sources == plotted.light_sources
    assert plotted.light_sources[0]['intensity_lumens'] == 400.0
    assert plotter._light_label(1, plotted.light_sources[0]) == 'L1: 25%'
    CostFunction.publish_configuration_events(sensor, Time())
    values = dict(zip(events[0].value_names, events[0].values))
    assert values['source_1_brightness_percent'] == 25.0
    assert values['source_1_relative_intensity_input'] == 400.0


def test_percentage_scenario_reaches_launch_and_metadata():
    runs, unsupported = expand_suite(load_suite(EXAMPLE))
    assert not unsupported
    assert len(runs) == 1
    run = runs[0]
    assert [s['relative_lumen_input'] for s in run['sources']] == [400, 1600]
    launch = build_launch_command(run)
    assert 'light_1_brightness_percent:=25.0' in launch
    assert 'light_2_brightness_percent:=100.0' in launch
    assert not any('intensity_lumens:=' in arg for arg in launch)
    metadata = build_metadata(run, 'test', 'brightness-interface', '')
    assert metadata['scenario_runner']['sources'] == run['sources']


def test_percentage_json_config_is_recorded_without_launch_overrides(tmp_path):
    template = PACKAGE / (
        'paper_recreations/heavy_ball_PDE_ESC/cost_function/'
        'multi_light_source_photoresistor.json'
    )
    config = json.loads(template.read_text())
    config['CostFunction']['params']['light_sources'] = [
        {'x': 1.0, 'y': 0.5, 'brightness_percent': 50.0},
    ]
    path = tmp_path / 'percent.json'
    path.write_text(json.dumps(config))
    args = plotter.build_parser().parse_args([str(path)])
    cost = plotter._load_cost_function(str(path), args)
    sensor = SimpleNamespace(cost_function=cost)
    CostFunction.configure_light_source_cost(sensor, args)
    assert sensor.configured_light_source_count == 1
    assert sensor.configured_light_sources[0]['brightness_percent'] == 50.0
    assert sensor.configured_light_sources[0]['intensity_lumens'] == 800.0


@pytest.mark.parametrize('value', [-1, 101, True, float('nan'), float('inf')])
def test_scenario_rejects_invalid_percentage(tmp_path, value):
    document = yaml.safe_load(EXAMPLE.read_text())
    document['cases'][0]['sources'][0]['brightness_percent'] = value
    path = tmp_path / 'invalid.yaml'
    path.write_text(yaml.safe_dump(document))
    with pytest.raises(ValueError):
        load_suite(path)


def test_scenario_rejects_dual_units_and_keeps_legacy_launch(tmp_path):
    document = yaml.safe_load(EXAMPLE.read_text())
    ambiguous = deepcopy(document)
    ambiguous['cases'][0]['sources'][0]['relative_lumen_input'] = 400
    path = tmp_path / 'scenario.yaml'
    path.write_text(yaml.safe_dump(ambiguous))
    with pytest.raises(ValueError, match='exactly one'):
        load_suite(path)
    for source in document['cases'][0]['sources']:
        source['relative_lumen_input'] = 16.0 * source.pop('brightness_percent')
    path.write_text(yaml.safe_dump(document))
    runs, _ = expand_suite(load_suite(path))
    assert 'light_1_intensity_lumens:=400.0' in build_launch_command(runs[0])
    assert 'brightness_percent' not in runs[0]['sources'][0]
