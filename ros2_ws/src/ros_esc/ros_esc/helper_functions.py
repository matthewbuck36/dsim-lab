#!/usr/bin/env python3

"""This script holds helper functions used for creating and interacting with test folders."""

import csv
import json
import numpy as np
from ros_esc.config_parsing import parse_optimal_position_expression, parse_object_into_str

def read_data_file(filepath):
    """This function extracts the data from a csv file given the filepath.

    Note in every csv file, there are timestamps in the first column of the
    data. This function returns a list of those timestamps, and the rest of
    the data with the timestamps removed.
    """

    # Initialize a variable for the prevous timestamp
    prev_tstamp = -1
    prev_len = None
    with open(filepath, mode='r', newline="", encoding='utf-8') as file:
        reader = csv.reader(file)
        # Save the data to two lists
        timestamps = []
        data = []
        for row in reader:
            # Get the current timestamp
            tstamp = row[0]
            # If the current timestamp matches the prev timestamp
            # then we ingnore a duplicate line
            if prev_tstamp == tstamp:
                # Ignore the duplicate line, continue to next iteration
                continue
            # If the line has more data than the previous line, meaning
            # something got overwritten, we ignore it
            if prev_len != len(row) and prev_len is not None:
                # Ignore the overwritten line, continue to next iteration
                continue
            # Otherwise this runs
            # The first entry is always a timestamp
            timestamps.append(float(row[0]))
            # Convert the data to floats
            data_list = [float(x) for x in row[1:]]
            # Everything afterwards is data
            data.append(data_list)
            # Update the prev timestamp
            prev_tstamp = tstamp
            # Update the previous row length
            prev_len = len(row)

    # Convert to numpy array
    data = np.array(data)
    # Return the lists of timestamps and data
    return timestamps, data

# pylint: disable=too-many-locals
def extract_test_data(test_folder_directory, test_folder_contents):
    """This function obtains the test data from the csv files organized into a dictionary."""

    # Organize results into a dictionary
    test_data = {}

    # If there is an encoder csv file in the test folder
    if 'encoder.csv' in test_folder_contents:
        # Get the encoder value filepath
        filepath = f'{test_folder_directory}/encoder.csv'
        # Extract the data from the csv file
        encoder_tstamps, encoder_data = read_data_file(filepath)
        # Organize results into dictionary
        test_data["encoder_tstamps"] = encoder_tstamps
        test_data["encoder_data"] = encoder_data

    # If there is an odometry csv file in the test folder
    if 'odometry.csv' in test_folder_contents:
        # Get the odometry filepath
        filepath = f'{test_folder_directory}/odometry.csv'
        # Extract the data from the csv file
        odom_tstamps, odom_data = read_data_file(filepath)
        # Convert the odom data into position and orientation data
        odom_position, odom_orientation = extract_vehicle_state_data(odom_data)
        # Organize results into dictionary
        test_data["odom_tstamps"] = odom_tstamps
        test_data["odom_position"] = odom_position
        test_data["odom_orientation"] = odom_orientation

    # If there is a sensor transform csv file in the test folder
    if 'sensor_transform.csv' in test_folder_contents:
        # Get the sensor transform filepath
        filepath = f'{test_folder_directory}/sensor_transform.csv'
        # Extract the data from the csv file
        sensor_tform_tstamps, sensor_tform_data = read_data_file(filepath)
        # Organize results into dictionary
        test_data["sensor_tform_tstamps"] = sensor_tform_tstamps
        test_data["sensor_tform_data"] = sensor_tform_data

    # If there is a cost value csv file in the test folder
    if 'cost_value.csv' in test_folder_contents:
        # Get the cost value filepath
        filepath = f'{test_folder_directory}/cost_value.csv'
        # Extract the data from the csv file
        cost_tstamps, cost_data = read_data_file(filepath)
        # Organize results into dictionary
        test_data["cost_tstamps"] = cost_tstamps
        test_data["cost_data"] = cost_data

    # If there is a filter value csv file in the test folder
    if 'filter_value.csv' in test_folder_contents:
        # Get the filter value filepath
        filepath = f'{test_folder_directory}/filter_value.csv'
        # Extract the data from the csv file
        filter_tstamps, filter_data = read_data_file(filepath)
        # Organize results into dictionary
        test_data["filter_tstamps"] = filter_tstamps
        test_data["filter_data"] = filter_data

    # If there is a control value csv file in the test folder
    if 'control_value.csv' in test_folder_contents:
        # Get the control value filepath
        filepath = f'{test_folder_directory}/control_value.csv'
        # Extract the data from the csv file
        control_tstamps, control_data = read_data_file(filepath)
        # Organize results into dictionary
        test_data["control_tstamps"] = control_tstamps
        test_data["control_data"] = control_data

    return test_data

