#!/usr/bin/env python3

"""This script holds helper functions used in live plots created by the data collection node."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

# Initialize variables for live plots
# pylint: disable=too-many-statements
def initialize_animation(live_plotting_mode):
    """This initializes a dictionary where live plotting data is stored."""

    # Initialize the live plots dictionary
    live_plot_data = {}
    # Set the live plotting mode
    live_plot_data["mode"] = live_plotting_mode

    # Initialize colors
    live_plot_data["colors"] = ['k', 'b', 'r', 'g', 'darkorange', 'm', 'c']

    # Initialize lists to contain position data
    live_plot_data["x_position"] = []
    live_plot_data["y_position"] = []
    live_plot_data["z_position"] = []
    live_plot_data["position_tstamps"] = []

    # Initialize lists to contain cost value data
    live_plot_data["num_distinct_cost_values"] = None
    live_plot_data["cost_value_tstamps"] = []

    # Set up a Matplotlib figure
    fig = plt.figure(figsize=(12,24))
    gridspec_obj = gridspec.GridSpec(2, 2, width_ratios=[1,2])
    # Create the plots in the left column
    ax1 = fig.add_subplot(gridspec_obj[0,0])
    ax2 = fig.add_subplot(gridspec_obj[1,0])
    # Create the plots in the right column
    ax3 = fig.add_subplot(gridspec_obj[0,1])
    ax4 = fig.add_subplot(gridspec_obj[1,1])

    # Create x value time history plot
    ax1.set_title("X Position Time History")
    xhist_plot, = ax1.plot(
        [], [], label="X Position", color="black", markersize=5
    )
    ax1.set_xlabel("Time [sec]")
    ax1.set_ylabel("Position [m]")
    ax1.grid()
    # Save to dictionary
    live_plot_data["xhist_plot"] = xhist_plot
    live_plot_data["ax1"] = ax1

    # Create y value time history plot
    ax2.set_title("Y Position Time History")
    yhist_plot, = ax2.plot(
        [], [], label="Y Position", color="black", markersize=5
    )
    ax2.set_xlabel("Time [sec]")
    ax2.set_ylabel("Position [m]")
    ax2.grid()
    # Save to dictionary
    live_plot_data["yhist_plot"] = yhist_plot
    live_plot_data["ax2"] = ax2

    # Create cost value time history plot
    ax3.set_title("Cost Value Time History")
    ax3.set_xlabel("Time [sec]")
    ax3.set_ylabel("Cost Value")
    ax3.grid()
    ax3.legend()
    # Save to dictionary
    live_plot_data["ax3"] = ax3

    # If we are in 2D mode
    if live_plotting_mode == "2D":
        # Create a plot displaying the path of the vehicle
        ax4.set_title("Trajectory of Vehicle")
        trajectory_plot, = ax4.plot(
            [], [], label="Trajectory", color="black", markersize=5
        )
        ax4.set_xlabel("X position [m]")
        ax4.set_ylabel("Y position [m]")
        ax4.grid()
        # Save to dictionary
        live_plot_data["trajectory_plot"] = trajectory_plot
        live_plot_data["ax4"] = ax4

    # If we are in 3D mode
    elif live_plotting_mode == "3D":
        # Create z value time history plot
        ax4.set_title("Z Position Time History")
        zhist_plot, = ax4.plot(
            [], [], label="Z Position", color="black", markersize=5
        )
        ax4.set_xlabel("Time [sec]")
        ax4.set_ylabel("Position [m]")
        ax4.grid()
        # Save to dictionary
        live_plot_data["zhist_plot"] = zhist_plot
        live_plot_data["ax4"] = ax4

    return fig, live_plot_data

# pylint: disable=unused-argument
def update_plot(frame, live_plot_data):
    """This function updates the live plots with the most recent data points."""

    # Select how much time we display in a live plot in seconds
    time_hist = 60

    # Check to make sure we have data
    if (
        live_plot_data["position_tstamps"] is not None
        and 
        len(live_plot_data["position_tstamps"]) > 0
    ):
        # Reduce the timestamp data if needed, only keep the most recent time history of data
        num_datapoints_to_cut, live_plot_data["position_tstamps"] = reduce_timestamps(
            time_hist, live_plot_data["position_tstamps"]
        )
        # Trim the position data based on trimmed position timestamp data
        live_plot_data["x_position"] = live_plot_data["x_position"][num_datapoints_to_cut:]
        live_plot_data["y_position"] = live_plot_data["y_position"][num_datapoints_to_cut:]
        live_plot_data["z_position"] = live_plot_data["z_position"][num_datapoints_to_cut:]

    # Check to make sure we have data
    if (
        live_plot_data["cost_value_tstamps"] is not None
        and
        len(live_plot_data["cost_value_tstamps"]) > 0
    ):
        # Reduce the timestamp data
        num_datapoints_to_cut, live_plot_data["cost_value_tstamps"] = reduce_timestamps(
            time_hist, live_plot_data["cost_value_tstamps"]
        )

        # Reduce data for all the distinct cost values based on trimmed cost timestamp data
        for i in range(live_plot_data["num_distinct_cost_values"]):
            live_plot_data[f"cost_value_{i}"] = live_plot_data[f"cost_value_{i}"][num_datapoints_to_cut:]


    # Update the plots with the new x, y data
    live_plot_data["xhist_plot"].set_data(
        live_plot_data["position_tstamps"],
        live_plot_data["x_position"]
    )
    live_plot_data["yhist_plot"].set_data(
        live_plot_data["position_tstamps"],
        live_plot_data["y_position"]
    )

    # Update the plot with new cost value data
    if live_plot_data["num_distinct_cost_values"] is not None:
        # Loop over all distinct cost values
        for i in range(live_plot_data["num_distinct_cost_values"]):
            # Set the data for this distinct cost value line
            live_plot_data[f"cost_value_line_{i}"].set_data(
                live_plot_data["cost_value_tstamps"],
                live_plot_data[f"cost_value_{i}"]
            )

    # If we are using the 2D live plotting mode
    if live_plot_data["mode"] == "2D":
        # Update the trajectory plot
        live_plot_data["trajectory_plot"].set_data(
            live_plot_data["x_position"],
            live_plot_data["y_position"]
        )

    # If we are using the 3D live plotting mode
    elif live_plot_data["mode"] == "3D":
        # Update the plot with new z data
        live_plot_data["zhist_plot"].set_data(
            live_plot_data["position_tstamps"],
            live_plot_data["z_position"]
        )

    # Adjust the axis scaling on all plots
    live_plot_data["ax1"].relim()
    live_plot_data["ax1"].autoscale_view()
    live_plot_data["ax2"].relim()
    live_plot_data["ax2"].autoscale_view()
    live_plot_data["ax3"].relim()
    live_plot_data["ax3"].autoscale_view()
    live_plot_data["ax4"].relim()
    live_plot_data["ax4"].autoscale_view()
    
    return live_plot_data

def reduce_timestamps(time_hist, tstamp_data):
    """This reduces the total number of timestamps to only keep the most recent data."""

    # Get the current value
    current_time = tstamp_data[-1]
    # If the current time is less then the requested time history window
    if current_time < time_hist:
        # We do not have to cut any timestamps
        num_datapoints_to_cut = 0
        # The new timestamps are the same as the old ones
        new_tstamp_data = tstamp_data
    
    # If the current time is greater than the requested time history window,
    # we cut timestamps from the beginning of the timestamp data
    else:
        # Calculate the furthest back timestamp in the past we will consider
        past_tstamp = current_time - time_hist

        # Define a new list of timestamp data that cuts all
        # timesteps before the above past timestamp
        new_tstamp_data = [t for t in tstamp_data if t > past_tstamp]

        # Compare the lengths of these two lists
        # to determine how many tstamps were cut
        num_datapoints_to_cut = len(tstamp_data) - len(new_tstamp_data)

    return num_datapoints_to_cut, new_tstamp_data

def reduce_data(n, data):
    """This reduces the input data by the requested number of samples."""

    # Remove the first n number of samples from the data 
    return data[n:]
