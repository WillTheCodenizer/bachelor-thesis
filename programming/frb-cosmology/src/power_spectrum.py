"""
power_spectrum.py — Nonlinear matter power spectrum P(k, z).

Uses the hmf package (MassFunction) to retrieve the nonlinear P(k)
at a grid of redshifts z = [0, z_max], converts from hmf's native h/Mpc 
units to physical 1/Mpc units, and builds a 2D cubic spline interpolation 
function P(k, z) over wavenumber and comoving distance.

The redshift evolution is computed self-consistently via MassFunction.update(z),
accounting for the nonlinear growth of structure with cosmic time.
"""

import numpy as np
from scipy.interpolate import RectBivariateSpline
from hmf import MassFunction

from config.parameters import COSMO, SIGMA_8, N_S, LITTLE_H


def build_power_spectrum_2d(z_max=4.0, n_z=120):
    """
    Compute the redshift-dependent nonlinear matter power spectrum P(k, z) 
    using a 2D cubic spline.

    Parameters
    ----------
    z_max : float, optional
        Maximum redshift to sample (default 4.0).
    n_z : int, optional
        Number of redshift sample points (default 120).

    Returns
    -------
    k_phys : ndarray
        Wavenumber array in units of 1/Mpc.
    P_interp_2d : callable
        2D interpolation function P_interp_2d(k, chi) that accepts
        k in 1/Mpc and comoving distance chi in Mpc, returning P(k, z(chi))
        in Mpc^3. Interpolated via cubic spline over the (chi, k) grid.
    k_min : float
        Minimum valid wavenumber for P_interp_2d [1/Mpc].
    k_max : float
        Maximum valid wavenumber for P_interp_2d [1/Mpc].
    """
    # ── Step 1: Initialise hmf MassFunction once at z=0 ──────────────────
    mf = MassFunction(
        cosmo_model=COSMO,
        sigma_8=SIGMA_8,
        n=N_S,
        transfer_model="EH",
    )

    # ── Step 2: Extract k-grid and convert to physical units ──────────────
    k_hmf = mf.k              # [h/Mpc]
    k_phys = k_hmf * LITTLE_H  # [1/Mpc] — converted to physical units. 

    # ── Step 3: Build redshift grid ───────────────────────────────────────
    z_grid = np.linspace(0.0, z_max, n_z)

    # ── Step 4: Allocate P_aux array ──────────────────────────────────────
    P_aux = np.zeros((n_z, len(k_phys)))

    # ── Step 5: Loop over redshifts, update MassFunction, store P(k, z) ───
    # iz = 0, 1, 2, ..., 119   ← Index für P_aux
    # z  = 0.0, 0.034, 0.067, ..., 4.0  ← real value for mf.update()
    # every row is a different redshift, every column is a different k
    for iz, z in enumerate(z_grid): # enumerate for indexing
        mf.update(z=z)
        # P in hmf is in (Mpc/h)^3, convert to Mpc^3
        P_aux[iz, :] = mf.nonlinear_power / (LITTLE_H ** 3)

    # ── Step 6: Convert redshift grid to comoving distance ────────────────
    #Before:   P_aux[iz] belongs to  z_grid[iz]  = 0.034
    #After:  P_aux[iz] belongs to  chi_grid[iz] = 150 Mpc
    chi_grid = COSMO.comoving_distance(z_grid).value  # [Mpc], input z_grid is 1D array, output chi_grid is 1D array of same length
    # Clamp chi[0] to avoid chi=0 (numerical stability)
    chi_grid[0] = max(chi_grid[0], 1e-3)

    # ── Step 7: Build 2D cubic spline in log-log space ────────────────────
    # Prepare log-transformed data
    log_k = np.log10(k_phys)
    log_P = np.log10(np.clip(P_aux, 1e-30, None))  # Avoid log(0) = -inf, np.clip does not modify P_aux in-place, it returns a new array where values < 1e-30 are set to 1e-30, ensuring all values are positive for log10

    # RectBivariateSpline: x=chi, y=log10(k), z=log10(P), 
    # Note: the spline is built as spl(chi_i, log10(k_j)) -> log10(P_ij)
    spline = RectBivariateSpline(
        chi_grid, log_k, log_P,
        kx=3, ky=3  # cubic spline in both dimensions, 3 stands for the degree of the spline
    )

    # ── Step 8: Define wrapper function ───────────────────────────────────
    def P_interp_2d(k, chi):
        """
        Evaluate the 2D power spectrum spline at (k, chi).

        Parameters
        ----------
        k : float or ndarray
            Wavenumber(s) in 1/Mpc.
        chi : float or ndarray
            Comoving distance(es) in Mpc (maps to z via redshift-distance relation).

        Returns
        -------
        P : float or ndarray
            Interpolated nonlinear power spectrum P(k, z(chi)) in Mpc^3.
        """
        # Evaluate spline in log-space: spline.ev(chi, log10(k))
        # Broadcasting: if k and chi are arrays of same shape, output is same shape
        log_P_interp = spline.ev(chi, np.log10(k))
        # Transform back to linear space
        return 10.0 ** log_P_interp

    # ── Step 9: Return interpolator and bounds ────────────────────────────
    k_min = k_phys.min()
    k_max = k_phys.max()
    return k_phys, P_interp_2d, k_min, k_max
