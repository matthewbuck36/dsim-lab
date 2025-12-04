#!/bin/user/python3
# -* coding:utf-8 *-

"""
Used to generate common helper functions for the examples.
"""

from itertools import product
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from extremum_seeking.seekers import (
    GradientFlow, HeavyBallFlow, AcceleratedGradientFlow, RMSpropFlow,
    NewtonFlow,
    DirectExtremumSeeker
)

# TODO: Add in adaptive gradient methods using spatial order in (1, 2)

# Default parameter ODEs for demonstrations
_parameter_odes = {
    GradientFlow : {
        'label' : 'GESC',
        'parameters' : ['k'],
        'theta' : ['theta_hat'],
        'spatial_order' : 1,
    },
    HeavyBallFlow : {
        'label' : 'HBESC',
        'parameters' : ['k', 'b'],
        'theta' : ['theta_hat', 'theta_hat_dot'],
        'spatial_order' : 1,
    },
    AcceleratedGradientFlow : {
        'label' : 'NesESC',
        'parameters' : ['r', 't0', 'k'],
        'theta' : ['theta_hat', 'theta_hat_dot'],
        'spatial_order' : 1,
    },
#     RMSpropFlow: {
#         'label': 'RMSpESC',
#         'parameters': ['k', 'omega_l'],
#         'theta' : ['theta_hat', 'v_hat'],
#         'spatial_order': 1,
#     },
    NewtonFlow: {
        'label': 'NESC',
        'parameters': ['k', 'omega_l', 'odim'],
        'theta': ['theta_hat', 'Gamma_hat'],
        'spatial_order': 2,
    }
}

_parameter_plot_labels = {
    'k' : '$k$',
    'b' : r'$\beta$',
    'r' : '$r$',
    't0' : '$t_0$',
    'omega_l': r'$\omega_l$',
    'odim': None
}


def simulate_direct_extremum_seeker(
        seeker, x0,
        ax=None, sim_kargs=None, plot_kargs=None
):
    r""" Simulate a direct extrema seeker
    
    Args:
        seeker (DirectExtremaSeeker): Seeker to simulate.
        t0, t1 (float): Start and stop times of the simulation.
        t_eval (np.ndarray): (N,) time vector to evaluate the simulation.
        x0 (np.ndarray): (n,) array to initialize the full system, including
                         any filter states or other hidden states.
        ax (plt.axis): Axis to plot the simulation on, otherwise None.
        \*\*kargs: Arguments for solve_ivp and plotting
    
    Returns:
        t_sim (np.ndarray): (M,) time vector of simulation where M >= N.
        theta_sim (np.ndarray): (M,m) time history of the theta values.
    """

    # Default arguments
    if sim_kargs is None:
        sim_kargs = dict()
    if plot_kargs is None:
        plot_kargs = dict()
    
    # Simulate the system
    results = solve_ivp(
        fun=seeker.differential_equation,
        y0=x0,
        **sim_kargs
    )

    # Extract the simulation results
    xh = results.y.T
    t_sim = results.t
    
    # Get the theta values from full system states
    _, theta_sim = seeker.parse_history(xh)  # Extract parameter dynamic states
    theta_sim = seeker.g.parse_history(theta_sim)[0]  # Output parameter values
    theta_sim = seeker.perturbed_parameter_history(
        t_sim, theta_sim
    )  # Perturbed paramter values
    if theta_sim.shape[1] == 1:
        theta_sim = theta_sim[:, 0]
    
    # If plotting
    if ax is not None:
        if theta_sim.ndim == 1:
            ax.plot(t_sim, theta_sim, **plot_kargs)
        else:
            # For each axis plot the ith coordinate time history
            for i, ax_i in enumerate(ax):
                ax_i.plot(t_sim, theta_sim[:, i], **plot_kargs)
        
    return t_sim, theta_sim
            

