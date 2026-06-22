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
Z_MAX = 3.0             # Maximum redshift
N_Z = 500               # Number of redshift sample points

Z_ARR = np.logspace(np.log10(Z_MIN), np.log10(Z_MAX), N_Z)

# =============================================================================
# Multipole array — log-spaced integers from ell_min to ell_max
# =============================================================================
ELL_MIN = 2             # Minimum multipole
ELL_MAX = 1000          # Maximum multipole
N_ELL = 50              # Number of multipole sample points

# Generate log-spaced values, round to unique integers
ELL_ARR = np.unique(
    np.logspace(np.log10(ELL_MIN), np.log10(ELL_MAX), N_ELL).astype(int)
)

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

# KiDS survey area used for tomographic galaxy bins
GALAXY_SURVEY_AREA_DEG2 = 1347.0
ARCMIN2_PER_DEG2 = 60.0 ** 2
GALAXY_SURVEY_AREA_ARCMIN2 = GALAXY_SURVEY_AREA_DEG2 * ARCMIN2_PER_DEG2

# Observed sky fraction from survey area
F_SKY_GALAXY = GALAXY_SURVEY_AREA_DEG2 / (4.0 * np.pi * (180.0 / np.pi) ** 2)


# =============================================================================
# Galaxy tomography parameters
# =============================================================================
GALAXY_N_BINS = 6                         # Number of tomographic galaxy bins

# KiDS number-density input: ngal_i in [arcmin^-2] for each tomographic bin.
GALAXY_NGAL_FILE = Path(__file__).resolve().parents[1] / "data" / "Ngal.txt"
GALAXY_NGAL_PER_ARCMIN2 = np.loadtxt(GALAXY_NGAL_FILE, comments="#", ndmin=1)

if GALAXY_NGAL_PER_ARCMIN2.size != GALAXY_N_BINS:
    raise ValueError(
        f"Expected {GALAXY_N_BINS} ngal values in Ngal.txt, "
        f"got {GALAXY_NGAL_PER_ARCMIN2.size}."
    )

# Number of galaxies per bin: N_i = survey_area[arcmin^2] * ngal_i[arcmin^-2]
GALAXY_N_PER_BIN = GALAXY_SURVEY_AREA_ARCMIN2 * GALAXY_NGAL_PER_ARCMIN2
GALAXY_N_TOTAL = float(np.sum(GALAXY_N_PER_BIN))

# Tomographic n(z) distributions (independent from ngal_i counts above)
GALAXY_NZ_FILE = (
    Path(__file__).resolve().parents[1] / "data" / "KiDS_Legacy_nz.txt"
)
