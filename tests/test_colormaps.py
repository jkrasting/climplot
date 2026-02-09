"""Tests for climplot.colormaps module."""

import pytest
import numpy as np
import matplotlib.colors as mcolors

import climplot


class TestColormaps:
    """Tests for colormap functions."""

    def test_anomaly_cmap_returns_tuple(self):
        """Test that anomaly_cmap returns cmap, norm, levels."""
        result = climplot.anomaly_cmap(-1, 1, 0.2)
        assert len(result) == 3
        cmap, norm, levels = result
        assert isinstance(norm, mcolors.BoundaryNorm)
        assert isinstance(levels, np.ndarray)

    def test_anomaly_cmap_levels(self):
        """Test that levels are correctly generated."""
        cmap, norm, levels = climplot.anomaly_cmap(-0.3, 0.3, 0.1)
        expected = np.array([-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3])
        np.testing.assert_array_almost_equal(levels, expected, decimal=10)

    def test_anomaly_cmap_symmetric(self):
        """Test that levels are symmetric around zero."""
        cmap, norm, levels = climplot.anomaly_cmap(-0.5, 0.5, 0.1)
        np.testing.assert_almost_equal(levels[0], -levels[-1], decimal=10)
        assert np.isclose(levels, 0.0).any()

    def test_discrete_cmap_extend(self):
        """Test that extend parameter is respected."""
        cmap, norm, levels = climplot.discrete_cmap(-1, 1, 0.2, extend="both")
        # BoundaryNorm should handle extension
        assert isinstance(norm, mcolors.BoundaryNorm)

    def test_sequential_cmap(self):
        """Test sequential colormap generation."""
        cmap, norm, levels = climplot.sequential_cmap(0, 100, 10)
        assert levels[0] == 0
        assert levels[-1] == 100

    def test_categorical_cmap(self):
        """Test categorical colormap generation."""
        cmap = climplot.categorical_cmap(5)
        assert isinstance(cmap, mcolors.ListedColormap)
        assert len(cmap.colors) == 5

    def test_list_colormaps(self):
        """Test that list_colormaps returns dict."""
        cmaps = climplot.list_colormaps()
        assert isinstance(cmaps, dict)
        assert "anomaly" in cmaps
        assert "temperature" in cmaps

    def test_center_on_white(self):
        """Test center_on_white creates white band."""
        cmap, norm, levels = climplot.anomaly_cmap(
            -0.3, 0.3, 0.1, center_on_white=True
        )
        # Should have additional levels for white band
        assert -0.05 in levels or np.isclose(levels, -0.05).any()
        assert 0.05 in levels or np.isclose(levels, 0.05).any()


class TestDiscreteRounding:
    """Tests for float noise removal in level generation."""

    def test_no_float_noise_standard(self):
        """Levels should be exact multiples of the interval."""
        _, _, levels = climplot.discrete_cmap(-0.3, 0.3, 0.1)
        expected = np.array([-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3])
        np.testing.assert_array_equal(levels, expected)

    def test_no_float_noise_small_interval(self):
        """Small intervals should not accumulate arange drift."""
        _, _, levels = climplot.discrete_cmap(-0.15, 0.15, 0.05)
        expected = np.array([-0.15, -0.1, -0.05, 0.0, 0.05, 0.1, 0.15])
        np.testing.assert_array_equal(levels, expected)

    def test_integer_levels(self):
        """Integer intervals stay as exact integers."""
        _, _, levels = climplot.discrete_cmap(-2, 2, 1)
        expected = np.array([-2, -1, 0, 1, 2], dtype=float)
        np.testing.assert_array_equal(levels, expected)


