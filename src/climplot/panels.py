"""
Multi-panel figure utilities.

This module provides functions for creating and labeling multi-panel
figures with consistent styling and colorbars.

Examples
--------
>>> import climplot
>>> climplot.publication()
>>> fig, axes = climplot.panel_figure(2, 3)  # 2 rows, 3 columns
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional, List, Union
import numpy as np


def panel_figure(
    nrows: int,
    ncols: int,
    figsize: Optional[Tuple[float, float]] = None,
    projection=None,
    constrained_layout: bool = True,
    **kwargs,
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create a multi-panel figure.

    Parameters
    ----------
    nrows : int
        Number of rows
    ncols : int
        Number of columns
    figsize : tuple, optional
        Figure size. If None, auto-calculated based on panels.
    projection : cartopy.crs.Projection, optional
        Map projection for all panels. If None, creates regular axes.
    constrained_layout : bool, optional
        Use constrained layout for better spacing. Default is True.
    **kwargs
        Additional arguments passed to plt.subplots()

    Returns
    -------
    fig : Figure
        The figure object
    axes : ndarray
        Array of axes objects (shape: nrows x ncols)

    Examples
    --------
    >>> # 2x3 panel figure
    >>> fig, axes = climplot.panel_figure(2, 3)
    >>> for ax in axes.flat:
    ...     ax.plot([1, 2, 3], [1, 4, 9])

    >>> # Panel figure with map projections
    >>> import cartopy.crs as ccrs
    >>> fig, axes = climplot.panel_figure(2, 2, projection=ccrs.Robinson())
    """
    if figsize is None:
        # Auto-calculate size
        panel_width = 3.5 if projection is None else 3.0
        panel_height = 2.5 if projection is None else 2.0
        figsize = (ncols * panel_width, nrows * panel_height)

    # Handle map projections
    if projection is not None:
        kwargs["subplot_kw"] = {"projection": projection}

    fig, axes = plt.subplots(
        nrows, ncols, figsize=figsize, constrained_layout=constrained_layout, **kwargs
    )

    # Ensure axes is always 2D array for consistency
    if nrows == 1 and ncols == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes.reshape(1, -1)
    elif ncols == 1:
        axes = axes.reshape(-1, 1)

    return fig, axes


def add_panel_labels(
    axes: Union[np.ndarray, List[plt.Axes]],
    labels: Optional[List[str]] = None,
    fontsize: int = 10,
    fontweight: str = "bold",
    x: float = 0.02,
    y: float = 0.98,
    ha: str = "left",
    va: str = "top",
):
    """
    Add panel labels (a. b. c. d.) to multi-panel figures.

    Parameters
    ----------
    axes : array-like
        List or array of axes objects
    labels : list of str, optional
        Custom labels. If None, uses lowercase letters with periods.
    fontsize : int, optional
        Font size. Default is 10.
    fontweight : str, optional
        Font weight. Default is 'bold'.
    x, y : float, optional
        Position in axes coordinates. Default is (0.02, 0.98).
    ha, va : str, optional
        Horizontal/vertical alignment. Default is 'left', 'top'.

    Examples
    --------
    >>> fig, axes = climplot.panel_figure(2, 2)
    >>> climplot.add_panel_labels(axes.flatten())
    """
    # Flatten if needed
    if hasattr(axes, "flatten"):
        axes = axes.flatten()

    if labels is None:
        labels = [f"{chr(97 + i)}." for i in range(len(axes))]

    for ax, label in zip(axes, labels):
        ax.text(
            x,
            y,
            label,
            transform=ax.transAxes,
            fontsize=fontsize,
            fontweight=fontweight,
            va=va,
            ha=ha,
        )


def _roundness_score(value):
    """Score how 'round' a number is for use as a tick label.

    Returns a higher score for rounder values.  Integers are strongly
    preferred over fractional values.  Within each tier, trailing zeros
    and last-digit quality (0 > 5 > even > odd) provide further
    discrimination.

    Score tiers:
    - Zero: 30 (modest bonus — important dividing line, but must not
      dominate sum-based scoring)
    - Integers: 20+ (bonus for trailing zeros and last-digit quality)
    - Fractions: 1–12 (penalty for more decimal places)
    """
    if value == 0:
        return 30

    abs_val = abs(value)

    # Integer tier — strongly preferred
    if np.isfinite(abs_val) and float(abs_val) == int(abs_val) and abs_val < 1e15:
        int_val = int(abs_val)
        s = str(int_val)
        trailing_zeros = len(s) - len(s.rstrip("0"))
        base = 20 + trailing_zeros * 3
        # Last non-zero digit preference: 5 > even > odd
        nz = s.rstrip("0")
        if nz:
            last = int(nz[-1])
            if last == 5:
                base += 2
            elif last % 2 == 0:
                base += 1
        return base

    # Fractional tier — penalise more decimal places
    s = f"{abs_val:.10g}"
    if "." in s:
        dec_part = s.split(".")[1].rstrip("0")
        n_decimals = len(dec_part)
        base = max(1, 10 - n_decimals * 2)
        # Last decimal digit preference: 5 > even > odd
        if dec_part:
            last = int(dec_part[-1])
            if last == 5:
                base += 2
            elif last % 2 == 0:
                base += 1
        return base

    return 15


