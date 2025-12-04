#!/bin/user/python3
# -* coding:utf-8 *-

r"""
File: SYSTEMS.PY

Author: Patrick McNamee

Date: December 16th, 2022

Brief:
    File containing various functions representing the ODE of various
    types of systems. Used to be a standard set of call inputs.

"""

from abc import ABC, abstractmethod
import numpy as np


def check_dimension_value(val):
    assert isinstance(val, int), "Only integer dimensions are allowed."
    assert val > 0, "Dimensions must be a strictly positive integer."

class System(ABC):
    """ Abstract Base Class for Systems """

    @property
    def ndim(self):
        """ Number of dimensions of system """
        return self.__ndim

    @ndim.setter
    def ndim(self, val):
        check_dimension_value(val)
        self.__ndim = val

    @property
    def udim(self):
        """ Number of control inputs """
        return self.__udim

    @udim.setter
    def udim(self, val):
        check_dimension_value(val)
        self.__udim = val
        
    @abstractmethod
    def __call__(self, t, x, u, **kargs):
        """
        
        Args:
           t (float): Time
           x (np.ndarray): State vector
           u (Callable): Controller
        """
        return NotImplemented
    
    
class FirstOrderIntegrator(System):
    r""" First order interator
        
        .. math::
        
            \dot{x} = u
    
    """
    def __init__(self, ndim=1):
        self.ndim = ndim
        self.udim = ndim

    def __call__(self, t, x, u, **kargs):
        r""" Dynamical system
        Args:
            t (float)      : Simulation time
            x (np.ndarray) : n-dimensional state vector
            u (np.ndarray) : n-dimensional control vector
            kargs          : Passed to control functions for more customized
                             behaviors

            Returns:
                xdot (np.ndarray) : Dynamical system derivative.
        """

        assert u.size == self.udim, (
            f"Control (u) has {u.size} elements but needs {self.udim}."
        )
        
        return u


