"""This script holds classes that describe spin profiles
for rotating sensor frames. If the user wants to use one of
these spin profile classes, they must specify the filepath to
this python script, and give the appropriate name to the
class they want to select in the rotate frame configuration
file. Then within this config file, they can specify various
parameters.
"""

from abc import ABC, abstractmethod
import numpy as np

# pylint: disable=too-few-public-methods
class SpinProfile(ABC):
    """ Defines function calls needed from spin profile objects.

    Every spin profile class needs to have the velocity
    output method. This is the method called by the rotate frame
    node to send a velocity command to the appropriate topic.
    The rotate frame node will always give the same three variables
    as inputs to this method:

    time (float): current time
        (either simulation or real time)

    angular_position (float): current angular position of the rotating frame

    spin_direction (boolean or None): current spin direction of the rotating frame
            (True for ccw rotation, False for cw rotation, None if uninitialized)

    This method will output a velocity command as a float. This will
    then be published to the appropriate ROS topic to control the velocity
    of the rotating sensor frame.

    Class Methods:
        velocity_output: gives the commanded velocity of the rotating
        sensor frame with the call signature shown below
        velocity_output(time, angular_position, spin_direction)

    Note the velocity ouput method should be the last method defined
    for the object, and it must end with this specific line of code:
    "return output". This is because this class will be parsed into
    a string for experiment documentation, and the parser is looking
    for the specific line "return output" to denote the end of the code
    describing this object.
    """

    @abstractmethod
    def velocity_output(self, time, angular_position, spin_direction):
        """ Every spin profile must have a velocity output function.

        This output function must depend on time, the rotating frame's
        angular position, and the current spin direction (True denotes
        ccw rotation, False denotes cw rotation). This method will output
        a float representing the velocity command in radians per second.

        output = float
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Constant_Full_Rotation(SpinProfile):
    """This class enables constant full rotation of the frame."""

    def __init__(self, params):
        """This initializes the spin profile object.

        The params input should be a dictionary with the following keys
        "params":{
            "spin_rpm": float
        }
        """

        # Define the rotation speed in radians per second
        self.speed = params["spin_rpm"]*(2*np.pi/60)

    def velocity_output(self, time, angular_position, spin_direction):
        """This operates on the input arguments and produces the velocity output.

        time (float): current time
            (either simulation or real time)

        angular_position (float): current angular position of the rotating frame

        spin_direction (boolean or None): current spin direction of the rotating frame
            (True for ccw rotation, False for cw rotation, None if uninitialized)
        """

        # No dependence on any input variable
        output = self.speed

        return output

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Constant_Back_And_Forth_Rotation(SpinProfile):
    """This class enables back and forth rotation of the frame.

    The frame will spin counterclockwise until its angular position is larger
    than the ccw bound specified in the parameters. This object switches the
    spin direction once the frame's position hits the bound. The frame will spin
    clockwise until its angular position is less than the cw bound specified in
    the parameters. This object switches the spin direction once the frame's
    position hits the bound.
    """

    def __init__(self, params):
        """This initializes the spin profile object.

        The params input should be a dictionary with the following keys
        "params":{
            "spin_rpm": float
            "cw_bound_deg": float
            "ccw_bound_deg": float
        }
        """

        # Define the rotation speed in radians per second
        self.speed = params["spin_rpm"]*(2*np.pi/60)
        # Assert this speed is positive
        warn_msg = "\n".join([
            "The spin_rpm must be positive in a ",
            "Constant_Back_And_Forth_Rotation spin profile."
        ])
        assert self.speed > 0, warn_msg

        # Define the clockwise bound in radians
        # If we pass this bound while spinning cw, we switch the direction to ccw
        self.cw_bound = params["cw_bound_deg"]*(np.pi/180)
        # Define the counterclockwise bound in radians
        # If we pass this bound while spinning ccw, we switch the direction to cw
        self.ccw_bound = params["ccw_bound_deg"]*(np.pi/180)

    def velocity_output(self, time, angular_position, spin_direction):
        """This operates on the input arguments and produces the velocity output.

        time (float): current time
            (either simulation or real time)

        angular_position (float): current angular position of the rotating frame

        spin_direction (boolean or None): current spin direction of the rotating frame
            (True for ccw rotation, False for cw rotation, None if uninitialized)
        """

        # If we havn't started spinning, spin_direction will be None,
        # Set the spin direction to counterclockwise
        if spin_direction is None:
            # Start spinning the frame counterclockwise
            spin_direction = True

        # Check the spin direction of the rotating frame
        # If we're traveling counterclockwise
        if spin_direction:
            # Check to ensure we are within the counterclockwise bound
            if angular_position < self.ccw_bound:
                # Set the velocity for ccw rotation
                output = self.speed
            # If we're outside the counterclockwise bound
            else:
                # Set the velocity for cw rotation
                output = self.speed * -1

        # If we're traveling clockwise
        elif not spin_direction:
            # Check to ensure we are within the clockwise bound
            if angular_position > self.cw_bound:
                # Set the velocity for cw rotation
                output = self.speed * -1
            # If we're outside the clockwise bound
            else:
                # Set the velocity for ccw rotation
                output = self.speed
        
        return output

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Two_Section_Back_And_Forth_Rotation(SpinProfile):
    """This class enables back and forth rotation of the frame.

    This class splits the spin profile into two sections:

    Section 1 - A counterclockwise spin from the position specified
    by the cw_bound to the position specified by the ccw_bound, the
    frame will be spinning at spin_rpm_section_one

    Section 2 - A clockwise spin from the position specified by the
    ccw_bound to the position specified by the cw_bound, the frame
    will be spinning at spin_rpm_section_two

    Note that the speed for section one must be positive for ccw
    rotation, the speed for section two must be negative for
    cw rotation.

    The frame will spin counterclockwise until its angular position is larger
    than the ccw bound specified in the parameters. This object switches the
    spin speed and direction once the frame's position hits the bound. The
    frame will spin clockwise until its angular position is less than the cw
    bound specified in the parameters. This object switches the spin speed and
    direction once the frame's position hits the bound.
    """

    def __init__(self, params):
        """This initializes the spin profile object.

        The params input should be a dictionary with the following keys
        "params":{
            "spin_rpm_section_one": float
            "spin_rpm_section_two": float
            "cw_bound_deg": float
            "ccw_bound_deg": float
        }
        """

        # Define the rotation speeds for each spin section, convert to radians per second
        self.velo_one = params["spin_rpm_section_one"]*(2*np.pi/60)
        self.velo_two = params["spin_rpm_section_two"]*(2*np.pi/60)

        # Assert that section one velocity is positive
        warn_msg = "\n".join([
            "The spin_rpm_section_one must be positive in a ",
            "Two_Section_Back_And_Forth_Rotation spin profile."
        ])
        assert self.velo_one > 0, warn_msg

        # Assert that section two velocity is negative
        warn_msg = "\n".join([
            "The spin_rpm_section_two must be negative in a ",
            "Two_Section_Back_And_Forth_Rotation spin profile."
        ])
        assert self.velo_two < 0, warn_msg

        # Define the clockwise bound in radians
        # If we pass this bound while spinning cw, we switch the direction to ccw
        self.cw_bound = params["cw_bound_deg"]*(np.pi/180)
        # Define the counterclockwise bound in radians
        # If we pass this bound while spinning ccw, we switch the direction to cw
        self.ccw_bound = params["ccw_bound_deg"]*(np.pi/180)

    def velocity_output(self, time, angular_position, spin_direction):
        """This operates on the input arguments and produces the velocity output.

        time (float): current time
            (either simulation or real time)

        angular_position (float): current angular position of the rotating frame

        spin_direction (boolean or None): current spin direction of the rotating frame
            (True for ccw rotation, False for cw rotation, None if uninitialized)
        """

        # If we havn't started spinning, spin_direction will be None,
        # Set the spin direction to counterclockwise
        if spin_direction is None:
            # Start spinning the frame counterclockwise
            spin_direction = True

        # Check the spin direction of the rotating frame
        # If we're traveling counterclockwise
        if spin_direction:
            # Check to ensure we are within the counterclockwise bound
            if angular_position < self.ccw_bound:
                # Set the velocity for section one's speed
                output = self.velo_one
            # If we're outside the counterclockwise bound
            else:
                # Set the velocity for section two's speed
                output = self.velo_two

        # If we're traveling clockwise
        elif not spin_direction:
            # Check to ensure we are within the clockwise bound
            if angular_position > self.cw_bound:
                # Set the velocity for section two's speed
                output = self.velo_two
            # If we're outside the clockwise bound
            else:
                # Set the velocity for section one's speed
                output = self.velo_one

        return output

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class Four_Section_Back_And_Forth_Rotation(SpinProfile):
    """This class enables back and forth rotation of the frame.

    This class splits the spin profile into four sections:

    Section 1 - A counterclockwise spin from the position specified
    by the cw_bound to the position specified by the swap_velo_bound,
    the frame will be spinning at spin_rpm_section_one

    Section 2 - A counterclockwise spin from the position specified by
    the swap_velo_bound to the position specified by the ccw_bound,
    the frame will be spinning at spin_rpm_section_two

    Section 3 - A clockwise spin from the position specified by the
    ccw_bound to the position specified by the swap_velo_bound, the
    frame will be spinning at spin_rpm_section_three

    Section 4 - A clockwise spin from the position specified by the
    swap_velo_bound to the position specified by the cw_bound, the
    frame will be spinning at spin_rpm_section_four

    Note that the speeds for sections one and two must be positive for ccw
    rotation, the speeds for sections three and four must be negative for
    cw rotation.

    The frame will spin counterclockwise until its angular position is larger
    than the ccw bound specified in the parameters. This object switches the
    spin direction once the frame's position hits the bound. The frame will
    spin clockwise until its angular position is less than the cw bound specified
    in the parameters. This object switches the spin direction once the frame's
    position hits the bound. The object only changes the speed once the frame
    rotates past the swap velo bound, it does not change the rotation direction.
    """

    def __init__(self, params):
        """This initializes the spin profile object.

        The params input should be a dictionary with the following keys
        "params":{
            "spin_rpm_section_one": float
            "spin_rpm_section_two": float
            "spin_rpm_section_three": float
            "spin_rpm_section_four": float
            "cw_bound_deg": float
            "ccw_bound_deg": float
            "swap_velo_bound_deg": float
        }
        """

        # Define the rotation speeds for each spin section, convert to radians per second
        self.velo_one = params["spin_rpm_section_one"]*(2*np.pi/60)
        self.velo_two = params["spin_rpm_section_two"]*(2*np.pi/60)
        self.velo_three = params["spin_rpm_section_three"]*(2*np.pi/60)
        self.velo_four = params["spin_rpm_section_four"]*(2*np.pi/60)


        # Assert that section one velocity is positive
        warn_msg = "\n".join([
            "The spin_rpm_section_one must be positive in a ",
            "Four_Section_Back_And_Forth_Rotation spin profile."
        ])
        assert self.velo_one > 0, warn_msg

        # Assert that section two velocity is positive
        warn_msg = "\n".join([
            "The spin_rpm_section_two must be positive in a ",
            "Four_Section_Back_And_Forth_Rotation spin profile."
        ])
        assert self.velo_two > 0, warn_msg

        # Assert that section three velocity is negative
        warn_msg = "\n".join([
            "The spin_rpm_section_three must be negative in a ",
            "Four_Section_Back_And_Forth_Rotation spin profile."
        ])
        assert self.velo_three < 0, warn_msg

        # Assert that section four velocity is negative
        warn_msg = "\n".join([
            "The spin_rpm_section_four must be negative in a ",
            "Four_Section_Back_And_Forth_Rotation spin profile."
        ])
        assert self.velo_four < 0, warn_msg

        # Define the clockwise bound in radians
        # If we pass this bound while spinning cw, we switch the direction to ccw
        self.cw_bound = params["cw_bound_deg"]*(np.pi/180)
        # Define the counterclockwise bound in radians
        # If we pass this bound while spinning ccw, we switch the direction to cw
        self.ccw_bound = params["ccw_bound_deg"]*(np.pi/180)
        # Define the swap velo bound in radians
        # If we pass this bound while spinning, we change the rotation speed
        self.swap_velo_bound = params["swap_velo_bound_deg"]*(np.pi/180)

    def velocity_output(self, time, angular_position, spin_direction):
        """This operates on the input arguments and produces the velocity output.

        time (float): current time
            (either simulation or real time)

        angular_position (float): current angular position of the rotating frame

        spin_direction (boolean or None): current spin direction of the rotating frame
            (True for ccw rotation, False for cw rotation, None if uninitialized)
        """

        # If we havn't started spinning, spin_direction will be None,
        # Set the spin direction to counterclockwise
        if spin_direction is None:
            # Start spinning the frame counterclockwise
            spin_direction = True

        # Check the spin direction of the rotating frame
        # If we're traveling counterclockwise
        if spin_direction:
            # Check if we are within spin section one
            if self.cw_bound < angular_position < self.swap_velo_bound:
                # Set the velocity to section one's speed
                output = self.velo_one
            # Check if we are within spin section two
            elif self.swap_velo_bound <= angular_position < self.ccw_bound:
                # Set the velocity to section two's speed
                output = self.velo_two
            # Check if we are outside the counterclockwise bound
            elif angular_position >= self.ccw_bound:
                # Set the velocity to section three's speed
                output = self.velo_three
            # Check if we are outside the clockwise bound (potential overshoot case)
            elif angular_position <= self.cw_bound:
                # Set the velocity to section one's speed
                output = self.velo_one

        # If we're traveling clockwise
        elif not spin_direction:
            # Check if we are within spin section three
            if self.ccw_bound > angular_position > self.swap_velo_bound:
                # Set the velocity to section three's speed
                output = self.velo_three
            # Check if we are within spin section two
            elif self.swap_velo_bound >= angular_position > self.cw_bound:
                # Set the velocity to section four's speed
                output = self.velo_four
            # Check if we are outside the clockwise bound
            elif angular_position <= self.cw_bound:
                # Set the velocity to section one's speed
                output = self.velo_one
            # Check if we are outside the counterclockwise bound (potential overshoot case)
            elif angular_position >= self.ccw_bound:
                # Set the velocity to section three's speed
                output = self.velo_three

        return output
