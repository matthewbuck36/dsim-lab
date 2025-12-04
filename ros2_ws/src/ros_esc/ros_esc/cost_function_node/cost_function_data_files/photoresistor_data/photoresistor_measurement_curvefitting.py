#!/usr/bin/env python3

"""This script can be used to vizualise the measurement data
taken with the photoresistor at multiple different beta angle
positions and distances.
"""

import os
import csv
import numpy as np
from scipy.optimize import curve_fit
from photoresistor_measurement_plots import make_contour_plot, make_xy_plane_contours, export_colorbar_rgba

# pylint: disable=too-many-locals
def main():
    """This function creates plots to visualize the test data."""

    # Specify plot style variables here
    plot_style = {
        "dpi_level": 300,
        "tick_size": 20,
        "axis_label_size": 25,
        "legend_label_size": 15,
        "fonttype": 'Times New Roman',
        "figsize": (10,8),
    }

    # Specify the filepath to the csv file
    # pylint: disable=line-too-long
    filepath = os.path.expanduser(
        '~/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/photoresistor_measurement_data.csv'
    )

    # Get the data from the csv file,
    # Note the data is in the format shown below:
    # Distance to Source (m),     Beta Angle (deg),     Photoresistor Resistance (ohms),
    data = read_csv_file(filepath, skip_lines=14)

    # Note we scale the radius data by two, effectively doubling the range of the photoresistor sensor
    # When we origionally took this data, the lantern was running out of battery and was a little dim
    # After replacing the batteries, the lantern was brighter, and we could see that it approximately
    # doubled the maximum range we could operate in
    data["distance_values"] *= 2

    # Loop over all data points, and append the voltage value
    # that corresponds to each resistance value
    data["voltage_values"] = []
    for r in data["resistance_values"]:
        # Voltage = 5 / (Resistance / 330 + 1)
        voltage = 5 / (r / 330 + 1)
        # Append the result
        data["voltage_values"].append(voltage)
    # Convert to np array
    data["voltage_values"] = np.array(data["voltage_values"])

    # Filter out some of the maximum resistance values from
    # our dataset so that we get a better curve fit
    fitting_data = get_data_to_fit(data)

    # Initialize bounds for only positive coefficients
    bounds = (0, np.inf)
    # Create the quadratic curve fit for the resistance values
    resistance_coeff = create_quadratic_fit(
        fitting_data["distance_fitting"],
        fitting_data["beta_angle_fitting"],
        fitting_data["resistance_fitting"],
        bounds,
        "Resistance"
    )

    # Specify the filepath for where the figures will be saved
    # pylint: disable=line-too-long
    filepath = os.path.expanduser(
        '~/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/figures'
    )

    # Initialize the resistance bounds
    resistance_bounds = (100, 337260)

    # Plot the results for the resistance fit
    make_contour_plot(plot_style, resistance_coeff, resistance_bounds, filepath)
    make_xy_plane_contours(plot_style, 0, fitting_data, resistance_bounds, filepath)
    make_xy_plane_contours(plot_style, 45, fitting_data, resistance_bounds, filepath)
    make_xy_plane_contours(plot_style, 90, fitting_data, resistance_bounds, filepath)

    # Export the colorbar colors for use in MATLAB plotting# pylint: disable=line-too-long
    filepath = os.path.expanduser(
        '~/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data'
    )
    export_colorbar_rgba(filepath)

def read_csv_file(filepath, skip_lines=0):
    """This function extracts the data from a csv file given the filepath."""

    with open(filepath, mode='r', newline="", encoding='utf-8') as file:
        reader = csv.reader(file)
        # Save the data to a dictionary
        data = {
            "distance_values": [],
            "beta_angle_values": [],
            "resistance_values": [],
        }

        # Skip any header rows, the total amount of lines skiped is equal to skip_lines
        for i in range(skip_lines): # pylint: disable=unused-variable
            next(reader)

        # Loop over all the remaining rows
        for row in reader:
            # Save the data
            data["distance_values"].append(float(row[0]))
            data["beta_angle_values"].append(float(row[1]))
            data["resistance_values"].append(float(row[2]))

    # Convert to numpy arrays
    data["distance_values"] = np.array(data["distance_values"])
    data["beta_angle_values"] = np.array(data["beta_angle_values"])
    data["resistance_values"] = np.array(data["resistance_values"])

    return data

