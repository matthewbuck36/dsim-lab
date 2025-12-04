"""This script holds classes that describe ODE objects
for use with controllers on the turtlebot vehicle. If the
user wants to use one of these ODE classes, they must specify
the filepath to this python script, and give the appropriate
name to the class they want to select in the controller
configuration file. Then within this config file, they can
specify various parameters.
"""

from abc import ABC, abstractmethod
from extremum_seeking.seekers.parameter_odes import RMSpropFlow, AdaGradFlow
import numpy as np

# pylint: disable=anomalous-backslash-in-string

class ODEObject(ABC): # pylint: disable=too-few-public-methods
    """ Defines function calls needed from ODE objects.

    Every ODE class needs to have the differential equation
    method. This is the method called by the controller
    object to operate on the input values it receives. The controller
    object will always give the same four variables as inputs:

    time (float): current time
        (either simulation or real time)
    state (np.ndarray): (6,) vector of system states
        (x, y, z, roll, pitch, yaw)
    dynamic_states (np.ndarray): a vector of dynamic states related
        to the choice of ODE
    input_values (np.ndarray): a vector of input values to operate on
        (typically the are derivative estimates in the vehicle relative
        frame coming from the output of a filter)

    This method will output a dictionary of two arrays in the form:
    theta_dot (np.ndarray): (2,) vector of the desired update direction
        converted to be in the vehicle relative frame
    z_dot (np.ndarray): a vector representing the change in dynamic
        states over time, used with a forward Euler step to update
        the dynamic states

    Class Methods:
        differential_equation: evaluates the ODE differential equation
        with call signature differential_equation(time, state,
        dynamic_states, input_values)

    Note the differential equation method should be the last method defined
    for the object, and it must end with this specific line of code:
    "return output". This is because this class will be parsed into
    a string for experiment documentation, and the parser is looking
    for the specific line "return output" to denote the end of the code
    describing this object.
    """

    @abstractmethod
    def differential_equation(self, time, state, dynamic_states, input_values):
        """Every ODE object must have an differential equation function.

        This function must depend on time, the vehicle's states, the differential
        equation dynamic states, and input values. This method will output a
        dictionary of commanded velocities in the following form:

        output = {
            "theta_dot" : np.ndarray,
            "z_dot" : np.ndarray
        }
        """

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

class RMSPropODE(ODEObject): # pylint: disable=too-few-public-methods
    """This implements the RMSProp ODE equation.

    The dynamic states for this ODE are captured in the v vector which
    describes a low pass filter estimation of the gradient squared.

    Note that derivative estimations in the vehicle relative frame
    are given as input values. These are converted via a rotation matrix
    to use with the ODE in the absolute frame. This results in a direction
    of improvement in the absolute frame, which is then converted back into
    a direction in the vehicle relative frame, to be used to issue control
    commands.
    """

    def __init__(self, omega_l, k, epsilon=0.1):
        """This initializes the RMSPropODE object.

        This RMSPropODE is setup for use with a vehicle conducting ESC
        experiments over a two dimensional (x, y) objective function

        This object requires a low pass filter parameter:
        omega_l = float
        This object requires a gain parameter:
        k = int, float, or list
        This object requires an epsilon parameter:
        epsilon = float

        This object implements the RMSProp ODE
        .. math::

            \frac{d}{dt} \hat{\theta}_i &= -\frac{k_{i}}{\sqrt{\hat{v}_i}}
            \left(\nabla J\right)_i \\
            \frac{d}{dt} \hat{v}_i &= \omega_{v,i} \left( \left(\nabla J\right)_i^2
            - \hat{v}_i \right)

        The dynamic states for this ODE relate to the v variable, this is an
        array of the gradient squared estimates across all dimensions. These
        dynamic states get updated by the controller object that calls this
        ODE object.
        """

        # Initialize the ode gains
        if isinstance(k, (int, float)):
            gains = k*np.eye(2)
        elif isinstance(k, list):
            # Convert to array
            gains = np.diag(np.array(k))

        # Initialize the parameter ODE
        self.param_ode = RMSpropFlow(gains, omega_l, epsilon)

        # Initialize a duplication matrix
        self.duplication_matrix = construct_duplication_matrix(2)

    # pylint: disable=too-many-locals
    def differential_equation(self, time, state, dynamic_states, input_values):
        """This implements the differential equation.

        Note this object expects derivative estimations as input values in the following form:
            g_relative = input_values[:2], gradient estimates in relative frame dimensions
            gop_relative = input_values[2:], gradient squared estiamtes in relative frame,
                these are collected in a half vectorization of a gradient outer product matrix

        The gradient estimates get converted via a rotation matrix to be in the absolute frame:
            g_absolute = rot_matrix @ g_relative

        Similarly for the gradient squared estimates in the gradient outer product matrix:
            gop_absolute = rot_matrix @ gop_relative @ rot_matrix.T

        We collect only the gradient squared estimates from the gop_absolute matrix
            g_squared = diag(gop_absolute)

        These estimates get used with the ODE equation

        The result theta_dot_absolute indicates a direction of improvement in the absolute
        frame, this gets converted to a direction of improvement in the relative frame:
            theta_dot_relative = rot_matrix.T @ theta_dot_absolute

        This theta_dot_relative is used to command the vehicle.
        """

        # Get the gradient estimates
        g_relative = input_values[:2]
        # Get the gradient outer product
        halfvec_gop_relative = input_values[2:]
        # Construct a rotation matrix with the vehicle state information
        rot_matrix = rotation_matrix(state)
        # Convert relative gradient estimaes to absolute frame
        g_absolute = rot_matrix @ g_relative
        # Convert half vectorization to full vectorization
        gop_relative = self.duplication_matrix @ halfvec_gop_relative
        # Convert this full vectorization into the appropriate matrix
        gop_relative = gop_relative.reshape((2, 2), order='F')
        # Convert relative gradient outer product to absolute frame
        gop_absolute = rot_matrix @ gop_relative @ rot_matrix.T
        # Keep only the diagonal terms from the gradient outer product
        g_squared = np.diag(gop_absolute)

        # Use the differential equation of the parameter ODE object
        theta_hat_dot = self.param_ode.differential_equation(
            time,
            theta_hat=np.concatenate((np.array([0,0]), dynamic_states)),
            z=np.concatenate((g_absolute, g_squared))
        )

        # Separate theta_hat_dot into components
        theta_dot_absolute = theta_hat_dot[:2]
        z_dot = theta_hat_dot[2:]

        # Convert the update direction into the relative frame
        theta_dot_relative = rot_matrix.T @ theta_dot_absolute

        # Combine results into a dictionary
        output = {
            "theta_dot" : theta_dot_relative,
            "z_dot" : z_dot
        }

        # Return the output dictionary
        return output

