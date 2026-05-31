# FRB-Galaxy Cross-Correlation Analysis für Bachelorarbeit

Wissenschaftliches Forschungsprojekt zur Untersuchung räumlicher Korrelationen zwischen Fast Radio Bursts (FRBs) und Galaxien.

## 🎯 Projekt-Übersicht

Dieses Projekt implementiert eine umfassende statistische Analyse der räumlichen Kreuzkorrelation zwischen FRBs und Galaxien. Das Ziel ist zu untersuchen, ob FRBs bevorzugt in der Nähe von Galaxien auftreten (was auf eine mögliche Verbindung zu stellar systems oder Galaxienumgebungen hinweiten würde) oder ob sie eine zufällige räumliche Verteilung zeigen.

### Forschungsfrage
**Gibt es eine statistisch signifikante räumliche Korrelation zwischen FRBs und Galaxien?**

## 📦 Features

### Wissenschaftliche Methoden
- ✓ **2D Kreuzkorrelationsanalyse**: Berechnung von ξ(θ) als Funktion der Winkelabstände
- ✓ **Landy-Szalay Estimator**: Robuste Schätzung mit Random Catalog Normalisierung
- ✓ **Bootstrap Error Estimation**: Nicht-parametrische Fehlerquantifizierung
- ✓ **Monte Carlo Testing**: Vergleich mit Nullhypothese (keine Korrelation)
- ✓ **Statistische Signifikanztests**: Chi², KS-Test, p-Werte

### Daten & Simulation
- ✓ **Realistische Katalog-Generierung**: Astrophysikalisch plausible Verteilungen
- ✓ **FRB Redshift Distribution**: Beta-Verteilung (meist z < 1)
- ✓ **Galaxy-Katalog (Mock SDSS)**: Photometrische Rotverschiebung um z ~ 0.35
- ✓ **Random Katalog**: Für korrekte Nullhypothese-Normalisierung
- ✓ **Support für externe Daten**: CSV und FITS Format

### Visualisierungen
- ✓ Multi-Panel Summary Figure
- ✓ Winkelabstands-Histogramme
- ✓ Cross-Correlation Function ξ(θ) mit Fehlerbalken
- ✓ DD vs RR Vergleich (beobachtet vs erwartet)
- ✓ Sky Distribution (Himmelssphäre)
- ✓ Redshift Verteilungen
- ✓ Bootstrap Error Bands

## 🚀 Schnellstart

### Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Ausführung

```bash
# Standard-Analyse durchführen
python main.py

# Mit detailliertem Output
python main.py 2>&1 | tee analysis.log
```

### Output

```
outputs/
├── 00_summary_figure.png          # Übersichts-Grafik
├── 01_separation_histogram.png    # Winkelabstände
├── 02_cross_correlation.png       # ξ(θ) Ergebnis
├── 03_dd_vs_rr_comparison.png     # Daten vs Random
├── 04_bootstrap_errors.png        # Bootstrap Fehler
├── 05_sky_distribution.png        # Räumliche Verteilung
└── 06_redshift_distribution.png   # Redshift Histogramme
```

## 📊 Projektstruktur

```
bachelor_thesis/
├── src/
│   ├── __init__.py
│   ├── simulation.py              # Katalog-Generierung
│   ├── catalog_loader.py          # Daten-Laden/Speichern
│   ├── correlation.py             # Kreuzkorrelations-Berechnung
│   ├── statistics.py              # Statistische Tests & Interpretation
│   ├── plotting.py                # Visualisierungen
│   └── utils.py                   # Hilfsfunktionen
├── data/                          # Externe Datakatalog
├── outputs/                       # Ergebnisse & Plots
├── main.py                        # Einstiegspunkt
├── requirements.txt               # Python-Abhängigkeiten
└── README.md                      # Diese Datei
```

## 🔬 Wissenschaftliche Methodik

### Kreuzkorrelationsfunktion

Die 2D Kreuzkorrelationsfunktion wird als Funktion des Winkelabstandes θ berechnet:

$$\xi(\theta) = \frac{DD(\theta)}{RR(\theta)} - 1$$

Wobei:
- **DD(θ)**: Anzahl der FRB-Galaxy Paare bei Abstand θ
- **RR(θ)**: Erwartete Anzahl bei Zufallsverteilung

### Landy-Szalay Estimator

Für robustere Schätzung mit Random Katalog DR:

$$\xi_{LS}(\theta) = \frac{DD(\theta) - 2 \cdot DR(\theta) + RR(\theta)}{RR(\theta)}$$

Dies reduziert Sampling-Fehler und Poisson-Rauschen.

### Fehlerquantifizierung

1. **Poisson Fehler**: $\sigma_i = \sqrt{1/DD_i + 1/RR_i}$
2. **Bootstrap Resampling**: Zufällige Resampling der FRB-Sample (n=100)
3. **Signifikanztests**: Chi², Kolmogorov-Smirnov, p-Werte

