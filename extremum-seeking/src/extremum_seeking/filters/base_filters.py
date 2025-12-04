#!/bin/user/python3
# -* coding:utf-8 *-

r"""
Author: Patrick McNamee

File: BASELINE_FILTERS.PY

Date: May 30, 2024

Brief:
    Handles all of the basic filters that are used as builing blocks for the
    derivative estimation filters.
"""


from abc import ABC, abstractmethod
import numpy as np
from typing import Callable


def _dimensional_check(val):
    """ Check to see if recieved a valid dimension number. 
    
    Dimensions are used to indicate the size of the input, internal states, and
    outputs that each of the filters require. Normally all dimensions are
    strictly positive integers however there are two special cases of
    exceptions: `0` and a tuple. A `0` indicates that there are no inputs/states
    required. A tuple of integers indicates that there are multiple possible
    dimensional values.
    
    """
    if isinstance(val, int):
        assert val >= 0, "Dimensions must be a positive integer."
    elif isinstance(val, tuple):
        for d in val:
            assert isinstance(d, int), "Only integer dimensions are allowed."
            assert d >= 0, "Dimensions must be a positive integer."
    else:
        raise ValueError(
            "Dimension must either be a positive integer"
            + " or tuple of positive integers."
        )

def _gain_positivity_check(val):
    """ Check to see if the filter gain(s) are (all) strictly positive.
    """

    if isinstance(val, np.ndarray):
        for v in val:
            assert v > 0., "All filter gains must be positive."
    elif isinstance(val, float):
        assert v > 0., "Filter gain must be positive."
    else:
        raise ValueError("Filter gains are either vectors or scalars.")

def value_based_filter(cls_or_obj):
    """ Indicates filter takes J """

    if isinstance(cls_or_obj, type):
        # Modifying class definition
        
        # Construct getters
        def is_value_based(*_):
            return True
        
        def is_derivative_based(*_):
            return False
        
        # Set the properties
        setattr(cls_or_obj, "is_value_based", property(fget=is_value_based))
        setattr(
            cls_or_obj,
            "is_derivative_based",
            property(fget=is_derivative_based)
        )
        
        return cls_or_obj
    
    else:
        # Modifying an object's attributes

        setattr(cls_or_obj, "is_value_based", True)
        setattr(cls_or_obj, "is_derivative_based", True)
        

def derivative_based_filter(cls_or_obj):
    r""" Indicates filter takes \frac{d}{dt}J """

    if isinstance(cls_or_obj, type):
        # Modifying a class definition

        # Construct getters
        def is_value_based(*_):
            return False

        def is_derivative_based(*_):
            return True

        # Set the properties
        setattr(cls_or_obj, "is_value_based", property(fget=is_value_based))
        setattr(
            cls_or_obj,
            "is_derivative_based",
            property(fget=is_derivative_based)
        )
        
        return cls_or_obj

    else:

        setattr(cls_or_obj, "is_derivative_based", True)
        setattr(cls_or_obj, "is_value_based", False)

    
class Filter(ABC):
    """ Defines function calls needed from filters but not their arguments 
    
    Class Properties:
        idim (int): Number of inputs to the filter
        ndim (int): Number of interal states in the filter
        odim (int): Number of output states from the filter
    
    Class Methods:
        differential_equation: ODE with call signature f(t, z, y)
        filter_output: Output from filter with signature h(z, y, t)
    
    """

    @property
    def idim(self):
        """ Dimensional of input to the filter """
        return self.__idim

    @idim.setter
    def idim(self, val):
        _dimensional_check(val)
        self.__idim = val
    
    @property
    def ndim(self):
        """ Number of internal states in the filter """
        return self.__ndim

    @ndim.setter
    def ndim(self, val):
        _dimensional_check(val)
        self.__ndim = val

    @property
    def odim(self):
        """ Number of output states from the filter """
        return self.__odim

    @odim.setter
    def odim(self, val):
        _dimensional_check(val)
        self.__odim = val
        
    @abstractmethod
    def differential_equation(self, *args, **kargs):
        """ Differential Equation """
        return NotImplemented

    @abstractmethod
    def filter_output(self, *args, **kargs):
        """ Output of the filter """
        return NotImplemented

    def valid_state(self, val):
        """ Determine if filter state is valid. """
        return np.all(np.isfinite(val))


"""
Simple Linear Filters
"""

