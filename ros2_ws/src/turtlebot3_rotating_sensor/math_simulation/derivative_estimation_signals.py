"""This script holds pre-made derivative estimation signals
for use in math simulations. The estimation signals seen here
are all functions of angular position signals that describe
the rotation of the sensor frame.
"""

import numpy as np
from abc import ABC, abstractmethod
from sensor_perturbation_signals import AngularPositionSignal

class DerivativeEstimationSignal(ABC): # pylint: disable=too-few-public-methods
    """Defines function calls needed from derivative estiamtion signal objects.

    Every derivative estimation signal class needs to have the estimation
    output method. This is the method called to compute the various derivative
    estimations needed for a custom filter. This method will output a vector of
    all necessary derivative estimations needed for the user's choice of angular
    position signal and extremum seeking scheme.

    Class Methods:
        estimation_output: gives an array of the various derivative estimates
        with call signature estimation_output(time)
    """

    @abstractmethod
    def estimation_output(self, time):
        """Every derivative estimation signal class must have an output function.

        This output function must depend on time. This method will output
        the derivative estimations needed for the user's choice of angular
        position signal and extremum seeking method.

        output = np.ndarray
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

class ConstantFullRotationEstimation(DerivativeEstimationSignal):
    """This class is contains derivative and derivative squared estimation signals
    corresponding to constant full rotation of the sensor frame.
    """

    def __init__(self, params):
        """This initializes the object
        
        The params dictionary should be defined in the following from
        "params":{
            "angular_position_signal_object": AngularPositionSignal,
            "frame_arm_length": float
        }
        """

        # Make assertions
        assert "angular_position_signal_object" in params, (
            "This class requires an angular_position_signal_object key."
        )
        assert isinstance(params["angular_position_signal_object"], AngularPositionSignal), (
            "This class requires an AngularPositionSignal object."
        )
        assert "frame_arm_length" in params, (
            "A frame arm length must be initialized with this class."
        )
        assert isinstance(params["frame_arm_length"], (float, int)), (
            "The frame arm length must be a float or an int."
        )

        # Initialize values
        self.angular_position_signal_object = params["angular_position_signal_object"]
        self.frame_arm_length = params["frame_arm_length"]
    
    def estimation_output(self, time):
        """This calculates derivative and derivative squared estimates as a function of time."""

        # Get the current angular position
        angular_pos = self.angular_position_signal_object.angular_position_output(time)
        
        # Calculate the derivative estimations
        m_x = 2 / self.frame_arm_length * np.cos(angular_pos)
        m_y = 2 / self.frame_arm_length * np.sin(angular_pos)

        # Calculate the derivative squared estimations
        m_x_squared = (1/self.frame_arm_length**2)*(3 - 4 * (np.sin(angular_pos))**2)
        m_x_times_m_y = (1/self.frame_arm_length**2)*(2 * np.sin(2*angular_pos))
        m_y_squared = (1/self.frame_arm_length**2)*(4 * (np.sin(angular_pos))**2 - 1)

        # Combine into an output array
        output = np.array([m_x, m_y, m_x_squared, m_x_times_m_y, m_y_squared])

        return output
    
class ConstantBnFRotationEstimation(DerivativeEstimationSignal):
    """This class is contains derivative and derivative squared estimation signals
    corresponding to constant back and forth rotation of the sensor frame with set
    bounds: cw_bound = -90, ccw_bound = 90 degrees.
    """

    def __init__(self, params):
        """This initializes the object
        
        The params dictionary should be defined in the following from
        "params":{
            "angular_position_signal_object": AngularPositionSignal,
            "frame_arm_length": float
        }
        """

        # Make assertions
        assert "angular_position_signal_object" in params, (
            "This class requires an angular_position_signal_object key."
        )
        assert isinstance(params["angular_position_signal_object"], AngularPositionSignal), (
            "This class requires an AngularPositionSignal object."
        )
        assert "frame_arm_length" in params, (
            "A frame arm length must be initialized with this class."
        )
        assert isinstance(params["frame_arm_length"], (float, int)), (
            "The frame arm length must be a float or an int."
        )

        # Initialize values
        self.angular_position_signal_object = params["angular_position_signal_object"]
        self.frame_arm_length = params["frame_arm_length"]
    
    def estimation_output(self, time):
        """This calculates derivative and derivative squared estimates as a function of time."""

        # Get the current angular position
        angular_pos = self.angular_position_signal_object.angular_position_output(time)
        
        # Calculate the derivative estimations
        m_x = 2 / self.frame_arm_length * (
            (np.pi**2 / (np.pi**2 - 8)) * np.cos(angular_pos) - 2 / (np.pi**2 - 8)
        )
        m_y = 2 / self.frame_arm_length * np.sin(angular_pos)

        # Initialize a coefficient matrix
        coeff = np.array([
            [117.293, 0, -17.970],
            [0, 4.351, 0],
            [-17.970, 0, 5.42]
        ])
        # Initialize a matrix of signals
        signals = np.array([
            (np.cos(angular_pos))**2 - 4/np.pi*(np.cos(angular_pos)) + 4/(np.pi**2),
            np.sin(2*angular_pos) - 4/np.pi*np.sin(angular_pos),
            (np.sin(angular_pos))**2
        ])

        # Calculate the derivative squared estimations
        gradient_squared_vector = (1/self.frame_arm_length)**2 * coeff @ signals.T
        m_x_squared = gradient_squared_vector[0]
        m_x_times_m_y = gradient_squared_vector[1]
        m_y_squared = gradient_squared_vector[2]

        # Combine into an output array
        output = np.array([m_x, m_y, m_x_squared, m_x_times_m_y, m_y_squared])

        return output
