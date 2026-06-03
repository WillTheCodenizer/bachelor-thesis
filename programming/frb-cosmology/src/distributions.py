"""
distributions.py — FRB redshift distribution, bias model, and weight function.

Defines:
  n(z)  — normalised redshift distribution of FRBs
  b(z)  — linear bias of the FRB host population (magnetar model)
  W(z)  — weight function for the Limber integral: b(z) * n(z), normalised
"""

import numpy as np
from scipy.integrate import trapezoid


def n_z(z, alpha):
    """
    Normalised FRB redshift distribution: n(z) = z^2 * exp(-alpha * z).

    Parameters
    ----------
    z : ndarray
        Redshift values.
    alpha : float
        Steepness parameter controlling the high-z tail.

    Returns
    -------
    n_norm : ndarray
        Normalised distribution (integrates to 1 over z).
    """
    raw = z ** 2 * np.exp(-alpha * z)
    norm = trapezoid(raw, z)  # integral over z for normalisation
    return raw / norm


def bias(z, b0, delta):
    """
    Linear bias of FRB hosts (magnetar model): b(z) = b0 * (1 + z)^delta.

    Parameters
    ----------
    z : ndarray
        Redshift values.
    b0 : float
        Bias amplitude at z = 0.
    delta : float
        Redshift evolution exponent.

    Returns
    -------
    b : ndarray
        Bias values at each redshift.
    """
    return b0 * (1.0 + z) ** delta


def weight_frb(z, alpha, b0, delta):
    """
    FRB weight function for the Limber integral: W(z) = b(z) * n(z), normalised.

    Parameters
    ----------
    z : ndarray
        Redshift values.
    alpha : float
        Steepness parameter of n(z).
    b0 : float
        Bias amplitude at z = 0.
    delta : float
        Bias redshift evolution exponent.

    Returns
    -------
    W : ndarray
        Normalised weight function (integrates to 1 over z).
    """
    n = n_z(z, alpha)
    b = bias(z, b0, delta)
    raw = b * n
    norm = trapezoid(raw, z)  # normalise so integral = 1
    return raw / norm
