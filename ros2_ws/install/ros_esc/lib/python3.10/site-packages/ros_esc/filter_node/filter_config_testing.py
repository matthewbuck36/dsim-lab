#!/usr/bin/env python3

"""This script can be used to test a custom filter config design on some
test inputs. This allows the user to verify their custom filter configuration
is working without launching an entire experiment. The outputs of the custom
filter will be printed to the terminal.
"""

import os
import json
import numpy as np # pylint: disable=unused-import
from ros_esc.config_parsing import parse_filter_config

def main():
    """This function tests the custom filter config file."""

    ### Please enter the filepath to the configuration file to be tested
    # pylint: disable=line-too-long
    filepath = os.path.expanduser(
        "~/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files"+
        "/turtlebot_vehicle/adaptive_methods/rmsprop_filter_full_rotation.json"
    )
    # pylint: enable=line-too-long

    # Open the json file
    with open(filepath, encoding='utf-8') as file:
        # Convert into a dictionary
        config_dict = json.load(file)
    # Parse that configuration dictionary, get the custom filter object
    custom_filter, z_vec = parse_filter_config(config_dict, [])

    # Print out the vector of filter states
    print("Custom filter initialized with the following state vector: ")
    print("\n"+str(z_vec))
    print("\nCustom filter output:\n")
    # Initialize the start time
    time = 0
    # Initialize a variable to hold the current time
    test_timestamps = [
        1, 2, 3, 4, 5
    ]
    # Initialize the test inputs to test the filter with
    test_inputs = [
        [50, np.pi],
        [55, 5/6*np.pi],
        [60, 3/4*np.pi],
        [65, 1/2*np.pi],
        [70, 1/4*np.pi],
    ]

    # Loop through the test inputs
    for value in enumerate(test_inputs):
        # Get the index
        index = value[0]
        # Get the test input, convert to an array
        filter_inp = np.array(value[1])
        # Get the current timestamp
        current_time = test_timestamps[index]
        # Get the time change
        dt = current_time - time # pylint: disable=invalid-name
        # Save the current time
        time = current_time
        # Compute the filter output
        output = custom_filter.filter_output(
            z_vec,
            filter_inp,
            current_time
        )
        # Print the filter output
        print("Filter output number: "+str(index+1))
        print(str(output))

        # Adjust the filter state
        z_vec = z_vec + dt * custom_filter.differential_equation(
            current_time,
            z_vec,
            filter_inp
        )
        # Print the filter state
        print("Filter state vector number: "+str(index+1))
        print(z_vec)
        print("")

if __name__ == "__main__":
    main()
