# Description:

This folder contains an examples of a robot's rotate frame config files.
Note that any configuration file can have any number of velocity controllers specified,
as long as they do not exceed the total amount of rotating frames on the vehicle. 
Note that the names of these velocity controllers must match those setup within a
robot's controller config yaml file, this is to ensure velocity commands get published
to the appropriate ROS topic that is denoted by the velocity controller's name. This spin 
profile object is used to spin the rotating sensor frames with a custom velocity profile.
