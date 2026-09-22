"""Export and plot the local fisherA2Z default LSST Y10 lens sample.

Run from any directory with ``py path/to/export_lsst_redshift.py``.
This reproduces fisher_flex._default_lens_sample(10, y1=False), including
its use of the dneff column, finite-grid Gaussian normalization, uniform
photo-z filters, and relative bin weights. It needs no pyccl installation.
The 48 arcmin^-2 total is the repository's forecast assumption, not a
measurement. Existing LSST_Y10_nz.txt and pipeline settings are untouched.
"""

from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import trapezoid
from scipy.stats import norm, uniform

from plot_style import configure_matplotlib_fonts


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = PROJECT_DIR.parents[1] / "lsst_data_repo" / "fisherA2Z"
SOURCE_PATH = REPOSITORY_DIR / "src" / "fisherA2Z" / "data" / "nzdist.txt"
N_BINS = 10
BIN_EDGES = np.linspace(0.2, 1.2, N_BINS + 1)
SIGMA_Z = 0.03
TOTAL_DENSITY_ARCMIN2 = 48.0
OUTPUT_STEM = "LSST_Y10_fisherA2Z"


def build_lens_sample(source_path):
    """Read source_path; return z_mid, unit-integral bin PDFs and arcmin^-2 densities."""
    source = np.genfromtxt(source_path, names=True)
    redshift = source["zmid"]
    parent_pdf = source["dneff"] / trapezoid(source["dneff"], redshift)
    scatter = SIGMA_Z * (1.0 + redshift)
    core = norm.pdf((redshift[:, None] - redshift[None, :]) / scatter) / scatter
    core /= trapezoid(core, redshift, axis=0)
    distributions = []
    weights = []
    for lower, upper in zip(BIN_EDGES[:-1], BIN_EDGES[1:]):
        selection = uniform.pdf(redshift, loc=lower, scale=upper - lower)
        joint = core * (parent_pdf * selection)[None, :]
        distribution = trapezoid(joint, redshift, axis=1)
        weight = trapezoid(distribution, redshift)
        distributions.append(distribution / weight)
        weights.append(weight)
    densities = TOTAL_DENSITY_ARCMIN2 * np.asarray(weights) / np.sum(weights)
    return redshift, np.asarray(distributions), densities


def export_tables(redshift, distributions, densities):
    """Write the supplied grid, bin PDFs and densities to data/; return None."""
    data_dir = PROJECT_DIR / "data"
    provenance = (
        "LSST Y10 lens forecast; fisherA2Z fisher_flex._default_lens_sample\n"
        "Source: lsst_data_repo/fisherA2Z/src/fisherA2Z/data/nzdist.txt (dneff)\n"
        "10 uniform photo-z bins: 0.2 to 1.2; sigma_z = 0.03 * (1 + z)\n"
    )
    np.savetxt(
        data_dir / f"{OUTPUT_STEM}_nz.txt",
        np.column_stack((redshift, distributions.T)),
        fmt="%.12e",
        delimiter="\t",
        header=provenance + "Each BIN integrates to 1 over z_mid.\n"
        + "Z_MID\t" + "\t".join(f"BIN{index}" for index in range(1, N_BINS + 1)),
    )
    np.savetxt(
        data_dir / f"{OUTPUT_STEM}_Ngal.txt",
        densities[None, :],
        fmt="%.12e",
        header=provenance
        + "Number of galaxies per arcmin^2; repository total = 48.0\n"
        + "Densities = 48 * bin weights / sum(bin weights); not equal-bin counts.\n"
        + " ".join(f"NGAL_{index}" for index in range(1, N_BINS + 1)),
    )


def plot_sample(redshift, distributions, densities):
    """Save PNG/PDF plots of the supplied PDFs and arcmin^-2 densities; return None."""
    configure_matplotlib_fonts()
    if shutil.which("latex") is None:
        plt.rcParams.update({"text.usetex": False, "font.serif": ["DejaVu Serif"]})
    figure, (pdf_axes, density_axes) = plt.subplots(
        2, 1, figsize=(11, 8), constrained_layout=True,
        gridspec_kw={"height_ratios": [2.2, 1]},
    )
    colors = plt.get_cmap("tab10").colors
    for index, distribution in enumerate(distributions):
        pdf_axes.plot(
            redshift, distribution, color=colors[index], linewidth=1.8,
            label=f"{index + 1}: {BIN_EDGES[index]:.1f}-{BIN_EDGES[index + 1]:.1f}",
        )
    pdf_axes.set(
        xlim=(0.0, 1.6), ylim=(0.0, None), xlabel=r"Redshift $z$",
        ylabel=r"Normalized $p_i(z)$", title="LSST Y10: 10 tomographic lens bins",
    )
    pdf_axes.legend(title="Photo-z bin", ncol=5, fontsize=10, title_fontsize=11)
    bin_numbers = np.arange(1, N_BINS + 1)
    bars = density_axes.bar(bin_numbers, densities, color=colors, width=0.7)
    density_axes.bar_label(bars, fmt="%.3f", padding=3, fontsize=10)
    density_axes.set(
        xticks=bin_numbers, xlabel="Tomographic bin", ylabel=r"$\bar{n}_i$ [arcmin$^{-2}$]",
        ylim=(0, densities.max() * 1.22), title=r"Repository forecast: total 48 arcmin$^{-2}$",
    )
    for axes in (pdf_axes, density_axes):
        axes.spines[["top", "right"]].set_visible(False)
        axes.grid(axis="y", alpha=0.2)
        axes.set_axisbelow(True)
    output_dir = PROJECT_DIR / "plots" / "galaxy_lsst"
    output_dir.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "pdf"):
        output_path = output_dir / f"{OUTPUT_STEM}_tomography.{extension}"
        figure.savefig(output_path, dpi=180)
        print(output_path)
    plt.close(figure)


def main():
    """Build, validate, export and plot the local Y10 lens sample; return None."""
    redshift, distributions, densities = build_lens_sample(SOURCE_PATH)
    assert distributions.shape == (N_BINS, redshift.size)
    assert np.all(np.diff(redshift) > 0)
    assert np.all(np.isfinite(distributions)) and np.all(distributions >= 0)
    assert np.all(np.isfinite(densities)) and np.all(densities > 0)
    np.testing.assert_allclose(trapezoid(distributions, redshift, axis=1), 1.0)
    np.testing.assert_allclose(densities.sum(), TOTAL_DENSITY_ARCMIN2)
    export_tables(redshift, distributions, densities)
    plot_sample(redshift, distributions, densities)
    print(f"Rows: {redshift.size}; columns: {N_BINS + 1}")
    print("Densities [arcmin^-2]:", np.array2string(densities, precision=6))
    print(f"Total [arcmin^-2]: {densities.sum():.6f}")


if __name__ == "__main__":
    main()