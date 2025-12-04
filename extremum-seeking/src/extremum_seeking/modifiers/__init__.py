r"""

Handles the various modifiers

"""

from .prescribed_time import (
    dilation,
    dilation_rate,
    inverse_dilation,
    prescribed_time_filter,
    prescribed_time_parameter_ode,
    prescribed_time_perturbation
)

__all__ = [
    "dilation",
    "dilation_rate",
    "inverse_dilation",
    "prescribed_time_filter",
    "prescribed_time_parameter_ode",
    "prescribed_time_perturbation"
]
