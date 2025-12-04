"""This script holds helper functions for use in math simulations."""

import os
import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from sensor_perturbation_signals import sensor_transform

def create_test_folder(filepath, math_sim_script_filepath):
    """This creates a test folder to save csv files of simulation data."""

    # Get the current time
    now = datetime.now()
    # Edit the date time string
    date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    # Create a default name for the new folder
    folder_title = f"Test_{date_time_str}"
    # Create the new folder to hold the test data
    new_folder = f"{filepath}/{folder_title}"
    # Create the new folder in the desired filepath directory
    os.makedirs(new_folder, exist_ok=True)

    # Create a csv filepath to hold odometry information
    odom_filepath = f"{new_folder}/odometry.csv"
    # Create a csv filepath to hold sensor transform information
    sensor_transform_filepath = f"{new_folder}/sensor_transform.csv"
    # Create a csv filepath to hold cost value information
    cost_filepath = f"{new_folder}/cost_value.csv"
    
    # Create a dictionary to store these filepaths
    csv_filepath_dict = {
        "odometry_csv": odom_filepath,
        "sensor_transform_csv": sensor_transform_filepath,
        "cost_value_csv": cost_filepath
    }

    # Redefine the filepath to accomodate the user's home directory
    filepath = os.path.expanduser(math_sim_script_filepath)
    # Open the script at the filepath
    with open(filepath, mode='r', encoding='utf-8') as file:
        # Read the file
        file_text = file.read()
    # Create a comment file to document simulation parameters
    comment_filepath = f"{new_folder}/comments.txt"
    # Create the comments file
    with open(comment_filepath, mode="w", encoding='utf-8') as comment:
        comment.write(file_text)

    return new_folder, csv_filepath_dict

def calculate_quaternions(transform_matrix):
    """This calculates quaternion angles from a transformation matrix.
    
    See https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    eqns (8 thru 9) for more information on this procedure.
    """

    # Pull data from the transform matrix
    r11 = transform_matrix[0][0]
    r12 = transform_matrix[0][1]
    r13 = transform_matrix[0][2]
    r21 = transform_matrix[1][0]
    r22 = transform_matrix[1][1]
    r23 = transform_matrix[1][2]
    r31 = transform_matrix[2][0]
    r32 = transform_matrix[2][1]
    r33 = transform_matrix[2][2]

    # Find the magnitude of each quaternion component
    mag_q0 = np.sqrt((1+r11+r22+r33)/4)
    mag_q1 = np.sqrt((1+r11-r22-r33)/4)
    mag_q2 = np.sqrt((1-r11+r22-r33)/4)
    mag_q3 = np.sqrt((1-r11-r22+r33)/4)
    
    # Find the largest magnitude of the above, assume its sign is positive
    largest = max(mag_q0, mag_q1, mag_q2, mag_q3)

    # If mag_q0 is largest
    if largest == mag_q0:
        qw = mag_q0
        qx = (r32-r23)/(4*mag_q0)
        qy = (r13-r31)/(4*mag_q0)
        qz = (r21-r12)/(4*mag_q0)
    
    # If mag_q1 is largest
    elif largest == mag_q1:
        qw = (r32-r23)/(4*mag_q1)
        qx = mag_q1
        qy = (r12+r21)/(4*mag_q1)
        qz = (r13+r31)/(4*mag_q1)
    
    # If mag_q2 is largest
    elif largest == mag_q2:
        qw = (r13-r31)/(4*mag_q2)
        qx = (r12+r21)/(4*mag_q2)
        qy = mag_q2
        qz = (r23+r32)/(4*mag_q2)
    
    # If mag_q3 is largest
    else:
        qw = (r21-r12)/(4*mag_q3)
        qx = (r13+r31)/(4*mag_q3)
        qy = (r23+r32)/(4*mag_q3)
        qz = mag_q3
    
    return qw, qx, qy, qz

