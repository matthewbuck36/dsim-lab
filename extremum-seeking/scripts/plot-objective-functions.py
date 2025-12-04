#!/bin/user/python3
# -* coding:utf-8 *-

"""
Used to generate common helper functions for the examples.
"""

from itertools import product
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from extremum_seeking.objectives import (
    Beale, Rosenbrock, Ackley, Rastrigin, Sphere
)

# Need a dictionary that calls for all the test functions and then prints each graph 
J_dict = {
    "Ackley": Ackley(),
    "Beale": Beale(),
    'Rastrigin': Rastrigin(),
    "Rosenbrock": Rosenbrock(),
    "Sphere": Sphere()
}


# Cost function
J_list = ["Ackley","Beale", "Rastrigin", "Rosenbrock","Sphere"]


for z in range(len(J_list)):

    J = J_dict[J_list[z]]
    global_min, global_min_location = J.global_minimum()
    print(global_min, global_min_location)

    # Set up figure for plotting
    fig, ax = plt.subplots(1, 1)
    # Create contours
    xc = np.linspace(-3, 3, 61)
    yc = np.linspace(-3, 3, 61)

    X, Y = np.meshgrid(xc, yc)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = J( # pylint: disable=not-callable
                0, np.array([X[i, j], Y[i, j]])
            )

    # Plot Contours
    # Check if the function is Rosenbrock or Ackley using isinstance
    if isinstance(J, (Rosenbrock, Beale)):  # Check if J is an instance of Rosenbrock or Beale
        ax.contourf(X, Y, Z, levels=np.logspace(-3, 3.5, 50), cmap='viridis', alpha=0.5)
        ax.plot(global_min_location[0], global_min_location[1], "ro")
    else: 
        plt.title(f"{J_list[z]} Test Function Graph")
        ax.contourf(X, Y, Z, alpha=1.0)
        ax.plot(global_min_location[0], global_min_location[1], "ro")

    # Finish up prettying figure
    ax.grid()
plt.show()