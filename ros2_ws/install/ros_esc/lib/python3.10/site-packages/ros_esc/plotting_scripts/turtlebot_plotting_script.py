#!/usr/bin/env python3

"""This script can be used to plot the data collected in a test folder.
This script can make plots to display time histories of the cost value,
filter values, controller commands, as well as a plot of the vehicle's
path. The user has to option to modify some plotting settings. All
figures are saved within the test folder the data was gathered from.
This script was specifically written for the turtlebot mounted with a
rotating sensor frame.
"""

import os
from ros_esc.helper_functions import extract_test_data, extract_source_position_trajectory
from ros_esc.plotting_scripts.plotting_helper_functions import init_plot_style
from ros_esc.plotting_scripts.plotting_vehicle_states import position_history, angular_position_history
from ros_esc.plotting_scripts.plotting_node_outputs import cost_history, filter_history, control_history
from ros_esc.plotting_scripts.plotting_trajectories import plot_2d_path


def main():
    """This function creates plots to visualize the test data."""

    # Specify plot style variables here
    plot_style = init_plot_style()

    # Set override to true if you want to override figures already created in a test folder
    override = False

    # Specify the directory where the test data folders are saved
    # pylint: disable=line-too-long
    directory = os.path.expanduser(
        '~/Documents/Gazebo_Simulations'
    )
    # pylint: enable=line-too-long

    # Get a list of the contents of this directory
    directory_list = os.listdir(directory)
    # Loop through the contents of the list
    for item in directory_list:
        # Check if this item is a test folder
        if item[:4] == "Test":
            # Specify the directory to this test folder
            test_folder_directory = f'{directory}/{item}'
            # Get a list of the contents of this test folder directory
            test_folder_contents = os.listdir(test_folder_directory)

            # Check if there are already figures here
            figs_present = False
            for file in test_folder_contents:
                if file[-3:] == "png":
                    figs_present = True

            # If there are figures present in this test folder and we don't
            # want to override them, simply continue to the next test folder
            if figs_present and override is False:
                continue
            # If there are figures present in this test folder and we do
            # want to override them, then make new figures. If there are
            # no figures in this test folder, make new figures.
            make_figures(test_folder_directory, test_folder_contents, plot_style)

# pylint: disable=too-many-locals
def make_figures(test_folder_directory, test_folder_contents, plot_style):
    """This function obtains the test data from the csv files, then creates plots."""

    # Extract the test data
    test_data = extract_test_data(test_folder_directory, test_folder_contents)

    # Read the comment file
    source_info = extract_source_position_trajectory(test_folder_directory, test_data)

    # Plot the x value time history
    position_history('X', plot_style, test_data, test_folder_directory)
    # Plot the y value time history
    position_history('Y', plot_style, test_data, test_folder_directory)
    # Plot the yaw angle time history
    angular_position_history('Yaw', plot_style, test_data, test_folder_directory)

    # Plot the cost values versus time
    cost_history(plot_style, test_data, test_folder_directory)

    # Plot the filter output values versus time
    filter_history(plot_style, test_data, test_folder_directory)

    # Plot the control values versus time
    control_history('Vx', plot_style, test_data, test_folder_directory)
    control_history('Wz', plot_style, test_data, test_folder_directory)

    # Plot the vehicle path
    plot_2d_path(
        plot_style, test_data,
        test_folder_directory, source_info=source_info
    )

    # Plot the vehicle path with the sensor trajectory
    # Plot the vehicle path
    plot_2d_path(
        plot_style, test_data,
        test_folder_directory, with_sensor_pose=True,
        source_info=source_info
    )

if __name__ == "__main__":
    main()
