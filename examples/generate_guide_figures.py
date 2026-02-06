#!/usr/bin/env python
"""Generate all figures for the climplot Plotting Style Guide.

This script creates the example figures embedded in docs/plotting-guide.md.
All data is synthetic (numpy-generated), so no external datasets are needed.

Usage
-----
    conda activate py312
    python examples/generate_guide_figures.py

Figures are saved to docs/images/ at 150 DPI for reasonable file sizes.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import cartopy.crs as ccrs
import climplot
from climplot.maps import add_land_feature

# ---------------------------------------------------------------------------
# Output configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = "docs/images"
SCREEN_DPI = 150


def _savefig(fig, name):
    """Save figure and close."""
    path = f"{OUTPUT_DIR}/{name}"
    fig.savefig(path, dpi=SCREEN_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  saved {path}")


# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------

def make_synthetic_2d_field(amplitude=0.3, wavelength=2.0, seed=42):
    """Create a fake anomaly field on a global lat/lon grid.

    Returns lon (360,), lat (180,), data (180, 360).
    """
    rng = np.random.default_rng(seed)
    lon = np.arange(0.5, 360.5, 1.0)
    lat = np.arange(-89.5, 90.5, 1.0)
    LON, LAT = np.meshgrid(lon, lat)

    # Large-scale wave pattern
    data = amplitude * np.sin(np.radians(LAT) * wavelength) * np.cos(
        np.radians(LON) * wavelength
    )
    # Add some noise
    data += rng.normal(0, amplitude * 0.15, data.shape)
    return lon, lat, data


def make_synthetic_timeseries(n_years=50, seed=42):
    """Create synthetic annual time series (obs + 2 models).

    Returns years, obs, model1, model2.
    """
    rng = np.random.default_rng(seed)
    years = np.arange(1970, 1970 + n_years)

    # Observations: trend + variability
    trend = 0.003 * (years - 1970)
    obs = trend + 0.01 * np.sin(2 * np.pi * years / 10) + rng.normal(0, 0.005, n_years)

    # Models: similar trend, different variability
    model1 = trend * 1.1 + rng.normal(0, 0.008, n_years)
    model2 = trend * 0.9 + 0.015 * np.sin(2 * np.pi * years / 8) + rng.normal(
        0, 0.006, n_years
    )
    return years, obs, model1, model2


# ===========================================================================
# Figure generators
# ===========================================================================


def fig_dimensions():
    """Side-by-side comparison of single-column vs two-column figure sizes."""
    climplot.reset_style()
    climplot.publication()

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5))

    # Single-column mock
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.5, '3.5" wide\n(single-column)',
            ha="center", va="center", fontsize=11, color="#333333")
    ax.set_title("Publication Mode", fontsize=10)
    # Draw a box showing the 3.5" proportion
    rect = plt.Rectangle((0.05, 0.15), 0.9, 0.65, linewidth=1.5,
                          edgecolor="#1f77b4", facecolor="#1f77b4", alpha=0.12)
    ax.add_patch(rect)
    ax.set_xticks([])
    ax.set_yticks([])

    # Two-column mock
    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.5, '7.0" wide\n(two-column / presentation)',
            ha="center", va="center", fontsize=11, color="#333333")
    ax.set_title("Presentation Mode", fontsize=10)
    rect = plt.Rectangle((0.05, 0.15), 0.9, 0.65, linewidth=1.5,
                          edgecolor="#ff7f0e", facecolor="#ff7f0e", alpha=0.12)
    ax.add_patch(rect)
    ax.set_xticks([])
    ax.set_yticks([])

    fig.suptitle("Standard Figure Widths", fontsize=11, fontweight="bold", y=1.02)
    _savefig(fig, "dimensions.png")


def fig_style_comparison():
    """Publication vs presentation typography side-by-side."""
    x = np.linspace(0, 4 * np.pi, 200)

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    # -- Publication style (left) --
    climplot.reset_style()
    climplot.publication()
    ax = axes[0]
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)")
    ax.set_xlabel("x-axis (radians)", fontsize=10)
    ax.set_ylabel("Amplitude", fontsize=10)
    ax.set_title("Publication Mode", fontsize=11)
    ax.legend(fontsize=8)
    ax.tick_params(labelsize=8)
    ax.grid(True, alpha=0.3, linewidth=0.3)

    # -- Presentation style (right) --
    ax = axes[1]
    ax.plot(x, np.sin(x), linewidth=2.5, label="sin(x)")
    ax.plot(x, np.cos(x), linewidth=2.5, label="cos(x)")
    ax.set_xlabel("x-axis (radians)", fontsize=14)
    ax.set_ylabel("Amplitude", fontsize=14)
    ax.set_title("Presentation Mode", fontsize=16)
    ax.legend(fontsize=12)
    ax.tick_params(labelsize=14)
    ax.grid(True, alpha=0.3, linewidth=0.5)

    fig.tight_layout()
    _savefig(fig, "style_comparison.png")


def fig_anomaly_cmap():
    """Diverging anomaly colormap on a global map."""
    climplot.reset_style()
    climplot.publication()

    lon, lat, data = make_synthetic_2d_field(amplitude=0.3)
    cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)

    fig, ax = climplot.map_figure(figsize=(7.0, 4.0))
    cs = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm,
                       transform=ccrs.PlateCarree())
    add_land_feature(ax)
    cbar = climplot.add_colorbar(cs, ax, "Anomaly (units)")
    ax.set_title("Diverging Anomaly Colormap (RdBu_r)", fontsize=11)
    _savefig(fig, "anomaly_cmap.png")


def fig_center_on_white():
    """Standard vs center-on-white diverging colormaps."""
    climplot.reset_style()
    climplot.publication()

    lon, lat, data = make_synthetic_2d_field(amplitude=0.3)

    fig = plt.figure(figsize=(7.0, 5.0))

    # Standard
    ax1 = fig.add_subplot(2, 1, 1, projection=ccrs.Robinson(central_longitude=180))
    cmap1, norm1, _ = climplot.anomaly_cmap(-0.3, 0.3, 0.05)
    cs1 = ax1.pcolormesh(lon, lat, data, cmap=cmap1, norm=norm1,
                         transform=ccrs.PlateCarree())
    add_land_feature(ax1)
    climplot.add_colorbar(cs1, ax1, "Standard (units)")
    ax1.set_title("Standard Diverging", fontsize=10)

    # Center-on-white
    ax2 = fig.add_subplot(2, 1, 2, projection=ccrs.Robinson(central_longitude=180))
    cmap2, norm2, _ = climplot.anomaly_cmap(-0.3, 0.3, 0.05, center_on_white=True)
    cs2 = ax2.pcolormesh(lon, lat, data, cmap=cmap2, norm=norm2,
                         transform=ccrs.PlateCarree())
    add_land_feature(ax2)
    climplot.add_colorbar(cs2, ax2, "Center-on-White (units)")
    ax2.set_title("Center-on-White (for difference plots)", fontsize=10)

    fig.tight_layout(h_pad=2.5)
    _savefig(fig, "center_on_white.png")


def fig_good_vs_bad_intervals():
    """Round vs awkward contour-level intervals."""
    climplot.reset_style()
    climplot.publication()

    lon, lat, data = make_synthetic_2d_field(amplitude=0.3)

    fig = plt.figure(figsize=(7.0, 5.0))

    # Bad: awkward intervals
    ax1 = fig.add_subplot(2, 1, 1, projection=ccrs.Robinson(central_longitude=180))
    bad_levels = np.arange(-0.3, 0.31, 0.07)  # 0.07 is awkward
    bad_cmap = plt.get_cmap("RdBu_r")
    bad_norm = mcolors.BoundaryNorm(bad_levels, bad_cmap.N, extend="both")
    cs1 = ax1.pcolormesh(lon, lat, data, cmap=bad_cmap, norm=bad_norm,
                         transform=ccrs.PlateCarree())
    add_land_feature(ax1)
    cbar1 = climplot.add_colorbar(cs1, ax1, "Awkward intervals (0.07)", max_ticks=5)
    ax1.set_title("Avoid: awkward intervals (0.07)", fontsize=10,
                  color="#d62728")

    # Good: round intervals
    ax2 = fig.add_subplot(2, 1, 2, projection=ccrs.Robinson(central_longitude=180))
    cmap2, norm2, _ = climplot.anomaly_cmap(-0.3, 0.3, 0.05)
    cs2 = ax2.pcolormesh(lon, lat, data, cmap=cmap2, norm=norm2,
                         transform=ccrs.PlateCarree())
    add_land_feature(ax2)
    climplot.add_colorbar(cs2, ax2, "Round intervals (0.05)")
    ax2.set_title("Prefer: round intervals (0.05)", fontsize=10,
                  color="#2ca02c")

    fig.tight_layout(h_pad=2.5)
    _savefig(fig, "good_vs_bad_intervals.png")


def fig_map_example():
    """Robinson map with land feature and colorbar."""
    climplot.reset_style()
    climplot.publication()

    lon, lat, data = make_synthetic_2d_field(amplitude=0.5, wavelength=3.0)
    cmap, norm, levels = climplot.anomaly_cmap(-0.5, 0.5, 0.1)

    fig, ax = climplot.map_figure(figsize=(7.0, 4.0))
    cs = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm,
                       transform=ccrs.PlateCarree())
    add_land_feature(ax)
    climplot.add_colorbar(cs, ax, "Sea Surface Height Anomaly (m)")
    ax.set_title("Robinson Projection, Pacific-Centered", fontsize=11)
    _savefig(fig, "map_example.png")


def fig_timeseries():
    """Time series with grid, labels, and legend."""
    climplot.reset_style()
    climplot.publication()

    years, obs, model1, model2 = make_synthetic_timeseries()

    fig, ax = climplot.timeseries_figure(figsize=(7.0, 3.5))
    ax.plot(years, obs, color="#000000", linestyle="--", linewidth=1.5,
            label="Observations")
    ax.plot(years, model1, color="#1f77b4", linewidth=1.5, label="Model 1")
    ax.plot(years, model2, color="#ff7f0e", linewidth=1.5, label="Model 2")
    ax.set_xlabel("Year")
    ax.set_ylabel("Global Mean Sea Level (m)")
    ax.set_title("Time Series Example")
    ax.legend(loc="upper left", framealpha=0.9)
    _savefig(fig, "timeseries_example.png")


def fig_multipanel():
    """2x2 panel figure with labels and shared colorbar."""
    climplot.reset_style()
    climplot.publication()

    lon, lat, _ = make_synthetic_2d_field()
    cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.05)

    fig, axes = climplot.panel_figure(
        2, 2, projection=ccrs.Robinson(central_longitude=180)
    )

    titles = ["DJF", "MAM", "JJA", "SON"]
    seeds = [42, 43, 44, 45]
    cs = None
    for ax, title, seed in zip(axes.flat, titles, seeds):
        _, _, data = make_synthetic_2d_field(amplitude=0.3, seed=seed)
        cs = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm,
                           transform=ccrs.PlateCarree())
        add_land_feature(ax)
        ax.set_title(title, fontsize=10)

    climplot.add_panel_labels(axes.flatten())
    climplot.bottom_colorbar(cs, fig, axes, "Anomaly (units)")
    _savefig(fig, "multipanel_example.png")


def fig_pitfall_jet_vs_rdbu():
    """Side-by-side comparison: jet (bad) vs RdBu_r (good)."""
    climplot.reset_style()
    climplot.publication()

    lon, lat, data = make_synthetic_2d_field(amplitude=0.3)

    fig = plt.figure(figsize=(7.0, 5.0))

    # Bad: jet colormap, continuous
    ax1 = fig.add_subplot(2, 1, 1, projection=ccrs.Robinson(central_longitude=180))
    cs1 = ax1.pcolormesh(lon, lat, data, cmap="jet", vmin=-0.3, vmax=0.3,
                         transform=ccrs.PlateCarree())
    add_land_feature(ax1)
    cbar1 = climplot.add_colorbar(cs1, ax1, "Continuous jet (avoid!)")
    ax1.set_title("Avoid: jet + continuous colormap", fontsize=10,
                  color="#d62728")

    # Good: RdBu_r, discrete levels
    ax2 = fig.add_subplot(2, 1, 2, projection=ccrs.Robinson(central_longitude=180))
    cmap2, norm2, _ = climplot.anomaly_cmap(-0.3, 0.3, 0.05)
    cs2 = ax2.pcolormesh(lon, lat, data, cmap=cmap2, norm=norm2,
                         transform=ccrs.PlateCarree())
    add_land_feature(ax2)
    climplot.add_colorbar(cs2, ax2, "Discrete RdBu_r (preferred)")
    ax2.set_title("Prefer: RdBu_r + discrete levels", fontsize=10,
                  color="#2ca02c")

    fig.tight_layout(h_pad=2.5)
    _savefig(fig, "pitfall_jet_vs_rdbu.png")


# ===========================================================================
# Main
# ===========================================================================

def main():
    from pathlib import Path
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    generators = [
        ("dimensions", fig_dimensions),
        ("style_comparison", fig_style_comparison),
        ("anomaly_cmap", fig_anomaly_cmap),
        ("center_on_white", fig_center_on_white),
        ("good_vs_bad_intervals", fig_good_vs_bad_intervals),
        ("map_example", fig_map_example),
        ("timeseries", fig_timeseries),
        ("multipanel", fig_multipanel),
        ("pitfall_jet_vs_rdbu", fig_pitfall_jet_vs_rdbu),
    ]

    print(f"Generating {len(generators)} figures for the plotting guide...\n")
    for name, func in generators:
        print(f"[{name}]")
        func()

    # Reset style when done
    climplot.reset_style()
    print(f"\nDone. All figures saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
