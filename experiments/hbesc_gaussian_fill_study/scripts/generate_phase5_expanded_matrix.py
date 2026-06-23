#!/usr/bin/env python3

import csv
import json
from copy import deepcopy
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = EXP_DIR.parents[1]
SCENARIO_DIR = EXP_DIR / "configs" / "scenarios"
COST_DIR = EXP_DIR / "configs" / "cost_functions"
CONTROLLER_DIR = EXP_DIR / "configs" / "controllers"
BASELINE_SCENARIO_DIR = (
    REPO_ROOT
    / "ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests"
)
BASELINE_COST_DIR = (
    REPO_ROOT / "ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function"
)

WORLD = "/home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/worlds/gazebo_empty.world"
FILTER = "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json"
ROTATE = "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json"
SENSOR = "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json"
DATA_ROOT = "~/dsim-lab/experiments/hbesc_gaussian_fill_study/results/runs"
DEFAULT_CONTROLLER = "~/dsim-lab/experiments/hbesc_gaussian_fill_study/configs/controllers/hbesc_gain_default.json"
GF_CONTROLLER = "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_gaussian_conservative_full_rotation.json"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cost_config(expression: str, noise: dict | None = None) -> dict:
    return {
        "CostFunction": {
            "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py",
            "object_name": "Position_Based_Sympy_Expression",
            "params": {
                "function": expression,
                "symbols": ["t", "x", "y", "z"],
                "substitutions": {},
            },
        },
        "Noise": noise
        if noise is not None
        else {
            "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/noise_objects.py",
            "object_name": "No_Noise",
        },
    }


def double_well_expression(alpha: float, beta: float, gamma: float) -> str:
    return (
        f"{alpha:g}*(((x+y)/2)-2)**2*(((x+y)/2)-10)**2 "
        f"+ {beta:g}*(x-y)**2 - {gamma:g}*((x+y)/2)"
    )


def local_cost_path(path: Path) -> str:
    return f"~/dsim-lab/experiments/hbesc_gaussian_fill_study/configs/cost_functions/{path.name}"


def local_controller_path(path: Path) -> str:
    return f"~/dsim-lab/experiments/hbesc_gaussian_fill_study/configs/controllers/{path.name}"


def scenario(
    *,
    name: str,
    test_id: str,
    description: str,
    axis: str,
    method: str,
    cost_family: str,
    cost_path: str,
    controller_path: str,
    stop_rule_sec: int,
    init_x: float,
    init_y: float,
    speed_label: str,
    target: dict | None = None,
    local_basin: dict | None = None,
    metadata: dict | None = None,
) -> dict:
    use_gf = method == "gaussian_fill"
    data = {
        "phase": 5,
        "name": name,
        "test_id": test_id,
        "description": description,
        "cost_family": cost_family,
        "characterization_axis": axis,
        "method_label": method,
        "speed_label": speed_label,
        "target": target or {"x": 10.0, "y": 10.0},
        "local_basin": local_basin,
        "stop_rule_sec": stop_rule_sec,
        "launch": {
            "entity_name": "turtlebot3",
            "init_x_position": init_x,
            "init_y_position": init_y,
            "init_yaw_angle": 0,
            "input_encoder_data_to_filter": True,
            "live_plot_mode": "2D",
            "use_pde_extensions": use_gf,
            "escape_policy": "conditional_gaussian_fill" if use_gf else "none",
            "rotate_frame_config_filepath": ROTATE,
            "sensor_transform_config_filepath": SENSOR,
            "cost_function_config_filepath": cost_path,
            "filter_config_filepath": FILTER,
            "controller_config_filepath": controller_path,
            "data_collection_filepath": DATA_ROOT,
            "world": WORLD,
        },
    }
    if metadata:
        data.update(metadata)
    return data


def make_speed_controllers() -> dict[str, str]:
    base = read_json(CONTROLLER_DIR / "hbesc_gain_default.json")
    speeds = {
        "vx005": 0.05,
        "vx010": 0.10,
        "vx015": 0.15,
        "vx020": 0.20,
        "real": None,
    }
    paths = {}
    for label, max_vx in speeds.items():
        config = deepcopy(base)
        config["params"]["set_max_vx"] = max_vx
        config["params"]["set_max_wz"] = 0.75
        path = CONTROLLER_DIR / f"phase5_speed_{label}.json"
        write_json(path, config)
        paths[label] = local_controller_path(path)
    return paths


