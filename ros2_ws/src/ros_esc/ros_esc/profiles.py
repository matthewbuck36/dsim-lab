"""Resolve one installed algorithm and environment profile without starting ROS."""

from copy import deepcopy
import json
from pathlib import Path


def profile_directory():
    """Prefer the selected install; allow direct source use for pure tests."""
    try:
        from ament_index_python.packages import get_package_share_directory
        installed = Path(get_package_share_directory("ros_esc")) / "config" / "profiles"
        if installed.is_dir():
            return installed
    except (ImportError, LookupError):
        pass
    source = Path(__file__).resolve().parents[1] / "config" / "profiles"
    if source.is_dir():
        return source
    raise FileNotFoundError("ros_esc installed profile resources are unavailable")


def _read(name, directory):
    with (directory / name).open(encoding="utf-8") as stream:
        return json.load(stream)


def available_profiles(*, directory=None):
    return tuple(sorted(_read("algorithms.json", Path(directory or profile_directory()))))


def resolve_profile(profile="gesc_v3", environment="gazebo", *, directory=None):
    """Return detached settings and existing installed configuration paths.

    A custom JSON profile may use the same small structure as a named profile;
    its config paths are relative to that file, or absolute. Custom original
    object JSONs may still use ``filepath`` instead of an installed ``module``.
    Environment adapters are selected by the caller, never imported here.
    """
    directory = Path(directory or profile_directory())
    environments = _read("environments.json", directory)
    if environment not in environments:
        raise ValueError(f"unknown environment {environment!r}; choose {tuple(environments)}")
    algorithms = _read("algorithms.json", directory)
    if profile in algorithms:
        selected = deepcopy(algorithms[profile])
        config_root = directory
    else:
        custom = Path(profile).expanduser()
        if not custom.is_file():
            raise ValueError(f"unknown algorithm profile {profile!r}; choose {tuple(sorted(algorithms))}")
        with custom.open(encoding="utf-8") as stream:
            selected = json.load(stream)
        config_root = custom.resolve().parent
    if selected.get("algorithm") not in ("legacy", "gesc_v3"):
        raise ValueError("profile algorithm must be legacy or gesc_v3; Gaussian V1/V2 are archived")
    required = {"rotation", "sensor", "cost", "filter", "controller"}
    if set(selected.get("configs", {})) != required:
        raise ValueError(f"profile configs must contain exactly {sorted(required)}")
    paths = {}
    for role, configured in selected.pop("configs").items():
        path = Path(configured).expanduser()
        path = path if path.is_absolute() else config_root / path
        path = path.resolve()
        if not path.is_file():
            raise FileNotFoundError(f"{role} configuration is unavailable: {path}")
        paths[role] = str(path)
    selected.update(deepcopy(environments[environment]))
    selected.update(profile=profile, environment=environment, config_paths=paths)
    if selected["algorithm"] == "gesc_v3":
        # The selected controller JSON owns effective gains and limits in both
        # runtimes. Do not maintain a second silently divergent copy.
        controller = json.loads(Path(paths["controller"]).read_text(encoding="utf-8"))
        selected["v3"].update(
            k_vx=controller["gains"]["k_vx"], k_wz=controller["gains"]["k_wz"],
            max_vx=controller["params"]["set_max_vx"], max_wz=controller["params"]["set_max_wz"],
            direct_escape_assistance_enabled=controller["params"].get(
                "direct_escape_assistance_enabled", True),
            escape_affine_magnitude=controller["params"].get("escape_affine_magnitude", 0.5),
        )
    entity = selected["entity"]
    selected["topics"] = {
        "pose": "/odom",
        "joints": "/joint_states",
        "encoder": f"/{entity}/encoder_chatter",
        "timekeeper": f"/{entity}/timekeeper_chatter",
        "sensor": f"/{entity}/sensor_transform_chatter",
        "cost": f"/{entity}/cost_value_chatter",
        "filter": f"/{entity}/filter_value_chatter",
        "control": f"/{entity}/control_value_chatter",
        "command": "/cmd_vel",
        "observation": "/gesc/observation",
        "events": "/gesc/events",
        "fills": "/gesc/fills",
    }
    return selected
