#!/bin/user/python3
# -* coding:utf-8 *-

r"""
File: PARAMETER_ODES.PY

Author: Patrick McNamee

Date: May 30th, 2024

Brief:
    Handles the parameter update equations.

"""

from abc import ABC, abstractmethod
from extremum_seeking.filters import LowPassRicattiFilter
import numpy as np


class ParameterUpdateODE(ABC):
    """ Defines how to call parameter update ODEs and their arguments """

    @property
    def idim(self):
        """ Dimension of inputs to the system """
        return self.__idim

    @idim.setter
    def idim(self, val):
        assert isinstance(val, int), "Only integer dimensions are allowed."
        assert val > 0, "Dimensions must be a strictly positive integer."
        self.__idim = val

    @property
    def ndim(self):
        """ Number of dimensions of the internal states of the system. """
        return self.__ndim

    @ndim.setter
    def ndim(self, val):
        assert isinstance(val, int), "Only integer dimensions are allowed."
        assert val > 0, "Dimensions must be a strictly positive integer."
        self.__ndim = val

    @property
    def odim(self):
        """ Dimensions of the system output """
        return self.__odim

    @odim.setter
    def odim(self, val):
        assert isinstance(val, int), "Only integer dimensions are allowed."
        assert val > 0, "Dimensions must be a strictly positive integer."
        self.__odim = val

    @abstractmethod
    def initialize_system(self, *args, **kargs):
        """ Initialize state vector given individual components """
        return NotImplemented

    @abstractmethod
    def differential_equation(self, t, theta, z, *args):
        """ Differential equation for updating the parameters

        Args:
            t (float) : Time
            theta (np.ndarray) : Parameters of the seeker.
            z (np.ndarray) : Various derivative estimates of the signal.
        """
        return NotImplemented

    @abstractmethod
    def system_output(self, theta_hat):
        """ Output of the system

        Args:
            theta_hat (np.ndarray): All parameters of the seeker,
                                    including the hidden ones.

        Returns:
            theta_hat_output (np.ndarray): Parameters that go into
                                           the controller.
        """
        return NotImplemented

    @abstractmethod
    def parse_history(self, theta_hat_h):
        """
        Args:
            theta_hat_h (np.ndarray): (N, ndim) array of time history
                                      over N points.

        Returns:
            theta_parsed_h: Tuple of individual histories of states
                            where first is parameter that go into
                            the controller.
        """
        return NotImplemented


class GradientFlow(ParameterUpdateODE):
    r""" Gradient Descent Algorithm

    .. math::

        \frac{d}{dt}\hat{\theta} = -k \nabla J

    """

    def __init__(self, k):
        """
        Args:
            k (float) : gain value
        """

        # Check for the dimensions of the parameter space
        if isinstance(k, float) or isinstance(k, int):
            self.ndim = 1
        elif isinstance(k, np.ndarray):
            assert np.ndim(k) == 2, "Gain must be a square matrix"
            assert np.shape(k)[0] == np.shape(k)[1], (
                "Gain must be a square matrix"
            )
            self.ndim = k.shape[0]
        else:
            raise ValueError(f"Gains of type {type(k)} not supported.")

        self.idim = self.ndim
        self.odim = self.ndim

        self.__k = k

    def initialize_system(self, theta_hat, **kargs):
        return theta_hat

    def differential_equation(self, t, theta_hat, z, *args):
        """
        Args:
            t (float) : Time in the simulation.
            theta_hat (np.ndarray): Estimates of optimal parameters of the
              controller
            z (np.ndarray): Estimates of the derivatives (Gradient) of the
              field.
            args: Other arguments
        """
        # pylint: disable=unused-argument
        if isinstance(z, np.ndarray) and isinstance(self.__k, np.ndarray):
            # Gain is a matrix
            return -self.__k @ z
        else:
            # Gain is a scalar
            return -self.__k*z

    def system_output(self, theta_hat):
        return theta_hat

    def parse_history(self, theta_hat_h):
        return (theta_hat_h,)

"""
Accelerated Methods
"""


