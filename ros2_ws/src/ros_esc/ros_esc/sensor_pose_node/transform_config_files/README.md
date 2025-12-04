# Description:

This folder contains an examples of a robot's transform configuration json files.
Note that any configuration file can have any number of frames specified,
however, they must all contain a key for the joint position (from the 
vehicle's footprint frame to the revolute joint), the rotation axis (i.e. the axis the
sensor frame piece rotate about), and the sensor transform (where the user specifies the
transformation matrix from the rotating sensor piece frame to the sensor's position on the
frame).
