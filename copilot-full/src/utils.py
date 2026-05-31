"""
Utility functions for FRB-Galaxy cross-correlation analysis.
"""

import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u


def angular_separation(ra1, dec1, ra2, dec2):
    """
    Calculate angular separation between two sets of celestial coordinates.
    
    Parameters
    ----------
    ra1, dec1 : array-like
        Right ascension and declination of first set (in degrees)
    ra2, dec2 : array-like
        Right ascension and declination of second set (in degrees)
    
    Returns
    -------
    separations : array
        Angular separations in arcminutes
    """
    coord1 = SkyCoord(ra=ra1*u.deg, dec=dec1*u.deg)
    coord2 = SkyCoord(ra=ra2*u.deg, dec=dec2*u.deg)
    
    # Handle scalar and array cases
    if np.isscalar(ra1):
        separation = coord1.separation(coord2).arcmin
    else:
        # Compute separation for each pair
        separation = np.array([coord1[i].separation(coord2).arcmin 
                              for i in range(len(ra1))])
    
    return separation


def euclidean_distance_3d(ra1, dec1, z1, ra2, dec2, z2, cosmology=None):
    """
    Calculate 3D comoving distance between FRBs/galaxies using redshift.
    
    Parameters
    ----------
    ra1, dec1, z1 : array-like
        Coordinates and redshift of first set
    ra2, dec2, z2 : array-like
        Coordinates and redshift of second set
    cosmology : Cosmology object, optional
        Cosmology to use. If None, uses Planck15.
    
    Returns
    -------
    distances : array
        3D distances in Mpc
    """
    from astropy.cosmology import Planck15
    
    if cosmology is None:
        cosmology = Planck15
    
    # Angular separation in radians
    coord1 = SkyCoord(ra=ra1*u.deg, dec=dec1*u.deg)
    coord2 = SkyCoord(ra=ra2*u.deg, dec=dec2*u.deg)
    
    theta = coord1.separation(coord2).radian
    
    # Comoving distances
    d1 = cosmology.comoving_distance(z1).Mpc
    d2 = cosmology.comoving_distance(z2).Mpc
    
    # 3D distance using law of cosines
    distance_3d = np.sqrt(d1**2 + d2**2 - 2*d1*d2*np.cos(theta))
    
    return distance_3d


def histogram_cross_correlation(separations, bin_edges):
    """
    Create histogram of separations.
    
    Parameters
    ----------
    separations : array
        Separations (angular or comoving)
    bin_edges : array
        Bin edges for histogram
    
    Returns
    -------
    counts : array
        Histogram counts
    bin_centers : array
        Center of each bin
    """
    counts, _ = np.histogram(separations, bins=bin_edges)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    return counts, bin_centers


def bootstrap_resample(data, n_bootstrap=1000, seed=42):
    """
    Bootstrap resampling for error estimation.
    
    Parameters
    ----------
    data : array
        Input data
    n_bootstrap : int
        Number of bootstrap samples
    seed : int
        Random seed
    
    Returns
    -------
    bootstrap_samples : array
        Bootstrap samples (shape: n_bootstrap x len(data))
    """
    np.random.seed(seed)
    bootstrap_samples = np.array([np.random.choice(data, size=len(data), replace=True)
                                  for _ in range(n_bootstrap)])
    return bootstrap_samples


def set_random_seed(seed=42):
    """Set random seed for reproducibility."""
    np.random.seed(seed)
