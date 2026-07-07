#!/usr/bin/env python3

"""The sensor pose node obtains the transformation matrices describing the
position and orientation of sensors attached to rotating sensor frames with
respect to some global reference frame. This node utilizes a forward kinematic
method to calculate the transformation matrix describing the sensor. This method
requires 'odom' data which contains position and orientation data of the vehicle's
chassis with respect to the global reference frame, the angular position values
of the rotating sensor frames, and additional information described in a sensor
transform configuration file. This additional information includes the rotating
sensor frame's rotation axis with respect to the vehicle chassis, the rotating sensor
frame joint position with respect to the vehicle chassis, and a transform matrix
specifying where the sensor is placed on the rotating frame with respect to the
rotating sensor frame joint.

Please note this node is setup only for use in Gazebo simulation.
"""

import os
import argparse
import json
import numpy as np
import rclpy
from rclpy.node import Node
import rclpy.parameter
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray, StampedTransformMultiArray
from geometry_msgs.msg import Transform
from nav_msgs.msg import Odometry
from ros_esc.config_parsing import parse_object_config

class SensorPosition(Node):
    """This class calculates the global position of sensors in Gazebo simulation."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        super().__init__("sensor_position_node")

        # Tell this node to use simulation time by setting this parameter
        # This means anytime we use the command 'self._clock.now()' it returns
        # the current simulation time, rather than the current system time.
        self.set_parameters([
            rclpy.parameter.Parameter('use_sim_time',rclpy.Parameter.Type.BOOL, True)
        ])

        # For parsing the input arguments
        description_msg = "\n".join([
            "This sensor pose node is used to calculate the transformation matrix describing ",
            "sensors attached to rotating sensor frames. This transformation matrix contains ",
            "both the position and orientation of the sensor with respect to some global ",
            "reference frame. This node utilizes a forward kinematic method to compute the ",
            "sensor's transformation matrix. The user can configure this computation with ",
            "a sensor transform configuration file which initializes a transform object. ",
            "This node always gives 'odom' data which contains the position and orientation ",
            "of the vehicle chassis w.r.t. the global reference frame, and rotating sensor ",
            "frame angular position data. The node always calls the object's ",
            "'transform_output' method expecting a transformation matrix representing the ",
            "sensor's pose w.r.t. the global frame. Note each rotating sensor frame ",
            "can have transformation object configured differently."
        ])
        inp_odom_topic_msg = "\n".join([
            "Please enter the input topic that is sending the position & orientation data ",
            "with respect to the global reference frame, e.g. '/odom'."
        ])
        inp_enc_topic_msg = "\n".join([
            "Please enter the input topic that is sending the encoder data, ",
            "e.g. '/encoder_chatter'."
        ])
        inp_timekeeping_topic_msg = "\n".join([
            "Please enter the input topic that is sending timekeeping information to reference ",
            "e.g. '/timekeeper_chatter'."
        ])
        out_topic_msg = "\n".join([
            "Please enter the output topic you want this node to publish to, ",
            "e.g. '/sensor_pose_chatter'."
        ])
        config_msg = "\n".join([
            "Please enter the filepath to a transformation config json file as a string, ",
            "this file should describe the configuration of the rotating sensor frames."
        ])
        parser = argparse.ArgumentParser(description=description_msg)
        parser.add_argument('input_odom_topic', type=str, help=inp_odom_topic_msg)
        parser.add_argument('input_enc_topic', type=str, help=inp_enc_topic_msg)
        parser.add_argument('input_timekeeping_topic', type=str, help=inp_timekeeping_topic_msg)
        parser.add_argument('output_topic', type=str, help=out_topic_msg)
        parser.add_argument('config', type=str, help=config_msg)
        args = parser.parse_args()

        # Initialize variables
        self.start_time = None
        self.odom_data = None
        self.encoder_angles = None

        # Initialize a list to hold transform objects
        self.objects_list = []

        # Expand the filepath if the ~ character is used
        config_filepath = os.path.expanduser(args.config)

        # Open the json file
        with open(config_filepath, encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)
        # Loop through the entries in the config dict
        for entry in config_dict:
            # Get the transform config dictionary
            transform_obj_dict = config_dict[entry]
            # Parse the transform configuration
            transform_obj = parse_object_config(transform_obj_dict)
            # Append to list
            self.objects_list.append(transform_obj)

        # Create a subscriber to the input odometry topic
        # This allows us to extract the vehicle pose (x, y, z, roll, pitch, yaw)
        self.pose_subscriber = self.create_subscription(
            Odometry, args.input_odom_topic, self.pose_callback, 10
        )

        # Create a subscriber to the input encoder reading topic
        # This allows us to extract the encoder readings
        self.encoder_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.input_enc_topic, self.encoder_callback, 10
        )

        # Create a subscriber to the timekeeping topic
        # This will tell give timekeeping information to reference
        self.timekeeping_subscriber = self.create_subscription(
            Timekeeper, args.input_timekeeping_topic, self.timekeeping_callback, 10
        )

        # Create a publisher
        # This will publish the transformation matrices describing
        # the sensors at the end of the rotating frames
        self.sensor_pose_publisher = self.create_publisher(
            StampedTransformMultiArray, args.output_topic, 10
        )

    def pose_callback(self, msg: Odometry):
        """This updates the transformation from the odom frame to the vehicle's footprint."""

        # Get the vehicle's position
        x_pos = msg.pose.pose.position.x
        y_pos = msg.pose.pose.position.y
        z_pos = msg.pose.pose.position.z

        # Note we have to use the quaternion angles given to us
        # by msg.pose.pose.orientation to calculate our r, p, y angles
        # For reference, see eqns (11a-c):
        # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        quat_w = msg.pose.pose.orientation.w
        quat_x = msg.pose.pose.orientation.x
        quat_y = msg.pose.pose.orientation.y
        quat_z = msg.pose.pose.orientation.z

        # Package this position and orientation data into an array
        self.odom_data = [x_pos, y_pos, z_pos, quat_w, quat_x, quat_y, quat_z]

    def encoder_callback(self, msg: StampedFloat64MultiArray):
        """This function collects the encoder readings."""

        # Collect the encoder information
        self.encoder_angles = msg.data
        # Publish our sensor position
        self.publish_sensor_position()

    def timekeeping_callback(self, msg: Timekeeper):
        """This function collects the timekeeper information to reference."""

        # Collect the start time of the experiment to reference
        self.start_time = msg.start_time

    def publish_sensor_position(self):
        """This function publishes the global (x,y,z) coordinates of the sensors as an array."""

        # Ensure we have all the data we need to publish
        # pylint: disable=line-too-long
        if (self.encoder_angles is not None) and (self.odom_data is not None) and (self.start_time is not None):
            # Initialize output list
            output_list = []

            # Loop through encoder angles, calculate the sensor pose for each frame
            for entry in enumerate(self.encoder_angles):
                # Get the index of the transformation matrix to update
                index = entry[0]
                # Get the encoder angular position reading
                angular_position = entry[1]
                # Get the transform object to use
                transform_object = self.objects_list[index]

                # Use the object to calculate the sensor's transformation matrix
                transform_matrix = transform_object.transform_output(
                    self.odom_data, angular_position
                )

                # Create a transform message
                tform_msg = Transform()
                # Extract the translation portion from the transform matrix
                tform_msg.translation.x = transform_matrix[0][3]
                tform_msg.translation.y = transform_matrix[1][3]
                tform_msg.translation.z = transform_matrix[2][3]

                # Calculate the quaternions from the transform matrix
                qw, qx, qy, qz = calculate_quaternions(transform_matrix) # pylint: disable=invalid-name
                # Assign these to the message
                tform_msg.rotation.w = qw
                tform_msg.rotation.x = qx
                tform_msg.rotation.y = qy
                tform_msg.rotation.z = qz

                # Append this to output
                output_list.append(tform_msg)

            # Construct the message
            msg = StampedTransformMultiArray()
            # Add the list of transforms
            msg.transform_array = output_list

            # Add the header information
            msg.header = "Sensor Transformation Matrices"

            # Get the publish sim time
            t_publish = self._clock.now()
            # Subtract the reference start time from simulation time
            publish_time = float(t_publish.nanoseconds*1e-9) - self.start_time
            # # Add the timestamp
            msg.timestamp = publish_time

            # Publish the message
            self.sensor_pose_publisher.publish(msg)

