"""
Time series plotting utilities.

This module provides functions for creating publication-quality time series
plots with consistent styling.

Examples
--------
>>> import climplot
>>> climplot.publication()
>>> fig, ax = climplot.timeseries_figure()
>>> ax.plot(time, data)
"""

import matplotlib.pyplot as plt
from typing import Tuple, Optional


# Standard colors for model configurations
CONFIG_COLORS = {
    "obs": "#000000",  # Black - observations
    "model": "#1f77b4",  # Blue - default model
    "model1": "#1f77b4",  # Blue
    "model2": "#ff7f0e",  # Orange
    "model3": "#2ca02c",  # Green
    "model4": "#d62728",  # Red
    "model5": "#9467bd",  # Purple
}

# Standard line styles
CONFIG_LINESTYLES = {
    "obs": "--",  # Dashed for observations
    "model": "-",  # Solid for models
    "model1": "-",
    "model2": "-",
    "model3": "-",
    "model4": "-",
    "model5": "-",
}


def timeseries_figure(
    figsize: Optional[Tuple[float, float]] = None,
    grid: bool = True,
    grid_alpha: float = 0.3,
    **kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a figure sized for time series plots.

    Parameters
    ----------
    figsize : tuple, optional
        Figure size (width, height) in inches. If None, uses (7.0, 3.5).
    grid : bool, optional
        Whether to add grid lines. Default is True.
    grid_alpha : float, optional
        Grid transparency. Default is 0.3.
    **kwargs
        Additional arguments passed to plt.subplots()

    Returns
    -------
    fig : Figure
        The figure object
    ax : Axes
        The axes object

    Examples
    --------
    >>> fig, ax = climplot.timeseries_figure()
    >>> ax.plot(time, data, label='Model')
    >>> ax.set_xlabel('Year')
    >>> ax.set_ylabel('Sea Level (m)')
    >>> ax.legend()
    """
    if figsize is None:
        figsize = (7.0, 3.5)

    fig, ax = plt.subplots(figsize=figsize, **kwargs)

    if grid:
        ax.grid(True, alpha=grid_alpha, linewidth=0.3)

    return fig, ax


def get_config_style(config: str) -> dict:
    """
    Get standard style parameters for a configuration name.

    Parameters
    ----------
    config : str
        Configuration name (e.g., 'obs', 'model', 'model1')

    Returns
    -------
    dict
        Style parameters with 'color' and 'linestyle' keys

    Examples
    --------
    >>> style = get_config_style('obs')
    >>> ax.plot(time, data, **style)
    """
    return {
        "color": CONFIG_COLORS.get(config, "#1f77b4"),
        "linestyle": CONFIG_LINESTYLES.get(config, "-"),
    }
