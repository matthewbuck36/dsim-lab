#!/bin/usr/python3

"""
Demonstrates using directions from RMSprop ESC
"""
# pylint: disable=invalid-name

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import DirectionalFilter
from extremum_seeking.seekers import LieBracketSeeker, RMSpropFlow
from extremum_seeking.systems import NonholonomicUnicycle
from example_helpers import  u, k_g, J

if __name__ == "__main__":

    h = DirectionalFilter(RMSpropFlow(k=k_g*np.ones((2,)), omega_l=1.))

    # Sensor returns gradient and gradient element-wise squared
    y = lambda t, x: np.hstack((
        J.gradient(t, x),  # Gradient terms
        J.gradient(t, x)**2  # Gradient squared terms
    ))
    
    seeker = LieBracketSeeker(
        f=NonholonomicUnicycle(),
        h=h, J=y, u=u
    )  # Form the dynamical system

    # Simulation parameters
    x0 = seeker.initialize_system(
        np.array([2, 2, 0]), np.zeros((4,))
    )
    tstart = 0.
    tstop = 10.
    dt = 1e-2
    tvec = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))
    stop_event = lambda t, y: np.linalg.norm(y[:2]) - 1e-2
    stop_event.terminal = True

    # Solve ODE
    results = solve_ivp(
        fun=seeker.differential_equation,
        t_span=(tstart, tstop),
        y0=x0,
        t_eval=tvec,
        max_step=0.1
    )

    xh = results.y.T
    plot_t = results.t

    # Create contours
    xc = np.linspace(-3, 3, 61)
    yc = np.linspace(-3, 3, 61)
    X, Y = np.meshgrid(xc, yc)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = J(0., np.array([X[i, j], Y[i, j]]))

    # Plot
    fig, ax = plt.subplots(1, 1)
    ax.plot(xh[:, 0], xh[:, 1], linewidth=2, label="Seeker")
    ax.contourf(X, Y, Z, alpha=0.2)
    ax.grid()
    plt.legend()
    plt.show()
