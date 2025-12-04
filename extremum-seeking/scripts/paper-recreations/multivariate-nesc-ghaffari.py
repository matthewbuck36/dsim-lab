#!/bin/usr/python3

"""
Demonstrates the implementation of the Multivariate Newton Extrumum Seeking 
Control in [Ghaffari2012]_

.. [Ghaffari2012] Azad Ghaffari, Miroslav Krstic, Dragan Nesic, "Multivariable
 Newton-based extremum seeking", Automatica, Volume 48, Issue 8, 2012, Pages 
1759-1767, ISSN 0005-1098
"""
# pylint: disable=invalid-name

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from extremum_seeking.filters import (
    HighPassFilter, LowPassFilter, ParallelFilter, ConvolutionFilter,
    CascadeFilter
)
from extremum_seeking.seekers import DirectExtremumSeeker, NewtonFlow


if __name__ == "__main__":

    # Need to add the setup of the values and the cost functions into the script
    # Parameter aspects
    delta = 0.1  # this is a regulation parameter for the frequencies
    omega = 0.1  # set frequency scale
    omega_1 = 70*omega  # first dither frequency
    omega_2 = 50*omega  # second second frequency 
    omega_vec = np.array([omega_1, omega_2])  # Angular velocity vector
    omega_h = 8*delta*omega  # high pass frequency
    omega_l = 10*delta*omega  # low pass frequency
    omega_r = 10*delta*omega  # ricatti frequency
    theta_star = np.array([2, 4])  # desired object location
    a = np.array([.1, .1])  # amplitude of perturbations
    Gamma_init = np.linalg.inv(400*np.eye(2)).flatten()  # Initial Gamma values
    Q_star = -100  # Set Cost value
    theta_init = np.array([2.5, 5]).T
    Kn = np.eye(2)*delta*omega  # Gain matrix for Newton

    # Cost Function
    H = np.array([[100, 30], [30, 20]])  # Hessian for Quadriatic
    Q = lambda t, x: (
        Q_star + 0.5*(x[:2] - theta_star).T @ H @ (x[:2] - theta_star)
    )  # The quadratic cost function
    Q.gradient = lambda t, x: H @ (x[:2] - theta_star)
    
    # Signals f1 - f3
    S = lambda t: a*np.sin(omega_vec*t)  # additive perturbation vector
    S.derivative = lambda t: a*omega_vec*np.cos(omega_vec*t)
    M = lambda t: 2.*np.sin(omega_vec*t)/a
    N = lambda t: np.array([
        [
            16.*(np.sin(omega_1*t)**2 - 0.5)/(a[0]**2),
            4.*np.sin(omega_1*t)*np.sin(omega_2*t)/(a[0]*a[1])
        ],
        [
            4.*np.sin(omega_1*t)*np.sin(omega_2*t)/(a[0]*a[1]),
            16.*(np.sin(omega_2*t)**2 - 0.5)/(a[1]**2)
        ]
    ]).flatten()

    # # Filter setup h
    hpf = HighPassFilter(omega_h, ndim=1) # High pass filter

    # gradient filter aspect
    gradient_est_conv = ConvolutionFilter(M, odim=2)
    gradient_est_lpf = LowPassFilter(omega_l, ndim=2)
    gradient_filter = CascadeFilter(gradient_est_conv, gradient_est_lpf)

    # hessian filter aspect
    hessian_est_conv = ConvolutionFilter(N, odim=4)
    hessian_est_lpf = LowPassFilter(omega_h, ndim=4)
    hessian_filter = CascadeFilter(hessian_est_conv, hessian_est_lpf)

    h = CascadeFilter(hpf, ParallelFilter(gradient_filter, hessian_filter))

    g = NewtonFlow(k=Kn[0, 0], omega_l=omega_r, odim=2)
    
    seeker = DirectExtremumSeeker(
        g=g, h=h, J=Q, p=S
    )  # Form the ESC dynamical system

    # Simulation parameters
    z0 = np.hstack((
        0.,  # High pass filter state
        np.zeros((2,)),  # Initial gradient filter state
        np.zeros((4,))  # H.flatten()  # Initial Hessian filter state
    ))
    theta0 = np.hstack((
        theta_init,
        Gamma_init
    ))
    x0 = seeker.initialize_system(
        z0,
        theta0
    )
    tstart = 0.
    tstop = 600.
    dt = 1e-2
    tvec = np.linspace(tstart, tstop, int(np.ceil((tstop - tstart)/dt)))

    # Solve ODE
    results = solve_ivp(
        fun=seeker.differential_equation,
        t_span=(tstart, tstop),
        y0=x0,
        t_eval=tvec,
        max_step=0.1)
    
    xh = results.y.T  # History of the states

    z_h, theta_h = seeker.parse_history(
        xh
    )  # Seperate states into filter and parameter states

    theta_h, Gamma_h = seeker.g.parse_history(
        theta_h
    )  # Seperate concatenate parameter history into paramers and Gamma

    plot_t = results.t  # Corresponding time stamps

    # Create contours
    xc = np.linspace(1, 3, 61)
    yc = np.linspace(2.5, 5.5, 61)
    X, Y = np.meshgrid(xc, yc)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = Q(0., np.array([X[i, j], Y[i, j]]))

    # Plot trajectory over contours
    fig, ax = plt.subplots(1, 1)
    ax.plot(theta_h[:, 0], theta_h[:, 1], linewidth=2, label="Seeker")
    ax.contourf(X, Y, Z, alpha=0.2)
    ax.grid()
    plt.legend()

    # Generate time history of Gamma inverse
    f = lambda x: np.linalg.inv(x).flatten()
    f_vec = np.vectorize(f, signature='(n,n)->(m)')
    Gamma_inv_h = f_vec(Gamma_h)

    # Plot time history of Gamma inverse
    fig, ax = plt.subplots(1, 1)
    ax.plot(plot_t, Gamma_inv_h[:, 0], label=r"$(\Gamma^{-1})_{11}$")
    ax.plot(plot_t, Gamma_inv_h[:, -1], label=r"$(\Gamma^{-1})_{22}$")
    ax.plot(plot_t, Gamma_inv_h[:, 1], label=r"$(\Gamma^{-1})_{12}$")

    ax.hlines(H[0, 0], plot_t[0], plot_t[-1], color="C0", linestyle="--")
    ax.hlines(H[1, 1], plot_t[0], plot_t[-1], color="C1", linestyle="--")
    ax.hlines(H[0, 1], plot_t[0], plot_t[-1], color="C2", linestyle="--")
    
    ax.set_title("Inverse Gamma Estimate vs Time")
    ax.set_xlabel("Time (t)")
    ax.set_ylabel("Inverse Hessian(t, x)")
    ax.set_xlim(plot_t[0], 100)
    ax.grid(True)
    ax.legend()

    # Show all plots
    plt.show()
