# Projektarchitektur & Workflows

## Architektur Überblick

```
┌─────────────────────────────────────────────────────────────────┐
│                    HAUPTANALYSE-PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  main.py (Orchestrator)                                          │
│  ├─ STEP 1: Katalog-Generierung/Laden                          │
│  │  └─> simulation.py + catalog_loader.py                      │
│  │                                                               │
│  ├─ STEP 2: Kreuzkorrelations-Berechnung                       │
│  │  └─> correlation.py (3 Estimatoren)                         │
│  │      ├─ 2D Correlation                                       │
│  │      ├─ Landy-Szalay Estimator                              │
│  │      └─ Bootstrap Error Estimation                           │
│  │                                                               │
│  ├─ STEP 3: Statistische Tests                                 │
│  │  └─> statistics.py                                           │
│  │      ├─ Chi² Test                                            │
│  │      ├─ KS Test                                              │
│  │      └─ p-value Berechnung                                   │
│  │                                                               │
│  ├─ STEP 4: Interpretation                                      │
│  │  └─> statistics.py (ResultInterpreter)                      │
│  │      └─ Automatische Textgenerierung                         │
│  │                                                               │
│  └─ STEP 5: Visualisierung                                      │
│     └─> plotting.py (7 verschiedene Plots)                      │
│                                                                   │
│  outputs/                                                         │
│  ├─ 00_summary_figure.png         (6-Panel)                    │
│  ├─ 01_separation_histogram.png   (Verteilung)                 │
│  ├─ 02_cross_correlation.png      (ξ(θ) mit Fehler)           │
│  ├─ 03_dd_vs_rr_comparison.png    (Beob. vs Erw.)             │
│  ├─ 04_bootstrap_errors.png       (Bootstrap)                  │
│  ├─ 05_sky_distribution.png       (Himmel)                     │
│  └─ 06_redshift_distribution.png  (z-Verteilung)              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Modul-Abhängigkeiten

```
                    ┌─────────────┐
                    │   main.py   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                   │
    ┌───▼───┐         ┌───▼────┐         ┌───▼────┐
    │ STEP1 │         │ STEP2  │         │ STEP5  │
    │ DATA  │         │ANALYSIS │         │ PLOTS  │
    └───┬───┘         └───┬────┘         └────────┘
        │                 │
    ┌───▼────────┐    ┌───▼──────┐
    │simulation  │    │correlation.py
    │catalog_    │    │  ├─ _2d_correlation()
    │loader      │    │  ├─ _landy_szalay()
    │            │    │  └─ _bootstrap()
    └────────────┘    └───┬──────┘
                          │
                      ┌───▼────────┐
                      │statistics  │
                      │  ├─ Tests  │
                      │  └─ Interp │
                      └────────────┘

utils.py (überall verwendet)
  ├─ angular_separation()
  ├─ histogram_cross_correlation()
  ├─ bootstrap_resample()
  └─ set_random_seed()

plotting.py (STEP5)
  └─ Alle Visualisierungen
```

## Daten-Flow Diagramm

```
┌─────────────────┐
│ Kataloge (real/ │
│ synthetic)      │
└────────┬────────┘
         │
         ├─────────────────┬───────────────┐
         │                 │               │
    ┌────▼─────┐   ┌──────▼──────┐  ┌────▼────┐
    │ FRBs     │   │ Galaxies     │  │ Random  │
    │ (150x)   │   │ (8000x)      │  │ (1500x) │
    └────┬─────┘   └──────┬──────┘  └────┬────┘
         │                │              │
         └────────────────┼──────────────┘
                          │
                    ┌─────▼────────┐
                    │ Pairwise     │
                    │ Separation   │
                    │ Calculation  │
                    └─────┬────────┘
                          │
            ┌─────────────┼──────────────┐
            │             │              │
       ┌────▼─────┐  ┌───▼────┐  ┌─────▼────┐
       │ DD Pairs │  │ RR Pairs│  │ DR Pairs │
       │ (Real)   │  │(Random) │  │ (Mixed)  │
       └────┬─────┘  └───┬────┘  └─────┬────┘
            │            │             │
            └────────────┼─────────────┘
                         │
                    ┌────▼─────────┐
                    │ Histogramme  │
                    │ Normalisiert │
                    └────┬─────────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼──┐  ┌───▼───┐  ┌──▼────┐
         │ξ(θ)  │  │LS Est │  │Bootstrap
         │Simple│  │Robust │  │Errors
         └────┬─┘  └───┬───┘  └──┬─────┘
              │        │         │
              └────────┼─────────┘
                       │
                  ┌────▼────────┐
                  │ Statistical │
                  │ Tests & p   │
                  │ values      │
                  └────┬────────┘
                       │
                  ┌────▼───────────┐
                  │ Interpretation │
                  │ & Conclusion   │
                  └────┬───────────┘
                       │
                  ┌────▼──────┐
                  │ Publication│
                  │ Quality    │
                  │ Plots (6)  │
                  └───────────┘
