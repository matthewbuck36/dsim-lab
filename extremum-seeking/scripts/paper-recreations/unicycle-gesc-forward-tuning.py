#!/usr/bin/python3

"""
Recreation of a Source seeking with non-holonomic unicycle without position 
measurement and with tuning of forward velocity [Zhang2009]_

.. [Zhang2009] C. Zhang , and M. Kristic "Source seeking with non-holonomic 
    unicycle without position measurement and with tuning of forward velocity," 
    in Proc. IEEE Conf. Decision and Control, pp. 5493-5498, 2009, 
    doi: 10.1109/CDC.2009.5400481.
"""

from extremum_seeking.filters import (
    WashoutFilter, ConvolutionFilter, CascadeFilter
)
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import NonholonomicUnicycle
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

if __name__ == "__main__":

    # Filter Parameters
    omega = 25  # Perturbation rate
    alpha = 0.1  # Dither amplitude
    c = 2  # Gain
    h = 1  # Washout Filter
    omega_0 = omega/5  # Vehicle turning rate
    r = 0.2  # Radius of the sensor

    # Cost Function 
    f_star = -1.  # minimum of the cost function
    qx = 0.5
    qy = 0.25
    x_star = np.array([0., 0.])
    H = np.array([[2*qx, 0], [0, 2*qy]])
    
    class CostFunction:
        """ Cost function used in the paper """
        def __init__(self, f_star, H, x_star, r):
            # pylint: disable=redefined-outer-name
            
            self.x_star = x_star
            self.r = r
            self.f_star = f_star
            self.H = H  # pylint: disable=invalid-name
        
        def __call__(self, t, x):
            """ Call signature for the Seeker """
            
            theta = x[2]
            x_s = x[:2] + self.r*np.array([np.cos(theta), np.sin(theta)])
            return (
                self.f_star
                + 0.5*(x_s - self.x_star).T @ self.H @ (x_s - self.x_star)
            )
        
        def gradient(self, t, x):
            
            theta = x[-1]
            x_s = x[:2] + self.r*np.array([np.cos(theta), np.sin(theta)])
            return np.hstack((
                self.H @ (x_s[:2] - self.x_star),
                (
                    self.r*np.array([-np.sin(theta), np.cos(theta)])
                    @ self.H @ (
                        x_s - self.x_star
                    ) # tracks the sensor motion for later
                )
            ))
            
    J = CostFunction(f_star, H, x_star, r)

    # initial states
    x_init = np.array([2, 2])
    theta_init = np.pi
    nu_0 = np.array([f_star])# np.zeros(1,)

    # Setup the filters 
    washout_filter = WashoutFilter(omega=h)
    convolution_filter = ConvolutionFilter(f=lambda t: np.sin(omega*t), odim=1)

    h = CascadeFilter(
        washout_filter,
        convolution_filter
    )

    # Controller
    def u(t, x, z):
        r""" Controller defined in the paper
        
        Args:
            t (float): time
            x (np.ndarray): (x, y, theta) for unicycle model
            z (np.ndarray): [\hat{g}, \hat{d}] where \hat{g} is the gradient
                estimate and \hat{d} is the inverse Hessian estimate.
        
        Return
            np.ndarray: Control value for forward and angular velocity.
        """
        # pylint: disable=unused-argument

        return np.array([
            (alpha*omega*np.cos(omega*t) - c*z[0]),  # Forward Velocity
            omega_0  # Angular velocity
        ])
    
    # # Seeker Needs to be the Lie Bracket
    seeker = LieBracketSeeker(f=NonholonomicUnicycle(), h=h, J=J, u=u)

    # Simulation parameters
    y_0 = seeker.initialize_system(
        np.hstack((x_init, theta_init)),  # (x,y,theta) for unicycle
        nu_0,  # Initial washout filter state
    )
    t_start = 0.
    t_stop = 50.
    t_span = t_stop - t_start
    t_eval = np.hstack((
        t_start,
        t_start + np.logspace(-5, -1, 2001)*t_span,
        np.linspace(t_start + 0.1*t_span, t_stop, 5001)[1:]
    ))

    # Simulate system
    results = solve_ivp(
        fun=seeker.differential_equation,
        y0=y_0,
        t_span=(t_start, t_stop),
        t_eval=t_eval
    )

    xh = results.y.T  # Get the ODE time history states
    xh, zh = seeker.parse_history(
        xh
    )  # Break ODE states into vehicle and filter states
    plot_t = results.t

    J_h = np.zeros(  # pylint: disable=invalid-name
        plot_t.shape
    )  # Preallocate sensor history

    for i in range(plot_t.shape[0]):
        J_h[i] = J(
            plot_t[i],
            np.array([xh[i, 0], xh[i, 1], xh[i, 2]])
        )
        
    v = (
        h.filter_output(plot_t, J_h, zh[:, 0])
        *np.sin(plot_t)*-c
    )

    # Create contours
    xc = np.linspace(-.5, 2.5, 81)
    yc = np.linspace(-.5, 2.5, 81)
    X, Y = np.meshgrid(xc, yc)
    Z = np.zeros(X.shape)
    J.r = 0.  # Collocate sensor and vehicle
    for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = J(0., np.array([X[i, j], Y[i, j], 0]))

    # Plot
    fig, ax = plt.subplots(1, 1)
    ax.plot(xh[:, 0], xh[:, 1], linewidth=2, label="Seeker")
    ax.plot(
        xh[:, 0] + r*np.cos(xh[:, 2]),
        xh[:, 1] + r*np.sin(xh[:, 2]),
        linewidth=2, label="Sensor Position"
    )
    ax.contourf(X, Y, Z, alpha=0.2)
    ax.set_xlim(-0.5, 2.5)
    ax.set_xlabel("$x$ [m]")
    ax.set_ylabel("$y$ [m]")
    ax.grid()
    plt.legend()

    fig, ax = plt.subplots(1, 1)
    ax.plot(plot_t, -J_h)
    ax.set_xlim(0, t_stop)
    ax.set_ylabel("Negative Cost Function ($-J$)")
    ax.set_xlabel("Time ($t$) [sec]")
    ax.grid()

    fig, ax = plt.subplots(1, 1)
    ax.plot(plot_t, v)
    ax.set_xlim(0, t_stop)
    ax.set_ylabel("Velocity ($v$) [sec]")
    ax.set_xlabel("Time ($t$) [sec]")
    ax.grid()

    plt.show()
