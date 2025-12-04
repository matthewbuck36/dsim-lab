#!/bin/usr/python3

"""
Testing of ESCs on the Rastrigin function.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import WashoutFilter
from extremum_seeking.objectives import Rastrigin
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import NonholonomicUnicycle

def generate_u(omega, k):  # pylint: disable=redefined-outer-name
    return lambda t, x, z: np.array([
        np.sqrt(np.abs(omega)), omega + np.sign(omega)*k*z[0]
    ])

def generate_seeker(omega, k, mu):  # pylint: disable=redefined-outer-name
    h = WashoutFilter(omega=1./mu)
    u = generate_u(omega, k)
    return LieBracketSeeker(f=NonholonomicUnicycle(), h=h, J=Rastrigin(), u=u)


if __name__ == "__main__":

    # Set up figure for plotting
    fig, ax = plt.subplots(1, 1)
    
    # Simulation parameters
    x0 = np.array([2., 2., 0., 0.])  # xvec = (x, y, theta, filter)
    tstart = 0.
    dt = 1e-3

    # Cost function
    J = Rastrigin()
    
    # Seeker parameters
    # omega = 25
    k = 1.2
    mu = 0.01

    # Iteration sweep variables
    omega_tests = [25., 25., 1., 0.0001]
    p0_tests = np.array([
        [2., 2.],
        [0.5, 1.5],
        [-2., 2.],
        [2., -2.]
    ])
    tstop_tests = [3., 3., 40.]
    dt_tests = [1e-3, 1e-3, 5e-2]

    # Plot start points
    ax.scatter(p0_tests[:, 0], p0_tests[:, 1], marker='o', color='k')
    
    # Iterate over seeker parameters and IC
    for omega, p0, tstop, dt in zip(
            omega_tests,
            p0_tests,
            tstop_tests,
            dt_tests
    ):
    
        es = generate_seeker(omega, k, mu)

        # Solve ODE with specified initial vehicle placement.
        x0[:2] = p0
        tvec = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))
        
        results = solve_ivp(
            fun=es.differential_equation,
            t_span=(tstart, tstop),
            y0=x0,
            t_eval=tvec,
            max_step=0.1
        )

        xh = results.y.T

        # Plot trajectory
        ax.plot(xh[:, 0], xh[:, 1], linewidth=2)
        ax.plot(xh[-100:, 0], xh[-100:, 1], linewidth=2, color='k')
        
    # Create contours
    xc = np.linspace(-3, 3, 61)
    yc = np.linspace(-3, 3, 61)

    X, Y = np.meshgrid(xc, yc)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = J( # pylint: disable=not-callable
                0, np.array([X[i, j], Y[i, j]])
            )

    # Plot Contours
    ax.contourf(X, Y, Z, alpha=0.2)

    # Finish up prettying figure
    ax.grid()
    plt.show()
