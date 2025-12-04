#!/bin/user/python3
# -* coding:utf-8 *-

r"""

File: SIMULATORS.PY

Author: Patrick McNamee

Brief:
    This submodule handles the various setup and dynamics for extremum seekers.
    An extremum seeker attempts to optimize a sensor output :math:`y = J(t,x)`,
    i.e. a cost function or scalar field :math:`J` which is a function of the 
    dynamic variables :math:`x`. The main assumption is that there is a
    contoller :math:`u` parameterized by the parameter vector :math:`\theta` 
    such that the steady mapping state :math:`x(t)\mapsto \ell(\theta)`. The 
    goal of extremum seekers is to drive :math:`x\mapsto x^{*}` where 
    :math:`x^*` is an optimal point of :math:`J`. Commonly, the map is unknown
    and so an estimate of an optimizing parameter :math:`\hat{\theta}` is driven
    to :math:`\theta^*` where :math:`\ell(\theta^*) = x^*`. In order to drive 
    the parameter estimate to the optimizing parameter, the parameter is 
    perturbed  to locally explore sensor outputs near the steady state of the 
    parameter estimate. This perturbed sensor output is then used to estimate 
    the local derivative estimates :math:`z(t) = h(t,y)` which are inputed into
    a dynamical system controlling the updates of :math:`\hat{\theta}`. A block
    diagram for this extremum seeker is given below.::

                      State System Dynamics           Cost Function          
                +--------------------------------+ x(t) +---------+        
             +->+ \dot{x} = f(t,x,u(t,x;\theta)) +------+ J(t, x) |---+---> y(t)
             |  +--------------------------------+      +---------+   |     
             |                                                        |     
             | \theta                                                 |     
             |                                                        V     
          +--+---+                             Derivative +-----------+--------+
          | p(t) | Perturbation                Estimation | \dot{z} = h(t,z,y) +
          +--+---+                                        +-----------+--------+
             ^                                                        |    
             |                                                        | 
             | \hat{theta}                                            | z(t)            
             |                                                        |                 
             |             Parameter Estimate Dynamics                |                 
             |      +-----------------------------------------+       |                 
             +------+ \dot{\hat{\theta} = g(t,\hat{\theta},z) +<------+
                    +-----------------------------------------+
                                                                                     
    This module ...

"""

from abc import ABC, abstractmethod
from extremum_seeking.filters import Filter
import numpy as np
from .parameter_odes import ParameterUpdateODE
from typing import Callable


"""
Abstract Base Classes
"""

class Seeker(ABC):
    """ Defines how to call parameter update ODEs and their arguments.
    
    Class Properties:
        ndim (int): Number of states that the system keeps track of
    
    Class Methods:
        
    """
    # pylint: disable=invalid-name

    @property
    def ndim(self):
        """ Number of dimensions of the filter """
        return self.__ndim

    @ndim.setter
    def ndim(self, val):
        assert isinstance(val, int), "Only integer dimensions are allowed."
        assert val > 0, "Dimensions must be a strictly positive integer."
        self.__ndim = val

    @property
    def J(self):
        return self.__J

    @J.setter
    def J(self, val):
        # Checks
        assert isinstance(val, Callable), (
            "Cost function J must be a callable function."
        )
        """
        assert hasattr(val, "gradient"), (
            "Cost function J must have a gradient."
        )
        """
        # Simplification
        if not hasattr(val, "partial_t"):
            val.partial_t = lambda *args: 0.
        # Assignment
        self.__J = val
            
    @property
    def h(self):
        return self.__h

    @h.setter
    def h(self, val):
        assert isinstance(val, Filter), (
            "h must be a Filter."
        )
        self.__h = val
        
    @abstractmethod
    def initialize_system(self, *args):
        """ Initialize all the ODE states given arguments. """
        return NotImplemented
        
    @abstractmethod
    def differential_equation(self, t, x_aug, *args):
        r""" Differential equation for updating the parameters 

        Args:
            t (float) : Time
            x_aug (np.ndarray) : Augmented state vector
            \*args : Additional arguments
        """
        return NotImplemented

    @abstractmethod
    def parse_history(self, x_augmented_history):
        """ Parse through array storying history of states
        
        Args:
            x_augmented_history (np.nadarray): (N, ndim) array of state time
              histories
        
        Returns:
            Parsed components of the history
        """
        return NotImplemented


class ParameterizedSystem(ABC):
    """ Systmes that will have parameters theta to optimize. """
    @property
    def g(self):
        return self.__g

    @g.setter
    def g(self, val):
        assert isinstance(val, ParameterUpdateODE), (
            "g must be a ParameterUpdateODE."
        )
        self.__g = val

