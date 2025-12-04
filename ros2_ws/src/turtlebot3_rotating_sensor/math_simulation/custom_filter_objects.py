"""This script holds pre-made derivative estimation filters
for use in math simulations.
"""

import numpy as np
from abc import ABC, abstractmethod
from derivative_estimation_signals import *
from extremum_seeking.filters import *
from extremum_seeking.seekers.parameter_odes import *

class CustomFilter(ABC): # pylint: disable=too-few-public-methods
    """Defines function calls needed from custom filter objects.
    
    Every custom filter object class needs to have the get filter
    object method. This is the method called to obtain a custom filter
    object made from components in the extremum seeking package.

    Individual custom filter objects define filters with a specific
    structure for a specific extremum seeking method. For example,
    a GESC method only needs its custom filter to perform first
    derivative estimation, this would have a filter with a unique
    structure. However an adaptive method like RMSpropESC needs a
    filter to perform both first derivative and first derivative
    squared estimation, and this filter will have its own unique
    structure. A custom filter object can be defined for both of
    these methods to capture the structure of these unique derivative
    estimation filters

    Class Methods:
        get_filter_object: gives the custom filter object made
        with the a specific structure with call signature
        get_filter_object()
    """

    @abstractmethod
    def get_filter_object(self):
        """Every custom filter object must have a function that
        returns an initialized filter object"""

        # pylint: disable=unnecessary-pass
        pass # This is an abstract method, no implementation here.

class RMSPropFilter(CustomFilter): # pylint: disable=too-few-public-methods
    """This class corresponds to custom filters using the RMSProp ESC method."""

    def __init__(self, params):
        """This initializes the object
        
        The params dictionary should be defined in the following from
        "params":{
            "estimation_signal_object": DerivativeEstimationSignal,
            "gradient_washout_omega_l": float,
            "gradient_squared_washout_omega_l": float,
            "directional_filter_gains": np.ndarray,
            "directional_filter_omega_l": float,
            "frame_arm_length": float
        }
        """

        # Make assertions
        assert "estimation_signal_object" in params, (
            "This class requires an estimation_signal_object key."
        )
        assert isinstance(params["estimation_signal_object"], DerivativeEstimationSignal), (
            "This class requires an DerivativeEstimationSignal object."
        )


        assert "gradient_washout_omega_l" in params, (
            "An omega_l for the gradient washout filter must be initialized with this class."
        )
        assert isinstance(params["gradient_washout_omega_l"], (float, int)), (
            "The gradient washout omega_l must be a float or an int."
        )


        assert "gradient_squared_washout_omega_l" in params, (
            "An omega_l for the gradient squared washout filter must be initialized with this class."
        )
        assert isinstance(params["gradient_squared_washout_omega_l"], (float, int)), (
            "The gradient squared washout omega_l must be a float or an int."
        )


        assert "directional_filter_gains" in params, (
            "An array of gains for the directional filter must be initialized with this class."
        )
        assert isinstance(params["directional_filter_gains"], np.ndarray), (
            "The directional filter gains must be an np.ndarray."
        )


        assert "directional_filter_omega_l" in params, (
            "An omega_l for the directional filter must be initialized with this class."
        )
        assert isinstance(params["directional_filter_omega_l"], (float, int)), (
            "The directional filter omega_l must be a float or an int."
        )


        assert "frame_arm_length" in params, (
            "A frame arm length must be initialized with this class."
        )
        assert isinstance(params["frame_arm_length"], (float, int)), (
            "The frame arm length must be a float or an int."
        )

        # Initialize our derivative estimation signal object
        deriv_estim_obj = params["estimation_signal_object"]

        # Construct the custom filter architecture
        # Track one of the parallel filter filters the cost value
        track_one = WashoutFilter(params["gradient_washout_omega_l"])
        # Track two of the parallel filter filters then squares the cost value
        track_two = CascadeFilter(
            WashoutFilter(params["gradient_squared_washout_omega_l"]),
            FunctionFilter(lambda x: x**2, idim=1, odim=1)
        )
        # Track three of the parallel filter is for derivative estimation signals
        track_three = CascadeFilter(
            FunctionFilter(lambda x: 1, idim=1, odim=1),
            FunctionFilter(
                lambda t: deriv_estim_obj.estimation_output(t),
                idim=1, odim=5
            )
        )
        # Construct the parallel filter
        parallel = ParallelFilter(track_one, track_two, track_three)

        # Construct the signal muxing filter
        mux = FunctionFilter(
            lambda x: np.array([
            x[0]*x[2],
            x[0]*x[3],
            x[1]*x[4],
            x[1]*x[6]
            ]),
            idim = 7, odim = 4
        )

        # Construct the directional filter
        directional = DirectionalFilter(
            RMSpropFlow(
                np.diag(params["directional_filter_gains"]),
                params["directional_filter_omega_l"]
            )
        )

        # Put the filters into cascade
        custom_filter = CascadeFilter(
            parallel, mux, directional
        )

        # Save the custom filter object
        self.filter_object = custom_filter

    def get_filter_object(self):
        """This returns the initialized filter object."""

        return self.filter_object

