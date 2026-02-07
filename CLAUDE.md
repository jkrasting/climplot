# climplot — AI Agent Guide

## Land-Rendering Decision Rule

| Grid type | How to render land | Functions |
|---|---|---|
| **Native ocean-model grid** (tripolar, MOM6) | Gray background + NaN masking | `climplot.plot_ocean_field()` |
| **Regular / regridded grid** (obs, 1°×1°) | Cartopy Natural Earth land | `climplot.add_land_feature()` + `climplot.add_coastlines()` |

> **Do NOT** use `add_land_feature` or `add_coastlines` on native model grids — Cartopy coastlines will not align with the model's land/sea boundary.

## Workflow A — Native Ocean-Model Grids

Use `plot_ocean_field()`. It bundles three steps: gray background, land masking, and plotting.

```python
import climplot
import cartopy.crs as ccrs

climplot.publication()
fig, ax = climplot.map_figure()

# geolon_c / geolat_c are CORNER coordinates for pcolormesh
cs = climplot.plot_ocean_field(
    ax, geolon_c, geolat_c, sst,
    wet_mask=wet,          # 1=ocean, 0=land
    method="pcolormesh",   # default
    cmap=cmap, norm=norm,
)
climplot.add_colorbar(cs, ax, "SST (°C)")
climplot.save_figure("native_grid_sst.png")
```

### Corner vs Center Coordinates

| Plot method | Coordinate type | Typical MOM6 variable |
|---|---|---|
| `pcolormesh` | **Corner** (cell boundaries) | `geolon_c`, `geolat_c` |
| `contourf` | **Center** (cell midpoints) | `geolon`, `geolat` |
| `contour` | **Center** (cell midpoints) | `geolon`, `geolat` |

## Workflow B — Regular / Regridded Grids

Use `add_land_feature()` (filled gray continents) and optionally `add_coastlines()`.

```python
import climplot
import cartopy.crs as ccrs

climplot.publication()
fig, ax = climplot.map_figure()

cs = ax.pcolormesh(
    lon, lat, data,
    cmap=cmap, norm=norm,
    transform=ccrs.PlateCarree(),
)
climplot.add_land_feature(ax)      # filled gray continents
climplot.add_coastlines(ax)        # optional coastline outlines
climplot.add_colorbar(cs, ax, "SSH Anomaly (m)")
climplot.save_figure("regridded_ssh.png")
```

## Map Function Reference

| Function | When to use | Notes |
|---|---|---|
| `climplot.map_figure()` | Always — creates figure + GeoAxes | Default: Robinson, central_longitude=180 |
| `climplot.plot_ocean_field()` | Native model grids | Bundles background + mask + plot |
| `climplot.set_land_background()` | Manual native-grid workflow | Sets ax facecolor so NaN → gray |
| `climplot.mask_land()` | Manual native-grid workflow | Sets land points to NaN using wet_mask |
| `climplot.add_land_feature()` | Regular/regridded grids | Draws Natural Earth filled continents |
| `climplot.add_coastlines()` | Regular/regridded grids | Draws Natural Earth coastline outlines |
| `climplot.add_land_overlay()` | Legacy — center-coord pcolormesh only | Paints gray over land using wet_mask with pcolormesh |

## Common Mistakes

1. **Using `add_coastlines()` on native grids** — coastlines won't align with model land mask. Use `plot_ocean_field()` instead.
2. **Passing center coords to pcolormesh** — pcolormesh expects corner coordinates (`geolon_c`/`geolat_c`). Center coords cause a half-cell shift.
3. **Forgetting `transform=ccrs.PlateCarree()`** — data in lon/lat coordinates needs this transform. `plot_ocean_field` sets it automatically.
4. **Using `add_land_feature()` on native grids** — Natural Earth polygons won't match the model's coastline. Gray background + NaN masking is the correct approach.
5. **Using `add_land_overlay()` with corner-coord pcolormesh** — `add_land_overlay` uses center coordinates internally, so shapes won't match. Use `plot_ocean_field()` instead.

## Package Conventions

- **Public API**: All functions are exported from `climplot` directly (e.g., `climplot.add_land_feature()`, not `from climplot.maps import add_land_feature`).
- **wet_mask convention**: 1 = ocean, 0 = land.
- **Default land color**: `#808080` (medium gray).
- **Default projection**: Robinson, centered on 180° (Pacific-centered).
- **Colormap intervals**: Use round numbers ending in 0, 1, 2, or 5.
