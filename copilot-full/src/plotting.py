"""
Plotting and visualization functions.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class CorrelationPlotter:
    """
    Create publication-quality plots for cross-correlation analysis.
    """
    
    def __init__(self, output_dir='outputs', figsize=(10, 8), dpi=150):
        """
        Initialize plotter.
        
        Parameters
        ----------
        output_dir : str
            Output directory for plots
        figsize : tuple
            Figure size (width, height) in inches
        dpi : int
            Resolution for saved figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.figsize = figsize
        self.dpi = dpi
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def plot_separation_histogram(self, separations_real, separations_random=None, 
                                   title='Angular Separation Distribution',
                                   xlabel='Angular Separation (arcmin)',
                                   filename='01_separation_histogram.png'):
        """
        Plot histogram of separations.
        
        Parameters
        ----------
        separations_real : array
            Real separations
        separations_random : array, optional
            Random separations for comparison
        title : str
            Plot title
        xlabel : str
            X-axis label
        filename : str
            Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        bins = np.linspace(0, max(separations_real.max(), 
                                  separations_random.max() if separations_random is not None else 0), 50)
        
        ax.hist(separations_real, bins=bins, alpha=0.7, label='Real FRB-Galaxy', 
                color='steelblue', edgecolor='black')
        
        if separations_random is not None:
            ax.hist(separations_random, bins=bins, alpha=0.5, label='Random-Galaxy',
                    color='orange', edgecolor='black')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Counts', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def plot_cross_correlation_function(self, result_dict, 
                                        title='2D Cross-Correlation Function ξ(θ)',
                                        filename='02_cross_correlation.png',
                                        with_error_band=True):
        """
        Plot cross-correlation function with errors.
        
        Parameters
        ----------
        result_dict : dict
            Result from CrossCorrelationAnalyzer.compute_2d_correlation()
        title : str
            Plot title
        filename : str
            Output filename
        with_error_band : bool
            Show error band
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        bin_centers = result_dict['bin_centers']
        xi = result_dict['correlation']
        xi_error = result_dict['xi_error']
        
        # Plot correlation
        ax.plot(bin_centers, xi, 'o-', linewidth=2.5, markersize=8, 
                color='darkred', label='ξ(θ)', zorder=3)
        
        # Error band
        if with_error_band:
            ax.fill_between(bin_centers, xi - xi_error, xi + xi_error,
                            alpha=0.25, color='darkred', label='1σ error')
        
        # Zero line
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('Angular Separation θ (arcmin)', fontsize=12)
        ax.set_ylabel('Cross-Correlation ξ(θ)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def plot_comparison_dd_rr(self, result_dict,
                              title='Data-Data vs Random-Random Pairs',
                              filename='03_dd_vs_rr_comparison.png'):
        """
        Plot comparison of observed vs expected pair counts.
        
        Parameters
        ----------
        result_dict : dict
            Result dictionary
        title : str
            Plot title
        filename : str
            Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        bin_centers = result_dict['bin_centers']
        
        ax.plot(bin_centers, result_dict['counts_real'], 'o-', linewidth=2.5, 
                markersize=8, label='DD (Real FRB-Galaxy)', color='darkred')
        ax.plot(bin_centers, result_dict['counts_random'], 's-', linewidth=2.5,
                markersize=8, label='RR (Random expectation)', color='steelblue', alpha=0.7)
        
        ax.set_xlabel('Angular Separation θ (arcmin)', fontsize=12)
        ax.set_ylabel('Pair Counts', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def plot_bootstrap_errors(self, result_dict, title='Bootstrap Error Estimation',
                              filename='04_bootstrap_errors.png'):
        """
        Plot correlation with bootstrap errors.
        
        Parameters
        ----------
        result_dict : dict
            Result from compute_correlation_with_bootstrap()
        title : str
            Plot title
        filename : str
            Output filename
        """
        if 'xi_error_bootstrap' not in result_dict:
            print("⚠ Bootstrap errors not available in result_dict")
            return
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        bin_centers = result_dict['bin_centers']
        xi = result_dict['correlation']
        xi_error_bootstrap = result_dict['xi_error_bootstrap']
        
        ax.plot(bin_centers, xi, 'o-', linewidth=2.5, markersize=8,
                color='darkred', label='ξ(θ)', zorder=3)
        
        ax.fill_between(bin_centers, xi - xi_error_bootstrap, xi + xi_error_bootstrap,
                        alpha=0.3, color='darkred', label='Bootstrap 1σ')
        
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('Angular Separation θ (arcmin)', fontsize=12)
        ax.set_ylabel('Cross-Correlation ξ(θ)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def plot_sky_distribution(self, frb_catalog, galaxy_catalog, 
                              title='Sky Distribution: FRBs and Galaxies',
                              filename='05_sky_distribution.png'):
        """
        Plot spatial distribution on sky.
        
        Parameters
        ----------
        frb_catalog : dict
            FRB catalog
        galaxy_catalog : dict
            Galaxy catalog
        title : str
            Plot title
        filename : str
            Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize, subplot_kw=dict(projection='rectilinear'))
        
        # Galaxies
        ax.scatter(galaxy_catalog['RA'], galaxy_catalog['Dec'], 
                   alpha=0.3, s=20, label='Galaxies', color='lightblue', edgecolors='none')
        
        # FRBs (larger markers)
        ax.scatter(frb_catalog['RA'], frb_catalog['Dec'],
                   alpha=0.8, s=100, label='FRBs', color='red', 
                   marker='*', edgecolors='darkred', linewidth=1)
        
        ax.set_xlabel('Right Ascension (degrees)', fontsize=12)
        ax.set_ylabel('Declination (degrees)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def plot_redshift_distribution(self, frb_catalog, galaxy_catalog,
                                   title='Redshift Distributions',
                                   filename='06_redshift_distribution.png'):
        """
        Plot redshift distributions.
        
        Parameters
        ----------
        frb_catalog : dict
            FRB catalog
        galaxy_catalog : dict
            Galaxy catalog
        title : str
            Plot title
        filename : str
            Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.hist(frb_catalog['redshift'], bins=20, alpha=0.7, label='FRBs',
                color='darkred', edgecolor='black')
        ax.hist(galaxy_catalog['redshift'], bins=30, alpha=0.5, label='Galaxies',
                color='steelblue', edgecolor='black')
        
        ax.set_xlabel('Redshift (z)', fontsize=12)
        ax.set_ylabel('Counts', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()
    
    def create_summary_figure(self, result_dict, frb_catalog, galaxy_catalog,
                              filename='00_summary_figure.png'):
        """
        Create multi-panel summary figure.
        
        Parameters
        ----------
        result_dict : dict
            Cross-correlation result
        frb_catalog : dict
            FRB catalog
        galaxy_catalog : dict
            Galaxy catalog
        filename : str
            Output filename
        """
        fig = plt.figure(figsize=(15, 10))
        
        # Panel 1: Sky distribution
        ax1 = plt.subplot(2, 3, 1)
        ax1.scatter(galaxy_catalog['RA'], galaxy_catalog['Dec'],
                   alpha=0.2, s=10, color='lightblue')
        ax1.scatter(frb_catalog['RA'], frb_catalog['Dec'],
                   alpha=0.8, s=80, color='red', marker='*', edgecolors='darkred')
        ax1.set_xlabel('RA (deg)', fontsize=10)
        ax1.set_ylabel('Dec (deg)', fontsize=10)
        ax1.set_title('Sky Distribution', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: Separation histogram
        ax2 = plt.subplot(2, 3, 2)
        ax2.hist(result_dict['separations_real'], bins=50, color='darkred',
                alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Angular Separation (arcmin)', fontsize=10)
        ax2.set_ylabel('Counts', fontsize=10)
        ax2.set_title('Separation Distribution', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Panel 3: Cross-correlation
        ax3 = plt.subplot(2, 3, 3)
        ax3.errorbar(result_dict['bin_centers'], result_dict['correlation'],
                    yerr=result_dict['xi_error'], fmt='o-', color='darkred',
                    capsize=5, capthick=2, markersize=6, linewidth=2)
        ax3.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax3.set_xlabel('θ (arcmin)', fontsize=10)
        ax3.set_ylabel('ξ(θ)', fontsize=10)
        ax3.set_title('Cross-Correlation Function', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Panel 4: DD vs RR
        ax4 = plt.subplot(2, 3, 4)
        ax4.plot(result_dict['bin_centers'], result_dict['counts_real'],
                'o-', label='DD', color='darkred', linewidth=2)
        ax4.plot(result_dict['bin_centers'], result_dict['counts_random'],
                's-', label='RR', color='steelblue', linewidth=2, alpha=0.7)
        ax4.set_xlabel('θ (arcmin)', fontsize=10)
        ax4.set_ylabel('Pair Counts', fontsize=10)
        ax4.set_title('Observed vs Expected', fontsize=11, fontweight='bold')
        ax4.set_yscale('log')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)
        
        # Panel 5: Redshift distributions
        ax5 = plt.subplot(2, 3, 5)
        ax5.hist(frb_catalog['redshift'], bins=15, alpha=0.7, label='FRBs',
                color='darkred', edgecolor='black')
        ax5.hist(galaxy_catalog['redshift'], bins=25, alpha=0.5, label='Galaxies',
                color='steelblue', edgecolor='black')
        ax5.set_xlabel('Redshift (z)', fontsize=10)
        ax5.set_ylabel('Counts', fontsize=10)
        ax5.set_title('Redshift Distributions', fontsize=11, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Panel 6: Stats text
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        stats_text = f"""
ANALYSIS SUMMARY
{'─' * 30}
N(FRBs): {len(frb_catalog['RA'])}
N(Galaxies): {len(galaxy_catalog['RA'])}
N(bins): {len(result_dict['bin_centers'])}

