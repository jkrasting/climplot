"""
Climate-specific colormap utilities.

This module provides colormaps optimized for climate data visualization,
including diverging colormaps for anomalies and sequential colormaps
for positive-only data.

Key Features
------------
- Discrete levels with "round" intervals (0, 1, 2, or 5 endings)
- Center-on-white option for difference plots
- Pre-defined colormaps for common climate variables

Examples
--------
>>> import climplot
>>> cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)
>>> ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm)
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from typing import Tuple, List, Optional

# Standard climate colormaps
CLIMATE_COLORMAPS = {
    "anomaly": "RdBu_r",  # Red-blue diverging (red=high, blue=low)
    "temperature": "RdBu_r",
    "precipitation": "BrBG",  # Brown-teal diverging
    "ssh": "RdBu_r",  # Sea surface height
    "wind": "PuOr_r",  # Purple-orange diverging
    "sequential": "viridis",  # Sequential
    "ice": "Blues_r",  # Ice concentration
}


def anomaly_cmap(
    vmin: float = -1.0,
    vmax: float = 1.0,
    interval: float = 0.1,
    center_on_white: bool = False,
    cmap_name: str = "RdBu_r",
) -> Tuple[mcolors.Colormap, mcolors.BoundaryNorm, np.ndarray]:
    """
    Create a diverging colormap for anomaly fields.

    Generates discrete color levels centered on zero with the specified
    interval. By default uses RdBu_r where red=positive, blue=negative.

    Parameters
    ----------
    vmin : float, optional
        Minimum value for color scale. Default is -1.0.
    vmax : float, optional
        Maximum value for color scale. Default is 1.0.
    interval : float, optional
        Interval between color levels. Should end in 0, 1, 2, or 5.
        Default is 0.1.
    center_on_white : bool, optional
        If True, creates a white band centered on zero.
        White band width is ±interval/2. Default is False.
        Recommended for difference plots.
    cmap_name : str, optional
        Base colormap name. Default is 'RdBu_r'.

    Returns
    -------
    cmap : Colormap
        The colormap object
    norm : BoundaryNorm
        Normalization for discrete levels
    levels : ndarray
        The discrete color levels

    Examples
    --------
    >>> # Standard anomaly colormap
    >>> cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)

    >>> # Difference plot with white band for near-zero values
    >>> cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05, center_on_white=True)

    Notes
    -----
    Common interval choices:
    - 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0, 2.0, 5.0
    """
    return discrete_cmap(
        vmin, vmax, interval, cmap_name=cmap_name, center_on_white=center_on_white
    )


def sequential_cmap(
    vmin: float = 0.0,
    vmax: float = 1.0,
    interval: float = 0.1,
    cmap_name: str = "viridis",
) -> Tuple[mcolors.Colormap, mcolors.BoundaryNorm, np.ndarray]:
    """
    Create a sequential colormap for positive-only data.

    Parameters
    ----------
    vmin : float, optional
        Minimum value. Default is 0.0.
    vmax : float, optional
        Maximum value. Default is 1.0.
    interval : float, optional
        Interval between levels. Default is 0.1.
    cmap_name : str, optional
        Colormap name. Default is 'viridis'.

    Returns
    -------
    cmap : Colormap
    norm : BoundaryNorm
    levels : ndarray

    Examples
    --------
    >>> cmap, norm, levels = climplot.sequential_cmap(0, 100, 10)
    """
    return discrete_cmap(vmin, vmax, interval, cmap_name=cmap_name, extend="max")


def categorical_cmap(
    n_categories: int,
    cmap_name: str = "tab10",
) -> ListedColormap:
    """
    Create a colormap for discrete categories.

    Parameters
    ----------
    n_categories : int
        Number of categories
    cmap_name : str, optional
        Base colormap. Default is 'tab10'.

    Returns
    -------
    ListedColormap
        Colormap with n_categories discrete colors

    Examples
    --------
    >>> cmap = climplot.categorical_cmap(5)
    """
    base_cmap = plt.get_cmap(cmap_name)
    colors = [base_cmap(i) for i in range(n_categories)]
    return ListedColormap(colors)


def discrete_cmap(
    vmin: float,
    vmax: float,
    interval: float,
    cmap_name: str = "RdBu_r",
    extend: str = "both",
    center_on_white: bool = False,
) -> Tuple[mcolors.Colormap, mcolors.BoundaryNorm, np.ndarray]:
    """
    Create a discrete colormap with BoundaryNorm.

    Generates color levels with "round" intervals for clean, readable
    colorbars. Optionally centers colormap on white for difference plots.

    Parameters
    ----------
    vmin : float
        Minimum value for color scale
    vmax : float
        Maximum value for color scale
    interval : float
        Interval between color levels. Should end in 0, 1, 2, or 5.
    cmap_name : str, optional
        Name of matplotlib colormap. Default is 'RdBu_r'.
    extend : str, optional
        Out-of-range handling: 'neither', 'min', 'max', or 'both'.
        Default is 'both'.
    center_on_white : bool, optional
        If True, creates a white band centered on zero.
        White band width is ±interval/2. Default is False.

    Returns
    -------
    cmap : Colormap
        The colormap object
    norm : BoundaryNorm
        Normalization for discrete levels
    levels : ndarray
        The discrete color levels

    Examples
    --------
    >>> # Standard discrete colormap
    >>> cmap, norm, levels = discrete_cmap(-0.3, 0.3, 0.05)

    >>> # With white band at center
    >>> cmap, norm, levels = discrete_cmap(-0.3, 0.3, 0.05, center_on_white=True)

    Notes
    -----
    When center_on_white=True:
    - White band width is ±interval/2
    - For interval=0.05, white covers -0.025 to +0.025
    - Best for difference plots where near-zero values are ambiguous
    """
    if center_on_white:
        # Create levels with white band centered on zero
        neg_levels = np.arange(vmin, -interval / 10, interval)
        white_band = np.array([-interval / 2, interval / 2])
        pos_levels = np.arange(interval, vmax + interval / 2, interval)
        levels = np.sort(np.concatenate([neg_levels, white_band, pos_levels]))
    else:
        # Standard levels
        levels = np.arange(vmin, vmax + interval / 2, interval)

    # Get base colormap
    base_cmap = plt.get_cmap(cmap_name)

    # Modify for center-on-white
    if center_on_white:
        n_colors = 256
        colors = base_cmap(np.linspace(0, 1, n_colors))
        center_idx = n_colors // 2
        colors[center_idx] = [1.0, 1.0, 1.0, 1.0]  # Pure white
        cmap = ListedColormap(colors, name=f"{cmap_name}_white_center")
    else:
        cmap = base_cmap

    # Create discrete normalization
    norm = BoundaryNorm(levels, cmap.N, extend=extend)

    return cmap, norm, levels


def list_colormaps() -> dict:
    """
    List recommended colormaps for climate variables.

    Returns
    -------
    dict
        Mapping of variable types to recommended colormap names

    Examples
    --------
    >>> climplot.list_colormaps()
    {'anomaly': 'RdBu_r', 'temperature': 'RdBu_r', ...}
    """
    return CLIMATE_COLORMAPS.copy()
