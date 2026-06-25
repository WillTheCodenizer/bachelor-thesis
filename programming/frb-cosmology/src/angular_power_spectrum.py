"""
angular_power_spectrum.py — Limber-approximation angular power spectrum C(ell).

Computes the FRB auto-correlation and FRB x Galaxy cross-correlation angular
power spectra:

Auto-correlation:
    C(ell) = integral over chi of
             [ W(chi)^2 / chi^2 ] * P(k = (ell + 0.5) / chi) dchi

Cross-correlation:
    C(ell) = integral over chi of
             [ W_1(chi) * W_2(chi) / chi^2 ] * P(k = (ell + 0.5) / chi) dchi

where W(chi) = W_z(z(chi)) * dz/dchi and dz/dchi = H(z) / c.
""" 

import numpy as np

from config.parameters import COSMO, Z_ARR, ELL_ARR
from src.cosmology import CHI_ARR, C_KM_S
from src.distributions import weight_frb


def compute_cell_from_weight(weight_z, P_interp, k_min, k_max):
    """
    Compute the angular power spectrum C(ell) for a provided W(z).

    Parameters
    ----------
    weight_z : ndarray
        Weight function sampled on Z_ARR.
    P_interp : callable
        Interpolated nonlinear power spectrum P(k, z) in Mpc^3,
        accepting k in 1/Mpc and chi in Mpc.
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
    if len(weight_z) != len(Z_ARR):
        raise ValueError("weight_z must have same length as Z_ARR.")

    # dz/dchi = H(z) / c  [1/Mpc]
    H_arr = COSMO.H(Z_ARR).value  # H(z) in km/s/Mpc
    dz_dchi = H_arr / C_KM_S      # convert to 1/Mpc

    # W(chi) = W_z(z(chi)) * dz/dchi — incorporates the Jacobian
    W = weight_z * dz_dchi

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

        # Integrand: W^2 / chi^2 * P(k, z) — P(k, z) evaluated at the redshift corresponding to chi via 2D spline
        integrand = (W_v ** 2) / (chi_v ** 2) * P_interp(k_v, chi_v)

        # Integrate over comoving distance using the trapezoidal rule
        C_ell[i] = np.trapezoid(integrand, chi_v)

    return ELL_ARR, C_ell


def compute_cell_cross_correlation(weight_1_z, weight_2_z, P_interp, k_min, k_max):
    """
    Compute the cross-correlation angular power spectrum C(ell) between two tracers.

    Uses the Limber approximation with the cross-correlation integrand W_1 * W_2:

        C(ell) = integral over chi of
                 [ W_1(chi) * W_2(chi) / chi^2 ] * P(k = (ell + 0.5) / chi) dchi

    No shot noise is included — cross-correlations between distinct populations
    carry no shot noise contribution.

    Parameters
    ----------
    weight_1_z : ndarray
        Weight function of tracer 1 sampled on Z_ARR.
    weight_2_z : ndarray
        Weight function of tracer 2 sampled on Z_ARR.
    P_interp : callable
        Interpolated nonlinear power spectrum P(k, z) in Mpc^3,
        accepting k in 1/Mpc and chi in Mpc.
    k_min : float
        Minimum valid wavenumber for P_interp [1/Mpc].
    k_max : float
        Maximum valid wavenumber for P_interp [1/Mpc].

    Returns
    -------
    ell_arr : ndarray
        Multipole values (integers).
    C_ell : ndarray
        Cross-correlation angular power spectrum at each multipole.
    """
    if len(weight_1_z) != len(Z_ARR) or len(weight_2_z) != len(Z_ARR):
        raise ValueError("weight arrays must have same length as Z_ARR.")

    # dz/dchi = H(z) / c  [1/Mpc]
    H_arr = COSMO.H(Z_ARR).value
    dz_dchi = H_arr / C_KM_S

    # W_i(chi) = W_z_i(z(chi)) * dz/dchi — incorporates the Jacobian for both tracers
    W1 = weight_1_z * dz_dchi
    W2 = weight_2_z * dz_dchi

    C_ell = np.zeros(len(ELL_ARR))

    for i, ell in enumerate(ELL_ARR):
        # Wavenumber probed at each comoving distance
        k_arr = (ell + 0.5) / CHI_ARR

        # Mask: keep only chi values where k falls inside the valid P(k) range
        valid = (k_arr >= k_min) & (k_arr <= k_max)
        if not np.any(valid):
            C_ell[i] = 0.0
            continue

        chi_v = CHI_ARR[valid]
        k_v = k_arr[valid]
        W1_v = W1[valid]
        W2_v = W2[valid]

        # Cross-correlation integrand: W_1 * W_2 / chi^2 * P(k, z)
        integrand = (W1_v * W2_v) / (chi_v ** 2) * P_interp(k_v, chi_v)

        C_ell[i] = np.trapezoid(integrand, chi_v)

    return ELL_ARR, C_ell


def compute_cell(alpha, P_interp, k_min, k_max, b0, delta):
    """
    Compute the angular power spectrum C(ell) via the Limber approximation.

    Parameters
    ----------
    alpha : float
        Steepness parameter for the FRB redshift distribution n(z).
    P_interp : callable
        Interpolated nonlinear power spectrum P(k, z) in Mpc^3,
        accepting k in 1/Mpc and chi in Mpc.
    k_min : float
        Minimum valid wavenumber for P_interp [1/Mpc].
    k_max : float
        Maximum valid wavenumber for P_interp [1/Mpc].
    b0 : float, optional
        Bias amplitude at z = 0.
    delta : float, optional
        Bias redshift evolution exponent.

    Returns
    -------
    ell_arr : ndarray
        Multipole values (integers).
    C_ell : ndarray
        Angular power spectrum at each multipole.
    """
    # Weight function evaluated on the redshift grid W(z) = b(z) * n(z)
    weight_z = weight_frb(Z_ARR, alpha, b0, delta)
    return compute_cell_from_weight(weight_z, P_interp, k_min, k_max)
