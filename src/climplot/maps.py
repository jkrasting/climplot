"""
Map plotting utilities with Cartopy projections.

This module provides functions for creating publication-quality maps
with appropriate projections, coastlines, and land overlays.

Two workflows for rendering land
---------------------------------
Choose based on your grid type:

* **Regular / regridded grids** (observations, reanalysis on 1°×1°):
  Use :func:`map_figure` + :func:`add_land_feature` (filled gray continents
  from Natural Earth) and optionally :func:`add_coastlines`.

* **Native ocean-model grids** (tripolar, MOM6):
  Use :func:`plot_ocean_field`, which bundles the recommended workflow:
  gray background for land, optional land masking via ``wet_mask``, and
  plotting with pcolormesh/contourf/contour.  Do **not** use
  :func:`add_land_feature` or :func:`add_coastlines` on native grids —
  Cartopy coastlines will not align with the model's land/sea boundary.

Coordinate conventions for ``plot_ocean_field``
------------------------------------------------
* ``method="pcolormesh"`` → pass **corner** coordinates (``geolon_c``,
  ``geolat_c``).
* ``method="contourf"`` or ``"contour"`` → pass **center** coordinates
  (``geolon``, ``geolat``).

Examples
--------
Regular grid:

>>> import climplot, cartopy.crs as ccrs
>>> fig, ax = climplot.map_figure()
>>> cs = ax.pcolormesh(lon, lat, data, transform=ccrs.PlateCarree())
>>> climplot.add_land_feature(ax)

Native ocean-model grid:

>>> fig, ax = climplot.map_figure()
>>> cs = climplot.plot_ocean_field(
...     ax, geolon_c, geolat_c, sst, wet_mask=wet,
... )
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
       because the coordinate shapes will not match. Use
       :func:`plot_ocean_field` instead, or call
       :func:`set_land_background` before plotting manually.

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
    For model data on native grids (e.g. tripolar ocean models), Cartopy
    coastlines will not align with the model's land/sea mask. Use
    :func:`plot_ocean_field` or :func:`add_land_overlay` instead.
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


def set_land_background(ax: plt.Axes, land_color: str = "#808080"):
    """
    Set axis background color so NaN values render as land.

    For native ocean-model grids, data is typically NaN over land.
    Setting the axis facecolor to a land-like color makes these NaN
    regions appear as land without needing a separate overlay.

    Parameters
    ----------
    ax : GeoAxes
        Map axes.
    land_color : str, optional
        Background color for land. Default is '#808080' (medium gray).

    Examples
    --------
    >>> fig, ax = climplot.map_figure()
    >>> climplot.set_land_background(ax)
    >>> ax.pcolormesh(geolon_c, geolat_c, data, transform=ccrs.PlateCarree())
    """
    ax.set_facecolor(land_color)


def mask_land(data, wet_mask):
    """
    Mask land points by setting them to NaN.

    Parameters
    ----------
    data : array-like or xarray.DataArray
        Data to mask. Must be broadcastable with ``wet_mask``.
    wet_mask : array-like or xarray.DataArray
        Mask where 1 = ocean and 0 = land.

    Returns
    -------
    masked : same type as ``data``
        Copy of ``data`` with land points set to NaN.

    Examples
    --------
    >>> masked_sst = climplot.mask_land(sst, wet_mask)
    """
    try:
        import xarray as xr

        if isinstance(data, xr.DataArray) or isinstance(wet_mask, xr.DataArray):
            return xr.where(wet_mask == 1, data, np.nan)
    except ImportError:
        pass

    data = np.array(data, dtype=float)
    wet_mask = np.asarray(wet_mask)
    return np.where(wet_mask == 1, data, np.nan)


def plot_ocean_field(
    ax: plt.Axes,
    lon,
    lat,
    data,
    wet_mask=None,
    land_color: str = "#808080",
    method: str = "pcolormesh",
    **kwargs,
):
    """
    Plot an ocean field on a native model grid.

    Convenience function that bundles the recommended workflow for
    tripolar / native ocean-model grids:

    1. Sets a gray background so NaN over land shows the model's coastline.
    2. Optionally masks land points using ``wet_mask``.
    3. Plots using the specified ``method``.

    Parameters
    ----------
    ax : GeoAxes
        Map axes (e.g. from :func:`map_figure`).
    lon : array-like
        Longitude coordinates. For ``method="pcolormesh"`` these should be
        **corner** coordinates (e.g. ``geolon_c``). For ``"contourf"`` and
        ``"contour"`` these should be **center** coordinates.
    lat : array-like
        Latitude coordinates (same convention as ``lon``).
    data : array-like
        2-D field to plot.
    wet_mask : array-like, optional
        Mask where 1 = ocean and 0 = land. If provided, land points in
        ``data`` are set to NaN before plotting.
    land_color : str, optional
        Background color for land. Default is '#808080'.
    method : str, optional
        Plot method: ``"pcolormesh"`` (default), ``"contourf"``, or
        ``"contour"``.
    **kwargs
        Forwarded to the underlying matplotlib plot call.

    Returns
    -------
    artist : QuadMesh or QuadContourSet
        The plot artist, suitable for passing to ``plt.colorbar()``.

    Raises
    ------
    ValueError
        If ``method`` is not one of the supported values.

    Examples
    --------
    >>> fig, ax = climplot.map_figure()
    >>> cs = climplot.plot_ocean_field(
    ...     ax, geolon_c, geolat_c, sst, wet_mask=wet,
    ... )
    >>> plt.colorbar(cs, ax=ax)
    """
    valid_methods = ("pcolormesh", "contourf", "contour")
    if method not in valid_methods:
        raise ValueError(
            f"Unknown method: {method!r}. Must be one of {valid_methods}"
        )

    set_land_background(ax, land_color)

    if wet_mask is not None:
        data = mask_land(data, wet_mask)

    kwargs.setdefault("transform", ccrs.PlateCarree())

    plot_func = getattr(ax, method)
    return plot_func(lon, lat, data, **kwargs)
