#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

r'''
Title:
    Estimate derivatives with perturbations

Date(Last updated):
    02-07-2025
    05-26-2025 -- Patrick McNamee

Author: 
    Dylan James-Kavanaugh

Description:
    This script enables the user to test out different perturbation sigals and 
    check whether they can be used to determine derivatives fo a cost function
    up to a specified order. By using this class, one can determine the effect
    of the perturbations on higher order derivative terms and determine if, in
    the average derivative estimate, one can distinguish between the
    derivatives. 

.. [kavanaugh-2025] Dylan James-Kavanaugh, Patrick McNamee, Qixu Wan, and Zahra 
    Nili Ahmadabadi, "A Further Unifying Derivative Estimation Scheme for 
    Extremum Seeking Control", 2025

'''

import itertools
import numpy as np
from scipy.special import comb, factorial
import sympy

class PerturbationDerivativeEstimation:
    r''' Handles the calculations of perturbation signals and estimators.
    
    For extremum seeking, one is concerned with finding the derivatives of the
    cost function :math:`J:\mathbb{R}^n\to\mathbb{R}` in a model-free way. The
    derivatives up to the :math:`m` -th order can be estimated around an estimate
    of the optimal parameter :math:`\hat{\theta}` using a time-varying perturbed
    cost function output and a time-varying estimation signal as in
    
    .. math::
    
        \hat{\xi}(\omega t, \hat{\theta}, a) = h(\omega t, a)\cdot J(
        \hat{\theta} + a\cdot p(\omega t))
    
    where :math:`\hat{\xi}\in\mathbb{R}^o` is an estimate of the various 
    derivatives of :math:`J` at :math:`\hat{\theta}` stored in a vector 
    :math:`\xi`, :math:`p:\mathbb{R}\to\mathbb{R}^n` is a periodic (for this 
    package) perturbation signal scaled by a small parameter :math:`a` and speed
    up by a large parameter  :math:`\omega`, and :math:`h:\mathbb{R}\times
    \mathbb{R}\to\mathbb{R}^o` is the signal used to estimate the derivatives 
    from the output. Note that we do not expect that :math:`\hat{\xi}` to be 
    close to the derivatives of :math:`J` but rather the averaged estimate

    .. math::
    
        \hat{\bar{\xi}}(\hat{\bar{\theta}}, a) = \lim_{T\to\infty} \frac{1}{T}
        \int_{0}^T \hat{\xi}(\tau, \hat{\bar{\theta}}, a) d\tau

    converges to the true derivative vector as :math:`a\to 0`. To accomplish
    this, we construct :math:`h` based on an order :math:`m` polynomial cost 
    function, which in multiindex notation, is
    
    .. math::
    
        J(\theta - \hat{\theta}) = \sum_{\vert \alpha \vert \leq m} 
        \frac{1}{\alpha!} D^{\alpha}J(\hat{\theta})
        (\theta - \hat{\theta})^{\alpha}

    with :math:`\alpha` being a `multiindex`_ and :math:`D^{\alpha}` being a 
    short hand for the derivative :math:`\left(\frac{\partial}
    {\partial\theta_1}\right)^{\alpha_1}\cdots\left(\frac{\partial}
    {\partial\theta_1}\right)^{\alpha_n}` . For simplicity, we can
    rearrange this summation into a linear algebra problem with

    .. math::
    
        J(\hat{\theta} + a\cdot p(\tau)) = J(\hat{\theta}) + \rho(\tau)^T A 
        \xi(\hat{\theta})
    
    with :math:`\rho(\tau)` being a vector to track all the 
    :math:`p(\tau)^{\alpha}` and :math:`A` is a diagonal matrix that 
    accounts for :math:`a^{\vert \alpha \vert}/\alpha!` for all derivatives 
    with an order of at least 1. We call :math:`\rho` the extended 
    perturbation signal, :math:`\bar{\rho}` is average value, and 
    :math:`\tilde{\rho}` is deviation from the mean. The crux of  knowing if an
    :math:`h` exists is if one must show that :math:`\tilde{\rho}` is a vector 
    of linearly independent signals which is equivalent to the check of the 
    covariance matrix
    
    .. math::
    
        Q := \lim_{T\to\infty} \frac{1}{T}\int_{0}^\tau \tilde{\rho}(\tau) 
        \tilde{\rho}(\tau)^T d\tau
    
    being a positive definite matrix. One solution for :math:`h` is with the 
    covariance matrix as
    
    .. math::
    
        h_Q(\tau, a) = A^{-1} Q^{-1} \tilde{\rho}(\tau)
    
    although the solution is nonunique. If one had another vector of zero-mean
    signals :math:`r:\mathbb{R}\to\mathbb{R}^o` , the crossvariance
    
    .. math::
    
        R := \lim_{T\to\infty} \frac{1}{T}\int_{0}^\tau r(\tau) 
        \tilde{\rho}(\tau)^T d\tau
    
    is used to construct the solution
    
    .. math::
    
        h_R(\tau, a) = A^{-1} R^{-1} r(\tau)

    For historical reasons, it possible to use signals that are not zero-mean.
    This can be included by setting the `zero_mean` keyword argument to `False`
    when intializing the class object. In this case, we do keep track of all
    vectors and matrices but this time with the 0th order derivative as well.

    .. _multiindex: https://en.wikipedia.org/wiki/Multi-index_notation
    '''

    @property
    def perturbations(self):
        r""" List of base perturbation signals :math:`p` ."""
        return self.__perturbations

    @perturbations.setter
    def perturbations(self, val):

        # Check validity of input value
        assert isinstance(val, list), (
            "Perturbation vector must be a list of sympy expressions."
        )
        assert all([isinstance(v, sympy.Expr) for v in val]), (
            "All elements in the perturbation vector must be a sympy "
            "expression."
        )
        assert len(val) == self.n, (
            "Perturbation signals must match input length."
        )

        # Update the perturbations
        self.__perturbations = val

        # Reset the necessary cached values
        self.m_max = 0

    @property
    def m_max(self):
        r""" Maximum derivative order of the multiindex set which was 
        calculated. The current multiindex set :math:`\mathcal{A}` will satisfy
        :math:`\vert \alpha \vert \leq m_{\max}` for all :math:`\alpha\in
        \mathcal{A}` .
        """
        return self.__m_max

    @m_max.setter
    def m_max(self, val):

        # Validate input
        assert isinstance(val, int) and val > -1, ""

        # Check to see if we have to generate a new set
        if val > self.__m_max:
            # We have exceeded how much we previously cached and now must
            # generate a new set.
            multiindex_set = self.multiindex_set  # Temporary variable

            # Add in the bias term if zero mean siganls are not enforced
            # and bias term currently not accounted for
            if (
                    (self.__m_max == 0)
                    and (not self._is_zero_mean)
                    and (np.shape(multiindex_set)[0] == 0)
            ):
                multiindex_set = np.zeros((1, self.n), dtype=np.int64)

            # Iterate through the orders that we have not generated
            for alpha_order in range(self.m_max + 1, val + 1):
                # Get the set at this particular order
                multiindex_set_of_order = np.array(sorted(
                    [
                        expr for expr in itertools.product(
                            range(alpha_order + 1), repeat=self.n
                        ) if sum(expr) == alpha_order
                    ], reverse=True
                ), dtype=np.int64)
                
                # Append the results
                multiindex_set = np.vstack((
                    multiindex_set, multiindex_set_of_order
                ))

            # Save the results
            self.__m_max = val
            self.multiindex_set = multiindex_set
            
        # Check for eliminations
        elif val < self.__m_max:
            self.__m_max = val
            for prop in [
                    'multiindex_set',
                    'extended_perturbations',
                    'extended_perturbation_averages',
                    'extended_perturbation_deviations'
                ]:

                if hasattr(self, prop):
                    if self._is_zero_mean:
                        i = (
                            self._upper_index_of_derivative_order(val)
                            if (val > 0) else -1
                        )
                    else:
                        i = self._upper_index_of_derivative_order(val)
                        
                    attr = getattr(self, prop)
                    i = min(i, np.shape(attr)[0])
                    setattr(self, prop, attr[:i+1, :])

            if hasattr(self, 'covariance_matrix'):
                setattr(
                    self, 'covariance_matrix', getattr(
                        self, 'covariance_matrix'
                    )[:i+1, :i+1]
                )

    @property
    def multiindex_set(self):
        r""" The ordered set of multiindices of the derivatives.
        
        This property is the ordered set :math:`\mathcal{A}` which contains the
        all the multiindices :math:`\alpha` in a `numpy.ndarray` . The ordering
        is so that the :math:`i` -th and :math:`j` -th elements of 
        :math:`\mathcal{A}` satisfy :math:`\vert \alpha_i \vert \leq \alpha_j
        \vert` for all :math:`i< j` . The first index represents the order and
        the second represents the individual elements of :math:`\alpha_i`.
        """

        # Return the multiindex set
        return self.__multiindex_set

    @multiindex_set.setter
    def multiindex_set(self, val):

        # Check value
        assert isinstance(val, np.ndarray), (
            "Multiindex set must be a numpy array."
        )
        assert len(np.shape(val)) == 2, "Multiindex set must be a 2D array."
        assert np.shape(val)[1] == self.n, (
            "2nd dimension must match input dimension for cost function."
        )
        assert np.shape(val)[0] == int(np.sum([
            comb(self.n, k, repetition=True) for k in range(
                1 if self._is_zero_mean else 0, self.m_max + 1
            )
        ])), "1st dimension must match total number of derivatives."
        assert np.all(val >= 0), "Entries must be strictly nonnegative."
        if self._is_zero_mean:
            assert np.all(np.sum(val, axis=1) > 0), (
                "Orders must be strictly positive."
            )

        self.__multiindex_set = val

    def __init__(self, n, p, T, t, zero_mean=True):
        '''
        Initialization of the class object
        
        Args:
        
            n: dimensions of the perturbations
            p: perturbation signals as a list of sympy functions
            T: common period of perturbation signals for integration
            t: symbol for the time

        Returns:
            Initialized object contiaining the dimensions
        '''

        # Check the given dimension
        assert isinstance(n, int) and n > 0, (
            "Input dimension n must be a strictly nonnegative integer."
        )
        self.n = n  # number of input dimensions

        # Assign the perturbation list
        
        
        # Check the given period
        assert isinstance(T, (int, float, sympy.Expr)), (
            'Expected T to be a float, integer, or sympy expression.'
        )
        if isinstance(T, (int, float)):
            assert T > 0, "Period must be a positive number."
        else:
            assert T.evalf() > 0, "Period must be a positive number."
            
        self.period = T
        
        # Lastly, keep track of time for later integrations.
        self.t = t

        # Added stuff for caching/memoization
        self.__m_max = 0
        self.__multiindex_set = np.empty((0, n), dtype=np.int64)
        self.perturbations = p
        self.extended_perturbations = sympy.Matrix(0, 0, [])
        self.extended_perturbation_averages = sympy.Matrix(0, 0, [])
        self.extended_perturbation_deviations = sympy.Matrix(0, 0, [])
        self.covariance_matrix = sympy.Matrix(0, 0, [])
        self._is_zero_mean = zero_mean

    def derivative_order(self):
        r""" Gives the derivative order of each multiindex i.e. :math:`\vert 
        \alpha \vert` for every multiindex being tracked.
        """
        
        return np.sum(self.multiindex_set, axis=1, dtype=np.int64)

    def multiindex_factorial(self):
        r""" Returns the multiindex factorial :math:`\alpha!` for all 
        multiindices being tracked.
        """
        
        return np.prod(
            factorial(self.multiindex_set), axis=1, dtype=np.int64
        )

    def _highest_order_calculated(self, prop):
        """ Determines the highest order calculated for cached results. """
        if hasattr(self, prop):
            attr = getattr(self, prop)
            if attr.shape[0] == 0:
                return -1
            else:
                return self.derivative_order()[attr.shape[0] - 1]
        else:
            return -1

    def _upper_index_of_derivative_order(self, m):
        """ Returns the largest index of an alpha with rank m. """
        assert isinstance(m, int) and m >= 0, (
            "Indexed orders are integers from 0."
        )
        current_derivative_order = self.derivative_order()
        index = np.arange(len(current_derivative_order))[
            self.derivative_order() <= m
        ][-1]
        return index

    def _order_check(self, m):
        """ Checks if m > 0 and m is an integer """
        assert m > 0 and isinstance(m, int), (
            f'Expected m ({m}) to be an integer greater than 0'
        )

    def _additional_multiindex_terms_to_calculate(
            self, m, highest_order_calculated
    ):
        """ Returns the additional multiindexes that need to be calculated based
        on the requested order and current highest order calculated.
        """
        
        # See if more terms are needed to be calculated
        if m > self.m_max:
            # Required to extend the largest order we considered.
            self.m_max = m
        # Get the additional terms above the highest calculated order
        multiindex_new_terms = self.multiindex_set[
            self.derivative_order() > highest_order_calculated
        ]
        return multiindex_new_terms
        
    def calculate_extended_perturbations(self, m):
        r""" Calculates the extended perturbation vector up to order m.
        
        The extended perturbation is defined as a vector with the elements
        
        .. math::
        
            \rho(\tau)_i = p(\tau)^{\alpha_i},\ i=1,2,\ldots \vert \mathcal{A} 
            \vert

        for the ordered set of :math:`\mathcal{A}` , which contains all the
        multiindices of interest.
        
        Args:
        
            m (int): maximum derivative order to calculate

        Returns: 
        
            A sympy vector of the extended perturbations.
        """
        # Input check
        self._order_check(m)
        
        # Check if we have cached results up to this order.
        # If not, see the highest calculated
        highest_order_calculated = self._highest_order_calculated(
            'extended_perturbations'
        )
        if m <= highest_order_calculated:
            # We have calculated the results
            i = self._upper_index_of_derivative_order(m)
            return self.extended_perturbations[:i+1]

        # Get the new terms to calculate
        multiindex_new_terms = self._additional_multiindex_terms_to_calculate(
            m, highest_order_calculated
        )
        
        # Create list to store terms
        additional_extended_perturbations = list()

        # Iterate through the new terms
        for alpha in multiindex_new_terms:
            p_alpha = sympy.prod([
                p_i**alpha_i for p_i, alpha_i in zip(self.perturbations, alpha)
            ])
            additional_extended_perturbations.append(p_alpha)
        
        # Generate a new extended dither signal
        if hasattr(self, 'extended_perturbations'):
            # new terms to existing list
            rho = (
                list(self.extended_perturbations)
                + additional_extended_perturbations
            )
        else:
            # There has been no extended perturbation signals calculated
            rho = additional_extended_perturbations

        # Construct the dither signal as a vector
        rho = sympy.Matrix(len(rho), 1, rho)

        # Return the extended perturbation signals
        self.extended_perturbations = rho
        return rho

    def calculate_extended_perturbation_averages(self, m):
        r""" Determines the average value of the extended perturbations.
        
        The average extended perturbations as defined as
        
        .. math::
        
            \bar{\rho} = \lim_{T\to\infty}\frac{1}{T}\int_{0}^{T} \rho(\tau) 
            d\tau
        
        Args:
            m (int): the maximum order of the derivatives being considered.

        Returns:
            the averages of the extended perturbation signal vector up to order
            :math:`m` .
        """

        # Input check
        self._order_check(m)

        # Check if we have cached results up to this order.
        # If not, see the highest calculated
        highest_order_calculated = self._highest_order_calculated(
            'extended_perturbation_averages'
        )
        if m <= highest_order_calculated:
            # We have calculated the results
            i = self._upper_index_of_derivative_order(m)
            return self.extended_perturbation_averages[:i+1]

        # Get previous solution if it exists
        if highest_order_calculated > 0:
            previous_averages = self.extended_perturbation_averages
        
        # Generate higher-order perturbation terms
        rho = self.calculate_extended_perturbations(m)
        if isinstance(rho, list):
            rho = sympy.Matrix(len(rho), 1, rho)
        
        # Preallocate new solution
        extended_perturbation_averages = sympy.Matrix(
            len(rho), 1, [0 for _ in range(np.size(rho))]
        )
        
        # Determine what orders the indexes belong to
        derivative_order_index = self.derivative_order()

        # Iterate over the derivative orders
        for i in range(rho.shape[0]):
            if derivative_order_index[i] <= highest_order_calculated:
                # Use the previously calculated if it exists
                extended_perturbation_averages[i] = previous_averages[i]
            else:
                # Do not have the current average, calculate it
                extended_perturbation_averages[i] = sympy.integrate(
                    rho[i], (self.t, 0, self.period)
                )/self.period
                extended_perturbation_averages[i] = (
                    extended_perturbation_averages[i].simplify()
                )

        # Store the solution and return it
        self.extended_perturbation_averages = extended_perturbation_averages

        # Return the deviation of the extended dither signal from its mean.
        return extended_perturbation_averages

    def calculate_extended_perturbation_deviations(self, m):
        r""" Calculates the deviation of the extended perturbation from the 
        average as :math:`\tilde{\rho}(\tau) = \rho(\tau) - \bar{\rho}` .
        
        Args:
            m: is the maximum order of the derivatives being estimated.

        Returns:
            Deviation of extended perturbation signal vector from the average.
        """

        # Input check
        self._order_check(m)

        # Check if we have cached results up to this order.
        # If not, see the highest calculated
        highest_order_calculated = self._highest_order_calculated(
            'extended_perturbation_deviations'
        )
        if m <= highest_order_calculated:
            # We have calculated the results
            i = self._upper_index_of_derivative_order(m)
            return self.extended_perturbation_deviations[:i+1]
        
        # Generate higher-order perturbation terms and deviations
        rho = self.calculate_extended_perturbations(m)
        if isinstance(rho, list):
            rho = sympy.Matrix(
                len(rho), 1, rho
            )
        rho_bar = (
            self.calculate_extended_perturbation_averages(m)
        )
        if isinstance(rho_bar, list):
            rho_bar = sympy.Matrix(len(rho_bar), 1, rho_bar)
        
        # Preallocate new solution
        extended_perturbation_deviations = sympy.Matrix(
            len(rho_bar), 1, [0 for _ in range(np.size(rho_bar))]
        )
        
        # Determine what orders the indexes belong to
        derivative_order_index = self.derivative_order()[
            :(1 + self._upper_index_of_derivative_order(m))
        ]
        
        # Iterate over the derivative orders
        for i in range(rho.shape[0]):
            if derivative_order_index[i] <= highest_order_calculated:
                # Use the previously calculated if it exists
                extended_perturbation_deviations[i] = (
                    self.extended_perturbation_deviations[i]
                )
            else:
                if derivative_order_index[i] > 0:
                    # Do not have the current average, calculate it
                    extended_perturbation_deviations[i] = (
                        rho[i] - rho_bar[i]
                    ).simplify()
                else:
                    # For a non-zero mean case, we will say that this
                    # is 1 to simply be able to calculate the result
                    extended_perturbation_deviations[i] = 1

        # Store the solution and return it
        self.extended_perturbation_deviations = extended_perturbation_deviations

        # Return the deviation of the extended dither signal from its mean.
        return extended_perturbation_deviations
    
    def calculate_covariance_matrix(self, m):
        r''' Calculates the covariance matrix of the perturbation signals.
        
        Function to calculate  the covariance matrix :math:`Q` and determines 
        whether the matrix is invertible. If it is invertible then the 
        demodulation signal :math:`h(t,a)` signal exists.
        
        Args:
            m: maximum order of derivatives being considered.
        
        Return:
            covariance_matrix: the covariance matrix of the extended 
                perturbations as a square `sympy.Matrix` .
        
            is_invertible: boolean value of whether the :math:`Q` is invertible
        
        '''

        # Check the order
        self._order_check(m)

        # Determine the highest order calculated
        highest_order_calculated = self._highest_order_calculated(
            'covariance_matrix'
        )

        if m <= highest_order_calculated:
            i = self._upper_index_of_derivative_order(m)
            covariance_matrix = self.covariance_matrix[:i+1, :i+1]
            is_invertible = (
                covariance_matrix.rank() == covariance_matrix.shape[0]
            )
            return covariance_matrix, is_invertible
        
        # Previous solution if it exists
        if highest_order_calculated > 0:
            previous_covariance_matrix = self.covariance_matrix

        # Get the signal basis for the covariance matrix
        if self._is_zero_mean:
            
            # Basis set is the the deviations from the mean
            basis_signals = (
                self.calculate_extended_perturbation_deviations(m)
            )

        else:

            # Basis set are the signals themselves
            basis_signals = (
                self.calculate_extended_perturbations(m)
            )

            # Get the average values for fast calculations
            rho_bar = self.calculate_extended_perturbation_averages(m)

        # Preallocate the solution
        length_of_basis = np.size(basis_signals)
        covariance_matrix = sympy.Matrix(
            length_of_basis, length_of_basis,
            [0 for _ in range(length_of_basis**2)]
        )
        
        # nested loop through the rows and columns of the Q matrix to get the
        # covariance of the signals.
        derivative_orders = self.derivative_order()
        start_index = 0 if self._is_zero_mean else 1
        for row in range(start_index, length_of_basis):
            for col in range(start_index, length_of_basis):
                if (
                        (derivative_orders[row] <= highest_order_calculated)
                        and (derivative_orders[col] <= highest_order_calculated)
                ):
                    # Previous solution
                    covariance_matrix[row, col] = (
                        previous_covariance_matrix[row, col]
                    )
                elif row > col:
                    # Symmetry of already calculated solution
                    covariance_matrix[row, col] = covariance_matrix[col, row]
                else:
                    # Calculate the solution
                    covariance_matrix[row, col] = sympy.integrate(
                        (
                            basis_signals[row]*basis_signals[col]
                        ),
                        (self.t, 0, self.period)
                    )/self.period
                    covariance_matrix[row, col] = (
                        covariance_matrix[row, col].simplify()
                    )

        if not self._is_zero_mean:

            # Need to add in the averages
            for i in range(length_of_basis):
                if i == 0:
                    covariance_matrix[0, 0] = rho_bar[0]  # Should be 1
                else:
                    covariance_matrix[i, 0] = rho_bar[i]
                    covariance_matrix[0, i] = rho_bar[i]

        # Check if the matrix is invertible
        is_invertible = (covariance_matrix.rank() == length_of_basis)

        # Save and return results
        self.covariance_matrix = covariance_matrix
            
        return covariance_matrix, is_invertible
    
    def calculate_crossvariance_matrix(self, m, r):
        r'''
        Generate the crossvariance :math:`R` based on the users input choice 
        of periodic signals. They should have a common period with the 
        perturbations :math:`p` .
        
        Args:
            m: maximum order of derivatives being considered.
            r: list of m zero-mean signals for derivative estimation

        Returns:
            R: the crossvariance matrix between signals
            is_invertible: boolean on if :math:`R` is invertible.
        '''

        # Check inputs
        self._order_check(m)
        assert isinstance(r, list), "Must provide a list of signals."
        assert all([isinstance(r_i, sympy.Expr) for r_i in r]), (
            "r must a list of sympy expressions."
        )
        if self._is_zero_mean:
            assert all([self.t in r_i.free_symbols for r_i in r]), (
                "All r elements must be a function of the time variable."
            )
            for r_i in r:
                integral_of_r_i = sympy.Integral(r_i, (self.t, 0, self.period))
                print(integral_of_r_i)
                assert integral_of_r_i.evalf() == 0, (
                    "The signal " + str(r_i) + " needs to be zero-mean on the "
                    "periodic interval. " + str(
                        sympy.Integral(r_i, (self.t, 0, self.period))
                    ) + " is not 0."
                )
        
        # Get the extended perturbations
        rho = (
            self.calculate_extended_perturbations(m)
        )

        # Check matching size
        assert len(r) == np.size(rho), (
            "r must the same length as the extended perturbation signals."
        )
        
        crossvariance = (
            sympy.Matrix(len(r), len(r), [0 for _ in range(len(r)**2)])
        )
        for i in range(len(r)):
            for j in range(len(r)):

                # Do the integration
                crossvariance[i, j] = sympy.simplify(
                    sympy.integrate(
                        r[i]*rho[j],
                        (self.t, 0, self.period)
                    )/self.period
                )
                
                # Simplify the result
                crossvariance[i, j] = crossvariance[i, j].simplify()

        # Return the results
        is_invertible = (crossvariance.rank() == crossvariance.shape[0])
            
        return crossvariance, is_invertible

    def calculate_coefficient_matrix(self, m, scaling_factor=None):
        r""" Calculates the coefficient matrix :math:`A` .

        The coefficient matrix :math:`A` is a diagonal matrix with the diagonal
        elements :math:`A_{ii} = a^{\vert \alpha_i \vert} / \alpha_{i}!`
        corresponding to the :math:`i` -th element of the ordered multiindex set
        :math:`\mathcal{A}` .
        
        Args:
            m (int): order of the estimation.
            scaling_factor (Sympy.Expr or None): Factor for scaling based on
                the perturbation input scalaing. Defaults to :math:`a` .
        """

        # Input check
        self._order_check(m)

        if scaling_factor is None:
            scaling_factor = sympy.symbols('a')
        assert isinstance(scaling_factor, sympy.Expr), (
            "Scaling factor must be symbolic."
        )

        self.m_max = max(m, self.m_max)  # Increase multiindex set as necessary

        i = self._upper_index_of_derivative_order(m)  # maximum index
        
        derivative_powers = self.derivative_order()[:i+1]
        multiindex_factorials = self.multiindex_factorial()[:i+1]

        coefficient_list = [
            (scaling_factor**p)/c for c, p
            in zip(multiindex_factorials, derivative_powers)
        ]

        return sympy.diag(*coefficient_list)

    def calculate_h_covariance(self, m, scaling_factor=None):
        r""" Generates the derivative estimation signal from covariance matrix.
        
        .. math::
        
            h_Q(\tau, a) = A^{-1}(a) Q^{-1} \tilde{\rho}(\tau)
        
        Args:
            m (int): maximum derivative order beging condiered.
            scaling_factor (sympy.Expr or None): Factor for scaling based on the
                perturbation amplitude. Default is :math:`a` .
        
        Returns:
            :math:`h_Q(\tau, a)` if it exists.
        
        Raises:
            `ValueError` if :math:`Q` was not invertible for the calculated
            maximum derivative order.
            
        """

        # Check inputs
        self._order_check(m)

        if scaling_factor is None:
            scaling_factor = sympy.symbols('a')
        assert isinstance(scaling_factor, sympy.Expr), (
            "Scaling factor must be symbolic."
        )

        # Check if forming the estimation signal off of the extended
        # perturbations or off of the extended perturbation deviations
        if self._is_zero_mean:
            # deviation case
            
            # Get the deviation signals
            extended_perturbation_deviations = (
                self.calculate_extended_perturbation_deviations(m)
            )
            if isinstance(extended_perturbation_deviations, list):
                # Ensure result is a vector
                extended_perturbation_deviations = sympy.Matrix(
                    len(extended_perturbation_deviations), 1,
                    extended_perturbation_deviations
                )
                
        else:
            # original signal case:

            # Get the extended perturbations
            extended_perturbations = (
                self.calculate_extended_perturbations(m)
            )
            if isinstance(extended_perturbations, list):
                # Ensure result is a vector
                extended_perturbations = sympy.Matrix(
                    len(extended_perturbations), 1,
                    extended_perturbations
                )
            
        # Find the crossvariance matrix
        covariance_matrix, is_invertible = self.calculate_covariance_matrix(m)

        # Return the solution if it exists
        if is_invertible:

            # Get index for trimming
            i = self._upper_index_of_derivative_order(m)
            
            # Get the coefficient matrix
            coefficient_matrix = self.calculate_coefficient_matrix(
                m, scaling_factor=scaling_factor
            )

            # Calculate the solution
            h_covariance = (
                coefficient_matrix.inv()
                @ covariance_matrix.inv()
                @ (
                    extended_perturbation_deviations[:i+1, 0]
                    if self._is_zero_mean else
                    extended_perturbations[:i+1, 0]
                )
            )

            # Simplify the solution
            for i in range(h_covariance.shape[0]):
                h_covariance[i] = h_covariance[i].simplify()

            # Return the solution
            return h_covariance
        
        else:
            raise ValueError("Covariance matrix is not invertible")

    def calculate_h_crossvariance(self, m, r, scaling_factor=None):
        r""" Generates the derivative estimation signal from a crossvariance 
        matrix.
        
        .. math::
        
            h_R(\tau, a) = A^{-1}(a) R^{-1} r(\tau)
        
        Args:
            m (int): maximum derivative order beging condiered.
            r (list[sympy.Expr]): list of (ideally) zero-mean signals with the
                length as :math:`\tilde{\rho}`
            scaling_factor (sympy.Expr or None): Factor for scaling based on the
                perturbation amplitude. Default is :math:`a` .
        
        Returns:
            :math:`h_R(\tau, a)` if it exists.
        
        Raises:
            ValueError` if :math:`R` was not invertible for the calculated
            maximum derivative order.
            
        """

        self._order_check(m)
        
        crossvariance_matrix, is_invertible = (
            self.calculate_crossvariance_matrix(m, r)
        )

        if scaling_factor is None:
            scaling_factor = sympy.symbols('a')
        assert isinstance(scaling_factor, sympy.Expr), (
            "Scaling factor must be symbolic."
        )

        if is_invertible:

            # make r a vector
            r_vec = sympy.Matrix(len(r), 1, r)

            # Get index for trimming
            i = self._upper_index_of_derivative_order(m)

            # Get the coefficients
            coefficient_matrix = self.calculate_coefficient_matrix(
                m, scaling_factor=scaling_factor
            )[:i+1, :i+1]

            # Return solutions
            return (
                coefficient_matrix.inv()
                @ crossvariance_matrix.inv()
                @ r_vec
            )
        else:
            raise ValueError("Covariance matrix is not invertible")

