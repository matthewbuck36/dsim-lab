#!/usr/bin/python3

r"""
Module to store some well known test objective functions. Functions in here are
compatible for instanciated instances to be used as `:math:J` for the `seekers`
subpackage.
"""

from abc import ABC, abstractmethod
import numpy as np


def autonomous_system(objective_function):
    """ Defines the partial_t function as 0. """

    objective_function.partial_t = lambda *args: 0.

    return objective_function

def make_callable(objective_function):
    """ Defines __call__ to make object Callable. """

    def call(self, _, x):
        return self.evaluate(x)
 
    objective_function.__call__ = call
    return objective_function

class ObjectiveFunction(ABC):
    """ Abstract Base Class for Objective Functions """

    @abstractmethod
    def __call__(self, *args):
        """ Call signature of either (x) or (t, x) """
        return NotImplemented

    @abstractmethod
    def evaluate(self, x):
        """ Returns the value of the funciton """
        return NotImplemented

    @abstractmethod
    def global_minimum(self, x):
        """ Returns the value of the function that is the global minimums and its location"""
        return NotImplemented

    @abstractmethod
    def gradient(self, *args):
        """ Gradient of the objective funciton """
        return NotImplemented

    @abstractmethod
    def hessian(self, *args):
        """ Hessian of the objective funciton """
        return NotImplemented

    @property
    def idim(self):
        """ Input dimension of the function """
        return self.__idim

    @idim.setter
    def idim(self, val):
        assert isinstance(val, int), "Must be integer dimension."
        assert val > 0, "Input dimension of the system mut be positive."
        self.__idim = val
    

@autonomous_system
@make_callable
class Ackley:
    """ Ackley Function for testing optimization algorithms """

    def __init__(self, a=20., b=0.2, c=2.*np.pi, idim=2):
        self.__a = a
        self.__b = b
        self.__c = c
        self.idim = idim

    @property
    def a(self):
        return self.__a

    @property
    def b(self):
        return self.__b

    @property
    def c(self):
        return self.__c

    def evaluate(self, x):
        d = self.idim
        return (
            -self.a*np.exp(-self.b*np.linalg.norm(x)/np.sqrt(d))
            -np.exp(np.sum(np.cos(self.c*x))/d)
            + self.a + np.exp(1)
        )

    def global_minimum(self):
        value = 0
        location = np.array([0,0])
        return value, location

    def gradient(self, x):
        d = self.idim
        norm_x = np.linalg.norm(x)

        return (
            self.a*self.b*np.exp(-self.b*norm_x/np.sqrt(d))*x/(norm_x*np.sqrt(d))
            + self.c*np.exp(np.sum(np.cos(self.c*x))/d)/d*np.sin(self.c*x)
        )

    def hessian(self, x):
        d = self.idim
        norm_x = np.linalg.norm(x)

        return (
            -self.a*self.b**2*np.exp(-self.b*norm_x/np.sqrt(d))/(np.sqrt(d))
            - self.c**2*np.exp((np.sum( np.sin(self.c*x)**2- np.cos(self.c*x)))/d)*d**2
        )

@autonomous_system
@make_callable
class Rastrigin:
    """ Rastrigin Function for testing optimization algorithms"""

    _A = 10.  # Common parameter

    def __init__(self, idim=2):

        self.idim = idim

    def evaluate(self, x):
        return self._A*self.idim + np.sum(x**2. - self._A*np.cos(2.*np.pi*x))

    def global_minimum(self):
        value = 0
        location = np.zeros(self.idim,)
        return value, location

    def gradient(self, x):
        return 2.*(x + np.pi*self._A*np.sin(2.*np.pi*x))

    def hessian(self, x):

        return 2.*(1 + 2.*np.pi**2*self._A*np.cos(2.*np.pi*x))

@autonomous_system
@make_callable
class Sphere:
    """ Sphere Function for testing optimization algorithms"""

    def __init__(self):
        self.idim = 3

    def evaluate(self, x):
        return np.sum(x**2)
     
    def global_minimum(self):
        value = 0
        location = np.zeros(self.idim,)
        return value, location
     
    def gradient(self, x):
        return 2*x
     
    def hessian(self):
        return 2
         
@autonomous_system
@make_callable
class Rosenbrock:
    """ Rosenbrock Function for testing optimization algorithms"""

    def __init__(self, a=100, idim=2):
        self.d = idim
        self.a = a
         
    def evaluate(self, x):
        return np.sum(self.a*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2 for i in range(len(x)-1)
                      )
     
    def global_minimum(self):
        value = 0
        location = np.ones(self.d,)
        return value, location
     
    def gradient(self, x):
        return (self.a*-4*(x[i+1] - x[i])*x[i] - 2*(1 - x[i]) for i in range(len(x-1)))
     
    def hessian(self, x):
        return (self.a*-4*((x[i+1] -2*x[i]) + 2) for i in range(len(x-1)))
    

@autonomous_system
@make_callable
class Beale:
    """ Beale Function for testing optimization algorithms"""

    def __init__(self, a=1.5, b=2.25, c=2.625, idim=3):
        self.d = idim
        self.a = a
        self.b = b
        self.c = c
         
    def evaluate(self, x):
        return ((self.a - x[0] + x[0]*x[1])**2 
                + (self.b - x[0] + x[0]*x[1]**2)**2 
                + (self.c - x[0] + x[0]*x[1]**3)**2)
     
    def global_minimum(self):
        value = 0
        location = np.array([3, 0.5, 0])
        return value, location
     
    def gradient(self, x):
        return (2*(self.a - x[0] + x[0]*x[1])*(-1 + x[1]) 
                + 2*(self.b - x[0] + x[0]*x[1]**2)*(-1 + x[1]**2) 
                + 2*(self.c - x[0] + x[0]*x[1]**3)*(-1 + x[1]**3))
     
    def hessian(self, x):
        return (2*((-1 + x[1]))*(-1 + x[1]) 
                + 2*(-1 + x[1]**2)*(-1 + x[1]**2) 
                + 2*(-1 + x[1]**3)*(-1 + x[1])
                )