class TestCenterOnWhite:
    """Tests for the center_on_white colormap construction."""

    def test_white_band_visible(self):
        """The center interval should be pure white."""
        cmap, norm, levels = climplot.discrete_cmap(
            -0.3, 0.3, 0.1, center_on_white=True
        )
        # Find the interval spanning zero
        for i in range(len(levels) - 1):
            if levels[i] < 0 < levels[i + 1]:
                color = cmap(norm((levels[i] + levels[i + 1]) / 2))
                assert color[:3] == (1.0, 1.0, 1.0), "Center interval should be white"
                break

    def test_no_duplicate_boundaries(self):
        """Boundaries should have no duplicate values."""
        _, _, levels = climplot.discrete_cmap(
            -0.5, 0.5, 0.1, center_on_white=True
        )
        assert len(levels) == len(np.unique(levels))

    def test_listed_colormap_type(self):
        """center_on_white should produce a ListedColormap."""
        cmap, _, _ = climplot.discrete_cmap(
            -0.3, 0.3, 0.1, center_on_white=True
        )
        assert isinstance(cmap, mcolors.ListedColormap)

    def test_n_colors_matches_intervals(self):
        """Number of colors should cover intervals plus extend arrows."""
        cmap, _, levels = climplot.discrete_cmap(
            -0.3, 0.3, 0.1, center_on_white=True
        )
        n_intervals = len(levels) - 1
        # extend="both" adds 2 extra colors (one per arrow)
        assert len(cmap.colors) == n_intervals + 2

    def test_n_colors_no_extend(self):
        """Without extend, colors should equal intervals exactly."""
        cmap, _, levels = climplot.discrete_cmap(
            -0.3, 0.3, 0.1, center_on_white=True, extend="neither"
        )
        assert len(cmap.colors) == len(levels) - 1


class TestAutoLevels:
    """Tests for auto_levels() nice-number selection."""

    def test_returns_tuple(self):
        result = climplot.auto_levels(0, 10)
        assert len(result) == 2
        interval, levels = result
        assert isinstance(interval, float)
        assert isinstance(levels, np.ndarray)

    def test_interval_ends_in_1_2_5(self):
        """The significant digit of the interval should be 1, 2, or 5."""
        for vmin, vmax in [(-2.3, 2.7), (0, 100), (990, 1030), (0, 0.07)]:
            interval, _ = climplot.auto_levels(vmin, vmax)
            # Normalize to extract leading significant digit
            sig = interval / 10 ** np.floor(np.log10(interval))
            assert sig in (1.0, 2.0, 5.0, 10.0), f"interval={interval}, sig={sig}"

    def test_levels_span_data(self):
        interval, levels = climplot.auto_levels(-2.3, 2.7)
        assert levels[0] <= -2.3
        assert levels[-1] >= 2.7

    def test_approximately_n_levels(self):
        interval, levels = climplot.auto_levels(0, 100, n_levels=10)
        n_intervals = len(levels) - 1
        assert 5 <= n_intervals <= 20

    def test_raises_on_equal_range(self):
        with pytest.raises(ValueError):
            climplot.auto_levels(5, 5)

    def test_no_float_artifacts(self):
        interval, levels = climplot.auto_levels(0, 1, n_levels=5)
        for lev in levels:
            # Check that string representation has no excessive digits
            s = f"{lev:.10g}"
            assert len(s) < 10, f"Level {lev} has too many digits: {s}"


class TestLogCmap:
    """Tests for log_cmap()."""

    def test_returns_tuple(self):
        result = climplot.log_cmap(0.01, 100)
        assert len(result) == 3
        cmap, norm, levels = result
        assert isinstance(norm, mcolors.BoundaryNorm)
        assert isinstance(levels, np.ndarray)

    def test_per_decade_1(self):
        _, _, levels = climplot.log_cmap(0.01, 100, per_decade=1)
        expected = np.array([0.01, 0.1, 1, 10, 100])
        np.testing.assert_array_almost_equal(levels, expected)

    def test_per_decade_3(self):
        _, _, levels = climplot.log_cmap(0.01, 100, per_decade=3)
        # Should include 1-2-5 subsequence
        assert 0.01 in levels
        assert 0.02 in levels
        assert 0.05 in levels

    def test_raises_on_negative_vmin(self):
        with pytest.raises(ValueError):
            climplot.log_cmap(-1, 100)

    def test_raises_on_zero_vmin(self):
        with pytest.raises(ValueError):
            climplot.log_cmap(0, 100)
