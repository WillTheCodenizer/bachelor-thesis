"""
power_spectrum.py — Nonlinear matter power spectrum P(k).

Uses the hmf package (MassFunction) to retrieve the nonlinear P(k)
at z = 0, converts from hmf's native h/Mpc units to physical 1/Mpc
units, and provides a log-log interpolation function.

Note: This uses P(k) at z = 0 without a growth factor D(z).
      The Limber integral therefore implicitly assumes that the
      power spectrum does not evolve with redshift — a simplification
      that can be refined later by multiplying by D(z)^2.
"""

import numpy as np
from scipy.interpolate import interp1d
from hmf import MassFunction

from config.parameters import COSMO, SIGMA_8, N_S, LITTLE_H


def build_power_spectrum():
    """
    Compute the nonlinear matter power spectrum P(k) using hmf.

    Returns
    -------
    k_phys : ndarray
        Wavenumber array in units of 1/Mpc.
    P_phys : ndarray
        Nonlinear power spectrum in units of Mpc^3.
    P_interp : callable
        Log-log interpolation function P_interp(k) that accepts
        k in 1/Mpc and returns P(k) in Mpc^3.  Returns 0 for
        k values outside the valid range.
    """
    # Initialise hmf MassFunction with Planck 2018 cosmology (instance, not class)
    mf = MassFunction(
        cosmo_model=COSMO,
        sigma_8=SIGMA_8,
        n=N_S,
    )

    # Raw arrays from hmf (h/Mpc and (Mpc/h)^3), getting it from mf because it has already computed it   
    k_hmf = mf.k              # [h/Mpc]
    P_hmf = mf.nonlinear_power  # [(Mpc/h)^3]

    # Convert to physical units
    k_phys = k_hmf * LITTLE_H           # [1/Mpc]
    P_phys = P_hmf / (LITTLE_H ** 3)    # [Mpc^3]

    # Build log-log interpolation (return 0 outside valid range) 
    # (making a continuous function that can be evaluated at any k, not just the tabulated points)
    log_k = np.log10(k_phys)
    log_P = np.log10(P_phys)

    interp_func = interp1d(
        log_k, log_P,
        kind="linear",
        bounds_error=False, # no error if k is outside the range, just return the fill_value
        fill_value=-np.inf,  # log10(0) = -inf → 10^(-inf) = 0
    )

    def P_interp(k):
        """
        Interpolate the nonlinear power spectrum at arbitrary k.

        Parameters
        ----------
        k : float or ndarray
            Wavenumber(s) in 1/Mpc.

        Returns
        -------
        P : float or ndarray
            Power spectrum value(s) in Mpc^3.
            Returns 0 for k outside the tabulated range.
        """
        return 10.0 ** interp_func(np.log10(k))

    return k_phys, P_phys, P_interp
