"""
parameters.py — Central configuration for the FRB cosmology project.

All physical constants, survey parameters, and array definitions
are collected here so that every module draws from one source of truth.
"""

import numpy as np
from astropy.cosmology import FlatLambdaCDM
from pathlib import Path

# =============================================================================
# Cosmological parameters (Planck 2018, Table 2, TT,TE,EE+lowE+lensing)
# =============================================================================
H0 = 67.36              # Hubble constant [km/s/Mpc]
OMEGA_M = 0.3153         # Total matter density parameter
OMEGA_B = 0.0493         # Baryon density parameter
SIGMA_8 = 0.8111         # RMS matter fluctuations in 8 Mpc/h spheres
N_S = 0.9667            # Scalar spectral index

# Derived: reduced Hubble parameter
LITTLE_H = H0 / 100.0  # h = H0 / (100 km/s/Mpc)

# CMB temperature (Planck 2018)
TCMB0 = 2.7255  # [K]

# Astropy cosmology object used throughout the project
COSMO = FlatLambdaCDM(H0=H0, Om0=OMEGA_M, Ob0=OMEGA_B, Tcmb0=TCMB0)

# =============================================================================
# Redshift array — log-spaced from z_min to z_max
# =============================================================================
Z_MIN = 0.01            # Minimum redshift
Z_MAX = 5.0             # Maximum redshift
N_Z = 1000               # Number of redshift sample points

Z_ARR = np.logspace(np.log10(Z_MIN), np.log10(Z_MAX), N_Z)

# =============================================================================
# Multipole array — dense integer grid from ell_min to ell_max
# =============================================================================
ELL_MIN = 10             # Minimum multipole
ELL_MAX = 1000          # Maximum multipole

# Dense integer multipole grid so that the Fisher sum sum_ell (2*ell+1)/2 * ...
# correctly counts every multipole (required for the Reischke Fisher formula).
ELL_ARR = np.arange(ELL_MIN, ELL_MAX + 1)

# =============================================================================
# FRB host-population bias models: b(z) = b0 * (1 + z)^delta
# =============================================================================
# Magnetars
MAGNETAR_B0 = 1.0
MAGNETAR_DELTA = 0.8

# Neutron stars
NEUTRON_STAR_B0 = 1.5
NEUTRON_STAR_DELTA = 0.2

# =============================================================================
# Survey parameters
# =============================================================================

# --- Shallow survey ---
N_TOTAL_SHALLOW = 5.0e3     # Total number of detected FRBs
ALPHA_SHALLOW = 3.5          # Steepness of n(z) ∝ z^2 exp(-alpha z)

# --- Deep survey ---
N_TOTAL_DEEP = 5.0e4         # Total number of detected FRBs
ALPHA_DEEP = 2.0             # Steepness of n(z) ∝ z^2 exp(-alpha z)

# --- Common survey parameters ---
F_SKY_FRB = 0.9              # Observed sky fraction for FRB surveys

# Fisher forecast sky fraction: KiDS survey footprint (1347 deg²)
F_SKY_FISHER = 1347.0 / (4.0 * np.pi * (180.0 / np.pi) ** 2)

# =============================================================================
# Galaxy tomography parameters
# =============================================================================
GALAXY_N_BINS = 6                         # Number of tomographic galaxy bins

# KiDS number-density input: one n_bar value per tomographic bin.
GALAXY_NGAL_FILE = Path(__file__).resolve().parents[1] / "data" / "Ngal.txt"

# Convert n_bar from [arcmin^-2] to [steradian^-1] for internal calculations.
ARCMIN2_PER_STERADIAN = (180.0 * 60.0 / np.pi) ** 2  # ≈ 1.1818e7
GALAXY_NBAR_PER_BIN = np.loadtxt(GALAXY_NGAL_FILE, comments="#", ndmin=1) * ARCMIN2_PER_STERADIAN

if GALAXY_NBAR_PER_BIN.size != GALAXY_N_BINS:
    raise ValueError(
        f"Expected {GALAXY_N_BINS} ngal values in Ngal.txt, "
        f"got {GALAXY_NBAR_PER_BIN.size}."
    )

# Tomographic n(z) distributions (independent from ngal_i values above)
GALAXY_NZ_FILE = (
    Path(__file__).resolve().parents[1] / "data" / "KiDS_Legacy_nz.txt"
)
