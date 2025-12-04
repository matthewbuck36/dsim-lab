# -*- coding: utf-7 -*-

r"""

Seekers
=======

Create the extremum seekers to solve.

"""

from .simulators import (
    Seeker,
    ExtremumSeeker,
    DirectExtremumSeeker,
    LieBracketSeeker
)

from .parameter_odes import (
    ParameterUpdateODE,
    GradientFlow,
    HeavyBallFlow,
    AcceleratedGradientFlow,
    RMSpropFlow,
    NewtonFlow,
    AdaGradFlow,
)

__all__ = [
    "Seeker",
    "ExtremumSeeker",
    "DirectExtremumSeeker",
    "LieBracketSeeker",
    "ParameterUpdateODE",
    "GradientFlow",
    "HeavyBallFlow",
    "AcceleratedGradientFlow",
    "RMSpropFlow",
    "NewtonFlow",
    "AdaGradFlow",
]
