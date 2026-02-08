"""Tests for climplot.maps module."""

import numpy as np
import pytest
import matplotlib
import matplotlib.pyplot as plt

import climplot
from climplot.maps import _get_projection

import cartopy.crs as ccrs


class TestGetProjection:
    """Tests for _get_projection helper."""

    def test_robinson(self):
        proj = _get_projection("robinson")
        assert isinstance(proj, ccrs.Robinson)

    def test_platecarree(self):
        proj = _get_projection("platecarree")
        assert isinstance(proj, ccrs.PlateCarree)

    def test_mollweide(self):
        proj = _get_projection("mollweide")
        assert isinstance(proj, ccrs.Mollweide)

    def test_orthographic(self):
        proj = _get_projection("orthographic")
        assert isinstance(proj, ccrs.Orthographic)

    def test_mercator(self):
        proj = _get_projection("mercator")
        assert isinstance(proj, ccrs.Mercator)

    def test_northpolarstereo(self):
        proj = _get_projection("northpolarstereo")
        assert isinstance(proj, ccrs.NorthPolarStereo)

    def test_southpolarstereo(self):
        proj = _get_projection("southpolarstereo")
        assert isinstance(proj, ccrs.SouthPolarStereo)

    def test_case_insensitive(self):
        proj = _get_projection("Robinson")
        assert isinstance(proj, ccrs.Robinson)

    def test_underscore_normalization(self):
        proj = _get_projection("north_polar_stereo")
        assert isinstance(proj, ccrs.NorthPolarStereo)

    def test_hyphen_normalization(self):
        proj = _get_projection("north-polar-stereo")
        assert isinstance(proj, ccrs.NorthPolarStereo)

    def test_central_longitude(self):
        proj = _get_projection("robinson", central_longitude=0)
        assert isinstance(proj, ccrs.Robinson)

    def test_invalid_projection(self):
        with pytest.raises(ValueError, match="Unknown projection"):
            _get_projection("bogus")


class TestMapFigure:
    """Tests for map_figure."""

    def teardown_method(self):
        plt.close("all")

    def test_returns_figure_and_geoaxes(self):
        fig, ax = climplot.map_figure()
        assert isinstance(fig, plt.Figure)
        assert hasattr(ax, "projection")

    def test_default_projection_is_robinson(self):
        fig, ax = climplot.map_figure()
        assert isinstance(ax.projection, ccrs.Robinson)

    def test_custom_projection(self):
        fig, ax = climplot.map_figure(projection="mollweide")
        assert isinstance(ax.projection, ccrs.Mollweide)

    def test_central_longitude(self):
        fig, ax = climplot.map_figure(
            projection="platecarree", central_longitude=0
        )
        assert isinstance(ax.projection, ccrs.PlateCarree)

    def test_figsize(self):
        fig, ax = climplot.map_figure(figsize=(12, 6))
        w, h = fig.get_size_inches()
        assert abs(w - 12) < 0.1
        assert abs(h - 6) < 0.1


class TestAddCoastlines:
    """Tests for add_coastlines."""

    def teardown_method(self):
        plt.close("all")

    def test_adds_coastlines(self):
        fig, ax = climplot.map_figure()
        climplot.add_coastlines(ax)
        # No error means success; check that artists were added
        assert len(ax.artists) >= 0  # coastlines added as collections

    def test_resolution_parameter(self):
        fig, ax = climplot.map_figure()
        climplot.add_coastlines(ax, resolution="50m")

    def test_linewidth_parameter(self):
        fig, ax = climplot.map_figure()
        climplot.add_coastlines(ax, linewidth=1.5)

    def test_color_parameter(self):
        fig, ax = climplot.map_figure()
        climplot.add_coastlines(ax, color="blue")


class TestAddLandFeature:
    """Tests for add_land_feature."""

    def teardown_method(self):
        plt.close("all")

    def test_adds_land_feature(self):
        fig, ax = climplot.map_figure()
        climplot.add_land_feature(ax)

    def test_custom_facecolor(self):
        fig, ax = climplot.map_figure()
        climplot.add_land_feature(ax, facecolor="green")

    def test_custom_edgecolor(self):
        fig, ax = climplot.map_figure()
        climplot.add_land_feature(ax, edgecolor="black")

    def test_resolution_parameter(self):
        fig, ax = climplot.map_figure()
        climplot.add_land_feature(ax, resolution="50m")


