"""
Beispiel-Skript: Verwendung mit echten Daten

Dieses Skript zeigt, wie man das Framework mit echten FRB- und Galaxy-Katalogen verwendet.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.catalog_loader import CatalogLoader, CatalogStatistics
from src.correlation import CrossCorrelationAnalyzer
from src.statistics import StatisticalAnalyzer, ResultInterpreter
from src.plotting import create_all_plots
from src.utils import set_random_seed


def analyze_real_data(frb_csv_path, galaxy_csv_path, output_dir='outputs', seed=42):
    """
    Analyse mit echten CSV-Daten.
    
    CSV-Format für FRBs (frbs.csv):
    ```
    name,RA,Dec,redshift,DM
    FRB_001,130.5,42.3,0.45,568
    FRB_002,131.2,43.1,0.62,723
    ```
    
    CSV-Format für Galaxien (galaxies.csv):
    ```
    name,RA,Dec,redshift,magnitude
    GALAXY_001,130.6,42.4,0.35,18.2
    GALAXY_002,131.3,43.2,0.41,17.8
    ```
    """
    
    set_random_seed(seed)
    
    # 1. Daten laden
    print("Lade Kataloge...")
    loader = CatalogLoader()
    
    frb_catalog = loader.load_frb_catalog_from_csv(frb_csv_path)
    galaxy_catalog = loader.load_galaxy_catalog_from_csv(galaxy_csv_path)
    
    # Validiere Kataloge
    is_valid_frb, msg_frb = loader.validate_catalog(frb_catalog)
    is_valid_gal, msg_gal = loader.validate_catalog(galaxy_catalog)
    
    print(f"FRB Katalog: {msg_frb[0]}")
    print(f"Galaxy Katalog: {msg_gal[0]}")
    
    # Statistiken
    CatalogStatistics.print_catalog_info(frb_catalog, "FRB Katalog")
    CatalogStatistics.print_catalog_info(galaxy_catalog, "Galaxy Katalog")
    
    # 2. Kreuzkorrelation
    print("\nBerechne Kreuzkorrelation...")
    
    analyzer = CrossCorrelationAnalyzer(frb_catalog, galaxy_catalog, seed=seed)
    
    # Mit Bootstrap-Fehler
    result = analyzer.compute_correlation_with_bootstrap(
        n_bootstrap=100,
        n_bins=25,
        max_sep=120
    )
    
    # 3. Statistik
    print("Führe statistische Tests durch...")
    significance = StatisticalAnalyzer.correlation_significance_test(
        result['correlation'],
        result.get('xi_error_bootstrap', result['xi_error']),
        result['bin_centers']
    )
    
    # 4. Interpretation
    interpretation = ResultInterpreter.interpret_correlation(
        significance,
        result['correlation'],
        result.get('xi_error_bootstrap', result['xi_error'])
    )
    print(interpretation)
    
    # 5. Plots
    print("\nGeneriere Plots...")
    create_all_plots(result, frb_catalog, galaxy_catalog, output_dir=output_dir)
    
    return result, significance


def analyze_fits_data(frb_fits_path, galaxy_fits_path, output_dir='outputs', seed=42):
    """
    Analyse mit FITS-Dateien (erfordert astropy).
    """
    set_random_seed(seed)
    
    print("Lade FITS-Kataloge...")
    loader = CatalogLoader()
    
    # Die FITS-Spalten müssen 'ra' und 'dec' heißen
    frb_catalog = loader.load_from_fits(frb_fits_path)
    galaxy_catalog = loader.load_from_fits(galaxy_fits_path)
    
    # Weitere Verarbeitung wie oben...
    analyzer = CrossCorrelationAnalyzer(frb_catalog, galaxy_catalog, seed=seed)
    result = analyzer.compute_correlation_with_bootstrap(n_bootstrap=100)
    
    significance = StatisticalAnalyzer.correlation_significance_test(
        result['correlation'],
        result['xi_error_bootstrap'],
        result['bin_centers']
    )
    
    print(ResultInterpreter.interpret_correlation(
        significance,
        result['correlation'],
        result['xi_error_bootstrap']
    ))
    
    create_all_plots(result, frb_catalog, galaxy_catalog, output_dir=output_dir)
    
    return result, significance


if __name__ == '__main__':
    """
    Beispiel-Aufruf:
    
    # Mit CSV-Dateien
    python example_real_data.py
    
    # Mit FITS-Dateien (Falls vorhanden)
    # result, sig = analyze_fits_data('data/frbs.fits', 'data/galaxies.fits')
    """
    
    # Beispiel: CSV-Dateien (müssen vorhanden sein)
    frb_csv = Path('data/frbs.csv')
    galaxy_csv = Path('data/galaxies.csv')
    
    if not frb_csv.exists() or not galaxy_csv.exists():
        print("ℹ️ CSV-Dateien nicht vorhanden.")
        print("   Erstelle data/frbs.csv und data/galaxies.csv mit folgendem Format:")
        print("\n   frbs.csv:")
        print("   name,RA,Dec,redshift,DM")
        print("   FRB_001,130.5,42.3,0.45,568")
        print("\n   galaxies.csv:")
        print("   name,RA,Dec,redshift,magnitude")
        print("   GALAXY_001,130.6,42.4,0.35,18.2")
    else:
        result, significance = analyze_real_data(str(frb_csv), str(galaxy_csv))
