"""
cosmology.py — Background cosmology setup.

Uses the Planck 2018 FlatLambdaCDM cosmology from config/parameters.py
to compute the comoving distance array over the project's redshift grid.
"""

import numpy as np
from astropy import units as u

from config.parameters import COSMO, Z_ARR

# Comoving distance for every redshift in Z_ARR, in Mpc (plain floats)
CHI_ARR = COSMO.comoving_distance(Z_ARR).to(u.Mpc).value

# Speed of light in km/s (for H(z)/c computation later)
C_KM_S = 2.998e5  # [km/s]


def _e_of_a(a):
    """
    Dimensionless Hubble expansion E(a) for a flat LambdaCDM model.

    Parameters
    ----------
    a : float or ndarray
        Scale factor.

    Returns
    -------
    ndarray
        E(a) = H(a) / H0.
    """
    omega_m = COSMO.Om0
    omega_lambda = 1.0 - omega_m
    return np.sqrt(omega_m / (a ** 3) + omega_lambda)


def _linear_growth_factor_integral(z, n_steps=4096):
    """
    Compute the linear growth factor D_+(z), normalised to D_+(0) = 1.

    The implementation follows the standard integral solution for flat LCDM:

        D(a) \\propto E(a) * integral_0^a [da' / (a'^3 E(a')^3)]

    Parameters
    ----------
    z : float or ndarray
        Redshift value(s).
    n_steps : int, optional
        Number of integration points for the internal scale-factor integral.

    Returns
    -------
    float or ndarray
        Linear growth factor D_+(z), normalized to unity at z=0.
    """
    z_arr = np.atleast_1d(np.asarray(z, dtype=float))
    a_arr = 1.0 / (1.0 + z_arr)

    # Avoid the integrable singularity at a=0 in numerical integration.
    a_min = 1e-5

    def _unnormalised_growth(a_target):
        a_grid = np.linspace(a_min, a_target, n_steps)
        integrand = 1.0 / (a_grid ** 3 * _e_of_a(a_grid) ** 3)
        prefactor = 2.5 * COSMO.Om0 * _e_of_a(a_target)
        return prefactor * np.trapezoid(integrand, a_grid)

    d0 = _unnormalised_growth(1.0)
    d_arr = np.array([_unnormalised_growth(a_val) / d0 for a_val in a_arr])

    if np.isscalar(z):
        return float(d_arr[0])
    return d_arr


def _linear_growth_factor_hmf(z):
    """
    Compute D_+(z) using hmf's internal growth-factor implementation.

    Parameters
    ----------
    z : float or ndarray
        Redshift value(s).

    Returns
    -------
    float or ndarray
        Linear growth factor D_+(z), normalized to unity at z=0.
    """
    from hmf import MassFunction

    # atleast_1d is used to ensure that scalars are also handled like arrays.
    z_arr = np.atleast_1d(np.asarray(z, dtype=float))

    # Evaluate only unique z values and map back for stable/efficient output.
    z_unique, inv = np.unique(z_arr, return_inverse=True)
    
    mf = MassFunction(
        cosmo_model=COSMO,
        # Use EH transfer directly to avoid CAMB backend incompatibilities
        # and keep behavior consistent with the power-spectrum module.
        transfer_model="EH",
    )

    d_unique = np.empty_like(z_unique)
    for idx, z_val in enumerate(z_unique):
        mf.update(z=float(z_val))
        # np.asarray(...).reshape(-1)[0] is used to extract the scalar growth factor from hmf's internal 
        # array structure, which may be a 1D array of length 1. This ensures we get a plain float value for D_+(z) 
        # at each unique redshift.
        growth = np.asarray(mf.growth_factor).reshape(-1)[0]
        d_unique[idx] = float(growth)

    d_arr = d_unique[inv]
    # If the input was a scalar, return a scalar output for convenience.
    if np.isscalar(z):
        return float(d_arr[0])
    return d_arr


def linear_growth_factor(z, n_steps=4096, method="hmf"):
    """
    Compute the linear growth factor D_+(z), normalised to D_+(0) = 1.

    Parameters
    ----------
    z : float or ndarray
        Redshift value(s).
    n_steps : int, optional
        Number of integration points for the internal scale-factor integral.
        Only used for ``method='integral'``.
    method : {"integral", "hmf"}, optional
        Backend used for D_+(z):
        - ``integral``: explicit LCDM integral solution
        - ``hmf``: use ``hmf.MassFunction(...).growth_factor`` (default)

    Returns
    -------
    float or ndarray
        Linear growth factor D_+(z), normalized to unity at z=0.
    """
    if method == "integral":
        return _linear_growth_factor_integral(z=z, n_steps=n_steps)
    if method == "hmf":
        return _linear_growth_factor_hmf(z=z)

    raise ValueError("method must be one of {'integral', 'hmf'}")