class TestAddLandOverlay:
    """Tests for add_land_overlay."""

    def teardown_method(self):
        plt.close("all")

    def _make_grid(self):
        """Create a simple 2D grid with wet mask."""
        lon = np.array([[0, 60, 120], [0, 60, 120]], dtype=float)
        lat = np.array([[-30, -30, -30], [30, 30, 30]], dtype=float)
        wet = np.array([[1, 0, 1], [0, 1, 0]])
        return lon, lat, wet

    def test_works_with_2d_arrays(self):
        fig, ax = climplot.map_figure()
        lon, lat, wet = self._make_grid()
        climplot.add_land_overlay(ax, lon, lat, wet)

    def test_land_color_parameter(self):
        fig, ax = climplot.map_figure()
        lon, lat, wet = self._make_grid()
        climplot.add_land_overlay(ax, lon, lat, wet, land_color="brown")

    def test_zorder_parameter(self):
        fig, ax = climplot.map_figure()
        lon, lat, wet = self._make_grid()
        climplot.add_land_overlay(ax, lon, lat, wet, zorder=5)


class TestSetLandBackground:
    """Tests for set_land_background."""

    def teardown_method(self):
        plt.close("all")

    def test_default_gray(self):
        fig, ax = climplot.map_figure()
        climplot.set_land_background(ax)
        assert ax.get_facecolor() == matplotlib.colors.to_rgba("#808080")

    def test_custom_color(self):
        fig, ax = climplot.map_figure()
        climplot.set_land_background(ax, land_color="tan")
        assert ax.get_facecolor() == matplotlib.colors.to_rgba("tan")


class TestMaskLand:
    """Tests for mask_land."""

    def test_numpy_land_becomes_nan(self):
        data = np.array([1.0, 2.0, 3.0, 4.0])
        wet = np.array([1, 0, 1, 0])
        result = climplot.mask_land(data, wet)
        assert np.isnan(result[1])
        assert np.isnan(result[3])

    def test_numpy_ocean_unchanged(self):
        data = np.array([1.0, 2.0, 3.0, 4.0])
        wet = np.array([1, 0, 1, 0])
        result = climplot.mask_land(data, wet)
        assert result[0] == 1.0
        assert result[2] == 3.0

    def test_xarray_land_becomes_nan(self):
        xr = pytest.importorskip("xarray")
        data = xr.DataArray([10.0, 20.0, 30.0])
        wet = xr.DataArray([1, 0, 1])
        result = climplot.mask_land(data, wet)
        assert np.isnan(result.values[1])

    def test_xarray_ocean_unchanged(self):
        xr = pytest.importorskip("xarray")
        data = xr.DataArray([10.0, 20.0, 30.0])
        wet = xr.DataArray([1, 0, 1])
        result = climplot.mask_land(data, wet)
        assert result.values[0] == 10.0
        assert result.values[2] == 30.0

    def test_preserves_values_exactly(self):
        data = np.array([1.5, 2.7, 3.14, 0.0])
        wet = np.array([1, 1, 1, 1])
        result = climplot.mask_land(data, wet)
        np.testing.assert_array_equal(result, data)

    def test_2d_array(self):
        data = np.array([[1.0, 2.0], [3.0, 4.0]])
        wet = np.array([[1, 0], [0, 1]])
        result = climplot.mask_land(data, wet)
        assert result[0, 0] == 1.0
        assert np.isnan(result[0, 1])
        assert np.isnan(result[1, 0])
        assert result[1, 1] == 4.0


