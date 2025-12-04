"""This script holds pre-made rotating sensor frame angular
position signals for use in math simulations. The perturbation
signals are functions of these angular position signals, they
physically represent the relative (x, y) position of the rotating
sensor with respect to the vehicle's center (x_c, y_c). With this
information, one can calculate the global position (x_s, y_s) and
orientation of the sensor to use when computing a cost value.
"""

import numpy as np
from abc import ABC, abstractmethod

class AngularPositionSignal(ABC): # pylint: disable=too-few-public-methods
    """Defines function calls needed from angular position signal objects.

    Every angular position signal class needs to have the angular position
    output method. This is the method called to compute the current angular
    position of the rotating sensor frame as a function of time. This method
    will output the current angular position of the rotating sensor frame
    in units of radians.

    Class Methods:
        angular_position_output: gives the current angular position
        with call signature angular_position_output(time)
    """

    @abstractmethod
    def angular_position_output(self, time):
        """ Every angular position signal must have an output function.

        This output function must depend on time. This method will output
        the angular position of the rotating sensor frame in radians.

        output = float
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

class ConstantFullRotation(AngularPositionSignal):
    """This class corresponds to constant full rotation of the sensor frame."""

    def __init__(self, params):
        """This initializes the object
        
        The params dictionary should be defined in the following form
        "params":{
            "spin_rpm": float
        }
        """

        # Make assertions
        assert "spin_rpm" in params, "A spin rpm must be initialized with this object."
        # Assert it is a float or int
        assert isinstance(params["spin_rpm"], (float, int)), (
            "The spin rpm must be a float or an int."
        )

        # Initialize value
        spin_rpm = params["spin_rpm"]

        # Calculate the period of the rotation
        self.period = 1 / (spin_rpm / 60) # period in seconds

        # Calculate the rotation speed in radians per second
        self.omega = spin_rpm / 60 * 2 * np.pi
    
    def angular_position_output(self, time):
        """This returns the angular position of the rotating sensor frame as a function of time."""

        # Calculate the angular position of the rotating sensor frame
        output = self.omega * (time % self.period)

        return output
    
class ConstantBnFRotation(AngularPositionSignal):
    """This class corresponds to constant back and forth rotation of the sensor frame.
    
    Note the rotating sensor frame will start from an angular position at the clockwise
    bound. It then spins counterclockwise until it arrives at the angular position described
    by the counterclockwise bound. Afterwards, it changes its spin direction to now rotate
    clockwise until it arrives at the angular position described by the clockwise bound.
    The spin direction changes to be counterclockwise again and the process repeats.
    Note these bounds must be specified in degrees in the dictionary.
    """

    def __init__(self, params):
        """This initializes the object
        
        The params dictionary should be defined in the following form
        
        "params":{
            "spin_rpm": float,
            "cw_bound": float,
            "ccw_bound": float
        }
        """

        # Make assertions
        assert "spin_rpm" in params, "A spin rpm must be initialized with this object."
        assert "cw_bound" in params, "A clockwise bound must be initialized with this object."
        assert "ccw_bound" in params, "A counterclockwise bound must be initialized with this object."
        # Assert values are a float or int
        assert isinstance(params["spin_rpm"], (float, int)), (
            "The spin rpm must be a float or an int."
        )
        assert isinstance(params["cw_bound"], (float, int)), (
            "The clockwise bound must be a float or an int."
        )
        assert isinstance(params["ccw_bound"], (float, int)), (
            "The counterclockwise bound must be a float or an int."
        )

        # Initialize values
        spin_rpm = params["spin_rpm"]
        cw_bound = params["cw_bound"] * np.pi/180
        ccw_bound = params["ccw_bound"] * np.pi/180

        # Convert the given angles to be in the range of 0 to 2*pi
        cw_bound = cw_bound % (2 * np.pi)
        ccw_bound = ccw_bound % (2 * np.pi)

        # Calculate the size of the arc traveled in one period
        if cw_bound > ccw_bound:
            radians_traveled_per_period = 2 * (ccw_bound + 2 * np.pi - cw_bound)
        else:
            radians_traveled_per_period = 2 * (ccw_bound - cw_bound)

        # Calculate the rotation speed in radians per second
        self.omega = spin_rpm / 60 * 2 * np.pi

        # Calculate the period of the rotation
        self.period = radians_traveled_per_period / self.omega # period in seconds

        # Save the bounds
        self.cw_bound = cw_bound
        self.ccw_bound = ccw_bound
    
    def angular_position_output(self, time):
        """This returns the angular position of the rotating sensor frame as a function of time."""

        # For the counterclockwise portion
        if (time % self.period) < (self.period / 2):
            output = self.cw_bound + self.omega * (time % self.period)

        # For the clockwise portion
        else:
            output = self.ccw_bound - self.omega*((time % self.period) - self.period / 2)

        return output

def sensor_transform(time, state_vector, angularpositionsignal_obj, frame_arm_length):
    """This function calculates the transformation matrix of the sensor.
    
    Note the perturbation signals are:
    m_1 = (1 / frame_arm_length) * cos(angular_pos)
    m_2 = (1 / frame_arm_length) * sin(angular_pos)
    """

    # Get the current global position of the vehicle's center
    x_c = state_vector[0]
    y_c = state_vector[1]
    # Define the current heading angle in radians
    theta = state_vector[2]

    # Get the current angular position of the sensor
    angular_pos = angularpositionsignal_obj.angular_position_output(time)

    # Use our perturbation signals to obtain our sensor's position
    # w.r.t. the vehicle's center not accounting for the vehicle's heading
    relative_position = np.asarray([
        frame_arm_length * np.cos(angular_pos),
        frame_arm_length * np.sin(angular_pos)
    ])

    # Define a 2D rotation matrix based on the vehicle's heading
    r = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    # Calculate the relative (x, y) position of the sensor w.r.t.
    # the vehicle's center now accounting for the vehicle's heading angle
    pos_vec = r @ relative_position.T

    # Add this to the vehicle's position to get the global sensor position
    x_s = x_c + pos_vec[0]
    y_s = y_c + pos_vec[1]

    # Create the transformation matrix that describes
    # the position and orientation of the sensor in the global frame
    transform = np.array([
        [np.cos(theta + angular_pos), -np.sin(theta + angular_pos), 0, x_s],
        [np.sin(theta + angular_pos), np.cos(theta + angular_pos), 0, y_s],
        [0,0,0,0],
        [0,0,0,1]
    ])

    return transform
