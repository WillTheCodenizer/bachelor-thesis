"""
main.py — FRB and galaxy tomographic angular power spectrum pipeline.

Runs the full computation for FRB surveys and galaxy tomographic bins,
then produces publication-quality diagnostic and comparison plots.
"""

import os

import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from config.parameters import (
    COSMO,
    ALPHA_SHALLOW, ALPHA_DEEP,
    N_TOTAL_SHALLOW, N_TOTAL_DEEP,
    Z_ARR, ELL_ARR,
    MAGNETAR_B0, MAGNETAR_DELTA,
    NEUTRON_STAR_B0, NEUTRON_STAR_DELTA,
    GALAXY_N_BINS, GALAXY_NBAR_PER_BIN, F_SKY_FRB, F_SKY_FISHER,
)
from src.power_spectrum import build_power_spectrum_2d
from src.angular_power_spectrum import (
    compute_cell,
    compute_cell_from_weight,
    compute_cell_cross_correlation,
)
from src.shot_noise import compute_shot_noise_from_counts, compute_shot_noise_from_density
from src.distributions import (
    load_galaxy_nz_data,
    compute_galaxy_bin_mean_redshifts,
    compute_galaxy_bias_from_means,
    interpolate_galaxy_bins,
    build_galaxy_weights,
    weight_frb,
)
from src.fisher import (
    compute_frb_cells,
    compute_galaxy_cells,
    compute_cell_derivative,
    compute_fisher_matrix,
    invert_fisher,
    get_confidence_ellipse,
)

# ── Output directory ────────────────────────────────────────────────────────
PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)


def _make_plot_dir(subdir_name):
    """Create and return a dedicated plot subdirectory for one pipeline."""
    plot_subdir = os.path.join(PLOT_DIR, subdir_name)
    os.makedirs(plot_subdir, exist_ok=True)
    return plot_subdir


FRB_PLOT_DIR = _make_plot_dir("frb")
GALAXY_PLOT_DIR = _make_plot_dir("galaxy")
PK_PLOT_DIR = _make_plot_dir("power_spectrum")
CROSS_PLOT_DIR = _make_plot_dir("frb_x_galaxy")
FISHER_PLOT_DIR = _make_plot_dir("fisher")


def run_pipeline():
    """
    Execute the full FRB + galaxy auto-correlation pipeline.

    Steps:
        1. Build the redshift-dependent nonlinear matter power spectrum P(k, z).
        2. Run FRB auto-correlation (shallow/deep) for both host populations.
        3. Run galaxy tomographic auto-correlations for all bins and plots.
        4. Produce and save a shared P(k, z) diagnostic plot.
        5. Run FRB x Galaxy cross-correlation for all 24 combinations
           (2 populations x 2 surveys x 6 galaxy bins) and comparison plots.
        6. Run Fisher matrix forecast for all 4 survey/model combinations,
           comparing FRB-only and Galaxy×FRB multi-tracer constraints on b0 and alpha.
    """
    # ── Step 1: nonlinear power spectrum ────────────────────────────────────
    print("Building redshift-dependent P(k, z) via 2D spline ...")
    k_phys, P_interp, k_min, k_max = build_power_spectrum_2d(z_max=5.0, n_z=120)
    print(f"  k range : {k_min:.4e} – {k_max:.4e}  [1/Mpc]")

    # ── Step 2: FRB angular power spectra for all FRB host populations ─────
    _run_frb_pipeline(P_interp, k_min, k_max)

    # ── Step 3: galaxy tomographic angular power spectra ────────────────────
    _run_galaxy_pipeline(P_interp, k_min, k_max)

    # ── Step 4: shared P(k, z) diagnostic plot ──────────────────────────────
    _plot_pk(k_phys, P_interp, PK_PLOT_DIR)

    # ── Step 5: FRB x Galaxy cross-correlation ───────────────────────────────
    print("\nStep 5: FRB × Galaxy cross-correlation ...")
    _run_cross_correlation_pipeline(P_interp, k_min, k_max)

    # ── Step 6: Fisher matrix forecast ──────────────────────────────────────
    print("\nStep 6: Fisher matrix forecast ...")
    _run_fisher_pipeline(P_interp, k_min, k_max)

    print("All plots saved to plots/ with one subfolder per pipeline")


