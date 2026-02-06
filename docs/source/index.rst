climplot: Climate Science Plotting
==================================

**climplot** is a Python package for creating publication-quality climate science
figures with minimal effort.

.. code-block:: python

   import climplot

   climplot.publication()  # Set publication style
   fig, ax = climplot.map_figure()  # Create a map

Features
--------

- **Style Modes**: Switch between publication and presentation styles
- **Climate Colormaps**: Optimized for anomaly fields, with center-on-white option
- **Map Utilities**: Easy map creation with Cartopy projections
- **Multi-panel Figures**: Consistent panel labeling and colorbars
- **Area-weighted Metrics**: Accurate statistics for gridded climate data

Installation
------------

.. code-block:: bash

   pip install climplot

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   style-guide

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api

.. toctree::
   :maxdepth: 1
   :caption: Additional Info

   metrics

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
