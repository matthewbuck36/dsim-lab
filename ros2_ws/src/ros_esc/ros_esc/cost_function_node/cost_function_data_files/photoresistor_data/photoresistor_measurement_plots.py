#!/usr/bin/env python3

"""This script holds plotting helper functions for
visualizing the photoresistor measurement data.
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.optimize import curve_fit
from matplotlib import cm

def make_contour_plot(plot_style, coefficients, bounds, filepath):
    """This function is used to plot contours of photoresistor data vs radius and beta."""

    # Create a meshgrid for custom coordinates
    radius = np.linspace(0, 6, 100)
    beta = np.linspace(-180, 180, 100)
    X, Y = np.meshgrid(beta, radius)

    # Create a list to store the resistance grid
    resistance_grid = []
    # Create a list to store the voltage grid
    voltage_grid = []
    # Get the terms from the curve fit
    a, b, c, d, e, f = coefficients # pylint: disable=invalid-name

    # Loop over all x
    for radius_value in radius:
        # Create a new list for the resistance
        resistance_results = []
        # Create a new list for the voltage
        voltage_results = []
        # Get the radius at this index
        rad = np.abs(radius_value)

        # Loop over all y
        for beta_value in beta:
            # Get the beta angle at this index
            b_ang = np.abs(beta_value)
            # Use the curve fit to calculate the resistance
            resistance = a*rad**2 + b*b_ang**2 + c*rad*b_ang + d*rad + e*b_ang + f
            # Ensure this doesn't exceed the largest bound
            resistance = min(resistance, max(bounds))
            # Ensure this doesn't go lower than the smallest bound
            resistance = max(resistance, min(bounds))

            # Append this to resistance results
            resistance_results.append(resistance)
            # Convert this resistance to a voltage
            voltage = 5/(resistance / 330 + 1)
            # Append this to voltage results
            voltage_results.append(voltage)

        # Append results to resistance grid
        resistance_grid.append(resistance_results)
        # Append results to voltage grid
        voltage_grid.append(voltage_results)

    # Convert to arrays
    resistance_Z = np.array(resistance_grid)
    voltage_Z = np.array(voltage_grid)



    # Create the figure for resistance contours
    plt.figure(figsize = plot_style["figsize"])
    # Make the contour plot
    contour = plt.pcolormesh(X, Y, resistance_Z, cmap="plasma_r", vmin=0, vmax=max(bounds))
    # Add the colorbar
    cbar = plt.colorbar(contour)
    # Set the axes labels
    plt.ylabel(
        r"$r_{s}$ [m]",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    plt.xlabel(
        r"$\beta$ [deg]",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    cbar.set_label(
        r'$R_{\mathrm{pr}}$ [$\Omega$]',
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    # Set the axes limits
    plt.xlim([-180,180])
    plt.ylim([0, 6])
    plt.clim(0, max(bounds))
    # Set the axes tick marks
    plt.xticks(
        [-180,-90,0,90,180],
        [-180,-90,0,90,180],
        fontname=plot_style["fonttype"]
    )
    plt.yticks(fontname=plot_style["fonttype"])
    # Adjust the axes tick font type
    for l in cbar.ax.yaxis.get_ticklabels():
        l.set_family(plot_style["fonttype"])
    # Adjust the tick size
    plt.tick_params(axis='both', which='major', labelsize=plot_style["tick_size"])
    cbar.ax.tick_params(labelsize=plot_style["tick_size"])
    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/resistance_contours.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure



    # Create the figure for voltage contours
    plt.figure(figsize = plot_style["figsize"])
    # Make the contour plot
    contour = plt.pcolormesh(
        X, Y, voltage_Z, norm=colors.LogNorm(vmin=0.004, vmax=5), cmap="plasma_r"
    )
    # Add the colorbar
    cbar = plt.colorbar(contour)
    # Set the axes labels
    plt.ylabel(
        r"$r_{s}$ [m]",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    plt.xlabel(
        r"$\beta [deg]$",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    cbar.set_label(
        r'$V_{\mathrm{meas}}$ [V]',
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    # Set the axes limits
    plt.xlim([-180,180])
    plt.ylim([0, 6])
    # Set the axes tick marks
    plt.xticks(
        [-180,-90,0,90,180],
        [-180,-90,0,90,180],
        fontname=plot_style["fonttype"]
    )
    plt.yticks(fontname=plot_style["fonttype"])
    # Adjust the axes tick font type
    for l in cbar.ax.yaxis.get_ticklabels():
        l.set_family(plot_style["fonttype"])
    # Adjust the tick size
    plt.tick_params(axis='both', which='major', labelsize=plot_style["tick_size"])
    cbar.ax.tick_params(labelsize=plot_style["tick_size"])
    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/voltage_contours.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure

def make_xy_plane_contours(plot_style, desired_beta, fitting_data, bounds, filepath):
    """This function is used to plot contours of photoresistor data over the x-y plane."""

    # Get lists of data which we will use for a curve fit
    radius_newfit = []
    resistance_newfit = []
    # Loop over all the data
    for index, angle in enumerate(fitting_data["beta_angle_fitting"]):
        # If the beta value is the one requested
        if angle == desired_beta:
            # Append the lists
            radius_newfit.append(fitting_data["distance_fitting"][index])
            resistance_newfit.append(fitting_data["resistance_fitting"][index])

    # Use scipy to fit a 1D quadratic curve (a function of the radius) to this dataset
    # pylint: disable=unused-variable
    params, _ = curve_fit(
        radius_vs_value_fit, radius_newfit, resistance_newfit
    )

    # Unpack the curve fit params
    a, b = params # pylint: disable=invalid-name

    # Create a meshgrid for cartesian coordinates
    x = np.linspace(-6, 6, 100) # pylint: disable=invalid-name
    y = np.linspace(-6, 6, 100) # pylint: disable=invalid-name
    X, Y = np.meshgrid(x, y) # pylint: disable=invalid-name

    # Create a grid of resistance values
    resistance_Z = []
    # Create a grid of voltage values
    voltage_Z = []

    # Loop over all x
    for x_val in x:
        # Create a list to hold resistance data
        resistance_results = []
        # Create a list to hold voltage data
        voltage_results = []
        # Loop over all y
        for y_val in y:
            # Calculate the radius
            rad = np.sqrt(x_val**2+y_val**2)
            # Use the curve fit to calculate a value
            resistance = a*rad**2 + b

            # Ensure this value isn't above the maximum value
            resistance = min(resistance, max(bounds))
            # Ensure this value isn't below the minimum value
            resistance = max(resistance, min(bounds))

            # Append to list
            resistance_results.append(resistance)
            # Calculate voltage
            voltage = 5/(resistance / 330 + 1)
            # Append to list
            voltage_results.append(voltage)

        # Append to lists
        resistance_Z.append(resistance_results)
        voltage_Z.append(voltage_results)



    # Create the figure for the resistance over x-y plane
    plt.figure(figsize = plot_style["figsize"])
    # Make the contour plot
    contour = plt.pcolormesh(X, Y, resistance_Z, cmap="plasma_r", vmin=0, vmax=max(bounds))
    # Add the colorbar
    cbar = plt.colorbar(contour)
    # Set the axes limits
    plt.xlim([-6, 6])
    plt.ylim([-6, 6])
    plt.clim(0,max(bounds))
    # Set the axes labels
    plt.xlabel(
        "X [m]",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    plt.ylabel(
        "Y [m]",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    cbar.set_label(
        r'$R_{\mathrm{pr}}$ [$\Omega$]',
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    # Set the axes tick marks and adjust the font type
    plt.tick_params(axis='both', which='major', labelsize=plot_style["tick_size"])
    plt.xticks(fontname=plot_style["fonttype"])
    plt.yticks(fontname=plot_style["fonttype"])
    for label in cbar.ax.yaxis.get_ticklabels():
        label.set_family(plot_style["fonttype"])
    cbar.ax.tick_params(labelsize=plot_style["tick_size"])
    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/xy_plane_resistance_at_beta_{desired_beta}.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure



    # Create the figure for the voltage over x-y plane
    plt.figure(figsize = plot_style["figsize"])
    # Make the contour plot
    contour = plt.pcolormesh(
        X, Y, voltage_Z, norm=colors.LogNorm(vmin=0.004, vmax=5), cmap="plasma_r"
    )
    # Add the colorbar
    cbar = plt.colorbar(contour)
    # Set the axes limits
    plt.xlim([-6, 6])
    plt.ylim([-6, 6])
    plt.clim(0.004, 5)
    # Set the axes labels
    plt.xlabel(
        "X [m]",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    plt.ylabel(
        "Y [m]",
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    cbar.set_label(
        r'$V_{\mathrm{meas}}$ [V]',
        fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    # Set the axes tick marks and adjust the font type
    plt.tick_params(axis='both', which='major', labelsize=plot_style["tick_size"])
    plt.xticks(fontname=plot_style["fonttype"])
    plt.yticks(fontname=plot_style["fonttype"])
    for label in cbar.ax.yaxis.get_ticklabels():
        label.set_family(plot_style["fonttype"])
    cbar.ax.tick_params(labelsize=plot_style["tick_size"])
    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/xy_plane_voltage_at_beta_{desired_beta}.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure

# pylint: disable=invalid-name
def radius_vs_value_fit(r, a, b):
    """Define a quadratic function of the form below

    This is used by scipy's curve fit to fit a quadratic
    function to the resistance versus radius from source comparison.
    See https://swharden.com/blog/2020-09-24-python-exponential-fit/
    and https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
    for more information.
    """

    return a * r**2 + b

def export_colorbar_rgba(filepath):
    """This exports the colorbar colors to a csv file, they can be used for MATLAB 3D plots."""

    # Create a csv filepath to hold odometry information
    cbar_filepath = f"{filepath}/plasma_r_colorbar.csv"

    # Append the csv file
    with open(cbar_filepath, mode="w", newline="", encoding="utf-8") as file:
        # Create the object
        log = csv.writer(file)

        # Loop over all colors in the colorbar
        for i in range(256):
            # Write the color data to the file
            log.writerow(cm.plasma_r(i))
