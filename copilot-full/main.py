"""
Main analysis pipeline for FRB-Galaxy cross-correlation study.

This script performs a comprehensive spatial cross-correlation analysis
between Fast Radio Bursts and galaxies to investigate possible associations.
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.simulation import create_realistic_mock_catalogs
from src.catalog_loader import CatalogLoader, CatalogStatistics
from src.correlation import CrossCorrelationAnalyzer
from src.statistics import StatisticalAnalyzer, ResultInterpreter
from src.plotting import create_all_plots
from src.utils import set_random_seed


def print_header():
    """Print analysis header."""
    print("\n" + "=" * 75)
    print(" FRB-GALAXY CROSS-CORRELATION ANALYSIS")
    print(" Investigating spatial associations for Bachelor Thesis")
    print("=" * 75)


def print_section(title):
    """Print section header."""
    print(f"\n{'─' * 75}")
    print(f"  {title}")
    print(f"{'─' * 75}")


def main():
    """
    Main analysis pipeline.
    """
    # Configuration
    SEED = 42
    OUTPUT_DIR = Path(__file__).parent / 'outputs'
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Set reproducibility
    set_random_seed(SEED)
    
    print_header()
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: DATA LOADING / GENERATION
    # ═══════════════════════════════════════════════════════════════════════
    print_section("STEP 1: CATALOG GENERATION")
    
    print("\nGenerating realistic synthetic catalogs...")
    print("  - Using realistic astrophysical distributions")
    print("  - FRB redshift distribution (beta distribution, mostly z < 1)")
    print("  - Galaxy redshift distribution (peaked around z ~ 0.35)")
    print("  - Random catalog for null hypothesis testing")
    
    frb_catalog, galaxy_catalog, random_catalog = create_realistic_mock_catalogs(
        n_frbs=150,           # Number of FRBs
        n_galaxies=8000,      # Number of galaxies
        sky_coverage='patch', # SDSS-like patch
        seed=SEED
    )
    
    print("✓ Catalogs generated successfully\n")
    
    # Print statistics
    CatalogStatistics.print_catalog_info(frb_catalog, "FRB Catalog")
    CatalogStatistics.print_catalog_info(galaxy_catalog, "Galaxy Catalog")
    CatalogStatistics.print_catalog_info(random_catalog, "Random Catalog")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: CROSS-CORRELATION ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    print_section("STEP 2: CROSS-CORRELATION COMPUTATION")
    
    print("\nInitializing cross-correlation analyzer...")
    analyzer = CrossCorrelationAnalyzer(
        frb_catalog, 
        galaxy_catalog, 
        random_catalog,
        seed=SEED
    )
    
    # Basic 2D correlation
    print("\nComputing 2D angular cross-correlation function ξ(θ)...")
    result_2d = analyzer.compute_2d_correlation(n_bins=25, max_sep=120)
    print("✓ 2D correlation computed")
    
    # Landy-Szalay estimator (superior to naive estimator)
    print("\nComputing Landy-Szalay estimator (more robust)...")
    result_ls = analyzer.compute_landy_szalay_estimator(n_bins=25, max_sep=120)
    print("✓ Landy-Szalay estimator computed")
    
    # Bootstrap error estimation
    print("\nPerforming bootstrap resampling (100 samples) for error estimation...")
    result_bootstrap = analyzer.compute_correlation_with_bootstrap(
        n_bootstrap=100,
        n_bins=25,
        max_sep=120
    )
    print("✓ Bootstrap errors computed")
    
    # Use bootstrap result as final result
    result = result_bootstrap
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: STATISTICAL ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    print_section("STEP 3: STATISTICAL TESTING")
    
    print("\nPerforming statistical significance tests...")
    
    # Correlation significance
    significance = StatisticalAnalyzer.correlation_significance_test(
        result['correlation'],
        result.get('xi_error_bootstrap', result['xi_error']),
        result['bin_centers']
    )
    
    print(f"  - Chi² test: χ² = {significance['chi2']:.2f}, p = {significance['p_value_chi2']:.4f}")
    print(f"  - Detection significance: {significance['detection_sigma']:.2f} σ")
    print(f"  - Mean correlation: ξ̄ = {significance['xi_overall']:.4f}")
    print(f"  - Result: {'SIGNIFICANT' if significance['is_significant'] else 'NOT SIGNIFICANT'}")
    
    # Kolmogorov-Smirnov test on distributions
    print("\nKolmogorov-Smirnov test (distribution comparison):")
    ks_stat, ks_pval = StatisticalAnalyzer.ks_test_separations(
        result['separations_real'],
        random_catalog['RA']  # Use random RA as proxy for random separations
    )
    print(f"  - KS statistic: {ks_stat:.4f}, p-value: {ks_pval:.4f}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4: INTERPRETATION
    # ═══════════════════════════════════════════════════════════════════════
    print_section("STEP 4: SCIENTIFIC INTERPRETATION")
    
    interpretation = ResultInterpreter.interpret_correlation(
        significance,
        result['correlation'],
        result.get('xi_error_bootstrap', result['xi_error'])
    )
    print(interpretation)
    
    # ═══════════════════════════════════════════════════════════════════════
    # STEP 5: VISUALIZATION
    # ═══════════════════════════════════════════════════════════════════════
    print_section("STEP 5: CREATING VISUALIZATIONS")
    
    print("\nGenerating publication-quality plots...")
    create_all_plots(
        result,
        frb_catalog,
        galaxy_catalog,
        random_catalog,
        output_dir=str(OUTPUT_DIR)
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    print_section("ANALYSIS COMPLETE")
    
    print(f"\n📊 Output saved to: {OUTPUT_DIR.absolute()}")
    print(f"\n📈 Generated files:")
    print(f"   • 00_summary_figure.png - Multi-panel summary")
    print(f"   • 01_separation_histogram.png - Angular separation distribution")
    print(f"   • 02_cross_correlation.png - ξ(θ) with errors")
    print(f"   • 03_dd_vs_rr_comparison.png - Observed vs expected pairs")
    print(f"   • 04_bootstrap_errors.png - Bootstrap error estimates")
    print(f"   • 05_sky_distribution.png - Spatial distribution on sky")
    print(f"   • 06_redshift_distribution.png - Redshift histograms")
    
    # Save numerical results
    print(f"\n📝 Summary statistics:")
    print(f"   • Number of FRBs: {len(frb_catalog['RA'])}")
    print(f"   • Number of galaxies: {len(galaxy_catalog['RA'])}")
    print(f"   • Maximum separation analyzed: {result['bin_edges'][-1]:.1f} arcmin")
    print(f"   • Mean correlation: {result['correlation'].mean():.4f}")
    print(f"   • Correlation range: [{result['correlation'].min():.4f}, {result['correlation'].max():.4f}]")
    
    # Final conclusion
    print(f"\n🎯 CONCLUSION:")
    if significance['is_significant']:
        if significance['xi_overall'] > 0:
            print("   ✓ POSITIVE correlation detected (FRBs cluster near galaxies)")
            print("   → FRBs show environmental association with galaxies")
        else:
            print("   ✗ NEGATIVE correlation detected (FRBs avoid galaxies)")
            print("   → FRBs prefer low-density environments")
    else:
        print("   ~ NO significant correlation found")
        print("   → No strong environmental dependence observed")
    
    print("\n" + "=" * 75 + "\n")


if __name__ == '__main__':
    main()
