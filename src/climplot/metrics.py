"""
Area-weighted statistical metrics for climate data.

This module provides functions for calculating area-weighted statistics
that are essential for accurate global and regional analyses of gridded
climate data.

Why Area Weighting Matters
--------------------------
Ocean/atmosphere grid cells near the poles are much smaller than equatorial
cells. Simple averaging treats all cells equally, over-weighting high
latitudes. This can produce errors of ~1 cm in global sea level means
or ~2 cm in RMSE calculations.

Examples
--------
>>> import climplot
>>> # Area-weighted global mean
>>> gmsl = climplot.area_weighted_mean(ssh, areacello, dim=['yh', 'xh'])

>>> # Area-weighted RMSE
>>> rmse = climplot.area_weighted_rmse(model, obs, areacello, dim=['yh', 'xh'])
"""

import numpy as np
import xarray as xr
from typing import Union, List, Optional


def area_weighted_mean(
    data: xr.DataArray,
    weights: xr.DataArray,
    dim: Optional[Union[str, List[str]]] = None,
) -> Union[xr.DataArray, float]:
    """
    Calculate area-weighted mean.

    Parameters
    ----------
    data : DataArray
        Data to average
    weights : DataArray
        Area weights (e.g., areacello grid cell areas)
    dim : str or list of str, optional
        Dimensions to average over. If None, averages over all.
        Common: dim=['yh', 'xh'] for spatial mean.

    Returns
    -------
    DataArray or float
        Area-weighted mean

    Examples
    --------
    >>> # Global mean SSH
    >>> gmsl = climplot.area_weighted_mean(ssh, areacello, dim=['yh', 'xh'])

    >>> # Time series of global mean
    >>> gmsl_ts = climplot.area_weighted_mean(ssh_3d, areacello, dim=['yh', 'xh'])

    Notes
    -----
    - NaN values are automatically excluded
    - Weights are normalized internally
    """
    # Mask where data or weights are NaN
    valid_mask = ~(np.isnan(data) | np.isnan(weights))

    data_masked = data.where(valid_mask)
    weights_masked = weights.where(valid_mask)

    weighted_sum = (data_masked * weights_masked).sum(dim=dim, skipna=True)
    total_weight = weights_masked.sum(dim=dim, skipna=True)

    return weighted_sum / total_weight


def area_weighted_bias(
    model: xr.DataArray,
    obs: xr.DataArray,
    weights: xr.DataArray,
    dim: Optional[Union[str, List[str]]] = None,
) -> Union[xr.DataArray, float]:
    """
    Calculate area-weighted mean bias (model - obs).

    Parameters
    ----------
    model : DataArray
        Model data
    obs : DataArray
        Observational data
    weights : DataArray
        Area weights
    dim : str or list of str, optional
        Dimensions to average over

    Returns
    -------
    DataArray or float
        Mean bias (positive = model too high)

    Examples
    --------
    >>> bias = climplot.area_weighted_bias(ssh_model, ssh_obs, areacello, dim=['yh', 'xh'])
    """
    diff = model - obs
    return area_weighted_mean(diff, weights, dim=dim)


def area_weighted_rmse(
    model: xr.DataArray,
    obs: xr.DataArray,
    weights: xr.DataArray,
    dim: Optional[Union[str, List[str]]] = None,
) -> Union[xr.DataArray, float]:
    """
    Calculate area-weighted root-mean-square error.

    Parameters
    ----------
    model : DataArray
        Model data
    obs : DataArray
        Observational data
    weights : DataArray
        Area weights
    dim : str or list of str, optional
        Dimensions to average over

    Returns
    -------
    DataArray or float
        RMSE (always positive)

    Examples
    --------
    >>> rmse = climplot.area_weighted_rmse(ssh_model, ssh_obs, areacello, dim=['yh', 'xh'])
    """
    squared_diff = (model - obs) ** 2
    mse = area_weighted_mean(squared_diff, weights, dim=dim)
    return np.sqrt(mse)


def area_weighted_std(
    data: xr.DataArray,
    weights: xr.DataArray,
    dim: Optional[Union[str, List[str]]] = None,
) -> Union[xr.DataArray, float]:
    """
    Calculate area-weighted standard deviation.

    Parameters
    ----------
    data : DataArray
        Data to compute std for
    weights : DataArray
        Area weights
    dim : str or list of str, optional
        Dimensions to compute over

    Returns
    -------
    DataArray or float
        Standard deviation

    Examples
    --------
    >>> spatial_std = climplot.area_weighted_std(ssh, areacello, dim=['yh', 'xh'])
    """
    mean = area_weighted_mean(data, weights, dim=dim)
    squared_dev = (data - mean) ** 2
    variance = area_weighted_mean(squared_dev, weights, dim=dim)
    return np.sqrt(variance)


def area_weighted_corr(
    x: xr.DataArray,
    y: xr.DataArray,
    weights: xr.DataArray,
    dim: Optional[Union[str, List[str]]] = None,
) -> Union[xr.DataArray, float]:
    """
    Calculate area-weighted pattern correlation coefficient.

    Parameters
    ----------
    x : DataArray
        First field (e.g., model)
    y : DataArray
        Second field (e.g., observations)
    weights : DataArray
        Area weights
    dim : str or list of str, optional
        Dimensions to compute over

    Returns
    -------
    DataArray or float
        Correlation coefficient (-1 to 1)

    Examples
    --------
    >>> r = climplot.area_weighted_corr(ssh_model, ssh_obs, areacello, dim=['yh', 'xh'])
    """
    x_mean = area_weighted_mean(x, weights, dim=dim)
    y_mean = area_weighted_mean(y, weights, dim=dim)

    x_anom = x - x_mean
    y_anom = y - y_mean

    covariance = area_weighted_mean(x_anom * y_anom, weights, dim=dim)
    x_var = area_weighted_mean(x_anom**2, weights, dim=dim)
    y_var = area_weighted_mean(y_anom**2, weights, dim=dim)

    return covariance / np.sqrt(x_var * y_var)


