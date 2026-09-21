"""Shared Matplotlib styling for FRB-Cosmology plots."""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont


# Adjust these values to change the appearance of every plot in one place.
TICK_LABEL_SIZE = 14
AXIS_LABEL_SIZE = 15
TITLE_SIZE = 17
SUPTITLE_SIZE = 16
LEGEND_SIZE = 13


def configure_matplotlib_fonts():
    """Use Latin Modern Roman via LaTeX so plot text matches the thesis document."""

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman"],
        "font.weight": "normal",
        "text.usetex": True,
        "text.latex.preamble": (
            r"\usepackage[T1]{fontenc}"
            r"\usepackage{lmodern}"
            r"\usepackage{amsmath}"
        ),
        "axes.unicode_minus": False,
        "axes.labelweight": "normal",
        "axes.titleweight": "normal",
        "xtick.labelsize": TICK_LABEL_SIZE,
        "ytick.labelsize": TICK_LABEL_SIZE,
        "axes.labelsize": AXIS_LABEL_SIZE,
        "axes.titlesize": TITLE_SIZE,
        "figure.titlesize": SUPTITLE_SIZE,
        "legend.fontsize": LEGEND_SIZE,
    })


def get_matplotlib_font_report():
    """Return a compact report of configured and resolved Matplotlib fonts."""
    serif_families = plt.rcParams.get("font.serif", [])
    preferred_serif = serif_families[0] if serif_families else "serif"

    if plt.rcParams.get("text.usetex"):
        resolved_text_font = "via LaTeX/lmodern"
        resolved_math_rm_font = "via LaTeX/lmodern"
    else:
        resolved_text_font = findfont(FontProperties(family=[preferred_serif]))
        resolved_math_rm_font = findfont(
            FontProperties(family=[plt.rcParams.get("mathtext.rm", preferred_serif)])
        )

    return {
        "font.family": plt.rcParams.get("font.family"),
        "font.serif": serif_families,
        "text.usetex": plt.rcParams.get("text.usetex"),
        "text.latex.preamble": plt.rcParams.get("text.latex.preamble"),
        "xtick.labelsize": plt.rcParams.get("xtick.labelsize"),
        "ytick.labelsize": plt.rcParams.get("ytick.labelsize"),
        "axes.labelsize": plt.rcParams.get("axes.labelsize"),
        "axes.titlesize": plt.rcParams.get("axes.titlesize"),
        "figure.titlesize": plt.rcParams.get("figure.titlesize"),
        "legend.fontsize": plt.rcParams.get("legend.fontsize"),
        "resolved_text_font_file": resolved_text_font,
        "resolved_math_rm_font_file": resolved_math_rm_font,
    }