"""Read-only installed-entry-point binding for the finite Q1 acquisition.

Import the installed console targets, but never call their main functions or
initialize a ROS node. The separate recorder --help smoke checks the wrapper.
"""
import ast
import hashlib
import importlib.metadata
import inspect
import os
import sys
from pathlib import Path

from ament_index_python.packages import get_package_prefix


REPOSITORY = Path('/home/mattb/dsim-lab')
BUILD = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial')
ENVIRONMENT_KEYS = ('ROS_DOMAIN_ID', 'PYTHONPATH', 'AMENT_PREFIX_PATH',
                    'COLCON_PREFIX_PATH', 'LD_LIBRARY_PATH', 'DISPLAY',
                    'RMW_IMPLEMENTATION', 'ROS_LOCALHOST_ONLY')


def receipt(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def selected_environment():
    return {key: os.environ.get(key) for key in ENVIRONMENT_KEYS}


def installed_entry_points(*, expected_build=BUILD):
    """Bind the explicitly expected install, preserving the original Q1 default.

    A later source milestone must pass its own frozen absolute build directory;
    the active AMENT/Python environment never chooses the expected build.
    """
    try:
        build = Path(expected_build)
    except TypeError:
        raise ValueError('expected isolated build must be an absolute path') from None
    if not build.is_absolute():
        raise ValueError('expected isolated build must be an absolute path')
    build = build.resolve()
    source_root = REPOSITORY / 'ros2_ws/src/ros_esc'
    tree = ast.parse((source_root / 'setup.py').read_text())
    setup = next(node for node in tree.body if isinstance(node, ast.Expr)
                 and isinstance(node.value, ast.Call)
                 and isinstance(node.value.func, ast.Name)
                 and node.value.func.id == 'setup').value
    declaration = ast.literal_eval(next(keyword.value for keyword in setup.keywords
                                        if keyword.arg == 'entry_points'))
    expected = dict(tuple(part.strip() for part in value.split('=', 1))
                    for value in declaration['console_scripts'])
    distribution = importlib.metadata.distribution('ros-esc')
    entries = [entry for entry in distribution.entry_points
               if entry.group == 'console_scripts']
    if len(entries) != len(expected) or {e.name: e.value for e in entries} != expected:
        raise ValueError('Q1 installed ros-esc console metadata differs from current setup.py')
    prefix = Path(get_package_prefix('ros_esc')).resolve()
    if prefix != (build / 'install/ros_esc').resolve():
        raise ValueError('Q1 selected ros_esc prefix is not the isolated V2 build')
    # Distribution.files contains the metadata actually selected by the wrapper.
    metadata_files = [Path(distribution.locate_file(item)).resolve()
                      for item in distribution.files or ()
                      if Path(item).name in ('entry_points.txt', 'PKG-INFO')]
    selected_metadata = build / 'build/ros_esc/ros_esc.egg-info'
    if (len(metadata_files) != 2
            or any(path.parent != selected_metadata for path in metadata_files)):
        raise ValueError('Q1 console metadata is not the isolated build metadata')
    loaded = []
    for entry in sorted(entries, key=lambda item: item.name):
        function = entry.load()
        if not callable(function):
            raise ValueError(f'Q1 console target is not callable: {entry.name}')
        module_path = Path(inspect.getfile(function)).resolve()
        if not module_path.is_relative_to(source_root / 'ros_esc'):
            raise ValueError(f'Q1 console target resolves outside this checkout: {entry.name}')
        wrapper = prefix / 'lib/ros_esc' / entry.name
        loaded.append({'name': entry.name, 'target': entry.value,
                       'wrapper': receipt(wrapper), 'module': receipt(module_path)})
    return {'python_executable': str(Path(sys.executable).resolve()),
            'package_prefix': str(prefix),
            'metadata_files': [receipt(path) for path in sorted(metadata_files)],
            'entry_points': loaded, 'node_entry_points_called': False}


def verify_environment(contract, release, *, expected_build=BUILD):
    """Check before output creation or any runner action."""
    if release.get('environment') != selected_environment():
        raise ValueError('Q1 process environment differs from its frozen dispatch release')
    if contract.get('installed_entry_points') != installed_entry_points(expected_build=expected_build):
        raise ValueError('Q1 installed console binding differs from the frozen contract')
