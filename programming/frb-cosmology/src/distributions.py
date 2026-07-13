"""
distributions.py — FRB redshift distribution, bias model, and weight function.

Defines:
  n(z)  — normalised redshift distribution of FRBs
    b(z)  — linear bias of the FRB host population
  W(z)  — weight function for the Limber integral: b(z) * n(z), normalised
"""

import numpy as np
from scipy.integrate import trapezoid

from config.parameters import GALAXY_NZ_FILE, GALAXY_N_BINS
from src.cosmology import linear_growth_factor


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
    Linear bias of FRB hosts: b(z) = b0 * (1 + z)^delta.

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
        weight function (integrates to 1 over z).
    """
    n = n_z(z, alpha)
    b = bias(z, b0, delta)
    raw = b * n
    return raw


def load_galaxy_nz_data(file_path=GALAXY_NZ_FILE):
    """
    Load galaxy tomographic redshift distributions from a text file.

    The file must contain:
      - column 0: Z_MID
      - columns 1..N: tomographic bins BIN1..BINN

    Parameters
    ----------
    file_path : str or pathlib.Path, optional
        Path to the galaxy n(z) file.

    Returns
    -------
    z_mid : ndarray
        Redshift grid values from column 0.
    nz_bins : ndarray
        Raw bin distributions with shape (n_z, n_bins).
    """
    data = np.loadtxt(file_path)
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError("Galaxy n(z) file must contain at least two columns.")

    z_mid = data[:, 0]
    nz_bins = data[:, 1:]

    if nz_bins.shape[1] != GALAXY_N_BINS:
        raise ValueError(
            f"Expected {GALAXY_N_BINS} galaxy bins, got {nz_bins.shape[1]}."
        )

    return z_mid, nz_bins


def compute_galaxy_bin_mean_redshifts(z_mid, nz_bins):
    """
    Compute mean redshift for each tomographic galaxy bin.

    Uses the discrete estimator:

        <z>_alpha = sum_i[z_i n_alpha(z_i)] / sum_i[n_alpha(z_i)]

    Parameters
    ----------
    z_mid : ndarray
        Redshift grid values from the input file.
    nz_bins : ndarray
        Bin values with shape (n_z, n_bins).

    Returns
    -------
    z_means : ndarray
        Mean redshift per galaxy bin.
    """
    # The computation of the numerator is vectorised across bins: z_mid[:, None] has shape (n_z, 1) 
    # and nz_bins has shape (n_z, n_bins), so the product has shape (n_z, n_bins). 
    # Summing over axis=0 gives the numerator for each bin. 
    # The denominator is simply the sum of nz_bins over axis=0. 
    # axis = 0 refers to column-wise summation, axis =1 
    numerator = np.sum(z_mid[:, None] * nz_bins, axis=0)
    denominator = np.sum(nz_bins, axis=0)

    z_means = np.zeros_like(denominator)
    valid = denominator > 0.0
    z_means[valid] = numerator[valid] / denominator[valid]
    return z_means


def compute_galaxy_bias_from_means(z_means):
    """
    Compute per-bin galaxy bias from mean redshift.

    Bias model:

        b_g^alpha = 0.95 / D_+(<z>_alpha)

    Parameters
    ----------
    z_means : ndarray
        Mean redshift values per tomographic bin.

    Returns
    -------
    biases : ndarray
        Galaxy bias values per tomographic bin.
    """
    d_plus = linear_growth_factor(z_means)
    return 0.95 / d_plus


def interpolate_galaxy_bins(z_target, z_mid, nz_bins, normalize=True):
    """
    Interpolate galaxy n(z) (z_mid) bins onto a target redshift grid (z_target).

    Parameters
    ----------
    z_target : ndarray
        Target redshift grid.
    z_mid : ndarray
        Source redshift grid from input data.
    nz_bins : ndarray
        Source bin distributions with shape (n_z, n_bins).
    normalize : bool, optional
        If True, normalize each interpolated bin to integral 1.

    Returns
    -------
    nz_interp : ndarray
        Interpolated (and optionally normalized) bins with shape
        (len(z_target), n_bins).
    """
    # n_bins is the number of tomographic bins, which corresponds to the number of columns in nz_bins.
    n_bins = nz_bins.shape[1]
    nz_interp = np.zeros((len(z_target), n_bins))


    for idx in range(n_bins):
        # np.interp is used to interpolate the n(z) values for each bin onto the target redshift grid.
        # left=0.0 and right=0.0 ensure that we get zero outside the original z range, which is a common assumption for n(z).
        arr = np.interp(z_target, z_mid, nz_bins[:, idx], left=0.0, right=0.0)
        if normalize:
            #arr is y and z_target is x, so this computes the area under the curve of arr(z) over the range of z_target.
            area = trapezoid(arr, z_target)
            if area > 0.0:
                arr = arr / area
        nz_interp[:, idx] = arr

    return nz_interp


def build_galaxy_weights(z_target, nz_interp, biases):
    """
    Build tomographic galaxy weight functions W_g^i(z) = n_i(z) * b_g^i.

    Parameters
    ----------
    z_target : ndarray
        Target redshift grid.
    nz_interp : ndarray
        Interpolated galaxy n(z) distributions with shape (len(z_target), n_bins).
    biases : ndarray
        Bias value per tomographic bin.

    Returns
    -------
    weights : ndarray
        Weight functions with shape (len(z_target), n_bins).
    """
    _ = z_target  # Keep explicit signature for readability in pipeline calls.
    # biases has shape (n_bins,) and nz_interp has shape (len(z_target), n_bins).
    # the multiplication nz_interp * biases[None, :] looks for example like: 
    # nz_interp: [[n1(z1), n2(z1), n3(z1)],
    #              [n1(z2), n2(z2), n3(z2)],
    #              ...,
    #              [n1(zN), n2(zN), n3(zN)]]
    # biases: [b1, b2, b3]
    # biases[None, :] adds a new axis to make it shape (1, n_bins), so it can be broadcasted across 
    # the z dimension: 
    # biases[None, :]: [[b1, b2, b3]]
    # The multiplication then yields:
    # weights: [[n1(z1)*b1, n2(z1)*b2, n3(z1)*b3],
    #           [n1(z2)*b1, n2(z2)*b2, n3(z2)*b3],
    #           ...,
    #           [n1(zN)*b1, n2(zN)*b2, n3(zN)*b3]]

    return nz_interp * biases[None, :]
