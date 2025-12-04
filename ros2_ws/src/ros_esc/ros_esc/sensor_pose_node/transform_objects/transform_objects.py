"""This script holds classes that describe transform objects
for rotating sensor frames. If the user wants to use one of
these transform classes, they must specify the filepath to
this python script, and give the appropriate name to the
class they want to select in the transform configuration
file. Then within this config file, they can specify various
parameters.
"""

from abc import ABC, abstractmethod
import numpy as np

# pylint: disable=too-few-public-methods
class TransformObject(ABC):
    """Defines function calls needed from transform objects.

    Every transform class needs to have the transform output method.
    This is the method called by the sensor pose node to get a
    transformation matrix describing the sensor in the global
    coordinate frame where the cost function will be evaluated.
    The sensor pose node will always give the same two variables
    as inputs to this method:

    odom_data (np.ndarray): (7,) vector of odometry information, this
        describes the vehicle's footprint in the odometry frame
        (x, y, z, qw, qx, qy, qz)

    angular_position (float): current angular position of the rotating frame

    This method will output a 4x4 matrix that represents the transformation
    from the origin to the sensor. This will then be used as an input
    to the cost function.

    Class Methods:
        transform_output: gives the transformation matrix of the sensor
        with the call signature shown below
        transform_output(odom_data, angular_position)

    Note the transform ouput method should be the last method defined
    for the object, and it must end with this specific line of code:
    "return output". This is because this class will be parsed into
    a string for experiment documentation, and the parser is looking
    for the specific line "return output" to denote the end of the code
    describing this object.
    """

    @abstractmethod
    def transform_output(self, odom_data, angular_position):
        """ Every transform object must have a transform output function.

        This output function must depend on odometry information, and the
        rotating frame's angular position. This method will output a matrix
        representing the transform from the origion to the sensor.

        output = 4x4 transformation matrix
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Transform_Odom_To_Sensor_Pose(TransformObject):
    """This calculates the transformation matrix of a sensor based on odometry and encoder data."""

    def __init__(self, params):
        """This initializes the transform object.

        The transform odom to sensor pose object should be configured in the config
        file as a dictionary named params in the following format. The joint position
        key should be an array that describes the position of the rotating sensor frame
        joint with respect to the vehicle's 'footprint', or 'base' frame. Note that this
        'footprint' or 'base' frame is specified in the vehicle's URDF file, and can be
        thought of as the vehicle's center of mass. The rotation axis key should be an
        array containing a unit vector describing the rotation axis of the rotating sensor
        frame in the local vehicle frame. The sensor position key should be a transformation
        matrix that describes the position and orientation of the sensor with respect the the
        rotating sensor frame joint. This matrix does not change as the frame rotates,
        this is a static transform.

        "params":{
            "joint_position": np.array (3,) (one row by three columns),
            "rotation_axis": np.array (3,) (one row by three columns),
            "sensor_transform": np.array (4,4) (four rows by four columns)
        }
        """

        # Assert all inputs are arrays of the correct dimensions
        joint_position = params["joint_position"]
        warn_msg = "The joint_position must be an array of length three."
        assert np.shape(joint_position) == (3,), warn_msg

        rotation_axis = params["rotation_axis"]
        warn_msg = "The rotation_axis must be an array of length three."
        assert np.shape(rotation_axis) == (3,), warn_msg

        sensor_transform = params["sensor_transform"]
        warn_msg = "The sensor_position must be a 4x4 transformation matrix."
        assert np.shape(sensor_transform) == (4, 4), warn_msg

        # Initialize the object with the inputs
        self.joint_position = joint_position
        self.rotation_axis = rotation_axis
        self.sensor_transform = sensor_transform

    # pylint: disable=no-self-use
    def odom_transform_matrix(self, odom_data):
        """This generates the transformation matrix from odom to the vehicle 'footprint'."""

        # The odom data is an array in the form
        # odom_data = [x_pos, y_pos, z_pos, quat_w, quat_x, quat_y, quat_z]

        # Get the vehicle's position
        x_pos = odom_data[0]
        y_pos = odom_data[1]
        z_pos = odom_data[2]

        # Note we have to use the quaternion angles given to us
        # by msg.pose.pose.orientation to calculate our r, p, y angles
        # For reference, see eqns (11a-c):
        # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        quat_w = odom_data[3]
        quat_x = odom_data[4]
        quat_y = odom_data[5]
        quat_z = odom_data[6]

        # Package this position and orientation data into a homogeneous transformation matrix
        # Note this transformation matrix represents the position & orientation of the vehicle
        # in the stationary odometry frame. The rotation matrix was constructed using eqn (7b):
        # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        transform_matrix = np.array([
            [1-2*quat_y**2-2*quat_z**2, 2*quat_x*quat_y-2*quat_w*quat_z,
             2*quat_x*quat_z+2*quat_w*quat_y, x_pos],

            [2*quat_x*quat_y+2*quat_w*quat_z, 1-2*quat_x**2-2*quat_z**2,
             2*quat_y*quat_z-2*quat_w*quat_x, y_pos],

            [2*quat_x*quat_z-2*quat_w*quat_y, 2*quat_y*quat_z+2*quat_w*quat_x,
             1-2*quat_x**2-2*quat_y**2, z_pos],

            [0,0,0,1]
        ])

        return transform_matrix

    def joint_transform_matrix(self, angular_position):
        """This generates the transformation matrix from the vehicle's 'footprint' to the joint."""

        # Convert an axis angle representation to quaternions
        # For reference, see eqns (4b-e):
        # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        quat_w = np.cos(angular_position / 2)
        quat_x = self.rotation_axis[0] * np.sin(angular_position / 2)
        quat_y = self.rotation_axis[1] * np.sin(angular_position / 2)
        quat_z = self.rotation_axis[2] * np.sin(angular_position / 2)

        # Convert these quaternions to a rotation matrix,
        # combine with position information the joint position variable

        # Package this position and orientation data into a homogeneous transformation matrix
        # Note this transformation matrix represents the position & orientation of the rotating
        # sensor frame in the vehicle footprint frame. For reference, see eqn (7b):
        # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        transform_matrix = np.array([
            [1-2*quat_y**2-2*quat_z**2, 2*quat_x*quat_y-2*quat_w*quat_z,
             2*quat_x*quat_z+2*quat_w*quat_y, self.joint_position[0]],

            [2*quat_x*quat_y+2*quat_w*quat_z, 1-2*quat_x**2-2*quat_z**2,
             2*quat_y*quat_z-2*quat_w*quat_x, self.joint_position[1]],

            [2*quat_x*quat_z-2*quat_w*quat_y, 2*quat_y*quat_z+2*quat_w*quat_x,
             1-2*quat_x**2-2*quat_y**2, self.joint_position[2]],

            [0,0,0,1]
        ])

        return transform_matrix

    def transform_output(self, odom_data, angular_position):
        """This uses the forward kinematic method to get the transformation matrix of the sensor."""

        # Get the transformation matrix from odom to vehicle footprint
        odom_transform = self.odom_transform_matrix(odom_data)

        # Get the transformation matrix from vehicle footprint to joint
        joint_transform = self.joint_transform_matrix(angular_position)

        # Multiply these two transformation matrices together
        intermediate_transform = np.matmul(odom_transform, joint_transform)

        # Multiply this by the sensor transform to get the final transformation
        # matrix describint the sensor's pose in the global frame
        final_transform = np.matmul(intermediate_transform, self.sensor_transform)

        # Return the final transformation matrix describing the sensor
        output = final_transform

        return output
