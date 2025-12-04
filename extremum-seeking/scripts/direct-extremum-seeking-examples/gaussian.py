#!/bin/user/python3
# -* coding:utf-8 *-

"""
Example of ESCs acting on a scalar gaussian function.
"""

import matplotlib.pyplot as plt
import numpy as np
from example_helpers import (
    plot_seeker_parameter_performances,
    generate_signal_perturbations
)
from extremum_seeking.filters import (
    HighPassFilter, ConvolutionFilter, LowPassFilter, CascadeFilter
)


if __name__ == "__main__":

    # Plotting Font Setup
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 11.

    # Cost function
    sigma = 1.
    J = lambda t, theta, *args: (
        1. - np.exp(-np.power(theta/sigma, 2.))/(np.sqrt(np.pi)*sigma)
    )
    J.gradient = lambda t, theta, *args: (
        2./np.sqrt(np.pi)*theta/np.power(sigma, 2.)
        *np.exp(-np.power(theta/sigma, 2.))
    )
    J.partial_t = lambda *args: 0.

    # Plot the costfunction
    fig, ax = plt.subplots(1, 1)

    fig.set_size_inches((3, 3))
    ax.set_position([0.18, 0.15, 0.8, 0.77])
    
    thetavec = np.linspace(-2., 2.5)
    ax.plot(thetavec, J(0., thetavec), linewidth=2.)
    ax.set_xlim(thetavec[0], thetavec[-1])

    ax.set_xlabel("Parameter ($\\theta$)")
    ax.set_ylabel("Cost function ($J$)")

    ax.set_xlim(thetavec[0], thetavec[-1])
    ax.set_ylim(0.2, 1.2)

    plt.show()
    
    # Simulation parameters
    tstart = 0.
    tstop = 80.
    dt = 1e-3
    tvec = np.linspace(tstart, tstop, int(np.round((tstop - tstart)/dt)) + 1)
    sim_kargs = {
        't_span' : (tstart, tstop),
        't_eval' : tvec,
    }

    # Plotting setup
    plot_kargs = {
        'linewidth' : 2.
    }
    fig_list = None

    # Initial conditions
    theta_hat_0_dict = {
        'theta_hat' : [2.],
        'theta_hat_dot' : [0.],
        'Gamma_hat': [1.],
        'v_hat': [1.],
    }

    # Parameter update ODE parameters
    param_dict = {
        'k' : [1.],
        'b' : [0.1],
        'omega_l': [1.],
        'odim': [1]
    }
    
    # Derivative estimator filter
    omega_h = 1.
    omega_l = 10.

    # Various perturbation signals
    a_list = [0.3]
    omega_list = [30.]

    for spatial_order in [1, 2]:

        # Get necessary perturbation signals
        signal_list = generate_signal_perturbations(
            a_list, omega_list, spatial_order
        )

        # Create the derivative estimator filter
        hpf = HighPassFilter(omega_h)
        lpf = LowPassFilter(omega_l, ndim=spatial_order)
        conv = ConvolutionFilter(
            lambda t: np.zeros((spatial_order,)),
            odim=spatial_order
        )
        h = CascadeFilter(hpf, conv, lpf)
        z_0_list = np.zeros((1, 1 + spatial_order))

        # Simulate for the various perturbation signals
        fig_list = plot_seeker_parameter_performances(
            J, h, signal_list, param_dict, theta_hat_0_dict, z_0_list,
            sim_kargs, plot_kargs, spatial_order=spatial_order,
            fig_list=fig_list
        )

    for fig in fig_list:
        fig.set_size_inches((6.0, 3.0))
        ax = fig.get_axes()[0]
   
        ax.hlines(
            0., tstart, tstop, linewidth=2., color='k', linestyle='-',
            label="Global Optimum", zorder=3
        )

        ax.set_position([0.1, 0.155, 0.85, 0.825])
                
        ax.grid()
        ax.set_xlim(tstart, tstop)
        ax.set_ylim(thetavec[0], thetavec[-1])
        ax.set_ylabel(r"Parameter ($\theta$)")
        
        ax.set_xlabel("Time ($t$)")
        
        ax.legend(loc='upper right', framealpha=1., ncol=2)
            
    plt.show()
