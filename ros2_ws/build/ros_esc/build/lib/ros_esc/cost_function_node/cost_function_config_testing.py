#!/usr/bin/env python3

"""This script can be used to test a cost function config design on some
test inputs. This allows the user to verify their cost function configuration
is working without launching an entire experiment. The outputs of the custom
cost function will be printed to the terminal.
"""

import os
import json
import numpy as np # pylint: disable=unused-import
from geometry_msgs.msg import Transform
from ros_esc.config_parsing import parse_object_config

# pylint: disable=too-many-locals
def main():
    """This function tests the cost function config file."""

    ### Please enter the filepath to the configuration file to be tested
    # pylint: disable=line-too-long
    filepath = os.path.expanduser(
        "~/ros2_ws/src/ros_esc/ros_esc/cost_function_node"+
        "/cost_function_config_files/static_2D_quadratic.json"
    )
    # pylint: enable=line-too-long

    # Open the json file
    with open(filepath, encoding='utf-8') as file:
        # Convert into a dictionary
        config_dict = json.load(file)

    # Assert that there are cost function and noise keys in this dictionary
    warn_msg = "There must be a 'CostFunction' key in file: "+filepath
    assert 'CostFunction' in config_dict, warn_msg
    warn_msg = "/n".join([
        "There must be a 'Noise' key in file: "+filepath+" \n",
        "If the user desires no noise to be added to the cost value ",
        "signal, please use the NoNoise object as a placeholder."
    ])
    assert 'Noise' in config_dict, warn_msg

    # Get the cost function object
    cost_function = parse_object_config(config_dict["CostFunction"])
    # Get the noise object
    noise_obj = parse_object_config(config_dict["Noise"])

    # Initialize some test timestamps
    test_timestamps = np.linspace(0, 3, 4)

    # Initialize some test transforms
    tform_1 = Transform()
    # Set the translation portion in the transform object
    tform_1.translation.x = 1.0
    tform_1.translation.y = 1.0
    tform_1.translation.z = 0.0
    # Set the quaternions in the transform object
    tform_1.rotation.w = 0.0
    tform_1.rotation.x = 0.0
    tform_1.rotation.y = 0.0
    tform_1.rotation.z = 0.0

    tform_2 = Transform()
    # Set the translation portion in the transform object
    tform_2.translation.x = 1.0
    tform_2.translation.y = 1.0
    tform_2.translation.z = 1.0
    # Set the quaternions in the transform object
    tform_2.rotation.w = 1.0
    tform_2.rotation.x = 1.57
    tform_2.rotation.y = 1.57
    tform_2.rotation.z = 1.0

    # Initialize some test inputs
    # Note each of the following lines is in this format:
    # input_1 = [sensor_1_transform, sensor_2_transform, ...]
    # input_2 = [sensor_1_transform, sensor_2_transform, ...]
    # and so on...
    test_inputs = [
        [tform_1],
        [tform_2],
        [tform_1],
        [tform_2],
    ]

    # Loop over all the test inputs
    for entry in enumerate(test_inputs):
        # Get the index
        index = entry[0]
        # Get the timestamp
        time = test_timestamps[index]
        # Get the list of transform objects
        points_list = entry[1]
        # Initialize a list of cost values
        cost_values = []

        # Loop through all the transform objects in the list
        for tform_obj in points_list:
            # Convert this object into a transformation matrix
            tform_matrix = create_transform_matrix(tform_obj)
            # Plug the transformation matrix and the current time into the cost function
            cost = cost_function.cost_output(time, tform_matrix)
            # Append to cost values
            cost_values.append(cost)

        # Plug the cost value into the noise object
        altered_cost_values = noise_obj.add_noise(time, np.array(cost_values))
        # Print the result to terminal
        print(altered_cost_values)

def create_transform_matrix(transform_object):
    """This converts a transform object into a transformation matrix."""

    # Get the translation portion in the transform object
    x_pos = transform_object.translation.x
    y_pos = transform_object.translation.y
    z_pos = transform_object.translation.z
    # Get the quaternions in the transform object
    quat_w = transform_object.rotation.w
    quat_x = transform_object.rotation.x
    quat_y = transform_object.rotation.y
    quat_z = transform_object.rotation.z

    # Package this position and orientation data into a homogeneous transformation matrix
    # Note this transformation matrix represents the position & orientation of the vehicle
    # in the stationary odometry frame. The rotation matrix was constructed using eqn (7b):
    # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    transform_matrix = np.array([
        [1-2*quat_y**2-2*quat_z**2, 2*quat_x*quat_y-2*quat_w*quat_z,
            2*quat_x*quat_z+2*quat_w*quat_y, x_pos],

        [2*quat_x*quat_y+2*quat_w*quat_z, 1-2*quat_x**2-2*quat_z**2,
            2*quat_y*quat_z-2*quat_w*quat_x, y_pos],

        [2*quat_x*quat_z-2*quat_w*quat_y, 2*quat_y*quat_z+2*quat_w*quat_x,
            1-2*quat_x**2-2*quat_y**2, z_pos],

        [0,0,0,1]
    ])

    return transform_matrix

if __name__ == "__main__":
    main()