class DynamicalSystem(ABC):
    """ System with state dynamics on x. """
    
    @property
    def f(self):
        return self.__f
    
    @f.setter
    def f(self, val):
        assert isinstance(val, Callable), (
            "System state dynamics must be a callable function."
        )
        assert hasattr(val, "ndim"), (
            "System state dynamics must specify the dimensions of the system."
        )
        self.__f = val

    @property
    def u(self):
        return self.__u

    @u.setter
    def u(self, val):
        assert isinstance(val, Callable), (
            "Controller u must be callable."
        )
        self.__u = val


"""
Various seeking algorithms.
"""
        
class ExtremumSeeker(Seeker, ParameterizedSystem, DynamicalSystem):
    r""" Extremum Seeker -- baseline algorithm.
    
    Class Members:
        f (Callable): Differential equation of system. 
                      Call Signature (t, x, u, ``**kargs``)
        g (ParameterUpdateODE): Differential equation for the parameter updates.
                                Call Signature (t, theta_hat, z, ``**kargs``)
        h (DerivativeEstimateFilter) : Estimates the derivatives of the cost 
          function. Call Signature (t, J, dJ/dt, z, ``**kargs``)
        J (Callable): Source Field to optimize on. Has a scalar function call 
          signature (t, x, ``**kargs``)
        p (Callable): Signal for excitation.
                      Call Signature (t)
        u (Callable): Static controller for the dynamics
                      Call Signature (t, x; \theta)
    
    """
    # pylint: disable=invalid-name,not-callable
    
    def __init__(self, f, g, h, J, p, u):
        
        # Get the subfunctions
        self.f = f
        self.g = g
        self.h = h
        self.J = J
        self.p = p
        self.u = u

        # Dimensions of vector
        self.ndim = self.f.ndim + self.h.ndim + self.g.ndim

        # Fast indices for augmented states
        self.__i_x = np.arange(self.f.ndim)
        self.__i_z = np.arange(self.h.ndim) + self.f.ndim
        self.__i_theta = self.f.ndim + self.h.ndim + np.arange(self.g.ndim)
    
    def initialize_system(self, x_0, z_0, theta_hat_0):
        x_aug_0 = np.zeros((self.ndim,))
        x_aug_0[self.__i_x] = x_0
        x_aug_0[self.__i_z] = z_0
        x_aug_0[self.__i_theta] = theta_hat_0

        return x_aug_0
        
    def differential_equation(self, t, x_aug, **kargs):
        r""" Differential Equation representation of the algorithm
        
        Args:
            t (float) : Time
            x_aug (np.ndarray): Augmented state vector for system.
                              : Structured [physical, filter, parameter] states
        
        Returns:
            x_aug_dot (np.ndarray) : Derivative of all augmented states
        
        """

        # Determine the derivative vector of the system
        xvec = x_aug[self.__i_x]  # System
        theta_hat_system = x_aug[self.__i_theta]  # All estimate parameters
        theta_hat = self.g.system_output(theta_hat_system)  # Optimal estimates
        zvec_system = x_aug[self.__i_z]  # Current filter states
        
        # Determine the instantaneous control
        theta = theta_hat + self.p(t)
        uvec = self.u(t, xvec, theta, **kargs)

        # State derivative
        xdot = self.f(t, xvec, uvec, **kargs)

        # Filter the Signal
        Jt = self.J(t, xvec)  # Current source field value
        zvec = self.h.filter_output(zvec_system, Jt, t)

        # Get filter derivative states
        if self.h.is_derivative_based:
            Jtdot = (
                np.sum(self.J.gradient(t, xvec, **kargs)*xdot)
                + self.J.partial_t(t, xvec, **kargs)
            )
            zdot = self.h.differential_equation(t, zvec_system, Jtdot)
        else:
            zdot = self.h.differential_equation(t, zvec_system, Jt)
        
        # Derivative of the controller parameter
        thetadot = self.g.differential_equation(
            t, theta_hat_system, zvec
        )

        # Agglemate and return
        x_aug_dot = np.zeros((self.ndim,))
        x_aug_dot[self.__i_x] = xdot
        x_aug_dot[self.__i_z] = zdot
        x_aug_dot[self.__i_theta] = thetadot
        return x_aug_dot

    def parse_history(self, x_aug_history):
        """ Seperates N x ndim vector into appropriate time histories """
        return (
            x_aug_history[:, self.__i_x],
            x_aug_history[:, self.__i_z],
            x_aug_history[:, self.__i_theta]
        )

    def perturbed_parameter_history(self, t_vec, theta_hat_vec):
        """ Returns a the perturbed parameters given a time 
        
        Args:
            t_vec (np.ndarray): (N,) array of N time points
            theta_hat_vec (np.ndarray): (N,n) of N times points and of 
               n-dimensional theta
        
        Returns:
            theta_vec (np.ndarray): (N,n) array of perturbed parameters.
        """
        
        p_vec = np.apply_along_axis(
            self.p, 1, t_vec.reshape(t_vec.shape + (1,))
        )
        return theta_hat_vec + p_vec