class SecondOrderIntegrator(System):
    r""" Second order interator
    
    .. math::
    
        \frac{d}{dt} \begin{bmatrix} x \\ \dot{x} \end{bmatrix} = 
        \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix} \begin{bmatrix} x 
        \\ \dot{x} \end{bmatrix} + \begin{bmatrix} 0 \\ u \end{bmatrix}
    
    """
    def __init__(self, ndim=2):
        assert (ndim % 2) == 0, "Must be an even number of dimensions"
        self.ndim = ndim
        self.udim = ndim // 2

    def __call__(self, t, x, u, **kargs):
        """ Second order interator

        Args:
            t (float)      : Simulation time
            x (np.ndarray) : n-dimensional state vector
            u (np.ndarray) : n-dimensional control vector
            kargs          : Passed to control functions for more customized 
                             behaviors

        Returns:
            xdot (np.ndarray) : Dynamical system derivative.
        """
    
        return np.hstack((x[x.size//2:], u))


class NonholonomicUnicycle(System):
    r"""  2D Non-holonomic Unicycle dynamical system
        
    .. math::
    
        \dot{x} &= u[0] \begin{bmatrix} \cos(\theta) \\ \sin(\theta)
        \end{bmatrix} \\
        \dot{\theta} &= u[1]
    
    """
    def __init__(self):
        self.ndim = 3
        self.udim = 2


    def __call__(self, t, x, u, **kargs):
        r"""
        Args:
            x (np.ndarray) : 3-dimensional state vector of (x1,x2,theta)
            u (np.ndarray) : Vector of the control inputs
                           : first argument planar velocity and second is
                             angular
                             velocity.
            t (float)      : Simulation time
            kargs          : Passed to control functions for more customized 
                             behaviors

        Returns:
            xdot (np.ndarray) : Dynamical system derivative.
        """
        
        return np.array([
            u[0]*np.cos(x[2]),
            u[0]*np.sin(x[2]),
            u[1]
        ])

    
class DriftingNonholonomicUnicycle(NonholonomicUnicycle):
    r""" Non-holonomic Unicycle dynamical system with drift
        
    .. math::
    
        \dot{x} &= u[0] \begin{bmatrix} \cos(\theta) \\ \sin(\theta)
        \end{bmatrix} + d(t, x) \\
        \dot{\theta} &= u[1]
    
    """
    def __init__(self, drifting_fun):
        """
        Args:
            drifing_fun (Callable): Function with argument (t, x)
        """
        super().__init__()
        self.__drifting_fun = drifting_fun

    def __call__(self, t, x, u, **kargs):
        r"""
        Args:
            x (np.ndarray) : 3-dimensional state vector of (x,y,theta)
            u (np.ndarray) : Control vector of (v, omega)
            t (float)      : Simulation time
            kargs          : Passed to control functions for more customized
                             behaviors

        Returns:
            xdot (np.ndarray) : Dynamical system derivative.
        """

        return (
            super().__call__(t, x, **kargs)
            + self.__drifting_fun(t, x, **kargs)
        )


class NonholonomicUnicycleSystem3D(System):
    r""" Three dimensional vehicle.
    
    .. math::
        
        \dot{r} &= u_1 \begin{bmatrix} \cos(\phi)\cos(\theta) \\
        \cos(\phi\sin(\theta) \\ \sin(\phi) \end{bmatrix} \\
        \dot{\phi} &= u_2 \\
        \dot{\theta} &= u_3
    
    """
    def __init__(self):
        self.ndim = 5
        self.ndim = 3
    
    def __call__(self, t, x, u, **kargs):
        r"""
        Args:
            t (float)      : Simulation time
            x (np.ndarray) : 5-dimensional state vector of (x, y, z, phi, theta)
            u (list)       : List of three control functions
            kargs          : Pass to control functions for more customized
                             behaviors

        Returns:
            xdot : derivative of the state
        """

        # preallocate state derivative
        xdot = np.zeros(x.shape)

        # derivative of positions
        xdot[:3] = u[0]*np.array([
            np.cos(x[3])*np.cos(x[4]),
            np.cos(x[3])*np.sin(x[4]),
            np.sin(x[3])
        ])
    
        # derivative of angles
        xdot[3] = u[1]
        xdot[4] = u[2]

        return xdot

class PursuerEvaderGame(System):
    r""" System of a two player pursuer-evader game.
    
    This class is to simulate a pursuer-evader game. The game assumes two
    players, each with their own, independent dynamics.
    
    .. math::
    
        \frac{d}{dt} x_{p} &= f(t, x_{p}, u_{p}) \\
        \frac{d}{dt} x_{e} &= f(t, x_{e}, u_{e})
    
    where:
    * :math:`x_{p}` is the pursuer states.
    * :math:`x_{e}` is the evader states.
    * :math:`u_{p}` is the pursuer controller vector.
    * :math:`u_{e}` is the evader controller vector.
    
    Note that one expects that the controllers will have feedback on both player
    states. The call signatures of the respective controllers look like
    
    .. math::
    
        u_{i}(t, x_{p}, x_{e}, theta)
    
    """

    def __init__(self, f_pursuer, f_evader):
        """
        Args:
            pursuer_ndim (int): Number of dimensions for a pursuer.
            evader_ndim (int): Number of dimensions for evader.
            u_pursuer (Callable): Controller for pursuer.
            u_evader (Callable): Controller for evader.
        """

        self.ndim = f_pursuer.ndim + f_evader.ndim
        self.udim = f_pursuer.udim + f_evader.udim
        
        self.f_pursuer = f_pursuer
        self.f_evader = f_evader
        
        self.__i_x_pursuer = np.arange(self.f_pursuer.ndim)
        self.__i_x_evader = np.arange(self.f_evader.ndim) + self.f_pursuer.ndim

        self.__i_u_pursuer = np.arange(self.f_pursuer.udim)
        self.__i_u_evader = np.arange(self.f_evader.udim) + self.f_pursuer.udim
        
    def seperate_player_states(self, x_aug):
        """ Splits the state vector into pursuer and evader portions """
        if x_aug.ndim == 1:
            return x_aug[self.__i_x_pursuer], x_aug[self.__i_x_evader]
        else:
            return x_aug[:, self.__i_x_pursuer], x_aug[: self.__i_x_evader]

    def seperate_player_controls(self, u_aug):
        """ Splits the control vector into pursuer and evader portions """
        return u_aug[self.__i_u_pursuer], u_aug[self.__i_u_evader]

    def concatenate_player_controls(self, u_p, u_e):
        r""" Concatenates two controllers for each player into one 
        
        Takes two controllers for the pursuer and evader with 
        
        Args:
            u_p (Callable): controller for the pursuer
            u_e (Callable): controller for the evader
        
        Returns:
            u (Callable): overall controller for the game.
        
        """
        def u(t, x, theta):
            x_p, x_e = self.seperate_player_states(x)
            return np.hstack((
                u_p(t, x_p, x_e, theta),
                u_e(t, x_p, x_e, theta)
            ))

        return u
    
    def __call__(self, t, x, u, **kargs):
        r"""
        Args:
            t (float): Current simulation time
            x (np.ndarray): State vector of pursuer states and then evaders
            u (Callable): State vector of controller inputs
        """
        
        x_p, x_e = self.seperate_player_states(x)
        u_p, u_e = self.seperate_player_controls(u)

        x_p_dot = self.f_pursuer(t, x_p, u_p)
        x_e_dot = self.f_evader(t, x_e, u_e)
        
        return np.hstack((x_p_dot, x_e_dot))

