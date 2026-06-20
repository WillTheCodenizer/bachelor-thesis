"""
shot_noise.py — Shot noise contribution to the angular power spectrum.

The current model uses Poisson shot noise per sample/bin:

    N_shot = 1 / n_bar

where
    n_bar = N_total / (4 * pi * f_sky)  [sr^-1]
"""

import numpy as np


def compute_shot_noise_from_counts(n_total, f_sky):
    """
    Compute shot noise from the total object count of one sample/bin.

    Parameters
    ----------
    n_total : float
        Total number of objects in the sample/bin.
    f_sky : float, optional
        Observed sky fraction. Default is F_SKY.

    Returns
    -------
    float
        Constant shot noise level for the sample/bin.
    """
    n_bar = n_total / (4.0 * np.pi * f_sky)
    return 1.0 / n_bar
