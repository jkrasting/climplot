"""
Style management for publication and presentation figures.

This module provides functions to configure matplotlib for publication-quality
or presentation-quality figures with appropriate font sizes, DPI, and other
settings.

Examples
--------
>>> import climplot
>>> climplot.publication()  # For journal figures
>>> climplot.presentation()  # For slides/posters
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional

# Track current mode
_current_mode: Optional[str] = None

# Style file directory
_STYLE_DIR = Path(__file__).parent / "data"


def publication(
    width: float = 3.5,
    for_pdf: bool = False,
    font_family: Optional[str] = None,
):
    """
    Configure matplotlib for publication-quality figures.

    Sets up small font sizes and high DPI appropriate for journal figures.
    Single-column figures are 3.5 inches wide (89 mm).

    Parameters
    ----------
    width : float, optional
        Default figure width in inches. Default is 3.5 (single-column).
        Use 7.0 for two-column figures.
    for_pdf : bool, optional
        If True, configure for PDF output with embedded fonts.
        Uses Myriad Pro font family by default.
    font_family : str, optional
        Font family to use. If None and for_pdf=True, uses 'Myriad Pro'.

    Examples
    --------
    >>> import climplot
    >>> climplot.publication()  # Standard PNG output
    >>> climplot.publication(for_pdf=True)  # PDF with embedded fonts
    >>> climplot.publication(width=7.0)  # Two-column width

    Notes
    -----
    Publication mode settings:
    - Figure width: 3.5" (single-column) or 7.0" (two-column)
    - DPI: 300
    - Axis labels: 10 pt
    - Tick labels: 8 pt
    - Title: 11 pt
    - Legend: 8 pt
    """
    global _current_mode

    settings = {
        # Font sizes (publication: smaller, dense)
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        # Figure settings
        "figure.figsize": (width, width * 0.75),
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        # Line widths
        "axes.linewidth": 0.8,
        "grid.linewidth": 0.3,
        "lines.linewidth": 1.5,
        # PDF settings
        "pdf.fonttype": 42,  # TrueType for editability
    }

    if for_pdf:
        if font_family is None:
            font_family = "Myriad Pro"
        settings["font.family"] = font_family

    plt.rcParams.update(settings)
    _current_mode = "publication"


def presentation(
    width: float = 7.0,
    for_pdf: bool = False,
    font_family: Optional[str] = None,
):
    """
    Configure matplotlib for presentation-quality figures.

    Sets up larger font sizes and moderate DPI appropriate for slides
    and posters. Default width is 7.0 inches for good visibility.

    Parameters
    ----------
    width : float, optional
        Default figure width in inches. Default is 7.0.
    for_pdf : bool, optional
        If True, configure for PDF output with embedded fonts.
    font_family : str, optional
        Font family to use. If None and for_pdf=True, uses 'Myriad Pro'.

    Examples
    --------
    >>> import climplot
    >>> climplot.presentation()  # Standard output
    >>> climplot.presentation(for_pdf=True)  # PDF for slides

    Notes
    -----
    Presentation mode settings:
    - Figure width: 7.0" (full slide width)
    - DPI: 150
    - Axis labels: 14 pt
    - Tick labels: 14 pt
    - Title: 16 pt
    - Legend: 12 pt
    """
    global _current_mode

    settings = {
        # Font sizes (presentation: larger, readable)
        "font.size": 14,
        "axes.labelsize": 14,
        "axes.titlesize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "legend.fontsize": 12,
        # Figure settings
        "figure.figsize": (width, width * 0.6),
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        # Line widths (thicker for visibility)
        "axes.linewidth": 1.2,
        "grid.linewidth": 0.5,
        "lines.linewidth": 2.5,
        # PDF settings
        "pdf.fonttype": 42,
    }

    if for_pdf:
        if font_family is None:
            font_family = "Myriad Pro"
        settings["font.family"] = font_family

    plt.rcParams.update(settings)
    _current_mode = "presentation"


def reset_style():
    """
    Reset matplotlib to default settings.

    Restores all rcParams to their default values and clears the
    current mode tracker.

    Examples
    --------
    >>> climplot.publication()
    >>> # ... make some figures ...
    >>> climplot.reset_style()  # Back to defaults
    """
    global _current_mode

    plt.rcdefaults()
    _current_mode = None


def get_current_mode() -> Optional[str]:
    """
    Get the currently active style mode.

    Returns
    -------
    str or None
        'publication', 'presentation', or None if no mode is set.

    Examples
    --------
    >>> climplot.publication()
    >>> climplot.get_current_mode()
    'publication'
    """
    return _current_mode