class AdaGradODE(ODEObject): # pylint: disable=too-few-public-methods
    """This implements the AdaGrad ODE equation.

    The dynamic states for this ODE are captured in the gamma vector which
    describes a low pass filter estimation of some inverse power of the
    gradient outer product matrix.

    Note that derivative estimations in the vehicle relative frame
    are given as input values. These are converted via a rotation matrix
    to use with the ODE in the absolute frame. This results in a direction
    of improvement in the absolute frame, which is then converted back into
    a direction in the vehicle relative frame, to be used to issue control
    commands.
    """

    def __init__(self, omega_l, k, power, epsilon=0.1):
        """This initializes the AdaGradODE object.

        This AdaGradODE is setup for use with a vehicle conducting ESC
        experiments over a two dimensional (x, y) objective function

        This object requires a low pass filter parameter:
        omega_l = float
        This object requires a gain parameter:
        k = int, float, or list
        This object requires a power parameter:
        power = int
        This object requires an epsilon parameter:
        epsilon = float

        This object implements the AdaGrad ODE
        .. math::

            & \frac{d}{dt} \hat{\theta} = -k \hat{\Gamma} \nabla J
            \\
            & \sum_{i=0}^{q-1} (\hat{\Gamma})^i(\frac{d}{dt}\hat{\Gamma})
            (\hat{\Gamma})^{q-1-i}
            =
            \omega_l ((\hat{\Gamma})^q -
            (\hat{\Gamma})^q (\hat{\nabla J}^T \hat{\nabla J}) (\hat{\Gamma})^q)

        The dynamic states for this ODE relate to the gamma variable, this is an
        array of the half vectorization of some inverse power of the gradient
        outer product matrix. These dynamic states get updated by the controller
        object that calls this ODE object.
        """

        # Initialize the ode gains
        if isinstance(k, (int, float)):
            gains = k*np.eye(2)
        elif isinstance(k, list):
            # Convert to array
            gains = np.diag(np.array(k))

        # Initialize the parameter ODE
        self.param_ode = AdaGradFlow(gains, omega_l, power, epsilon)

        # Construct duplication and elimination matrices
        self.duplication_matrix = construct_duplication_matrix(2)
        self.elimination_matrix = construct_elimination_matrix(2)

    # pylint: disable=too-many-locals
    def differential_equation(self, time, state, dynamic_states, input_values):
        """This implements the differential equation.

        Note this object expects derivative estimations as input values in the following form:
            g_relative = input_values[:2], gradient estimates in relative frame dimensions
            gop_relative = input_values[2:], gradient squared estiamtes in relative frame,
                these are collected in a half vectorization of a gradient outer product matrix

        The gradient estimates get converted via a rotation matrix to be in the absolute frame:
            g_absolute = rot_matrix @ g_relative

        Similarly for the gradient squared estimates in the gradient outer product matrix:
            gop_absolute = rot_matrix @ gop_relative @ rot_matrix.T

        These estimates get used with the ODE equation

        The result theta_dot_absolute indicates a direction of improvement in the absolute
        frame, this gets converted to a direction of improvement in the relative frame:
            theta_dot_relative = rot_matrix.T @ theta_dot_absolute

        This theta_dot_relative is used to command the vehicle.
        """

        # Get the gradient estimates
        g_relative = input_values[:2]
        # Get the gradient outer product
        halfvec_gop_relative = input_values[2:]
        # Construct a rotation matrix with the vehicle state information
        rot_matrix = rotation_matrix(state)
        # Convert relative gradient estimaes to absolute frame
        g_absolute = rot_matrix @ g_relative
        # Convert half vectorization to full vectorization
        gop_relative = self.duplication_matrix @ halfvec_gop_relative
        # Convert this full vectorization into the appropriate matrix
        gop_relative = gop_relative.reshape((2, 2), order='F')
        # Convert relative gradient outer product to absolute frame
        gop_absolute = rot_matrix @ gop_relative @ rot_matrix.T
        # Reduce the relative gradient outer product matrix to a half vectorization
        halfvec_gop_absolute = self.elimination_matrix @ gop_absolute.flatten('F')

        # Use the differential equation of the parameter ODE object
        theta_hat_dot = self.param_ode.differential_equation(
            time,
            theta_hat=np.concatenate((np.array([0,0]), dynamic_states)),
            z=np.concatenate((g_absolute, halfvec_gop_absolute))
        )

        # Separate theta_hat_dot into components
        theta_dot_absolute = theta_hat_dot[:2]
        z_dot = theta_hat_dot[2:]

        # Convert the update direction into the relative frame
        theta_dot_relative = rot_matrix.T @ theta_dot_absolute

        # Combine results into a dictionary
        output = {
            "theta_dot" : theta_dot_relative,
            "z_dot" : z_dot
        }

        # Return the output dictionary
        return output


