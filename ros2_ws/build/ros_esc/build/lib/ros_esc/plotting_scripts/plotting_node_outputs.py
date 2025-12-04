#!/usr/bin/env python3

"""This script holds helper functions used in plotting data from the ROS nodes."""

import numpy as np
from ros_esc.plotting_scripts.plotting_helper_functions import plot_time_history

def cost_history(plot_style, test_data, filepath):
    """This function plots the time history of all the cost values on the same plot."""

    # Set the figure name to save the image as
    plot_style["figure_name"] = "cost_value_history"
    # Set the y axis name and data label
    plot_style["yaxis_name"] = "Cost Value ($J$)"

    # Collect all the cost value data
    cost_data = test_data["cost_data"]
    # Get the number of different cost value sequences to plot
    num_seq = np.shape(cost_data)[1]
    # If we have more than one sequence, add a legend automatically
    if num_seq > 1:
        plot_style["add_legend"] = True
    # Initialize a maximum cost value
    max_val = None
    # Initialize a minimum cost value
    min_val = None
    # Initialize the data labels list
    labels = []
    # Initialize the data list
    data_list = []

    # Loop over all cost outputs
    for i in range(num_seq):
        # Get the particular cost value sequence
        cost_seq = cost_data[:, i]
        # Append this label to the list
        labels.append(f'Sensor {i+1} Cost')
        # Append this data to the list
        data_list.append(cost_seq)

        # If we don't have a max cost value yet
        if max_val is None:
            max_val = max(cost_seq)
            min_val = min(cost_seq)

        # If we do have values to compare to
        else:
            # Update values if needed
            max_val = max([max_val, max(cost_seq)])
            min_val = min([min_val, min(cost_seq)])

    # Set the data labels
    plot_style["data_labels"] = labels
    # Round the axis limits
    max_val = round(max_val, 0)
    min_val = round(min_val, 0)

    # If the y axis limits are not already configured
    if "yaxis_limits" not in plot_style:
        # Set the y axis limits to default values
        plot_style["yaxis_limits"] = [min_val, max_val]
        # Set the tick locations
        loc = np.linspace(min_val, max_val, 6)
        # Set the y axis ticks to default values
        plot_style["yaxis_tick_locations"] = [round(x,1) for x in loc]
        # # Format the labels
        plot_style["yaxis_tick_labels"] = plot_style["yaxis_tick_locations"]

    # Override the plot linewidth
    preset_linewidth = plot_style["linewidth"]
    plot_style["linewidth"] = 0.5

    # Create the plot
    plot_time_history(
        plot_style,
        test_data["cost_tstamps"],
        data_list,
        filepath
    )

    # Delete the default y axis limits
    del plot_style["yaxis_limits"]
    # Delete the default y axis ticks
    if "yaxis_tick_locations" in plot_style:
        del plot_style["yaxis_tick_locations"]
        del plot_style["yaxis_tick_labels"]
    # Reset to the preset linewidth
    plot_style["linewidth"] = preset_linewidth

def filter_history(plot_style, test_data, filepath):
    """This function plots the time history of all the filter output values in separate plots"""

    # Collect all the filter data
    filter_data = test_data["filter_data"]
    # Get the number of filter outputs to plot
    num_outputs = np.shape(filter_data)[1]
    # Loop over all filter outputs
    for i in range(num_outputs):
        # Get the particular filter output data
        output_data = filter_data[:, i]

        # Set the figure name to save the image as
        plot_style["figure_name"] = f"filter_value_{i+1}_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = f"Filter Output Value ($z_{i+1}$)"
        plot_style["data_labels"] = [f"Filter Output Value ($z_{i+1}$)"]

        # Do not create a legend
        plot_style["add_legend"] = False

        # If the y axis limits are not already configured
        if "yaxis_limits" not in plot_style:
            # Get the min and max filter value
            max_val = max(output_data[5:])
            min_val = min(output_data[5:])
            # Round to one decimal place
            max_val = round(max_val, 1)
            min_val = round(min_val, 1)
            # Get the larger magnitude of the two
            scale = max(np.abs(max_val), np.abs(min_val))

            # Set the y axis limits to default values
            plot_style["yaxis_limits"] = [scale*-1.5, scale*1.5]
            # Set the y axis ticks to default values
            plot_style["yaxis_tick_locations"] = [
                -1.5*scale, -1*scale, -0.5*scale,
                0, 0.5*scale, scale, 1.5*scale
            ]
            # Format the labels
            plot_style["yaxis_tick_labels"] = [
                f"{x:.2f}" for x in plot_style["yaxis_tick_locations"]
            ]

            # Override the plot linewidth
            preset_linewidth = plot_style["linewidth"]
            plot_style["linewidth"] = 0.5

        # Create the plot
        plot_time_history(
            plot_style,
            test_data["filter_tstamps"],
            output_data,
            filepath
        )

        # Delete the default y axis limits
        del plot_style["yaxis_limits"]
        # Delete the default y axis ticks
        if "yaxis_tick_locations" in plot_style:
            del plot_style["yaxis_tick_locations"]
            del plot_style["yaxis_tick_labels"]
        # Reset to the preset linewidth
        plot_style["linewidth"] = preset_linewidth

