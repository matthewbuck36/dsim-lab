"""The purpose of this script is to find appropriate estimation
signals that can be used to construct a filter object. These
estimation signals are functions of a user defined piecewise 
perturbation function phi(t) where phi represensts the angular 
position of the rotating sensor frame as it spins clockwise and
counterclockwise.

There are four variables that are important in this analysis.
Beta denotes the rotation speed of the rotating sensor frame.
Note that the rotation speed is assumed to be the same whether
the frame is rotating clockwise or counterclockwise. The variable
d denotes the distance from the sensor to the axis the sensor
is rotating about, i.e. the center of the turtlebot vehicle.
Finally, phi_upper and phi_lower denote the upper and lower
bounds of the spin envelope the rotating sensor frame is
spinning within. 

The user can choose to define these variables with constants, or
leave them as symbols before sympy does its calculations. If the
user defines these variables as constants, this script will
generate two plots showing one period of the perturbation signal
and the estimation signals.
"""

import os
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

def main():
    """This function calculates the estimation signals symbolically."""

    ### User can define these variables as constants
    beta = 20*(2*np.pi/60) # arbitrary rotation speed (rad/s)
    phi_lower = -np.pi/2 # lower bound on spin envelope
    phi_upper = np.pi/2 # upper bound on spin envelope
    d = 0.1524 # rotating sensor frame arm length in meters

    ### Or choose to leave them as symbols
    # beta = sp.Symbol('B') # arbitrary rotation speed (rad/s)
    # phi_lower = sp.Symbol('phi_low') # lower bound on spin envelope
    # phi_upper = sp.Symbol('phi_upr') # upper bound on spin envelope
    # d = sp.Symbol('d') # rotating sensor frame arm length in meters

    # Create a list of these variables
    variable_list = [beta,phi_lower,phi_upper,d]

    # Define the signal period
    period = 2*(phi_upper - phi_lower)/beta
    # Define a symbol for time
    t = sp.Symbol('t')

    # Define the piecewise portion for ccw rotation
    ccw_expression = phi_lower + beta*t
    ccw_condition = t < period/2
    # Define the piecewise portion for cw rotation
    cw_expression = phi_upper - beta*(t-period/2)
    cw_condition = True
    # Define an expression for phi(t)
    phi = sp.Piecewise((ccw_expression,ccw_condition),(cw_expression,cw_condition))
    
    # Define x and y coordinates that describe the sensor's position w.r.t. the vehicle's center
    x = d*sp.cos(phi)
    y = d*sp.sin(phi)

    # Define the average coordinates x_bar and y_bar, these 
    # come from using the average value equation on x and y
    x_bar = sp.simplify(sp.integrate(x,(t,0,period))/period)
    y_bar = sp.simplify(sp.integrate(y,(t,0,period))/period)

    # Define x_tilde and y_tilde, these are the x and y coordinates
    # when we subtract out the mean values
    x_tilde = x - x_bar
    y_tilde = y - y_bar
    
    # We now construct the terms of the covariance matrix Q
    q_11 = sp.simplify(sp.integrate(x_tilde**2,(t,0,period))/period)
    q_22 = sp.simplify(sp.integrate(y_tilde**2,(t,0,period))/period)
    q_12 = sp.simplify(sp.integrate(x_tilde*y_tilde,(t,0,period))/period)
    q_mat = sp.Matrix(2,2,[q_11,q_12,q_12,q_22])
    
    # We now invert the covariance matrix to get the precision matrix
    p_mat = q_mat.inv()

    # Finally we multiply the precision matrix by a vector
    # of x and y tilde to get our estimation signals
    estim_signals = p_mat @ sp.Matrix(2,1,[x_tilde,y_tilde])
    
    # Define a filepath where plot figures will be saved
    filepath = os.path.expanduser(
        "~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/python_simulation"
    )

    # If beta, phi_lower, phi_upper, and d are all defined as numbers
    # we can plot one period of the perturbation and estimation signals
    type_list = [type(x) for x in variable_list]
    # Check the type of all the variables
    if sp.core.symbol.Symbol not in type_list:
        # Plot the perturbation signal for reference
        plot_perturbation_signal(t, phi, x, y, period, filepath)
        # Plot the estimation signal for reference
        plot_estimation_signals(t, estim_signals, period, filepath)
    
    # Print out the signals to terminal
    print("Perturbation Signal:")
    print(phi)
    print("Estimation Signals:")
    # Convert sympy mutable matrix into numpy array
    m = np.array(estim_signals)
    print(m)

