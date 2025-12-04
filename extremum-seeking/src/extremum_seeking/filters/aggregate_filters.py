#!/usr/bin/python3

r"""

Handles the aggregation of base filters into more complicated estimation
filters. The two methods for aggregation are to assemble component filters
into their parallel or sequential circuits.

"""

# from base_filters import Filter
from extremum_seeking.filters import Filter
import numpy as np


def _filter_check(val):
    for v in val:
        assert isinstance(v, Filter), "Only filters may be given as inputs."

class ParallelFilter(Filter):
    r"""
    
    ::
                                                                                    
         y      +-----+                                                         
        ---+--->+ h_1 +---> z_1                                                 
           |    +-----+                                                         
           |                                                                    
           |    +-----+                                                         
           +--->+ h_2 +---> z_2                                                 
           |    +-----+                                                         
                                                                                
           :       :                                                            
           :       :                                                            
           :       :                                                            
                                                            
           |    +-----+                                                         
           +--->+ h_n +---> z_n                                                 
                +-----+                                                         
                                                                                
    
    """

    def __init__(self, *args):

        # Check if all inputs are filters
        assert args, "Need to specify the component filters."
        _filter_check(args)

        # Check to see if all filters are either value or derivative based
        assert (
            all([h.is_value_based for h in args]) or
            all([h.is_derivative_based for h in args])
        ), "Filters must either all be value or all be derivative based."

        # Split filters between variable and fixed input dimensions
        h_fixed_idim = [h for h in args if isinstance(h.idim, int)]
        h_var_idim = [h for h in args if isinstance(h.idim, tuple)]

        # Check filters with fixed input dimensions for consistency
        unique_fixed_idim = np.unique([h.idim for h in h_fixed_idim])
        if unique_fixed_idim.size > 1:
            # Inconsistency between filters with fixed input dimensions
            raise ValueError(
                "Not all component filters share same input dimension."
            )

        # If a unique fixed dimension exists, get it. Otherwise be None
        fixed_idim = int(unique_fixed_idim[0]) if unique_fixed_idim else None

        # Check filters with variable input dimensions for consistency
        if not h_var_idim:
            # No variable input filters exist
            var_idim = None
        else:
            var_idim = set(h_var_idim[0].idim)  # Get first posibilites

            # Iterate over the rest of the filters
            for i in range(1, len(h_var_idim)):
                var_idim = var_idim.intersection(
                    set(h_var_idim[i].idim)
                )
                if not var_idim:
                    # If the empty set is the only possibility
                    raise ValueError(
                        "Filters with variable input dimensions are "
                        "incompatible."
                    )
        
        # At this point, either fixed_idim or possible_idim is not None.
        # We need to ensure compatibility between fixed and variable filters
        if fixed_idim is None:
            # Case 1: No fixed idim, use the variable idim for overall idim
            if len(var_idim) > 1:
                # Multiple possibilities, use set as tuple for idim
                self.idim = tuple(var_idim)
            else:
                # Singleton set. Simple get the numerical value
                self.idim = var_idim.pop()
        elif var_idim is None:
            # Case 2: no variable idim, use the fixed idim
            self.idim = fixed_idim
        else:
            # Case 3: Both variable and fixed idim, check compatibility
            assert fixed_idim in var_idim, (
                "The input dimension from fixed input dimensional filters must "
                "be a possible input  dimension for variable dimensional "
                "filters."
            )
            self.idim = fixed_idim
            
        # Assignments
        self.__filters = args
        self.__nfilters = len(args)

        # Get the cummulative internal and output dimension size
        for attr in ['ndim', 'odim']:
            # Get the cummulative sum of properties in filters
            cummulative_sum = np.cumsum(
                [getattr(h, attr) for h in self.__filters]
            )

            # Set the overall filter property to the final cummulative sum
            setattr(self, attr, int(cummulative_sum[-1]))

            # Gather indices for quick indexing 
            indices = list()
            for i in range(self.__nfilters):
                if i == 0:
                    indices.append(np.arange(getattr(self.__filters[i], attr)))
                else:
                    indices.append(
                        np.arange(getattr(self.__filters[i], attr))
                        + cummulative_sum[i - 1]
                    )

            # Save the indices
            setattr(self, "_ParallelFilter__{:s}_indices".format(attr), indices)

    @property
    def filters(self):
        return self.__filters
            
    @property
    def is_value_based(self):
        return self.__filters[0].is_value_based

    @property
    def is_derivative_based(self):
        return self.__filters[0].is_derivative_based
        
    def differential_equation(self, t, z, y):

        zdot = np.zeros((self.ndim,))

        for i in range(self.__nfilters):
            # Get the indices to look at internal states
            filter_simulation_index = self.__ndim_indices[i]

            # Get the individual filter state
            z_i = z[filter_simulation_index]

            # Assign individual output state
            zdot[filter_simulation_index] = (
                self.__filters[i].differential_equation(t, z_i, y)
            )

        return zdot
            
    def filter_output(self, z, y, t):

        # Initialize output vector
        output_vec = np.zeros((self.odim,))
        
        for i in range(self.__nfilters):
            # Get the indices to look at internal and output states
            filter_simulation_index = self.__ndim_indices[i]
            filter_output_index = self.__odim_indices[i]
            
            # Get the individual filter state
            z_i = z[filter_simulation_index]
            
            # Assign individual output state
            output_vec[filter_output_index] = (
                self.__filters[i].filter_output(z_i, y, t)
            )

        return output_vec

    def valid_state(self, z):
        """ Check if every filter state is valid """

        for i in range(self.__nfilters):

            # Filter state subset
            z_i = z[self.__ndim_indices[i]]

            # Return flase if filter state is invalid
            if not self.__filters[i].valid_state(z_i):
                return False

        # Return true if all filter states are valid
        return True

