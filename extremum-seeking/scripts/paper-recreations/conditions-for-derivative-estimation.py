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

from extremum_seeking.averaging import PerturbationDerivativeEstimation
import sympy

if __name__ == '__main__':

    # Preallocate the information estimation
    period = 2  # the period of the periodic signal
    dimensions = 2  # number of dimensions for the cost function
    order = 2  # order of derivatives to calculate

    # Construct the dither signal in the 2D plane.
    dither_amplitude = sympy.symbols('a')  # the dither amplitude
    time = sympy.symbols('t')  # time symbol

    # setup a piecewise function over time to represent the continuous
    # movement of the rotating sensor
    phi = sympy.Piecewise(
        (-sympy.pi/2 + sympy.pi*time, time < 1),
        (sympy.pi/2 - sympy.pi*(time - 1), True)
    )

    # define the variables
    x = sympy.cos(phi)  # normalized signal
    y = sympy.sin(phi)  # normalized signal
    r_x = sympy.cos(2*sympy.pi*time)
    r_y = sympy.cos(sympy.pi*time)
    
    # Define perturbations in the system for the x and y dimensions
    sensor_perturbations = [x, y]
    
    # define the estimator
    estimator = PerturbationDerivativeEstimation(
        dimensions,
        sensor_perturbations,
        period,
        time
    )

    # Covariance for the 2nd order derivatives
    covariance, is_invertible = estimator.calculate_covariance_matrix(2)
    print("Second order covariance matrix:")
    print(covariance)
    if is_invertible:
        print("\tMatrix is invertible.")
    else:
        print("\tMatrix is not invertible.")

    # Determining the estimation signals
    h_covariance = estimator.calculate_h_covariance(
        1, scaling_factor=dither_amplitude
    )
    h_crossvariance = estimator.calculate_h_crossvariance(
        1, [r_x, r_y], scaling_factor=dither_amplitude
    )

    print("Covariance-based estimation signal:")
    print(h_covariance)

    print("\nCrossvariance-based estimation signal:")
    print(h_crossvariance)
