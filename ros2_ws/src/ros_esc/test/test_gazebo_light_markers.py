"""Gazebo light markers follow modeled sources without changing control input."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from ros_esc.profiles import resolve_profile

ROOT = Path(__file__).resolve().parents[4]
SIMULATION = ROOT / "ros2_ws/src/turtlebot3_rotating_sensor"
PROFILES = ROOT / "ros2_ws/src/ros_esc/config/profiles"


@pytest.fixture
def launch_module():
    pytest.importorskip("launch")
    spec = importlib.util.spec_from_file_location(
        "gazebo_light_launch", SIMULATION / "launch/gazebo.launch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _arguments(rows):
    return [dict(zip(row[::2], row[1::2])) for row in rows]


def test_v3_markers_use_selected_cost_positions_without_changing_inputs(launch_module, tmp_path):
    profile = resolve_profile("gesc_v3", directory=PROFILES)
    config = json.loads(Path(profile["config_paths"]["cost"]).read_text())
    config["CostFunction"]["params"]["light_sources"][0].update(x=-2.75, y=4.125)
    path = tmp_path / "custom_cost.json"
    path.write_text(json.dumps(config))
    profile["config_paths"]["cost"] = str(path)
    before = deepcopy(profile)
    commands_before = launch_module.algorithm_commands(profile)

    markers = _arguments(launch_module.light_marker_arguments(profile, SIMULATION))

    assert [(float(marker["-x"]), float(marker["-y"])) for marker in markers] == [
        (source["x"], source["y"]) for source in config["CostFunction"]["params"]["light_sources"]]
    assert [marker["-entity"] for marker in markers] == ["manual_light_1", "manual_light_2"]
    assert all(marker["-file"] == str(SIMULATION / "models/light_source/model.sdf") for marker in markers)
    assert profile == before
    assert launch_module.algorithm_commands(profile) == commands_before
    assert json.loads(path.read_text()) == config


@pytest.mark.parametrize("profile_name", ["adagrad_full_rotation_voltage", "adagrad_full_rotation_resistance"])
def test_legacy_photoresistor_marker_matches_its_cost_model(launch_module, profile_name):
    profile = resolve_profile(profile_name, directory=PROFILES)
    parameters = json.loads(Path(profile["config_paths"]["cost"]).read_text())["CostFunction"]["params"]
    markers = _arguments(launch_module.light_marker_arguments(profile, SIMULATION))
    assert len(markers) == 1
    assert float(markers[0]["-x"]) == parameters["x_optimal"]
    assert float(markers[0]["-y"]) == parameters["y_optimal"]


def test_acoustic_profile_has_no_light_markers(launch_module):
    profile = resolve_profile("gesc_full_rotation_acoustic", directory=PROFILES)
    assert launch_module.light_marker_arguments(profile, SIMULATION) == []


def test_launch_spawns_original_noncolliding_assets_in_gui_and_headless(launch_module, monkeypatch):
    from launch import LaunchContext
    from launch.utilities import perform_substitutions
    from launch_ros.actions import Node

    monkeypatch.setattr(launch_module, "get_package_share_directory", lambda _: str(SIMULATION))
    profile = resolve_profile("gesc_v3", directory=PROFILES)
    expected = _arguments(launch_module.light_marker_arguments(profile, SIMULATION))
    for gui in ("true", "false"):
        context = LaunchContext()
        context.launch_configurations.update(profile="gesc_v3", environment="gazebo",
                                             gui=gui, plot="false", record="false", output="/tmp/unused")
        commands = [[perform_substitutions(context, word) for word in action.cmd]
                    for action in launch_module._launch(context) if isinstance(action, Node)]
        markers = [command for command in commands if "-file" in command]
        assert len(markers) == 2
        for command, marker in zip(markers, expected):
            assert "spawn_entity.py" in command[0]
            assert command[command.index("-entity") + 1] == marker["-entity"]
            assert command[command.index("-x") + 1] == marker["-x"]
            assert command[command.index("-y") + 1] == marker["-y"]

    model = ET.parse(SIMULATION / "models/light_source/model.sdf").getroot()
    assert model.findtext("model/static") == "true"
    assert model.findall(".//visual") and model.findall(".//light")
    assert model.findall(".//collision") == []