def make_costs() -> dict[str, str]:
    paths: dict[str, str] = {}
    curves = {
        "quartic_center10_scale0001": "0.0001*((x-10)**4 + (y-10)**4)",
        "quartic_center10_scale0005": "0.0005*((x-10)**4 + (y-10)**4)",
        "quartic_center10_scale0015": "0.0015*((x-10)**4 + (y-10)**4)",
        "quartic_asym_center10": "0.0002*(x-10)**4 + 0.0010*(y-10)**4",
        "quartic_cross_center10": "0.0005*(((x+y)/1.41421356237)-14.1421356237)**4 + 0.0002*(((x-y)/1.41421356237))**4",
    }
    for label, expression in curves.items():
        path = COST_DIR / f"phase5b_{label}.json"
        write_json(path, cost_config(expression))
        paths[label] = local_cost_path(path)

    for alpha in (0.0025, 0.005, 0.01, 0.02, 0.04):
        label = f"double_well_alpha{str(alpha).replace('.', 'p')}"
        path = COST_DIR / f"phase5b_{label}.json"
        write_json(path, cost_config(double_well_expression(alpha, 0.0125, 0.005)))
        paths[label] = local_cost_path(path)

    for beta in (0.00625, 0.025):
        label = f"double_well_beta{str(beta).replace('.', 'p')}"
        path = COST_DIR / f"phase5b_{label}.json"
        write_json(path, cost_config(double_well_expression(0.01, beta, 0.005)))
        paths[label] = local_cost_path(path)

    for gamma in (0.0025, 0.01):
        label = f"double_well_gamma{str(gamma).replace('.', 'p')}"
        path = COST_DIR / f"phase5b_{label}.json"
        write_json(path, cost_config(double_well_expression(0.01, 0.0125, gamma)))
        paths[label] = local_cost_path(path)

    for seed in (101, 202, 303):
        label = f"double_well_alpha0p01_noise_seed{seed}"
        path = COST_DIR / f"phase5b_{label}.json"
        write_json(
            path,
            cost_config(
                double_well_expression(0.01, 0.0125, 0.005),
                {
                    "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/noise_objects.py",
                    "object_name": "Gaussian",
                    "params": {"std_dev": 0.01, "seed_num": seed},
                },
            ),
        )
        paths[label] = local_cost_path(path)

    return paths


def normalize_baseline_scenario(src: Path, index: int) -> dict:
    raw = read_json(src)
    launch = raw.setdefault("launch", {})
    launch["data_collection_filepath"] = DATA_ROOT
    launch["world"] = WORLD
    launch.setdefault("live_plot_mode", "2D")
    name = f"phase5b_pilot_{src.stem.lower()}"
    raw.update(
        {
            "phase": 5,
            "name": name,
            "test_id": f"P5B-PILOT-{index:02d}-{src.stem.upper()}",
            "description": f"Phase 5B normalized pilot replication of existing baseline scenario {src.name}.",
            "characterization_axis": "pilot_replication",
            "method_label": "baseline_hbesc",
            "source_scenario": str(src),
            "stop_rule_sec": raw.get("stop_rule_sec", 700 if src.stem.startswith(("W", "G", "H")) else 500),
        }
    )
    raw.setdefault("target", {"x": 10.0, "y": 10.0})
    if src.stem.startswith("W"):
        raw.setdefault("local_basin", {"x": 2.0, "y": 2.0})
    else:
        raw.setdefault("local_basin", None)
    return raw