def extract_vehicle_state_data(odom_data): # pylint: disable=too-many-locals
    """This function organizes the position and orientation data into lists."""

    # Note the odom data list has the following data organized by column
    # x, y, z, qw, qx, qy, qz

    # Extract the data from the columns
    x_data = odom_data[:,0].tolist()
    y_data = odom_data[:,1].tolist()
    z_data = odom_data[:,2].tolist()
    qw_data = odom_data[:,3].tolist()
    qx_data = odom_data[:,4].tolist()
    qy_data = odom_data[:,5].tolist()
    qz_data = odom_data[:,6].tolist()
    # Calculate roll, pitch, yaw from quaternions
    roll_data = []
    pitch_data = []
    yaw_data = []
    for value in enumerate(qw_data):
        # Get the index i
        i = value[0]

        # Initialize variables
        quat_w, quat_x, quat_y, quat_z = qw_data[i], qx_data[i], qy_data[i], qz_data[i]
        # Calculate and convert to degrees
        roll_data.append(
            np.arctan2(
                2*(quat_w*quat_x+quat_y*quat_z),
                quat_w**2-quat_x**2-quat_y**2+quat_z**2
                )
            *180/np.pi
        )
        pitch_data.append(
            np.arcsin(
                2*(quat_w*quat_y-quat_x*quat_z)
                )
            *180/np.pi
        )
        yaw_data.append(
            np.arctan2(
                2*(quat_w*quat_z+quat_x*quat_y),
                quat_w**2+quat_x**2-quat_y**2-quat_z**2
            )
            *180/np.pi
        )

    # Format into position and orientation data
    position = [x_data, y_data, z_data]
    orientation = [roll_data, pitch_data, yaw_data]

    return position, orientation

# pylint: disable=too-many-locals
def extract_source_position_trajectory(test_folder_filepath, test_data):
    """This function extracts the source position trajectory from a comments file.

    Every cost function config file should come with keys in the params dictionary
    which describe the (x, y, z), possibly time varying, position of the optimal
    point. These descriptions will be parsed into sympy expressions. If the position
    of the optimal point varies with time, this sympy expression will be evaluated
    with input timestamps to calculate the trajectory of the point. These results are
    organized into the dictionary below.

    source_info = {
        "x_init": float,
        "y_init": float,
        "z_init": float,
        "time_varying": boolean,
        "x_data": list,
        "y_data": list,
        "z_data": list
    }
    """

    # Initialize the comment file filepath
    path = str(test_folder_filepath+"/comments.txt")
    # Open the comments file and extract a config dictionary
    with open(path, mode='r', newline="", encoding='utf-8') as file:
        # Read the file
        text = file.read()
        # Isolate the cost function configuration
        # The cost function config will be after the phrase "Cost Function Configuration Used:"
        config_text = text.split("Cost Function Configuration Used:")[1]
        # The cost function config will be before the separator string --------
        config_text = config_text.split("---------")[0]
        # Remove any '\n' characters from this string
        config_text = config_text.replace("\n","")
        # Convert this string to a dictionary
        config_dict = json.loads(config_text)

    # Get the cost function key
    cost_funct_dict = config_dict["CostFunction"]
    # Get the params key
    params_dict = cost_funct_dict["params"]
    # Check if the optimal expression is in this params
    # dictionary or if we need to look through substitutions
    if ("x_optimal" in params_dict) or ("y_optimal" in params_dict) or ("z_optimal" in params_dict):
        input_dict = params_dict
    else:
        # Get the substitutions key
        input_dict = params_dict["substitutions"]

    # Initialize the results dictionary
    source_info = {}

    # Extract the cost value timestamps
    tstamps = test_data["cost_tstamps"]

    # Extract the optimal x position history
    x_init, x_data = parse_optimal_position_expression(input_dict, 'x_optimal', tstamps)
    # Extract the optimal y position history
    y_init, y_data = parse_optimal_position_expression(input_dict, 'y_optimal', tstamps)
    # Extract the optimal z position history
    z_init, z_data = parse_optimal_position_expression(input_dict, 'z_optimal', tstamps)

    # Check if the source is time varying
    time_varying = bool(x_data) or bool(y_data) or bool(z_data)

    # Organize the results
    source_info["x_init"] = x_init
    source_info["y_init"] = y_init
    source_info["z_init"] = z_init
    source_info["time_varying"] = time_varying
    source_info["x_data"] = x_data
    source_info["y_data"] = y_data
    source_info["z_data"] = z_data

    return source_info

