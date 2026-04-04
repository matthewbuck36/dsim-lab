#!/usr/bin/env python3

"""This script can be used to test a custom transform config file on some
test inputs. This allows the user to verify their transform configuration
is working without launching an entire experiment. The outputs of the
transform will be printed to the terminal.
"""

import os
import json
import numpy as np # pylint: disable=unused-import
from ros_esc.config_parsing import parse_object_config

# pylint: disable=too-many-locals

def main():
    """This function tests the custom transform config file."""

    ### Please enter the filepath to the configuration file to be tested
    # pylint: disable=line-too-long
    filepath = os.path.expanduser(
        "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/"+
        "transform_config_files/turtlebot_rotating_sensor.json"
    )
    # pylint: enable=line-too-long

    # Initialize a list to hold rotating frame names
    rotating_frame_names = []
    # Initialize a list to hold transform objects
    objects_list = []

    # Open the json file
    with open(filepath, encoding='utf-8') as file:
        # Convert into a dictionary
        config_dict = json.load(file)
    # Loop through the entries in the config dict
    for entry in config_dict:
        # Get the transform config dictionary
        transform_obj_dict = config_dict[entry]
        # Each entry name denotes the name of the rotating frame
        rotating_frame_names.append(entry)
        # Parse the transform configuration
        transform_obj = parse_object_config(transform_obj_dict)
        # Append to list
        objects_list.append(transform_obj)

    # Initialize test encoder value data
    # Note each of the following lines represents an array in this format:
    # [encoder_value_1, encoder_value_2, ... ]
    test_angular_positions = [
        [-np.pi/2],
        [-np.pi/4],
        [0],
        [np.pi/4],
        [np.pi/2],
    ]

    # Initialize test odometry data
    # Note the odometry reading has the following form:
    # [x_pos, y_pos, z_pos, quat_w, quat_x, quat_y, quat_z]
    test_odom_data = [
        [0,0,0,1,0,0,1],
        [1,0,1,1,0,1,0],
        [0,1,0,0,1,0,1],
        [1,1,0,1,0,1,1],
        [0,1,1,1,1,1,1],
    ]

    # Note that for one position, you may have multiple encoder readings
    # corresponding to multiple rotating sensor frames, however you
    # will have only one odometry reading, which describes the position
    # of the vehicle's footprint w.r.t. the fixed odom frame

    # Define the input number
    input_num = 1
    # Loop through the test inputs
    for value in enumerate(test_odom_data):
        # Get the index
        index = value[0]
        # Get the odom data
        odom_data = value[1]
        # Get the list of encoder values at this position
        encoder_data_list = test_angular_positions[index]

        # Loop through all the encoder values in the list
        for entry in enumerate(encoder_data_list):
            # Get the sensor number as an index
            sensor_num = entry[0]
            # Get the encoder value
            angular_position = entry[1]
            # Get the transform object to use
            transform_object = objects_list[sensor_num]

            # Use the object to calculate the position
            transform_matrix = transform_object.transform_output(odom_data, angular_position)

            # Create an output message
            output = "\n".join([
                "Input "+str(input_num)+", Sensor "+str(sensor_num+1),
                "Transform Matrix: "+str(transform_matrix)
            ])
            # Print the output
            print(output)

        # Increment the input number
        input_num += 1

if __name__ == "__main__":
    main()
