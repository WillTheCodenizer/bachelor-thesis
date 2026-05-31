"""
Cross-correlation analysis between FRBs and galaxies.
"""

import numpy as np
from .utils import angular_separation, histogram_cross_correlation


class CrossCorrelationAnalyzer:
    """
    Compute 2D and 3D cross-correlation functions.
    """
    
    def __init__(self, frb_catalog, galaxy_catalog, random_catalog=None, seed=42):
        """
        Initialize analyzer.
        
        Parameters
        ----------
        frb_catalog : dict
            FRB catalog with 'RA', 'Dec' keys
        galaxy_catalog : dict
            Galaxy catalog with 'RA', 'Dec' keys
        random_catalog : dict, optional
            Random catalog for comparison
        seed : int
            Random seed
        """
        self.frb_catalog = frb_catalog
        self.galaxy_catalog = galaxy_catalog
        self.random_catalog = random_catalog
        self.seed = seed
        np.random.seed(seed)
    
    def compute_pairwise_separations(self, catalog1_ra, catalog1_dec, 
                                     catalog2_ra, catalog2_dec):
        """
        Compute pairwise separations between all objects.
        
        Parameters
        ----------
        catalog1_ra, catalog1_dec : array
            Coordinates of first catalog
        catalog2_ra, catalog2_dec : array
            Coordinates of second catalog
        
        Returns
        -------
        separations : array
            All pairwise separations (flattened)
        """
        separations = []
        for i in range(len(catalog1_ra)):
            sep = angular_separation(catalog1_ra[i], catalog1_dec[i],
                                     catalog2_ra, catalog2_dec)
            separations.append(sep)
        
        return np.concatenate(separations)
    
    def compute_2d_correlation(self, bin_edges=None, n_bins=20, max_sep=60):
        """
        Compute 2D angular cross-correlation function.
        
        Parameters
        ----------
        bin_edges : array, optional
            Custom bin edges (in arcminutes)
        n_bins : int
            Number of bins if bin_edges not provided
        max_sep : float
            Maximum separation (arcminutes)
        
        Returns
        -------
        result : dict
            Dictionary containing:
            - 'bin_centers': center of each bin
            - 'counts_real': histogram of real FRB-galaxy separations
            - 'counts_random': histogram of random-galaxy separations
            - 'correlation': cross-correlation function ξ(θ)
            - 'xi_error': errors on correlation
        """
        if bin_edges is None:
            bin_edges = np.linspace(0, max_sep, n_bins + 1)
        
        # Real FRB-Galaxy separations
        sep_real = self.compute_pairwise_separations(
            self.frb_catalog['RA'], self.frb_catalog['Dec'],
            self.galaxy_catalog['RA'], self.galaxy_catalog['Dec']
        )
        
        counts_real, bin_centers = histogram_cross_correlation(sep_real, bin_edges)
        
        # Random-Galaxy separations (for normalization)
        if self.random_catalog is not None:
            sep_random = self.compute_pairwise_separations(
                self.random_catalog['RA'], self.random_catalog['Dec'],
                self.galaxy_catalog['RA'], self.galaxy_catalog['Dec']
            )
            counts_random, _ = histogram_cross_correlation(sep_random, bin_edges)
        else:
            # If no random catalog, use uniform expectation
            bin_width = bin_edges[1] - bin_edges[0]
            expected_pairs = len(self.frb_catalog['RA']) * len(self.galaxy_catalog['RA'])
            counts_random = expected_pairs * bin_width / (np.pi * max_sep**2) * np.ones_like(counts_real)
        
        # Normalize to avoid division by zero
        counts_random = np.maximum(counts_random, 1)
        
        # Cross-correlation function: ξ(θ) = (DD / RR) - 1
        correlation = (counts_real / counts_random) - 1
        
        # Poisson error estimate
        xi_error = np.sqrt(1/np.maximum(counts_real, 1) + 1/np.maximum(counts_random, 1))
        
        result = {
            'bin_centers': bin_centers,
            'bin_edges': bin_edges,
            'counts_real': counts_real,
            'counts_random': counts_random,
            'correlation': correlation,
            'xi_error': xi_error,
            'separations_real': sep_real
        }
        
        return result
    
    def compute_landy_szalay_estimator(self, bin_edges=None, n_bins=20, max_sep=60):
        """
        Compute Landy-Szalay estimator for cross-correlation.
        
        ξ_LS = (DD - 2*DR + RR) / RR
        
        Where:
        DD = data-data pairs
        DR = data-random pairs
        RR = random-random pairs
        
        Parameters
        ----------
        bin_edges : array, optional
            Custom bin edges (in arcminutes)
        n_bins : int
            Number of bins if bin_edges not provided
        max_sep : float
            Maximum separation (arcminutes)
        
        Returns
        -------
        result : dict
            Dictionary containing correlation and error estimates
        """
        if bin_edges is None:
            bin_edges = np.linspace(0, max_sep, n_bins + 1)
        
        # DD: FRB-Galaxy pairs
        sep_dd = self.compute_pairwise_separations(
            self.frb_catalog['RA'], self.frb_catalog['Dec'],
            self.galaxy_catalog['RA'], self.galaxy_catalog['Dec']
        )
        counts_dd, bin_centers = histogram_cross_correlation(sep_dd, bin_edges)
        
        if self.random_catalog is not None:
            # DR: Random-Galaxy pairs
            sep_dr = self.compute_pairwise_separations(
                self.random_catalog['RA'], self.random_catalog['Dec'],
                self.galaxy_catalog['RA'], self.galaxy_catalog['Dec']
            )
            counts_dr, _ = histogram_cross_correlation(sep_dr, bin_edges)
            
            # RR: Random-Random pairs (approximated)
            sep_rr = self.compute_pairwise_separations(
                self.random_catalog['RA'], self.random_catalog['Dec'],
                self.random_catalog['RA'], self.random_catalog['Dec']
            )
            counts_rr, _ = histogram_cross_correlation(sep_rr, bin_edges)
        else:
            # Fallback
            counts_dr = counts_dd
            counts_rr = counts_dd
        
        # Normalize by counts
        counts_rr = np.maximum(counts_rr, 1)
        counts_dr = np.maximum(counts_dr, 1)
        
        # Landy-Szalay estimator
        xi_ls = (counts_dd - 2*counts_dr + counts_rr) / counts_rr
        
        # Error estimate
        xi_error = np.sqrt(counts_dd) / counts_rr
        
        result = {
            'bin_centers': bin_centers,
            'bin_edges': bin_edges,
            'counts_dd': counts_dd,
            'counts_dr': counts_dr,
            'counts_rr': counts_rr,
            'correlation': xi_ls,
            'xi_error': xi_error,
            'estimator': 'Landy-Szalay',
            'separations_real': sep_dd
        }
        
        return result
    
    def compute_correlation_with_bootstrap(self, n_bootstrap=100, bin_edges=None, 
                                           n_bins=20, max_sep=60):
        """
        Compute correlation with bootstrap error estimation.
        
        Parameters
        ----------
        n_bootstrap : int
            Number of bootstrap samples
        bin_edges : array, optional
            Custom bin edges
        n_bins : int
            Number of bins
        max_sep : float
            Maximum separation
        
        Returns
        -------
        result : dict
            Dictionary with correlation and bootstrap errors
        """
        if bin_edges is None:
            bin_edges = np.linspace(0, max_sep, n_bins + 1)
        
        # Compute nominal correlation
        result = self.compute_2d_correlation(bin_edges)
        
        # Bootstrap: resample FRBs
        xi_bootstrap = np.zeros((n_bootstrap, len(result['bin_centers'])))
        
        np.random.seed(self.seed)
        n_frbs = len(self.frb_catalog['RA'])
        
        for b in range(n_bootstrap):
            # Resample FRBs with replacement
            indices = np.random.choice(n_frbs, size=n_frbs, replace=True)
            
            # Compute separation for resampled FRBs
            sep_boot = []
            for idx in indices:
                sep = angular_separation(
                    self.frb_catalog['RA'][idx], 
                    self.frb_catalog['Dec'][idx],
                    self.galaxy_catalog['RA'], 
                    self.galaxy_catalog['Dec']
                )
                sep_boot.append(sep)
            
            sep_boot = np.concatenate(sep_boot)
            counts_boot, _ = histogram_cross_correlation(sep_boot, bin_edges)
            
            # Normalize
            xi_bootstrap[b] = (counts_boot / result['counts_random']) - 1
        
        # Bootstrap error
        xi_error_bootstrap = np.std(xi_bootstrap, axis=0)
        
        result['xi_error_bootstrap'] = xi_error_bootstrap
        result['xi_bootstrap_samples'] = xi_bootstrap
        
        return result
