#!/bin/user/python3
# -* coding:utf-8 *-

"""
Examples of ESC trajectories on a scalar quartic with multiple minimum.
"""
import matplotlib.pyplot as plt
import numpy as np
from example_helpers import (
    plot_seeker_parameter_performances,
    generate_signal_perturbations
)
from extremum_seeking.filters import (
    LowPassFilter, HighPassFilter, ConvolutionFilter, CascadeFilter
)


if __name__ == "__main__":
    
    # Cost function
    J = lambda t, theta, *args: (
        np.power(theta, 4.) + np.power(theta, 3.) - 2.*np.power(theta, 2.)
        - 3.*theta
    )
    J.gradient = lambda t, theta, *args: (
        4.*np.power(theta, 3.) + 3.*np.power(theta, 2.) - 4.*theta - 3.
    )
    J.partial_t = lambda *args: 0.

    # Plot the performance
    fig, ax = plt.subplots(1, 1)
    thetavec = np.linspace(-2.5, 2.)
    ax.plot(thetavec, J(0., thetavec))
    ax.set_xlim(thetavec[0], thetavec[-1])

    ax.set_xlabel("Parameter $\\theta$")
    ax.set_ylabel("Cost function $J(\\theta)$")

    fig.savefig("./figures/cost-functions/quartic-multiple-minimum.png")

    # Simulation parameters
    tstart = 0.
    tstop = 40.
    dt = 1e-3
    tvec = np.linspace(tstart, tstop, int(np.round((tstop - tstart)/dt)) + 1)
    sim_kargs = {
        't_span' : (tstart, tstop),
        't_eval' : tvec,
        'max_step' : 1e-3
    }

    # Plotting setup
    plot_kargs = {
        'linewidth' : 2.
    }
    fig_list = None

    # Initial Conditions
    theta_hat_0_dict = {
        'theta_hat' : [-2.],
        'theta_hat_dot' : [0.],
        'Gamma_hat': [1.],
        'v_hat': [1.],
    }

    # Parameter update ODE parameters
    param_dict = {
        'k' : [0.1],
        'b' : [0.25],
        'omega_l': [0.1],
        'odim': [1],
    }


    # Various perturbation signals
    a_list = [0.1, 0.3]
    omega_list = [30.]

    for spatial_order in [1, 2]:

        # Signals
        signal_list = generate_signal_perturbations(
            a_list, omega_list, spatial_order
        )
        z_odim = np.size(signal_list[0][1](0.))
        
        # Derivative estimator filter
        omega_h = 1.
        omega_l = 10.
        hpf = HighPassFilter(omega_h)
        lpf = LowPassFilter(omega_l, ndim=z_odim)
        conv = ConvolutionFilter(lambda t: np.zeros((z_odim,)), odim=z_odim)
        h = CascadeFilter(hpf, conv, lpf)
        z_0_list = np.zeros((1, 1 + z_odim))

        # Simulate for the various perturbation signals
        fig_list = plot_seeker_parameter_performances(
            J, h, signal_list, param_dict, theta_hat_0_dict, z_0_list,
            sim_kargs, plot_kargs,
            spatial_order=spatial_order, fig_list=fig_list
        )

    for i, fig in enumerate(fig_list):
        ax = fig.get_axes()[0]
   
        ax.hlines(
            1., tstart, tstop, linewidth=2., color='k', linestyle='-',
            label="Global Optimum", zorder=3
        )
        ax.hlines(
            -1., tstart, tstop, linewidth=2., color='k', linestyle='--',
            label="Local Optimum", zorder=3
        )
                
        ax.grid()
        ax.set_xlim(tstart, tstop)
        ax.set_ylim(thetavec[0], thetavec[-1])
        ax.set_ylabel("$\\theta$")
        
        ax.set_xlabel("Time $t$")
        
        ax.legend(loc='lower right', framealpha=1., ncol=2)

        fig.savefig(
            "./figures/convergence-quartic-multiple-minimum-a={}.png".format(
                str(a_list[i]).replace('.', 'p')
            ),
            pad_inches=0.
        )
            
    plt.show()
