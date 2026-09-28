from pathlib import Path
from setuptools import find_packages, setup

package_name = 'ros_esc'
profile_files = [
    (str(Path('share/ros_esc') / path.parent), [str(path)])
    for path in sorted(Path('config/profiles').rglob('*.json'))
]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/ros_esc']),
        ('share/ros_esc', ['package.xml']),
        *profile_files,
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nick',
    maintainer_email='ncalkins8746@sdsu.edu',
    description='Shared ESC algorithms with optional simulation and analysis tools',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={'console_scripts': [
        'encoder_node = ros_esc.encoder_node.encoder_node_script:main',
        'sensor_pose_node = ros_esc.sensor_pose_node.sensor_pose_node_script:main',
        'rotate_frame_node = ros_esc.rotate_frame_node.rotate_frame_node_script:main',
        'cost_function_node = ros_esc.cost_function_node.cost_function_node_script:main',
        'filter_node = ros_esc.filter_node.filter_node_script:main',
        'controller_node = ros_esc.controller_node.controller_node_script:main',
        'sensor_observation_node = ros_esc.gesc_v3.observation_node:main',
        'live_plot_node = ros_esc.data_collection_node.data_collection_node_script:main',
        'data_collection_node = ros_esc.data_collection_node.data_collection_node_script:main',
        'record_bag = ros_esc.run_tools.record_bag:main',
        'analyze_bag = ros_esc.run_tools.analyze_bag:main',
    ]},
)