### Helper Functions
def rotation_matrix(state):
    """This creates a 2D rotation matrix based off of the vehicle's heading."""

    # Obtain the heading or yaw angle from the state vector
    heading = state[-1]
    # Define the 2D rotation matrix
    rot_matrix = np.array([
        [np.cos(heading), -np.sin(heading)],
        [np.sin(heading), np.cos(heading)]
    ])

    return rot_matrix

# pylint: disable=invalid-name
def construct_duplication_matrix(n):
    """Constructs a duplication matrix for a n by n symmetric matrix."""

    # Construct the duplication matrix via the following equation
    # D_n = \sum_{i \geq j} (u_{ij} vec(T_{ij})^T)

    # Initialize the duplication matrix transposed
    duplication_matrix = np.zeros((int(n*(n+1)/2), int(n**2)))

    # Loop over all j
    for j in range(n):
        # Define i >= j
        i = j
        # Loop over all i
        while i < n:
            # Construct unit vector u
            u = np.zeros(int(n*(n+1)/2))
            # Put a one in appropriate index
            index = int(j*n + i - j*(j+1)/2)
            u[index] = 1
            # Convert to column vector
            u = np.asmatrix(u).T

            # Construct T matrix
            t = np.zeros((n, n))
            # Place ones in appropriate indices
            t[i, j] = 1
            t[j, i] = 1
            # Vectorize the T matrix
            t_vec = np.asmatrix(t.flatten('F'))

            # Update the duplication matrix via the following equation
            # D_n = \sum_{i \geq j} (u_{ij} vec(T_{ij})^T)
            duplication_matrix += u @ t_vec

            # Increment i
            i += 1

    # Transpose the duplication matrix
    duplication_matrix = duplication_matrix.T

    return duplication_matrix

def construct_elimination_matrix(n):
    """Constructs an elimination matrix for a n by n symmetric matrix."""

    # Construct the elimination matrix L_n based off of the size of A
    # Initialize with zeros
    elimination_matrix = np.zeros((int((n*(n+1))/2), int(n**2)))

    # Construct the elimination matrix via the following equation
    # L_n = \sum_{i \geq j} (u_{ij} \otimes e_{j}^{T} \otimes e_{i}^{T})

    # Loop over all j
    for j in range(n):
        # Create the column vector e_j where it is already transposed
        e_j = np.zeros(n)
        # Add a one to the jth index
        e_j[j] = 1

        # Initialize i >= j
        i = j
        # Loop over all i
        while i < n:
            # Define vector u
            u = np.zeros(int(n*(n+1)/2))
            # Put a one in the appropriate position
            index = int(j*n + i-(j*(j+1))/2)
            u[index] = 1
            # Convert u to a column vector
            u = np.asmatrix(u).T

            # Create the column unit vector e_i where it is already transposed
            e_i = np.zeros(n)
            # Add a one to the ith index
            e_i[i] = 1

            # Update the elimination matrix with the following equation
            # L_n = \sum_{i \geq j} (u_{ij} \otimes e_{j}^{T} \otimes e_{i}^{T})
            elimination_matrix += np.kron(u, np.kron(e_j, e_i))

            # Increment i
            i += 1

    return elimination_matrix