def _is_symmetric(boundaries):
    """Return True if *boundaries* are symmetric about zero."""
    return len(boundaries) > 2 and np.allclose(boundaries, -boundaries[::-1])


def _score_subset(subset):
    """Score a tick subset by total roundness + uniform-spacing bonus."""
    score = sum(_roundness_score(v) for v in subset)
    gaps = np.diff(subset)
    if len(gaps) > 0 and np.allclose(gaps, gaps[0]):
        score += 20
    return score


def _best_stride_subset(boundaries, max_ticks, min_ticks):
    """Find the best stride+offset subset of *boundaries*.

    Does **not** force endpoints — the stride pattern alone decides
    which boundaries appear.  Returns None if no valid subset exists.
    """
    n = len(boundaries)
    min_stride = max(1, int(np.ceil(n / max_ticks)))
    best_subset = None
    best_score = -1

    for stride in range(min_stride, 2 * min_stride + 1):
        for offset in range(stride):
            subset = boundaries[offset::stride]
            if len(subset) > max_ticks or len(subset) < min_ticks:
                continue
            score = _score_subset(subset)
            if score > best_score:
                best_score = score
                best_subset = subset

    # Fallback: relax min_ticks if nothing was found
    if best_subset is None:
        for stride in range(min_stride, 2 * min_stride + 1):
            for offset in range(stride):
                subset = boundaries[offset::stride]
                if len(subset) > max_ticks:
                    continue
                if len(subset) < 2:
                    continue
                score = _score_subset(subset)
                if score > best_score:
                    best_score = score
                    best_subset = subset

    return best_subset


def _select_symmetric_ticks(boundaries, max_ticks, min_ticks):
    """Select ticks for boundaries that are symmetric about zero.

    Runs stride+offset on the non-negative half, then mirrors to
    guarantee symmetric labels on both sides of zero.
    """
    pos = boundaries[boundaries >= 0]  # includes 0 if present

    # Budget: half the max_ticks for each side, plus zero in the middle
    has_zero = np.isclose(pos[0], 0.0) if len(pos) > 0 else False
    half_max = max_ticks // 2
    if has_zero:
        half_max = (max_ticks - 1) // 2  # reserve slot for zero

    # Find best subset of positive-only boundaries (exclude zero)
    pos_only = pos[pos > 0]
    if len(pos_only) == 0:
        return boundaries  # degenerate

    best_pos = None
    best_score = -1
    n = len(pos_only)
    min_stride = max(1, int(np.ceil(n / half_max))) if half_max > 0 else 1

    for stride in range(min_stride, 2 * min_stride + 1):
        for offset in range(stride):
            subset = pos_only[offset::stride]
            if len(subset) > half_max:
                continue
            if len(subset) < 1:
                continue
            score = _score_subset(subset)
            if score > best_score:
                best_score = score
                best_pos = subset

    if best_pos is None:
        best_pos = pos_only  # fallback: use all

    # Mirror: negative side is the reverse of positive
    neg = -best_pos[::-1]
    if has_zero:
        result = np.concatenate([neg, [0.0], best_pos])
    else:
        result = np.concatenate([neg, best_pos])

    return result


def _thin_colorbar_ticks(cbar, max_ticks=9, min_ticks=5):
    """Reduce colorbar ticks to between *min_ticks* and *max_ticks*.

    For ``BoundaryNorm`` colorbars, selects actual boundary values using
    a stride+offset search that maximises tick "roundness" (integers
    preferred, clean last digits preferred).  Candidate subsets with
    fewer than *min_ticks* are rejected to avoid overly sparse labels.

    Symmetric boundaries (diverging colormaps) are handled by selecting
    ticks on the positive half and mirroring, guaranteeing symmetric
    labels.  Endpoints are **not** forced — the stride pattern alone
    decides which boundaries appear, avoiding edge crowding.

    For other norms, thins auto-generated ticks by selecting
    evenly-spaced indices.
    """
    norm = cbar.mappable.norm
    if hasattr(norm, "boundaries"):
        boundaries = np.asarray(norm.boundaries)
        n = len(boundaries)
        if n <= max_ticks:
            cbar.set_ticks(boundaries)
            return

        if _is_symmetric(boundaries):
            subset = _select_symmetric_ticks(boundaries, max_ticks, min_ticks)
        else:
            subset = _best_stride_subset(boundaries, max_ticks, min_ticks)

        if subset is not None:
            cbar.set_ticks(subset)
    else:
        ticks = cbar.get_ticks()
        if len(ticks) <= max_ticks:
            return
        indices = np.round(np.linspace(0, len(ticks) - 1, max_ticks)).astype(int)
        subset = ticks[indices]
        cbar.set_ticks(subset)


