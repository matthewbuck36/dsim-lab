#!/usr/bin/env python3

"""This script can be used to test a custom rotate frame config file.
This allows the user to verify their rotate frame configuration is
working without launching an entire experiment. The outputs of this
script is a printout of the commanded velocities to the desired
velocity controller commands topic.
"""

import os
import json
import numpy as np
from ros_esc.config_parsing import parse_object_config

# pylint: disable=too-many-locals

def main():
    """This function tests the custom rotate frame config file."""

    ### Please enter the filepath to the configuration file to be tested
    # pylint: disable=line-too-long
    filepath = os.path.expanduser(
        "~/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node"+
        "/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json"
    )
    # pylint: enable=line-too-long

    # Initialize a list to hold topic names
    controller_names = []
    # Initialize a list to hold spin profile objects
    objects_list = []

    # Open the json file
    with open(filepath, encoding='utf-8') as file:
        # Convert into a dictionary
        config_dict = json.load(file)
    # Loop through the entries in the config dict
    for entry in config_dict:
        # Get the velocity controller dictionary
        velo_controller_dict = config_dict[entry]
        # Each entry name denotes the name of the velocity controller topic to publish to
        controller_names.append(entry)
        # Parse the spin profile configuration
        spin_profile_obj = parse_object_config(velo_controller_dict)
        # Append to list
        objects_list.append(spin_profile_obj)

    # Initialize some test timestamps
    test_timestamps = np.linspace(0, 9, 10)

    # Initialize some test angular positions
    # Note each of the following lines represents an array in this format:
    # [encoder_value_1, encoder_value_2, ... ]
    test_angular_positions = [
        [-np.pi/2],
        [-np.pi/4],
        [0],
        [np.pi/4],
        [np.pi/2],
        [np.pi/2],
        [np.pi/4],
        [0],
        [-np.pi/4],
        [-np.pi/2],
    ]

    # Initialize some test spin directions
    # Note each of the following lines represents a list in this format:
    # [spin_dir_frame_1, spin_dir_frame_2, ... ]
    # Note True denotes ccw rotation, False deontes cw rotation
    test_spin_directions = [
        [True],
        [True],
        [True],
        [True],
        [True],
        [False],
        [False],
        [False],
        [False],
        [False],
    ]

    # Print the topic names the velocity commands are being published to
    print(controller_names)

    # Loop over all the test inputs
    for item in enumerate(test_timestamps):
        # Get the index
        index = item[0]
        # Get the timestamp
        time = item[1]
        # Get the angular positions
        angular_position_array = test_angular_positions[index]
        # Get the test spin_directions
        spin_directions_list = test_spin_directions[index]

        # Create a list of output velocities being
        # sent to the velocity command topics
        velocity_cmds = []

        # Loop over all the spin profile objects
        for entry in enumerate(objects_list):
            # Get the index
            index = entry[0]
            # Get the spin profile object
            spin_profile = entry[1]
            # Get the angular position for this specific rotating frame
            phi = angular_position_array[index]
            # Get the spin direction for this specific rotating frame
            direction = spin_directions_list[index]
            # Evaluate this information with the spin profile object
            velocity = spin_profile.velocity_output(time, phi, direction)
            # Append to list
            velocity_cmds.append(velocity)

        # Print the velocity commands to terminal
        print(velocity_cmds)

if __name__ == "__main__":
    main()
