"""
angular_power_spectrum.py — Limber-approximation angular power spectrum C(ell).

Computes the FRB auto-correlation angular power spectrum:

    C(ell) = integral over chi of
             [ W(chi)^2 / chi^2 ] * P(k = (ell + 0.5) / chi) dchi

where W(chi) = W_z(z(chi)) * sqrt(dz/dchi) and dz/dchi = H(z) / c.
""" 

import numpy as np

from config.parameters import COSMO, Z_ARR, ELL_ARR, B0, DELTA
from src.cosmology import CHI_ARR, C_KM_S
from src.distributions import weight_frb


def compute_cell(alpha, P_interp, k_min, k_max):
    """
    Compute the angular power spectrum C(ell) via the Limber approximation.

    Parameters
    ----------
    alpha : float
        Steepness parameter for the FRB redshift distribution n(z).
    P_interp : callable
        Interpolated nonlinear power spectrum P(k) in Mpc^3,
        accepting k in 1/Mpc.
    k_min : float
        Minimum valid wavenumber for P_interp [1/Mpc].
    k_max : float
        Maximum valid wavenumber for P_interp [1/Mpc].

    Returns
    -------
    ell_arr : ndarray
        Multipole values (integers).
    C_ell : ndarray
        Angular power spectrum at each multipole.
    """
    # Weight function evaluated on the redshift grid W(z) = b(z) * n(z)
    W_z = weight_frb(Z_ARR, alpha, B0, DELTA)

    # dz/dchi = H(z) / c  [1/Mpc]
    H_arr = COSMO.H(Z_ARR).value  # H(z) in km/s/Mpc
    dz_dchi = H_arr / C_KM_S      # convert to 1/Mpc

    # W(chi) = W_z(z(chi)) * sqrt(dz/dchi) — incorporates the Jacobian
    W = W_z * np.sqrt(dz_dchi)

    # Allocate output
    C_ell = np.zeros(len(ELL_ARR))

    # i is index and ell is the multipole value (integer)
    for i, ell in enumerate(ELL_ARR):
        # Wavenumber probed at each comoving distance: k = (ell + 0.5) / chi
        k_arr = (ell + 0.5) / CHI_ARR

        # Mask: keep only chi values where k falls inside the valid P(k) range
        valid = (k_arr >= k_min) & (k_arr <= k_max)
        if not np.any(valid):
            C_ell[i] = 0.0
            continue

        # Evaluate integrand on valid points
        chi_v = CHI_ARR[valid]
        k_v = k_arr[valid]
        W_v = W[valid]

        # Integrand: W^2 / chi^2 * P(k)
        integrand = (W_v ** 2) / (chi_v ** 2) * P_interp(k_v)

        # Integrate over comoving distance using the trapezoidal rule
        C_ell[i] = np.trapezoid(integrand, chi_v)

    return ELL_ARR, C_ell