def _format_colorbar_ticks(cbar):
    """Apply clean tick formatting to a colorbar.

    Shows integers without decimals, floats with minimal precision, and
    zero as ``'0'``.
    """
    from matplotlib.ticker import FuncFormatter

    def _clean_label(x, pos):
        if x == 0:
            return "0"
        if np.isfinite(x) and float(x) == int(x) and abs(x) < 1e15:
            return f"{int(x)}"
        return f"{x:.10g}"

    formatter = FuncFormatter(_clean_label)
    cbar.ax.xaxis.set_major_formatter(formatter)
    cbar.ax.yaxis.set_major_formatter(formatter)


def add_colorbar(
    mappable,
    ax: plt.Axes,
    label: str,
    orientation: str = "horizontal",
    extend: str = "both",
    **kwargs,
) -> plt.colorbar:
    """
    Add a colorbar with consistent formatting.

    Parameters
    ----------
    mappable : ScalarMappable
        The plot object (e.g., from pcolormesh)
    ax : Axes
        The axes to attach colorbar to
    label : str
        Colorbar label with units
    orientation : str, optional
        'horizontal' or 'vertical'. Default is 'horizontal'.
    extend : str, optional
        Out-of-range handling. Default is 'both'.
    **kwargs
        Additional keyword arguments.  The following are handled
        specially before passing the rest to ``plt.colorbar()``:

        - *max_ticks* (int): maximum number of colorbar ticks (default 9).
        - *min_ticks* (int): minimum number of colorbar ticks (default 5).
        - *width* (float): colorbar thickness as a fraction of axes
          (maps to the ``fraction`` argument; default 0.046).
        - *label_fontsize*: font size for the label (default from rcParams).
        - *tick_fontsize*: font size for tick labels (default from rcParams).

    Returns
    -------
    Colorbar
        The colorbar object

    Examples
    --------
    >>> cs = ax.pcolormesh(lon, lat, data)
    >>> cbar = climplot.add_colorbar(cs, ax, 'Temperature (K)')
    """
    max_ticks = kwargs.pop("max_ticks", 9)
    min_ticks = kwargs.pop("min_ticks", 5)
    width = kwargs.pop("width", None)
    label_fontsize = kwargs.pop("label_fontsize", plt.rcParams.get("axes.labelsize", 8))
    tick_fontsize = kwargs.pop("tick_fontsize", plt.rcParams.get("xtick.labelsize", 8))

    fraction = width if width is not None else 0.046

    if orientation == "horizontal":
        cbar_kwargs = {"orientation": "horizontal", "pad": 0.05, "fraction": fraction, "aspect": 35}
    else:
        cbar_kwargs = {"orientation": "vertical", "pad": 0.05, "fraction": fraction, "aspect": 35}

    cbar_kwargs.update(kwargs)
    cbar = plt.colorbar(mappable, ax=ax, extend=extend, **cbar_kwargs)
    cbar.set_label(label, fontsize=label_fontsize)
    cbar.ax.tick_params(labelsize=tick_fontsize)
    cbar.minorticks_off()
    _format_colorbar_ticks(cbar)

    if max_ticks is not None:
        _thin_colorbar_ticks(cbar, max_ticks, min_ticks)

    return cbar


