"""Visual demo of native-grid plotting functions.

Creates a 4-panel figure showing plot_ocean_field on tripolar and
lat-lon grids plus a traditional Cartopy-based panel for comparison.
"""

import numpy as np
import cartopy.crs as ccrs
import momgrid

import climplot

# ---------- style ----------------------------------------------------------
climplot.publication()

# ---------- colormap -------------------------------------------------------
cmap, norm, levels = climplot.anomaly_cmap(
    vmin=-15, vmax=15, interval=2.5, cmap_name="RdBu_r"
)

# ---------- tripolar grid (ESM4) ------------------------------------------
grd = momgrid.MOMgrid("esm4_sym")

geolon = np.asarray(grd.geolon)
geolat = np.asarray(grd.geolat)
geolon_c = np.asarray(grd.geolon_c)
geolat_c = np.asarray(grd.geolat_c)
wet = np.asarray(grd.wet)

sst_tri = 15.0 * np.cos(np.deg2rad(geolat))

# ---------- regular lat-lon grid (WOA 1°) ---------------------------------
woa = momgrid.external.woa18_grid(1.0)

lon_1d = np.asarray(woa.lon)
lat_1d = np.asarray(woa.lat)
lon_b_1d = np.asarray(woa.lon_b)
lat_b_1d = np.asarray(woa.lat_b)
mask_woa = np.asarray(woa.mask)

lon_2d, lat_2d = np.meshgrid(lon_1d, lat_1d)
lon_b_2d, lat_b_2d = np.meshgrid(lon_b_1d, lat_b_1d)

sst_ll = 15.0 * np.cos(np.deg2rad(lat_2d))

# ---------- figure ---------------------------------------------------------
fig, axes = climplot.panel_figure(
    2, 2, projection=ccrs.Robinson(central_longitude=180)
)

# (a) pcolormesh on tripolar with corner coords
cs_a = climplot.plot_ocean_field(
    axes[0, 0], geolon_c, geolat_c, sst_tri,
    wet_mask=wet, method="pcolormesh",
    cmap=cmap, norm=norm,
)
axes[0, 0].set_title("plot_ocean_field — pcolormesh (tripolar)", fontsize=7)

# (b) contourf on tripolar with center coords
cs_b = climplot.plot_ocean_field(
    axes[0, 1], geolon, geolat, sst_tri,
    wet_mask=wet, method="contourf",
    cmap=cmap, norm=norm, levels=levels,
)
axes[0, 1].set_title("plot_ocean_field — contourf (tripolar)", fontsize=7)

# (c) pcolormesh on regular lat-lon via plot_ocean_field
cs_c = climplot.plot_ocean_field(
    axes[1, 0], lon_b_2d, lat_b_2d, sst_ll,
    wet_mask=mask_woa, method="pcolormesh",
    cmap=cmap, norm=norm,
)
axes[1, 0].set_title("plot_ocean_field — pcolormesh (lat-lon 1°)", fontsize=7)

# (d) traditional workflow: pcolormesh + add_land_feature + add_coastlines
ax_d = axes[1, 1]
cs_d = ax_d.pcolormesh(
    lon_b_2d, lat_b_2d, sst_ll,
    transform=ccrs.PlateCarree(),
    cmap=cmap, norm=norm,
)
climplot.add_land_feature(ax_d, resolution="110m")
climplot.add_coastlines(ax_d, resolution="110m")
ax_d.set_title("Traditional: pcolormesh + land + coastlines", fontsize=7)

# ---------- finishing touches ----------------------------------------------
climplot.add_panel_labels(axes)
climplot.bottom_colorbar(cs_a, fig, axes, "Synthetic SST (°C)")
path = climplot.save_figure("demo_native_grid.png")
print(f"Saved to {path}")
