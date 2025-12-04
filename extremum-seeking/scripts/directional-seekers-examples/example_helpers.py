#!/bin/usr/python3

"""
Demonstrates using this python code to contain all the
repetitive aspects of the examples in this folder.
"""
# pylint: disable=invalid-name
import numpy as np

# Signal parameters with the Cost Function
P = np.eye(2)  # Hessian for quadratic
J = lambda t, x: 0.5*x[:2].T@P@x[:2]  # Cost function
J.gradient = lambda t, x: P@x[:2]  # Gradient of cost function
# Gradient outer product of the cost function
J.gop = lambda t, x: (
    np.asarray((np.asmatrix(P@x[:2]).T @ np.asmatrix(P@x[:2])).flatten('F')).reshape((-1,))
)
J.gradient_with_gop = lambda t, x:(
    np.concatenate((J.gradient(t,x), J.gop(t,x)))
)
J.hessian = lambda t, x: P.flatten()  # Vector for solver
J.partial_t = lambda *args: 0.  # Autonomous function
J_derivatives = lambda t, x: np.hstack((
    J.gradient(t, x), J.hessian(t, x)
))

# Seeker parameters
k_g = 1. # gain in the parameter ODE
k_v = 0.5 # gain in the velocity controller
k_t = 2. # gain in the heading angle controller

# Controller input
def u(t, x, z):
    """  Controller for the vehicle
    Args:
    t (float): time
    x (np.ndarray): (3,) vector of system states
    z (np.ndarray): (2,) vector of desired direction of motion
    """
    # pylint: disable=unused-argument

    theta = x[-1]  # Heading angle
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    z_rel = R.T@z  # z in the vehicle centric frame
    return np.array([k_v*z_rel[0], -k_t*z_rel[1]])
