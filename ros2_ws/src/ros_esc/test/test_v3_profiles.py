"""Original profile parity and active launch contracts, without a ROS graph."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import subprocess

import numpy as np
import pytest

from ros_esc.config_parsing import parse_filter_config, parse_object_config
from ros_esc.profiles import available_profiles, resolve_profile

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "ros2_ws/src/ros_esc"
PROFILES = PACKAGE / "config/profiles"
SIMULATION = ROOT / "ros2_ws/src/turtlebot3_rotating_sensor"
ORIGINAL = "acb59020ac96d8ec67e8764092c6c51c01b7ea07"


def _json(path):
    return json.loads(Path(path).read_text())


def _old(path):
    return subprocess.check_output(["git", "show", f"{ORIGINAL}:{path}"], cwd=ROOT, text=True)


def _numeric(value):
    if isinstance(value, dict):
        return {k: _numeric(v) for k, v in value.items() if k not in ("module", "filepath")}
    if isinstance(value, list):
        return [_numeric(v) for v in value]
    return value


def _module_paths(value):
    """Turn module refs into original-compatible local files for parity tests."""
    if isinstance(value, list):
        return [_module_paths(v) for v in value]
    if not isinstance(value, dict):
        return value
    result = {k: _module_paths(v) for k, v in value.items() if k != "module"}
    if "module" in value:
        result["filepath"] = str(PACKAGE / (value["module"].replace(".", "/") + ".py"))
    return result


def test_original_aliases_retain_their_selected_numerical_configs():
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", ORIGINAL,
                                    "ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts"], cwd=ROOT, text=True).splitlines()
    keys = {"rotate_frame_config_filepath": "rotation", "sensor_transform_config_filepath": "sensor",
            "cost_function_config_filepath": "cost", "filter_config_filepath": "filter",
            "controller_config_filepath": "controller"}
    for script in (p for p in paths if p.endswith(".bash")):
        old_args = dict(re.findall(r"(\w+):=\s*'?([^\n]+?)'?\s*\\?$", _old(script), re.M))
        selected = resolve_profile(Path(script).stem, directory=PROFILES)
        for argument, role in keys.items():
            original_path = "ros2_ws/" + old_args[argument].split("/ros2_ws/")[1]
            # Two original scripts referenced absent names; use their existing
            # voltage controller files, not a guessed replacement algorithm.
            if original_path.endswith(("angular_tuning_controller.json", "lie_bracket_controller.json")):
                original_path = original_path[:-5] + "_voltage.json"
            assert _numeric(_json(selected["config_paths"][role])) == _numeric(json.loads(_old(original_path)))
        alias = ROOT / script
        assert alias.is_file()
        text = alias.read_text()
        assert f"profile:={Path(script).stem}" in text
        assert "colcon" not in text and "source " not in text
        assert len(text.splitlines()) <= 6


@pytest.mark.parametrize("profile", available_profiles(directory=PROFILES))
def test_installed_modules_match_custom_file_objects_without_mutating_inputs(profile):
    selected = resolve_profile(profile, directory=PROFILES)
    config = _json(selected["config_paths"]["controller"])
    before = deepcopy(config)
    module_object = parse_object_config(config)
    file_object = parse_object_config(_module_paths(config))
    assert config == before
    # Exercise actual numerical controller API across sequential timestamps.
    for t in (0.0, 0.2, 0.4):
        state = np.array([0.2, 0.4, 0, 0, 0, 0.3])
        # Adaptive methods consume [gradient(2), half-vectorized outer product(3)].
        # The inherited Lie-bracket implementation takes a scalar cost.
        inputs = (0.4 if profile == "lie_bracket" else
                  np.array([0.4, -0.2, 0.16, -0.08, 0.04]))
        np.testing.assert_allclose(module_object.controller_output(t, state, inputs),
                                   file_object.controller_output(t, state, inputs))


def test_filter_config_is_reusable_and_not_mutated():
    config = _json(resolve_profile("gesc_full_rotation_acoustic", directory=PROFILES)["config_paths"]["filter"])
    before = deepcopy(config)
    first, z1 = parse_filter_config(config, [])
    second, z2 = parse_filter_config(config, [])
    assert config == before
    assert z1 == z2
    np.testing.assert_allclose(first.filter_output(np.array(z1), np.array([-0.5, 0.7]), 0.2),
                               second.filter_output(np.array(z2), np.array([-0.5, 0.7]), 0.2))


def test_profiles_have_no_source_tree_paths_or_archived_algorithms():
    for profile in available_profiles(directory=PROFILES):
        selected = resolve_profile(profile, directory=PROFILES)
        assert selected["algorithm"] in ("legacy", "gesc_v3")
        for filename in selected["config_paths"].values():
            text = Path(filename).read_text()
            assert '"filepath"' not in text and "~/" not in text
    with pytest.raises(ValueError, match="unknown algorithm"):
        resolve_profile("gesc_gaussian_v2", directory=PROFILES)


def test_physical_profile_does_not_select_plotting_or_simulation_clock():
    resolved = resolve_profile("gesc_v3", "physical", directory=PROFILES)
    assert resolved["use_sim_time"] is False and resolved["plot"] is False
    assert resolved["topics"]["pose"] == "/odom"
    assert resolved["v3"]["sample_rate_hz"] == 5.0
    assert resolved["v3"]["arm_rpm"] == 20.0
    assert resolved["v3"]["encoder_offset_deg"] == 54.0
    # This portable development profile is not the installed physical V1.
    assert (resolved["v3"]["max_vx"], resolved["v3"]["max_wz"]) == (0.10, 0.50)
    assert resolved["v3"]["k_vx"] == .5
    controller = _json(resolved["config_paths"]["controller"])
    assert resolved["v3"]["k_vx"] == controller["gains"]["k_vx"]
    assert resolved["v3"]["max_vx"] == controller["params"]["set_max_vx"]
    resolved["v3"]["max_vx"] = 99
    assert resolve_profile("gesc_v3", "physical", directory=PROFILES)["v3"]["max_vx"] == .10


def test_v3_development_caps_match_archived_full_rotation_light_baseline():
    original_path = ("ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/"
                     "turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json")
    baseline = json.loads(subprocess.check_output(
        ["git", "show", f"archive/pre-v3-refactor-20260928:{original_path}"], cwd=ROOT, text=True))
    selected = resolve_profile("gesc_v3", directory=PROFILES)
    actual = parse_object_config(_json(selected["config_paths"]["controller"]))
    assert actual.max_vx == selected["v3"]["max_vx"] == baseline["params"]["set_max_vx"]
    assert actual.max_wz == selected["v3"]["max_wz"] == baseline["params"]["set_max_wz"]
    assert actual.k_vx == .5  # Match caps without silently doubling the gain.


def test_v3_direct_assistance_uses_controller_json_and_preserves_old_default(tmp_path):
    selected = resolve_profile("gesc_v3", directory=PROFILES)
    assert selected["v3"]["direct_escape_assistance_enabled"] is False
    assert selected["v3"]["escape_affine_magnitude"] == .5
    profile = _json(PROFILES / "algorithms.json")["gesc_v3"]
    profile["configs"] = dict(selected["config_paths"])
    controller = _json(profile["configs"]["controller"])
    path = tmp_path / "controller.json"
    profile["configs"]["controller"] = str(path)
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile))
    for enabled in (True, False, None):
        if enabled is None:
            controller["params"].pop("direct_escape_assistance_enabled")
        else:
            controller["params"]["direct_escape_assistance_enabled"] = enabled
        path.write_text(json.dumps(controller))
        actual = resolve_profile(str(profile_path), directory=PROFILES)
        assert actual["v3"]["direct_escape_assistance_enabled"] is (enabled is not False)
        assert actual["v3"]["max_vx"] == .1 and actual["v3"]["max_wz"] == .5
        assert actual["v3"]["k_vx"] == .5 and actual["v3"]["k_wz"] == 5.


def _launch_module():
    pytest.importorskip("launch")
    spec = importlib.util.spec_from_file_location("test_gazebo_launch", SIMULATION / "launch/gazebo.launch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launch_commands_preserve_legacy_graph_and_remove_v3_choreography():
    module = _launch_module()
    legacy = module.algorithm_commands(resolve_profile("rmsprop_full_rotation", directory=PROFILES))
    assert [row[0] for row in legacy] == ["encoder_node", "rotate_frame_node", "sensor_pose_node", "cost_function_node", "filter_node", "controller_node"]
    assert legacy[-1][-2:] == ["--use-sim-time", "True"]
    v3 = module.algorithm_commands(resolve_profile("gesc_v3", directory=PROFILES))
    assert [row[0] for row in v3] == ["encoder_node", "rotate_frame_node", "sensor_pose_node", "cost_function_node"]
    assert v3[-1][-2:] == ["--sample-rate-hz", "5.0"]
    assert not any("supervisor" in arg or "recording_ready" in arg for row in v3 for arg in row)


def test_launch_describes_observers_without_starting_graph(monkeypatch):
    module = _launch_module()
    from launch import LaunchContext
    from launch.actions import ExecuteProcess
    from launch.utilities import perform_substitutions
    from launch_ros.actions import Node
    monkeypatch.setattr(module, "get_package_share_directory", lambda _: str(SIMULATION))
    context = LaunchContext()
    context.launch_configurations.update(profile="gesc_v3", environment="gazebo", gui="true", plot="auto", record="true", output="/tmp/esc-unused-test-output")
    actions = module._launch(context)
    def command_text(action):
        return " ".join(perform_substitutions(context, word) for word in action.cmd)
    observer_commands = [command_text(action) for action in actions if type(action) is ExecuteProcess]
    assert all(command.startswith("/") and "ros2 run" not in command
               for command in observer_commands)
    assert sum("live_plot_node" in command for command in observer_commands) == 1
    assert sum("record_bag" in command for command in observer_commands) == 1
    assert sum(isinstance(action, Node) for action in actions) == 5  # robot, two lights, observation, control
    context.launch_configurations.update(gui="false")
    assert not any("live_plot_node" in command_text(action) for action in module._launch(context) if type(action) is ExecuteProcess)
    context.launch_configurations.update(environment="physical")
    with pytest.raises(ValueError, match="external physical workspace"):
        module._launch(context)


def test_gazebo_launch_owns_server_and_gui_without_wrapper_children():
    from launch import LaunchContext
    from launch.utilities import perform_substitutions
    spec = importlib.util.spec_from_file_location("test_empty_world", SIMULATION / "launch/empty_world.launch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    context = LaunchContext()
    context.launch_configurations.update(gazebo_gui="true", world="/tmp/test.world")
    commands = [[perform_substitutions(context, word) for word in action.cmd]
                for action in module._start(context)]
    assert [command[0] for command in commands] == ["gzserver", "gzclient"]
    assert commands[0][-1] == "/tmp/test.world"
    assert commands[1] == ["gzclient", "--verbose"]
    context.launch_configurations.update(gazebo_gui="false")
    assert len(module._start(context)) == 1
