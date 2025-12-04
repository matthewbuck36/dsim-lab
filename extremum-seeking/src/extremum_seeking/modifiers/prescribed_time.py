# -* utf-8 *-

r"""
File: PRESCRIBED_TIME.PY

Author: Patrick McNamee

Brief:
    Implementation of prescribed time for the extremum seekers. The prescribed
    time operates on a dilation of a finite time interval into an infinite time
    interval. Rigirously, we define the dilation by :math:`\nu: [t_0, t_0 + T]
    \mapsto [t_0, \infty)` where :math:`t_0` is the initial time and :math:`T`
    is the length of the finite time interval. In principle, we take methods
    that we know work in the infinite interval and modify their inputs and
    governing differential equations so that they work in the finite interval.
    For example, if :math:`\tau` is the infinite time variable, then the
    governing differential equation for the finite time variable :math:`t` is
    
    .. math::

        \frac{d}{d\tau}x &= f(\tau, x, u) \\
        \frac{d}{dt}x &= \frac{d\tau}{dt}\cdot f(\nu(t), x, u)

    In code, we simply mask any output that may depend on time so that the
    input is mapped to :math:`\tau` before being passed into the original
    function. We also modify the differential equation by multiplying the
    dilation rate.
"""

from extremum_seeking.filters import Filter
from extremum_seeking.seekers import ParameterUpdateODE
import numpy as np

def dilation(t, T, t_0=0.):
    r"""

    .. math::
    
        \tau = \frac{t - t_0}{1 - \frac{(t - t_0)}{T}} + t_0
    
    """
    return (t - t_0)/(1. - (t - t_0)/T) + t_0

def dilation_rate(t, T, t_0=0.):
    r"""

    .. math::
    
        \frac{d\tau}{dt} = \left(1 - \frac{(t - t_0)}{T}\right)^{-2}
    
    """
    return np.power(1 - (t - t_0)/T, -2.)

def inverse_dilation(tau, T, t_0=0.):
    r"""

    .. math::
    
        t = \frac{\tau - t_0}{1 + \frac{(\tau - t_0)}{T}} + t_0
    
    """
    return t_0 + (tau - t_0)/(1 + (tau - t_0)/T)

def prescribed_time_perturbation(p, T, t_0=0.):
    """ Alters the perturbation to the finite time scale """
    return lambda t: p(dilation(t, T, t_0))

def prescribed_time_filter(h, T, t_0=0.):
    """ Alters a filter to the finite time scale """

    assert isinstance(h, Filter), "Only handles Filter objects"

    __old_differential_equation = h.differential_equation
    __old_filter_output = h.filter_output

    h.differential_equation = lambda t, z, y: (
        dilation_rate(t, T, t_0)
        *__old_differential_equation(dilation(t, T, t_0), z, y)
    )
    h.filter_output = lambda t, z, y: (
        __old_filter_output(z, y, dilation(t, T, t_0))
    )

    return h

def prescribed_time_parameter_ode(g, T, t_0=0.):
    """ Alters the parameter dynamics to the finite time scale """
    
    assert isinstance(g, ParameterUpdateODE), (
        "Only handles ParameterUpdateODE objects."
    )

    __old_differential_equation = g.differential_equation
    g.differential_equation = lambda t, theta, z:(
        dilation_rate(t, T, t_0)
        *__old_differential_equation(dilation(t, T, t_0), theta, z)
    )
    return g
