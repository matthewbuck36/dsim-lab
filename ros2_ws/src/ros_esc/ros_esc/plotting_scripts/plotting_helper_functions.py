#!/usr/bin/env python3

"""This script holds helper functions used for creating plots."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

def init_plot_style():
    """This returns a dictionary with some preset plot style items."""

    # Initialize plot style dictionary
    plot_style = {}

    # Set the image size, 3.25 inches is about one column width on a page
    plot_style["figsize"] = (3.25, 3.25)
    # Set the image dpi level
    plot_style["dpi_level"] = 300
    # Set the font type
    plot_style["fonttype"] = "Times New Roman"
    # Set the axis label size
    plot_style["axis_label_size"] = 12
    # Set the tick size
    plot_style["ticksize"] = 10
    # Set the line width
    plot_style["linewidth"] = 1.0

    # By default, do not add a legend
    plot_style["add_legend"] = False
    # Set the legend label size
    plot_style["legend_label_size"] = 6

    # Set default colors
    plot_style["colors"] = ['k', 'b', 'r', 'g', 'darkorange', 'm', 'c']

    return plot_style

def plot_time_history(plot_style, tstamps, data, filepath):
    """This plots a time history of a given quantity."""

    # Create the figure
    # This removes the error from pylint about the variable 'ax'
    # pylint: disable=invalid-name
    fig, ax = plt.subplots(1, 1, figsize=plot_style["figsize"], constrained_layout=True) # pylint: disable=unused-variable
    # pylint: enable=invalid-name

    # If we only have one sequence to plot
    if len(np.shape(data))== 1:
        # Plot the data
        ax.plot(
            tstamps, data, plot_style["colors"][0],
            linewidth=plot_style["linewidth"], label=plot_style["data_labels"][0]
        )

    # If we have a list of entries to plot
    else:
        # Loop over all possible entries in tstamps and data lists
        for index, datapoints in enumerate(data):
            # Plot the data
            ax.plot(
                tstamps, datapoints, plot_style["colors"][index],
                linewidth=plot_style["linewidth"], label=plot_style["data_labels"][index]
            )

    # Adjust the tick size
    ax.tick_params(axis='both', which='major', labelsize=plot_style["ticksize"])

    # Set the axes limits
    ax.set_xlim([0,tstamps[-1]])
    ax.set_ylim(plot_style["yaxis_limits"])

    # Set the axes labels
    ax.set_xlabel(
        "Time ($t$) [sec]", fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )
    ax.set_ylabel(
        plot_style["yaxis_name"], fontsize=plot_style["axis_label_size"],
        fontname=plot_style["fonttype"]
    )

    # Set the axes ticks if given
    if "yaxis_tick_locations" in plot_style:
        # Set the y tick labels
        plt.yticks(plot_style["yaxis_tick_locations"], plot_style["yaxis_tick_labels"])

    # Create a grid
    ax.grid(True)

    # Add a legend if desired
    if plot_style["add_legend"]:
        ax.legend(fontsize=plot_style["legend_label_size"], framealpha=1.0)

    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))

    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/{plot_style["figure_name"]}.png', dpi=plot_style["dpi_level"])
    plt.close()  # Close the current figure
