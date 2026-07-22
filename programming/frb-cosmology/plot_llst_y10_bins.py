import numpy as np
import matplotlib.pyplot as plt
import yaml

from scipy.special import erf
from src.plot_style import configure_matplotlib_fonts


# ---------------------------------------------------------
# Einstellungen
# ---------------------------------------------------------

configure_matplotlib_fonts()

forecast_year = "10"

yaml_file = "parameters/lsst_desc_parameters.yaml"

z = np.linspace(0.0, 3.5, 500)


# ---------------------------------------------------------
# YAML laden
# ---------------------------------------------------------

with open(yaml_file, "r") as f:
    params = yaml.load(f, Loader=yaml.FullLoader)


lens = params["lens_sample"][forecast_year]
source = params["source_sample"][forecast_year]


# ---------------------------------------------------------
# Smail distribution wie in lsst_galaxy_sample.py
# ---------------------------------------------------------

def smail(z, z0, alpha, beta):

    return (z/z0)**beta * np.exp(-(z/z0)**alpha)



# ---------------------------------------------------------
# Photo-z convolution wie Github
# ---------------------------------------------------------

def photoz_bin(nz, zmin, zmax, sigma_z, z_bias):

    scatter = sigma_z * (1 + z)

    upper = (
        zmax - z + z_bias
    ) / (np.sqrt(2)*scatter)

    lower = (
        zmin - z + z_bias
    ) / (np.sqrt(2)*scatter)


    return 0.5*nz*(erf(upper)-erf(lower))



# ---------------------------------------------------------
# Normalisierung
# ---------------------------------------------------------

def normalize(y):

    return y/np.trapezoid(y,z)



# ---------------------------------------------------------
# Lens Y10
# ---------------------------------------------------------

nz_lens = smail(
    z,
    lens["z_0"],
    lens["alpha"],
    lens["beta"]
)

nz_lens = normalize(nz_lens)


# LSST Y10 lens bins:
# 0.2 - 1.2 spacing 0.1

edges = np.arange(
    lens["bin_start"],
    lens["bin_stop"]+lens["bin_spacing"],
    lens["bin_spacing"]
)


lens_bins = {}

for i in range(len(edges)-1):

    nz_bin = photoz_bin(
        nz_lens,
        edges[i],
        edges[i+1],
        lens["sigma_z"],
        lens["z_bias"]
    )

    lens_bins[i+1] = normalize(nz_bin)



# ---------------------------------------------------------
# Source Y10
# ---------------------------------------------------------

nz_source = smail(
    z,
    source["z_0"],
    source["alpha"],
    source["beta"]
)

nz_source = normalize(nz_source)



# source bins: equal number galaxies
cdf = np.cumsum(nz_source)
cdf /= cdf[-1]


source_edges = [
    np.interp(i/source["n_tomo_bins"], cdf, z)
    for i in range(source["n_tomo_bins"]+1)
]


source_bins = {}

for i in range(source["n_tomo_bins"]):

    nz_bin = photoz_bin(
        nz_source,
        source_edges[i],
        source_edges[i+1],
        source["sigma_z"],
        source["z_bias"]
    )

    source_bins[i+1] = normalize(nz_bin)



# ---------------------------------------------------------
# Plot lens
# ---------------------------------------------------------

plt.figure(figsize=(9,5))

for i,nz_bin in lens_bins.items():

    plt.plot(
        z,
        nz_bin,
        label=f"Lens bin {i}"
    )


plt.xlabel("Redshift z")
plt.ylabel(r"$p(z)$")
plt.title("LSST Y10 Lens Tomographic Bins")
#set x limits to 0-1.5
plt.xlim(0, 1.5)
plt.legend(ncol=2)
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()



# ---------------------------------------------------------
# Plot source
# ---------------------------------------------------------

plt.figure(figsize=(9,5))

for i,nz_bin in source_bins.items():

    plt.plot(
        z,
        nz_bin,
        label=f"Source bin {i}"
    )


plt.xlabel("Redshift z")
plt.ylabel(r"$p(z)$")
plt.title("LSST Y10 Source Tomographic Bins")
plt.legend(ncol=2)
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()



# ---------------------------------------------------------
# Bin centers ausgeben
# ---------------------------------------------------------

print("\nLens bin edges:")
print(edges)

print("\nSource bin edges:")
print(source_edges)