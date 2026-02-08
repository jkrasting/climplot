# climplot

Publication-quality climate science plotting utilities for Python.

**Mission:** Help climate science beginners make beautiful, publication-ready plots with minimal effort.

## Features

- **Style Modes**: Switch between publication and presentation styles with one function call
- **Climate Colormaps**: Discrete colormaps optimized for anomaly fields, with center-on-white option
- **Map Utilities**: Easy map creation with Cartopy projections
- **Multi-panel Figures**: Consistent panel labeling and colorbars
- **Area-weighted Metrics**: Accurate statistics for gridded climate data

## Installation

```bash
pip install climplot
```

Or install from source:

```bash
git clone https://github.com/jkrasting/climplot.git
cd climplot
pip install -e .
```

## Quick Start

```python
import climplot
import matplotlib.pyplot as plt

# Set publication style
climplot.publication()

# Create a map figure
fig, ax = climplot.map_figure()

# Plot with discrete colormap
cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)
cs = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())

# Add colorbar
climplot.add_colorbar(cs, ax, 'SSH Anomaly (m)')

# Save
climplot.save_figure('my_figure.png')
plt.close()
```

## Style Modes

### Publication Mode
For journal figures with small, dense typography:
- 3.5" width (single-column), 7.0" (two-column)
- 8-11pt fonts
- 300 DPI

```python
climplot.publication()  # Single column
climplot.publication(width=7.0)  # Two-column
climplot.publication(for_pdf=True)  # PDF with embedded fonts
```

### Presentation Mode
For slides and posters with larger, readable typography:
- 7.0" width
- 12-16pt fonts
- 150 DPI

```python
climplot.presentation()
climplot.presentation(for_pdf=True)  # PDF for slides
```

## Colormaps

### Anomaly Colormap
Red-blue diverging, centered on zero:

```python
cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)
```

### Center-on-White
For difference plots where near-zero values should appear neutral:

```python
cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05, center_on_white=True)
```

## Maps

### Projections

```python
# Robinson projection (Pacific-centered)
fig, ax = climplot.map_figure()

# Atlantic-centered
fig, ax = climplot.map_figure(central_longitude=0)

# Different projection
fig, ax = climplot.map_figure(projection='mollweide')
```

### Rendering Land: Three Workflows

**Atmosphere / lat-lon grids** (reanalysis, CMIP atmos, observations):

```python
fig, ax = climplot.map_figure()
cmap, norm, levels = climplot.anomaly_cmap(-2, 2, 0.5)
cs = climplot.plot_atmos_field(
    ax, lon, lat, temperature,
    cmap=cmap, norm=norm, levels=levels,
)
climplot.add_gridlines(ax, x_spacing=30, y_spacing=30)  # optional
climplot.add_colorbar(cs, ax, 'Temperature Anomaly (K)')
```

`plot_atmos_field` draws light-gray land underneath, plots data with slight transparency on top, and adds thin coastlines — all in one call.

**Regular / regridded grids** (observations, reanalysis on 1°×1°, etc.):

```python
fig, ax = climplot.map_figure()
cs = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm,
                   transform=ccrs.PlateCarree())
climplot.add_land_feature(ax)    # filled gray continents from Natural Earth
climplot.add_coastlines(ax)      # optional coastline outlines
```

**Native ocean-model grids** (tripolar, MOM6 — Cartopy coastlines won't align):

```python
fig, ax = climplot.map_figure()
cs = climplot.plot_ocean_field(
    ax, geolon_c, geolat_c, sst,
    wet_mask=wet,   # 1=ocean, 0=land
)
```

`plot_ocean_field` sets a gray background so NaN over land renders as the model's coastline, optionally masks land, and plots the data in one call. See the [Plotting Guide](docs/plotting-guide.md) for full details.

## Multi-panel Figures

```python
# 2x3 panel figure
fig, axes = climplot.panel_figure(2, 3)

# Add panel labels (a. b. c. etc.)
climplot.add_panel_labels(axes.flatten())

# Single colorbar below all panels
climplot.bottom_colorbar(cs, fig, axes, 'Temperature (K)')
```

## Area-weighted Metrics

**Why area weighting matters:** Simple averaging over-weights polar regions.
This can produce errors of ~1 cm in global sea level means.

```python
import climplot

# Area-weighted mean (CORRECT)
gmsl = climplot.area_weighted_mean(ssh, areacello, dim=['yh', 'xh'])

# Simple mean (WRONG - ~1 cm error)
# gmsl = ssh.mean(dim=['yh', 'xh'])

# Other metrics
bias = climplot.area_weighted_bias(model, obs, areacello, dim=['yh', 'xh'])
rmse = climplot.area_weighted_rmse(model, obs, areacello, dim=['yh', 'xh'])
corr = climplot.area_weighted_corr(model, obs, areacello, dim=['yh', 'xh'])

# Comprehensive summary
metrics = climplot.metrics_summary(model, obs, areacello, dim=['yh', 'xh'])
climplot.print_metrics_summary(metrics, name='My Model')
```

## Dependencies

- matplotlib >= 3.7
- numpy >= 1.24
- xarray >= 2023.1
- cartopy >= 0.21

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions are welcome! Please see our [contributing guide](CONTRIBUTING.md).
