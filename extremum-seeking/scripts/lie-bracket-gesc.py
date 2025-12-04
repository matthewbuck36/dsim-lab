#!/bin/usr/python3

"""
Demonstrates a Lie Bracket Extremum Seeker on a Quadratic Map.
"""
# pylint: disable=invalid-name

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import WashoutFilter
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import NonholonomicUnicycle

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

    seeker = LieBracketSeeker(f=NonholonomicUnicycle(), h=h, J=J, u=u)

    # Simulation parameters
    x0 = seeker.initialize_system(np.array([2, 2, 0]), np.zeros((1,)))
    tstart = 0.
    tstop = 10.
    dt = 1e-2
    tvec = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))

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
    ax.plot(xh[:, 0], xh[:, 1], linewidth=2, label='Seeker')
    ax.contourf(X, Y, Z, alpha=0.2)
    ax.grid()
    plt.legend() 
    plt.show()