Mean ξ(θ): {result_dict['correlation'].mean():.4f}
Max ξ(θ): {result_dict['correlation'].max():.4f}
Min ξ(θ): {result_dict['correlation'].min():.4f}

Total DD pairs: {np.sum(result_dict['counts_real']):.0f}
Total RR pairs: {np.sum(result_dict['counts_random']):.0f}
        """
        
        ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes,
                fontsize=9, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.suptitle('FRB-Galaxy Cross-Correlation Analysis', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved: {filepath}")
        plt.close()


def create_all_plots(result_dict, frb_catalog, galaxy_catalog, 
                     random_catalog=None, output_dir='outputs'):
    """
    Create all standard plots.
    
    Parameters
    ----------
    result_dict : dict
        Cross-correlation result
    frb_catalog : dict
        FRB catalog
    galaxy_catalog : dict
        Galaxy catalog
    random_catalog : dict, optional
        Random catalog
    output_dir : str
        Output directory
    """
    plotter = CorrelationPlotter(output_dir=output_dir)
    
    # Summary figure
    plotter.create_summary_figure(result_dict, frb_catalog, galaxy_catalog)
    
    # Individual plots
    plotter.plot_sky_distribution(frb_catalog, galaxy_catalog)
    plotter.plot_separation_histogram(result_dict['separations_real'])
    plotter.plot_cross_correlation_function(result_dict)
    plotter.plot_comparison_dd_rr(result_dict)
    plotter.plot_redshift_distribution(frb_catalog, galaxy_catalog)
    
    if 'xi_error_bootstrap' in result_dict:
        plotter.plot_bootstrap_errors(result_dict)
    
    print(f"\n✓ All plots saved to: {output_dir}")
