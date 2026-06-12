"""
main.py — FRB auto-correlation angular power spectrum pipeline.

Runs the full computation for both the shallow and deep surveys,
then produces publication-quality plots comparing signal and shot noise.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from config.parameters import (
    COSMO,
    ALPHA_SHALLOW, ALPHA_DEEP,
    N_TOTAL_SHALLOW, N_TOTAL_DEEP,
)
from src.power_spectrum import build_power_spectrum_2d
from src.angular_power_spectrum import compute_cell
from src.shot_noise import compute_shot_noise

# ── Output directory ────────────────────────────────────────────────────────
PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)


def run_pipeline():
    """
    Execute the full FRB auto-correlation pipeline for both surveys.

    Steps:
        1. Build the redshift-dependent nonlinear matter power spectrum P(k, z).
        2. Compute C(ell) for the shallow and deep surveys.
        3. Compute shot noise for each survey.
        4. Produce and save four diagnostic plots.
    """
    # ── Step 1: nonlinear power spectrum ────────────────────────────────────
    print("Building redshift-dependent P(k, z) via 2D spline ...")
    k_phys, P_interp, k_min, k_max = build_power_spectrum_2d(z_max=4.0, n_z=120)
    print(f"  k range : {k_min:.4e} – {k_max:.4e}  [1/Mpc]")

    # ── Step 2: angular power spectra for magnetars ─────────────────────────
    print("Computing C(ell) for shallow survey (alpha = 3.5) ...")
    ell_arr, C_ell_shallow = compute_cell(ALPHA_SHALLOW, P_interp, k_min, k_max)

    print("Computing C(ell) for deep survey (alpha = 2.0) ...")
    _, C_ell_deep = compute_cell(ALPHA_DEEP, P_interp, k_min, k_max)

    # ── Step 3: shot noise ──────────────────────────────────────────────────
    N_shot_shallow = compute_shot_noise(ALPHA_SHALLOW, N_TOTAL_SHALLOW)
    N_shot_deep = compute_shot_noise(ALPHA_DEEP, N_TOTAL_DEEP)
    print(f"  N_shot (shallow) = {N_shot_shallow:.4e}")
    print(f"  N_shot (deep)    = {N_shot_deep:.4e}")

    # ── Step 4: plots ───────────────────────────────────────────────────────
    _plot_cell_with_noise(
        ell_arr, C_ell_shallow, N_shot_shallow,
        title="FRB Auto-Correlation Angular Power Spectrum (Shallow Survey)",
        filename="Cell_shallow_shotnoise",
    )
    _plot_cell_with_noise(
        ell_arr, C_ell_deep, N_shot_deep,
        title="FRB Auto-Correlation Angular Power Spectrum (Deep Survey)",
        filename="Cell_deep_shotnoise",
    )
    _plot_cell_comparison(ell_arr, C_ell_shallow, C_ell_deep)
    _plot_pk(k_phys, P_interp)

    print("All plots saved to plots/")


# =============================================================================
# Plotting helpers
# =============================================================================

def _plot_cell_with_noise(ell_arr, C_ell, N_shot, title, filename):
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
    fig.savefig(os.path.join(PLOT_DIR, f"{filename}.pdf"))
    fig.savefig(os.path.join(PLOT_DIR, f"{filename}.png"), dpi=200)
    plt.close(fig)
    print(f"  Saved {filename}.pdf / .png")


def _plot_cell_comparison(ell_arr, C_ell_shallow, C_ell_deep):
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
    ax.set_title("FRB Auto-Correlation: Shallow vs Deep Survey")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "Cell_comparison.pdf"))
    fig.savefig(os.path.join(PLOT_DIR, "Cell_comparison.png"), dpi=200)
    plt.close(fig)
    print("  Saved Cell_comparison.pdf / .png")


def _plot_pk(k_phys, P_interp):
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
    fig.savefig(os.path.join(PLOT_DIR, "Pk_nonlinear.pdf"))
    fig.savefig(os.path.join(PLOT_DIR, "Pk_nonlinear.png"), dpi=200)
    plt.close(fig)
    print("  Saved Pk_nonlinear.pdf / .png")


if __name__ == "__main__":
    run_pipeline()
