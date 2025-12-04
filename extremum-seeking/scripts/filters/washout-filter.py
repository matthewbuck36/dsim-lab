#!/usr/bin/python3

"""
Example usage of the Washout Filter
"""

from extremum_seeking.filters import WashoutFilter
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


if __name__ == "__main__":

    # Common figure manipulation
    def manipulate_plots(figure, axis):
        """ Figure and Axis manipulations """
        # pylint: disable=unused-argument
        # Figure manipulations
        
        # Axis manipulations
        axis.set_xlim(t_eval[0], t_eval[-1])
        axis.set_xlabel("Time $t$")
        axis.set_ylabel("$y_i$")
        axis.legend()

    omega_0 = 20.
    r_omega = np.array([0.2, 1., 2., 3.])  # Relative signal rates
    y = lambda t: np.sin(r_omega*omega_0*t) + 1.  # Signals
    t_eval = np.linspace(0., 1., 201)
    y_h = np.apply_along_axis(
        y,
        1,
        t_eval.reshape(t_eval.shape + (1,))
    )

    fig, ax = plt.subplots(1, 1)
    for i in range(y_h.shape[1]):
        ax.plot(t_eval, y_h[:, i], label="$y_{:d}$".format(i+1))

    manipulate_plots(fig, ax)
    ax.set_title("Input signals")

    # Washout Filter with single input and single output
    signal_index = 1
    wo = WashoutFilter(omega=10.)
    
    result = solve_ivp(
        fun=lambda t, z: (
            wo.differential_equation(t, z, y(t)[signal_index])
        ),
        t_span=(0., 1.),
        y0=np.zeros((wo.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T[:]
    z_h = z_h[:, 0]
    z_h = wo.filter_output(z_h, y_h[:, signal_index])

    fig, ax = plt.subplots(1, 1)

    ax.plot(
        t_eval, y_h[:, signal_index],
        label="$y_{}$".format(signal_index + 1)
    )
    ax.plot(t_eval, z_h, label="$z_{}$".format(signal_index + 1))

    manipulate_plots(fig, ax)
    ax.set_title("Single input single output")
    ax.set_ylabel("Filter Outputs ($z_i$)")
    
    # Washout Filter with a single filter gain for multiple signals
    wo = WashoutFilter(omega=10., ndim=y(0).size)
    
    result = solve_ivp(
        fun=lambda t, z: (
            wo.differential_equation(t, z, y(t))
        ),
        t_span=(0., 1.),
        y0=np.zeros((wo.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = wo.filter_output(z_h, y_h)
    
    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{:d}$".format(i+1))

    manipulate_plots(fig, ax)
    ax.set_title("Multiple signals using common filter gain")
    ax.set_ylabel("Filter Outputs ($z_i$)")

    # Washout Filter with multiple filter gains for single input
    signal_index = 1
    wo = WashoutFilter(omega=(1.*r_omega))
    
    result = solve_ivp(
        fun=lambda t, z: (
            wo.differential_equation(t, z, y(t)[signal_index])
        ),
        t_span=(0., 1.),
        y0=np.zeros((wo.ndim,)),
        t_eval=t_eval,
    )
    
    z_h = result.y.T
    z_h = wo.filter_output(z_h, y_h)

    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{}$".format(i + 1))

    manipulate_plots(fig, ax)
    ax.set_title("One signal using different filter gains")
    ax.set_ylabel("Filter Outputs ($z_i$)")
    
    # Low Pass Filter with a single filter gain for multiple signals
    wo = WashoutFilter(omega=(1.*r_omega))
    
    result = solve_ivp(
        fun=lambda t, z: (
            wo.differential_equation(t, z, y(t))
        ),
        t_span=(0., 1.),
        y0=np.zeros((wo.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = wo.filter_output(z_h, y_h)
    
    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{:d}$".format(i+1))

    manipulate_plots(fig, ax)
    ax.set_title("Multiple signals using different filter gain")
    ax.set_ylabel("Filter Outputs ($z_i$)")
    
    plt.show()
