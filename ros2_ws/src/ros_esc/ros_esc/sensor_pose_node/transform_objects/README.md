# Description:

This folder contains examples of transform objects for various robotic
vehicles. These scripts are referenced by the transform configuration
json file, and can contain many different transform objects. To use
a transform object in an experiment the user must simply name the desired 
transform object within the config file and give it some parameters to
initialize the object. This node will parse the configuration file,
instantiate the transform object, and then use the transform output
method to operate on input values.
