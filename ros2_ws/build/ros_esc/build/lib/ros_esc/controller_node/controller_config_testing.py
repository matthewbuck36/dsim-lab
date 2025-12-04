#!/usr/bin/env python3

"""This script can be used to test a controller config design on some
test inputs. This allows the user to verify their controller configuration file
is working without launching an entire experiment. The outputs of the custom
controller will be printed to the terminal.
"""

import os
import json
import numpy as np # pylint: disable=unused-import
from ros_esc.config_parsing import parse_object_config

def main():
    """This function tests the controller config file."""

    ### Please enter the filepath to the configuration file to be tested
    # pylint: disable=line-too-long
    filepath = os.path.expanduser(
        "~/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files" +
        "/turtlebot_vehicle/adaptive_methods/rmsprop_controller_full_rotation.json"
    )
    # pylint: enable=line-too-long

    # Open the json file
    with open(filepath, encoding='utf-8') as file:
        # Convert into a dictionary
        config_dict = json.load(file)
    # Parse that configuration dictionary
    # Get the initialized controller object
    controller_obj = parse_object_config(config_dict)

    # Initialize some test inputs
    # Note each of the following lines is in this format:
    # [input_val_1, input_val_2]
    test_inputs = [
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,1,1,1],
    ]

    # Initialize some test states
    # Note each of the following lines is in this format:
    # [x_pos, y_pos, z_pos, roll, pitch, yaw]
    test_states = [
        [0,1,0,0,0,0],
        [1,1,0,0,0,1/2*np.pi],
        [2,1,0,0,0,1/4*np.pi],
        [1.5,2,0,0,0,-1/4*np.pi],
        [1,3,0,0,0,-1/2*np.pi]
    ]

    # Initialize some test timestamps
    test_tstamps = np.linspace(0, 4, 5)

    # Loop over all the test inputs
    for entry in enumerate(test_inputs):
        # Get the index
        index = entry[0]
        # Get the timestamp
        time = test_tstamps[index]
        # Get the states
        states = test_states[index]
        # Get the test inputs
        inp_vals = test_inputs[index]
        # Plug the information into the controller object
        output = controller_obj.controller_output(time, states, inp_vals)
        # Print the result to terminal
        print(output)

if __name__ == "__main__":
    main()
