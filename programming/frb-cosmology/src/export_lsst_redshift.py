"""Export and plot the LSST Y10 lens curves in the Figure 3 convention.

Run from any directory with ``py path/to/export_lsst_redshift.py``.
The curves use the local fisherA2Z dneff data and uniform bin filters,
with Gaussian kernels evaluated and normalized on a dense output grid.
They are neither unit-integral PDFs nor absolute galaxy number densities.
Only the Figure 3 data table and PNG/PDF plots are written.
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
OUTPUT_STEM = "LSST_Y10_fisherA2Z"
FIGURE3_GRID_SIZE = 4001


def build_figure3_sample(source_path):
    """Return a dense z grid and unnormalized Fisher lens curves from source_path.

    Keep the original parent-distribution integration grid, but evaluate and
    normalize the Gaussian kernels on a dense output grid. This avoids the
    coarse-grid normalization error for kernels narrower than the input step.
    """
    source = np.genfromtxt(source_path, names=True)
    input_redshift = source["zmid"]
    redshift = np.linspace(0.0, 4.0, FIGURE3_GRID_SIZE)
    parent_pdf = source["dneff"] / trapezoid(source["dneff"], input_redshift)
    scatter = SIGMA_Z * (1.0 + input_redshift)
    core = norm.pdf((redshift[:, None] - input_redshift[None, :]) / scatter) / scatter
    core /= trapezoid(core, redshift, axis=0)
    distributions = []
    for lower, upper in zip(BIN_EDGES[:-1], BIN_EDGES[1:]):
        selection = uniform.pdf(input_redshift, loc=lower, scale=upper - lower)
        joint = core * (parent_pdf * selection)[None, :]
        distributions.append(trapezoid(joint, input_redshift, axis=1))
    return redshift, np.asarray(distributions)


def export_figure3_sample(redshift, distributions):
    """Save supplied raw Fisher curves as an 11-column table and Figure-3-style plot."""
    configure_matplotlib_fonts()
    if shutil.which("latex") is None:
        plt.rcParams.update({"text.usetex": False, "font.serif": ["DejaVu Serif"]})
    output_dir = PROJECT_DIR / "plots" / "galaxy_lsst"
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(
        PROJECT_DIR / "data" / f"{OUTPUT_STEM}_figure3_nz.txt",
        np.column_stack((redshift, distributions.T)), fmt="%.12e", delimiter="\t",
        header="LSST Y10 lens curves; original Fisher._makeLensPZ convention\n"
        "Reference: https://arxiv.org/abs/2507.01374 Figure 3\n"
        "Source: fisherA2Z/data/nzdist.txt, dneff column\n"
        "Original 40-point parent integration; dense Gaussian evaluation and normalization\n"
        "Raw n_i(z), NOT unit-integral PDFs and NOT galaxies/arcmin^2/z\n"
        + "Z_MID\t" + "\t".join(f"BIN{index}" for index in range(1, N_BINS + 1)),
    )
    figure, axes = plt.subplots(figsize=(10, 5), constrained_layout=True)
    colors = plt.get_cmap("tab10").colors
    for distribution, color in zip(distributions, colors):
        axes.plot(redshift, distribution, color=color, linewidth=1.5)
    axes.set(xlim=(0.0, 1.5), xlabel="redshift", ylabel=r"$n_i(z)$")
    axes.grid(alpha=0.55)
    for extension in ("png", "pdf"):
        output_path = output_dir / f"{OUTPUT_STEM}_figure3.{extension}"
        figure.savefig(output_path, dpi=180)
        print(output_path)
    plt.close(figure)


def main():
    """Build, validate, export and plot the local Y10 lens sample; return None."""
    redshift, distributions = build_figure3_sample(SOURCE_PATH)
    assert distributions.shape == (N_BINS, redshift.size)
    assert np.all(np.diff(redshift) > 0)
    assert np.all(np.isfinite(distributions)) and np.all(distributions >= 0)
    assert np.all(trapezoid(distributions, redshift, axis=1) > 0)
    export_figure3_sample(redshift, distributions)
    print("Figure 3 peak heights:", distributions.max(axis=1))
    print(f"Rows: {redshift.size}; columns: {N_BINS + 1}")


if __name__ == "__main__":
    main()