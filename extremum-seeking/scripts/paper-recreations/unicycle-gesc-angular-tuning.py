#!/usr/bin/python3

"""
Nonholonomic Source Seeking With
Tuning of Angular Velocity [JCochran2009]_

.. [JCochran2009] J. Cochran , and M. Kristic " Nonholonomic Source Seeking With
Tuning of Angular Velocity," in Proc. IEEE Conf. Decision and Control, 
pp. 5493-5498, 2009, doi: 10.1109/CDC.2009.5400481.
"""

from extremum_seeking.filters import WashoutFilter
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import NonholonomicUnicycle
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from typing import Callable

if __name__ == "__main__":

    # Filter Parameters
    a = 0.5 # alpha gain
    d = 10
    c = 100 # additive gain
    Vc = 0.1 # forward velocity, pylint: disable=invalid-name
    omega = 40 
    R = 0.1
    h = 1  # washout filer
    
    # Cost Function (It is a maximization but setup as a minimization)
    f_star = -0  # minimum of the cost function
    qr = 1.5
    qp = 0.25
    x_star = np.array([1, 1])
    x_star_f = lambda t: np.array([0.5*np.sin(0.13*t), 0.5*np.sin(0.26*t)])
    H = np.array([[1, 0], [0, 1]])

    # Initial filter states and system states
    x_init = np.array([1., 1.])# np.array([0, 0])
    theta_init = 0
    nu_0 = 0

    class CostFunction:
        """ Cost function used in the paper without time in the x_star """
        def __init__(self, f_star, H, x_star, r):
            # pylint: disable=redefined-outer-name
            
            self.x_star = x_star
            self.r = r
            self.f_star = f_star
            self.H = H  # pylint: disable=invalid-name
        
        def __call__(self, t, x):
            """ Call signature for the Seeker """
            # pylint: disable=unused-argument
            
            theta = x[-1]
            x_s = x[:2] + self.r*np.array([np.cos(theta), np.sin(theta)])
            if isinstance(self.x_star, Callable):
                x_opt = self.x_star(t)
            else:
                x_opt = self.x_star
            return (
                self.f_star
                + qr*np.linalg.norm(x_s - x_opt)**2.
            )
                        
    J = CostFunction(f_star, H, x_star_f, R)  
    
    # Controller (set)
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
            Vc, # forward velocity set to be a constant
            (
                a*omega*np.cos(omega*t)
                - (c - d*z[0])*np.sin(omega*t)*z[0]
            ) # Angular velocity
        ])
    
    # next step is setting up the filter
    # Setup the filters 
    washout_filter = WashoutFilter(omega=h)
    h = washout_filter

    # # Seeker Needs to be the Lie Bracket
    seeker = LieBracketSeeker(f=NonholonomicUnicycle(), h=h, J=J, u=u)

    # Simulation parameters
    y_0 = seeker.initialize_system(
        np.hstack((x_init, theta_init)),  # (x,y,theta) for unicycle
        nu_0,  # Initial washout filter state
    )
    t_start = 0.
    t_stop = 100.
    t_eval = np.linspace(t_start, t_stop, 5000)

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
        J_h[i] = J(0., np.array([xh[i, 0], xh[i, 1]]))
        
    v = h.filter_output(plot_t, J_h, zh[:, 0])

    # Get stored data as a matrix
    x_star_matrix = np.apply_along_axis(x_star_f, 0, t_eval).T
    print(x_star_matrix.shape)

    # Plot
    fig, ax = plt.subplots(1, 1)
    ax.plot(xh[:, 0], xh[:, 1], linewidth=2, label="Vehicle")
    ax.plot(
        x_star_matrix[:, 0],
        x_star_matrix[:, 1],
        linewidth=2, label="Source"
    )
    ax.set_xlim(-0.6, 1)
    ax.set_ylim(-0.6, 1)
    ax.set_xlabel("$x$ [m]")
    ax.set_ylabel("$y$ [m]")
    ax.grid()
    ax.legend()

    plt.show()

