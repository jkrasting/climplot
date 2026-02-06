Quick Start Guide
=================

This guide will get you making publication-quality climate figures in minutes.

Installation
------------

Install climplot using pip:

.. code-block:: bash

   pip install climplot

Basic Usage
-----------

Setting Up Style
~~~~~~~~~~~~~~~~

Always start by setting your style mode:

.. code-block:: python

   import climplot

   # For journal figures
   climplot.publication()

   # For slides/posters
   climplot.presentation()

Creating a Map
~~~~~~~~~~~~~~

.. code-block:: python

   import climplot
   import cartopy.crs as ccrs

   climplot.publication()

   # Create a Robinson projection map (Pacific-centered)
   fig, ax = climplot.map_figure()

   # Plot your data
   cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)
   cs = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm,
                      transform=ccrs.PlateCarree())

   # Add colorbar
   climplot.add_colorbar(cs, ax, 'SSH Anomaly (m)')

   # Save
   climplot.save_figure('my_map.png')

Time Series Plot
~~~~~~~~~~~~~~~~

.. code-block:: python

   import climplot

   climplot.publication()

   fig, ax = climplot.timeseries_figure()
   ax.plot(time, data, label='Model')
   ax.set_xlabel('Year')
   ax.set_ylabel('Sea Level (m)')
   ax.legend()

   climplot.save_figure('timeseries.png')

Multi-Panel Figure
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import climplot

   climplot.publication()

   # Create 2x2 panel figure
   fig, axes = climplot.panel_figure(2, 2)

   # Plot in each panel
   for i, ax in enumerate(axes.flat):
       ax.plot([1, 2, 3], [1, 4, 9])

   # Add panel labels (a. b. c. d.)
   climplot.add_panel_labels(axes.flatten())

   climplot.save_figure('panels.png')

Area-Weighted Statistics
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import climplot

   # CORRECT: Area-weighted mean
   gmsl = climplot.area_weighted_mean(ssh, areacello, dim=['yh', 'xh'])

   # WRONG: Simple mean (introduces ~1 cm error)
   # gmsl = ssh.mean(dim=['yh', 'xh'])

   # Model validation metrics
   rmse = climplot.area_weighted_rmse(model, obs, areacello, dim=['yh', 'xh'])
   corr = climplot.area_weighted_corr(model, obs, areacello, dim=['yh', 'xh'])

Next Steps
----------

- Read the :doc:`style-guide` for detailed style recommendations
- See the :doc:`api` for complete function reference
- Check the :doc:`metrics` guide for area-weighted statistics