# pylint: disable=too-many-locals
def calculate_quaternions(transform_matrix):
    """This calculates quaternion angles from a transformation matrix.

    See https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    eqns (8 thru 9) for more information on this procedure.
    """

    # Pull data from the transform matrix
    r11 = transform_matrix[0][0]
    r12 = transform_matrix[0][1]
    r13 = transform_matrix[0][2]
    r21 = transform_matrix[1][0]
    r22 = transform_matrix[1][1]
    r23 = transform_matrix[1][2]
    r31 = transform_matrix[2][0]
    r32 = transform_matrix[2][1]
    r33 = transform_matrix[2][2]

    # Find the magnitude of each quaternion component
    mag_q0 = np.sqrt((1+r11+r22+r33)/4)
    mag_q1 = np.sqrt((1+r11-r22-r33)/4)
    mag_q2 = np.sqrt((1-r11+r22-r33)/4)
    mag_q3 = np.sqrt((1-r11-r22+r33)/4)

    # Find the largest magnitude of the above, assume its sign is positive
    largest = max(mag_q0, mag_q1, mag_q2, mag_q3)

    # pylint: disable=invalid-name
    # If mag_q0 is largest
    if largest == mag_q0:
        qw = mag_q0
        qx = (r32-r23)/(4*mag_q0)
        qy = (r13-r31)/(4*mag_q0)
        qz = (r21-r12)/(4*mag_q0)

    # If mag_q1 is largest
    elif largest == mag_q1:
        qw = (r32-r23)/(4*mag_q1)
        qx = mag_q1
        qy = (r12+r21)/(4*mag_q1)
        qz = (r13+r31)/(4*mag_q1)

    # If mag_q2 is largest
    elif largest == mag_q2:
        qw = (r13-r31)/(4*mag_q2)
        qx = (r12+r21)/(4*mag_q2)
        qy = mag_q2
        qz = (r23+r32)/(4*mag_q2)

    # If mag_q3 is largest
    else:
        qw = (r21-r12)/(4*mag_q3)
        qx = (r13+r31)/(4*mag_q3)
        qy = (r23+r32)/(4*mag_q3)
        qz = mag_q3

    return qw, qx, qy, qz # pylint: enable=invalid-name

def main(args=None):
    """This will initialize and launch the node."""

    rclpy.init(args=args)
    node = SensorPosition()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()