def get_data_to_fit(data):
    """This function filters out many of the maximum resistance values at longer distances.

    This is done so that we get a better curve fit that captures the variation of resistance
    w.r.t. radius and angle beta, without trying to also fit the plateau of values where
    the sensor's resistance is maxed out.
    """

    # Define a dataset which will be used for curve fitting
    fitting_data = {
        "distance_fitting": [],
        "beta_angle_fitting": [],
        "resistance_fitting": [],
        "voltage_fitting": [],
    }
    # Track the last radius read
    prev_rad = 0
    # Create a flag
    flag = False
    # Loop over the data
    for i in range(len(data["distance_values"])):
        # Get the radius
        radius = data["distance_values"][i]
        # Get the angle
        beta = data["beta_angle_values"][i]
        # Get the resistance
        ohm = data["resistance_values"][i]
        # Get the voltage
        volt = data["voltage_values"][i]

        # Check if this value has the same radius as the previous entry
        if radius == prev_rad:
            # Check if the resistance value is the max value
            if ohm == 337260:
                # If this is the first time we've seen the max resistance value
                # for this particular radius from the source,
                if not flag:
                    # Append the data
                    fitting_data["distance_fitting"].append(radius)
                    fitting_data["beta_angle_fitting"].append(beta)
                    fitting_data["resistance_fitting"].append(ohm)
                    fitting_data["voltage_fitting"].append(volt)

                    # Update the flag to indicate we've seen the max resistance value
                    # at this particular radius from the source
                    flag = True

                # If we've seen the max resistance value already for this particular
                # radius, we do nothing, this is how we filter these values out of
                # the dataset for a better curve fit
                else:
                    pass

            else:
                # Append the data
                fitting_data["distance_fitting"].append(radius)
                fitting_data["beta_angle_fitting"].append(beta)
                fitting_data["resistance_fitting"].append(ohm)
                fitting_data["voltage_fitting"].append(volt)

        else:
            # Append the data
            fitting_data["distance_fitting"].append(radius)
            fitting_data["beta_angle_fitting"].append(beta)
            fitting_data["resistance_fitting"].append(ohm)
            fitting_data["voltage_fitting"].append(volt)
            # Reset the flag for a new radius
            flag = False

        # Update variables
        prev_rad = radius

    # Convert to np arrays
    fitting_data["distance_fitting"] = np.array(fitting_data["distance_fitting"])
    fitting_data["beta_angle_fitting"] = np.array(fitting_data["beta_angle_fitting"])
    fitting_data["resistance_fitting"] = np.array(fitting_data["resistance_fitting"])
    fitting_data["voltage_fitting"] = np.array(fitting_data["voltage_fitting"])

    # Write fitting data to csv file for matlab plotting script
    fitting_data_filepath = os.path.expanduser(
        '~/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_data_files/photoresistor_data/curve_fitting_data.csv'
    )
    # Write the header row for csv file
    with open(fitting_data_filepath, mode="w", newline="", encoding="utf-8") as file:
        log = csv.writer(file)
        # Write header rows
        log.writerow(["Distance (m), Beta (deg), Resistance (ohms), Voltage (V)"])
        for i in range(len(fitting_data["distance_fitting"])):
            log.writerow([
                fitting_data["distance_fitting"][i],
                fitting_data["beta_angle_fitting"][i],
                fitting_data["resistance_fitting"][i],
                fitting_data["voltage_fitting"][i]
            ])

    return fitting_data

def create_quadratic_fit(distance, beta, values_of_interest, bounds, label):
    """This function creates a quadratic curve fit of the value of interest.
    
    We use scipy to fit a 2D quadratic curve (in radius and beta)
    to fit a dataset of either resistance or voltage values. The 
    quadratic curve fit is of the following form:
    
    value_of_interest = a*radius**2 + b*beta**2 + c*radius*beta + d*radius + e*beta + f

    where a,b,c,d,e,f are all coefficients of this quadratic curve fit
    which are are bounded from zero to infinity. This function organizes
    these coefficients into a list, and computes the R^2 value of this
    fitted quadratic equation.
    """

    # Use scipy to fit a 2D quadratic curve to this dataset
    # pylint: disable=unused-variable
    coefficients, _ = curve_fit(
        quadratic_curve_fit,
        (distance, beta),
        values_of_interest,
        bounds=bounds
    )

    # Print the curve fit coefficients
    print(f"{label} Curve Fit Coefficients:")
    print(coefficients)
    a, b, c, d, e, f = coefficients # pylint: disable=invalid-name

    # Get the residual sum of squares with
    fit_values = []
    for index, value in enumerate(distance):
        rad = value
        b_ang = beta[index]
        fit_values.append(
            quadratic_curve_fit(
                (rad, b_ang),
                a, b, c, d, e, f
            )
        )
    # Calcualte the residuals
    residuals = np.array(values_of_interest) - np.array(fit_values)
    # Calculate the sum of squared residuals
    ss_res = np.sum(residuals**2)

    # Get the total sum of squares with
    ss_tot = np.sum((values_of_interest - np.mean(values_of_interest))**2)

    # Calculate the R^2 value from these parameters
    # Reference:
    # https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit
    r_squared = 1 - (ss_res/ ss_tot)
    print("R squared value: "+str(r_squared))
    print(" ")

    return coefficients 

# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
def quadratic_curve_fit(indep_variables, a, b, c, d, e, f):
    """Define a quadratic function of the form below

    This is used by scipy's curve fit to fit a quadratic
    function to the values of interest versus beta angle and radius from source comparison.
    See https://swharden.com/blog/2020-09-24-python-exponential-fit/
    and https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
    for more information.
    """

    radius, beta = indep_variables
    return a * radius**2 + b * beta**2 + c * radius * beta + d * radius + e * beta + f

if __name__ == "__main__":
    main()
