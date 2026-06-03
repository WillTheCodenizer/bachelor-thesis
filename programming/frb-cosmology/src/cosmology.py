"""
cosmology.py — Background cosmology setup.

Uses the Planck 2018 FlatLambdaCDM cosmology from config/parameters.py
to compute the comoving distance array over the project's redshift grid.
"""

import numpy as np
from astropy import units as u

from config.parameters import COSMO, Z_ARR

# Comoving distance for every redshift in Z_ARR, in Mpc (plain floats)
CHI_ARR = COSMO.comoving_distance(Z_ARR).to(u.Mpc).value

# Speed of light in km/s (for H(z)/c computation later)
C_KM_S = 2.998e5  # [km/s]
