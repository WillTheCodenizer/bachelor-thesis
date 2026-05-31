"""
Catalog loading and data management.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json


class CatalogLoader:
    """
    Load FRB and galaxy catalogs from various sources.
    """
    
    @staticmethod
    def load_frb_catalog_from_csv(filepath):
        """
        Load FRB catalog from CSV file.
        
        Expected columns: RA, Dec, redshift (optional)
        
        Parameters
        ----------
        filepath : str
            Path to CSV file
        
        Returns
        -------
        catalog : dict
            FRB catalog
        """
        df = pd.read_csv(filepath)
        
        # Standardize column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        if 'ra' not in df.columns or 'dec' not in df.columns:
            raise ValueError("CSV must contain 'RA' and 'Dec' columns")
        
        catalog = {
            'RA': df['ra'].values,
            'Dec': df['dec'].values,
            'name': df.get('name', [f'FRB_{i}' for i in range(len(df))]).values
        }
        
        if 'redshift' in df.columns or 'z' in df.columns:
            z_col = 'redshift' if 'redshift' in df.columns else 'z'
            catalog['redshift'] = df[z_col].values
        
        if 'dm' in df.columns:
            catalog['DM'] = df['dm'].values
        
        return catalog
    
    @staticmethod
    def load_galaxy_catalog_from_csv(filepath):
        """
        Load galaxy catalog from CSV file.
        
        Expected columns: RA, Dec, redshift
        
        Parameters
        ----------
        filepath : str
            Path to CSV file
        
        Returns
        -------
        catalog : dict
            Galaxy catalog
        """
        df = pd.read_csv(filepath)
        
        # Standardize column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        if 'ra' not in df.columns or 'dec' not in df.columns:
            raise ValueError("CSV must contain 'RA' and 'Dec' columns")
        
        catalog = {
            'RA': df['ra'].values,
            'Dec': df['dec'].values,
            'name': df.get('name', [f'GALAXY_{i}' for i in range(len(df))]).values
        }
        
        if 'redshift' in df.columns or 'z' in df.columns:
            z_col = 'redshift' if 'redshift' in df.columns else 'z'
            catalog['redshift'] = df[z_col].values
        
        if 'magnitude' in df.columns:
            catalog['magnitude'] = df['magnitude'].values
        
        return catalog
    
    @staticmethod
    def load_from_fits(filepath):
        """
        Load catalog from FITS file (if astropy available).
        
        Parameters
        ----------
        filepath : str
            Path to FITS file
        
        Returns
        -------
        catalog : dict
            Catalog
        """
        try:
            from astropy.table import Table
            table = Table.read(filepath)
            
            # Convert to dictionary
            catalog = {}
            for colname in table.colnames:
                catalog[colname.lower()] = table[colname].data
            
            return catalog
        except ImportError:
            raise ImportError("astropy required for FITS support")
    
    @staticmethod
    def save_catalog(catalog, filepath, format='csv'):
        """
        Save catalog to file.
        
        Parameters
        ----------
        catalog : dict
            Catalog to save
        filepath : str
            Output path
        format : str
            'csv' or 'json'
        """
        if format == 'csv':
            df = pd.DataFrame(catalog)
            df.to_csv(filepath, index=False)
        elif format == 'json':
            # Convert numpy arrays to lists
            catalog_json = {k: v.tolist() if isinstance(v, np.ndarray) else v 
                           for k, v in catalog.items()}
            with open(filepath, 'w') as f:
                json.dump(catalog_json, f, indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    @staticmethod
    def validate_catalog(catalog, required_keys=None):
        """
        Validate catalog structure.
        
        Parameters
        ----------
        catalog : dict
            Catalog to validate
        required_keys : list, optional
            Keys that must be present
        
        Returns
        -------
        is_valid : bool
            Whether catalog is valid
        messages : list
            Validation messages
        """
        messages = []
        
        if not isinstance(catalog, dict):
            messages.append("Catalog must be a dictionary")
            return False, messages
        
        if required_keys is None:
            required_keys = ['RA', 'Dec']
        
        for key in required_keys:
            if key not in catalog:
                messages.append(f"Missing required key: {key}")
        
        # Check array lengths
        if 'RA' in catalog and 'Dec' in catalog:
            if len(catalog['RA']) != len(catalog['Dec']):
                messages.append("RA and Dec have different lengths")
        
        if len(messages) == 0:
            messages.append("✓ Catalog is valid")
            return True, messages
        else:
            return False, messages


class CatalogStatistics:
    """
    Compute statistics on catalogs.
    """
    
    @staticmethod
    def print_catalog_info(catalog, name='Catalog'):
        """
        Print information about a catalog.
        
        Parameters
        ----------
        catalog : dict
            Catalog
        name : str
            Name for printing
        """
        print(f"\n{name} Statistics")
        print("=" * 50)
        print(f"Number of objects: {len(catalog['RA'])}")
        print(f"RA range: [{catalog['RA'].min():.2f}, {catalog['RA'].max():.2f}] degrees")
        print(f"Dec range: [{catalog['Dec'].min():.2f}, {catalog['Dec'].max():.2f}] degrees")
        
        if 'redshift' in catalog:
            print(f"Redshift range: [{catalog['redshift'].min():.4f}, {catalog['redshift'].max():.4f}]")
            print(f"Mean redshift: {catalog['redshift'].mean():.4f}")
        
        if 'DM' in catalog:
            print(f"DM range: [{catalog['DM'].min():.1f}, {catalog['DM'].max():.1f}] pc/cm³")
        
        if 'magnitude' in catalog:
            print(f"Magnitude range: [{catalog['magnitude'].min():.2f}, {catalog['magnitude'].max():.2f}]")
    
    @staticmethod
    def get_catalog_summary(catalog):
        """
        Get summary statistics.
        
        Parameters
        ----------
        catalog : dict
            Catalog
        
        Returns
        -------
        summary : dict
            Summary statistics
        """
        summary = {
            'n_objects': len(catalog['RA']),
            'ra_mean': float(catalog['RA'].mean()),
            'ra_std': float(catalog['RA'].std()),
            'dec_mean': float(catalog['Dec'].mean()),
            'dec_std': float(catalog['Dec'].std()),
        }
        
        if 'redshift' in catalog:
            summary['z_mean'] = float(catalog['redshift'].mean())
            summary['z_median'] = float(np.median(catalog['redshift']))
            summary['z_std'] = float(catalog['redshift'].std())
        
        return summary
