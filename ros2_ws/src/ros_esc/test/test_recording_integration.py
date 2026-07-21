"""Non-hardware integration contract for the unified recording entry point."""

import os
from pathlib import Path
import subprocess

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
METADATA = REPOSITORY_ROOT / "ros2_ws/src/ros_esc/test/fixtures/recording_smoke_metadata.yaml"


def smoke_command(runs_root, duration_sec=8.0):
    """Return the exact shared-runner Gazebo smoke argv without a shell."""

    return [
        "ros2", "run", "ros_esc", "record_run",
        "--mode", "simulation",
        "--metadata-input", str(METADATA),
        "--duration-sec", str(duration_sec),
        "--preflight-timeout-sec", "60.0",
        "--runs-root", str(runs_root),
        "--",
        "ros2", "launch", "turtlebot3_rotating_sensor", "gazebo.launch.xml",
        "algorithm_profile:=robust_gaussian_v1",
        "use_pde_extensions:=True",
        "enable_observability:=True",
        "recording_ready_required:=True",
        "recording_ready_topic:=/gesc_gaussian/recording_ready",
        "recording_ready_stale_sec:=0.50",
        "cost_surface_start_delay_sec:=0.0",
        "show_cost_surface_plot:=False",
        "live_plot_mode:=None",
        "recenter_after_escape:=False",
        "controller_config_filepath:=" + str(
            REPOSITORY_ROOT / "ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json"
        ),
        "cost_function_config_filepath:=" + str(
            REPOSITORY_ROOT / "ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json"
        ),
        "data_collection_filepath:=/tmp/dsim_phase05_legacy_csv",
    ]


def test_short_simulation_recording_command_is_shared_and_motion_gated(tmp_path):
    command = smoke_command(tmp_path)

    assert command[:4] == ["ros2", "run", "ros_esc", "record_run"]
    assert command.count("--") == 1
    assert "recording_ready_required:=True" in command
    assert "algorithm_profile:=robust_gaussian_v1" in command
    assert not any("physical" in argument for argument in command)


@pytest.mark.skipif(
    os.environ.get("DSIM_RUN_GAZEBO_RECORDING_TEST") != "1",
    reason="set DSIM_RUN_GAZEBO_RECORDING_TEST=1 for the visible Gazebo smoke",
)
def test_short_visible_gazebo_recording(tmp_path):
    environment = dict(os.environ)
    environment.setdefault("DISPLAY", ":0")
    result = subprocess.run(
        smoke_command(tmp_path),
        cwd=REPOSITORY_ROOT / "ros2_ws",
        env=environment,
        timeout=150.0,
        check=False,
    )
    assert result.returncode == 0
    completeness = list(tmp_path.glob("*/*/completeness.json"))
    assert len(completeness) == 1
    assert '"passed": true' in completeness[0].read_text(encoding="utf-8")
