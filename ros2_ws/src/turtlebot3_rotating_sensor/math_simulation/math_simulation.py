#!/bin/usr/python3

"""This is used to conduct math simulations of extremum seeking schemes."""

import os
import numpy as np
from scipy.integrate import solve_ivp
from sensor_perturbation_signals import *
from derivative_estimation_signals import *
from cost_functions import *
from custom_filter_objects import *
from control_functions import *
from helper_functions import *
from extremum_seeking.filters import *
from extremum_seeking.seekers import *
from extremum_seeking.systems import NonholonomicUnicycle

def main():
    ### Define Simulation parameters
    # Define the frame "arm length" in meters
    frame_arm_length = 0.18
    # Define the rotation speed of the arm in rpm
    spin_rpm = 20
    # Define the starting state of the seeker
    # State vector is in the form [x_init, y_init, theta_init]
    start_pose = np.array([0, 0, 0])
    # Define the position of the source
    x_optimal, y_optimal = 3, 3
    # Define the length of time to simulate
    test_time = 1000.0
    # Define the dt variable
    dt = 1e-2
    # Define a time vector
    tvec = np.linspace(0.0, test_time, int(np.ceil((test_time - 0.0)/dt)))
    # Define the directory where test folders will be saved
    directory = os.path.expanduser(
        "~/Experiments/Numerical-Simulations"
    )


    # Initialize the angular position signal object
    # For constant back and forth rotation
    angpossignal_obj = ConstantBnFRotation(
        {
            "spin_rpm": spin_rpm,
            "cw_bound": -90,
            "ccw_bound": 90
        }
    )

    # Initialize the derivative estimation signal object
    # For constant back and forth rotation in a [90, -90] degree envelope
    estimsignal_obj = ConstantBnFRotationEstimation(
        {
            "angular_position_signal_object": angpossignal_obj,
            "frame_arm_length": frame_arm_length
        }
    )

    # Initialize our custom filter object
    # For an RMS Prop custom filter
    customfilter = RMSPropFilter(
        {
            "estimation_signal_object": estimsignal_obj,
            "gradient_washout_omega_l": 1.0,
            "gradient_squared_washout_omega_l": 1.0,
            "directional_filter_gains": np.array([0.1, 0.1]),
            "directional_filter_omega_l": 1.0,
            "frame_arm_length": frame_arm_length
        }
    )
    # Define initial states for the two washout filters
    washout_init = np.array([0,0])
    # Define initial guess for the optimal position
    theta_hat_init = start_pose[:2]
    # Define initial gradient squared estimatimates
    v_hat_init = np.array([0,0])
    # Define the initial filter state
    filter_init_state = np.concatenate((
        washout_init, theta_hat_init, v_hat_init
    ))

    # Get the initialized custom filter object
    customfilter_obj = customfilter.get_filter_object()

    # Initialize the cost funciton object
    # For a quadratic cost function
    cost_funct_obj = PositionBasedSympyExpression(
        {
            "function": "a*(x-x_optimal)**2 + a*(y-y_optimal)**2",
            "symbols": ["t", "x", "y", "z"],
            "substitutions":{
                "a": 0.5,
                "x_optimal": x_optimal,
                "y_optimal": y_optimal
            }
        }
    )
    # Create a lambda function which calls the cost function
    cost_funct = lambda t, x: cost_funct_obj.cost_output(
        t, sensor_transform(t, x, angpossignal_obj, frame_arm_length)
    )

    # Initialize the controller function
    # For a directional controller
    controller_obj = DirectionalController(
        {
            "k_vx": 1.0,
            "k_wz": 5.0,
            "wheel_radius": 0.033,
            "wheel_distance": 0.158,
            "wheel_max_rpm": 70,
            "set_max_vx": 0.1,
            "set_max_wz": 0.5
        }
    )
    # Create a controller function which is called in the iteration
    controller_funct = lambda t, x, z: controller_obj.controller_output(t, x, z)



    # Initialize a Lie Bracket Seeker
    seeker = LieBracketSeeker(
        f=NonholonomicUnicycle(),
        h=customfilter_obj,
        J=cost_funct,
        u=controller_funct
    )
    # Initialize the system
    x0 = seeker.initialize_system(start_pose, filter_init_state)


    # Use solve ivp to solve ODE and iterate in time
    results = solve_ivp(
        fun=seeker.differential_equation,
        t_span=(0.0, test_time),
        y0=x0,
        t_eval=tvec,
        max_step=0.1
    )
    # Save the time history of the vehicle states
    state_hist = results.y.T
    # Save the history of timestamps
    tstamps = results.t

    # Initialize the filepath to this script
    math_sim_filepath = "~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/math_simulation/math_simulation.py"

    # Create a new test folder to hold simulation results
    test_folder_filepath, csv_filepath_dict = create_test_folder(directory, math_sim_filepath)

    ### Specify plot style variables here
    plot_style = {
        "save_to_filepath": test_folder_filepath,
        "dpi_level": 300,
        "tick_size": 10,
        "axis_label_size": 10,
        "legend_label_size": 10,
        "fonttype": 'Times New Roman',
        "figsize": (8,8)
    }

    # Save simulation results to csv files
    sensor_pose_hist, cost_value_hist = save_data_to_csv(
        tstamps, state_hist, cost_funct_obj, 
        angpossignal_obj, frame_arm_length, csv_filepath_dict
    )

    # Make plots of vehicle trajectory
    plot_seeker_path(plot_style, state_hist, sensor_pose_hist, source_pose=(x_optimal, y_optimal))

    # Make plots of cost value history
    plot_cost_value_hist(plot_style, tstamps, cost_value_hist)

if __name__ == "__main__":
    main()
