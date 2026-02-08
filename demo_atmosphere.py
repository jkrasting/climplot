"""Visual demo of atmosphere data plotting functions.

Creates a 4-panel figure showing plot_atmos_field with different
variables and methods, plus an add_gridlines demo. Uses synthetic
data only (no external dependencies beyond climplot).
"""

import numpy as np
import cartopy.crs as ccrs

import climplot

# ---------- style ----------------------------------------------------------
climplot.publication()

# ---------- synthetic data -------------------------------------------------
lon = np.arange(0.5, 360.5, 2.0)
lat = np.arange(-89.5, 90.5, 2.0)
LON, LAT = np.meshgrid(lon, lat)

# (a) Temperature anomaly: dipole pattern
temperature = 2.0 * np.sin(np.deg2rad(LAT * 3)) * np.cos(np.deg2rad(LON * 2))

# (b) Precipitation: ITCZ-like tropical band (positive only)
precip = 8.0 * np.exp(-((LAT / 15.0) ** 2)) * (1 + 0.5 * np.cos(np.deg2rad(LON * 3)))

# (c) Sea level pressure: wavy zonal pattern
slp = 1013.0 + 15.0 * np.sin(np.deg2rad(LAT * 2)) + 5.0 * np.cos(np.deg2rad(LON))

# (d) Wind speed: jet stream pattern (positive only)
wind = 12.0 * np.exp(-(((LAT - 45) / 10.0) ** 2)) + 8.0 * np.exp(
    -(((LAT + 45) / 10.0) ** 2)
)
wind = wind * (1 + 0.3 * np.cos(np.deg2rad(LON * 4)))

# ---------- colormaps ------------------------------------------------------
cmap_t, norm_t, levels_t = climplot.anomaly_cmap(vmin=-2, vmax=2, interval=0.5)
cmap_p, norm_p, levels_p = climplot.sequential_cmap(vmin=0, vmax=12, interval=1)
cmap_s, norm_s, levels_s = climplot.sequential_cmap(vmin=990, vmax=1030, interval=5)
cmap_w, norm_w, levels_w = climplot.sequential_cmap(
    vmin=0, vmax=20, interval=2, cmap_name="inferno"
)

# ---------- figure ---------------------------------------------------------
fig, axes = climplot.panel_figure(
    2, 2, projection=ccrs.Robinson(central_longitude=180)
)

# (a) Temperature anomaly -- contourf (default)
cs_a = climplot.plot_atmos_field(
    axes[0, 0], lon, lat, temperature,
    cmap=cmap_t, norm=norm_t, levels=levels_t,
)
climplot.add_colorbar(cs_a, axes[0, 0], "Temperature Anomaly (K)")
axes[0, 0].set_title("contourf — Temperature Anomaly", fontsize=7)

# (b) Precipitation -- contourf with sequential colormap
cs_b = climplot.plot_atmos_field(
    axes[0, 1], lon, lat, precip,
    cmap=cmap_p, norm=norm_p, levels=levels_p,
)
climplot.add_colorbar(cs_b, axes[0, 1], "Precipitation (mm/day)")
axes[0, 1].set_title("contourf — Precipitation", fontsize=7)

# (c) Sea level pressure -- contourf
cs_c = climplot.plot_atmos_field(
    axes[1, 0], lon, lat, slp,
    cmap=cmap_s, norm=norm_s, levels=levels_s,
)
climplot.add_colorbar(cs_c, axes[1, 0], "SLP (hPa)")
axes[1, 0].set_title("contourf — SLP", fontsize=7)

# (d) Wind speed -- pcolormesh
cs_d = climplot.plot_atmos_field(
    axes[1, 1], lon, lat, wind,
    method="pcolormesh",
    cmap=cmap_w, norm=norm_w,
)
climplot.add_colorbar(cs_d, axes[1, 1], "Wind Speed (m/s)")
axes[1, 1].set_title("pcolormesh — Wind Speed", fontsize=7)

# Gridlines on all panels
for ax in axes.flat:
    climplot.add_gridlines(ax, x_spacing=30, y_spacing=30)

# ---------- finishing touches ----------------------------------------------
climplot.add_panel_labels(axes)
path = climplot.save_figure("demo_atmosphere.png")
print(f"Saved to {path}")