def plot_seeker_parameter_performances(
        J, h, signal_list, param_dict, theta_hat_0_dict, z_0_list,
        sim_kargs, plot_kargs=None, G_list=None, spatial_order=1, fig_list=None
):
    """ Plot seekers given list of ODE parameters
    
    Iterates over the various selected parameter signals and initial conditions
    to show the performance of the seekers over the map.

    Args:
        J (Callable): Cost function
        h (Filter): filter for derivative estimates
        signal_list (List(Tuple)): List of (perturbation, estimation) signals.
                                   The size of list determines the figures.
        param_dict (dict): Dictionary of parameters to iterate over.
                           {'param' : [values]}
        theta_hat_0_dict (dict): Dictionary of initial parameter conditions.
        z_0_dict (dict): Dictionary of initial filter conditions.
        sim_kargs (dict): Dictionary of simulation keyword arguments.
        plot_kargs (dict): Dictionary of plotting keyword arguments.
        G_list (list(ParameterUpdateODE)): List of parameter ODE Classes to 
                                           compare.
        spatial_order (int): Indicates parameter ODE's spatial order.
    
    Returns:
        fig_list (list): List of figures for the various signals.
    """
    # pylint: disable=invalid-name

    # Default arguments
    if plot_kargs is None:
        plot_kargs = dict()
    if G_list is None:
        G_list = [
            G for G in _parameter_odes
            if _parameter_odes[G]['spatial_order'] == spatial_order
        ]

    if fig_list is None:
        fig_list = [plt.figure() for _ in range(len(signal_list))]
        
    label_params_flag = (
        False if np.ndim(theta_hat_0_dict['theta_hat'][0]) > 0
        else True
    )
    
    for i, signal in enumerate(signal_list):

        ndim = np.size(signal[0](0))

        # Generate the common figure figure
        fig = fig_list[i]
        if fig.axes:
            ax = fig.get_axes()
            if ndim == 1:
                ax = ax[0]
        else:
            ax = fig.subplots(ndim, 1)

        # Get the signals for perturbation and estimation
        perturbation_signal = signal[0]
        h.filters[1].f = signal[1]

        for z_0 in z_0_list:
            for G in G_list:

                # Plot label
                G_label = _parameter_odes[G]['label']

                # Get the parameters for parameter update ODE
                parameter_labels = _parameter_odes[G]['parameters']
                parameter_list = [x for x in product(*[
                    param_dict[key] for key in parameter_labels
                    if key in param_dict.keys()
                ])]
                parameter_labels = [
                    key for key in parameter_labels if key in param_dict.keys()
                ]
                parameter_plot_label = "(" + ",".join(
                    _parameter_plot_labels[p] for p in parameter_labels if
                    _parameter_plot_labels[p]
                ) + ")"
                
                for parameters in parameter_list:
                    g = G(**dict(zip(parameter_labels, parameters)))

                    if label_params_flag:
                        plot_kargs['label'] = G_label + ', {} = {}'.format(
                            parameter_plot_label,
                            "(" + ",".join([
                                str(x) for x, p
                                in zip(parameters, parameter_labels)
                                if _parameter_plot_labels[p]
                            ]) + ")"
                        )
                    else:
                        plot_kargs['label'] = G_label
                        
                    # Get the initial conditions
                    theta_segments = _parameter_odes[G]['theta']
                    theta_0_list = [x for x in product(*[
                        theta_hat_0_dict[key] for key in theta_segments
                    ])]
                    theta_0_list = [
                        g.initialize_system(*t) for t in theta_0_list
                    ]

                    # Iterate through parameter initial conditions
                    for theta_0 in theta_0_list:

                        seeker = DirectExtremumSeeker(
                            g, h, J, perturbation_signal
                        )
                        x_0 = seeker.initialize_system(z_0, theta_0)

                        _ = simulate_direct_extremum_seeker(
                            seeker, x_0,
                            ax=ax, sim_kargs=sim_kargs, plot_kargs=plot_kargs
                        )
    return fig_list

def generate_sinusoidal_dither_signals(a, omega, spatial_order=1):
    r""" Generates the sinusoidal perturbation and estimation signals 
    
    .. math::
    
        p(t) = a \sin(\omega t)
        e(t) = 2 \sin(\omega t)/a
    
    Args:
        a (float or np.ndarray): signal amplitude
        omega (float or np.ndarray): signal rate
    """
    perturbation_signal = lambda t: a*np.sin(omega*t)
    perturbation_signal.derivative = (
        lambda t: a*omega*np.cos(omega*t)
    )


    # TODO: Add in spatial orders for adaptive gradient methods

    if spatial_order == 1:
        estimation_signal = lambda t: 2.*np.sin(omega*t)/a
    elif spatial_order == 2:
        
        # Gradient estimator
        m = lambda t: 2.*np.sin(omega*t)/a

        # Hessian estimator
        if np.size(a) == 1:
            N = ( # pylint: disable=invalid-name
                lambda t: 16.*(np.sin(omega*t)**2 - 0.5)/(a*a)
            ) 
        else:
            a_inv = 1./a
            def N(t):
                # pylint: disable=invalid-name
                sin_over_a = np.sin(omega*t)/a
                est_sig_val = (
                    4*np.outer(sin_over_a, sin_over_a)
                    + 12.*np.diag(sin_over_a**2)
                    - 8*np.diag(a_inv*a_inv)
                )
                return est_sig_val.flatten()

        # Combined estimation signal
        estimation_signal = lambda t: np.hstack((m(t), N(t)))

    return (perturbation_signal, estimation_signal)
    
def generate_signal_perturbations(a_list, omega_list, spatial_order=1):
    """ Generates permutations of perturbation and estimation signals.
    
    Args:
        a_list (Iterable): Sinusoidal dither amplitudes.
        omega_list (Iterable): Sinusoidal dither rates.
    
    Returns:
        signal_list (list): List of (perturbation, estimation) signals.
    """

    a_omega_list = product(a_list, omega_list)
    return [
        generate_sinusoidal_dither_signals(
            *a_omega, spatial_order=spatial_order
        )
        for a_omega in a_omega_list
    ]
