r"""

Combines all of the filters together

"""

from .base_filters import (
    value_based_filter,
    derivative_based_filter,
    Filter,
    ConvolutionFilter,
    FunctionFilter,
    LowPassFilter,
    HighPassFilter,
    WashoutFilter,
    LowPassRicattiFilter,
    DirectionalFilter
)
from .aggregate_filters import (
    ParallelFilter,
    CascadeFilter
)

__all__ = [
    "value_based_filter",
    "derivative_based_filter",
    "Filter",
    "ConvolutionFilter",
    "FunctionFilter",
    "LowPassFilter",
    "HighPassFilter",
    "WashoutFilter",
    "LowPassRicattiFilter",
    "DirectionalFilter",
    "ParallelFilter",
    "CascadeFilter"
]

del base_filters, aggregate_filters
