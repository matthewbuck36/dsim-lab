#!/usr/bin/python3

r"""
Demostration of using the High Pass Filter.

.. math::

    \frac{d}{dt}z = \left(\frac{d}{dt} y \right) - \omega_{h} z


"""

from extremum_seeking.filters import HighPassFilter
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
    omega_0 = 20.  # Baseline signal rate
    r_omega = np.array([0.2, 1., 2., 3.])  # Relative signal rates
    y = lambda t: np.sin(r_omega*omega_0*t) + 1.  # Signals
    ydot = lambda t: r_omega*omega_0*np.cos(r_omega*omega_0*t)  # Derivatives
    t_eval = np.linspace(0., 1., 201)
    y_h = np.apply_along_axis(
        y,
        1,
        t_eval.reshape(t_eval.shape + (1,))
    )
    ydot_h = np.apply_along_axis(
        ydot,
        1,
        t_eval.reshape(t_eval.shape + (1,))
    )

    fig, ax = plt.subplots(1, 1)
    for i in range(y_h.shape[1]):
        ax.plot(t_eval, y_h[:, i], label="$y_{:d}$".format(i+1))

    manipulate_plots(fig, ax)
    ax.set_title("Input signals")

    # High Pass Filter with single input and single output
    signal_index = 3
    hpf = HighPassFilter(omega_h=10.)
    
    result = solve_ivp(
        fun=lambda t, z: (
            hpf.differential_equation(t, z, ydot(t)[signal_index])
        ),
        t_span=(0., 1.),
        y0=np.zeros((hpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = hpf.filter_output(z_h, y_h[:, signal_index])
    if z_h.ndim < 2:
        z_h = z_h.reshape(z_h.shape + (1,))

    fig, ax = plt.subplots(1, 1)

    ax.plot(
        t_eval, y_h[:, signal_index],
        label="$y_{}$".format(signal_index + 1)
    )
    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{}$".format(signal_index + 1))

    manipulate_plots(fig, ax)
    ax.set_title("Single Input Single Output")
    ax.set_ylabel("Filter Outputs ($z_i$)")
    
    # High Pass Filter with a single filter gain for multiple input signals
    hpf = HighPassFilter(omega_h=1., ndim=y(0).size)
    
    result = solve_ivp(
        fun=lambda t, z: (
            hpf.differential_equation(t, z, ydot(t))
        ),
        t_span=(0., 1.),
        y0=np.zeros((hpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = hpf.filter_output(z_h)

    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{}$".format(i + 1))

    manipulate_plots(fig, ax)
    ax.set_title("Multiple signals using common filter gain")
    ax.set_ylabel("Filter Outputs ($z_i$)")

    # High Pass Filter with multiple filter gain for single input
    signal_index = 1
    hpf = HighPassFilter(omega_h=10.*r_omega)
    
    result = solve_ivp(
        fun=lambda t, z: (
            hpf.differential_equation(t, z, ydot(t)[signal_index])
        ),
        t_span=(0., 1.),
        y0=np.zeros((hpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = hpf.filter_output(z_h)

    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{}$".format(i + 1))

    manipulate_plots(fig, ax)
    ax.set_title("One signal using different filter gain")
    ax.set_ylabel("Filter Outputs ($z_i$)")
    
    # High Pass Filter with multiple filter gain for multiple input signals
    hpf = HighPassFilter(omega_h=10.*r_omega)
    
    result = solve_ivp(
        fun=lambda t, z: (
            hpf.differential_equation(t, z, ydot(t))
        ),
        t_span=(0., 1.),
        y0=np.zeros((hpf.ndim,)),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = hpf.filter_output(z_h)

    fig, ax = plt.subplots(1, 1)

    for i in range(z_h.shape[1]):
        ax.plot(t_eval, z_h[:, i], label="$z_{}$".format(i + 1))

    manipulate_plots(fig, ax)
    ax.set_title("Multiple signals using different filter gain")
    ax.set_ylabel("Filter Outputs ($z_i$)")
    
    plt.show()
