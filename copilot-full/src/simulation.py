"""
Simulation and synthetic catalog generation for FRB and galaxy data.
"""

import numpy as np
from scipy.stats import uniform, norm


class CatalogSimulator:
    """
    Generate realistic synthetic catalogs of FRBs and galaxies.
    """
    
    def __init__(self, seed=42):
        """
        Initialize simulator.
        
        Parameters
        ----------
        seed : int
            Random seed for reproducibility
        """
        np.random.seed(seed)
        self.seed = seed
    
    def generate_frb_catalog(self, n_frbs=100, sky_coverage='full'):
        """
        Generate synthetic FRB catalog.
        
        Parameters
        ----------
        n_frbs : int
            Number of FRBs
        sky_coverage : str
            'full' (entire sky) or 'patch' (SDSS-like patch)
        
        Returns
        -------
        catalog : dict
            FRB catalog with keys: 'RA', 'Dec', 'redshift', 'DM'
        """
        if sky_coverage == 'full':
            ra = np.random.uniform(0, 360, n_frbs)
            dec = np.arcsin(np.random.uniform(-1, 1, n_frbs)) * 180 / np.pi
        elif sky_coverage == 'patch':
            # SDSS-like patch (high-latitude)
            ra = np.random.uniform(130, 140, n_frbs)
            dec = np.random.uniform(40, 50, n_frbs)
        
        # Redshift distribution (realistic for FRBs)
        # Most FRBs have z < 1, with a tail to higher z
        redshift = np.random.beta(2, 5, n_frbs)
        
        # Dispersion measure (DM) - proxy for distance
        # DM ∝ z for cosmological FRBs
        dm = redshift * 1000 + np.random.normal(0, 50, n_frbs)
        dm = np.clip(dm, 0, None)
        
        catalog = {
            'RA': ra,
            'Dec': dec,
            'redshift': redshift,
            'DM': dm,
            'name': [f'FRB_{i:04d}' for i in range(n_frbs)]
        }
        
        return catalog
    
    def generate_galaxy_catalog(self, n_galaxies=5000, sky_coverage='full'):
        """
        Generate synthetic galaxy catalog (mock SDSS-like).
        
        Parameters
        ----------
        n_galaxies : int
            Number of galaxies
        sky_coverage : str
            'full' or 'patch'
        
        Returns
        -------
        catalog : dict
            Galaxy catalog with keys: 'RA', 'Dec', 'redshift'
        """
        if sky_coverage == 'full':
            ra = np.random.uniform(0, 360, n_galaxies)
            dec = np.arcsin(np.random.uniform(-1, 1, n_galaxies)) * 180 / np.pi
        elif sky_coverage == 'patch':
            # Higher galaxy density in survey region
            ra = np.random.uniform(130, 140, n_galaxies)
            dec = np.random.uniform(40, 50, n_galaxies)
        
        # Galaxy redshift distribution (photometric)
        # Peaked around z ~ 0.3 with Gaussian scatter
        redshift = np.abs(np.random.normal(0.35, 0.25, n_galaxies))
        
        # Apparent magnitude
        magnitude = np.random.normal(18, 1, n_galaxies)
        magnitude = np.clip(magnitude, 12, 22)
        
        catalog = {
            'RA': ra,
            'Dec': dec,
            'redshift': redshift,
            'magnitude': magnitude,
            'name': [f'GALAXY_{i:06d}' for i in range(n_galaxies)]
        }
        
        return catalog
    
    def generate_random_catalog(self, n_random, ra_range=(0, 360), dec_range=(-90, 90)):
        """
        Generate random point catalog with same angular distribution.
        
        Parameters
        ----------
        n_random : int
            Number of random points
        ra_range : tuple
            RA range in degrees
        dec_range : tuple
            Dec range in degrees
        
        Returns
        -------
        catalog : dict
            Random catalog
        """
        ra_min, ra_max = ra_range
        dec_min, dec_max = dec_range
        
        # Uniform in RA
        ra = np.random.uniform(ra_min, ra_max, n_random)
        
        # Uniform on sphere: dec = arcsin(uniform(-1, 1))
        dec_rad_min = np.arcsin(np.sin(np.radians(dec_min)))
        dec_rad_max = np.arcsin(np.sin(np.radians(dec_max)))
        dec = np.degrees(np.arcsin(np.random.uniform(
            np.sin(dec_rad_min), 
            np.sin(dec_rad_max), 
            n_random
        )))
        
        catalog = {
            'RA': ra,
            'Dec': dec,
            'random': True
        }
        
        return catalog
    
    def add_poisson_noise(self, catalog, noise_level=0.01):
        """
        Add small positional noise to catalog (arcseconds).
        
        Parameters
        ----------
        catalog : dict
            Input catalog
        noise_level : float
            Noise level in degrees
        
        Returns
        -------
        noisy_catalog : dict
            Catalog with noise added
        """
        noisy_catalog = catalog.copy()
        noisy_catalog['RA'] = catalog['RA'] + np.random.normal(0, noise_level, len(catalog['RA']))
        noisy_catalog['Dec'] = catalog['Dec'] + np.random.normal(0, noise_level, len(catalog['Dec']))
        
        # Wrap RA to [0, 360)
        noisy_catalog['RA'] = noisy_catalog['RA'] % 360
        
        return noisy_catalog


def create_realistic_mock_catalogs(n_frbs=100, n_galaxies=5000, sky_coverage='patch', seed=42):
    """
    Convenience function to create realistic mock catalogs.
    
    Parameters
    ----------
    n_frbs : int
        Number of FRBs
    n_galaxies : int
        Number of galaxies
    sky_coverage : str
        'full' or 'patch'
    seed : int
        Random seed
    
    Returns
    -------
    frb_catalog, galaxy_catalog, random_catalog : dict
        Three catalogs for analysis
    """
    sim = CatalogSimulator(seed=seed)
    
    frb_catalog = sim.generate_frb_catalog(n_frbs, sky_coverage)
    galaxy_catalog = sim.generate_galaxy_catalog(n_galaxies, sky_coverage)
    
    # Generate random catalog with same footprint
    if sky_coverage == 'patch':
        ra_range = (130, 140)
        dec_range = (40, 50)
    else:
        ra_range = (0, 360)
        dec_range = (-90, 90)
    
    random_catalog = sim.generate_random_catalog(n_frbs * 10, ra_range, dec_range)
    
    return frb_catalog, galaxy_catalog, random_catalog