def bottom_colorbar(
    mappable,
    fig: plt.Figure,
    axes: np.ndarray,
    label: str,
    extend: str = "both",
    **kwargs,
) -> plt.colorbar:
    """
    Add a single colorbar below all panels.

    The colorbar is manually positioned so it is always at least *min_width*
    wide (as a fraction of figure width) and horizontally centered.

    Parameters
    ----------
    mappable : ScalarMappable
        The plot object (e.g., from pcolormesh)
    fig : Figure
        The figure object
    axes : ndarray
        Array of all axes
    label : str
        Colorbar label with units
    extend : str, optional
        Out-of-range handling. Default is 'both'.
    **kwargs
        Additional keyword arguments.  The following are handled specially:

        - *max_ticks* (int): maximum number of colorbar ticks (default 9).
        - *min_ticks* (int): minimum number of colorbar ticks (default 5).
        - *label_fontsize*: font size for the label (default from rcParams).
        - *tick_fontsize*: font size for tick labels (default from rcParams).
        - *pad* (float): fraction of the axes height to leave between the
          data axes and the colorbar (default 0.05; passed to
          ``fig.colorbar``).
        - *fraction* (float): fraction of the axes height to use for the
          colorbar (default 0.03; passed to ``fig.colorbar``).
        - *aspect* (int): ratio of colorbar long to short dimension
          (default 35; passed to ``fig.colorbar``).
        - *min_width* (float): minimum colorbar width as a fraction of total
          figure width (default 0.60).  When the axes span is wider, the
          colorbar expands to match.
        - *max_width* (float): maximum colorbar width as a fraction of total
          figure width (default 0.80).  Caps the width even when the axes
          span is larger.

    Returns
    -------
    Colorbar
        The colorbar object

    Examples
    --------
    >>> fig, axes = climplot.panel_figure(2, 2)
    >>> for ax in axes.flat:
    ...     cs = ax.pcolormesh(lon, lat, data)
    >>> cbar = climplot.bottom_colorbar(cs, fig, axes, 'SSH (m)')
    """
    max_ticks = kwargs.pop("max_ticks", 9)
    min_ticks = kwargs.pop("min_ticks", 5)
    label_fontsize = kwargs.pop("label_fontsize", plt.rcParams.get("axes.labelsize", 8))
    tick_fontsize = kwargs.pop("tick_fontsize", plt.rcParams.get("xtick.labelsize", 8))
    pad = kwargs.pop("pad", 0.05)
    fraction = kwargs.pop("fraction", 0.03)
    aspect = kwargs.pop("aspect", 35)
    min_width = kwargs.pop("min_width", 0.60)
    max_width = kwargs.pop("max_width", 0.80)

    # Flatten axes
    if hasattr(axes, "flatten"):
        axes_flat = axes.flatten()
    else:
        axes_flat = list(axes)

    # Step 1: Create a temporary colorbar using ax= so matplotlib shrinks the
    # data axes to make room (guarantees no overlap with tick labels).
    _temp_cbar = fig.colorbar(
        mappable,
        ax=list(axes_flat),
        orientation="horizontal",
        pad=pad,
        fraction=fraction,
        aspect=aspect,
        extend=extend,
    )

    # Step 2: Draw so constrained layout finalises all positions, then freeze.
    fig.canvas.draw()
    fig.set_layout_engine("none")

    # Step 3: Read the correct vertical position and data-axes span.
    temp_pos = _temp_cbar.ax.get_position()
    cbar_y0 = temp_pos.y0
    cbar_height = temp_pos.height
    pos_bboxes = [ax.get_position() for ax in axes_flat]
    axes_span = max(b.x1 for b in pos_bboxes) - min(b.x0 for b in pos_bboxes)

    # Step 4: Discard the narrow temp colorbar (data axes stay frozen).
    _temp_cbar.ax.remove()

    # Step 5: Build a new, wide, centered axes for the final colorbar.
    cbar_width = min(max_width, max(min_width, axes_span))
    cbar_x0 = 0.5 - cbar_width / 2
    cbar_x0 = max(0.0, cbar_x0)
    cbar_x0 = min(cbar_x0, 1.0 - cbar_width)
    cax = fig.add_axes([cbar_x0, cbar_y0, cbar_width, cbar_height])
    cbar = fig.colorbar(
        mappable,
        cax=cax,
        orientation="horizontal",
        extend=extend,
        **kwargs,
    )
    cbar.set_label(label, fontsize=label_fontsize)
    cbar.ax.tick_params(labelsize=tick_fontsize)
    cbar.minorticks_off()
    _format_colorbar_ticks(cbar)

    if max_ticks is not None:
        _thin_colorbar_ticks(cbar, max_ticks, min_ticks)

    return cbar


def save_figure(
    filename: str,
    output_dir: str = "figures",
    dpi: int = 300,
    **kwargs,
) -> Path:
    """
    Save figure with consistent settings.

    Parameters
    ----------
    filename : str
        Filename (should include extension)
    output_dir : str or Path, optional
        Directory to save to. Default is 'figures'.
    dpi : int, optional
        Resolution. Default is 300.
    **kwargs
        Additional arguments passed to plt.savefig()

    Returns
    -------
    Path
        Full path where figure was saved

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9])
    >>> climplot.save_figure('test_plot.png')
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    save_path = output_dir / filename

    save_kwargs = {
        "dpi": dpi,
        "bbox_inches": "tight",
        "facecolor": "white",
    }
    save_kwargs.update(kwargs)

    plt.savefig(save_path, **save_kwargs)

    return save_path
