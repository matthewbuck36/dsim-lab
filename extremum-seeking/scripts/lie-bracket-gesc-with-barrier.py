#!/bin/usr/python3

"""
Example of using barrier functions with ESCs to create safe ESCs.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import HighPassFilter
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import NonholonomicUnicycle

if __name__ == "__main__":
    
    # Simulation parameters
    x0 = np.array([-2, 0, 0, 0])  # xvec = (x, y, theta, filter)
    tstart = 0.
    tstop = 100.
    dt = 1e-3
    tvec = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))

    # Barrier boundary -- in 2D plane
    yb = -0.125
    xb = -0.125
    b_scale = 0.125
    b_factor = 10.

    # Barrier function -- has seeker stay above limit
    b = lambda x: -b_factor*np.log(np.abs(x[1] - yb)/b_scale)
    b.gradient = lambda x: np.array([
        0.,
        -(b_factor/np.abs(x[1] - yb)*np.sign(x[1] - yb)),
        0.
    ])
    # b = lambda x: max(0, -np.log(x[0]/xb - 1))
    
    # Signal parameters
    P = 1.*np.array([[1., -0.5], [-0.5, 1.]])
    J = lambda t, x: 0.*0.5*x[:2].T @ P @ x[:2]
    J.gradient = lambda t, x: 0.*np.hstack((P@x[:2], 0.))

    J_safety = lambda t, x: J(t, x) + b(x)  # pylint: disable=invalid-name
    J_safety.gradient = lambda t, x: J.gradient(t, x) - b.gradient(x)
    
    # Seeker parameters
    omega = 25
    k = 1.
    mu = 1e-4

    # Filter
    h = HighPassFilter(omega_h=1./mu)
    
    # Controllers
    u_clockwise = lambda t, x, z: (
        np.array([np.sqrt(omega), omega + k*z], dtype=np.float)
    )
    u_counter_clockwise = lambda t, x, z: (
        np.array([np.sqrt(omega), -omega - k*z], dtype=np.float)
    )

    seeker_cw = LieBracketSeeker(
        f=NonholonomicUnicycle(), h=h, J=J_safety, u=u_clockwise
    )
    seeker_cw_unsafe = LieBracketSeeker(
        f=NonholonomicUnicycle(), h=h, J=J, u=u_clockwise
    )
    seeker_ccw = LieBracketSeeker(
        f=NonholonomicUnicycle(), h=h, J=J_safety, u=u_counter_clockwise
    )

    # Solve ODE
    results = solve_ivp(
        fun=seeker_cw.differential_equation,
        t_span=(tstart, tstop),
        y0=x0,
        t_eval=tvec,
        max_step=0.1
    )
    cwxh = results.y.T

    results = solve_ivp(
        fun=seeker_ccw.differential_equation,
        t_span=(tstart, tstop),
        y0=x0,
        t_eval=tvec,
        max_step=0.1
    )
    ccwxh = results.y.T

    results = solve_ivp(
        fun=seeker_cw_unsafe.differential_equation,
        t_span=(tstart, tstop),
        y0=x0,
        t_eval=tvec,
        max_step=0.1
    )
    cwxh_nb = results.y.T
    

    # Create contours
    xc = np.linspace(-3, 1, 41)
    yc = np.linspace(-1, 1, 21)

    X, Y = np.meshgrid(xc, yc)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = J(0, np.array([X[i, j], Y[i, j]]))

    # Plot
    fig, ax = plt.subplots(1, 1)
    ax.plot(cwxh[:, 0], cwxh[:, 1], linewidth=2, label='CW Seeker')
    ax.plot(ccwxh[:, 0], ccwxh[:, 1], linewidth=2, label='CCW Seeker')
    ax.plot(cwxh_nb[:, 0], cwxh_nb[:, 1], linewidth=2, label='CW Seeker w/o BF')
    ax.contourf(X, Y, Z, alpha=0.2)

    ax.fill_between(
        np.array([np.min(xc), np.max(xc)]),
        np.min(yc)*np.ones((2,)),
        np.max(yb)*np.ones((2,)),
        facecolor='k',
        alpha=0.3
    )
    """
    ax.fill_betweenx(
        np.array([np.min(yc), np.max(yc)]),
        xb*np.ones((2,)),
        np.max(xc)*np.ones((2,)),
        facecolor='k',
        alpha=0.3
    )
    """
    ax.grid()
    plt.legend()

    plt.savefig("figures/lie-bracket-gesc-with-barrier.png")
    
    plt.show()


    # Plot Sensor Time History
    """
    fig, ax = plt.subplots(1, 1)

    ax.set_title('CW ES Sensor Field Error')
    ax.plot(
        tvec,
        10 - np.apply_along_axis(
            lambda x: J(0, np.hstack((x, 0.))), 1, cwxh[:, :2]
        ),
        label='Sensor'
    )
    ax.plot(tvec, 10 - cwxh[:,-1], label='Washout Filter Output')

    ax.set_xlim(left=0, right=np.max(xc))
    ax.set_ylim(bottom=0)

    plt.show()
    """
