#!/usr/bin/env python3

"""This script holds functions used in plotting vehicle position and angular position results."""

import numpy as np
from ros_esc.plotting_scripts.plotting_helper_functions import plot_time_history

def position_history(variable, plot_style, test_data, filepath):
    """This function sets up style parameters for a position value time history plot."""

    warn_msg = "Position history variable must be 'X', 'Y', or 'Z'."
    assert variable in ["X", "Y", "Z"], warn_msg

    if variable == "X":
        # Get the position data
        position = test_data["odom_position"][0]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "x_position_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = "X [m]"
        plot_style["data_labels"] = ["X [m]"]

    elif variable == "Y":
        # Get the position data
        position = test_data["odom_position"][1]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "y_position_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = "Y [m]"
        plot_style["data_labels"] = ["Y [m]"]

    else:
        # Get the position data
        position = test_data["odom_position"][2]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "z_position_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = "Z [m]"
        plot_style["data_labels"] = ["Z [m]"]

    # Do not create a legend
    plot_style["add_legend"] = False

    # If the y axis limits are not already configured
    if "yaxis_limits" not in plot_style:
        # Get the min and max position
        max_val = max(position)
        min_val = min(position)

        # Adjust the limits
        max_val = adjust_limit(max_val, "max")
        min_val = adjust_limit(min_val, "min")

        # Set the y axis limits to default values
        plot_style["yaxis_limits"] = [min_val, max_val]
        # Set the y axis tick locations and labels
        loc = np.linspace(min_val, max_val, 6)
        plot_style["yaxis_tick_locations"] = [round(x,1) for x in loc]
        plot_style["yaxis_tick_labels"] = plot_style["yaxis_tick_locations"]

    # Create the plot
    plot_time_history(
        plot_style,
        test_data["odom_tstamps"],
        position,
        filepath
    )

    # Delete the default y axis limits
    del plot_style["yaxis_limits"]
    # Delete the default y axis ticks
    if "yaxis_tick_locations" in plot_style:
        del plot_style["yaxis_tick_locations"]
        del plot_style["yaxis_tick_labels"]

def angular_position_history(variable, plot_style, test_data, filepath):
    """This function sets up style parameters for an angular position value time history plot."""

    warn_msg = "Position history variable must be 'Roll', 'Pitch', or 'Yaw'."
    assert variable in ["Roll", "Pitch", "Yaw"], warn_msg

    if variable == "Roll":
        # Get the angular position data
        angle = test_data["odom_orientation"][0]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "roll_angle_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Roll Angle ($\phi$) [deg]"
        plot_style["data_labels"] = [r"Roll Angle ($\phi$) [deg]"]

    elif variable == "Pitch":
        # Get the angular position data
        angle = test_data["odom_orientation"][1]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "pitch_angle_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Pitch Angle ($\theta$) [deg]"
        plot_style["data_labels"] = [r"Pitch Angle ($\theta$) [deg]"]

    else:
        # Get the angular position data
        angle = test_data["odom_orientation"][2]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "yaw_angle_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Yaw Angle ($\psi$) [deg]"
        plot_style["data_labels"] = [r"Yaw Angle ($\psi$) [deg]"]

    # Do not create a legend
    plot_style["add_legend"] = False

    # If the y axis limits are not already configured
    if "yaxis_limits" not in plot_style:
        # Set the y axis limits to default values
        plot_style["yaxis_limits"] = [-180, 180]
        # Set the y axis tick locations and labels
        plot_style["yaxis_tick_locations"] = [-180, -135, -90, -45, 0, 45, 90, 135, 180]
        plot_style["yaxis_tick_labels"] = [-180, -135, -90, -45, 0, 45, 90, 135, 180]

    # Create the plot
    plot_time_history(
        plot_style,
        test_data["odom_tstamps"],
        angle,
        filepath
    )

    # Delete the default y axis limits
    del plot_style["yaxis_limits"]
    # Delete the default y axis ticks
    if "yaxis_tick_locations" in plot_style:
        del plot_style["yaxis_tick_locations"]
        del plot_style["yaxis_tick_labels"]

def adjust_limit(value, type):
    """This adjust the axis limit to look nice."""

    if type == "max":
        limit = round(value, 0) + 1

    if type == "min":
        limit = round(value, 0) - 1

    return limit
