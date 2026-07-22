"""Shared Matplotlib styling for FRB-Cosmology plots."""

import matplotlib.pyplot as plt


def configure_matplotlib_fonts():
    """Use a serif font stack that matches the thesis document as closely as possible."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": [
            "Latin Modern Roman",
            "Computer Modern Roman",
            "CMU Serif",
            "DejaVu Serif",
        ],
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,
    })