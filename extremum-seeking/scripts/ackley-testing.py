#!/bin/usr/python3

"""
Script for testing out ESCs on the Ackley function.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import WashoutFilter
from extremum_seeking.objectives import Ackley
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import NonholonomicUnicycle


def generate_u(omega, k):  # pylint: disable=redefined-outer-name
    return lambda t, x, z: np.array([
        np.sqrt(np.abs(omega)), omega + np.sign(omega)*k*z[0]  
    ])

def generate_seeker(omega, k, mu):  # pylint: disable=redefined-outer-name
    h = WashoutFilter(omega=1./mu)
    u = generate_u(omega, k)
    return LieBracketSeeker(f=NonholonomicUnicycle(), h=h, J=Ackley(), u=u)
    

if __name__ == "__main__":
    
    # Simulation parameters
    x0 = np.array([2., 2., 0., 0.])  # xvec = (x, y, theta, filter)
    tstart = 0.
    tstop = 3.
    dt = 1e-3
    tvec = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))

    # Cost function
    J = Ackley()
    
    # Create Signal Contours
    xc = np.linspace(-4, 4, 61)
    yc = np.linspace(-4, 4, 61)

    X, Y = np.meshgrid(xc, yc)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = J.evaluate(np.array([X[i, j], Y[i, j]]))
            
    # Iterate over some plots
    for case in [2]:
        if case == 0:
            # Standard Seeker parameters
            omega = 25
            k = 8.
            mu = 0.01
            seeker = generate_seeker(omega, k, mu)
            
            # Set up figure for plotting the radial tests
            fig, ax = plt.subplots(1, 1)
            fig.suptitle("Differential Wheeled Robots at different IC")
            
            # Iterate over seeker parameters and IC
            flag_initial_label = False
            n_theta = 8
            dtheta = 2.*np.pi/n_theta
            p0_vec = np.empty([n_theta*2, 2], dtype=np.float)
            
            for i in range(8):
                for r in np.arange(1, 3):
                    # Solve ODE
                    p0 = r*np.array([np.cos(i*dtheta), np.sin(i*dtheta)])
                    x0[:2] = p0
                    
                    # Solve ODE
                    results = solve_ivp(
                        fun=seeker.differential_equation,
                        t_span=(tstart, tstop),
                        y0=x0,
                        t_eval=tvec,
                        max_step=0.1
                    )
                    
                    xh = results.y.T
                    t_plot = results.t
                    
                    lo_index = t_plot.size//10
                    
                    # Plot trajectory
                    ax.plot(xh[:, 0], xh[:, 1], linewidth=2)
                    ax.plot(
                        xh[-lo_index:, 0], xh[-lo_index:, 1],
                        linewidth=4, color='k',
                        label=(
                            ("_" if flag_initial_label else "")
                            + "Limiting Orbit"
                        )
                    )
                    
                    flag_initial_label = True
                    
                    # Plot initial conditions
                    ax.scatter(
                        p0_vec[:, 0], p0_vec[:, 1],
                        marker='o', color='k', label="Starting Point"
                    )
                    # Plot Contours
                    ax.contourf(X, Y, Z, alpha=0.2)
                    ax.legend()
                    ax.grid()

        if case == 1:

            x0 = np.zeros((4,))
            k = 5.
            mu = 1e-3
            
            # Iteration sweep variables for different seekers
            omega_tests = [25., 9., 1.]
            p0_tests = np.array([
                [2., 2.],
                [0.5, 1.5],
                [-2., 2.],
            ])
            tstop_tests = [3., 30., 200.]
            dt_tests = [1e-3, 1e-3, 5e-2]
            
            # Set up figure for plotting
            fig, ax = plt.subplots(1, 1)
            fig.suptitle(
                "Differential Wheeled Robots at different perturbation "
                "magnitudes."
            )
            
            # Plot start points
            ax.scatter(
                p0_tests[:, 0], p0_tests[:, 1],
                marker='o', color='k', label="Starting Point"
            )
            
            # Iterate over seeker parameters and IC
            for omega, p0, tstop, dt in zip(
                    omega_tests,
                    p0_tests,
                    tstop_tests,
                    dt_tests
            ):
                
                seeker = generate_seeker(omega, k, mu)
                # Solve ODE
                x0[:2] = p0

                # Solve ODE
                results = solve_ivp(
                    fun=seeker.differential_equation,
                    t_span=(tstart, tstop),
                    y0=x0,
                    # max_step = 0.1
                )

                xh = results.y.T
                t_plot = results.t

                # Plot trajectory
                ax.plot(
                    xh[:, 0], xh[:, 1],
                    linewidth=2, label="$\\omega={}$".format(omega)
                )
        
            # Plot Contours
            ax.contourf(X, Y, Z, alpha=0.2)

            # Finish up prettying figure
            ax.grid()
            plt.legend()

        if case == 2:

            # Set up figure for plotting
            fig, ax = plt.subplots(1, 1)
            fig.suptitle("Differential Wheeled Robots at different gains")
    
            # Iteration sweep variables for different seekers
            k_tests = np.logspace(1, 2, 3)
            tstop_tests = 1.5*np.ones(k_tests.shape)
    
            # Baseline ESC
            x0 = np.zeros((4,))
            x0[:2] = 2.*np.array([np.cos(np.pi/4), np.sin(np.pi/4)])
            omega = 25.
            mu = 1e-2
            dt = 1e-3
            tstart = 0.
            tstop = 2.
            
            # Plot start points
            ax.scatter(
                x0[0], x0[1],
                marker='o', color='k', label="Starting Point"
            )
    
            # Iterate over seeker parameters and IC
            for k, tstop in zip(
                    k_tests,
                    tstop_tests
            ):

                tvec = np.linspace(
                    tstart, tstop, int(np.ceil((tstop - tstart)/dt))
                )
                seeker = generate_seeker(omega, k, mu)
                
                # Solve ODE
                results = solve_ivp(
                    fun=seeker.differential_equation,
                    t_span=(tstart, tstop),
                    y0=x0,
                    t_eval=tvec,
                    max_step=0.01
                )

                xh = results.y.T
                t_plot = results.t

                # Plot trajectory
                ax.plot(
                    xh[:, 0], xh[:, 1],
                    linewidth=2, label="$k={:2.2}$".format(k)
                )

                # Plot last portion
                # ax.plot(xh[-100:, 0], xh[-100:, 1], linewidth=2, color='k')
        
            # Plot Contours
            ax.contourf(X, Y, Z, alpha=0.2)

            # Finish up prettying figure
            ax.grid()
            plt.legend()
    
        # Plot all figures
        plt.show()