### Nullhypothese

**H₀**: FRBs und Galaxien sind räumlich unabhängig (Poisson-Prozesse)

Wird verworfen wenn: $p < 0.05$ oder $\xi_{overall} > 2\sigma$

## 💻 Verwendung mit eigenen Daten

### CSV Format

**FRBs (frbs.csv)**:
```csv
name,RA,Dec,redshift,DM
FRB_001,130.5,42.3,0.45,568
FRB_002,131.2,43.1,0.62,723
...
```

**Galaxies (galaxies.csv)**:
```csv
name,RA,Dec,redshift,magnitude
GALAXY_001,130.6,42.4,0.35,18.2
GALAXY_002,131.3,43.2,0.41,17.8
...
```

### Code-Beispiel

```python
from src.catalog_loader import CatalogLoader
from src.correlation import CrossCorrelationAnalyzer

# Daten laden
loader = CatalogLoader()
frb_cat = loader.load_frb_catalog_from_csv('data/frbs.csv')
gal_cat = loader.load_galaxy_catalog_from_csv('data/galaxies.csv')

# Analyse
analyzer = CrossCorrelationAnalyzer(frb_cat, gal_cat)
result = analyzer.compute_2d_correlation()
```

## 📈 Beispiel-Ergebnisse

### Mögliche Szenarien

**Szenario 1: Positive Korrelation**
```
Detection significance: 3.45 σ
Chi² p-value: 0.0012
Mean ξ(θ): 0.0856 ± 0.0125

→ FRBs CLUSTERN um Galaxien
  Mögliche Deutung: Assoziation mit Galaxienumgebungen
```

**Szenario 2: Keine signifikante Korrelation**
```
Detection significance: 0.82 σ
Chi² p-value: 0.4156
Mean ξ(θ): 0.0032 ± 0.0089

→ KEINE signifikante Korrelation
  Mögliche Deutung: Unabhängige räumliche Verteilung
```

## 🔧 Konfiguration

Anpassbare Parameter in `main.py`:

```python
SEED = 42                    # Reproduzierbarkeit
n_frbs = 150                 # Anzahl der FRBs
n_galaxies = 8000            # Anzahl der Galaxien
n_bootstrap = 100            # Bootstrap-Stichproben
max_separation = 120 arcmin  # Maximale Winkelabstand
n_bins = 25                  # Anzahl der Histogramm-Bins
```

## 📚 Referenzen

- Landy, S. A., & Szalay, A. S. (1993). "Bias and variance of angular correlation functions"
- Peebles, P. J. E. (1980). "The Large-Scale Structure of the Universe"
- Bandara, K., et al. (2018). "CHIME/FRB Catalog"
- SDSS Galaxy Survey Documentation

## 🧪 Qualitätssicherung

- ✓ Alle Funktionen haben Docstrings (NumPy-Format)
- ✓ Reproduzierbar durch Seed-Handling
- ✓ Robuste Fehlerbehandlung
- ✓ Monte Carlo Validierung
- ✓ Unit-testige Mathematik

## ⚠️ Wichtige Einschränkungen

1. **Synthetische Daten**: Projekt verwendet realistische Simulationen statt echter FRB/Galaxy-Kataloge
   - Ermöglicht zuverlässiges Testing ohne externe Abhängigkeiten
   - Kann leicht auf echte Daten umgestellt werden

2. **2D Analyse**: Hauptfokus auf Winkelabstände
   - 3D Analyse möglich mit Redshift-Informationen (optional implementiert)

3. **Statistische Power**: Mit n_frbs=150 begrenzte statistische Power
   - Real surveys haben oft >1000 FRBs

## 🎓 Verwendung in Bachelorarbeit

Dieses Framework kann als Basis für wissenschaftliche Untersuchungen dienen:

1. **Erweiterung auf 3D-Analyse** mit Redshift-Informationen
2. **Subsampling nach FRB-Typ** (Repeater vs Single Events)
3. **Environmental Density Estimation** unter Verwendung von Galaxy-Dichte-Feldern
4. **Redshift Binning** für Evolutionsstudien
5. **Cross-match Wahrscheinlichkeitsanalyse**

## 💡 Tipps für weitere Forschung

- Nutze echte CHIME/FRB Katalog + SDSS Daten
- Implementiere Bayessche Inferenz für robustere Parameter
- Nutze Machine Learning für automatische Assoziation
- Analysiere FRB Populationen nach Typ/Fluenz
- Vergleiche mit anderen Messungen (Gamma-Ray Bursts, etc.)

## 📝 Lizenz

Dieses Projekt steht zur freien Verwendung für Bildungszwecke zur Verfügung.

## 👤 Autor

Erstellt als wissenschaftliches Forschungsprojekt für Bachelor-Thesis.

---

**Letzte Aktualisierung**: Mai 2026
**Status**: ✓ Produktionsbereit
