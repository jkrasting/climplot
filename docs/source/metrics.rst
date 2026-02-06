Area-Weighted Metrics Guide
===========================

Why Area Weighting Matters
--------------------------

**The Problem:**

Ocean and atmosphere grid cells near the poles are much smaller than equatorial
cells. A simple ``.mean()`` treats all cells equally, which over-weights high
latitudes.

**Errors without area weighting:**

- ~1 cm error in global mean sea level
- ~2 cm error in RMSE calculations
- Incorrect pattern correlations

**The Solution:**

Use area weights (``areacello`` for ocean, ``areacella`` for atmosphere) to
properly weight each grid cell by its area.

Core Functions
--------------

Area-Weighted Mean
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import climplot

   # Global mean SSH (CORRECT)
   gmsl = climplot.area_weighted_mean(ssh, areacello, dim=['yh', 'xh'])

   # Simple mean (WRONG - ~1 cm error)
   # gmsl_wrong = ssh.mean(dim=['yh', 'xh'])

Area-Weighted Bias
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Model - observation bias
   bias = climplot.area_weighted_bias(ssh_model, ssh_obs, areacello, dim=['yh', 'xh'])

Area-Weighted RMSE
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   rmse = climplot.area_weighted_rmse(ssh_model, ssh_obs, areacello, dim=['yh', 'xh'])

Pattern Correlation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   corr = climplot.area_weighted_corr(ssh_model, ssh_obs, areacello, dim=['yh', 'xh'])

Time Series Metrics
-------------------

For 1D time series that are already spatially averaged:

.. code-block:: python

   # Bias
   bias_ts = climplot.timeseries_bias(gmsl_model, gmsl_obs)

   # RMSE
   rmse_ts = climplot.timeseries_rmse(gmsl_model, gmsl_obs)

   # Correlation
   corr_ts = climplot.timeseries_corr(gmsl_model, gmsl_obs)

Comprehensive Summary
---------------------

Get all metrics at once:

.. code-block:: python

   metrics = climplot.metrics_summary(
       ssh_model, ssh_obs, areacello,
       dim=['yh', 'xh'],
       name='My Model'
   )

   climplot.print_metrics_summary(metrics, name='My Model')

Output::

   My Model Validation Metrics:
     Bias (model - obs):     +0.0012
     RMSE:                   0.0456
     Correlation:            0.9234
     Model mean:             0.0023
     Obs mean:               0.0011
     Model std:              0.0789
     Obs std:                0.0812

Usage Guidelines
----------------

**ALWAYS use area weighting for:**

- Global mean calculations
- Regional/basin statistics
- Model-observation bias
- RMSE calculations
- Pattern correlation
- Spatial variance/std

**DO NOT use simple** ``.mean()`` **for spatial fields!**

NaN Handling
------------

All climplot metrics functions automatically handle NaN values:

- NaN values are excluded from calculations
- Area weights are renormalized
- Works with both numpy arrays and xarray DataArrays
- Tested with up to 30% missing data

Example Workflow
----------------

.. code-block:: python

   import xarray as xr
   import climplot

   # Load data
   ds_model = xr.open_dataset('model_output.nc')
   ds_obs = xr.open_dataset('observations.nc')

   ssh_model = ds_model['SSH']
   ssh_obs = ds_obs['sla']
   area = ds_model['areacello']

   # Global mean time series
   gmsl_model = climplot.area_weighted_mean(ssh_model, area, dim=['yh', 'xh'])
   gmsl_obs = climplot.area_weighted_mean(ssh_obs, area, dim=['yh', 'xh'])

   # Time series metrics
   print(f"Bias: {climplot.timeseries_bias(gmsl_model, gmsl_obs):.4f} m")
   print(f"RMSE: {climplot.timeseries_rmse(gmsl_model, gmsl_obs):.4f} m")
   print(f"Corr: {climplot.timeseries_corr(gmsl_model, gmsl_obs):.4f}")

   # Spatial pattern metrics (climatology)
   ssh_model_clim = ssh_model.mean(dim='time')
   ssh_obs_clim = ssh_obs.mean(dim='time')

   metrics = climplot.metrics_summary(ssh_model_clim, ssh_obs_clim, area, dim=['yh', 'xh'])
   climplot.print_metrics_summary(metrics, name='Model Climatology')
