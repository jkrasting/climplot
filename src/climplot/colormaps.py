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
    # Determine rounding precision from interval to eliminate float noise
    _decimals = max(0, -int(np.floor(np.log10(abs(interval)))) + 1) if interval != 0 else 0

    if center_on_white:
        # Create levels with white band centered on zero
        neg_levels = np.arange(vmin, -interval / 10, interval)
        white_band = np.array([-interval / 2, interval / 2])
        pos_levels = np.arange(interval, vmax + interval / 2, interval)
        levels = np.unique(np.concatenate([neg_levels, white_band, pos_levels]))
        levels = np.round(levels, _decimals)
        levels = np.unique(levels)  # Remove duplicates after rounding
    else:
        # Standard levels
        levels = np.arange(vmin, vmax + interval / 2, interval)
        levels = np.round(levels, _decimals)

    # Get base colormap
    base_cmap = plt.get_cmap(cmap_name)

    # Build colormap
    if center_on_white:
        # ListedColormap with exactly N colors (one per interval),
        # plus extra colors for extend arrows so BoundaryNorm is satisfied.
        n_intervals = len(levels) - 1
        midpoints = (levels[:-1] + levels[1:]) / 2
        linear_norm = plt.Normalize(vmin=levels[0], vmax=levels[-1])
        colors = [base_cmap(linear_norm(m)) for m in midpoints]
        # Find the interval spanning zero and set it to white
        for i in range(n_intervals):
            if levels[i] < 0 < levels[i + 1]:
                colors[i] = (1.0, 1.0, 1.0, 1.0)
                break
        # BoundaryNorm with extend needs extra color bins
        n_extra = 0
        if extend in ("min", "both"):
            n_extra += 1
            colors.insert(0, base_cmap(0.0))
        if extend in ("max", "both"):
            n_extra += 1
            colors.append(base_cmap(1.0))
        cmap = ListedColormap(colors, name=f"{cmap_name}_white_center")
        norm = BoundaryNorm(levels, len(colors), extend=extend)
    else:
        cmap = base_cmap
        norm = BoundaryNorm(levels, cmap.N, extend=extend)

    return cmap, norm, levels


def auto_levels(
    vmin: float,
    vmax: float,
    n_levels: int = 10,
) -> Tuple[float, np.ndarray]:
    """
    Automatically choose a "nice" interval and levels for a data range.

    Picks an interval whose significant digit is 1, 2, or 5 (the standard
    "nice number" set), then snaps vmin down and vmax up to multiples of
    the chosen interval.

    Parameters
    ----------
    vmin : float
        Minimum data value.
    vmax : float
        Maximum data value.
    n_levels : int, optional
        Target number of intervals. Default is 10.

    Returns
    -------
    interval : float
        The chosen interval.
    levels : ndarray
        Array of level boundaries.

    Raises
    ------
    ValueError
        If vmin >= vmax or n_levels < 1.

    Examples
    --------
    >>> interval, levels = climplot.auto_levels(-2.3, 2.7, n_levels=10)
    >>> interval
    0.5
    >>> levels
    array([-2.5, -2. , -1.5, -1. , -0.5,  0. ,  0.5,  1. ,  1.5,  2. ,  2.5,  3. ])
    """
    if vmin >= vmax:
        raise ValueError(f"vmin ({vmin}) must be less than vmax ({vmax})")
    if n_levels < 1:
        raise ValueError(f"n_levels ({n_levels}) must be >= 1")

    span = vmax - vmin
    raw_interval = span / n_levels
    magnitude = 10 ** np.floor(np.log10(raw_interval))
    candidates = np.array([1, 2, 5, 10]) * magnitude

    # Pick the candidate closest to raw_interval
    idx = np.argmin(np.abs(candidates - raw_interval))
    interval = candidates[idx]

    # Snap vmin down and vmax up to multiples of the interval
    snapped_vmin = np.floor(vmin / interval) * interval
    snapped_vmax = np.ceil(vmax / interval) * interval

    # Round to interval precision
    _decimals = max(0, -int(np.floor(np.log10(abs(interval)))) + 1) if interval != 0 else 0
    levels = np.arange(snapped_vmin, snapped_vmax + interval / 2, interval)
    levels = np.round(levels, _decimals)

    return float(interval), levels


def log_cmap(
    vmin: float,
    vmax: float,
    cmap_name: str = "viridis",
    per_decade: int = 1,
    extend: str = "both",
) -> Tuple[mcolors.Colormap, mcolors.BoundaryNorm, np.ndarray]:
    """
    Create a colormap with logarithmically-spaced boundaries.

    Uses ``BoundaryNorm`` so the result integrates with the standard
    colorbar machinery (``add_colorbar``, ``bottom_colorbar``).

    Parameters
    ----------
    vmin : float
        Minimum value (must be > 0).
    vmax : float
        Maximum value (must be > vmin).
    cmap_name : str, optional
        Colormap name. Default is 'viridis'.
    per_decade : int, optional
        Number of boundaries per decade of the logarithmic range.

        - ``1``: powers of 10 → [0.01, 0.1, 1, 10, 100]
        - ``2``: half-decades → [0.01, 0.03, 0.1, 0.3, 1, 3, ...]
        - ``3``: 1-2-5 sequence → [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, ...]

        Default is 1.
    extend : str, optional
        Out-of-range handling. Default is 'both'.

    Returns
    -------
    cmap : Colormap
    norm : BoundaryNorm
    levels : ndarray

    Raises
    ------
    ValueError
        If vmin <= 0 or vmax <= vmin.

    Examples
    --------
    >>> cmap, norm, levels = climplot.log_cmap(0.01, 100, per_decade=3)
    """
    if vmin <= 0:
        raise ValueError(f"vmin ({vmin}) must be positive for log scale")
    if vmax <= vmin:
        raise ValueError(f"vmax ({vmax}) must be greater than vmin ({vmin})")

    # Subsequences for each per_decade setting
    if per_decade == 1:
        subs = [1.0]
    elif per_decade == 2:
        subs = [1.0, 3.0]
    elif per_decade == 3:
        subs = [1.0, 2.0, 5.0]
    else:
        # General: evenly spaced in log space within a decade
        subs = np.logspace(0, 1, per_decade + 1)[:-1].tolist()

    # Build boundaries
    log_min = np.floor(np.log10(vmin))
    log_max = np.ceil(np.log10(vmax))

    levels = []
    for exp in range(int(log_min), int(log_max) + 1):
        for s in subs:
            val = s * 10**exp
            if vmin <= val <= vmax:
                levels.append(val)

    # Ensure vmin and vmax endpoints are included
    levels = np.array(sorted(set(levels)))
    if len(levels) == 0:
        levels = np.array([vmin, vmax])

    cmap = plt.get_cmap(cmap_name)
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
