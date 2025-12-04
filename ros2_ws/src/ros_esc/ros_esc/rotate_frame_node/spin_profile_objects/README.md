# Description:

This folder contains examples of spin profile objects which describe
the spin profile of a rotating sensor frame. This script is referenced
by rotate frame configuration json files. To use a spin profile object
in an experiment, the user must simply name the desired object within
the config file and give it some parameters to initialize the object.
This node will parse the configuration file and instantiate the spin
profile object, and then use the spin profile object to command the
velocity of the rotating sensor frames.
