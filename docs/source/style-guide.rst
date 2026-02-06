Style Guide
===========

This guide provides recommendations for creating consistent, publication-quality
climate science figures.

Figure Dimensions
-----------------

Standard Sizes
~~~~~~~~~~~~~~

- **Single-column figure**: 3.5 inches wide (89 mm)
- **Two-column figure**: 7.0 inches wide (178 mm)
- **Height**: Typically 2.5-5.0 inches

Resolution
~~~~~~~~~~

- **Publication**: 300 DPI
- **Presentation**: 150 DPI
- **Format**: PNG (default) or PDF

Typography
----------

Publication Mode
~~~~~~~~~~~~~~~~

For journal figures with smaller, dense typography:

============== ======
Element        Size
============== ======
Axis labels    10 pt
Tick labels    8 pt
Titles         11 pt
Legends        8 pt
Colorbar labels 8 pt
============== ======

.. code-block:: python

   climplot.publication()

Presentation Mode
~~~~~~~~~~~~~~~~~

For slides and posters with larger, readable typography:

============== ======
Element        Size
============== ======
Axis labels    14 pt
Tick labels    14 pt
Titles         16 pt
Legends        12 pt
Colorbar labels 12 pt
============== ======

.. code-block:: python

   climplot.presentation()

Color Schemes
-------------

Anomaly Fields
~~~~~~~~~~~~~~

- **Colormap**: ``RdBu_r`` (red-blue diverging, reversed)
- **Convention**: Red = positive, Blue = negative
- **Center**: Always center on zero
- **Levels**: Use discrete levels with BoundaryNorm

.. code-block:: python

   cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)

Difference Plots
~~~~~~~~~~~~~~~~

For difference plots (model - obs), use center-on-white:

.. code-block:: python

   cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05, center_on_white=True)

This creates a white band for near-zero values, highlighting where differences
are negligible (white) versus substantial (red/blue).

Level Selection
~~~~~~~~~~~~~~~

Always use "round" intervals ending in 0, 1, 2, or 5:

- 0.01, 0.02, 0.05
- 0.10, 0.20, 0.50
- 1.0, 2.0, 5.0, 10.0

Map Projections
---------------

Global Maps
~~~~~~~~~~~

- **Default**: Robinson projection
- **Central longitude**: 180° (Pacific-centered)

.. code-block:: python

   fig, ax = climplot.map_figure()  # Robinson, Pacific-centered
   fig, ax = climplot.map_figure(central_longitude=0)  # Atlantic-centered

Land Rendering
~~~~~~~~~~~~~~

For model data on native grids, use explicit gray overlay:

.. code-block:: python

   climplot.add_land_overlay(ax, lon, lat, wet_mask)

Do NOT use cartopy coastlines for model data - they won't align with the grid.

Colorbars
---------

- **Orientation**: Horizontal below plot (for maps)
- **Extensions**: Always use ``extend='both'``
- **Labels**: Always include units

.. code-block:: python

   climplot.add_colorbar(cs, ax, 'SSH Anomaly (m)')

Multi-Panel Figures
-------------------

- Use ``constrained_layout=True`` (default in ``panel_figure``)
- Label panels: **a.** **b.** **c.** **d.** (bold)

.. code-block:: python

   fig, axes = climplot.panel_figure(2, 2)
   climplot.add_panel_labels(axes.flatten())

Common Pitfalls
---------------

1. Don't forget units in axis labels and colorbar labels
2. Don't use simple mean for global statistics (use area-weighted)
3. Don't use asymmetric color limits for centered anomaly fields
4. Don't use rainbow colormaps (jet, etc.)
5. Don't use continuous colormaps - always use discrete levels
6. Don't use awkward intervals - stick to 0, 1, 2, or 5 endings
7. Don't make fonts too small - 8pt minimum
8. Don't forget ``extend='both'`` on colorbars
9. Don't add gridlines to maps
10. Don't save without ``bbox_inches='tight'``

See Also
--------

For a beginner-friendly version of this guide with visual examples, see
`docs/plotting-guide.md <../plotting-guide.md>`_.
