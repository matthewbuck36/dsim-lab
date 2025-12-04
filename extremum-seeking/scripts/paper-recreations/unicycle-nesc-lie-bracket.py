#!/usr/bin/python3

"""
Recreation of a Newton Extremum Seeker from [Todorovski2024]_

.. [Todorovski2024] V. Todorovski and M. Krstic, "Newton Nonholonomic Source 
Seeking for Distance-Dependent Maps," in IEEE Transactions on Automatic Control,
 vol. 70, no. 1, pp. 510-517, Jan. 2025, doi: 10.1109/TAC.2024.3428070
"""

from extremum_seeking.filters import (
    WashoutFilter, ConvolutionFilter, LowPassRicattiFilter,
    ParallelFilter, CascadeFilter
)
from extremum_seeking.seekers import LieBracketSeeker
from extremum_seeking.systems import NonholonomicUnicycle
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

if __name__ == "__main__":

    # Seeker parameters
    omega = 15.  # dither rate
    omega_0 = 1.  # vehicle rotational rate
    alpha = 2.  # normalized perturbation amplitude/gain
    omega_d = 0.3  # filter rate for inverse hessian
    h = 10.  # washout filter parameter (guessed)
    p = 0.61  # some tuning parameter

    c = np.power(omega, 1. - p)  # correction for gradient estimation
    alpha_tilde = alpha*np.power(omega, p)  # perturbation amplitude

    # Cost function (negative of the paper)
    H = 1./100.  # Hessian
    x_star = np.array([1., -1.])
    F_star = -5.  # pylint: disable=invalid-name
    F = lambda t, x: F_star + 0.5*H*np.linalg.norm(x[:2] - x_star)**2.
    F.gradient = (  # pylint: disable=assignment-from-no-return
        lambda t, x: np.hstack((H*(x[:2] - x_star), 0.))
    )

    # Initial States
    x_0 = np.array([4., -4.])  # (x,y) of vehicle
    nu_0 = 0.  # washout filter state
    d_0 = 1.  # inverse hessian estimate

    # Set up filters
    wo_filter = WashoutFilter(omega=h)
    gradient_filter = ConvolutionFilter(f=lambda t: c*np.sin(omega*t), odim=1)
    hessian_filter = ConvolutionFilter(
        f=lambda t: -8.*np.power(omega/alpha_tilde, 2.)*np.cos(2.*omega*t),
        odim=1
    )
    inverse_hessian_filter = LowPassRicattiFilter(omega_l=omega_d, ndim=1)

    h = CascadeFilter(
        wo_filter,
        ParallelFilter(
            gradient_filter,
            CascadeFilter(
                hessian_filter,
                inverse_hessian_filter
            )
        )
    )  # Filter block

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
            alpha_tilde*np.cos(omega*t) - z[0]*z[1],  # Forward Velocity
            omega_0  # Angular velocity
        ])

    # Seeker
    seeker = LieBracketSeeker(f=NonholonomicUnicycle(), h=h, J=F, u=u)
    
    # Simulation parameters
    y_0 = seeker.initialize_system(
        np.hstack((x_0, 0.)),  # (x,y,theta) for unicycle
        np.array([
            nu_0,  # Initial washout filter state
            d_0
        ])
    )
    t_start = 0.
    t_stop = 50.
    t_eval = np.linspace(t_start, t_stop, 501)

    # Simulate system
    results = solve_ivp(
        fun=seeker.differential_equation,
        y0=y_0,
        t_span=(t_start, t_stop),
        t_eval=t_eval
    )

    x_h = results.y.T  # Full augmented state vector
    x_h, z_h = seeker.parse_history(x_h)  # Unicycle and filter states
    t_vec = results.t  # Corresponding times

    # Plot results
    for i in range(2):
        
        fig, ax = plt.subplots(1, 1)

        ax.plot(t_vec, x_h[:, i])
        ax.hlines(x_star[i], t_vec[0], t_vec[-1], linestyle='--', color='k')
        
        ax.set_xlabel("Time ($t$) [sec]")
        ax.set_ylabel("$x_{" + str(i+1) + "}(t)$")
        ax.set_xlim(t_vec[0], t_vec[-1])

        # ax.legend()

    fig, ax = plt.subplots(1, 1)

    ax.plot(t_vec, z_h[:, -1])
    ax.hlines(1./H, t_vec[0], t_vec[-1], linestyle='--', color='k')

    ax.set_xlim(t_vec[0], t_vec[-1])
    ax.set_xlabel("Time ($t$) [sec]")
    ax.set_ylabel("$d(t)$")
        
    plt.show()
