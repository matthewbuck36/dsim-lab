# Description

This folder contains examples of controller config files for various
controllers. Every config file must start with the absolute filepath
to the script the user wants to pull a controller object from. The user
must then give the name of that controller object, and then instantiate
it with their desired gains and parameters. The controller node will
parse this configuration file and instantiate a controller object with
the desired settings. This will then be used to operate on input values
and issue velocity commands in experimentation.

When adjusting or tuning controllers during experimentation, the user
should be changing the values in the config file. The controller objects
themselves just take care of the logic of the controller, and should not
be changed or tuned. If one needs to make a new controller with new logic,
then they should add a new controller object to the vehicle specific script.
They can then submit a merge request to add their controller to the package.