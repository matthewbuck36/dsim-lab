# Description

This folder contains examples of math simulations with this Turtlebot vehicle.
These simulations make use of filer objects defined in the extremum-seeking package.
These files are useful for testing out filter and controller designs with a simple
simulation, before using those designs and running a simulation in Gazebo.

Additionally, this folder contains a script that will calculate gradient estimation signals for
an ESC controller with sympy. The user must give some details describing the perturbation
singal used, then the code works through the steps to find the matching estimation singal.
Note the perturbation signal describes how the rotating sensor frame spins atop the vehicle.
