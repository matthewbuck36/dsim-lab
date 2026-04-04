"""This script holds classes that describe controllers
for the turtlebot vehicle. If the user wants to use one of
these controller classes, they must specify the filepath to
this python script, and give the appropriate name to the
class they want to select in the controller configuration
file. Then within this config file, they can specify various
gains and parameters.
"""

from abc import ABC, abstractmethod
from ros_esc.config_parsing import parse_object_config
import numpy as np

class ControllerObject(ABC): # pylint: disable=too-few-public-methods
    """ Defines function calls needed from controller objects.

    Every controller class needs to have the controller
    output method. This is the method called by the controller
    node to operate on the input values it receives. The controller
    node will always give the same three variables as inputs:

    time (float): current time
        (either simulation or real time)
    state (np.ndarray): (6,) vector of system states
        (x, y, z, roll, pitch, yaw)
    input_values (np.ndarray): a vector of input values to operate on
        (typically these come from the output of a filter)

    This method will output an array of commanded velocities in the form:
    output = [vx, vy, vz, wx, wy, wz]

    This array will then be parsed into a Twist message by the
    controller node. This Twist message will command the robot
    to move in the environment.

    Class Methods:
        controller_output: gives the output of the controller
        with call signature controller_output(time, state, input_values)

    Note the controller ouput method should be the last method defined
    for the object, and it must end with this specific line of code:
    "return output". This is because this class will be parsed into
    a string for experiment documentation, and the parser is looking
    for the specific line "return output" to denote the end of the code
    describing this object.
    """

    @abstractmethod
    def controller_output(self, time, state, input_values):
        """ Every controller must have an output function.

        This output function must depend on time, the vehicle's
        states, and input values. This method will output an
        array of commanded velocities in the following form:

        output = [vx, vy, vz, wx, wy, wz]
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
class Directional_Controller(ControllerObject):
    """This class is meant to be used with a directional filter.

    The directional filter outputs a direction where the vehicle
    can see an improvement in its measured cost value. We want to
    command the vehicle to move along this direction.
    """

    def __init__(self, gains, params):
        """This initializes the directional controller object.

        The gains input should be a dictionary with the following keys
        "gains":{
            "k_vx": float,
            "k_wz": float
        },

        The params input should be a dictionary with the following keys
        "params":{
            "wheel_radius": float,
            "wheel_distance": float,
            "wheel_max_rpm": float,
            "set_max_vx": null,
            "set_max_wz": null
        }

        The user can override the maximum forward and angular velocity
        constraints by replacing null with a float value.
        """

        # Define forward velocity gain
        self.k_vx = gains["k_vx"]
        # Define angular velocity gain
        self.k_wz = gains["k_wz"]
        # Define necessary parameters
        radius = params["wheel_radius"] # wheel radius in meters
        dist = params["wheel_distance"] # horizontal distance between wheels in meters
        max_rpm = params["wheel_max_rpm"] # maximum no load speed for the driving servo motors

        # Calculate the maximum angular velocity of the driving servos
        omega_max = max_rpm/60*2*np.pi # max angular velocity in rad/s
        # Calculate the maximum velocity constraints
        self.max_vx = omega_max*radius # maximum forward velocity
        self.max_wz = 2*omega_max*radius/dist # maximum turning velocity while turning in place

        # Override the maximum forward velocity if the user desires
        if params["set_max_vx"] is not None:
            self.max_vx = params["set_max_vx"]

        # Override the maximum angular velocity if the user desires
        if params["set_max_wz"] is not None:
            self.max_wz = params["set_max_wz"]

    def controller_output(self, time, state, input_values):
        """This operates on the input arguments and produces the controller output.

        time (float): current time
            (either simulation or real time)
        state (np.ndarray): (6,) vector of system states
            (x, y, z, roll, pitch, yaw)
        input_values (np.ndarray): a vector of input values to operate on
            (typically these come from the output of a filter)
        """

        # Linear velocity vx
        v_x = self.k_vx*input_values[0]
        # Angular velocity wz
        w_z = self.k_wz*input_values[1]

        # Make sure these commands don't go over our vehicle constraints
        if np.abs(v_x) > self.max_vx:
            v_x = float(self.max_vx*np.sign(v_x))
        if np.abs(w_z) > self.max_wz:
            w_z = float(self.max_wz*np.sign(w_z))

        # Return a list of commanded velocities
        # [vx, vy, vz, wx, wy, wz]
        output = np.array([v_x, 0, 0, 0, 0, w_z])

        return output


# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Rotating_Frame_Directional_Controller(ControllerObject):
    """This can be used with derivative estimations obtained in the vehicle relative frame.

    This class can be used for methods that collect a time history of a derivative estimation.
    Adaptive methods like RMSProp and AdaGrad ESC obtain and track the time history of derivative
    estimates in the vehicle relative frame. These must be converted via a 2D rotation matrix so
    that the derivative estimates are transformed into the absolute frame. The selected ODE can be
    used with the derivative estimates to obtain a direction of travel in the absolute frame
    where one sees improvement in their cost value. This direction must then be converted
    back into the vehicle relative frame. With this result, one can then apply their feedback
    control law to navigate along the desired direction in the relative frame.
    """

    def __init__(self, gains, dynamic_states, params):
        """This initializes the rotating frame directional controller object.

        The gains input should be a dictionary with the following keys
        "gains":{
            "k_vx": float,
            "k_wz": float
        },

        The dynamic states input should be a dictionary with the following keys
        "dynamic_states": {
            "m" : int > 0,

            "ode" : {
                "filepath" : string,
                "object_name" : string,

                    ode_object must have a method: "differential_equation"
                    with call signature: differential_equation(t, x, z, u)

                    t is a float for time
                    x is a vector of vehicle states
                    z is a vector of controller dynamic states (for choice of ODE)
                    u is a vector of input values coming from derivative estimation filter

                Include other keys used to intialize the ODE object such as:
                "omega_l" : float, low pass filter parameter
                "k" : ndarray, gains for the ode equation
                "epsilon" : float, small value in ODE equation
            },

            "initial_values": list[float]
                is a vector of initial controller dynamic states
        }

        The params input should be a dictionary with the following keys
        "params":{
            "wheel_radius": float,
            "wheel_distance": float,
            "wheel_max_rpm": float,
            "set_max_vx": null,
            "set_max_wz": null
        }

        The user can override the maximum forward and angular velocity
        constraints by replacing null with a float value.
        """

        # Initialize a vector of dynamic states
        self.num_dynamic_states = dynamic_states["m"]
        self.dynamic_states = np.zeros((self.num_dynamic_states,))

        # If given initial values for the dynamic states
        if dynamic_states["initial_values"]:
            # Initialize with user defined initial states
            self.dynamic_states = dynamic_states["initial_values"]

        # Obtain the dictionary describing the ode
        ode_dict = dynamic_states["ode"]
        # Parse this ode dictionary and return the initialized ODE object
        self.ode_object = parse_object_config(ode_dict)

        # Define a variable to track the previous timestamp
        self.prev_tstamp = None

        # Define forward velocity gain
        self.k_vx = gains["k_vx"]
        # Define angular velocity gain
        self.k_wz = gains["k_wz"]
        # Define necessary parameters
        radius = params["wheel_radius"] # wheel radius in meters
        dist = params["wheel_distance"] # horizontal distance between wheels in meters
        max_rpm = params["wheel_max_rpm"] # maximum no load speed for the driving servo motors

        # Calculate the maximum angular velocity of the driving servos
        omega_max = max_rpm/60*2*np.pi # max angular velocity in rad/s
        # Calculate the maximum velocity constraints
        self.max_vx = omega_max*radius # maximum forward velocity
        self.max_wz = 2*omega_max*radius/dist # maximum turning velocity while turning in place

        # Override the maximum forward velocity if the user desires
        if params["set_max_vx"] is not None:
            self.max_vx = params["set_max_vx"]

        # Override the maximum angular velocity if the user desires
        if params["set_max_wz"] is not None:
            self.max_wz = params["set_max_wz"]

    def update_dynamic_states(self, time, state, input_values, dt):
        """Updates controller dynamic states for choice of ODE method."""

        # Use the ODE object to operate on input information
        diff_eqn_output = self.ode_object.differential_equation(
            time, state, self.dynamic_states, input_values
        )

        # Separate the dictionary into the different parts
        theta_dot = diff_eqn_output["theta_dot"]
        z_dot = diff_eqn_output["z_dot"]

        # Update dynamic states with a forward Euler step
        self.dynamic_states += z_dot * dt

        # Update the previous timestamp
        self.prev_tstamp = time

        # Return the desired update direction in the vehicle relative frame
        return theta_dot

    def controller_output(self, time, state, input_values):
        """This operates on the input arguments and produces the controller output.

        time (float): current time
            (either simulation or real time)
        state (np.ndarray): (6,) vector of system states
            (x, y, z, roll, pitch, yaw)
        input_values (np.ndarray): a vector of input values to operate on
            (typically these come from the output of a filter)
        """

        # Calculate the change in time from previous timestamp.
        # On first callback, avoid a large startup integration jump.
        if self.prev_tstamp is None:
            dt = 0.0
        else:
            dt =  time - self.prev_tstamp
        # Update controller dynamic states,
        # obtain the update direction in the vehicle relative frame
        update_direction = self.update_dynamic_states(time, state, input_values, dt)

        # Calculate the feed back law:
        # Linear velocity vx
        v_x = self.k_vx * update_direction[0]
        # Angular velocity wz
        w_z = self.k_wz * update_direction[1]

        # Apply vehicle constraints:
        # Make sure these commands don't go over our vehicle constraints
        if np.abs(v_x) > self.max_vx:
            v_x = float(self.max_vx * np.sign(v_x))
        if np.abs(w_z) > self.max_wz:
            w_z = float(self.max_wz * np.sign(w_z))

        # Return a list of commanded velocities
        # [vx, vy, vz, wx, wy, wz]
        output = np.array([v_x, 0, 0, 0, 0, w_z])

        return output

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
class Forward_Velocity_Input_Controller(ControllerObject):
    """This class is meant to be used for forward velocity tuning.

    The controller only adjusts the forward velocity,
    the angular velocity is kept constant.
    """

    def __init__(self, gains, params):
        """This initializes the controller object.

        The gains input should be a dictionary with the following keys
        "gains":{
            "k_vx": float,
            "k_wz": float,
            "alpha": float,
            "omega": float,
        },

        The params input should be a dictionary with the following keys
        "params":{
            "wheel_radius": float,
            "wheel_distance": float,
            "wheel_max_rpm": float,
            "set_max_vx": null,
            "set_max_wz": null
        }

        The user can override the maximum forward and angular velocities
        by replacing null with a float value.
        """

        # Define forward velocity gain
        self.k_vx = gains["k_vx"]
        # Define angular velocity gain
        self.k_wz = gains["k_wz"]
        # Dither amplitude
        self.alpha = gains["alpha"]
        # Proportional gain
        self.c = gains["c_gain"]
        # Perturbation rate
        self.omega = gains["omega"]
        # Define necessary parameters
        radius = params["wheel_radius"] # wheel radius in meters
        dist = params["wheel_distance"] # horizontal distance between wheels in meters
        max_rpm = params["wheel_max_rpm"] # maximum no load speed for the driving servo motors

        # Calculate the maximum angular velocity of the driving servos
        omega_max = max_rpm/60*2*np.pi # max angular velocity in rad/s
        # Calculate the maximum velocity constraints
        self.max_vx = omega_max*radius # maximum forward velocity
        self.max_wz = 2*omega_max*radius/dist # maximum turning velocity while turning in place

        # Override the maximum forward velocity if the user desires
        if params["set_max_vx"] is not None:
            self.max_vx = params["set_max_vx"]

        # Override the maximum angular velocity if the user desires
        if params["set_max_wz"] is not None:
            self.max_wz = params["set_max_wz"]

    def controller_output(self, time, state, input_values):
        """This operates on the input arguments and produces the controller output.

        time (float): current time
            (either simulation or real time)
        state (np.ndarray): (6,) vector of system states
            (x, y, z, roll, pitch, yaw)
        input_values (np.ndarray): a vector of input values to operate on
            (typically these come from the output of a filter)
        """

        # Calculate the forward velocity
        v_x =  (
            self.omega*self.alpha*np.cos(self.omega*time) -
            self.k_vx*input_values[0]*self.c*np.sin(self.omega*time)
        )
        # Angular velocity wz
        w_z = self.k_wz

        # Make sure these commands don't go over our vehicle constraints
        if np.abs(v_x) > self.max_vx:
            v_x = float(self.max_vx*np.sign(v_x))
        if np.abs(w_z) > self.max_wz:
            w_z = float(self.max_wz*np.sign(w_z))

        # Return a list of commanded velocities
        # [vx, vy, vz, wx, wy, wz]
        output = np.array([v_x, 0, 0, 0, 0, w_z])

        return output

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Angular_Velocity_Input_Controller(ControllerObject):
    """This class is meant to be used for angular velocity tuning.

    The controller only adjusts the angular velocity,
    the forward velocity is kept constant.
    """

    def __init__(self, gains, params):
        """This initializes the controller object.

        The gains input should be a dictionary with the following keys
        "gains":{
            "k_vx": float,
            "k_wz": float,
            "alpha": float,
            "omega": float,
            "c": float,
            "d": float,
        },

        The params input should be a dictionary with the following keys
        "params":{
            "wheel_radius": float,
            "wheel_distance": float,
            "wheel_max_rpm": float,
            "set_max_vx": null,
            "set_max_wz": null
        }

        The user can override the maximum forward and angular velocities
        by replacing null with a float value.
        """

        # Define forward velocity gain
        self.k_vx = gains["k_vx"]
        # Define angular velocity gain
        self.k_wz = gains["k_wz"]
        # Dither amplitude
        self.alpha = gains["alpha"]
        # Perturbation rate
        self.omega = gains["omega"]
        self.c = gains["c"]
        self.d = gains["d"]
        # Define necessary parameters
        radius = params["wheel_radius"] # wheel radius in meters
        dist = params["wheel_distance"] # horizontal distance between wheels in meters
        max_rpm = params["wheel_max_rpm"] # maximum no load speed for the driving servo motors

        # Calculate the maximum angular velocity of the driving servos
        omega_max = max_rpm/60*2*np.pi # max angular velocity in rad/s
        # Calculate the maximum velocity constraints
        self.max_vx = omega_max*radius # maximum forward velocity
        self.max_wz = 2*omega_max*radius/dist # maximum turning velocity while turning in place


        # Override the maximum forward velocity if the user desires
        if params["set_max_vx"] is not None:
            self.max_vx = params["set_max_vx"]

        # Override the maximum angular velocity if the user desires
        if params["set_max_wz"] is not None:
            self.max_wz = params["set_max_wz"]

    def controller_output(self, time, state, input_values):
        """This operates on the input arguments and produces the controller output.

        time (float): current time
            (either simulation or real time)
        state (np.ndarray): (6,) vector of system states
            (x, y, z, roll, pitch, yaw)
        input_values (np.ndarray): a vector of input values to operate on
            (typically these come from the output of a filter)
        """

        # Forward velocity v_x
        v_x = self.k_vx
        # Calculate the angular velocity w_z
        term_1 = self.alpha * self.omega * np.cos(self.omega*time) * self.k_wz
        term_2 = (self.c - self.d * input_values[0]) * np.sin(self.omega * time) * input_values[0]
        w_z = term_1 - term_2

        # Make sure these commands don't go over our vehicle constraints
        if np.abs(v_x) > self.max_vx:
            v_x = float(self.max_vx*np.sign(v_x))
        if np.abs(w_z) > self.max_wz:
            w_z = float(self.max_wz*np.sign(w_z))

        # Return a list of commanded velocities
        # [vx, vy, vz, wx, wy, wz]
        output = np.array([v_x, 0, 0, 0, 0, w_z])

        return output

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Lie_Bracket_Controller(ControllerObject):
    """This class is meant to be used for lie bracket method.

    The controller only adjusts the angular velocity,
    the forward velocity is kept constant.
    """

    def __init__(self, gains, params):
        """This initializes the controller object.

        The gains input should be a dictionary with the following keys
        "gains":{
            "k_vx": float,
            "k_wz": float,
            "k": float,
            "omega": float,
            "mu": float
        },

        The params input should be a dictionary with the following keys
        "params":{
            "wheel_radius": float,
            "wheel_distance": float,
            "wheel_max_rpm": float,
            "set_max_vx": null,
            "set_max_wz": null
        }

        The user can override the maximum forward and angular velocities
        by replacing null with a float value.
        """

    # Define forward velocity gain
        self.k_vx = gains["k_vx"]
        # Define angular velocity gain
        self.k_wz = gains["k_wz"]
        # k gain
        self.k = gains["k"]
        # dither rate
        self.omega = gains["omega"]
        # define the washout filter gain
        self.mu = gains["mu"]

        # Define necessary parameters
        radius = params["wheel_radius"] # wheel radius in meters
        dist = params["wheel_distance"] # horizontal distance between wheels in meters
        max_rpm = params["wheel_max_rpm"] # maximum no load speed for the driving servo motors

        # Calculate the maximum angular velocity of the driving servos
        omega_max = max_rpm/60*2*np.pi # max angular velocity in rad/s
        # Calculate the maximum velocity constraints
        self.max_vx = omega_max*radius # maximum forward velocity
        self.max_wz = 2*omega_max*radius/dist # maximum turning velocity while turning in place


        # Override the maximum forward velocity if the user desires
        if params["set_max_vx"] is not None:
            self.max_vx = params["set_max_vx"]

        # Override the maximum angular velocity if the user desires
        if params["set_max_wz"] is not None:
            self.max_wz = params["set_max_wz"]

    def controller_output(self, time, state, input_values):
        """This operates on the input arguments and produces the controller output.

        time (float): current time
            (either simulation or real time)
        state (np.ndarray): (6,) vector of system states
            (x, y, z, roll, pitch, yaw)
        input_values (np.ndarray): a vector of input values to operate on
            (typically these come from the output of a filter)
        """
        # Forward velocity v_x
        v_x = self.k_vx
        # Calculate the angular velocity w_z
        w_z = self.omega + (self.omega * time) * self.k * self.mu * input_values
        # Make sure these commands don't go over our vehicle constraints
        if np.abs(v_x) > self.max_vx:
            v_x = float(self.max_vx*np.sign(v_x))
        if np.abs(w_z) > self.max_wz:
            w_z = float(self.max_wz*np.sign(w_z))

        # Return a list of commanded velocities
        # [vx, vy, vz, wx, wy, wz]
        output = np.array([v_x,0,0,0,0,w_z])

        return output

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Newton_LB_Forward_Velocity_Input_Controller(ControllerObject):
    """This class is meant to be used with a Newton ESC Forward Tuning Control filter.

    The directional filter outputs a direction where the vehicle
    can see an improvement in its measured cost value. We want to
    command the vehicle to move along this direction.
    """

    def __init__(self, gains, params):
        """This initializes the directional controller object.

        The gains input should be a dictionary with the following keys
        "gains":{
            "k_vx": float,
            "k_wz": float,
            "alpha": float,
            "omega": float,
            "p": float,
        },

        The params input should be a dictionary with the following keys
        "params":{
            "wheel_radius": float,
            "wheel_distance": float,
            "wheel_max_rpm": float,
            "set_max_vx": null,
            "set_max_wz": null
        }

        The user can override the maximum forward and angular velocities
        by replacing null with a float value.
        """

        # Define forward velocity gain
        self.k_vx = gains["k_vx"]
        # Define angular velocity gain
        self.k_wz = gains["k_wz"]
        # Dither amplitude
        alpha = gains["alpha"]
        # Perturbation rate
        self.omega = gains["omega"]
        # The power gain
        p = gains["p"]
        # Define alpha tilde from these parameters
        self.alpha_tilde = alpha*np.power(self.omega, p)
        # Define necessary parameters
        radius = params["wheel_radius"] # wheel radius in meters
        dist = params["wheel_distance"] # horizontal distance between wheels in meters
        max_rpm = params["wheel_max_rpm"] # maximum no load speed for the driving servo motors

        # Calculate the maximum angular velocity of the driving servos
        omega_max = max_rpm/60*2*np.pi # max angular velocity in rad/s
        # Calculate the maximum velocity constraints
        self.max_vx = omega_max*radius # maximum forward velocity
        self.max_wz = 2*omega_max*radius/dist # maximum turning velocity while turning in place


        # Override the maximum forward velocity if the user desires
        if params["set_max_vx"] is not None:
            self.max_vx = params["set_max_vx"]

        # Override the maximum angular velocity if the user desires
        if params["set_max_wz"] is not None:
            self.max_wz = params["set_max_wz"]

    def controller_output(self, time, state, input_values): # pylint: disable=unused-argument
        """This operates on the input arguments and produces the controller output.

        time (float): current time
            (either simulation or real time)
        state (np.ndarray): (6,) vector of system states
            (x, y, z, roll, pitch, yaw)
        input_values (np.ndarray): a vector of input values to operate on
            (typically these come from the output of a filter)
        """

        # Forward velocity vz
        v_x =  (self.alpha_tilde * np.cos(self.omega * time)
            + self.k_vx * input_values[0] * input_values[1]
        )
        # Angular velocity wz
        w_z = self.k_wz # Constant Angular elocity

        # Make sure these commands don't go over our vehicle constraints
        if np.abs(v_x) > self.max_vx:
            v_x = float(self.max_vx*np.sign(v_x))
        if np.abs(w_z) > self.max_wz:
            w_z = float(self.max_wz*np.sign(w_z))

        # Return a list of commanded velocities
        # [vx, vy, vz, wx, wy, wz]
        output = np.array([v_x, 0, 0, 0, 0, w_z])


        return output