```

## Kreuzkorrelations-Berechnung (Detailliert)

```
Eingabe: FRB_Katalog, Galaxy_Katalog, Random_Katalog

┌─────────────────────────────────────────────────────┐
│ 1. Pairwise Separation Berechnung                   │
├─────────────────────────────────────────────────────┤
│ for each FRB:                                        │
│   for each Galaxy:                                   │
│     θ = spherical_distance(FRB_coords, Gal_coords) │
│                                                      │
│ Resultat: Array aller DD Paare (150 * 8000 = 1.2M) │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼────────────────────────────────────┐
│ 2. Histogrammierung in Winkelabstands-Bins       │
├────────────────────────────────────────────────────┤
│ for each bin:                                       │
│   counts_DD[bin] = count(θ in [θ_min, θ_max])     │
│   counts_RR[bin] = count(random_θ in range)       │
│                                                     │
│ Bins: 25 Bins von 0 - 120 arcmin (4.8 arcmin/bin) │
└──────────────┬────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────┐
│ 3. Korrelations-Berechnung                     │
├──────────────────────────────────────────────────┤
│ Naive Methode:                                  │
│   ξ(θ) = (DD(θ) / RR(θ)) - 1                  │
│                                                  │
│ Landy-Szalay (robust):                         │
│   ξ_LS(θ) = (DD - 2·DR + RR) / RR             │
│                                                  │
│ Resultat: 25 ξ-Werte mit Bin-Centern          │
└──────────────┬─────────────────────────────────┘
               │
┌──────────────▼────────────────────────────────┐
│ 4. Bootstrap Error Estimation                 │
├─────────────────────────────────────────────────┤
│ for i = 1 to 100:                              │
│   FRBs_boot = resample(FRBs, replacement)     │
│   ξ_boot[i] = compute_correlation(FRBs_boot)  │
│                                                 │
│ σ_bootstrap[bin] = std(ξ_boot[:, bin])        │
│                                                 │
│ Resultat: Robust Error Estimates               │
└──────────────┬────────────────────────────────┘
               │
              ▼

Ausgabe: ξ(θ), σ_boot(θ), p-values, Interpretation
```

## Statistische Test-Pipeline

```
INPUT: ξ(θ), σ(θ), Bin-Centers

┌──────────────────────────┐
│ Chi² Test                │
├──────────────────────────┤
│ χ² = Σ(ξ_i/σ_i)²       │
│ p = P(χ²>χ²_obs)        │
│                          │
│ H₀: No correlation      │
│ Reject if p < 0.05      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Detection Significance   │
├──────────────────────────┤
│ σ_det = ξ_mean / σ_mean │
│                          │
│ Detectable if |σ| > 2   │
│ Highly sig. if |σ| > 3  │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ KS Test (Distribution)   │
├──────────────────────────┤
│ KS = max|CDF(DD)-CDF(RR)||
│ p = P(KS > KS_obs)      │
│                          │
│ Vergleicht Verteilungen │
└──────────┬───────────────┘
           │
           ▼
┌────────────────────────────┐
│ Automated Interpretation   │
├────────────────────────────┤
│ IF p < 0.05 AND ξ > 0:    │
│   "POSITIVE CORRELATION"  │
│ ELSE IF p < 0.05:         │
│   "NEGATIVE CORRELATION"  │
│ ELSE:                      │
│   "NO SIGNIFICANT CORR."   │
└────────────────────────────┘
```

## Klassische vs Moderne Methoden

```
┌─────────────────────────────────────┐
│ KLASSISCHE METHODEN (Naive)         │
├─────────────────────────────────────┤
│ ξ(θ) = DD(θ) / RR(θ) - 1           │
│                                      │
│ ✗ Anfällig gegenüber Randeneffekten │
│ ✗ Höheres Rauschen                   │
│ ✓ Einfach zu verstehen              │
└─────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ MODERNE METHODEN (In diesem Projekt)   │
├─────────────────────────────────────────┤
│ 1. Landy-Szalay:                        │
│    ξ_LS = (DD - 2DR + RR) / RR         │
│    ✓ Robuster gegenüber Randeneffekten │
│    ✓ Geringeres Rauschen               │
│                                          │
│ 2. Bootstrap Errors:                    │
│    ✓ Non-parametrisch                   │
│    ✓ Keine Verteilungsannahmen          │
│                                          │
│ 3. Monte Carlo:                         │
│    ✓ Nullhypothese-Testing             │
│    ✓ Statistische Signifikanz          │
└─────────────────────────────────────────┘
```

---

Diese Architektur ist:
- **Modular**: Jedes Modul kann unabhängig getestet werden
- **Skalierbar**: Funktioniert mit 100 bis 100.000 Objekten
- **Erweiterbar**: Einfach 3D/Rshift/Typ-basierte Analysen hinzufügen
- **Reproduzierbar**: Vollständiges Seed-Management
- **Dokumentiert**: Ausführliche Docstrings und README