class DirectExtremumSeeker(Seeker, ParameterizedSystem):
    r""" Direct Extremum Seeker -- Acts directly on the source field or map.
    
    A Direct Extremum Eeeker operates directly on the cost function/source 
    field/map. This is analogous to an Extremum Seeker with fast state dynamics
    or a continous time perturbation based optimizer. This block diagram is as 
    follows: ::
    
                                                  Cost Function          
                            \theta(t)           +--------------+        
             +----------------------------------+ J(t, \theta) |---+-----> y(t)
             |                                  +--------------+   |     
             |                                                     |     
             |                                                     |     
             |                                                     V     
          +--+---+                            Derivative  +--------+-----------+
          | p(t) | Perturbation               Estimation  | \dot{z} = h(t,z,y) +
          +--+---+                                        +--------+-----------+
             ^                                                     |    
             |                                                     | z(t)
             | \hat{\theta}                                        |                 
             |                                                     |                 
             |             Parameter Estimate Dynamics             |                 
             |      +-----------------------------------------+    |                 
             +------+ \dot{\hat{\theta} = g(t,\hat{\theta},z) +<---+
                    +-----------------------------------------+
                                                                                     
    
    Class Members:
        J (Callable): Source Field to optimize on.
                      Has a scalar functioncall signature (t, theta, \*\*kargs)
    
        h (Callable): Filtering of the source field.
                      Call Signature (t, J, dJ/dt, z, pert_signal, \*\*kargs)
    
        g (Class): Parameter update ODE system.
                   Call Signature (t, theta_hat, z)
    
        perturbation_signal (Callable): Signal for excitation.
                                        Call Signature (t)
    
    """
    # pylint: disable=invalid-name,not-callable
    
    def __init__(self, g, h, J, p):
        
        # Get the subfunctions
        self.g = g
        self.h = h
        self.J = J
        self.p = p

        # Dimensions of vector
        self.ndim = self.h.ndim + self.g.ndim

        # Fast indices for augmented states
        self.__i_z = np.arange(self.h.ndim)
        self.__i_theta = self.h.ndim + np.arange(self.g.ndim)
        
    def initialize_system(self, z_0, theta_hat_sys_0):
        """ Returns an initial condition for the combined given component 
          initial states.

        Args:
            z_0: Initial filter states
            theta_hat_0: Initial optimial parameter estimates
        
        """
        x_aug_0 = np.zeros((self.ndim))
        x_aug_0[self.__i_z] = z_0
        x_aug_0[self.__i_theta] = theta_hat_sys_0

        return x_aug_0
        
        
    def differential_equation(self, t, x_aug, *args, **kargs):
        r""" Differential Equation representation of the algorithm
        
        Args:
            t (float): Time
            x_aug (np.array): Augmented state vector for system.
        
        """

        # Determine the current states
        theta_hat_sys_states = x_aug[
            self.__i_theta
        ]  # All parameter update states
        theta_hat = self.g.system_output(
            theta_hat_sys_states
        )  # Estimate parameters
        theta = theta_hat + self.p(t)  # Current parameter values
        zvec_system = x_aug[self.__i_z]  # Current filter states
        Jt = self.J(t, theta, **kargs)  # Current source field value
        zvec = self.h.filter_output(zvec_system, Jt, t)  # Output of filter
        
        # Derivative of the controller parameter
        theta_hat_dot = self.g.differential_equation(
            t, theta_hat_sys_states, zvec
        ) 
        
        # Derivative of filter states
        if self.h.is_derivative_based:
            Jtdot = (
                np.sum(
                    self.J.gradient(t, theta, **kargs)*(
                        self.g.system_output(theta_hat_dot)
                        + self.p.derivative(t)
                    )
                )
                + self.J.partial_t(t, theta, **kargs)
            )
            zdot = self.h.differential_equation(t, zvec_system, Jtdot)
        else:
            zdot = self.h.differential_equation(t, zvec_system, Jt)

        # Agglemate and return
        x_aug_dot = np.zeros((self.ndim,))
        x_aug_dot[self.__i_z] = zdot
        x_aug_dot[self.__i_theta] = theta_hat_dot
        return x_aug_dot
    
    def parse_history(self, x_aug_history):
        r""" Seperates N x ndim vector into appropriate time histories """
        return (
            x_aug_history[:, self.__i_z],
            x_aug_history[:, self.__i_theta]
        )

    def perturbed_parameter_history(self, t_vec, theta_hat_vec):
        """ Returns a the perturbed parameters given a time 
        
        Args:
            t_vec (np.ndarray): (N,) array of N time points
            theta_hat_vec (np.ndarray): (N,n) of N times points and of 
              n-dimensional theta
        
        Returns:
            theta_vec (np.ndarray): (N,n) array of perturbed parameters.
        """
        
        p_vec = np.apply_along_axis(
            self.p, 1, t_vec.reshape(t_vec.shape + (1,))
        )
        return theta_hat_vec + p_vec


