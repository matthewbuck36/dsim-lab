#!/usr/bin/python3

"""
Demonstration of the Low Pass Ricatti Filter for inverting matrices.
"""

from extremum_seeking.filters import LowPassRicattiFilter
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


if __name__ == "__main__":

    Y = np.array([[4., 1.], [1., 1.]])
    Y_INV = np.linalg.inv(Y)
    YVEC = Y.flatten('F')
    Y_INV_VEC = Y_INV.flatten('F')
    y = lambda t: YVEC
    yinv = lambda t: Y_INV_VEC
    Z0 = np.eye(2)
    t_eval = np.linspace(0, 1, 201)
    y_h = np.apply_along_axis(
        y,
        1,
        t_eval.reshape(t_eval.shape + (1,))
    )
    yinv_h = np.apply_along_axis(
        yinv,
        1,
        t_eval.reshape(t_eval.shape + (1,))
    )
    
    # Single input single output
    signal_index = 0
    rf = LowPassRicattiFilter(omega_l=1., ndim=1)

    fig, ax = plt.subplots(1, 1)
    ax.plot(t_eval, 1./y_h[:, signal_index], label="Steady State")
    
    for i, z0 in enumerate([0.01, 0.1, 1, 2]):
        result = solve_ivp(
            fun=lambda t, z: (
                rf.differential_equation(t, z, y(t)[signal_index])
            ),
            t_span=(0., 1.),
            y0=np.array([z0]),
            t_eval=t_eval
        )
    
        z_h = result.y.T
        z_h = rf.filter_output(z_h, y_h[:, signal_index])
    
        ax.plot(t_eval, z_h[:, 0], label="$z_{:d}$".format(i + 1))

    ax.set_title("Single Input Single Output Filter for Different IC")
    ax.set_ylabel("Steady State and Output Signals")
    ax.set_xlim(t_eval[0], t_eval[-1])
    ax.set_ylim(bottom=0.)
    ax.legend()

    # Single input single output matrix version
    rf = LowPassRicattiFilter(omega_l=1., ndim=2)

    fig, ax = plt.subplots(4, 1, sharex=True)
    for i in range(yinv_h.shape[1]):
        ax[i].plot(t_eval, yinv_h[:, i], label="$Y^{-1}$")
    
    result = solve_ivp(
        fun=lambda t, z: (
            rf.differential_equation(t, z, y(t))
        ),
        t_span=(0., 1.),
        y0=Z0.flatten('F'),
        t_eval=t_eval
    )
    
    z_h = result.y.T
    z_h = rf.filter_output(z_h, y_h)

    for i in range(z_h.shape[1]):
        ax[i].plot(t_eval, z_h[:, i], label="$Z_{:d}$".format(i+1))

        ax[i].set_ylabel("$X_{{{:d},{:d}}}$".format(i//2 + 1, i%2 + 1))
        
    ax[0].set_title("Matrix Version")
    
    ax[-1].set_xlim(t_eval[0], t_eval[-1])
    ax[0].legend()
    
    plt.show()
    