def create_experiment_parameters_dict(config_files_dict):
    """This creates a dictionary of config files and objects used in an experiment."""

    # Define a dictionary of experiment parameters
    experiment_params = {}

    # If the rotate frame config exists
    if "rotate_frame_config" in config_files_dict:
        # Save the rotate frame config used as a string
        with open(config_files_dict["rotate_frame_config"], 'r', encoding='utf-8') as file:
            # Save the config file as a string
            experiment_params["rotate_frame_config"] = file.read()

        # Initialize lists to hold names and objects written as strings
        experiment_params["rotate_frame_names"] = []
        experiment_params["rotate_frame_objects"] = []

        with open(config_files_dict["rotate_frame_config"], 'r', encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)
            # Loop through the entries in the config dict
            for entry in config_dict:
                # Each entry name denotes the name of the velocity controller topic to publish to
                experiment_params["rotate_frame_names"].append(entry)
                # Get the velocity controller dictionary
                velo_controller_dict = config_dict[entry]
                # Parse the spin profile configuration
                spin_profile_obj_str = parse_object_into_str(velo_controller_dict)
                # Append to list
                experiment_params["rotate_frame_objects"].append(spin_profile_obj_str)



    # If the transform config exists
    if "transform_config" in config_files_dict:
        # Save the transform config used as a string
        with open(config_files_dict["transform_config"], 'r', encoding='utf-8') as file:
            # Save the config file used as a string
            experiment_params["transform_config"] = file.read()
        # Initialize lists to hold names and objects written as strings
        experiment_params["transform_names"] = []
        experiment_params["transform_objects"] = []

        with open(config_files_dict["transform_config"], 'r', encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)
            # Loop through the entries in the config dict
            for entry in config_dict:
                # Each entry name denotes the name of the rotate frame transform matrix
                experiment_params["transform_names"].append(entry)
                # Get the transform dictionary
                transform_dict = config_dict[entry]
                # Parse the transform configuration
                transform_obj_str = parse_object_into_str(transform_dict)
                # Append to list
                experiment_params["transform_objects"].append(transform_obj_str)



    # If the cost function config exists
    if "cost_function_config" in config_files_dict:
        # Save the cost function config used as a string
        with open(config_files_dict["cost_function_config"], 'r', encoding='utf-8') as file:
            # Save the config file used as a string
            experiment_params["cost_function_config"] = file.read()

        with open(config_files_dict["cost_function_config"], 'r', encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)
            # Save the cost function object used as a string
            cost_funct_dict = config_dict["CostFunction"]
            experiment_params["cost_function_object"] = parse_object_into_str(cost_funct_dict)
            # Save the noise object used as a string
            noise_obj_dict = config_dict["Noise"]
            experiment_params["noise_object"] = parse_object_into_str(noise_obj_dict)



    # If the filter config exists
    if "filter_config" in config_files_dict:
        # Save the filter config used as a string
        with open(config_files_dict["filter_config"], 'r', encoding='utf-8') as file:
            # Save the config file used as a string
            experiment_params["filter_config"] = file.read()



    # If the controller config exists
    if "controller_config" in config_files_dict:
        # Save the controller config used as a string
        with open(config_files_dict["controller_config"], 'r', encoding='utf-8') as file:
            # Convert the file into a string
            experiment_params["controller_config"] = file.read()
        # Save the controller object used as a string
        with open(config_files_dict["controller_config"], 'r', encoding='utf-8') as file:
            # Convert the file into a dictionary
            config_dict = json.load(file)
            # Get the controller object string
            experiment_params["controller_object"] = parse_object_into_str(config_dict)

    return experiment_params

