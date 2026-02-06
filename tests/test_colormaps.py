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