class _LinearFilter(Filter):
    r""" Linear Filter
    
    This class is to handle the setup of linear filters: low pass, high pass,
    and washout filters. The common similarity is how they handle the
    dimensionalities of the filter. The filters can be any of the following:
    
    * Single Input Single Output (SISO)
    * Single Input Multiple Output (SIMO)
    * Multiple Input Multiple Output (MIMO)
    
    Each of the filters initialization has a parameter (or variation of) `omega`
    and the option of specifying `ndim`. If `omega` is a vector, then the size
    of `omega` determines `ndim` and `odim` although `idim` can either be `1`
    or the same dimension as `omega`. Otherwise, `omega` is a scalar value and
    the dimenions are all set by specifying `ndim`.
    """

    def __init__(self, omega, ndim):
        if np.ndim(omega):
            # If multiple gains
            self.ndim = omega.size
            self.odim = self.ndim
            self.idim = (1, self.ndim)
        elif ndim > 1:
            # Gains from ndim
            self.idim = ndim
            self.ndim = ndim
            self.odim = ndim
        else:
            # Default SISO
            self.idim = ndim
            self.ndim = ndim
            self.odim = ndim

@value_based_filter
class LowPassFilter(_LinearFilter):
    r""" Low Pass Filter

    .. math::
    
        z = \left[\frac{1}{s + \omega_l}\right](y)

    """
    
    def __init__(self, omega_l, ndim=1):
        # Assignment
        super().__init__(omega_l, ndim)
        self.__omega_l = omega_l
            
        
    def differential_equation(self, _, z, y):
        return self.__omega_l*(y - z)
    
    def filter_output(self, z, *args):
        # pylint: disable=unused-argument
        return z


@derivative_based_filter
class HighPassFilter(_LinearFilter):
    r""" High Pass Filter
    
    .. math::
    
        z = \left[\frac{s}{s + \omega_h}\right](y)
    
    """
    def __init__(self, omega_h, ndim=1):
        super().__init__(omega_h, ndim)
        self.__omega_h = omega_h
        
    def differential_equation(self, _, z, ydot):
        return ydot - self.__omega_h*z

    def filter_output(self, z, *args):
        # pylint: disable=unused-argument
        return z
    

@value_based_filter
class WashoutFilter(_LinearFilter):
    r""" Washout Filter
    
    Essentially a high pass filter implemented with a low
    pass filter.::
    
         y  +---------------------------------+ y - z    
        --->+ \frac{d}{dt} z = \omega (y - z) +-------> 
            +---------------------------------+         
                                                          
                                                          
    """
    def __init__(self, omega, ndim=1):
        super().__init__(omega, ndim)
        self.__omega = omega

    def differential_equation(self, _, z, y):
        zdot = self.__omega*(y - z)
        return zdot
    
    def filter_output(self, z, y, *args):
        return y - z

    
"""
Nonlinear Filters
"""