# pylint: disable=too-many-statements
def create_comment_file(date_time_str, timekeeper_info, experiment_params, filepath):
    """This function creates a comments file to reference what was used for an experiment."""

    # Unpack the timekeeper info
    start_time = timekeeper_info["start_time"]
    timekeeper_mode = timekeeper_info["timekeeper_mode"]

    # Define a string to separate the comment file sections
    separator = "-------------------------------------------------------------------"
    # Create the comments file
    with open(filepath, mode="w", encoding='utf-8') as comment:
        comment.write(separator)

        # Leave space at the top for user comments
        comment.write("\nUser Comments:")
        comment.write("\n")
        comment.write("\n")
        comment.write("\n")
        comment.write("\n"+separator)

        # Record the date and time the simulation was conducted
        comment.write("\nExperiment Conducted At:")
        comment.write("\n"+date_time_str)
        comment.write("\n"+separator)

        # Record the timekeeper start time
        comment.write("\nTimekeeper Information:")
        comment.write("\nStart Time:")
        comment.write("\n"+start_time)
        comment.write("\nTimekeeper Mode:")
        comment.write("\n"+timekeeper_mode)
        comment.write("\n"+separator)

        # If the rotate frame config exists
        if "rotate_frame_config" in experiment_params:
            # Record the rotate frame config file used
            comment.write("\nRotate Frame Configuration Used:")
            comment.write("\n"+experiment_params["rotate_frame_config"] )
            comment.write("\n"+separator)

            # Record the rotate frame objects used
            for entry in enumerate(experiment_params["rotate_frame_names"]):
                # Get the index
                index = entry[0]
                # Get the velocity controller name
                name = entry[1]
                # Get the object string
                obj_str = experiment_params["rotate_frame_objects"][index]
                # Record the object string
                comment.write("\nRotate Frame Velocity Controller Name:")
                comment.write("\n"+name)
                comment.write("\n")
                comment.write("\nSpin Profile Object Used:")
                comment.write("\n"+obj_str)
                comment.write("\n"+separator)

        # If the transform config exists
        if "transform_config" in experiment_params:
            # Record the transform config file used
            comment.write("\nTransform Configuration Used:")
            comment.write("\n"+experiment_params["transform_config"] )
            comment.write("\n"+separator)

            # Record the transform objects used
            for entry in enumerate(experiment_params["transform_names"]):
                # Get the index
                index = entry[0]
                # Get the name
                name = entry[1]
                # Get the object string
                obj_str = experiment_params["transform_objects"][index]
                # Record the object string
                comment.write("\nTransform Name:")
                comment.write("\n"+name)
                comment.write("\n")
                comment.write("\nTransform Object Used:")
                comment.write("\n"+obj_str)
                comment.write("\n"+separator)

        # If the cost function config exists
        if "cost_function_config" in experiment_params:
            # Record the cost function used
            comment.write("\nCost Function Configuration Used:")
            comment.write("\n"+experiment_params["cost_function_config"])
            comment.write("\n"+separator)

            # Record the cost function object used
            comment.write("\nCost Function Object Used:")
            comment.write("\n"+experiment_params["cost_function_object"])
            comment.write("\n"+separator)

            # Record the noise function object used
            comment.write("\nNoise Object Used:")
            comment.write("\n"+experiment_params["noise_object"])
            comment.write("\n"+separator)

        # If there is physical sensor information to document
        if "physical_sensor_name" in experiment_params:
            # Record the name of the sensor used
            comment.write("\nPhysical Sensor Used:")
            comment.write("\n"+experiment_params["physical_sensor_name"])
            # Record the type of data being collected
            comment.write("\nType of Data Being Collected:")
            comment.write("\n"+experiment_params["physical_sensor_datatype"])
            # Record the units of the data being collected
            comment.write("\nData Units:")
            comment.write("\n"+experiment_params["physical_sensor_units"])
            comment.write("\n"+separator)

        # If the filter config exists
        if "filter_config" in experiment_params:
            # Record the filter used
            comment.write("\nFilter Configuration Used:")
            comment.write("\n"+experiment_params["filter_config"])
            comment.write("\n"+separator)

        # If the controller config exists
        if "controller_config" in experiment_params:
            # Record the controller used
            comment.write("\nController Configuration Used:")
            comment.write("\n"+experiment_params["controller_config"])
            comment.write("\n"+separator)

            # Record the controller object used
            comment.write("\nController Object Used:")
            comment.write("\n"+experiment_params["controller_object"])
            comment.write("\n"+separator)
        