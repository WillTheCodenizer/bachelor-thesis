# FRB Cosmology — Angular Power Spectrum Pipeline

Computes angular auto-correlation power spectra with the Limber approximation
for:
- Fast Radio Bursts (FRBs)
- Galaxy tomography bins from KiDS legacy n(z) data

## Quick Start

### Setup (erste Nutzung)

```bash
# Environment aus environment.yml erstellen
mamba env create -f environment.yml

# Environment aktivieren
mamba activate frb
```

### Ausführen

```bash
mamba activate frb
python main.py
```

Output plots are saved to `plots/`.

The run now produces:
- FRB shallow/deep auto-correlation plots (signal and signal+shot noise)
- Galaxy tomographic n(z) plot with BIN1..BIN6
- Galaxy BinixBini auto-correlation plots (signal and signal+shot noise)
- Galaxy all-bin signal-only comparison plot
- Nonlinear matter power-spectrum evolution plot

## Project Structure

```
frb-cosmology/
├── config/
│   └── parameters.py          # all physical & survey constants
├── src/
│   ├── cosmology.py           # background cosmology (chi, H, c)
│   ├── power_spectrum.py      # nonlinear P(k) via hmf
│   ├── distributions.py       # n(z), b(z), W(z)
│   ├── angular_power_spectrum.py  # Limber integral → C(ell)
│   └── shot_noise.py          # shot noise N_shot
├── plots/                     # saved figures (.pdf + .png)
├── notebooks/                 # Jupyter notebooks (optional)
├── main.py                    # runs the full pipeline
└── README.md
```

## Surveys

| Parameter | Shallow | Deep   |
|-----------|---------|--------|
| N_total   | 5 000   | 50 000 |
| alpha     | 3.5     | 2.0    |

Both use f_sky = 0.9 and magnetar bias b(z) = 1.0 × (1+z)^0.8.

## Galaxy Bias Model

For each tomographic galaxy bin i, the code computes:

- Mean redshift from file columns:
	- z_mean_bin1 ... z_mean_bin6
- Bias values from linear growth factor:
	- b_g_bin1 ... b_g_bin6

Bias relation:

```text
b_g^i = 0.95 / D_+(<z>_i)
```

Galaxy Limber weight function:

```text
W_g^i(z) = n_i(z) * b_g^i
```
