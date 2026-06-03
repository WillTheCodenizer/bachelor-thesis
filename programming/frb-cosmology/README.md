# FRB Cosmology — Angular Power Spectrum Pipeline

Computes the auto-correlation angular power spectrum of Fast Radio Bursts
(FRBs) using the Limber approximation with Planck 2018 cosmology.

## Quick Start

```bash
pip install numpy scipy matplotlib astropy hmf
cd frb-cosmology
python main.py
```

Output plots are saved to `plots/`.

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
