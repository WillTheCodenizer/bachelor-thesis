"""
shot_noise.py — Shot noise contribution to the angular power spectrum.

The shot noise for a single tomographic bin (n_tomo = red shift bin) is:

    N_shot = n_tomo * <sigma_host^2> / n_bar

where
    sigma_host(z)   = sigma_host_0 * (1 + z)^(-1)
    <sigma_host^2>  = integral of n(z) * sigma_host(z)^2 dz
    n_bar           = N_total / (4 * pi * f_sky)      [sr^-1]

The scatter sigma_host is treated as a dimensionless noise amplitude
(not a physical distance) following the project specification.
"""

import numpy as np
from scipy.integrate import trapezoid

from config.parameters import (
    Z_ARR, F_SKY, SIGMA_HOST_0, N_TOMO,
)
from src.distributions import n_z


def compute_shot_noise(alpha, N_total):
    """
    Compute the shot noise level N_shot for a given survey.

    Parameters
    ----------
    alpha : float
        Steepness parameter of the FRB redshift distribution.
    N_total : float
        Total number of detected FRBs in the survey.

    Returns
    -------
    N_shot : float
        Constant shot noise that is added to every C(ell).
    """
    # Normalised redshift distribution
    nz = n_z(Z_ARR, alpha)

    # Mean source density on the sky [sr^-1]
    n_bar = N_total / (4.0 * np.pi * F_SKY)

    # Shot noise for n_tomo tomographic bins
    N_shot = 1 / n_bar

    return N_shot