def plot_perturbation_signal(t, phi, x, y, period, filepath):
    """This function plots one period of the perturbation signal for reference."""

    # Specify plot style parameters
    dpi_level = 300
    tick_size = 8
    axis_label_size = 12
    legend_label_size = 12
    fonttype = 'Times New Roman'
    figsize = (3.25, 3.25)

    # Create a vector of timestamps to evaluate phi(t) with
    tstamps = np.linspace(0,period,500)
    # Create a list to store values 
    phi_values = []
    # Evaluate phi(t) at every timestamp
    for time in tstamps:
        phi_values.append(phi.subs(t,float(time)))

    # This removes the error from pylint about the variable 'ax'
    # pylint: disable=invalid-name
    fig, ax = plt.subplots(1, 1, figsize=figsize, constrained_layout=True) # pylint: disable=unused-variable
    # pylint: enable=invalid-name

    # Plot phi(t)
    ax.plot(tstamps,phi_values,c='k')
    # Adjust the tick size
    ax.tick_params(axis='both', which='major', labelsize=tick_size)
    # Set the axes limits
    ax.set_xlim([0,period])
    ax.set_ylim([-np.pi, np.pi])
    # Set the ticks
    ax.set_yticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    ax.set_yticklabels(["$-\pi$", "$-\pi/2$", "$0$", "$\pi/2$", "$\pi$"])
    # Set the axes labels
    ax.set_xlabel("Time (sec)", fontsize=axis_label_size, fontname=fonttype)
    ax.set_ylabel("$\phi (t)$ (radians)" , fontsize=axis_label_size, fontname=fonttype)

    ax.grid(True)

    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/arm_angle_signals.png', dpi=dpi_level)
    plt.close()  # Close the current figure


    # This removes the error from pylint about the variable 'ax'
    # pylint: disable=invalid-name
    fig, ax = plt.subplots(1, 1, figsize=figsize, constrained_layout=True) # pylint: disable=unused-variable
    # pylint: enable=invalid-name

    # Create a vector of timestamps to evaluate phi(t) with
    tstamps = np.linspace(0,period,500)
    # Create a list to store values 
    signal_values = [[],[]]
    # Evaluate phi(t) at every timestamp
    for time in tstamps:
        # Calculate the perturbation matrix at this timestamp
        x_val = x.subs(t,float(time))
        y_val = y.subs(t,float(time))
        # Apped these values to our list
        signal_values[0].append(x_val)
        signal_values[1].append(y_val)

    # Plot perturbation signals
    ax.plot(tstamps,signal_values[0],c='b',label="Perturbation Signal #1")
    ax.plot(tstamps,signal_values[1],c='r',label="Perturbation Signal #2")
    # Adjust the tick size
    ax.tick_params(axis='both', which='major', labelsize=tick_size)
    # Set the axes limits
    ax.set_xlim([0,period])
    ax.set_ylim([-.2, .2])
    # Set the axes labels
    ax.set_xlabel("Time (sec)", fontsize=axis_label_size, fontname=fonttype)
    ax.set_ylabel("Perturbation Signal Value $s_i(\phi(t))$" , fontsize=axis_label_size, fontname=fonttype)
    # ax.set_title("Periodic Perturbation Signals", fontsize = 20)
    ax.grid(True)

    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/perturbation_signals.png', dpi=dpi_level)
    plt.close()  # Close the current figure

def plot_estimation_signals(t, estim_signals, period, filepath):
    """This function plots one period of the estimation signals for reference."""

    # Specify plot style parameters
    dpi_level = 300
    tick_size = 8
    axis_label_size = 12
    legend_label_size = 12
    fonttype = 'Times New Roman'
    figsize = (3.25, 3.25)

    # Create a vector of timestamps to evaluate phi(t) with
    tstamps = np.linspace(0,period,500)
    # Create a list to store values 
    signal_values = [[],[]]
    # Evaluate phi(t) at every timestamp
    for time in tstamps:
        # Calculate the estimation matrix at this timestamp
        estim_matrix = estim_signals.subs(t,float(time))
        # Apped these values to our list
        signal_values[0].append(estim_matrix[0])
        signal_values[1].append(estim_matrix[1])

    # This removes the error from pylint about the variable 'ax'
    # pylint: disable=invalid-name
    fig, ax = plt.subplots(1, 1, figsize=figsize, constrained_layout=True) # pylint: disable=unused-variable
    # pylint: enable=invalid-name

    # Plot m(t)
    ax.plot(tstamps,signal_values[0],c='b',label="Estimation Signal #1")
    ax.plot(tstamps,signal_values[1],c='r',label="Estimation Signal #2")
    # Adjust the tick size
    ax.tick_params(axis='both', which='major', labelsize=tick_size)
    # Set the axes limits
    ax.set_xlim([0,period])
    ax.set_ylim([-50, 30])
    # Set the axes labels
    ax.set_xlabel("Time (sec)", fontsize=axis_label_size, fontname=fonttype)
    ax.set_ylabel("Estimation Signal Value $m_i(\phi(t))$", fontsize=axis_label_size, fontname=fonttype)
    # ax.set_title("Periodic Estimation Signal", fontsize = 20)
    ax.grid(True)

    # Save the figure to the designated filepath
    plt.savefig(f'{filepath}/estimation_signals.png', dpi=dpi_level)
    plt.close()  # Close the current figure

if __name__ == '__main__':
    main()