class ADAGradFilter(CustomFilter): # pylint: disable=too-few-public-methods
    """This class corresponds to custom filters using the ADAGrad ESC method."""

    def __init__(self, params):
        """This initializes the object
        
        The params dictionary should be defined in the following from
        "params":{
            "estimation_signal_object": DerivativeEstimationSignal,
            "gradient_washout_omega_l": float,
            "gradient_squared_washout_omega_l": float,
            "directional_filter_gains": np.ndarray,
            "directional_filter_omega_l": float,
            "adagrad_power": int,
            "frame_arm_length": float
        }
        """

        # Make assertions
        assert "estimation_signal_object" in params, (
            "This class requires an estimation_signal_object key."
        )
        assert isinstance(params["estimation_signal_object"], DerivativeEstimationSignal), (
            "This class requires an DerivativeEstimationSignal object."
        )


        assert "gradient_washout_omega_l" in params, (
            "An omega_l for the gradient washout filter must be initialized with this class."
        )
        assert isinstance(params["gradient_washout_omega_l"], (float, int)), (
            "The gradient washout omega_l must be a float or an int."
        )


        assert "gradient_squared_washout_omega_l" in params, (
            "An omega_l for the gradient squared washout filter must be initialized with this class."
        )
        assert isinstance(params["gradient_squared_washout_omega_l"], (float, int)), (
            "The gradient squared washout omega_l must be a float or an int."
        )


        assert "directional_filter_gains" in params, (
            "An array of gains for the directional filter must be initialized with this class."
        )
        assert isinstance(params["directional_filter_gains"], np.ndarray), (
            "The directional filter gains must be an np.ndarray."
        )


        assert "directional_filter_omega_l" in params, (
            "An omega_l for the directional filter must be initialized with this class."
        )
        assert isinstance(params["directional_filter_omega_l"], (float, int)), (
            "The directional filter omega_l must be a float or an int."
        )


        assert "adagrad_power" in params, (
            "An exponential power must be initialized with this class."
        )
        assert isinstance(params["adagrad_power"], int), (
            "The exponential power must be an int."
        )


        assert "frame_arm_length" in params, (
            "A frame arm length must be initialized with this class."
        )
        assert isinstance(params["frame_arm_length"], (float, int)), (
            "The frame arm length must be a float or an int."
        )

        # Initialize our derivative estimation signal object
        deriv_estim_obj = params["estimation_signal_object"]

        # Construct the custom filter architecture
        # Track one of the parallel filter filters the cost value
        track_one = WashoutFilter(params["gradient_washout_omega_l"])
        # Track two of the parallel filter filters then squares the cost value
        track_two = CascadeFilter(
            WashoutFilter(params["gradient_squared_washout_omega_l"]),
            FunctionFilter(lambda x: x**2, idim=1, odim=1)
        )
        # Track three of the parallel filter is for derivative estimation signals
        track_three = CascadeFilter(
            FunctionFilter(lambda x: 1, idim=1, odim=1),
            FunctionFilter(
                lambda t: deriv_estim_obj.estimation_output(t),
                idim=1, odim=5
            )
        )
        # Construct the parallel filter
        parallel = ParallelFilter(track_one, track_two, track_three)

        # Construct the signal muxing filter
        mux = FunctionFilter(
            lambda x: np.array([
            x[0]*x[2],
            x[0]*x[3],
            x[1]*x[4],
            x[1]*x[5],
            x[1]*x[6]
            ]),
            idim = 7, odim = 5
        )

        # Construct the directional filter
        directional = DirectionalFilter(
            AdaGradFlow(
                np.diag(params["directional_filter_gains"]),
                params["directional_filter_omega_l"],
                params["adagrad_power"]
            )
        )

        # Put the filters into cascade
        custom_filter = CascadeFilter(
            parallel, mux, directional
        )

        # Save the custom filter object
        self.filter_object = custom_filter

    def get_filter_object(self):
        """This returns the initialized filter object."""

        return self.filter_object
