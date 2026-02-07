"""
Map plotting utilities with Cartopy projections.

This module provides functions for creating publication-quality maps
with appropriate projections, coastlines, and land overlays.

Examples
--------
>>> import climplot
>>> climplot.publication()
>>> fig, ax = climplot.map_figure()
>>> cs = ax.pcolormesh(lon, lat, data, transform=ccrs.PlateCarree())
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, Optional

# Cartopy imports (required dependency)
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def map_figure(
    projection: str = "robinson",
    central_longitude: float = 180,
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a map figure with specified projection.

    Parameters
    ----------
    projection : str, optional
        Map projection name. Options:
        - 'robinson' (default): Good for global maps
        - 'platecarree': Equirectangular, simple lat/lon
        - 'mollweide': Equal-area, good for global
        - 'orthographic': Globe view
        - 'mercator': Standard navigation projection
        - 'northpolarstereo': Arctic view
        - 'southpolarstereo': Antarctic view
    central_longitude : float, optional
        Central longitude for projection. Default is 180 (Pacific-centered).
    figsize : tuple, optional
        Figure size (width, height) in inches. If None, uses matplotlib defaults.
    **kwargs
        Additional arguments passed to plt.figure()

    Returns
    -------
    fig : Figure
        The figure object
    ax : GeoAxes
        The map axes with specified projection

    Examples
    --------
    >>> # Global Robinson projection (Pacific-centered)
    >>> fig, ax = climplot.map_figure()

    >>> # Atlantic-centered
    >>> fig, ax = climplot.map_figure(central_longitude=0)

    >>> # Plate Carree for regional maps
    >>> fig, ax = climplot.map_figure(projection='platecarree')
    """
    # Get projection
    proj = _get_projection(projection, central_longitude)

    # Create figure
    if figsize is not None:
        kwargs["figsize"] = figsize
    fig = plt.figure(**kwargs)
    ax = fig.add_subplot(111, projection=proj)

    return fig, ax


def _get_projection(name: str, central_longitude: float = 180):
    """Get a cartopy projection by name."""
    projections = {
        "robinson": ccrs.Robinson(central_longitude=central_longitude),
        "platecarree": ccrs.PlateCarree(central_longitude=central_longitude),
        "mollweide": ccrs.Mollweide(central_longitude=central_longitude),
        "orthographic": ccrs.Orthographic(
            central_longitude=central_longitude, central_latitude=0
        ),
        "mercator": ccrs.Mercator(central_longitude=central_longitude),
        "northpolarstereo": ccrs.NorthPolarStereo(),
        "southpolarstereo": ccrs.SouthPolarStereo(),
    }

    name_lower = name.lower().replace("_", "").replace("-", "")
    if name_lower not in projections:
        raise ValueError(
            f"Unknown projection: {name}. "
            f"Available: {list(projections.keys())}"
        )

    return projections[name_lower]


def add_land_overlay(
    ax: plt.Axes,
    lon,
    lat,
    wet_mask,
    land_color: str = "#808080",
    zorder: int = 10,
):
    """
    Add gray overlay to render land areas.

    Draws a solid color layer over land points (wet=0), ensuring
    continents appear uniformly regardless of underlying data values.
    Uses pcolormesh internally, so ``lon`` and ``lat`` must be cell-center
    coordinates (same shape as ``wet_mask``).

    .. note::

       When the data pcolormesh uses **corner** coordinates (e.g.
       ``geolon_c`` / ``geolat_c``), this function should not be used
       because the coordinate shapes will not match. Instead, set a gray
       axis background before plotting::

           ax.set_facecolor("#808080")
           ax.pcolormesh(geolon_c, geolat_c, data, ...)

       Model data is NaN over land, so the gray background shows through
       and reveals the model's true coastline.

       For regridded or observational data (no wet mask available), use
       :func:`add_land_feature` instead.

    Parameters
    ----------
    ax : GeoAxes
        Map axes to add overlay to
    lon : array-like
        2D longitude array (cell centers, same shape as wet_mask)
    lat : array-like
        2D latitude array (cell centers, same shape as wet_mask)
    wet_mask : array-like
        Wet mask where 1 = ocean, 0 = land
    land_color : str, optional
        Color for land. Default is '#808080' (medium gray).
    zorder : int, optional
        Drawing order. Default is 10 (on top of most elements).

    Examples
    --------
    >>> fig, ax = climplot.map_figure()
    >>> cs = ax.pcolormesh(lon, lat, data, transform=ccrs.PlateCarree())
    >>> climplot.add_land_overlay(ax, lon, lat, wet_mask)
    """
    import xarray as xr
    from matplotlib.colors import ListedColormap

    # Create land overlay: 1 where land (wet=0), NaN where ocean
    land_overlay = xr.where(wet_mask == 0, 1.0, np.nan)

    # Single-color colormap
    gray_cmap = ListedColormap([land_color])

    # Draw over land
    ax.pcolormesh(
        lon,
        lat,
        land_overlay,
        transform=ccrs.PlateCarree(),
        cmap=gray_cmap,
        vmin=0,
        vmax=1,
        zorder=zorder,
    )


def add_coastlines(
    ax: plt.Axes,
    resolution: str = "110m",
    linewidth: float = 0.5,
    color: str = "black",
    **kwargs,
):
    """
    Add coastlines to a map.

    Parameters
    ----------
    ax : GeoAxes
        Map axes
    resolution : str, optional
        Resolution: '110m' (default), '50m', or '10m'.
        Higher resolution = more detail but slower.
    linewidth : float, optional
        Line width. Default is 0.5.
    color : str, optional
        Line color. Default is 'black'.
    **kwargs
        Additional arguments passed to ax.coastlines()

    Examples
    --------
    >>> fig, ax = climplot.map_figure()
    >>> climplot.add_coastlines(ax)

    Notes
    -----
    For model data on native grids, consider using add_land_overlay()
    instead of coastlines, as coastlines may not align with the model grid.
    """
    ax.coastlines(resolution=resolution, linewidth=linewidth, color=color, **kwargs)


def add_land_feature(
    ax: plt.Axes,
    resolution: str = "110m",
    facecolor: str = "#808080",
    edgecolor: str = "none",
    **kwargs,
):
    """
    Add land feature (filled continents) to a map.

    Parameters
    ----------
    ax : GeoAxes
        Map axes
    resolution : str, optional
        Resolution: '110m' (default), '50m', or '10m'.
    facecolor : str, optional
        Fill color. Default is '#808080' (gray).
    edgecolor : str, optional
        Edge color. Default is 'none'.
    **kwargs
        Additional arguments passed to ax.add_feature()

    Examples
    --------
    >>> fig, ax = climplot.map_figure()
    >>> climplot.add_land_feature(ax)
    """
    land = cfeature.NaturalEarthFeature(
        "physical", "land", resolution, facecolor=facecolor, edgecolor=edgecolor
    )
    ax.add_feature(land, **kwargs)
