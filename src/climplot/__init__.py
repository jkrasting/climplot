"""
climplot - Publication-quality climate science plotting utilities.

A Python package for creating beautiful, publication-ready climate and weather
science figures with minimal effort. Designed for climate science beginners
and experts alike.

Quick Start
-----------
>>> import climplot
>>> climplot.publication()  # Set up publication-quality defaults
>>> fig, ax = climplot.map_figure()  # Create a map with Robinson projection

Style Modes
-----------
- climplot.publication(): 3.5" width, 8-11pt fonts, 300 DPI
- climplot.presentation(): 7" width, 12-16pt fonts, 150 DPI

See Also
--------
- Documentation: https://climplot.readthedocs.io
- Source: https://github.com/jkrasting/climplot
"""

from importlib.metadata import version as _version

__version__ = _version("climplot")

# Style functions
from .style import (
    publication,
    presentation,
    reset_style,
    get_current_mode,
)

# Colormap functions
from .colormaps import (
    anomaly_cmap,
    sequential_cmap,
    categorical_cmap,
    discrete_cmap,
    list_colormaps,
    auto_levels,
    log_cmap,
)

# Map functions
from .maps import (
    map_figure,
    add_land_overlay,
    add_coastlines,
    add_land_feature,
    set_land_background,
    mask_land,
    plot_ocean_field,
    plot_atmos_field,
    add_gridlines,
)

# Time series functions
from .timeseries import (
    timeseries_figure,
)

# Panel/multi-figure functions
from .panels import (
    panel_figure,
    add_panel_labels,
    add_colorbar,
    bottom_colorbar,
    save_figure,
)

# Metrics functions
from .metrics import (
    area_weighted_mean,
    area_weighted_bias,
    area_weighted_rmse,
    area_weighted_corr,
    area_weighted_std,
    timeseries_bias,
    timeseries_rmse,
    timeseries_corr,
    timeseries_std,
    metrics_summary,
    print_metrics_summary,
)

__all__ = [
    # Version
    "__version__",
    # Style
    "publication",
    "presentation",
    "reset_style",
    "get_current_mode",
    # Colormaps
    "anomaly_cmap",
    "sequential_cmap",
    "categorical_cmap",
    "discrete_cmap",
    "list_colormaps",
    "auto_levels",
    "log_cmap",
    # Maps
    "map_figure",
    "add_land_overlay",
    "add_coastlines",
    "add_land_feature",
    "set_land_background",
    "mask_land",
    "plot_ocean_field",
    "plot_atmos_field",
    "add_gridlines",
    # Time series
    "timeseries_figure",
    # Panels
    "panel_figure",
    "add_panel_labels",
    "add_colorbar",
    "bottom_colorbar",
    "save_figure",
    # Metrics
    "area_weighted_mean",
    "area_weighted_bias",
    "area_weighted_rmse",
    "area_weighted_corr",
    "area_weighted_std",
    "timeseries_bias",
    "timeseries_rmse",
    "timeseries_corr",
    "timeseries_std",
    "metrics_summary",
    "print_metrics_summary",
]
