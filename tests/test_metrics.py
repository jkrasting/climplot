"""Tests for climplot.metrics module."""

import pytest
import numpy as np
import xarray as xr

import climplot


class TestMetrics:
    """Tests for metrics functions."""

    def setup_method(self):
        """Create test data."""
        # Create simple test data
        self.data = xr.DataArray(
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            dims=["y", "x"],
        )
        # Equal weights
        self.weights = xr.DataArray(
            np.array([[1.0, 1.0], [1.0, 1.0]]),
            dims=["y", "x"],
        )
        # Unequal weights (high latitude smaller)
        self.unequal_weights = xr.DataArray(
            np.array([[0.5, 0.5], [1.0, 1.0]]),
            dims=["y", "x"],
        )

    def test_area_weighted_mean_equal_weights(self):
        """Test area_weighted_mean with equal weights."""
        result = climplot.area_weighted_mean(self.data, self.weights)
        expected = 2.5  # (1+2+3+4)/4
        assert np.isclose(result, expected)

    def test_area_weighted_mean_unequal_weights(self):
        """Test area_weighted_mean with unequal weights."""
        result = climplot.area_weighted_mean(self.data, self.unequal_weights)
        # (1*0.5 + 2*0.5 + 3*1 + 4*1) / (0.5 + 0.5 + 1 + 1) = 8.5/3 = 2.833...
        expected = 8.5 / 3
        assert np.isclose(result, expected)

    def test_area_weighted_mean_with_nan(self):
        """Test that NaN values are excluded."""
        data_with_nan = self.data.copy()
        data_with_nan.values[0, 0] = np.nan
        result = climplot.area_weighted_mean(data_with_nan, self.weights)
        # (2+3+4)/3 = 3
        expected = 3.0
        assert np.isclose(result, expected)

    def test_area_weighted_bias(self):
        """Test area_weighted_bias calculation."""
        model = xr.DataArray([[2.0, 3.0], [4.0, 5.0]], dims=["y", "x"])
        obs = xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=["y", "x"])
        result = climplot.area_weighted_bias(model, obs, self.weights)
        expected = 1.0  # All differences are 1
        assert np.isclose(result, expected)

    def test_area_weighted_rmse(self):
        """Test area_weighted_rmse calculation."""
        model = xr.DataArray([[2.0, 3.0], [4.0, 5.0]], dims=["y", "x"])
        obs = xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=["y", "x"])
        result = climplot.area_weighted_rmse(model, obs, self.weights)
        expected = 1.0  # sqrt(mean(1^2)) = 1
        assert np.isclose(result, expected)

    def test_area_weighted_corr_perfect(self):
        """Test perfect correlation."""
        x = xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=["y", "x"])
        y = xr.DataArray([[2.0, 4.0], [6.0, 8.0]], dims=["y", "x"])  # y = 2x
        result = climplot.area_weighted_corr(x, y, self.weights)
        assert np.isclose(result, 1.0)

    def test_timeseries_bias(self):
        """Test timeseries_bias."""
        model = np.array([1.0, 2.0, 3.0, 4.0])
        obs = np.array([0.5, 1.5, 2.5, 3.5])
        result = climplot.timeseries_bias(model, obs)
        expected = 0.5
        assert np.isclose(result, expected)

    def test_timeseries_rmse(self):
        """Test timeseries_rmse."""
        model = np.array([1.0, 2.0, 3.0, 4.0])
        obs = np.array([0.0, 2.0, 3.0, 5.0])
        result = climplot.timeseries_rmse(model, obs)
        # Differences: [1, 0, 0, -1], squared: [1, 0, 0, 1], mean: 0.5
        expected = np.sqrt(0.5)
        assert np.isclose(result, expected)

    def test_timeseries_corr(self):
        """Test timeseries_corr."""
        x = np.array([1.0, 2.0, 3.0, 4.0])
        y = np.array([2.0, 4.0, 6.0, 8.0])
        result = climplot.timeseries_corr(x, y)
        assert np.isclose(result, 1.0)

    def test_metrics_summary(self):
        """Test metrics_summary returns all expected keys."""
        model = xr.DataArray([[2.0, 3.0], [4.0, 5.0]], dims=["y", "x"])
        obs = xr.DataArray([[1.0, 2.0], [3.0, 4.0]], dims=["y", "x"])
        result = climplot.metrics_summary(model, obs, self.weights)

        expected_keys = [
            "bias",
            "rmse",
            "correlation",
            "model_mean",
            "obs_mean",
            "model_std",
            "obs_std",
        ]
        for key in expected_keys:
            assert key in result
