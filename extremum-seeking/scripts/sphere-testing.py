"""
Testing of the Sphere function.
"""

import numpy as np
import matplotlib.pyplot as plt
from extremum_seeking.objectives import Sphere

# Cost function
J = Sphere()  # pylint: disable=redefined-outer-name
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
ax.contourf(X, Y, Z, alpha=1.0)
ax.plot(global_min_location[0], global_min_location[1],
        global_min_location[2], "ro")

# Finish up prettying figure
ax.grid()
plt.show()
