#!/bin/usr/python3

"""
Script with a safety filter implemented onto a Lie Bracket GESC.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import WashoutFilter
from extremum_seeking.seekers import LieBracketSeeker

if __name__ == "__main__":
    
    # Simulation parameters
    x0 = np.array([1, 1, 0, 1, -1])
    # xvec = (x, y, theta, safety state, washout state)
    tstart = 0.
    tstop = 1.
    dt = 1e-5
    teval = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))

    # Barrier boundary
    yb = -0.125
    xb = -0.125
    b = lambda x: -np.log(1 - max(0, x[1]/yb))
    # b = lambda x: max(0, -np.log(x[0]/xb - 1))
    
    # Signal parameters
    P = np.array([[1., 0], [0, 1.]])  # np.eye(2)  # Something symmetric
    J = lambda t, x: 0.5 * x[:2].T @ P @ x[:2]
    J.gradient = lambda t, x: np.hstack((P @ x[:2], 0.))
    
    # Seeker parameters
    omega = 35
    k = 4
    mu = 5e-3

    # Cost function filter
    wof = WashoutFilter(omega=1./mu)

    # Add in safety filter
    # Define the obstacle and barrier function portions
    circle_origin = np.array([0.5, 0.5])
    R = 0.4
    h = lambda x: np.sum(np.power(x[:2] - circle_origin, 2)) - R**2
    Lgh = lambda x: (  # pylint: disable=invalid-name
        2*(x[0] - circle_origin[0])*np.cos(x[2])
        + 2*(x[1] - circle_origin[1])*np.sin(x[2])
    )

    # Add in filter portions
    alpha = lambda h: (1 + 13*h)*np.sqrt(h)
    epsilon = 1e-3
    dGamma = lambda Gamma, Lgh_val: (  # pylint: disable=invalid-name
        Gamma*(1 - Gamma*np.power(Lgh_val, 2))/epsilon
    )
    
    def safe_nonholonomic_unicycle_system(t, x, u):  # pylint: disable=redefined-outer-name,unused-argument
        r""" Safe nonholonomic unicycle system

        Function to form the dynamic system of a unicycle with a dynamic 
        feedback controller.

        .. math::
        
            \dot{x} &= u_{s} \cos(\theta) \\
            \dot{y} &= u_{s} \sin(\theta) \\
            \dot{\theta} &= u[1] \\
            \dot{\Gamma} &= \Gamma\cdot\left(1 - \Gamma L_{g}h(x,y,\theta) 
            \right)/\varepsilon 

        where `:math:x`, `:math:y` are the position in 2D space, `:math:\theta`
        is the heading angle, and lastly `:math:\Gamma` is a controller dynamic 
        state. Note that `:math:h` is the control barrier function
        
        .. math::
        
            h(x,y,\theta) = (x - x_c)^2 + (y - y_c)^2  - R^2
        
        and `:math:L_{g}h` is the Lie derivative of `:math:h` with the control
        vector `:math:g` which in this case is forward velocity vector in the
        absolute coordinate system.

        Args:
            t (float): time
            x (np.ndarray): array of [`:math:x`, `:math:`y`, `:math:\theta`, 
              `:math:\Gamma`]
            u (np.ndarray): vector of the current static feedback controller
              states.
        """
        # pylint: disable=unused-variable
        
        # Preallocate derivative vector
        xdot = np.zeros(x.shape)
        
        # Get original control input control input

        # Get barrier function portions
        alpha_h = alpha(h(x[:2]))
        Lgh_val = Lgh(x[:3])  # pylint: disable=invalid-name

        #  Update forward velocity
        # u0_safe = u0*x[-1]*Lgh_val*max(Lgh_val, -alpha_h/u0)
        u0_safe = u[0] + x[-1]*Lgh_val*max(0, -u[0]*Lgh_val -alpha_h)

        # Derivative of state
        xdot[0] = u0_safe*np.cos(x[2])
        xdot[1] = u0_safe*np.sin(x[2])
        xdot[2] = u[1]
        xdot[3] = dGamma(x[3], Lgh_val)
        
        return xdot

    safe_nonholonomic_unicycle_system.ndim = 4

    # Controller
    u = lambda t, x, z: np.array([np.sqrt(omega), omega + k*z], dtype=np.float) 
    
    # Solve ODE
    seeker = LieBracketSeeker(
        f=safe_nonholonomic_unicycle_system, u=u, J=J, h=wof
    )
    results = solve_ivp(
        fun=seeker.differential_equation,
        y0=x0,
        t_span=(tstart, tstop),
        t_eval=teval
    )
    

    cwxh = results.y.T
    tvec = results.t

    """
    tvec, ccwxh = simulateSystem(
        RungeKutta4, nonholonomicUnicycleSystem,
        x0, ccwes,
        tstart, tstop, dt,
        **kargs
    )
    
    tvec, cwxh_nb = simulateSystem(
        RungeKutta4, nonholonomicUnicycleSystem,
        x0, cwes,
        tstart, tstop, dt,
        **{'F': F, 'Ft': Ft}
        )
    """

    # Create contours
    # xc = np.linspace(-3, 1, 41)
    # yc = np.linspace(-1, 1, 21)

    # X, Y = np.meshgrid(xc, yc)
    # Z = np.zeros(X.shape)
    # for i in range(X.shape[0]):
    #     for j in range(Y.shape[1]):
    #         Z[i, j] = F(np.array([X[i, j], Y[i, j]]))

    # Plot
    fig, ax = plt.subplots(1, 1)
    ax.plot(cwxh[:, 0], cwxh[:, 1], linewidth=2, label='CW Exponential Seeker')
    """
    ax.plot(
        ccwxh[:, 0], ccwxh[:, 1],
        linewidth=2, label='CCW Exponential Seeker'
    )
    ax.plot(
        cwxh_nb[:, 0], cwxh_nb[:, 1],
        linewidth=2, label='CW Exponential Seeker w/o BF'
    )
    ax.contourf(X, Y, Z, alpha=0.2)
    """
    """
    ax.fill_between(
        np.array([np.min(xc), np.max(xc)]),
        np.min(yc)*np.ones((2,)),
        np.max(yb)*np.ones((2,)),
        facecolor='k',
        alpha=0.3
    )
    """
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
    plt.show()

    """

    # Plot Sensor Time History
    fig, ax = plt.subplots(1, 1)

    ax.set_title('CW ES Sensor Field Error')
    ax.plot(tvec, 10 - np.apply_along_axis(F, 1, cwxh[:, :2]), label='Sensor')
    ax.plot(tvec, 10 - cwxh[:,-1], label='Washout Filter Output')

    ax.set_xlim(left=0, right=np.max(xc))
    ax.set_ylim(bottom=0)

    plt.show()
    """