def _run_frb_pipeline(P_interp, k_min, k_max):
    """Compute and plot FRB auto-correlation signals for both host populations."""

    populations = [
        ("Magnetars", "magnetar", MAGNETAR_B0, MAGNETAR_DELTA),
        ("Neutron Stars", "neutron_star", NEUTRON_STAR_B0, NEUTRON_STAR_DELTA),
    ]

    # Shot noise depends on survey counts/f_sky and is shared across populations.
    N_shot_shallow = compute_shot_noise_from_counts(N_TOTAL_SHALLOW, F_SKY_FRB)
    N_shot_deep = compute_shot_noise_from_counts(N_TOTAL_DEEP, F_SKY_FRB)

    for population_label, population_slug, b0, delta in populations:
        print(
            f"Computing FRB C(ell) for {population_label} "
            f"(b0={b0:.2f}, delta={delta:.2f}) ..."
        )

        ell_arr, c_ell_shallow = compute_cell(
            ALPHA_SHALLOW, P_interp, k_min, k_max, b0=b0, delta=delta
        )
        _, c_ell_deep = compute_cell(
            ALPHA_DEEP, P_interp, k_min, k_max, b0=b0, delta=delta
        )

        print(f"  N_shot (shallow) = {N_shot_shallow:.4e}")
        print(f"  N_shot (deep)    = {N_shot_deep:.4e}")

        _plot_cell_with_noise(
            ell_arr,
            c_ell_shallow,
            N_shot_shallow,
            title=(
                f"FRB Auto-Correlation Angular Power Spectrum "
                f"(Shallow Survey) for {population_label}"
            ),
            filename=f"FRB_{population_slug}_Cell_shallow_shotnoise",
            plot_dir=FRB_PLOT_DIR,
        )
        _plot_cell_with_noise(
            ell_arr,
            c_ell_deep,
            N_shot_deep,
            title=(
                f"FRB Auto-Correlation Angular Power Spectrum "
                f"(Deep Survey) for {population_label}"
            ),
            filename=f"FRB_{population_slug}_Cell_deep_shotnoise",
            plot_dir=FRB_PLOT_DIR,
        )
        _plot_cell_comparison(
            ell_arr,
            c_ell_shallow,
            c_ell_deep,
            population_label=population_label,
            population_slug=population_slug,
            plot_dir=FRB_PLOT_DIR,
        )


def _run_galaxy_pipeline(P_interp, k_min, k_max):
    """
    Compute and plot galaxy tomographic auto-correlations for all bins.

    This pipeline:
      1) loads the measured n(z) data,
      2) computes per-bin <z> and b_g,
      3) builds W_g^i = n_i(z) * b_g^i,
      4) computes C_ell for each bin i x i,
      5) plots n(z), per-bin C_ell, and combined C_ell comparison.
    """
    z_mid, nz_bins_raw = load_galaxy_nz_data()
    _plot_galaxy_nz(z_mid, nz_bins_raw, GALAXY_PLOT_DIR)

    z_means = compute_galaxy_bin_mean_redshifts(z_mid, nz_bins_raw)
    biases = compute_galaxy_bias_from_means(z_means)

    print("Galaxy tomographic mean redshifts and biases:")
    for idx in range(GALAXY_N_BINS):
        print(f"  z_mean_bin{idx + 1} = {z_means[idx]:.6f}")
    for idx in range(GALAXY_N_BINS):
        print(f"  b_g_bin{idx + 1}    = {biases[idx]:.6f}")

    # Interpolate n(z) bins onto Z_ARR and build W_g^i(z) weights for each bin.
    nz_bins_interp = interpolate_galaxy_bins(Z_ARR, z_mid, nz_bins_raw, normalize=True)
    weights = build_galaxy_weights(Z_ARR, nz_bins_interp, biases)

    # Use one direct n_bar value per tomographic bin from Ngal.txt. converted to steradians.
    nbar_bins = GALAXY_NBAR_PER_BIN
    print("Galaxy n_bar values (from Ngal.txt):")
    for idx in range(GALAXY_N_BINS):
        print(f"  n_bar_bin{idx + 1} = {nbar_bins[idx]:.6e}")

    ell_arr = None
    cell_bins = []

    for idx in range(GALAXY_N_BINS):
        ell_arr, c_ell_bin = compute_cell_from_weight(
            weights[:, idx], P_interp, k_min, k_max
        )
        n_shot_bin = compute_shot_noise_from_density(nbar_bins[idx])
        cell_bins.append(c_ell_bin)

        _plot_cell_with_noise(
            ell_arr,
            c_ell_bin,
            n_shot_bin,
            title=f"Galaxy Auto-Correlation Angular Power Spectrum (Bin {idx + 1} x Bin {idx + 1})",
            filename=f"Galaxy_Cell_bin{idx + 1}_shotnoise",
            plot_dir=GALAXY_PLOT_DIR,
        )

    _plot_galaxy_cell_comparison(ell_arr, cell_bins, GALAXY_PLOT_DIR)


# =============================================================================
# Plotting helpers
# =============================================================================

def _plot_cell_with_noise(ell_arr, C_ell, N_shot, title, filename, plot_dir):
    """
    Log-log plot of C(ell) with and without shot noise.

    Parameters
    ----------
    ell_arr : ndarray
        Multipole values.
    C_ell : ndarray
        Signal-only angular power spectrum.
    N_shot : float
        Shot noise level.
    title : str
        Plot title.
    filename : str
        Base filename (without extension) for saving.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(ell_arr, C_ell, label="Signal only", linewidth=1.5)
    ax.loglog(ell_arr, C_ell + N_shot, label="Signal + Shot Noise",
              linewidth=1.5, linestyle="--")
    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell$")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(plot_dir, f"{filename}.pdf"))
    fig.savefig(os.path.join(plot_dir, f"{filename}.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved {filename}.pdf / .png")


def _plot_cell_comparison(
    ell_arr,
    C_ell_shallow,
    C_ell_deep,
    population_label="Magnetars",
    population_slug="magnetar",
    plot_dir=FRB_PLOT_DIR,
):
    """
    Overlay the signal-only C(ell) from both surveys on one log-log plot.

    Parameters
    ----------
    ell_arr : ndarray
        Multipole values.
    C_ell_shallow : ndarray
        C(ell) for the shallow survey.
    C_ell_deep : ndarray
        C(ell) for the deep survey.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(ell_arr, C_ell_shallow, label=r"Shallow ($\alpha=3.5$)", linewidth=1.5)
    ax.loglog(ell_arr, C_ell_deep, label=r"Deep ($\alpha=2.0$)", linewidth=1.5)
    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell$")
    ax.set_title(f"FRB Auto-Correlation: Shallow vs Deep Survey for {population_label}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(plot_dir, f"FRB_{population_slug}_Cell_comparison.pdf"))
    fig.savefig(os.path.join(plot_dir, f"FRB_{population_slug}_Cell_comparison.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved FRB_{population_slug}_Cell_comparison.pdf / .png")


def _plot_pk(k_phys, P_interp, plot_dir):
    """
    Log-log plot of the nonlinear matter power spectrum P(k, z) at multiple redshifts.

    Parameters
    ----------
    k_phys : ndarray
        Wavenumber array in 1/Mpc.
    P_interp : callable
        2D interpolation function P_interp(k, chi) returning P(k, z(chi)) in Mpc^3.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Sample redshifts to display the evolution
    z_sample = np.array([0.0, 0.5, 1.0, 2.0, 3.0, 4.0 ])
    
    # Convert redshifts to comoving distances
    chi_sample = COSMO.comoving_distance(z_sample).value  # [Mpc]
    
    # Plot P(k) at each sampled redshift
    colors = plt.cm.viridis(np.linspace(0, 1, len(z_sample)))
    for chi, z, color in zip(chi_sample, z_sample, colors):
        P_at_z = P_interp(k_phys, np.full_like(k_phys, chi))
        ax.loglog(k_phys, P_at_z, linewidth=1.8, label=f"z = {z:.1f}", color=color)
    
    ax.set_xlabel(r"Wavenumber $k$ [1/Mpc]")
    ax.set_ylabel(r"$P(k)$ [Mpc$^3$]")
    ax.set_title("Nonlinear Matter Power Spectrum P(k, z) — Redshift Evolution")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(os.path.join(plot_dir, "Pk_nonlinear.pdf"))
    fig.savefig(os.path.join(plot_dir, "Pk_nonlinear.png"), dpi=200)
    plt.close(fig)
    print("  Saved Pk_nonlinear.pdf / .png")


def _plot_galaxy_nz(z_mid, nz_bins, plot_dir):
    """Plot all tomographic galaxy n(z) bins in one figure."""
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, nz_bins.shape[1]))

    for idx in range(nz_bins.shape[1]):
        ax.plot(z_mid, nz_bins[:, idx], linewidth=1.8, color=colors[idx], label=f"BIN{idx + 1}")

    ax.set_xlabel(r"Redshift $z$")
    ax.set_ylabel(r"$n_i(z)$")
    ax.set_title("Galaxy Tomographic Redshift Distributions")
    ax.legend(loc="best", ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(plot_dir, "Galaxy_nz_bins.pdf"))
    fig.savefig(os.path.join(plot_dir, "Galaxy_nz_bins.png"), dpi=200)
    plt.close(fig)
    print("  Saved Galaxy_nz_bins.pdf / .png")


def _plot_galaxy_cell_comparison(ell_arr, cell_bins, plot_dir):
    """Overlay signal-only galaxy C(ell) curves for BIN1..BIN6."""
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, len(cell_bins)))

    for idx, c_ell in enumerate(cell_bins):
        ax.loglog(
            ell_arr,
            c_ell,
            linewidth=1.6,
            color=colors[idx],
            label=f"Bin {idx + 1} x Bin {idx + 1}",
        )

    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell$")
    ax.set_title("Galaxy Auto-Correlation Comparison (Signal Only)")
    ax.legend(loc="best", ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(plot_dir, "Galaxy_Cell_comparison.pdf"))
    fig.savefig(os.path.join(plot_dir, "Galaxy_Cell_comparison.png"), dpi=200)
    plt.close(fig)
    print("  Saved Galaxy_Cell_comparison.pdf / .png")


def _run_cross_correlation_pipeline(P_interp, k_min, k_max):
    """
    Compute and plot FRB x Galaxy cross-correlation spectra for all combinations.

    Iterates over:
      - 2 FRB host populations: Magnetars, Neutron Stars
      - 2 FRB surveys: Shallow, Deep
      - 6 galaxy tomographic bins

    yielding 24 cross-correlation spectra C(ell)^{FRB x gal_i}.
    No shot noise is added — cross-correlations between distinct populations
    carry no Poissonian noise contribution.

        Three types of comparison plots are produced in the comparisons/ subdirectory:
            1. Population: Magnetar vs Neutron Star (per survey, all bins together)
            2. Survey: Shallow vs Deep (per population, all bins together)
            3. Galaxy bins: Bin 1..6 overlay (per population, per survey)
    """
    populations = [
        ("Magnetars", "magnetar", MAGNETAR_B0, MAGNETAR_DELTA),
        ("Neutron Stars", "neutron_star", NEUTRON_STAR_B0, NEUTRON_STAR_DELTA),
    ]
    surveys = [
        ("Shallow", "shallow", ALPHA_SHALLOW),
        ("Deep", "deep", ALPHA_DEEP),
    ]

    # Create per-population/survey subdirectories inside frb_x_galaxy/
    cell_dirs = {}
    for _, pop_slug, _, _ in populations:
        for _, survey_slug, _ in surveys:
            path = os.path.join(CROSS_PLOT_DIR, pop_slug, survey_slug)
            os.makedirs(path, exist_ok=True)
            cell_dirs[(pop_slug, survey_slug)] = path
    comp_dir = os.path.join(CROSS_PLOT_DIR, "comparisons")
    os.makedirs(comp_dir, exist_ok=True)

    # Load and prepare galaxy data (identical preparation as in _run_galaxy_pipeline)
    z_mid, nz_bins_raw = load_galaxy_nz_data()
    z_means = compute_galaxy_bin_mean_redshifts(z_mid, nz_bins_raw)
    biases = compute_galaxy_bias_from_means(z_means)
    nz_bins_interp = interpolate_galaxy_bins(Z_ARR, z_mid, nz_bins_raw, normalize=True)
    weights_galaxy = build_galaxy_weights(Z_ARR, nz_bins_interp, biases)

    # Compute all 2 × 2 × 6 = 24 cross-correlation spectra.
    # Store in dict indexed by (pop_slug, survey_slug, bin_idx).
    cells = {}
    ell_arr = None

    for pop_label, pop_slug, b0, delta in populations:
        for survey_label, survey_slug, alpha in surveys:
            print(
                f"Computing FRB×Galaxy cross-correlations: "
                f"{pop_label}, {survey_label} survey ..."
            )
            w_frb = weight_frb(Z_ARR, alpha, b0, delta)

            for bin_idx in range(GALAXY_N_BINS):
                w_gal = weights_galaxy[:, bin_idx]
                ell_arr, c_ell = compute_cell_cross_correlation(
                    w_frb, w_gal, P_interp, k_min, k_max
                )
                cells[(pop_slug, survey_slug, bin_idx)] = c_ell
                print(
                    f"  Bin {bin_idx + 1}: "
                    f"C_ell_max = {np.max(c_ell):.4e}"
                )
                _plot_cross_cell(
                    ell_arr,
                    c_ell,
                    title=(
                        f"FRB×Galaxy Cross-Correlation ({pop_label}, "
                        f"{survey_label} Survey, Galaxy Bin {bin_idx + 1})"
                    ),
                    filename=f"cross_cell_bin{bin_idx + 1}",
                    plot_dir=cell_dirs[(pop_slug, survey_slug)],
                )

    # --- Comparison plots ---

    # 1. Population comparison: Magnetar vs Neutron Star
    #    One plot per survey with all galaxy bins overlaid.
    for survey_label, survey_slug, _ in surveys:
        _plot_cross_population_comparison(
            ell_arr, cells, survey_slug, survey_label, comp_dir
        )

    # 2. Survey comparison: Shallow vs Deep
    #    One plot per population with all galaxy bins overlaid.
    for pop_label, pop_slug, _, _ in populations:
        _plot_cross_survey_comparison(
            ell_arr, cells, pop_slug, pop_label, comp_dir
        )

    # 3. Bin comparison: all 6 galaxy bins overlaid
    #    One plot per (population, survey) with 6 curves.
    for pop_label, pop_slug, _, _ in populations:
        for survey_label, survey_slug, _ in surveys:
            _plot_cross_bin_comparison(
                ell_arr, cells,
                pop_slug, pop_label,
                survey_slug, survey_label,
                comp_dir,
            )


# =============================================================================
# Cross-correlation plotting helpers
# =============================================================================

def _plot_cross_cell(ell_arr, c_ell, title, filename, plot_dir):
    """
    Log-log plot of a single FRB x Galaxy cross-correlation spectrum.

    No shot noise overlay — cross-correlations between distinct populations
    have no shot noise contribution.

    Parameters
    ----------
    ell_arr : ndarray
        Multipole values.
    c_ell : ndarray
        Cross-correlation angular power spectrum.
    title : str
        Plot title.
    filename : str
        Base filename (without extension) for saving.
    plot_dir : str
        Directory in which to save the figure.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(ell_arr, c_ell, linewidth=1.5, color="C0")
    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell^{\rm FRB \times gal}$")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(os.path.join(plot_dir, f"{filename}.pdf"))
    fig.savefig(os.path.join(plot_dir, f"{filename}.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved {filename}.pdf / .png")


def _plot_cross_population_comparison(
    ell_arr, cells, survey_slug, survey_label, comp_dir
):
    """
    Overlay Magnetar vs Neutron Star cross-correlation for a fixed survey.

    All galaxy bins are shown in one figure. For each bin, Magnetars and
    Neutron Stars are distinguished by line style.

    Parameters
    ----------
    ell_arr : ndarray
        Multipole values.
    cells : dict
        Mapping (pop_slug, survey_slug, bin_idx) → C_ell ndarray.
    survey_slug : str
        Survey identifier key ('shallow' or 'deep').
    survey_label : str
        Human-readable survey name for the plot title.
    comp_dir : str
        Output directory for comparison plots.
    """
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, GALAXY_N_BINS))

    for bin_idx in range(GALAXY_N_BINS):
        ax.loglog(
            ell_arr,
            cells[("magnetar", survey_slug, bin_idx)],
            linewidth=1.4,
            color=colors[bin_idx],
            linestyle="-",
            label=f"Magnetars Bin {bin_idx + 1}",
        )
        ax.loglog(
            ell_arr,
            cells[("neutron_star", survey_slug, bin_idx)],
            linewidth=1.4,
            color=colors[bin_idx],
            linestyle="--",
            label=f"Neutron Stars Bin {bin_idx + 1}",
        )

    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell^{\rm FRB \times gal}$")
    ax.set_title(f"FRB Population Comparison ({survey_label} Survey, all bins)")
    ax.legend(loc="best", ncol=2, fontsize=8)
    fig.tight_layout()
    fname = f"population_{survey_slug}_all_bins"
    fig.savefig(os.path.join(comp_dir, f"{fname}.pdf"))
    fig.savefig(os.path.join(comp_dir, f"{fname}.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved {fname}.pdf / .png")


def _plot_cross_survey_comparison(
    ell_arr, cells, pop_slug, pop_label, comp_dir
):
    """
    Overlay Shallow vs Deep survey cross-correlation for a fixed population.

    All galaxy bins are shown in one figure. For each bin, Shallow and Deep
    are distinguished by line style.

    Parameters
    ----------
    ell_arr : ndarray
        Multipole values.
    cells : dict
        Mapping (pop_slug, survey_slug, bin_idx) → C_ell ndarray.
    pop_slug : str
        Population identifier key ('magnetar' or 'neutron_star').
    pop_label : str
        Human-readable population name for the plot title.
    comp_dir : str
        Output directory for comparison plots.
    """
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, GALAXY_N_BINS))

    for bin_idx in range(GALAXY_N_BINS):
        ax.loglog(
            ell_arr,
            cells[(pop_slug, "shallow", bin_idx)],
            linewidth=1.4,
            color=colors[bin_idx],
            linestyle="-",
            label=f"Shallow Bin {bin_idx + 1}",
        )
        ax.loglog(
            ell_arr,
            cells[(pop_slug, "deep", bin_idx)],
            linewidth=1.4,
            color=colors[bin_idx],
            linestyle="--",
            label=f"Deep Bin {bin_idx + 1}",
        )

    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell^{\rm FRB \times gal}$")
    ax.set_title(f"FRB Survey Comparison ({pop_label}, all bins)")
    ax.legend(loc="best", ncol=2, fontsize=8)
    fig.tight_layout()
    fname = f"survey_{pop_slug}_all_bins"
    fig.savefig(os.path.join(comp_dir, f"{fname}.pdf"))
    fig.savefig(os.path.join(comp_dir, f"{fname}.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved {fname}.pdf / .png")


def _plot_cross_bin_comparison(
    ell_arr, cells, pop_slug, pop_label, survey_slug, survey_label, comp_dir
):
    """
    Overlay all six galaxy bins for a fixed FRB population and survey.

    Shows which galaxy redshift bins carry the highest cross-correlation signal
    with the FRB sample — a direct probe of their redshift overlap.

    Parameters
    ----------
    ell_arr : ndarray
        Multipole values.
    cells : dict
        Mapping (pop_slug, survey_slug, bin_idx) → C_ell ndarray.
    pop_slug : str
        Population identifier key.
    pop_label : str
        Human-readable population name.
    survey_slug : str
        Survey identifier key.
    survey_label : str
        Human-readable survey name.
    comp_dir : str
        Output directory for comparison plots.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, GALAXY_N_BINS))

    for bin_idx in range(GALAXY_N_BINS):
        ax.loglog(
            ell_arr,
            cells[(pop_slug, survey_slug, bin_idx)],
            linewidth=1.6,
            color=colors[bin_idx],
            label=f"Galaxy Bin {bin_idx + 1}",
        )

    ax.set_xlabel(r"Multipole $\ell$")
    ax.set_ylabel(r"$C_\ell^{\rm FRB \times gal}$")
    ax.set_title(
        f"FRB×Galaxy — All Bins ({pop_label}, {survey_label} Survey)"
    )
    ax.legend(loc="best", ncol=2)
    fig.tight_layout()
    fname = f"bin_comparison_{pop_slug}_{survey_slug}"
    fig.savefig(os.path.join(comp_dir, f"{fname}.pdf"))
    fig.savefig(os.path.join(comp_dir, f"{fname}.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved {fname}.pdf / .png")


# =============================================================================
# Fisher matrix forecast pipeline
# =============================================================================

def _run_fisher_pipeline(P_interp, k_min, k_max):
    """
    Run Fisher matrix forecast for all 4 survey/model combinations.

    For each combination (Deep/Shallow × Magnetar/Neutron Star):
      1. Compute fiducial FRB auto- and FRB×galaxy C_ells.
      2. Compute numerical C_ell derivatives with b0 and alpha (±1%).
      3. Build and invert the Fisher matrix for:
         a. FRB-only forecast (1×1 covariance from C_ell^ff).
         b. Multi-tracer forecast (7×7 covariance from [g1..g6, FRB]).
      4. Plot both confidence ellipses on the b0–alpha plane.

    The galaxy-galaxy C_ell block (6×6, parameter-independent) is computed
    once and reused across all four combinations.
    """
    # ── Galaxy setup (identical to _run_cross_correlation_pipeline) ─────────
    z_mid, nz_bins_raw = load_galaxy_nz_data()
    z_means = compute_galaxy_bin_mean_redshifts(z_mid, nz_bins_raw)
    biases = compute_galaxy_bias_from_means(z_means)
    nz_bins_interp = interpolate_galaxy_bins(Z_ARR, z_mid, nz_bins_raw, normalize=True)
    weights_galaxy = build_galaxy_weights(Z_ARR, nz_bins_interp, biases)

    # Galaxy shot noise: one constant N_shot per tomographic bin
    n_shot_gal = np.array([
        compute_shot_noise_from_density(GALAXY_NBAR_PER_BIN[i])
        for i in range(GALAXY_N_BINS)
    ])

    # Galaxy-galaxy C_ell block — computed once (FRB-parameter-independent)
    print("  Computing galaxy-galaxy C_ell block (6×6) ...")
    cell_gg = compute_galaxy_cells(weights_galaxy, P_interp, k_min, k_max)
    print("  Galaxy-galaxy C_ell block done.")

    populations = [
        ("Magnetars", "magnetar", MAGNETAR_B0, MAGNETAR_DELTA),
        ("Neutron Stars", "neutron_star", NEUTRON_STAR_B0, NEUTRON_STAR_DELTA),
    ]
    surveys = [
        ("Deep", "deep", ALPHA_DEEP, N_TOTAL_DEEP),
        ("Shallow", "shallow", ALPHA_SHALLOW, N_TOTAL_SHALLOW),
    ]

    # Collect data for 2x2 comparison plot
    fisher_data = []
    
    for pop_label, pop_slug, b0, delta in populations:
        for survey_label, survey_slug, alpha, n_total in surveys:
            print(
                f"\n  Fisher forecast: {pop_label}, {survey_label} survey "
                f"(b0={b0:.2f}, alpha={alpha:.2f}, delta={delta:.2f}) ..."
            )

            n_shot_frb = compute_shot_noise_from_counts(n_total, F_SKY_FRB)

            # Fiducial FRB C_ells
            cell_ff, cell_gf = compute_frb_cells(
                alpha, b0, delta, weights_galaxy, P_interp, k_min, k_max
            )

            # Numerical derivatives via ±1% central finite difference
            print("    Computing dC/db0 ...")
            d_b0 = compute_cell_derivative(
                'b0', alpha, b0, delta, weights_galaxy, P_interp, k_min, k_max
            )
            print("    Computing dC/ddelta ...")
            d_delta = compute_cell_derivative(
                'delta', alpha, b0, delta, weights_galaxy, P_interp, k_min, k_max
            )

            # ── FRB-only Fisher ──────────────────────────────────────────────
            # Uses the full FRB survey footprint (F_SKY_FRB); no galaxy overlap
            # constraint applies when only the FRB auto-correlation is used.
            F_frb = compute_fisher_matrix(
                cell_ff, cell_gg, cell_gf,
                n_shot_frb, n_shot_gal,
                d_b0, d_delta, F_SKY_FRB, mode='frb_only',
            )
            cov_frb = invert_fisher(F_frb)

            # ── Multi-tracer Fisher ──────────────────────────────────────────
            # Restricted to the FRB × galaxy survey overlap (F_SKY_FISHER).
            F_multi = compute_fisher_matrix(
                cell_ff, cell_gg, cell_gf,
                n_shot_frb, n_shot_gal,
                d_b0, d_delta, F_SKY_FISHER, mode='multitracer',
            )
            cov_multi = invert_fisher(F_multi)

            # Print marginal 1σ constraints
            sigma_b0_frb    = np.sqrt(cov_frb[0, 0])
            sigma_delta_frb = np.sqrt(cov_frb[1, 1])
            sigma_b0_multi    = np.sqrt(cov_multi[0, 0])
            sigma_delta_multi = np.sqrt(cov_multi[1, 1])
            print(
                f"    FRB-only:     sigma_b0 = {sigma_b0_frb:.4f}, "
                f"sigma_delta = {sigma_delta_frb:.4f}"
            )
            print(
                f"    Multi-tracer: sigma_b0 = {sigma_b0_multi:.4f}, "
                f"sigma_delta = {sigma_delta_multi:.4f}"
            )

            _plot_fisher_ellipses(
                cov_frb, cov_multi,
                b0_fid=b0,
                delta_fid=delta,
                title=(
                    f"Fisher Forecast — {pop_label}, {survey_label} Survey\n"
                    rf"Fiducial: $b_0={b0}$, $\delta={delta}$"
                ),
                filename=f"fisher_{survey_slug}_{pop_slug}",
                plot_dir=FISHER_PLOT_DIR,
            )
            
            # Collect data for 2x2 comparison plot
            fisher_data.append({
                'pop_label': pop_label,
                'survey_label': survey_label,
                'cov_frb': cov_frb,
                'cov_multi': cov_multi,
                'b0_fid': b0,
                'delta_fid': delta,
            })
    
    # Create 2x2 comparison plot
    _plot_fisher_comparison_2x2(fisher_data, FISHER_PLOT_DIR)


def _nice_half_ticks(fiducial, lim, target_ticks=7):
    """
    Generate tick values at .0 or .5 spacing, symmetric around the fiducial.

    Chooses the smallest multiple of 0.5 as step size that yields
    no more than target_ticks within the axis range.
    """
    extent = lim[1] - lim[0]
    # Ideal spacing for target number of ticks
    ideal_step = extent / target_ticks
    # Round up to nearest 0.5 multiple
    step = max(0.5, np.ceil(ideal_step / 0.5) * 0.5)

    n_ticks_half = int(np.ceil((extent / 2.0) / step))
    ticks = [fiducial + i * step for i in range(-n_ticks_half, n_ticks_half + 1)]
    # Keep only ticks within axis limits
    ticks = [t for t in ticks if lim[0] <= t <= lim[1]]
    return ticks


def _plot_fisher_comparison_2x2(fisher_data, plot_dir):
    """
    Create a 2x2 comparison plot of Fisher ellipses for all combinations.

    Parameters
    ----------
    fisher_data : list of dict
        List of dictionaries, each containing:
        - pop_label: population label (e.g., "Magnetars")
        - survey_label: survey label (e.g., "Deep")
        - cov_frb: FRB-only covariance matrix
        - cov_multi: Multi-tracer covariance matrix
        - b0_fid: fiducial b0 value
        - delta_fid: fiducial delta value
    plot_dir : str
        Output directory for the figure.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    # Color and style scheme
    style = {
        'frb':   {'color': 'C0', 'label_1s': r'FRB-only $1\sigma$',          'label_2s': r'FRB-only $2\sigma$'},
        'multi': {'color': 'C1', 'label_1s': r'FRB$\times$Galaxy $1\sigma$', 'label_2s': r'FRB$\times$Galaxy $2\sigma$'},
    }

    for idx, data in enumerate(fisher_data):
        ax = axes[idx]
        cov_frb = data['cov_frb']
        cov_multi = data['cov_multi']
        b0_fid = data['b0_fid']
        delta_fid = data['delta_fid']
        pop_label = data['pop_label']
        survey_label = data['survey_label']

        # Plot ellipses
        for cov, key in [(cov_frb, 'frb'), (cov_multi, 'multi')]:
            color = style[key]['color']
            for confidence, ls, lbl in [
                (0.6827, '-',  style[key]['label_1s']),
                (0.9545, '--', style[key]['label_2s']),
            ]:
                wa, wb, ang = get_confidence_ellipse(cov, confidence=confidence)
                ellipse = mpatches.Ellipse(
                    xy=(b0_fid, delta_fid),
                    width=2.0 * wa,
                    height=2.0 * wb,
                    angle=ang,
                    edgecolor=color,
                    facecolor='none',
                    linestyle=ls,
                    linewidth=1.8,
                    label=lbl,
                )
                ax.add_patch(ellipse)

        # Mark fiducial point
        ax.plot(b0_fid, delta_fid, 'k+', markersize=10, markeredgewidth=1.5, zorder=5)

        # Axis limits: 3.0× the FRB×Galaxy 2σ projected extents
        wa_2s, wb_2s, ang_2s = get_confidence_ellipse(cov_multi, confidence=0.9545)
        ang_rad = np.radians(ang_2s)
        dx = np.sqrt((wa_2s * np.cos(ang_rad)) ** 2 + (wb_2s * np.sin(ang_rad)) ** 2)
        dy = np.sqrt((wa_2s * np.sin(ang_rad)) ** 2 + (wb_2s * np.cos(ang_rad)) ** 2)
        margin = 3.0
        xlim = (b0_fid - margin * dx, b0_fid + margin * dx)
        ylim = (delta_fid - margin * dy, delta_fid + margin * dy)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Set ticks at .0 or .5 values, symmetric around fiducial
        ax.set_xticks(_nice_half_ticks(b0_fid, xlim))
        ax.set_yticks(_nice_half_ticks(delta_fid, ylim))

        ax.set_xlabel(r"$b_0$", fontsize=10)
        ax.set_ylabel(r"$\delta$", fontsize=10)
        ax.set_title(f"{pop_label}, {survey_label} Survey", fontsize=11, fontweight='bold')
        
        # Add legend only to the first subplot to avoid clutter
        if idx == 0:
            ax.legend(loc="best", fontsize=8)

    # Remove any unused subplots (if fisher_data has fewer than 4 items)
    for idx in range(len(fisher_data), 4):
        fig.delaxes(axes[idx])

    fig.suptitle("Fisher Forecast Comparison", fontsize=14, fontweight='bold', y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    fig.savefig(os.path.join(plot_dir, "fisher_comparison_2x2.pdf"))
    fig.savefig(os.path.join(plot_dir, "fisher_comparison_2x2.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved fisher_comparison_2x2.pdf / .png")


def _plot_fisher_ellipses(
    cov_frb, cov_multi,
    b0_fid, delta_fid,
    title, filename, plot_dir,
):
    """
    Plot 1σ and 2σ Fisher confidence ellipses for FRB-only and multi-tracer forecasts.

    Both sets of ellipses are centered at the fiducial parameter values
    (b0_fid, delta_fid). The FRB-only ellipse provides the baseline constraint;
    the multi-tracer ellipse shows the improvement from adding galaxy tomography.

    Parameters
    ----------
    cov_frb : ndarray, shape (2, 2)
        Covariance matrix from the FRB-only Fisher matrix.
    cov_multi : ndarray, shape (2, 2)
        Covariance matrix from the multi-tracer Fisher matrix.
    b0_fid : float
        Fiducial b0 value (ellipse center x-coordinate).
    delta_fid : float
        Fiducial delta value (ellipse center y-coordinate).
    title : str
        Plot title.
    filename : str
        Base filename (without extension) for saving.
    plot_dir : str
        Output directory.
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    # Color and style scheme
    style = {
        'frb':   {'color': 'C0', 'label_1s': r'FRB-only $1\sigma$',          'label_2s': r'FRB-only $2\sigma$'},
        'multi': {'color': 'C1', 'label_1s': r'FRB$\times$Galaxy $1\sigma$', 'label_2s': r'FRB$\times$Galaxy $2\sigma$'},
    }

    for cov, key in [(cov_frb, 'frb'), (cov_multi, 'multi')]:
        color = style[key]['color']
        for confidence, ls, lbl in [
            (0.6827, '-',  style[key]['label_1s']),
            (0.9545, '--', style[key]['label_2s']),
        ]:
            wa, wb, ang = get_confidence_ellipse(cov, confidence=confidence)
            ellipse = mpatches.Ellipse(
                xy=(b0_fid, delta_fid),
                width=2.0 * wa,
                height=2.0 * wb,
                angle=ang,
                edgecolor=color,
                facecolor='none',
                linestyle=ls,
                linewidth=1.8,
                label=lbl,
            )
            ax.add_patch(ellipse)

    # Mark fiducial point
    ax.plot(b0_fid, delta_fid, 'k+', markersize=10, markeredgewidth=1.5, zorder=5)

    # Axis limits: 3.0× the FRBxGalaxy 2σ projected extents
    wa_2s, wb_2s, ang_2s = get_confidence_ellipse(cov_multi, confidence=0.9545)
    ang_rad = np.radians(ang_2s)
    dx = np.sqrt((wa_2s * np.cos(ang_rad)) ** 2 + (wb_2s * np.sin(ang_rad)) ** 2)
    dy = np.sqrt((wa_2s * np.sin(ang_rad)) ** 2 + (wb_2s * np.cos(ang_rad)) ** 2)
    margin = 3.0
    xlim = (b0_fid - margin * dx, b0_fid + margin * dx)
    ylim = (delta_fid - margin * dy, delta_fid + margin * dy)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Set ticks at .0 or .5 values, symmetric around fiducial
    ax.set_xticks(_nice_half_ticks(b0_fid, xlim))
    ax.set_yticks(_nice_half_ticks(delta_fid, ylim))

    ax.set_xlabel(r"$b_0$")
    ax.set_ylabel(r"$\delta$")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(plot_dir, f"{filename}.pdf"))
    fig.savefig(os.path.join(plot_dir, f"{filename}.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved {filename}.pdf / .png")


if __name__ == "__main__":
    run_pipeline()
