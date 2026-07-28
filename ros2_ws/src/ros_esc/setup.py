from glob import glob

from setuptools import find_packages, setup

package_name = 'ros_esc'
scenario_files = [
    'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml',
    'ros_esc/scenario_runner/scenarios/phase06_catalog.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_parameter_candidates.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_training.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_holdout.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_full_matrix.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_frozen_parameters.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_2_recenter.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_v2_activation.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_v2_training.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_v2_holdout.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_v2_validation.yaml',
    'ros_esc/scenario_runner/scenarios/phase08_v2_reproducibility.yaml',
    *sorted(glob(
        'ros_esc/scenario_runner/scenarios/phase08_v[34]_*'
    )),
]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/experiment_recording', [
            'ros_esc/experiment_recording/topic_manifest.yaml',
            'ros_esc/experiment_recording/experiment_metadata.yaml',
            'ros_esc/experiment_recording/qos_overrides.yaml',
        ]),
        ('share/' + package_name + '/aggregate_field_truth', [
            'paper_recreations/heavy_ball_PDE_ESC/cost_function/'
            'multi_light_source_photoresistor.json',
            'ros_esc/sensor_pose_node/transform_config_files/'
            'turtlebot_rotating_sensor.json',
        ]),
        (
            'share/' + package_name + '/scenario_runner/scenarios',
            scenario_files,
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nick',
    maintainer_email='ncalkins8746@sdsu.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Note this follows the following format:
            # {node_name} = {folder_name}.{subfolder_name}.{script_name}:{function_name}
            'encoder_node = '
            'ros_esc.encoder_node.encoder_node_script:main',
            'sensor_pose_node = '
            'ros_esc.sensor_pose_node.sensor_pose_node_script:main',
            'rotate_frame_node = '
            'ros_esc.rotate_frame_node.rotate_frame_node_script:main',
            'cost_function_node = '
            'ros_esc.cost_function_node.cost_function_node_script:main',
            'filter_node = '
            'ros_esc.filter_node.filter_node_script:main',
            'convergence_detector_node = '
            'ros_esc.convergence_detector_node.'
            'convergence_detector_node_script:main',
            'gaussian_fill_node = '
            'ros_esc.gaussian_fill_node.gaussian_fill_script:main',
            'modified_cost_node = '
            'ros_esc.modified_cost_node.modified_cost_script:main',
            'pde_history_node = '
            'ros_esc.pde_history_node.pde_history_script:main',
            'controller_node = '
            'ros_esc.controller_node.controller_node_script:main',
            'data_collection_node = '
            'ros_esc.data_collection_node.data_collection_node_script:main',
            'pde_cost_history_node = '
            'ros_esc.pde_cost_history_node.pde_cost_history_script:main',
            'cost_surface_plotter = '
            'ros_esc.plotting_scripts.cost_surface_plotter:main',
            'supervisor_node = '
            'ros_esc.supervisor_node.supervisor_node_script:main',
            'record_run = '
            'ros_esc.experiment_recording.record_run:main',
            'validate_run = '
            'ros_esc.experiment_recording.validate_run:main',
            'run_scenario = '
            'ros_esc.scenario_runner.run_scenario:main',
            'simulation_disturbance_node = '
            'ros_esc.scenario_runner.simulation_disturbance_node:main',
            'validate_robustness = '
            'ros_esc.scenario_runner.phase08_validation:main',
            'analyze_run = '
            'ros_esc.plotting_scripts.gesc_gaussian_bag_analysis:main',
            'summarize_matrix = '
            'ros_esc.plotting_scripts.gesc_gaussian_bag_analysis:main_matrix',
        ],
    },
)