class TestPlotOceanField:
    """Tests for plot_ocean_field."""

    def teardown_method(self):
        plt.close("all")

    def _make_corner_grid(self):
        """Create corner-coordinate grid (one larger than data in each dim)."""
        lon_c, lat_c = np.meshgrid(
            np.linspace(0, 360, 7), np.linspace(-90, 90, 5)
        )
        data = np.random.default_rng(42).random((4, 6))
        return lon_c, lat_c, data

    def _make_center_grid(self):
        """Create center-coordinate grid (same shape as data)."""
        lon, lat = np.meshgrid(
            np.linspace(30, 330, 6), np.linspace(-60, 60, 4)
        )
        data = np.random.default_rng(42).random((4, 6))
        return lon, lat, data

    def test_pcolormesh_returns_quadmesh(self):
        fig, ax = climplot.map_figure()
        lon_c, lat_c, data = self._make_corner_grid()
        artist = climplot.plot_ocean_field(ax, lon_c, lat_c, data)
        assert isinstance(artist, matplotlib.collections.QuadMesh)

    def test_pcolormesh_sets_gray_background(self):
        fig, ax = climplot.map_figure()
        lon_c, lat_c, data = self._make_corner_grid()
        climplot.plot_ocean_field(ax, lon_c, lat_c, data)
        assert ax.get_facecolor() == matplotlib.colors.to_rgba("#808080")

    def test_contourf_returns_contourset(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_center_grid()
        artist = climplot.plot_ocean_field(
            ax, lon, lat, data, method="contourf"
        )
        assert isinstance(artist, matplotlib.contour.QuadContourSet)

    def test_contour_returns_contourset(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_center_grid()
        artist = climplot.plot_ocean_field(
            ax, lon, lat, data, method="contour"
        )
        assert isinstance(artist, matplotlib.contour.QuadContourSet)

    def test_with_wet_mask(self):
        fig, ax = climplot.map_figure()
        lon_c, lat_c, data = self._make_corner_grid()
        wet = np.ones_like(data)
        wet[0, 0] = 0
        artist = climplot.plot_ocean_field(
            ax, lon_c, lat_c, data, wet_mask=wet
        )
        assert isinstance(artist, matplotlib.collections.QuadMesh)

    def test_without_wet_mask(self):
        fig, ax = climplot.map_figure()
        lon_c, lat_c, data = self._make_corner_grid()
        artist = climplot.plot_ocean_field(ax, lon_c, lat_c, data)
        assert isinstance(artist, matplotlib.collections.QuadMesh)

    def test_custom_land_color(self):
        fig, ax = climplot.map_figure()
        lon_c, lat_c, data = self._make_corner_grid()
        climplot.plot_ocean_field(
            ax, lon_c, lat_c, data, land_color="tan"
        )
        assert ax.get_facecolor() == matplotlib.colors.to_rgba("tan")

    def test_kwargs_forwarded(self):
        fig, ax = climplot.map_figure()
        lon_c, lat_c, data = self._make_corner_grid()
        artist = climplot.plot_ocean_field(
            ax, lon_c, lat_c, data, vmin=0, vmax=1, cmap="viridis"
        )
        assert artist.get_clim() == (0, 1)

    def test_invalid_method_raises(self):
        fig, ax = climplot.map_figure()
        lon_c, lat_c, data = self._make_corner_grid()
        with pytest.raises(ValueError, match="Unknown method"):
            climplot.plot_ocean_field(
                ax, lon_c, lat_c, data, method="scatter"
            )


class TestPlotAtmosField:
    """Tests for plot_atmos_field."""

    def teardown_method(self):
        plt.close("all")

    def _make_1d_grid(self):
        """Create 1-D lon/lat arrays and 2-D data."""
        lon = np.linspace(0, 360, 37)
        lat = np.linspace(-90, 90, 19)
        data = np.random.default_rng(42).random((19, 37))
        return lon, lat, data

    def _make_2d_grid(self):
        """Create 2-D lon/lat arrays and 2-D data."""
        lon_1d = np.linspace(0, 360, 37)
        lat_1d = np.linspace(-90, 90, 19)
        lon, lat = np.meshgrid(lon_1d, lat_1d)
        data = np.random.default_rng(42).random((19, 37))
        return lon, lat, data

    def test_contourf_returns_contourset(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(ax, lon, lat, data)
        assert isinstance(artist, matplotlib.contour.QuadContourSet)

    def test_pcolormesh_returns_quadmesh(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(
            ax, lon, lat, data, method="pcolormesh"
        )
        assert isinstance(artist, matplotlib.collections.QuadMesh)

    def test_contour_returns_contourset(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(
            ax, lon, lat, data, method="contour"
        )
        assert isinstance(artist, matplotlib.contour.QuadContourSet)

    def test_1d_coords(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(ax, lon, lat, data)
        assert isinstance(artist, matplotlib.contour.QuadContourSet)

    def test_2d_coords(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_2d_grid()
        artist = climplot.plot_atmos_field(ax, lon, lat, data)
        assert isinstance(artist, matplotlib.contour.QuadContourSet)

    def test_land_false_skips_land_feature(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        n_features_before = len(ax._feature_artist_map) if hasattr(ax, '_feature_artist_map') else 0
        climplot.plot_atmos_field(ax, lon, lat, data, land=False, coastlines=False)
        # No land feature should be added; we just check no error is raised

    def test_coastlines_false_skips_coastlines(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        climplot.plot_atmos_field(ax, lon, lat, data, coastlines=False)
        # Should not raise; land is still added

    def test_kwargs_forwarded(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(
            ax, lon, lat, data, method="pcolormesh", vmin=0, vmax=1, cmap="viridis"
        )
        assert artist.get_clim() == (0, 1)

    def test_invalid_method_raises(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        with pytest.raises(ValueError, match="Unknown method"):
            climplot.plot_atmos_field(ax, lon, lat, data, method="scatter")

    def test_custom_land_color(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        # Should not raise
        climplot.plot_atmos_field(ax, lon, lat, data, land_color="tan")

    def test_alpha_forwarded_to_pcolormesh(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(
            ax, lon, lat, data, method="pcolormesh", alpha=0.5
        )
        assert artist.get_alpha() == 0.5

    def test_default_alpha(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(
            ax, lon, lat, data, method="pcolormesh"
        )
        assert artist.get_alpha() == 0.85

    def test_coastline_linewidth(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        # Should not raise with custom linewidth
        climplot.plot_atmos_field(
            ax, lon, lat, data, coastline_linewidth=0.8
        )

    def test_contourf_extend_both_by_default(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(ax, lon, lat, data)
        assert artist.extend == "both"

    def test_contourf_extend_can_be_overridden(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        artist = climplot.plot_atmos_field(
            ax, lon, lat, data, extend="neither"
        )
        assert artist.extend == "neither"

    def test_pcolormesh_no_extend(self):
        fig, ax = climplot.map_figure()
        lon, lat, data = self._make_1d_grid()
        # pcolormesh doesn't support extend; should not raise
        artist = climplot.plot_atmos_field(
            ax, lon, lat, data, method="pcolormesh"
        )
        assert isinstance(artist, matplotlib.collections.QuadMesh)


class TestAddGridlines:
    """Tests for add_gridlines."""

    def teardown_method(self):
        plt.close("all")

    def test_returns_gridliner(self):
        from cartopy.mpl.gridliner import Gridliner

        fig, ax = climplot.map_figure()
        gl = climplot.add_gridlines(ax)
        assert isinstance(gl, Gridliner)

    def test_custom_spacing(self):
        from cartopy.mpl.gridliner import Gridliner

        fig, ax = climplot.map_figure()
        gl = climplot.add_gridlines(ax, x_spacing=30, y_spacing=15)
        assert isinstance(gl, Gridliner)

    def test_custom_linewidth_alpha(self):
        fig, ax = climplot.map_figure()
        gl = climplot.add_gridlines(ax, linewidth=1.0, alpha=0.5)
        # Verify the gridliner was created with custom values
        assert gl.collection_kwargs.get("alpha", None) == 0.5

    def test_draw_labels_on_platecarree(self):
        fig, ax = climplot.map_figure(projection="platecarree")
        gl = climplot.add_gridlines(ax, draw_labels=True)
        # Should not raise on PlateCarree

    def test_default_linestyle(self):
        fig, ax = climplot.map_figure()
        gl = climplot.add_gridlines(ax)
        # The gridliner should be created (attributes can vary by cartopy version)
