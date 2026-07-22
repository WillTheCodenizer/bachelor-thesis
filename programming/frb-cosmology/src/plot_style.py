"""Shared Matplotlib styling for FRB-Cosmology plots."""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont


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
        "mathtext.fontset": "custom",
        "mathtext.rm": "Latin Modern Roman",
        "mathtext.it": "Latin Modern Roman:italic",
        "mathtext.bf": "Latin Modern Roman:bold",
        "mathtext.fallback": "cm",
        "axes.unicode_minus": False,
    })


def get_matplotlib_font_report():
    """Return a compact report of configured and resolved Matplotlib fonts."""
    serif_families = plt.rcParams.get("font.serif", [])
    preferred_serif = serif_families[0] if serif_families else "serif"

    resolved_text_font = findfont(FontProperties(family=[preferred_serif]))
    resolved_math_rm_font = findfont(
        FontProperties(family=[plt.rcParams.get("mathtext.rm", preferred_serif)])
    )

    return {
        "font.family": plt.rcParams.get("font.family"),
        "font.serif": serif_families,
        "mathtext.fontset": plt.rcParams.get("mathtext.fontset"),
        "mathtext.rm": plt.rcParams.get("mathtext.rm"),
        "mathtext.it": plt.rcParams.get("mathtext.it"),
        "mathtext.bf": plt.rcParams.get("mathtext.bf"),
        "mathtext.fallback": plt.rcParams.get("mathtext.fallback"),
        "resolved_text_font_file": resolved_text_font,
        "resolved_math_rm_font_file": resolved_math_rm_font,
    }