class CascadeFilter(Filter):
    r"""
    
    ::
                                                                                    
         y      +-----+    +-----+             +-----+                          
        ------->+ h_1 +--->+ h_2 +---> ... --->+ h_n +---> z                    
                +-----+    +-----+             +-----+                          
                                                                                
    
    """

    def __init__(self, *args):

        # Check if all inputs are filters
        assert args, "Need to specify the component filters."
        _filter_check(args)

        # Make sure all filters not the first are value based
        assert all([h.is_value_based for h in args[1:]]), (
            "Only first filter can be derivative based."
        )

        # Ensure the sequential filter blocks can be placed in a cascade
        for i in range(1, len(args)):
            h_prev_odim = args[i - 1].odim
            h_current_idim = args[i].idim
            if isinstance(h_current_idim, int):
                assert h_prev_odim is h_current_idim, (
                    "Output dimension of previous filter must match current "
                    "filter input dimension. Error at connection "
                    "{:d}.".format(i)
                )
            elif isinstance(h_current_idim, tuple):
                assert h_prev_odim in h_current_idim, (
                    "Output dimension of previous filter must be a possible "
                    "current filter input dimension. Error at connection "
                    "{:d}.".format(i)
                )
            else:
                raise ValueError("Unrecognized type for an input dimension.")
                
        # Assignments
        self.__filters = args
        self.__nfilters = len(args)
        self.idim = self.__filters[0].idim
        self.odim = self.__filters[-1].odim

        # Get the cummulative internal dimension size
        for attr in ['ndim']:
            # Get the cummulative sum of properties in filters
            cummulative_sum = np.cumsum(
                [getattr(h, attr) for h in self.__filters]
            )

            # Set the overall filter property to the final cummulative sum
            setattr(self, attr, int(cummulative_sum[-1]))

            # Gather indices for quick indexing 
            indices = list()
            for i in range(self.__nfilters):
                if i == 0:
                    indices.append(np.arange(getattr(self.__filters[i], attr)))
                else:
                    indices.append(
                        np.arange(getattr(self.__filters[i], attr))
                        + cummulative_sum[i - 1]
                    )

            # Save the indices
            setattr(self, "_CascadeFilter__{:s}_indices".format(attr), indices)

    @property
    def filters(self):
        return self.__filters
            
    @property
    def is_value_based(self):
        return self.__filters[0].is_value_based

    @property
    def is_derivative_based(self):
        return self.__filters[0].is_derivative_based
        
    def differential_equation(self, t, z, y):

        # Preallocate
        zdot = np.zeros((self.ndim,))

        # Initial filter input
        y_i = y

        for i in range(self.__nfilters):
            # Get the indices to look at internal states
            filter_simulation_index = self.__ndim_indices[i]

            # Get the individual filter state
            z_i = z[filter_simulation_index]

            # Assign individual output state
            zdot[filter_simulation_index] = (
                self.__filters[i].differential_equation(t, z_i, y_i)
            )

            # Get output of current filter as input to next filter
            y_i = self.__filters[i].filter_output(z_i, y_i, t)

        return zdot
            
    def filter_output(self, z, y, t):

        # Initial filter input
        y_i = y

        for i in range(self.__nfilters):
            # Get the indices to look at internal states
            filter_simulation_index = self.__ndim_indices[i]

            # Get the individual filter state
            z_i = z[filter_simulation_index]
            
            # Get output of current filter as input to next filter
            y_i = self.__filters[i].filter_output(z_i, y_i, t)

        return y_i

    def valid_state(self, z):

        # Check each filter
        for i in range(self.__nfilters):

            # Get filter state subset
            z_i = z[self.__ndim_indices[i]]

            # Return false if particular filter is invalid
            if not self.__filters[i].valid_state(z_i):
                return False

        # Return true as all filters are valid
        return True