def control_history(variable, plot_style, test_data, filepath):
    """This function sets up additional style parameters for a control value time history plot."""

    warn_msg = "Control history variable must be 'Vx', 'Vy', 'Vz', 'Wx', 'Wy', or 'Wz'."
    assert variable in ["Vx", "Vy", "Vz", "Wx", "Wy", "Wz"], warn_msg

    if variable == "Vx":
        # Get the control data
        control = test_data["control_data"][:,0]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "control_value_vx_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Velocity ($V_x$) [m/s]"
        plot_style["data_labels"] = [r"Velocity ($V_x$) [m/s]"]

    elif variable == "Vy":
        # Get the control data
        control = test_data["control_data"][:,1]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "control_value_vy_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Velocity ($V_y$) [m/s]"
        plot_style["data_labels"] = [r"Velocity ($V_y$) [m/s]"]

    elif variable == "Vz":
        # Get the control data
        control = test_data["control_data"][:,2]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "control_value_vz_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Velocity ($V_z$) [m/s]"
        plot_style["data_labels"] = [r"Velocity ($V_z$) [m/s]"]

    elif variable == "Wx":
        # Get the control data
        control = test_data["control_data"][:,3]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "control_value_wx_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Angular Velocity ($\omega_x$) [rad/s]"
        plot_style["data_labels"] = [r"Angular Velocity ($\omega_x$) [rad/s]"]

    elif variable == "Wy":
        # Get the control data
        control = test_data["control_data"][:,4]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "control_value_wy_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Angular Velocity ($\omega_y$) [rad/s]"
        plot_style["data_labels"] = [r"Angular Velocity ($\omega_y$) [rad/s]"]

    else:
        # Get the control data
        control = test_data["control_data"][:,5]
        # Set the figure name to save the image as
        plot_style["figure_name"] = "control_value_wz_history"
        # Set the y axis name and data label
        plot_style["yaxis_name"] = r"Angular Velocity ($\omega_z$) [rad/s]"
        plot_style["data_labels"] = [r"Angular Velocity ($\omega_z$) [rad/s]"]

    # Do not create a legend
    plot_style["add_legend"] = False

    # If the y axis limits are not already configured
    if "yaxis_limits" not in plot_style:
        # Get the min and max control
        max_val = max(control)
        min_val = min(control)
        # Round to one decimal place
        max_val = round(max_val, 1)
        min_val = round(min_val, 1)
        # Get the larger magnitude of the two
        scale = max(np.abs(max_val), np.abs(min_val))

        # Set the y axis limits to default values
        plot_style["yaxis_limits"] = [scale*-1.5, scale*1.5]
        # Set the y axis ticks to default values
        plot_style["yaxis_tick_locations"] = [
            -1.5*scale, -1*scale, -0.5*scale,
            0, 0.5*scale, scale, 1.5*scale
        ]
        # Format the labels
        plot_style["yaxis_tick_labels"] = [f"{x:.2f}" for x in plot_style["yaxis_tick_locations"]]

        # Override the plot linewidth
        preset_linewidth = plot_style["linewidth"]
        plot_style["linewidth"] = 0.5

    # Create the plot
    plot_time_history(
        plot_style,
        test_data["control_tstamps"],
        control,
        filepath
    )

    # Delete the default y axis limits
    del plot_style["yaxis_limits"]
    # Delete the default y axis ticks
    if "yaxis_tick_locations" in plot_style:
        del plot_style["yaxis_tick_locations"]
        del plot_style["yaxis_tick_labels"]
    # Reset to the preset linewidth
    plot_style["linewidth"] = preset_linewidth
