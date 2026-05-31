# Modul-Dokumentation

Ausführliche Dokumentation der wichtigsten Module.

## src/simulation.py

Erzeugt realistische synthetische Kataloge für FRBs, Galaxien und Random Points.

### CatalogSimulator

```python
sim = CatalogSimulator(seed=42)
frbs = sim.generate_frb_catalog(n_frbs=100, sky_coverage='patch')
galaxies = sim.generate_galaxy_catalog(n_galaxies=5000, sky_coverage='patch')
random = sim.generate_random_catalog(n_random=1000)
```

**FRB Verteilungen**:
- RA/Dec: Gleichverteilt über den Himmel (oder Patch)
- Redshift: Beta(2,5) - realistische Verteilung, meist z < 1
- DM: Korreliert mit Redshift + Rauschen

**Galaxy Verteilungen**:
- RA/Dec: Gleichverteilt
- Redshift: Normal(μ=0.35, σ=0.25) - SDSS-ähnlich
- Magnitude: Normal(μ=18, σ=1)

## src/correlation.py

Implementiert Cross-Correlation Analysis.

### CrossCorrelationAnalyzer

```python
analyzer = CrossCorrelationAnalyzer(frb_cat, galaxy_cat, random_cat)

# Naive Methode
result_2d = analyzer.compute_2d_correlation(n_bins=20, max_sep=60)

# Robust (Landy-Szalay)
result_ls = analyzer.compute_landy_szalay_estimator(n_bins=20, max_sep=60)

# Mit Bootstrap-Fehler
result_boot = analyzer.compute_correlation_with_bootstrap(n_bootstrap=100)
```

**Ausgang**:
```
result = {
    'bin_centers': [1.2, 3.6, 6.0, ...],
    'correlation': [0.012, 0.045, -0.003, ...],  # ξ(θ)
    'xi_error': [0.008, 0.012, 0.010, ...],     # Fehler
    'counts_real': [45, 128, 256, ...],         # Beobachtete Paare
    'counts_random': [41, 135, 247, ...],       # Erwartete Paare
    'separations_real': [0.5, 1.2, ..., 120.3] # Alle Abständen
}
```

## src/statistics.py

Statistische Analyse und Interpretation.

### StatisticalAnalyzer

```python
# Signifikanz-Test
sig_dict = StatisticalAnalyzer.correlation_significance_test(
    xi_values, xi_error, bin_centers
)

# KS-Test für Verteilungen
ks_stat, p_val = StatisticalAnalyzer.ks_test_separations(sep_real, sep_random)
```

### ResultInterpreter

```python
# Automatische Interpretation
interpretation = ResultInterpreter.interpret_correlation(sig_dict, xi, xi_error)
print(interpretation)
```

Gibt wissenschaftliche Interpretation in Textform aus.

## src/plotting.py

Publikationsqualitäts-Grafiken.

### CorrelationPlotter

```python
plotter = CorrelationPlotter(output_dir='outputs', dpi=150)

# Einzelne Plots
plotter.plot_cross_correlation_function(result_dict)
plotter.plot_separation_histogram(separations_real)
plotter.plot_sky_distribution(frb_catalog, galaxy_catalog)

# Oder alle auf einmal
create_all_plots(result_dict, frb_cat, gal_cat, output_dir='outputs')
```

## src/utils.py

Hilfsfunktionen für die Datenverarbeitung.

### Hauptfunktionen

```python
# Winkelabstände
sep = angular_separation(ra1, dec1, ra2, dec2)  # In Arcminuten

# 3D Comoving Distance (wenn Redshift vorhanden)
dist_3d = euclidean_distance_3d(ra1, dec1, z1, ra2, dec2, z2)

# Histogramm
counts, bin_centers = histogram_cross_correlation(separations, bin_edges)

# Bootstrap Resampling
bootstrap_samples = bootstrap_resample(data, n_bootstrap=1000)
```

## src/catalog_loader.py

Laden und Speichern von Katalogen.

### CatalogLoader

```python
loader = CatalogLoader()

# CSV Laden
frbs = loader.load_frb_catalog_from_csv('data/frbs.csv')
galaxies = loader.load_galaxy_catalog_from_csv('data/galaxies.csv')

# FITS Laden
cat = loader.load_from_fits('data/catalog.fits')

# Speichern
loader.save_catalog(catalog, 'output.csv', format='csv')

# Validieren
is_valid, messages = loader.validate_catalog(catalog)
```

### CatalogStatistics

```python
CatalogStatistics.print_catalog_info(catalog, "My Catalog")

# Oder Summary
summary = CatalogStatistics.get_catalog_summary(catalog)
print(summary['n_objects'])
print(summary['z_mean'])
```

---

## Typischer Analyse-Workflow

```python
# 1. Daten laden/erzeugen
frbs, galaxies, random = create_realistic_mock_catalogs(n_frbs=150, n_galaxies=8000)

# 2. Kreuzkorrelation berechnen
analyzer = CrossCorrelationAnalyzer(frbs, galaxies, random)
result = analyzer.compute_correlation_with_bootstrap(n_bootstrap=100)

# 3. Statistik
sig = StatisticalAnalyzer.correlation_significance_test(
    result['correlation'], result['xi_error_bootstrap'], result['bin_centers']
)

# 4. Interpretation
print(ResultInterpreter.interpret_correlation(sig, result['correlation'], result['xi_error_bootstrap']))

# 5. Plots
create_all_plots(result, frbs, galaxies, random)
```

