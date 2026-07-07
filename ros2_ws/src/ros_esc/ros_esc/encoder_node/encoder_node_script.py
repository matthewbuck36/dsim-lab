#!/usr/bin/env python3

"""This node parses a joint state message for joints of interest
in order to extract angular position information correlating to
rotating sensor frames. The user must specify a list of names for
each joint of interest, the encoder node that reads the joint state message
from the input topic, and publishes the angular position (in radians) of
the desired joints of interest in a StampedFloat64MultiArray message
to the output topic.

Please note this node is setup only for use in Gazebo simulation.
"""

import argparse
import rclpy
from rclpy.node import Node
import rclpy.parameter
from sensor_msgs.msg import JointState
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray

class EncoderNode(Node):
    """This node publishes angular positions of rotating sensor frames in Gazebo simulation."""

    def __init__(self):
        super().__init__("encoder_node")

        # Tell this node to use simulation time by setting this parameter
        # This means anytime we use the command 'self._clock.now()' it returns
        # the current simulation time, rather than the current system time.
        self.set_parameters([
            rclpy.parameter.Parameter('use_sim_time',rclpy.Parameter.Type.BOOL, True)
        ])

        # For parsing the input arguments
        description_msg = "\n".join([
            "This node is used to publish angular positions of joints of interest. "
            "Upon execution, this node publishes the angular positions of rotating ",
            "sensor frames in units of radians."
        ])
        inp_joint_state_topic_msg = "\n".join([
            "Please enter the input joint state topic you want this node to subscribe to, ",
             "e.g. '/joint_states'."
        ])
        inp_timekeeping_topic_msg = "\n".join([
            "Please enter the input topic that is sending timekeeping information to reference ",
            "e.g. '/timekeeper_chatter'."
        ])
        out_topic_msg = "\n".join([
            "Please enter the output topic you want this node to publish to, ",
            "e.g. '/encoder_chatter'."
        ])
        joint_names_msg = '\n'.join([
            "Please enter the names of the joints of interest separated by spaces, ",
            "these joints must be setup with the joint state publisher in the robot's URDF file, ",
            "e.g. 'rotating_frame_joint_1' 'rotating_frame_joint_2' 'rotating_frame_joint_3'"
        ])
        parser = argparse.ArgumentParser(description=description_msg)
        parser.add_argument('input_joint_state_topic', type=str, help=inp_joint_state_topic_msg)
        parser.add_argument('input_timekeeping_topic', type=str, help=inp_timekeeping_topic_msg)
        parser.add_argument('output_topic', type=str, help=out_topic_msg)
        parser.add_argument('--joint_names', type=str, nargs="*",
                             help=joint_names_msg, dest="joint_names")
        args = parser.parse_args()

        # Initialize variables
        self.start_time = None
        self.encoder_angles = None

        # Assert that we have joint names to reference
        warn_msg = "Please enter joint names to reference using the --joint_names tag."
        assert args.joint_names is not None, warn_msg
        # Save the joint names as a list
        self.joint_names = args.joint_names

        # Create a subscriber to the input topic
        # This allows us to extract the desired joints' angular positions
        self.joint_state_subscriber = self.create_subscription(
            JointState, args.input_joint_state_topic, self.joint_state_callback, 10
        )

        # Create a subscriber to the timekeeping topic
        # This will tell give timekeeping information to reference
        self.timekeeping_subscriber = self.create_subscription(
            Timekeeper, args.input_timekeeping_topic, self.timekeeping_callback, 10
        )

        # Create a publisher to the output topic
        # This will publish the angular positions of the rotating frames
        self.encoder_publisher = self.create_publisher(
            StampedFloat64MultiArray, args.output_topic, 10
        )

    def joint_state_callback(self, msg: JointState):
        """This function collects the angular position of the desired joints."""

        # Get the list of joint names published in the JointState message
        msg_names = msg.name
        # Check that the joint names this object is tracking are in this message
        for entry in self.joint_names:
            warn_msg = "Joint "+entry+" is not found in the JointState message."
            assert entry in msg_names, warn_msg
        # Initialize a list of indicies
        indices = [msg_names.index(x) for x in self.joint_names]

        # Get the positions of the joints published in the JointState message
        msg_positions = msg.position
        # Get the positions of our desired joints
        # Note these angular positions are in radians
        self.encoder_angles = [msg_positions[x] for x in indices]

        # Publish the readings
        self.publish_encoder_reading()

    def timekeeping_callback(self, msg: Timekeeper):
        """This function collects the timekeeper information to reference."""

        # Collect the start time of the experiment to reference
        self.start_time = msg.start_time

    def publish_encoder_reading(self):
        """This function publishes the encoder readings."""

        # Ensure we have the data we need to publish
        if (self.start_time is not None) and (self.encoder_angles is not None):
            # Create the message
            msg = StampedFloat64MultiArray()
            # Create the header
            msg.header = "Encoder Values"

            # Get the current time
            t_current = self._clock.now()
            # Subtract the reference start time from simulation time
            current_sim_time = float(t_current.nanoseconds*1e-9) - self.start_time
            # Add the timestamp
            msg.timestamp = current_sim_time

            # Add the data
            msg.data = self.encoder_angles
            # Publish the message
            self.encoder_publisher.publish(msg)

def main(args=None):
    """This will initialize and launch this node."""

    rclpy.init(args=args)
    node = EncoderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()
    
