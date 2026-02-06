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


def _thin_colorbar_ticks(cbar, max_ticks=7):
    """Reduce colorbar ticks to at most *max_ticks* evenly-spaced values.

    The auto-generated ticks are checked first; if fewer than
    *max_ticks* are present they are left untouched.  Otherwise, for
    ``BoundaryNorm`` colorbars, tick positions are replaced with
    *max_ticks* values evenly spaced between the first and last
    boundary (rounded to remove floating-point noise).  For other norms,
    auto-generated ticks are thinned by selecting evenly-spaced indices.
    """
    ticks = cbar.get_ticks()
    if len(ticks) < max_ticks:
        return

    norm = cbar.mappable.norm
    if hasattr(norm, "boundaries"):
        boundaries = np.asarray(norm.boundaries)
        # Use linspace to get clean, evenly-spaced values across the range
        subset = np.linspace(boundaries[0], boundaries[-1], max_ticks)
        # Round to remove floating-point noise (e.g. 5.55e-17 → 0.0)
        span = abs(boundaries[-1] - boundaries[0])
        decimals = max(0, int(-np.floor(np.log10(span / max_ticks))) + 2)
        subset = np.round(subset, decimals)
    else:
        indices = np.round(np.linspace(0, len(ticks) - 1, max_ticks)).astype(int)
        subset = ticks[indices]

    cbar.set_ticks(subset)


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
        Additional arguments passed to plt.colorbar()

    Returns
    -------
    Colorbar
        The colorbar object

    Examples
    --------
    >>> cs = ax.pcolormesh(lon, lat, data)
    >>> cbar = climplot.add_colorbar(cs, ax, 'Temperature (K)')
    """
    max_ticks = kwargs.pop("max_ticks", 7)

    if orientation == "horizontal":
        cbar_kwargs = {"orientation": "horizontal", "pad": 0.05, "fraction": 0.046, "aspect": 35}
    else:
        cbar_kwargs = {"orientation": "vertical", "pad": 0.05, "fraction": 0.046, "aspect": 35}

    cbar_kwargs.update(kwargs)
    cbar = plt.colorbar(mappable, ax=ax, extend=extend, **cbar_kwargs)
    cbar.set_label(label, fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    if max_ticks is not None:
        _thin_colorbar_ticks(cbar, max_ticks)

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
        Additional arguments passed to fig.colorbar()

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
    max_ticks = kwargs.pop("max_ticks", 7)

    # Flatten axes
    if hasattr(axes, "flatten"):
        axes_flat = axes.flatten()
    else:
        axes_flat = axes

    cbar = fig.colorbar(
        mappable,
        ax=list(axes_flat),
        orientation="horizontal",
        pad=0.05,
        fraction=0.03,
        aspect=35,
        extend=extend,
        **kwargs,
    )
    cbar.set_label(label, fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    if max_ticks is not None:
        _thin_colorbar_ticks(cbar, max_ticks)

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