# ============================================================================
# Time Series Metrics (1D arrays, no area weighting)
# ============================================================================


def timeseries_bias(
    model: Union[np.ndarray, xr.DataArray],
    obs: Union[np.ndarray, xr.DataArray],
) -> float:
    """
    Calculate mean bias for time series.

    Parameters
    ----------
    model : array-like
        Model time series
    obs : array-like
        Observed time series

    Returns
    -------
    float
        Mean bias (positive = model too high)

    Examples
    --------
    >>> bias = climplot.timeseries_bias(gmsl_model, gmsl_obs)
    """
    diff = np.array(model) - np.array(obs)
    return float(np.nanmean(diff))


def timeseries_rmse(
    model: Union[np.ndarray, xr.DataArray],
    obs: Union[np.ndarray, xr.DataArray],
) -> float:
    """
    Calculate RMSE for time series.

    Parameters
    ----------
    model : array-like
        Model time series
    obs : array-like
        Observed time series

    Returns
    -------
    float
        RMSE (always positive)

    Examples
    --------
    >>> rmse = climplot.timeseries_rmse(gmsl_model, gmsl_obs)
    """
    diff = np.array(model) - np.array(obs)
    return float(np.sqrt(np.nanmean(diff**2)))


def timeseries_corr(
    x: Union[np.ndarray, xr.DataArray],
    y: Union[np.ndarray, xr.DataArray],
) -> float:
    """
    Calculate correlation coefficient for time series.

    Parameters
    ----------
    x : array-like
        First time series
    y : array-like
        Second time series

    Returns
    -------
    float
        Correlation coefficient (-1 to 1)

    Examples
    --------
    >>> r = climplot.timeseries_corr(gmsl_model, gmsl_obs)
    """
    x_arr = np.array(x)
    y_arr = np.array(y)

    valid = ~(np.isnan(x_arr) | np.isnan(y_arr))
    x_valid = x_arr[valid]
    y_valid = y_arr[valid]

    return float(np.corrcoef(x_valid, y_valid)[0, 1])


def timeseries_std(data: Union[np.ndarray, xr.DataArray]) -> float:
    """
    Calculate standard deviation for time series.

    Parameters
    ----------
    data : array-like
        Time series data

    Returns
    -------
    float
        Standard deviation

    Examples
    --------
    >>> std = climplot.timeseries_std(gmsl)
    """
    return float(np.nanstd(data))


# ============================================================================
# Summary Functions
# ============================================================================


def metrics_summary(
    model: xr.DataArray,
    obs: xr.DataArray,
    weights: xr.DataArray,
    dim: Optional[Union[str, List[str]]] = None,
    name: str = "Model",
) -> dict:
    """
    Calculate comprehensive validation metrics.

    Parameters
    ----------
    model : DataArray
        Model data
    obs : DataArray
        Observational data
    weights : DataArray
        Area weights
    dim : str or list of str, optional
        Dimensions to compute over
    name : str, optional
        Model name for output

    Returns
    -------
    dict
        Dictionary with bias, rmse, correlation, means, and stds

    Examples
    --------
    >>> metrics = climplot.metrics_summary(ssh_model, ssh_obs, areacello, dim=['yh', 'xh'])
    >>> print(f"RMSE: {metrics['rmse']:.3f}")
    """
    return {
        "bias": float(area_weighted_bias(model, obs, weights, dim=dim)),
        "rmse": float(area_weighted_rmse(model, obs, weights, dim=dim)),
        "correlation": float(area_weighted_corr(model, obs, weights, dim=dim)),
        "model_mean": float(area_weighted_mean(model, weights, dim=dim)),
        "obs_mean": float(area_weighted_mean(obs, weights, dim=dim)),
        "model_std": float(area_weighted_std(model, weights, dim=dim)),
        "obs_std": float(area_weighted_std(obs, weights, dim=dim)),
    }


def print_metrics_summary(metrics: dict, name: str = "Model"):
    """
    Print formatted metrics summary.

    Parameters
    ----------
    metrics : dict
        Dictionary from metrics_summary()
    name : str
        Model name for display

    Examples
    --------
    >>> metrics = climplot.metrics_summary(model, obs, weights, dim=['yh', 'xh'])
    >>> climplot.print_metrics_summary(metrics, name='OM5 b01')
    """
    print(f"\n{name} Validation Metrics:")
    print(f"  Bias (model - obs):     {metrics['bias']:+.4f}")
    print(f"  RMSE:                   {metrics['rmse']:.4f}")
    print(f"  Correlation:            {metrics['correlation']:.4f}")
    print(f"  Model mean:             {metrics['model_mean']:.4f}")
    print(f"  Obs mean:               {metrics['obs_mean']:.4f}")
    print(f"  Model std:              {metrics['model_std']:.4f}")
    print(f"  Obs std:                {metrics['obs_std']:.4f}")
