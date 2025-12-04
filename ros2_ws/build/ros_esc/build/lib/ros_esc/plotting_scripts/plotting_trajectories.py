#!/usr/bin/env python3

"""This script holds helper functions used in plotting seeker trajectories."""

import numpy as np
import matplotlib.pyplot as plt

# pylint: disable=too-many-locals
def plot_2d_path(plot_style, test_data, filepath, with_sensor_pose = False, source_info = None):
    """This plots the seeker trajectory in 2D space."""

    # Set the figure name
    plot_style["figure_name"] = "vehicle_path"

    # Get the x and y data from the test data dictionary
    x_data = test_data["odom_position"][0]
    y_data = test_data["odom_position"][1]

    # Create the figure
    # This removes the error from pylint about the variable 'ax'
    # pylint: disable=invalid-name
    fig, ax = plt.subplots(1, 1, figsize=plot_style["figsize"], constrained_layout=True) # pylint: disable=unused-variable
    # pylint: enable=invalid-name

    # Plot the seeker trajectory
    ax.plot(
        x_data, y_data, 'k',
        linewidth=plot_style["linewidth"], label="Seeker Trajectory"
    )
    # Plot the initial position as a point
    ax.scatter(x_data[0], y_data[0], c='g',
                s=50, label="Seeker Initial Position", zorder=2)

    # Calculate the axes limits
    lower_xlim = round(min(x_data),0) - 1
    upper_xlim = round(max(x_data),0) + 1
    lower_ylim = round(min(y_data),0) - 1
    upper_ylim = round(max(y_data),0) + 1

    # If we are given a source trajectory, plot that as well
    if source_info is not None:
        # If the source's position is varying with time
        if source_info["time_varying"]:
            # Plot the source trajectory
            ax.plot(
                source_info["x_data"], source_info["y_data"], 'r--',
                linewidth=plot_style["linewidth"], label="Source Trajectory"
            )

            # Recalculate the axes limits
            lower_xlim = min(lower_xlim, round(min(source_info["x_data"]),0) - 1)
            upper_xlim = max(upper_xlim, round(max(source_info["x_data"]),0) + 1)
            lower_ylim = min(lower_ylim, round(min(source_info["y_data"]),0) - 1)
            upper_ylim = max(upper_ylim, round(max(source_info["y_data"]),0) + 1)

        # Plot the initial source position as a point
        ax.scatter(
            source_info["x_init"], source_info["y_init"], c='r', marker='*',
            s=50, label="Source Initial Position", zorder=3
        )

    # If we are told to plot the sensor pose as well
    if with_sensor_pose:
        # If we directly have the sensor position data 
        if "sensor_tform_data" in test_data:
            # Get the sensor transform data
            sensor_tform_data = test_data["sensor_tform_data"]
            # Plot the sensor trajectory
            ax.plot(
                sensor_tform_data[:,0],
                sensor_tform_data[:,1],
                'b', label='Sensor Trajectory'
            )
        
        # If we have to calculate the sensor's position with encoder data
        else:
            # Create empty lists to hold sensor pose data
            sensor_pose_xdata = []
            sensor_pose_ydata = []
            # Get the yaw angle history of the vehicle
            yaw = test_data["odom_orientation"][2]
            # Create a variable for the encoder timestamp index
            enc_tstamp_index = 0

            # Loop over all odom timestamps
            for index, odom_tstamp in enumerate(test_data["odom_tstamps"]):
                # Get the yaw angle of the vehicle
                yaw_angle = yaw[index]
                # Create a variable to track timestamp error
                tstamp_error = None

                # Loop until we find the encoder timestamp that best matches the odometry timestamp
                while True:
                    # Check if we've passed the final index
                    if enc_tstamp_index > len(test_data["encoder_tstamps"])-1:
                        break

                    # Get the encoder timestamp based off of the index from the last iteration
                    enc_tstamp = test_data["encoder_tstamps"][enc_tstamp_index]
                    # Calculate the error between the odom and encoder timestamps
                    current_error = np.abs(odom_tstamp - enc_tstamp)

                    # If this was the first value tested
                    if tstamp_error is None:
                        # Set the best value of timestamp error
                        tstamp_error = current_error
                        # Increment the index
                        enc_tstamp_index += 1
                    else:
                        # If the current error is better than previous
                        if current_error < tstamp_error:
                            # Set the best value of timestamp error
                            tstamp_error = current_error
                            # Increment the index
                            enc_tstamp_index += 1
                        
                        # If the current error got worse than previous
                        elif current_error > tstamp_error:
                            # Get the previous index of the best matching timestamps
                            enc_tstamp_index = enc_tstamp_index - 1
                            # Get the encoder value at this index
                            phi = test_data["encoder_data"][enc_tstamp_index]
                            # Break out of the loop
                            break

                # Set the arm length
                d = test_data["arm_length"]
                
                # Now knowing the best matching encoder reading, calculate the sensor pose
                sensor_x = x_data[index] + d*np.cos(yaw_angle + phi)
                sensor_y = y_data[index] + d*np.sin(yaw_angle + phi)
                sensor_pose_xdata.append(sensor_x)
                sensor_pose_ydata.append(sensor_y)

            # Plot the sensor trajectory
            ax.plot(
                sensor_pose_xdata, sensor_pose_ydata,
                'b', label='Sensor Trajectory'
            )

        # Override the figure name if we're plotting the sensor pose
        plot_style["figure_name"] = "vehicle_path_with_sensor_pose"

    # Set the axes limits
    ax.set_xlim([lower_xlim, upper_xlim])
    ax.set_ylim([lower_ylim, upper_ylim])

    # Set the axes ticks
    xloc = np.linspace(lower_xlim, upper_xlim, 6)
    xloc = [round(x,1) for x in xloc]
    yloc = np.linspace(lower_ylim, upper_ylim, 6)
    yloc = [round(y,1) for y in yloc]
    plt.xticks(xloc, xloc)
    plt.yticks(yloc, yloc)

    # Adjust the tick size
    ax.tick_params(axis='both', which='major', labelsize=plot_style["ticksize"])

    # Set the axes labels
    ax.set_xlabel("X [m]", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"])
    ax.set_ylabel("Y [m]", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"])

    # Create the grid
    ax.grid(True)

    # Add a legend
    ax.legend(fontsize=plot_style["legend_label_size"], framealpha=1.0)

    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/{plot_style["figure_name"]}.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure
