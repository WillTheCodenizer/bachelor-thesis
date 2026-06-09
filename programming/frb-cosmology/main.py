"""
main.py — FRB auto-correlation angular power spectrum pipeline.

Runs the full computation for both the shallow and deep surveys,
then produces publication-quality plots comparing signal and shot noise.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from config.parameters import (
    ALPHA_SHALLOW, ALPHA_DEEP,
    N_TOTAL_SHALLOW, N_TOTAL_DEEP,
)
from src.power_spectrum import build_power_spectrum
from src.angular_power_spectrum import compute_cell
from src.shot_noise import compute_shot_noise

# ── Output directory ────────────────────────────────────────────────────────
PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)


def run_pipeline():
    """
    Execute the full FRB auto-correlation pipeline for both surveys.

    Steps:
        1. Build the nonlinear matter power spectrum P(k).
        2. Compute C(ell) for the shallow and deep surveys.
        3. Compute shot noise for each survey.
        4. Produce and save four diagnostic plots.
    """
    # ── Step 1: nonlinear power spectrum ────────────────────────────────────
    print("Building nonlinear P(k) via hmf ...")
    k_phys, P_phys, P_interp = build_power_spectrum()
    k_min, k_max = k_phys.min(), k_phys.max()
    print(f"  k range : {k_min:.4e} – {k_max:.4e}  [1/Mpc]")
    print(f"  P range : {P_phys.min():.4e} – {P_phys.max():.4e}  [Mpc^3]")

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
    _plot_pk(k_phys, P_phys)

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


def _plot_pk(k_phys, P_phys):
    """
    Log-log plot of the nonlinear matter power spectrum P(k).

    Parameters
    ----------
    k_phys : ndarray
        Wavenumber in 1/Mpc.
    P_phys : ndarray
        Power spectrum in Mpc^3.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(k_phys, P_phys, linewidth=1.5)
    ax.set_xlabel(r"Wavenumber $k$ [1/Mpc]")
    ax.set_ylabel(r"$P(k)$ [Mpc$^3$]")
    ax.set_title("Nonlinear Matter Power Spectrum (z = 0)")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "Pk_nonlinear.pdf"))
    fig.savefig(os.path.join(PLOT_DIR, "Pk_nonlinear.png"), dpi=200)
    plt.close(fig)
    print("  Saved Pk_nonlinear.pdf / .png")


if __name__ == "__main__":
    run_pipeline()
