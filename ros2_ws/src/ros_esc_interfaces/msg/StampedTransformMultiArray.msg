# This message is used to broadcast transformation matrices
# which contain the global position and orientation of sensors 
# for other ROS nodes to reference.

# Header containing a description of what the data represents
string      header

# Timestamp of the message.
float64     timestamp

# Array of transformation matrices, each matrix 
# represents the information for one individual sensor.
geometry_msgs/Transform[]   transform_array