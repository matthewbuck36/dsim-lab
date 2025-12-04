#!/bin/user/python3
# -* coding:utf-8 *-

"""
Example of ESC trajectories on a multivariable function.
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
    
    # Cost function
    Q = np.array([[5., 2.], [0., 1.]])
    Q = 0.5*(Q + Q.T)
    J = lambda t, theta, *args: (
        1./2.*theta.T @ Q @ theta
    )
    J.gradient = lambda t, theta, *args: (
        Q @ theta
    )
    J.partial_t = lambda *args: 0.

    # Plot the performance
    fig, ax = plt.subplots(1, 1)
    thetavec = np.linspace(-1., 3.)
    T1, T2 = np.meshgrid(thetavec, thetavec)
    THETA = np.stack((T1, T2), axis=2)
    JVEC = np.apply_along_axis(
        lambda x: J(0, x),
        2,
        THETA
    )
    ax.contourf(T1, T2, JVEC, levels=10)
    ax.set_xlim(thetavec[0], thetavec[-1])
    ax.set_ylim(thetavec[0], thetavec[-1])

    ax.set_xlabel("Parameter $\\theta_1$")
    ax.set_ylabel("Parameter $\\theta_2$")

    # Simulation parameters
    tstart = 0.
    tstop = 40.
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
        'theta_hat' : [np.array([2., 2.])],
        'theta_hat_dot' : [np.zeros((2,))],
        'Gamma_hat': [np.eye(2).flatten()],
        'v_hat': [np.array([1., 1.])],
    }

    # Parameter update ODE parameters
    param_dict = {
        'k' : [0.1*np.eye(2)],
        'b' : [0.25],
        'omega_l': [0.1],
        'odim': [2],
    }
    
    # Various perturbation signals
    a_0 = np.array([0.3])
    omega_0 = np.array([30.])
    a_r = np.array([1., 1.])  # Relative amplitude to baseline
    omega_r = np.array([1., 4.])  # Relative rates to baseline

    for spatial_order in [1, 2]:

        if spatial_order == 2:
            # Edit the parameter inputs for Hessian
            param_dict['k'] = [k[0, 0] for k in param_dict['k']]
        
        # Get the signals
        signal_list = generate_signal_perturbations(
            np.outer(a_0, a_r), np.outer(omega_0, omega_r),
            spatial_order=spatial_order
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

    for fig in fig_list:
        for i, ax in enumerate(fig.get_axes()):
   
            ax.hlines(
                0., tstart, tstop, linewidth=2., color='k', linestyle='-',
                label="Global Optimum", zorder=3
            )
                
            ax.grid()
            ax.set_xlim(tstart, tstop)
            ax.set_ylim(thetavec[0], thetavec[-1])
            ax.set_ylabel("$\\theta_{}$".format(i+1))
        
            ax.set_xlabel("Time $t$")
        
            ax.legend(loc='upper right', framealpha=1., ncol=2)
            
    plt.show()
