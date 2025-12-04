"""This script holds pre-made control functions
for use in math simulations."""

import numpy as np
from abc import ABC, abstractmethod

class ControlFunction(ABC): # pylint: disable=too-few-public-methods
    """Defines function calls needed from control function objects.

    Every control function class needs to have the controller output method.
    This is the method called to give velocity commands to the vehicle.

    time (float): current time
        (either simulation or real time)
    state (np.ndarray): (3,) vector of system states
        (x, y, yaw)
    input_values (np.ndarray): a vector of input values to operate on
        (typically these come from the output of a filter)

    This method will output an array of commanded velocities in the form:
    output = [vx, wz]

    Class Methods:
        controller_output: gives the current angular position
        with call signature controller_output(time, states, filter_output)
    """

    @abstractmethod
    def controller_output(self, time, states, filter_output):
        """Every angular position signal must have an output function.

        This output function must depend on time, the vehicle's states,
        and the filter output. This method will return the commanded
        velocities vx and wz in units m/s and rad/s respectively.

        output = [vx, wz]
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

class DirectionalController(ControlFunction):
    """This controller is used with a directional filter."""

    def __init__(self, params):
        """This initializes the object.
        
        The params dictionary should be defined in the following from
        "params":{
            "k_vx": float,
            "k_wz": float,
            "wheel_radius": float,
            "wheel_distance": float,
            "wheel_max_rpm": float,
            "set_max_vx": null,
            "set_max_wz": null
        }

        The user can override the maximum forward and angular velocity
        constraints by replacing null with a float value.
        """

        # Make assertions
        assert "k_vx" in params, "Controller must be initialized with forward velocity gain."
        assert "k_wz" in params, "Controller must be initialized with angular velocity gain."
        assert "wheel_radius" in params, "Controller must be initialized with a wheel radius."
        assert "wheel_distance" in params, (
            "Controller must be initialized with a distance between the vehicle wheels."
        )
        assert "wheel_max_rpm" in params, "Controller must be initialized with a max wheel rpm."
        assert "set_max_vx" in params, "Controller must be initialized with max vx constraint key."
        assert "set_max_wz" in params, "Controller must be initialized with max wz constraint key."

        assert isinstance(params["k_vx"], (float, int)), "Gain k_vx must be a float or int."
        assert isinstance(params["k_wz"], (float, int)), "Gain k_wz must be a float or int."
        assert isinstance(params["wheel_radius"], (float, int)), (
            "Wheel radius must be a float or int."
        )
        assert isinstance(params["wheel_distance"], (float, int)), (
            "Wheel distance must be a float or int."
        )
        assert isinstance(params["wheel_max_rpm"], (float, int)), (
            "Wheel max rpm must be a float or int."
        )

        # Calculate the default max vx and max wz constraints from given information
        omega_max = params["wheel_max_rpm"] / 60 * 2 * np.pi
        max_vx = omega_max * params["wheel_radius"]
        max_wz = omega_max * params["wheel_radius"] / params["wheel_distance"]

        # If we want to override default constraints
        if params["set_max_vx"] is not None:
            assert isinstance(params["set_max_vx"], (float, int)), (
                "Max vx constraint must be a float or int."
            )
            # Override the max forward velocity
            max_vx = params["set_max_vx"]

        if params["set_max_wz"] is not None:
            assert isinstance(params["set_max_wz"], (float, int)), (
                "Max wz constraint must be a float or int."
            )
            # Override the max angular velocity
            max_wz = params["set_max_wz"]

        # Save the variables
        self.k_vx = params["k_vx"]
        self.k_wz = params["k_wz"]
        self.max_vx = max_vx
        self.max_wz = max_wz

    def controller_output(self, time, states, filter_output):
        """This commands a velocity based on the filter output."""
    
        # Command for linear velocity
        command_vx = self.k_vx * filter_output[0]
        # Command for angular velocity
        command_wz = self.k_wz * filter_output[1]

        # Make sure these commands don't go over our vehicle constraints
        if np.abs(command_vx) > self.max_vx:
            command_vx = self.max_vx * np.sign(command_vx)
        if np.abs(command_wz) > self.max_wz:
            command_wz = self.max_wz * np.sign(command_wz)

        # Form output array
        output = np.array([command_vx, command_wz])

        return output