class HeavyBallFlow(ParameterUpdateODE):
    r""" Heavy Ball i.e. stable 2nd order ODE

    .. math::

        \frac{d^2}{dt^2}\hat{\theta}
        + \beta \left(\frac{d}{dt}\hat{\theta}\right)
        + k\nabla J = 0

    This computationally calculated using the system of equations

    .. math::

        \frac{d}{dt} \begin{bmatrix} \hat{\theta} \\
        \frac{d}{dt}\hat{\theta} \end{bmatrix} = \begin{bmatrix}
        \frac{d}{dt}\hat{\theta} \\ -\beta \left(\frac{d}{dt}\hat{\theta}
        \right) - k \nabla J \end{bmatrix}

    """

    def __init__(self, k, b):
        """
        Args:
            k (float or np.ndarray) : Gain value
            b (float or np.ndarray) : Dampening coefficient
        """
        self.__k = k
        self.__b = b
        if isinstance(self.__k, float) or isinstance(self.__k, int):
            self.ndim = 2
        elif isinstance(self.__k, np.ndarray):
            assert np.ndim(k) == 2, (
                "Gain coefficient must be a square matrix."
            )
            assert np.shape(k)[0] == np.shape(k)[1], (
                "Gain coefficient must be a square matrix."
            )
            if np.ndim(b):
                assert np.ndim(b) == 2, (
                    "Dampening coefficient must be a matrix if not a scalar."
                )
                assert np.shape(b)[0] == np.shape(b)[1], (
                    "Dampening coefficient must be a square matrix."
                )
            else:
                self.__b = b*np.eye(np.shape(k)[0])
            self.ndim = 2*self.__k.shape[0]
        else:
            raise ValueError(f"Gains of type {type(k)} not supported.")

        self.idim = self.ndim//2
        self.odim = self.ndim//2

    def initialize_system(self, theta_hat, theta_hat_dot, **kargs):
        return np.hstack((theta_hat, theta_hat_dot))

    def differential_equation(self, t, theta_hat, z, *args):
        theta_hat_dot = theta_hat[self.ndim//2:]
        if isinstance(z, np.ndarray) and isinstance(self.__k, np.ndarray):
            theta_hat_dotdot = -self.__b @ theta_hat_dot - self.__k @ z
        else:
            theta_hat_dotdot = -self.__b * theta_hat_dot - self.__k * z
        return np.hstack((theta_hat_dot, theta_hat_dotdot))

    def system_output(self, theta_hat_vec):
        return theta_hat_vec[:self.ndim//2]

    def parse_history(self, theta_hat_h):
        return (theta_hat_h[:, :self.ndim//2], theta_hat_h[:, self.ndim//2:])


class AcceleratedGradientFlow(ParameterUpdateODE):
    r""" Accelerated Gradient Methods

    .. math::

        \frac{d^2}{dt^2}\hat{\theta}
        + \frac{r}{t + t_0} \frac{d}{dt}\hat{\theta}
        + k\nabla J = 0

    This computationally calculated using the system of equations

    .. math::

        \frac{d}{dt} \begin{bmatrix} \hat{\theta} \\
        \frac{d}{dt}\hat{\theta} \end{bmatrix} = \begin{bmatrix}
        \frac{d}{dt}\hat{\theta} \\ -\frac{r}{t + t_0}
        \left(\frac{d}{dt}\hat{\theta}\right) - k \nabla J \end{bmatrix}

    Method Types:
        - Accelerated Gradient Method (AGM): :math:`r \in [0,\infty),\ t_0 > 0`
        - Optimized Gradient Method Gradient based (OGM-G):
            :math:`r = -3,\ t_0 = -T < 0`

    """

    def __init__(self, k, r=3., t0=1e-2):
        self.__r = r
        self.__t0 = t0
        self.__k = k

        if isinstance(self.__k, (float, int)):
            self.ndim = 2
        elif isinstance(self.__k, np.ndarray):
            self.ndim = 2*self.__k.shape[0]
        else:
            raise ValueError(f"Gains of type {type(k)} not supported.")

        self.idim = self.ndim//2
        self.odim = self.ndim//2

    def initialize_system(self, theta_hat, theta_hat_dot, **kargs):
        return np.hstack((theta_hat, theta_hat_dot))

    def differential_equation(self, t, theta_hat, z):
        theta_hat_dot = theta_hat[self.ndim//2:]
        if isinstance(z, np.ndarray) and isinstance(self.__k, np.ndarray):
            theta_hat_dotdot = (
                -(self.__r/(t + self.__t0)) * theta_hat_dot
                - self.__k @ z
            )
        else:
            theta_hat_dotdot = (
                -self.__r/(t + self.__t0) * theta_hat_dot
                - self.__k * z
            )
        return np.hstack((theta_hat_dot, theta_hat_dotdot))

    def system_output(self, theta_hat_vec):
        return theta_hat_vec[:self.ndim//2]

    def parse_history(self, theta_hat_h):
        return (
            theta_hat_h[:, :self.ndim//2],
            theta_hat_h[:, self.ndim//2:]
        )

"""
Adaptive Methods
"""

class RMSpropFlow(ParameterUpdateODE):
    r""" RMSprop Optimizer

    The RMSprop Optimizer with a distinction from traditional discrete-time
    based optimizers. THe distinction is that we have two seperate inputs
    for the gradient and the gradient squared terms. This is due to the fact
    that this package is for model-free extremum seeking control, where the
    estimation of these quantities are seperate.

    .. math::

        \frac{d}{dt} \hat{\theta}_i &= -\frac{k_{i}}{\sqrt{\hat{v}_i}}
        \left(\nabla J\right)_i \\
        \frac{d}{dt} \hat{v}_i &= \omega_{v,i} \left( \left(\nabla J\right)_i^2
        - \hat{v}_i \right)

    """

    def __init__(self, k, omega_l, epsilon=1e-1):

        # Check for a valid dimension based on the gain
        if isinstance(k, float) or isinstance(k, int):
            self.idim = 2
        elif isinstance(k, np.ndarray):
            if k.ndim == 2:
                # Check to make sure it is strictly diagonal square matrix
                assert k.shape[0] is k.shape[1], (
                    "Gains must be a square matrix."
                )
                assert np.allclose(k, np.diag(np.diag(k))), (
                    "Gain matrices must be a strictly diagonal matrix."
                )
            elif k.ndim > 2:
                raise ValueError(
                    "Gains must be a scalar (0D), vector (1D), or a "
                    "square matrix (2d). Recieved a {}D array.".format(k.ndim)
                )
            self.idim = 2*k.shape[0]
        else:
            raise ValueError(f"Gains of type {type(k)} not supported.")

        # Reshape diagonal matrices to vectors for faster math.
        if np.ndim(k) == 2:
            k = np.diag(k)

        # Check to make sure low pass filter fits the states
        if isinstance(omega_l, float) or isinstance(omega_l, int):
            pass
        elif isinstance(omega_l, np.ndarray):
            assert omega_l.ndim == 1, (
                "Filter gains must be a (N,) array if not a scalar."
            )
            assert omega_l.size == self.idim, (
                "Filter gains must match input size."
            )
        else:
            raise ValueError("Filter gains of type {} not supported.".format(
                str(type(omega_l))
            ))

        # Check positivies
        assert np.all(k > 0), (
            "Gains must be either a strictly positive scalar, vector of "
            "strictly positive reals, or a positive definite matrix."
        )
        assert np.all(omega_l > 0), "Filter gains must all be positive."

        # Assignments
        self.__omega_l = omega_l
        self.__k = k
        self.__epsilon = epsilon
        self.ndim = self.idim
        self.odim = self.idim//2

    def initialize_system(self, theta_hat, v_hat):
        x0 = np.zeros((self.ndim,))
        x0[:self.idim] = theta_hat
        x0[self.idim:] = v_hat
        return x0

    def differential_equation(self, t, theta_hat, z):

        # Preallocate
        theta_hat_dot = np.zeros((self.ndim,))

        # Get the various estimates
        g = z[:(self.idim//2)]
        g2 = z[(self.idim//2):]

        # Get the estimates of the gradient squared
        v_hat_i = theta_hat[self.ndim//2:]

        # Apply parameter portion of ODE
        theta_hat_dot[:self.ndim//2] = (
            -self.__k*g/(np.sqrt(np.abs(v_hat_i)) + self.__epsilon)
        )
        theta_hat_dot[self.ndim//2:] = self.__omega_l*(g2 - v_hat_i)

        return theta_hat_dot

    def system_output(self, theta_hat_vec):
        return theta_hat_vec[:self.odim]

    def parse_history(self, theta_hat_h):
        return (
            theta_hat_h[:, :self.ndim//2],
            theta_hat_h[:, self.ndim//2:]
        )

class AdaGradFlow(ParameterUpdateODE):
    r"""AdaGrad Flow

    Adaptive Gradient Method commonly referred to as AdaGrad. This version is
    slightly different from the discrete version as 1) we use an exponential
    moving average for the gradient outer product and 2) we do not assume that
    the gradient can directly give the gradient outer product. The second
    difference is the more notable distinction as one would normally assume that
    :math:`\nabla J` would be sufficient to determine 
    :math:`\nabal J \nabla J^T`. However, this package is written for model-free
    extremum seeking control and thus the estimation for the gradient and
    gradient outer product are handeled seperately and treated as two distinct
    inputs rather than just a single input.

    The unique elements of the gradient outer product estimate are tracked via a
    half vectorization operator (:math:`\text{vech}(\hat{\Gamma})`). To convert this
    array containing only the unique terms to a full vectorization, use the duplication
    matrix :math:`D_n` with :math:`\text{vec}(\hat{\Gamma}) = D_n \text{vech}(\hat{\Gamma})`
    This allows one to utilize the differential eqaution seen below.

    .. math::

        & \frac{d}{dt} \hat{\theta} = -k \hat{\Gamma} \nabla J
        \\
        & \sum_{i=0}^{q-1} (\hat{\Gamma})^i(\frac{d}{dt}\hat{\Gamma})
        (\hat{\Gamma})^{q-1-i}
        =
        \omega_l ((\hat{\Gamma})^q -
        (\hat{\Gamma})^q (\hat{\nabla J}^T \hat{\nabla J}) (\hat{\Gamma})^q)

    Once results are obtained from this differential equation, the full vectorization
    is converted back into a half vectoriation using an elimination matrix :math:`L_n`
    such that :math:`\text{vech}(\hat{\Gamma}) = L_n \text{vec}(\hat{\Gamma})`.
    """

    def __init__(self, k, omega_l, power, epsilon=1e-1):
        """This initializes the filter with gains and parameters.

        The user may select the inverse gradient outer product power term
        q from the equation above to use with this object by inputting an
        integer in for the power keyword argument above.
        """

        # Check for a valid dimension based on the gain
        if isinstance(k, (float, int)):
            self.idim = 2
        elif isinstance(k, np.ndarray):
            if k.ndim == 2:
                # Check to make sure it is strictly diagonal square matrix
                assert k.shape[0] is k.shape[1], (
                    "Gains must be a square matrix."
                )
                assert np.allclose(k, np.diag(np.diag(k))), (
                    "Gain matrices must be a strictly diagonal matrix."
                )
            elif k.ndim > 2:
                raise ValueError(
                    "Gains must be a scalar (0D), vector (1D), or a ",
                    f"square matrix (2d). Recieved a {str(k.ndim)}D array."
                )
            self.idim = k.shape[0]
            self.idim = int(self.idim + self.idim*(self.idim + 1) / 2)
        else:
            raise ValueError(f"Gains of type {type(k)} not supported.")

        # Check to make sure low pass filter fits the states
        if isinstance(omega_l, (float, int)):
            pass
        else:
            raise ValueError(
                f"Filter gains of type {str(type(omega_l))} not supported."
            )

        # Check positivies
        if np.ndim(k) == 0:
            assert k > 0, "Scalar gains must be strictly positive."
        elif np.ndim(k) == 1:
            assert np.all(k > 0), "Vector gains must be positive."
        elif np.ndim(k) == 2:
            assert np.all(np.diag(k) > 0), (
                "All diagonal elements of gains must be positive."
            )
        
        assert np.all(omega_l > 0), "Filter gain must be positive."
        assert power > 0, (
            "Inverse gradient outer product power 'p' must be positive."
        )

        # Ensure inverse power is an integer
        assert isinstance(power, int), (
            "Inverse gradient outer product power 'p' must be an integer."
        )

        # Assignments
        self.ndim = self.idim
        self.odim = k.shape[0] if np.ndim(k) else 1
        self.__omega_l = omega_l
        self.__k = k
        self.__power = power
        self.__epsilon_vector = epsilon*np.eye(self.odim).flatten('F')

        # Initialize duplication and elimination matrices
        self.duplication_matrix = self.__construct_duplication_matrix()
        self.elimination_matrix = self.__construct_elimination_matrix()
        
    def initialize_system(self, theta_hat, gamma_hat):
        """ This initializes the filter states with inital values for theta and 
        gamma.
        """

        # We initialize this system with an array of size n + n(n+1)/2
        x0 = np.zeros((self.ndim,)) # pylint: disable=invalid-name

        # Ensure that theta_hat is the appropriate size
        assert theta_hat.size == self.odim, (
            "Theta hat initialization must must match output size: "
            +str(self.odim) + "."
        )
        # The first n number of terms are used to track the theta_hat portion
        x0[:self.odim] = theta_hat

        # Ensure that gamma_hat is the appropriate size
        assert gamma_hat.size == self.idim - self.odim, (
            "Gamma hat initialization must match output size: "
            +str(self.idim - self.odim) + "."
        )
        # The last n(n+1)/2 terms are used to track the gamma_hat portion
        x0[self.odim:] = gamma_hat

        # Return the initialized state vector
        return x0

    def __construct_duplication_matrix(self):
        """Constructs a duplication matrix for a n by n symmetric matrix."""

        # Initialize the size n
        n = self.odim

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
    
    def __construct_elimination_matrix(self):
        """Constructs an elimination matrix for a n by n symmetric matrix."""

        # Initialize the size n
        n = self.odim

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

    def differential_equation(self, t, theta_hat, z):
        """This computes the differential equation of the system."""

        # Preallocate
        theta_hat_dot = np.zeros((self.ndim,))

        # The first n number of terms in z are used for the gradient
        g = z[:self.odim] # pylint: disable=invalid-name
        
        # The last n(n+1)/2 number of terms in z are used to track
        # the estimate of the gradient outer product matrix.
        # Convert from the unique terms to full vectoriazation
        gop_estimate_vec = self.duplication_matrix @ z[self.odim:]
        # Note we add the flattened epsilon times the identity matrix
        # vector here to ensure this is full rank
        gop_estimate_vec += self.__epsilon_vector
        # Convert into a column vector with numpy matrix
        gop_estimate_vec = np.matrix(gop_estimate_vec).T

        # Get the filter state related to the gradient outer product
        gamma_i_vec = theta_hat[self.odim:]
        # Convert from the unique terms to full vectorization
        gamma_i_fullvec = self.duplication_matrix @ gamma_i_vec
        # Construct the symmetric gamma matrix by reshaping the vector form
        gamma_i = gamma_i_fullvec.reshape((self.odim, self.odim), order='F')

        # Apply parameter portion of ODE
        # Update with the theta dot differential equation
        theta_hat_dot[:self.odim] = (
            -self.__k * gamma_i @ g.T
        )

        # Initialize a matrix to track the summation of kronecker products
        sum_matrix = np.zeros((self.odim**2, self.odim**2))
        for i in range(self.__power):
            sum_matrix += np.kron(
                np.linalg.matrix_power(gamma_i, self.__power - 1 - i),
                np.linalg.matrix_power(gamma_i, i)
            )
            
        # Invert the summation matrix
        inv_kron_sum = np.linalg.inv(sum_matrix)

        # Update with the gamma dot differential equation
        # Calculate the following matrix result before applying filter parameter
        gamma_power = np.linalg.matrix_power(gamma_i, self.__power)
        matrix_result = inv_kron_sum @ (
            gamma_power.reshape((self.odim**2, 1)) - (
                np.kron(
                    gamma_power,
                    gamma_power
                )
                @ (gop_estimate_vec)
            )
        )

        # Apply the low pass filter parameter
        gamma_dot = self.__omega_l*matrix_result
        # Convert result into a form with only unique terms
        gamma_dot = self.elimination_matrix @ gamma_dot
        # Update the theta hat dot parameter
        theta_hat_dot[self.odim:] = gamma_dot.T

        return theta_hat_dot

    def system_output(self, theta_hat_vec):
        return theta_hat_vec[:self.odim]

    def parse_history(self, theta_hat_h):
        return (
            theta_hat_h[:, :self.odim],
            theta_hat_h[:, self.odim:]
        )

"""
Second Order Methods
"""
class NewtonFlow(ParameterUpdateODE):
    r""" Newton Flow

    Spatial second order method involving the Hessian of the cost function.
    Updates the estimate of the optimal parameters :math:`\hat{\theta}` using
    the gradient :math:`\nabla J` and an estimate of the inverse Hessian
    :math:`\hat{\Gamma}`. To achieve this we use the following differential
    equations

    .. math:

        \frac{d}{dt} \hat{\theta} &= -k\hat{\Gamma} \nabla J \\          
        \frac{d}{dt} \hat{\Gamma} &= \omega_{l}\left( \hat{\Gamma}
        - \hat{\Gamma} \nabla^2 J \hat{\Gamma} \right)

    where scalars :math:`k` and :math:`\omega_{l}` are the gain and filter rate.
    We are estimating the inverse Hessian based on the low pass inverse Ricatti
    equation.

    """

    def __init__(self, k, omega_l, odim):

        # Check that gain and filter rate are acceptable.
        assert not np.ndim(k), "Gain k must be a scalar"
        assert k > 0., "Gain k must be strictly positive"
        assert not np.ndim(omega_l), "Filter rate omega must be a scalar."
        assert omega_l > 0., "Filter rate omega must be strictly positive."

        # Assign the variables
        self.__k = k

        # Set dimensions
        total_dimensions = odim*(1 + odim)
        self.odim = odim
        self.idim = total_dimensions
        self.ndim = total_dimensions

        self.__inverse_hessian_filter = LowPassRicattiFilter(
            omega_l, ndim=self.odim
        )

    def initialize_system(self, theta_hat, Gamma_hat):

        # Sanitize
        assert np.ndim(theta_hat) in [0, 1], (
            "Parameter estimate must be a scalar or a vector."
        )
        assert np.ndim(Gamma_hat) in [0, 1, 2], (
            " Inverse Hessian estimate must either be a scalar, matrix or a "
            "flattened matrix."
        )

        if np.ndim(Gamma_hat) == 2:
            Gamma_hat = Gamma_hat.flatten()

        assert np.size(theta_hat) is self.odim, (
            "Parameter vector has {:d} elements".format(theta_hat.size) +
            " and not the required {:d}.".format(self.odim)
        )
        assert np.size(Gamma_hat) is (self.ndim - self.odim), (
            "Inverse Hessian estimate has {:d} elements and not the ".format(
                np.size(Gamma_hat)
            ) +
            "required {:d}".format(self.ndim - self.odim)
        )

        if np.size(Gamma_hat) > 1:
            assert (
                np.all(
                    Gamma_hat.reshape(
                        (self.odim, self.odim), order='F'
                    ).flatten() == Gamma_hat
                )
            ), "Inverse Hessian must correspond to a symmetric matrix."

        # Construct initialization vector and return said vector.
        x0 = np.zeros((self.ndim,))
        x0[:self.odim] = theta_hat
        x0[self.odim:] = Gamma_hat

        return x0

    def differential_equation(self, t, theta, z):

        # Preallocate
        theta_dot = np.zeros((self.ndim,))

        # Get required information for parameter ODE
        g = z[:self.odim]  # Gradient estimate
        Gamma_hat = (  # pylint: disable=invalid-name
            theta[self.odim:].reshape((self.odim, self.odim))
        )

        theta_dot[:self.odim] = -self.__k * Gamma_hat @ g
        theta_dot[self.odim:] = (
            self.__inverse_hessian_filter.differential_equation(
                t, theta[self.odim:], z[self.odim:]
            )
        )

        return theta_dot

    def system_output(self, theta_hat_vec):
        return theta_hat_vec[:self.odim]

    def parse_history(self, theta_hat_h):

        n = theta_hat_h.shape[0]  # Number of data points

        theta_h = theta_hat_h[:, :self.odim]
        Gamma_h = (  # pylint: disable=invalid-name
            theta_hat_h[:, self.odim:].reshape((n, self.odim, self.odim))
        )

        return theta_h, Gamma_h
