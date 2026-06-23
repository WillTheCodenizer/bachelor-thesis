"""
shot_noise.py — Shot noise contribution to the angular power spectrum.

Poisson shot noise per sample/bin is modeled as:

    N_shot = 1 / n_bar
"""

import numpy as np


def compute_shot_noise_from_counts(n_total, f_sky):
    """
    Compute shot noise from total counts and observed sky fraction.

    Parameters
    ----------
    n_total : float
        Total number of objects in the sample/bin.
    f_sky : float
        Observed sky fraction.

    Returns
    -------
    float
        Constant shot noise level for the sample/bin.
    """
    n_bar = n_total / (4.0 * np.pi * f_sky)
    return 1.0 / n_bar


def compute_shot_noise_from_density(n_bar):
    """
    Compute shot noise directly from number density n_bar.

    Parameters
    ----------
    n_bar : float
        Number density for one tomographic bin.

    Returns
    -------
    float
        Constant shot noise level for the bin.
    """
    return 1.0 / n_bar
