"""
main.py — FRB and galaxy tomographic angular power spectrum pipeline.

Runs the full computation for FRB surveys and galaxy tomographic bins,
then produces publication-quality diagnostic and comparison plots.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from config.parameters import (
    COSMO,
    ALPHA_SHALLOW, ALPHA_DEEP,
    N_TOTAL_SHALLOW, N_TOTAL_DEEP,
    Z_ARR,
    MAGNETAR_B0, MAGNETAR_DELTA,
    NEUTRON_STAR_B0, NEUTRON_STAR_DELTA,
    GALAXY_N_BINS, GALAXY_NBAR_PER_BIN, F_SKY_FRB,
)
from src.power_spectrum import build_power_spectrum_2d
from src.angular_power_spectrum import compute_cell, compute_cell_from_weight
from src.shot_noise import compute_shot_noise_from_counts, compute_shot_noise_from_density
from src.distributions import (
    load_galaxy_nz_data,
    compute_galaxy_bin_mean_redshifts,
    compute_galaxy_bias_from_means,
    interpolate_galaxy_bins,
    build_galaxy_weights,
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


def run_pipeline():
    """
    Execute the full FRB + galaxy auto-correlation pipeline.

    Steps:
        1. Build the redshift-dependent nonlinear matter power spectrum P(k, z).
        2. Run FRB auto-correlation (shallow/deep) for both host populations.
        3. Run galaxy tomographic auto-correlations for all bins and plots.
        4. Produce and save a shared P(k, z) diagnostic plot.
    """
    # ── Step 1: nonlinear power spectrum ────────────────────────────────────
    print("Building redshift-dependent P(k, z) via 2D spline ...")
    k_phys, P_interp, k_min, k_max = build_power_spectrum_2d(z_max=4.0, n_z=120)
    print(f"  k range : {k_min:.4e} – {k_max:.4e}  [1/Mpc]")

    # ── Step 2: FRB angular power spectra for all FRB host populations ─────
    _run_frb_pipeline(P_interp, k_min, k_max)

    # ── Step 3: galaxy tomographic angular power spectra ────────────────────
    _run_galaxy_pipeline(P_interp, k_min, k_max)

    # ── Step 4: shared P(k, z) diagnostic plot ──────────────────────────────
    _plot_pk(k_phys, P_interp, PK_PLOT_DIR)

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

    # Use one direct n_bar value per tomographic bin from Ngal.txt.
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


if __name__ == "__main__":
    run_pipeline()
