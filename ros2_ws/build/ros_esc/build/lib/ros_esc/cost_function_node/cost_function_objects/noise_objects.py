"""This script holds classes that describe noise signals.
If the user wants to add noise to their cost value signal,
one of these classes will be selected in the configuration
file. The cost function node will then instantiate the selected
object from this script and then use it to add noise to the
published cost value.

References:
https://physbam.stanford.edu/cs448x/old/Noise_Review.html
"""

from abc import ABC, abstractmethod
import random
import numpy as np
from ros_esc.config_parsing import parse_sympy_expression

# pylint: disable=too-few-public-methods
class NoiseObject(ABC):
    """ Defines function calls needed from noise objects.

    Every noise class needs to have the add noise method.
    This is the method called by the cost function node to
    operate on the input values it receives. The cost function
    node will always give the same two variables as inputs:

    time (float): current time
        (either simulation or real time)
    cost (np.ndarray): vector of cost values

    This method will output an array of altered cost values
    with additive noise.

    Class Methods:
        add_noise: gives the altered cost values with additive
        noise with call signature add_noise(time, cost)

    Note the add noise method should be the last method defined
    for the object, and it must end with this specific line of code:
    "return output". This is because this class will be parsed into
    a string for experiment documentation, and the parser is looking
    for the specific line "return output" to denote the end of the code
    describing this object.
    """

    @abstractmethod
    def add_noise(self, time, cost):
        """ Every noise object must have an add noise function.

        This add noise function must depend on time and an array
        of cost values. This method will output an array of altered
        cost values with additive noise in the following form:

        output = [altered_cost_1, altered_cost_2, ... ]
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class No_Noise(NoiseObject):
    """This class implements no noise, it is simply a placeholder in a config file."""

    def __init__(self):
        """This initializes the object."""

        # pylint: disable=unnecessary-pass
        pass

    def add_noise(self, time, cost):
        """This takes in the cost value and adds in noise."""

        # Return the unaltered cost values
        output = cost
        # Convert from array to list
        output = output.tolist()

        return output

# pylint: disable=too-few-public-methods
class Uniform(NoiseObject):
    """This class implements uniform noise with zero mean to add to a cost value."""

    def __init__(self, params):
        """This initializes the object.

        The uniform noise object should be defined in the config file as a dictionary
        named params in the following format. The bound key should contain the bounds
        on the uniform distribution. The randorm noise value generated will fall within
        the range of (- bound, + bound). The seed number key is optional, this is used
        to set the seed of the random number generator with an int. Note that if no
        seed number is given, the random seed is truly random.

        "params":{
            "bound": float,
            "seed_num": int,
        }
        """

        # Initialize the bounds on the uniform distribution
        # The noise distribution will fall within +-bound
        self.bound = params["bound"]

        # If a seed number is given
        if "seed_num" in params:
            # Initialize random with requested seed
            random.seed(params["seed_num"])
        # If no seed number is given
        else:
            # Initialize random with a random seed
            random.seed(None)

    # pylint: disable=unused-argument
    def add_noise(self, time, cost):
        """This takes in the cost value and adds in noise."""

        # Generate an array of noise with random numbers within the bounds
        noise_array = np.array([(float(random.random())-0.5)*2*self.bound for x in cost])
        # Add the noise to the cost values
        output = cost + noise_array
        # Convert from array to list
        output = output.tolist()

        return output

# pylint: disable=too-few-public-methods
class Gaussian(NoiseObject):
    """This class implements Gaussian noise with zero mean to add to a cost value."""

    def __init__(self, params):
        """This initializes the object.

        The uniform noise object should be defined in the config file as a dictionary
        named params in the following format. The standard deviation key should contain
        the standard deviation to use for this Gaussian noise distribution. The seed number
        key is optional, this is used to set the seed of the random number generator with
        an int. Note that if no seed number is given, the random seed is truly random.

        "params":{
            "std_dev": float,
            "seed_num": int,
        }
        """

        # Initialize the standard deviation
        self.std_dev = params["std_dev"]

        # If a seed number is given
        if "seed_num" in params:
            # Initialize random with requested seed
            random.seed(params["seed_num"])
        # If no seed number is given
        else:
            # Initialize random with a random seed
            random.seed(None)

    # pylint: disable=unused-argument
    def add_noise(self, time, cost):
        """This takes in the cost value and adds in noise."""

        # Generate an array of random numbers within the Gaussian distribution
        noise_array = np.array(
            [
                float(np.random.normal(
                    loc=0, scale=self.std_dev, size=None
                )) for x in cost
            ]
        )
        # Add the noise to the cost value
        output = cost + noise_array
        # Convert from array to list
        output = output.tolist()

        return output

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
class User_Defined(NoiseObject):
    """This implements a pre-defined, time varying noise signal with the input cost value."""

    def __init__(self, params):
        """This initializes the object.

        The user defined expression should be defined in the config file as a dictionary
        named params in the following format. The function key should contain the
        noise function expressed symbolically as a string. The symbols key should
        match the one shown below, all noise functions will be functions of time.
        Finally, the substitutions key is optional, this can be used to define a
        dictionary of variables that will get substituted into the main expression.
        These variables may be defined as ints or floats, or they may contain more
        expressions expressed as strings.

        "params":{
            "function": {noise_function_expressed_symbolically_as_a_string},
            "symbols": ["t"],
            "substitutions":{
                "substitution_1": float
                "substitution_2": {expression_string}
                etc...
            }
        }
        """

        # Initialize the pre-defined function
        # This pre-defined function must be a function of time
        # Create a lambda function with sympy
        # pylint: disable=unused-variable
        self.noise_function, self.noise_expression = parse_sympy_expression(params)

    def add_noise(self, time, cost):
        """This takes in the cost value and adds in noise as a function of time."""

        # Get the noise value from the function
        noise_array = self.noise_function(time)
        # Add the noise to the cost value
        output = cost + noise_array
        # Convert from array to list
        output = output.tolist()

        return output
