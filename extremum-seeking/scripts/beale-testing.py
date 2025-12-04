"""
Testing of the Beale function.
"""

import numpy as np
import matplotlib.pyplot as plt
from extremum_seeking.objectives import Beale

# Cost function
J = Beale()
global_min, global_min_location = J.global_minimum()
print(global_min, global_min_location)

# Set up figure for plotting
fig, ax = plt.subplots(1, 1)
# Create contours
xc = np.linspace(-4.5, 4.5, 500)
yc = np.linspace(-4.5, 4.5, 500)

X, Y = np.meshgrid(xc, yc)
Z = np.zeros(X.shape)
for i in range(X.shape[0]):
        for j in range(Y.shape[1]):
            Z[i, j] = J( # pylint: disable=not-callable
                0, np.array([X[i, j], Y[i, j]])
            )

    # Plot Contours
ax.contourf(X, Y, Z, levels=np.logspace(-3, 3.5,50), cmap='viridis', alpha = 0.5)
ax.plot(global_min_location[0], global_min_location[1], "ro", label=f"Global Minimum Point {global_min_location}")

    # Finish up prettying figure
ax.grid()
plt.show()