class LieBracketSeeker(Seeker, DynamicalSystem):
    r""" Extremum Seeker using Lie Brackets

    Extremum seeking where the controller directly takes in derivative 
    estimates to modify the controller. The block diagram appears like ::

                                                          Cost           
                      System Dynamics                   Function         
                +-------------------------------+ x(t) +---------+       
             +->+ \dot{x} = f(t, x, u(t, x; z)) +----->+ J(t, x) |--+-----> y(t)
             |  +-------------------------------+      +---------+  |     
             |                                                      |     
             |                                                      |     
             |              Estimation Filters                      |     
             |     z(t)  +---------------------+                    |     
             +-----------+ \dot{z} = h(t,z,y)  +--------------------+     
                         +---------------------+                         
                                                                        
                                                                         
    and the state ODE can be rewritten into the special affine form of
    
    .. math::
    
        \dot{x} = f_{0}(t, x)
        + \sum_{i=1}^{m} f_{i}(t,x) \omega^{p_i} u'_{i}(k_i\omega t)
    
    where :math:`p\in (0,1)`, :math:`k_i \in \mathbb{Q}_{>0}`, and 
    :math:`u'_{i}` is a :math:`2\pi` periodic function.

    """
    # pylint: disable=invalid-name,not-callable

    def __init__(self, f, h, J, u):
        
        # Get the subfunctions
        self.f = f
        self.h = h
        self.J = J
        self.u = u

        # Dimensions of vector
        self.ndim = self.f.ndim + self.h.ndim

        # Fast indices for augmented states
        self.__i_x = np.arange(self.f.ndim)
        self.__i_z = np.arange(self.h.ndim) + self.f.ndim

    def initialize_system(self, x_0, z_0):
        x_aug_0 = np.zeros((self.ndim,))
        x_aug_0[self.__i_x] = x_0
        x_aug_0[self.__i_z] = z_0

        return x_aug_0
    
    def differential_equation(self, t, x_aug, **kargs):
        r""" Differential Equation representation of the algorithm
        
        Args:
            t (float) : Time
            x_aug (np.ndarray) : Augmented state vector for system.
                               : Structured [physical, filter, parameter] states
        
        Returns:
            x_aug_dot (np.ndarray) : Derivative of all augmented states
        
        """
        # pylint: disable=invalid-name,not-callable

        # Determine the derivative vector of the system
        xvec = x_aug[self.__i_x]  # Current physical states
        zvec_system = x_aug[self.__i_z]  # Current filter states
        Jt = self.J(t, xvec, **kargs)  # Current source field value
        zvec = self.h.filter_output(zvec_system, Jt, t)  # Current filter output
        uvec = self.u(t, xvec, zvec)  # Current controller output
        
        xdot = self.f(t, xvec, uvec)  # Current physical state derivative

        # Filter derivative
        if self.h.is_derivative_based:
            Jtdot = (
                np.sum(self.J.gradient(t, xvec, **kargs)*xdot)
                + self.J.partial_t(t, xvec, xdot, uvec, **kargs)
            )
            zdot = self.h.differential_equation(t, zvec_system, Jtdot)
        else:
            zdot = self.h.differential_equation(t, zvec_system, Jt)

        # Aggregate and return
        x_aug_dot = np.zeros((self.ndim,))
        x_aug_dot[self.__i_x] = xdot
        x_aug_dot[self.__i_z] = zdot

        return x_aug_dot

    def parse_history(self, x_aug_history):
        r""" Seperates N x ndim vector into appropriate time histories """
        return (
            x_aug_history[:, self.__i_x],
            x_aug_history[:, self.__i_z],
        )
