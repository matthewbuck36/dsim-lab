#!/bin/usr/python3

"""
Old script meant to recreate the results of a paper. Never successful.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from seekers import ExponentialSeeker3D, nonholonomicUnicycleSystem3D
from seekers import simulateSystem, RungeKutta4

# Still needs work to demo a stable case

if __name__ == "__main__":
    
    # Simulation parameters
    x0 = np.array([1, 0.1, 0.3, 0, 0, 0])
    tstart = 0.
    tstop = 30
    dt = 1e-3
    sys = nonholonomicUnicycleSystem3D
    
    # Seeker parameters
    Vc = 0.1
    omega = 25
    a = 0.5
    k_alpha = np.array([100, 300])
    k_theta = np.array([100, 300])
    mu = 1e-1
    R = 0.1

    es = ExponentialSeeker3D(Vc, omega, a, k_alpha, k_theta, mu)

    # Signal parameters
    P = np.eye(3)  # Something symmetric
    s_offset = lambda theta, R: R*np.array([  # Sensor offset
        np.cos(theta[0])*np.cos(theta[1]),
        np.cos(theta[0])*np.sin(theta[1]),
        np.sin(theta[0])
        ])
    F = lambda x, R=R: 10 - 0.5*(
        (x[:3] + s_offset(x[3:5], R)).T
        @ P @
        (x[:3] + s_offset(x[3:5], R))
        )
    gradF = lambda x: -P@x
    Ft = lambda x, scale: (F(x[:2]) - x[-1])/scale  # Incorporating the washout
    E = lambda kappa: kappa*np.array([[-1, 0], [0, -1]])
    kappa = 1.

    kargs = {
        'E': E,
        'F': F, 
        'Ft': Ft,
        'gradF': gradF,
    }
    
    # Solve ODE
    tvec, eh = simulateSystem(
        RungeKutta4, sys,
        x0, es,
        tstart, tstop, dt,
        **kargs
    )

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.plot(eh[:, 0], eh[:, 1], eh[:, 2])
    # ax.set_aspect('equal')
    plt.show()
            