def save_data_to_csv(tstamps, state_hist, cost_funct_obj, angularpositionsignal_obj, frame_arm_length, csv_filepath_dict):
    """This calculates the true cost value given the simulation time and the seeker's state."""

    # Unpack dictionary of csv filepaths
    odom_filepath = csv_filepath_dict["odometry_csv"]
    sensor_transform_filepath = csv_filepath_dict["sensor_transform_csv"]
    cost_filepath = csv_filepath_dict["cost_value_csv"]

    # Initialize lists to save the time history results
    cost_value_hist = []
    sensor_pose_hist = []

    # Loop over the simulation time
    for i, t in enumerate(tstamps):
        # Get the current state of the vehicle at this time index
        state = state_hist[i].tolist()
        state_data = [t] + state

        # Append state data to csv
        append_csv_file(odom_filepath, state_data)

        # Get the sensor transformation matrix at this time index
        sensor_tform = sensor_transform(t, state, angularpositionsignal_obj, frame_arm_length)

        # Save the sensor's transform information into a list
        x = sensor_tform[0][3]
        y = sensor_tform[1][3]
        z = sensor_tform[2][3]
        qw, qx, qy, qz = calculate_quaternions(sensor_tform)
        tform = [x, y, z, qw, qx, qy, qz]

        # Save the time history results of the sensor pose
        sensor_pose_hist.append(tform[:2])
        # Append transform history to csv
        tform_data = [t] + tform
        # Save to csv
        append_csv_file(sensor_transform_filepath, tform_data)

        # Calculate the cost value based on the sensor's transformation matrix
        cost = [cost_funct_obj.cost_output(t, sensor_tform)]
        cost_data = [t] + cost
        # Save the time history results of the cost value
        cost_value_hist.append(cost)
        # Save to csv
        append_csv_file(cost_filepath, cost_data)

    # Convert to array
    sensor_pose_hist = np.array(sensor_pose_hist)

    return sensor_pose_hist, cost_value_hist

def append_csv_file(filepath, data):
    """This function appends the csv file with the timestamped data."""

    # Check that the data variable isn't None, if there isn't data don't write anything
    if data is not None:
        # Append the csv file
        with open(filepath, mode="a", newline="", encoding="utf-8") as file:
            # Create the object
            log = csv.writer(file)
            # Write the data to the file
            log.writerow(data)

def plot_seeker_path(plot_style, state_hist, sensor_pose_hist, source_pose):

    ### Plot the seeker's path
    fig, ax = plt.subplots(1, 1)
    plt.title("Vehicle Path")
    ax.scatter(state_hist[0,0], state_hist[0,1], linewidths=2, c="g", s=200,
               label="Seeker's Initial Position", zorder=2)
    ax.scatter(source_pose[0], source_pose[1], c='r', marker='*',
                s=200, label="Source's Position", zorder=3)
    ax.plot(state_hist[:, 0], state_hist[:, 1], linewidth=2, c='k', label="Seeker Path")

    ax.set_xlabel(
        "X [m]", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"]
    )
    ax.set_ylabel(
        "Y [m]", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"]
    )
    ax.tick_params(
        axis='both', which='major', labelsize=plot_style["tick_size"]
    )

    # Calculate and set axis limits
    axes_lim = max(max(np.abs(state_hist[:,0])),max(np.abs(state_hist[:,1])))//1+2
    ax.set_xlim([-axes_lim,axes_lim])
    ax.set_ylim([-axes_lim,axes_lim])
    ax.legend(fontsize=plot_style["legend_label_size"])

    # Save the figure to the designated filepath
    plt.savefig(f'{plot_style["save_to_filepath"]}/vehicle_path.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure


    ### Plot the seeker's path with the sensor pose
    fig, ax = plt.subplots(1, 1)
    plt.title("Vehicle Path with Sensor Pose")
    ax.scatter(state_hist[0,0], state_hist[0,1], linewidths=2, c="g", s=200,
               label="Seeker's Initial Position", zorder=2)
    ax.scatter(source_pose[0], source_pose[1], c='r', marker='*',
                s=200, label="Source's Position", zorder=3)
    ax.plot(state_hist[:, 0], state_hist[:, 1], linewidth=2, c='k', label="Seeker Path")
    ax.plot(sensor_pose_hist[:, 0], sensor_pose_hist[:, 1], linewidth=2, c='b', label="Sensor Trajectory")

    ax.set_xlabel(
        "X [m]", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"]
    )
    ax.set_ylabel(
        "Y [m]", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"]
    )
    ax.tick_params(
        axis='both', which='major', labelsize=plot_style["tick_size"]
    )

    # Set axis limits
    ax.set_xlim([-axes_lim,axes_lim])
    ax.set_ylim([-axes_lim,axes_lim])
    ax.legend(fontsize=plot_style["legend_label_size"])

    # Save the figure to the designated filepath
    plt.savefig(f'{plot_style["save_to_filepath"]}/vehicle_path_with_sensor_pose.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure

def plot_cost_value_hist(plot_style, tstamps, cost_value_hist):

    ### Plot our cost value versus time
    fig, ax = plt.subplots(1,1)
    plt.title("Cost Value Time History")
    ax.plot(tstamps, cost_value_hist)

    ax.set_xlabel(
        "Time [sec]", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"]
    )
    ax.set_ylabel(
        "Cost Value", fontsize=plot_style["axis_label_size"], fontname=plot_style["fonttype"]
    )
    ax.tick_params(
        axis='both', which='major', labelsize=plot_style["tick_size"]
    )
    ax.set_xlim([0,tstamps[-1]])

    # Save the figure to the designated filepath
    plt.savefig(f'{plot_style["save_to_filepath"]}/cost_history.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure
