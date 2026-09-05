"""
fisher.py — Fisher matrix forecast for FRB bias parameters b0 and delta.

Implements the Reischke Fisher formalism:

    F_{ij} = f_sky * sum_ell (2*ell+1)/2
             * Tr[ C_hat^{-1} dC/dp_i C_hat^{-1} dC/dp_j ]

where C_hat = C_ell + N_ell is the observed covariance (signal + noise).

Derivatives dC/dp_i are computed numerically via central finite differences
at a ±1% perturbation around the fiducial parameter values.

Two forecast modes:
  - 'frb_only'    : 1×1 covariance using only C_ell^ff
  - 'multitracer' : (N+1)×(N+1) covariance using [g1, ..., gN, FRB]
"""

import numpy as np
from scipy.stats import chi2 as chi2_dist

from config.parameters import Z_ARR, ELL_ARR
from src.angular_power_spectrum import compute_cell_from_weight, compute_cell_cross_correlation
from src.distributions import weight_frb


# =============================================================================
# C_ell computation helpers
# =============================================================================

def compute_frb_cells(alpha, b0, delta, weights_galaxy, P_interp, k_min, k_max):
    """
    Compute FRB auto-correlation and FRB×galaxy cross-correlation C_ells.

    Parameters
    ----------
    alpha : float
        FRB redshift distribution steepness parameter.
    b0 : float
        FRB bias amplitude at z = 0.
    delta : float
        FRB bias redshift evolution exponent.
    weights_galaxy : ndarray, shape (N_Z, 6)
        Pre-built galaxy weight functions W_g^i(z) on Z_ARR.
    P_interp : callable
        2D power spectrum interpolator P(k, chi).
    k_min, k_max : float
        Valid wavenumber range [1/Mpc].

    Returns
    -------
    cell_ff : ndarray, shape (n_ell,)
        FRB auto-correlation angular power spectrum.
    cell_gf : ndarray, shape (6, n_ell)
        FRB×galaxy cross-correlation for each galaxy bin.
    """
    w_frb = weight_frb(Z_ARR, alpha, b0, delta)
    _, cell_ff = compute_cell_from_weight(w_frb, P_interp, k_min, k_max)

    n_bins = weights_galaxy.shape[1]
    n_ell = len(ELL_ARR)
    cell_gf = np.zeros((n_bins, n_ell))
    for i in range(n_bins):
        _, cell_gf[i] = compute_cell_cross_correlation(
            weights_galaxy[:, i], w_frb, P_interp, k_min, k_max
        )

    return cell_ff, cell_gf


def compute_galaxy_cells(weights_galaxy, P_interp, k_min, k_max):
    """
    Compute the full symmetric 6×6 galaxy covariance C_ell block.

    Galaxy C_ells are independent of FRB parameters and computed once,
    shared across all FRB parameter perturbations.

    Parameters
    ----------
    weights_galaxy : ndarray, shape (N_Z, 6)
        Pre-built galaxy weight functions W_g^i(z) on Z_ARR.
    P_interp : callable
        2D power spectrum interpolator P(k, chi).
    k_min, k_max : float
        Valid wavenumber range [1/Mpc].

    Returns
    -------
    cell_gg : ndarray, shape (6, 6, n_ell)
        Symmetric galaxy auto- and cross-correlation spectra.
    """
    n_bins = weights_galaxy.shape[1]
    n_ell = len(ELL_ARR)
    cell_gg = np.zeros((n_bins, n_bins, n_ell))

    for i in range(n_bins):
        for j in range(i, n_bins):
            if i == j:
                _, c = compute_cell_from_weight(
                    weights_galaxy[:, i], P_interp, k_min, k_max
                )
            else:
                _, c = compute_cell_cross_correlation(
                    weights_galaxy[:, i], weights_galaxy[:, j], P_interp, k_min, k_max
                )
            cell_gg[i, j] = c
            cell_gg[j, i] = c

    return cell_gg


# =============================================================================
# Numerical derivatives
# =============================================================================

def compute_cell_derivative(param, alpha, b0, delta, weights_galaxy, P_interp, k_min, k_max,
                             step_frac=0.01):
    """
    Compute numerical central-difference derivatives of FRB-containing C_ells.

        dC/d(param) = [C(param + step) - C(param - step)] / (2 * step)

    where step = param_fiducial * step_frac (default ±1%).

    Only FRB-containing C_ells (cell_ff, cell_gf) carry non-zero derivatives.
    The galaxy-galaxy block cell_gg is FRB-parameter-independent (derivative = 0).

    Parameters
    ----------
    param : str
        Parameter to differentiate: 'b0' or 'delta'.
    alpha : float
        Fiducial alpha value.
    b0 : float
        Fiducial b0 value.
    delta : float
        FRB bias redshift evolution exponent.
    weights_galaxy : ndarray, shape (N_Z, 6)
        Pre-built galaxy weight functions.
    P_interp : callable
        2D power spectrum interpolator.
    k_min, k_max : float
        Valid wavenumber range.
    step_frac : float
        Fractional perturbation size (default 0.01 = 1%).

    Returns
    -------
    d_ff : ndarray, shape (n_ell,)
        Derivative of FRB auto-correlation with param.
    d_gf : ndarray, shape (6, n_ell)
        Derivative of FRB×galaxy cross-correlation with param.
    """
    if param == 'b0':
        step = max(abs(b0) * step_frac, step_frac)

        ff_plus, gf_plus = compute_frb_cells(
            alpha, b0 + step, delta, weights_galaxy, P_interp, k_min, k_max
        )
        ff_minus, gf_minus = compute_frb_cells(
            alpha, b0 - step, delta, weights_galaxy, P_interp, k_min, k_max
        )
    elif param == 'delta':
        step = max(abs(delta) * step_frac, step_frac)

        ff_plus, gf_plus = compute_frb_cells(
            alpha, b0, delta + step, weights_galaxy, P_interp, k_min, k_max
        )
        ff_minus, gf_minus = compute_frb_cells(
            alpha, b0, delta - step, weights_galaxy, P_interp, k_min, k_max
        )
    else:
        raise ValueError(f"Unknown parameter '{param}'. Use 'b0' or 'delta'.")

    d_ff = (ff_plus - ff_minus) / (2.0 * step)
    d_gf = (gf_plus - gf_minus) / (2.0 * step)

    return d_ff, d_gf


# =============================================================================
# Fisher matrix construction
# =============================================================================

def compute_fisher_matrix(cell_ff, cell_gg, cell_gf,
                           n_shot_frb, n_shot_gal,
                           d_b0, d_delta, f_sky, mode):
    """
    Compute the 2×2 Fisher matrix for parameters (b0, delta).

    Uses the Reischke formula with einsum for efficiency:
        F_{ij} = f_sky * sum_ell (2*ell+1)/2
                 * Tr[ C_hat^{-1} dC/dp_i C_hat^{-1} dC/dp_j ]

    where C_hat = C_ell + N_ell is signal + noise, and the derivatives act
    only on the theoretical signal C_ell (not the noise term N_ell).

    Parameters
    ----------
    cell_ff : ndarray, shape (n_ell,)
        FRB auto-correlation C_ell.
    cell_gg : ndarray, shape (6, 6, n_ell)
        Galaxy auto- and cross-correlation C_ells (used in multitracer mode).
    cell_gf : ndarray, shape (6, n_ell)
        FRB×galaxy cross-correlations (used in multitracer mode).
    n_shot_frb : float
        FRB shot noise level.
    n_shot_gal : ndarray, shape (6,)
        Galaxy shot noise per tomographic bin.
    d_b0 : tuple (d_ff_b0, d_gf_b0)
        Derivatives w.r.t. b0 from compute_cell_derivative.
    d_delta : tuple (d_ff_delta, d_gf_delta)
        Derivatives w.r.t. delta from compute_cell_derivative.
    f_sky : float
        Observed sky fraction for the Fisher sum prefactor.
    mode : str
        'frb_only' — 1×1 covariance from FRB auto-correlation only.
        'multitracer' — 7×7 covariance from [g1..g6, FRB] multi-tracer.

    Returns
    -------
    F : ndarray, shape (2, 2)
        Fisher matrix; rows/columns ordered as [b0, delta].
    """
    d_ff_b0, d_gf_b0 = d_b0
    d_ff_delta, d_gf_delta = d_delta
    n_ell = len(ELL_ARR)

    # ── FRB-only forecast ───────────────────────────────────────────────────
    if mode == 'frb_only':
        # Build observed covariance per multipole: C_hat_ell = C_ell^ff + N_shot^ff
        # Shape: (n_ell,) — scalar per multipole
        C_hat_ell = cell_ff + n_shot_frb

        # Compute traces for the 2×2 Fisher matrix via Tr[C^{-1} dC_i C^{-1} dC_j]
        # For 1×1 matrices: Tr[C^{-1} dC_i C^{-1} dC_j] = (dC_i * dC_j) / C^2
        trace_b0b0 = (d_ff_b0 * d_ff_b0) / (C_hat_ell ** 2)  # d(b0) × d(b0)
        trace_b0d = (d_ff_b0 * d_ff_delta) / (C_hat_ell ** 2)  # d(b0) × d(delta)
        trace_dd = (d_ff_delta * d_ff_delta) / (C_hat_ell ** 2)  # d(delta) × d(delta)

        # Sum over multipoles with prefactor (2*ell+1)/2
        prefactors = (2.0 * ELL_ARR + 1.0) / 2.0
        F_11 = np.sum(prefactors * trace_b0b0)
        F_12 = np.sum(prefactors * trace_b0d)
        F_22 = np.sum(prefactors * trace_dd)

        # Apply sky fraction and build Fisher matrix
        F = np.array([
            [f_sky * F_11, f_sky * F_12],
            [f_sky * F_12, f_sky * F_22],
        ])

    # ── Multi-tracer forecast ───────────────────────────────────────────────
    elif mode == 'multitracer':
        n_bins = cell_gg.shape[0]
        n_tracers = n_bins + 1  # ordering: [g1, ..., gN, FRB]

        # Build full 7×7 observed covariance matrices for all multipoles
        # Shape: (n_ell, n_tracers, n_tracers)
        C_hat_full = np.zeros((n_ell, n_tracers, n_tracers))

        for i_ell in range(n_ell):
            # Galaxy-galaxy block (6×6) with shot noise on the diagonal
            C_hat_full[i_ell, :n_bins, :n_bins] = cell_gg[:, :, i_ell]
            for a in range(n_bins):
                C_hat_full[i_ell, a, a] += n_shot_gal[a]

            # FRB-galaxy cross block (symmetric)
            C_hat_full[i_ell, :n_bins, n_bins] = cell_gf[:, i_ell]
            C_hat_full[i_ell, n_bins, :n_bins] = cell_gf[:, i_ell]

            # FRB-FRB entry with shot noise
            C_hat_full[i_ell, n_bins, n_bins] = cell_ff[i_ell] + n_shot_frb
        # 7x7 covariance matrices built for all multipoles

        # Invert the covariance matrices for all multipoles
        # Shape: (n_ell, n_tracers, n_tracers)
        C_hat_inv = np.zeros_like(C_hat_full)
        for i_ell in range(n_ell):
            try:
                C_hat_inv[i_ell] = np.linalg.inv(C_hat_full[i_ell])
            except np.linalg.LinAlgError:
                # If inversion fails, skip this multipole (set inverse to zero)
                print(f"Warning: Covariance matrix at ell={ELL_ARR[i_ell]} is singular. Skipping this multipole.")
                continue

        # Build derivative matrices for each parameter
        # dC_b0[ell, :, :] and dC_delta[ell, :, :] contain the derivatives
        # at each multipole ell (7×7 matrices with nonzero entries only in
        # the FRB-containing rows/columns)
        dC_b0 = np.zeros((n_ell, n_tracers, n_tracers))
        dC_delta = np.zeros((n_ell, n_tracers, n_tracers))

        for i_ell in range(n_ell):
            # FRB-galaxy cross-correlation derivatives
            dC_b0[i_ell, :n_bins, n_bins] = d_gf_b0[:, i_ell]
            dC_b0[i_ell, n_bins, :n_bins] = d_gf_b0[:, i_ell]
            dC_b0[i_ell, n_bins, n_bins] = d_ff_b0[i_ell]

            dC_delta[i_ell, :n_bins, n_bins] = d_gf_delta[:, i_ell]
            dC_delta[i_ell, n_bins, :n_bins] = d_gf_delta[:, i_ell]
            dC_delta[i_ell, n_bins, n_bins] = d_ff_delta[i_ell]

        # Compute the trace terms using einsum for efficiency
        # Tr[C_hat^{-1} dC_i C_hat^{-1} dC_j]
        # via:
        #   temp_i = C_hat_inv @ dC_i          (shape: n_ell × n_tracers × n_tracers)
        #   arg_i  = dC_i @ temp_i             (shape: n_ell × n_tracers × n_tracers)
        #   trace  = Tr[C_hat_inv @ arg_i]    (shape: n_ell)

        # For parameter pair (b0, b0):
        temp_b0 = np.einsum('lij, ljk -> lik', C_hat_inv, dC_b0) #e.g. (temp_b0_{l, i, k} = sum_j C_hat_inv_{l, i, j} * dC_b0_{l, j, k})
        arg_b0b0 = np.einsum('lij, ljk -> lik', dC_b0, temp_b0)
        trace_b0b0 = np.einsum('lij, lji -> l', C_hat_inv, arg_b0b0)

        # For parameter pair (b0, delta):
        temp_delta = np.einsum('lij, ljk -> lik', C_hat_inv, dC_delta)
        arg_b0d = np.einsum('lij, ljk -> lik', dC_b0, temp_delta)
        trace_b0d = np.einsum('lij, lji -> l', C_hat_inv, arg_b0d)

        # For parameter pair (delta, delta):
        arg_dd = np.einsum('lij, ljk -> lik', dC_delta, temp_delta)
        trace_dd = np.einsum('lij, lji -> l', C_hat_inv, arg_dd)

        # Sum over multipoles with prefactor (2*ell+1)/2
        prefactors = (2.0 * ELL_ARR + 1.0) / 2.0
        F_11 = np.sum(prefactors * trace_b0b0)
        F_12 = np.sum(prefactors * trace_b0d)
        F_22 = np.sum(prefactors * trace_dd)

        # Apply sky fraction and build Fisher matrix
        F = np.array([
            [f_sky * F_11, f_sky * F_12],
            [f_sky * F_12, f_sky * F_22],
        ])

    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'frb_only' or 'multitracer'.")

    return F


# =============================================================================
# Covariance and ellipse helpers
# =============================================================================

def invert_fisher(fisher_matrix):
    """
    Invert a Fisher matrix to obtain the parameter covariance matrix.

    Parameters
    ----------
    fisher_matrix : ndarray, shape (2, 2)
        Fisher information matrix.

    Returns
    -------
    cov : ndarray, shape (2, 2)
        Parameter covariance matrix Cov = F^{-1}.
    """
    return np.linalg.inv(fisher_matrix)


def get_confidence_ellipse(cov_2x2, confidence=0.6827):
    """
    Extract confidence ellipse parameters from a 2×2 covariance matrix.

    Uses the chi2 distribution with 2 degrees of freedom to scale the
    semi-axes to the requested joint confidence level.

    Parameters
    ----------
    cov_2x2 : ndarray, shape (2, 2)
        Parameter covariance matrix.
    confidence : float
        Joint confidence level.
        Default 0.6827 ≈ 1σ in 2D (chi2(2) → scale ≈ 1.51).
        Use 0.9545 for 2σ in 2D (scale ≈ 2.49).

    Returns
    -------
    width_a : float
        Major semi-axis length (in parameter units).
    width_b : float
        Minor semi-axis length (in parameter units).
    angle_deg : float
        Orientation angle of the major axis w.r.t. the b0 (x) axis, in degrees.
    """
    scale = np.sqrt(chi2_dist.ppf(confidence, df=2))

    eigenvalues, eigenvectors = np.linalg.eigh(cov_2x2)

    # Sort descending: index 0 → major axis
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    width_a = scale * np.sqrt(eigenvalues[0])
    width_b = scale * np.sqrt(eigenvalues[1])

    # Angle of the major eigenvector w.r.t. the b0 (x) axis
    angle_deg = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))

    return width_a, width_b, angle_deg
