#!/usr/bin/python3

"""
Example usage of the Low Pass Filter
"""

from extremum_seeking.filters import LowPassFilter
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

    # Input signals
    omega_0 = 10.  # Baseline signal rate
    omega_r = np.array([0.1, 0.2, 1., 2., 3.])  # Relative signal rates
    y = lambda t: np.sin(omega_r*omega_0*t) + 1.
    t_eval = np.linspace(0., 1., 201)
    y_h = np.apply_along_axis(
        y,
        1,
        t_eval.reshape(t_eval.shape + (1,))
    )

    fig, ax = plt.subplots(1, 1)
    for i in range(y_h.shape[1]):
        ax.plot(t_eval, y_h[:, i], label="$y_{:d}$".format(i+1))

    ax.set_title("Input signals")
    manipulate_plots(fig, ax)
    
    # Low Pass Filter with a single filter gain for a single signal
    signal_index = 1
    lpf = LowPassFilter(omega_l=10.)
    
    result = solve_ivp(
        fun=lambda t, z: (
            lpf.differential_equation(t, z, y(t)[signal_index])
        ),
        t_span=(0., 1.),
        y0=np.zeros((lpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = lpf.filter_output(z_h)
    
    fig, ax = plt.subplots(1, 1)

    ax.plot(
        t_eval, y_h[:, signal_index],
        label="$y_{:d}$".format(signal_index + 1)
    )
    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{:d}$".format(signal_index + 1))

    ax.set_title("Single Signal Low Pass Filter")
    manipulate_plots(fig, ax)
    ax.set_ylabel("Intput and Output Signals")
    
    # Low Pass Filter with a single filter gain for multiple signals
    lpf = LowPassFilter(omega_l=10., ndim=y(0).size)
    
    result = solve_ivp(
        fun=lambda t, z: (
            lpf.differential_equation(t, z, y(t))
        ),
        t_span=(0., 1.),
        y0=np.zeros((lpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = lpf.filter_output(z_h)
    
    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{:d}$".format(i+1))

    manipulate_plots(fig, ax)
    ax.set_title("Multiple signals using common filter gain")
    ax.set_ylabel("Filter Outputs ($z_i$)")

    # Low Pass Filter with multiple filter gains for single input
    signal_index = 1
    lpf = LowPassFilter(omega_l=10.*omega_r)
    
    result = solve_ivp(
        fun=lambda t, z: (
            lpf.differential_equation(t, z, y(t)[signal_index])
        ),
        t_span=(0., 1.),
        y0=np.zeros((lpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = lpf.filter_output(z_h)

    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{}$".format(i + 1))

    manipulate_plots(fig, ax)
    ax.set_title("One signal using different filter gains")
    ax.set_ylabel("Filter Outputs ($z_i$)")
    
    # Low Pass Filter with a single filter gain for multiple signals
    lpf = LowPassFilter(omega_l=10.*omega_r)
    
    result = solve_ivp(
        fun=lambda t, z: (
            lpf.differential_equation(t, z, y(t))
        ),
        t_span=(0., 1.),
        y0=np.zeros((lpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = lpf.filter_output(z_h)
    
    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{:d}$".format(i+1))

    manipulate_plots(fig, ax)
    ax.set_title("Multiple signals using different filter gain")
    ax.set_ylabel("Filter Outputs ($z_i$)")

    
    plt.show()
