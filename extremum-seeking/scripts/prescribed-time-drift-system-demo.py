#!/bin/usr/python3

"""
Working script to test and debug implementation of prescribed time to ESCs.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import WashoutFilter
from extremum_seeking.modifiers import dilation_rate, prescribed_time_filter
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import (
    NonholonomicUnicycle, # DriftingNonholonomicUnicycle
)

if __name__ == "__main__":

    # Signal parameters
    P = np.eye(2)  # Something symmetric
    J = lambda t, x: 0.5*x[:2].T@P@x[:2]
    J.gradient = lambda t, x: P@x
    J.partial_t = lambda *args: 0.

    # Seeker parameters
    omega = 25  # nominal angular rates
    k = 10  # gain in the controller
    mu = 0.01  # washout filter parameter (based on inverse)

    h = WashoutFilter(omega=1./mu)
    u = lambda t, x, z: np.array([
        np.sqrt(np.abs(omega)),
        omega + np.sign(omega)*k*z[0]
    ])
    
    # Simulation parameters
    x0 = np.array([2, 1, 0, 0])
    tstart = 0.
    tstop = 10
    dt = 1e-2
    tvec = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))
    
    # Seeker parameters
    omega = 25
    k = 10
    mu = 1e-2
    T = 12

    # Get the standard GESC
    h = WashoutFilter(omega=1./mu)
    u = lambda t, x, z: np.array([
        np.sqrt(np.abs(omega)),
        omega + np.sign(omega)*k*z[0]
    ])

    es = LieBracketSeeker(f=NonholonomicUnicycle(), h=h, J=J, u=u)

    # Solve ODE
    results = solve_ivp(
        fun=es.differential_equation,
        t_span=(tstart, tstop),
        y0=x0,
        t_eval=tvec,
        max_step=0.1
    )
    
    eh = results.y.T
    plot_t = results.t

    # Get the prescribed time GESC
    u_ps = lambda t, x, z: dilation_rate(t, T)*np.array([
        np.sqrt(np.abs(omega)),
        omega + np.sign(omega)*k*z
    ])
    
    ps = LieBracketSeeker(
        f=NonholonomicUnicycle(),
        h=prescribed_time_filter(h, T),
        J=J,
        u=u_ps
    )
    
    results = solve_ivp(
        fun=ps.differential_equation,
        t_span=(tstart, tstop),
        y0=x0,
        t_eval=tvec,
        max_step=0.1
    )
    
    ph = results.y.T
    
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
    plt.plot(ph[:, 0], ph[:, 1], label='Prescribed Time Seeker')
    plt.plot(eh[:, 0], eh[:, 1], label='Exponential Time Seeker')
    ax.contourf(X, Y, Z, alpha=0.2)
    ax.set_aspect('equal')
    ax.grid()
    plt.legend()
    plt.show()
            