@value_based_filter
class LowPassRicattiFilter(Filter):
    r""" Low Pass Ricatti Based Inverse Filter for Matrices

    Used for the low pass filter of a symmetric inverse matrix. Let 
    :math:`Y \in \mathbb{S}_{++}^{n\times n}` be a positive definite symmetric
    matrix estimated by a low pass filter version :math:`X`. If  :math:`XZ = I`,
    then
    
    .. math:: 
    
        \frac{d}{dt} Z = \omega_{l} \left(Z - ZYZ \right) 
    
    This matrix differential transformed into a vector differential equation by 
    using a Kronecker product.
    
    .. math::
    
        \frac{d}{dt} \text{vec}(Z) = \omega_{l} \left(\text{vec}(Z)
        - (Z \otimes Z) \text{vec}(Y)\right)
    
    """
    # pylint: disable=invalid-name
    
    def __init__(self, omega_l, ndim):

        # Checks
        assert not np.ndim(omega_l), "Filter gain must be a scalar."
        assert omega_l > 0., "Filter gain must be positive."

        # Get the number of elements in square matrix
        ndim2 = ndim*ndim
        
        # Assignments
        self._shape_dim = ndim  # Value for reshaping into a matrix
        self.idim = ndim2  # Expects a square matrix
        self.ndim = ndim2  # Simulating a square matrix
        self.odim = ndim2  # Output is a square matrix
        self.__omega_l = omega_l  # Filter gain
        
    def __scalar_differential_equation(self, _, z, y):
        return self.__omega_l*(z - z*y*z)
        
    def __matrix_differential_equation(self, _, z, y):
        """ Matrix version of the differential equation """

        # There is no good way to handle vectorization, hence
        Z = z.reshape((self._shape_dim, self._shape_dim), order='F')
        Zvec = z.reshape(z.shape + (1,))
        
        if np.ndim(y):
            Yvec = y.reshape(y.shape + (1,))
        else:
            Yvec = y.reshape((1, 1))

        Zvec_dot = self.__omega_l*(Zvec - np.kron(Z, Z) @ Yvec)
        return Zvec_dot.flatten('F')

    def differential_equation(self, t, z, y):
        if self._shape_dim == 1:
            return self.__scalar_differential_equation(t, z, y)
        else:
            return self.__matrix_differential_equation(t, z, y)

    def filter_output(self, z, *args, matrix_form=False):
        # pylint: disable=unused-argument
        if matrix_form:
            return z.reshape(
                z.shape[:-2] + (self._shape_dim, self._shape_dim),
                order='F'
            )
        else:
            return z

    def valid_state(self, state):
        if np.all(np.isfinite(state)):
            if self._shape_dim == 1:
                return np.all(state > 0)
            else:
                return np.all(
                    np.linalg.eigvals(
                        state.reshape(self._shape_dim, self._shape_dim)
                    ) > 0
                )
        else:
            return False

"""
Functional Filters
"""

@value_based_filter
class ConvolutionFilter(Filter):
    r"""
    
    ::
    
                                                                                
          y   /-\   z                                                           
        ---->| X |---->                                                         
              \-/                                                               
               ^                                                                
               |                                                                
               | f(t)                                                           
                                                                                
    
    """

    def __init__(self, f, odim=None):

        self.f = f
        self.ndim = 0
        if odim and not hasattr(self, "_Filter__odim"):
            self.odim = odim
            self.idim = (1, odim)
        elif not hasattr(self, "_Filter__odim"):
            self.odim = 1
            self.idim = 1

    @property
    def f(self):
        return self.__f

    @f.setter
    def f(self, val):
        # Check value
        assert isinstance(val, Callable), "f is a callable function f(t)."

        # Assign necessary internal properties
        odim = np.size(val(0))
        if odim > 1:
            self.odim = odim
            self.idim = (1, odim)
        self.__f = val

    def differential_equation(self, t, z, y):  # pylint: disable=unused-argument
        return np.empty(0)
    
    def filter_output(self, _, y, t):
        return y*self.__f(t)


@value_based_filter
class FunctionFilter(Filter):
    r"""
    
    ::
    
                                                                                
          y  +------+  z                                                        
        ---->+ f(y) +---->                                                      
             +------+                                                           
                                                                                
    """

    def __init__(self, f, idim, odim):

        if isinstance(f, Callable):
            self.__f = f
        elif isinstance(f, str):
            if f.startswith("lambda y"):
                self.__f = eval(f)  # convert strings to lambda functions
            else:
                raise ValueError("String must be a lambda function on y.")

        else:
            raise ValueError(
                "Function f is not recognized as a function"
                + "or lambda function as a string."
            )

        self.idim = idim
        self.ndim = 0
        self.odim = odim

    def differential_equation(self, t, z, y):  # pylint: disable=unused-argument
        return np.empty(0)
    
    def filter_output(self, z, y, t):  # pylint: disable=unused-argument
        return self.__f(y)


"""
Optimization Directions:
    Modifies an optimization ODE to output a direction.
"""
@value_based_filter
class DirectionalFilter(Filter):
    """ Filter that outputs a direction rather than derivative.

    Simple wrapper class to allow for a `ParameterUpdateODE` to become a filter.
    The main reason behind this is that the parameter systems update the
    parameters based on a direction that "should" improve the cost function.
    For vehicles with kinematic constraints, we could like to know this
    direction and then attempt to move along this direction.
    """

    def __init__(self, g):

        self.idim = g.idim
        self.odim = g.odim
        self.ndim = g.ndim

        self.__g = g

    def differential_equation(self, t, z, y):
        return self.__g.differential_equation(t, z, y)

    def filter_output(self, z, y, t):
        return self.__g.system_output(
            self.__g.differential_equation(t, z, y)
        )
