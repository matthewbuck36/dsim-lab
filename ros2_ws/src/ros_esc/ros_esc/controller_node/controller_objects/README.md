# Description:

This folder contains examples of controller objects for various robotic
vehicles. These scripts are referenced by the controller configuration
json file, and can contain many different controller objects. To use
a controller object in an experiment the user must simply name the desired 
controller object within the config file and give it some parameters to
initialize the object. This node will parse the configuration file,
instantiate the controller object, and then use the controller output
method to operate on input values.