def main() -> int:
    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    COST_DIR.mkdir(parents=True, exist_ok=True)
    CONTROLLER_DIR.mkdir(parents=True, exist_ok=True)

    speed_controllers = make_speed_controllers()
    costs = make_costs()
    rows: list[dict] = []
    scenario_paths: list[Path] = []

    def add(data: dict) -> None:
        path = SCENARIO_DIR / f"{data['name']}.json"
        write_json(path, data)
        scenario_paths.append(path)
        rows.append(
            {
                "scenario_config": f"experiments/hbesc_gaussian_fill_study/configs/scenarios/{path.name}",
                "scenario_id": data["test_id"],
                "axis": data.get("characterization_axis", ""),
                "method": data.get("method_label", ""),
                "cost_family": data.get("cost_family", ""),
                "speed_label": data.get("speed_label", ""),
                "start_x": data.get("launch", {}).get("init_x_position", ""),
                "start_y": data.get("launch", {}).get("init_y_position", ""),
                "stop_rule_sec": data.get("stop_rule_sec", ""),
                "status": "planned",
            }
        )

    for index, src in enumerate(sorted(BASELINE_SCENARIO_DIR.glob("*.json")), start=1):
        add(normalize_baseline_scenario(src, index))

    # Gaussian-fill paired pilot/local-basin cases.
    pilot_pairs = [
        ("Q1_quadratic_start0_real", "polynomial_quadratic_bowl_center10.json", 0, 0, 500, "quadratic_bowl", None),
        ("R1_quartic_start0_real", "polynomial_quartic_bowl_center10.json", 0, 0, 500, "quartic_bowl", None),
        ("R2_quartic_start6_real", "polynomial_quartic_bowl_center10.json", 6, 6, 500, "quartic_bowl", None),
        ("W2_double_well_start1_real", "polynomial_quartic_double_well_local2_global10.json", 1, 1, 700, "quartic_double_well", {"x": 2.0, "y": 2.0}),
        ("G2_globalW40_start1_real", "gaussian_two_basin_globalW40.json", 1, 1, 700, "gaussian_two_basin", {"x": 2.0, "y": 2.0}),
    ]
    for label, cost_file, init_x, init_y, stop, family, basin in pilot_pairs:
        add(
            scenario(
                name=f"phase5b_pilot_gf_{label.lower()}",
                test_id=f"P5B-PILOT-GF-{label.upper()}",
                description=f"Phase 5B Gaussian-fill paired pilot comparison for {label}.",
                axis="pilot_gaussian_fill_pair",
                method="gaussian_fill",
                cost_family=family,
                cost_path=f"~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/{cost_file}",
                controller_path=GF_CONTROLLER,
                stop_rule_sec=stop,
                init_x=init_x,
                init_y=init_y,
                speed_label="conservative",
                local_basin=basin,
            )
        )

    for label, cost_key in [
        ("shallow", "quartic_center10_scale0001"),
        ("default", "quartic_center10_scale0005"),
        ("steep", "quartic_center10_scale0015"),
        ("asym", "quartic_asym_center10"),
        ("cross", "quartic_cross_center10"),
    ]:
        for method, controller, speed_label in [
            ("baseline_hbesc", DEFAULT_CONTROLLER, "real"),
            ("gaussian_fill", GF_CONTROLLER, "conservative"),
        ]:
            add(
                scenario(
                    name=f"phase5b_curv_{label}_{'gf' if method == 'gaussian_fill' else 'hb'}",
                    test_id=f"P5B-CURV-{label.upper()}-{'GF' if method == 'gaussian_fill' else 'HB'}",
                    description=f"Phase 5B quartic curvature/shape sweep: {label}, {method}.",
                    axis="quartic_curvature_and_shape",
                    method=method,
                    cost_family="quartic_bowl",
                    cost_path=costs[cost_key],
                    controller_path=controller,
                    stop_rule_sec=500,
                    init_x=0,
                    init_y=0,
                    speed_label=speed_label,
                )
            )

    for alpha in (0.0025, 0.005, 0.01, 0.02, 0.04):
        cost_key = f"double_well_alpha{str(alpha).replace('.', 'p')}"
        for speed_label in ("vx005", "vx010", "vx015", "vx020", "real"):
            add(
                scenario(
                    name=f"phase5b_dw_a{str(alpha).replace('.', 'p')}_{speed_label}_hb",
                    test_id=f"P5B-DW-A{str(alpha).replace('.', 'P')}-{speed_label.upper()}-HB",
                    description=f"Phase 5B baseline HBESC double-well alpha/speed sweep alpha={alpha}, speed={speed_label}.",
                    axis="double_well_alpha_speed",
                    method="baseline_hbesc",
                    cost_family="quartic_double_well",
                    cost_path=costs[cost_key],
                    controller_path=speed_controllers[speed_label],
                    stop_rule_sec=700,
                    init_x=1,
                    init_y=1,
                    speed_label=speed_label,
                    local_basin={"x": 2.0, "y": 2.0},
                    metadata={"barrier_alpha": alpha, "cross_valley_beta": 0.0125, "tilt_gamma": 0.005},
                )
            )
        for method, controller in [("gaussian_fill", GF_CONTROLLER)]:
            add(
                scenario(
                    name=f"phase5b_dw_a{str(alpha).replace('.', 'p')}_gf",
                    test_id=f"P5B-DW-A{str(alpha).replace('.', 'P')}-GF",
                    description=f"Phase 5B Gaussian-fill double-well alpha sweep alpha={alpha}.",
                    axis="double_well_alpha_gaussian_fill",
                    method=method,
                    cost_family="quartic_double_well",
                    cost_path=costs[cost_key],
                    controller_path=controller,
                    stop_rule_sec=700,
                    init_x=1,
                    init_y=1,
                    speed_label="conservative",
                    local_basin={"x": 2.0, "y": 2.0},
                    metadata={"barrier_alpha": alpha, "cross_valley_beta": 0.0125, "tilt_gamma": 0.005},
                )
            )

    for beta in (0.00625, 0.025):
        for method, controller, speed_label in [
            ("baseline_hbesc", DEFAULT_CONTROLLER, "real"),
            ("gaussian_fill", GF_CONTROLLER, "conservative"),
        ]:
            add(
                scenario(
                    name=f"phase5b_dw_beta{str(beta).replace('.', 'p')}_{'gf' if method == 'gaussian_fill' else 'hb'}",
                    test_id=f"P5B-DW-BETA{str(beta).replace('.', 'P')}-{'GF' if method == 'gaussian_fill' else 'HB'}",
                    description=f"Phase 5B double-well cross-valley stiffness sweep beta={beta}, {method}.",
                    axis="double_well_beta",
                    method=method,
                    cost_family="quartic_double_well",
                    cost_path=costs[f"double_well_beta{str(beta).replace('.', 'p')}"],
                    controller_path=controller,
                    stop_rule_sec=700,
                    init_x=1,
                    init_y=1,
                    speed_label=speed_label,
                    local_basin={"x": 2.0, "y": 2.0},
                    metadata={"barrier_alpha": 0.01, "cross_valley_beta": beta, "tilt_gamma": 0.005},
                )
            )

    for gamma in (0.0025, 0.01):
        for method, controller, speed_label in [
            ("baseline_hbesc", DEFAULT_CONTROLLER, "real"),
            ("gaussian_fill", GF_CONTROLLER, "conservative"),
        ]:
            add(
                scenario(
                    name=f"phase5b_dw_gamma{str(gamma).replace('.', 'p')}_{'gf' if method == 'gaussian_fill' else 'hb'}",
                    test_id=f"P5B-DW-GAMMA{str(gamma).replace('.', 'P')}-{'GF' if method == 'gaussian_fill' else 'HB'}",
                    description=f"Phase 5B double-well tilt sweep gamma={gamma}, {method}.",
                    axis="double_well_gamma",
                    method=method,
                    cost_family="quartic_double_well",
                    cost_path=costs[f"double_well_gamma{str(gamma).replace('.', 'p')}"],
                    controller_path=controller,
                    stop_rule_sec=700,
                    init_x=1,
                    init_y=1,
                    speed_label=speed_label,
                    local_basin={"x": 2.0, "y": 2.0},
                    metadata={"barrier_alpha": 0.01, "cross_valley_beta": 0.0125, "tilt_gamma": gamma},
                )
            )

    for start_label, init_x, init_y in [("s00", 0, 0), ("s11", 1, 1), ("s31", 3, 1), ("s55", 5, 5), ("s81", 8, 1)]:
        for method, controller, speed_label in [
            ("baseline_hbesc", DEFAULT_CONTROLLER, "real"),
            ("gaussian_fill", GF_CONTROLLER, "conservative"),
        ]:
            add(
                scenario(
                    name=f"phase5b_start_{start_label}_{'gf' if method == 'gaussian_fill' else 'hb'}",
                    test_id=f"P5B-START-{start_label.upper()}-{'GF' if method == 'gaussian_fill' else 'HB'}",
                    description=f"Phase 5B double-well starting-position grid {start_label}, {method}.",
                    axis="starting_position_grid",
                    method=method,
                    cost_family="quartic_double_well",
                    cost_path=costs["double_well_alpha0p01"],
                    controller_path=controller,
                    stop_rule_sec=700,
                    init_x=init_x,
                    init_y=init_y,
                    speed_label=speed_label,
                    local_basin={"x": 2.0, "y": 2.0},
                    metadata={"barrier_alpha": 0.01, "cross_valley_beta": 0.0125, "tilt_gamma": 0.005},
                )
            )

    for seed in (101, 202, 303):
        for method, controller, speed_label in [
            ("baseline_hbesc", DEFAULT_CONTROLLER, "real"),
            ("gaussian_fill", GF_CONTROLLER, "conservative"),
        ]:
            add(
                scenario(
                    name=f"phase5b_noise_seed{seed}_{'gf' if method == 'gaussian_fill' else 'hb'}",
                    test_id=f"P5B-NOISE-SEED{seed}-{'GF' if method == 'gaussian_fill' else 'HB'}",
                    description=f"Phase 5B deterministic Gaussian cost-noise seed {seed}, {method}.",
                    axis="noise_seed",
                    method=method,
                    cost_family="quartic_double_well",
                    cost_path=costs[f"double_well_alpha0p01_noise_seed{seed}"],
                    controller_path=controller,
                    stop_rule_sec=700,
                    init_x=1,
                    init_y=1,
                    speed_label=speed_label,
                    local_basin={"x": 2.0, "y": 2.0},
                    metadata={"noise_std_dev": 0.01, "noise_seed": seed},
                )
            )

    matrix_path = SCENARIO_DIR / "phase5_expanded_characterization_matrix.csv"
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} scenarios")
    print(matrix_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
