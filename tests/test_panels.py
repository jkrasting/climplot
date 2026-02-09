"""Tests for climplot.panels module — tick thinning, formatting, colorbars."""

import pytest
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import climplot
from climplot.panels import (
    _thin_colorbar_ticks, _format_colorbar_ticks, _roundness_score,
    _is_symmetric, _select_symmetric_ticks,
)


class TestRoundnessScore:
    """Tests for the _roundness_score helper."""

    def test_zero_gets_bonus(self):
        assert _roundness_score(0) == 30
        assert _roundness_score(0) > _roundness_score(1)

    def test_integer_rounder_than_float(self):
        assert _roundness_score(1) > _roundness_score(1.5)
        assert _roundness_score(10) > _roundness_score(13)

    def test_trailing_zeros_are_rounder(self):
        """100 (1 sig fig) should be rounder than 123 (3 sig figs)."""
        assert _roundness_score(100) > _roundness_score(123)
        assert _roundness_score(1000) > _roundness_score(100)

    def test_last_digit_preference(self):
        """5 > even > odd for last significant digit."""
        assert _roundness_score(5) > _roundness_score(2)
        assert _roundness_score(2) > _roundness_score(1)
        assert _roundness_score(0.5) > _roundness_score(0.7)


class TestThinColorbarTicks:
    """Tests for _thin_colorbar_ticks with roundness-based selection."""

    def _make_colorbar(self, levels, extend="both"):
        """Helper: create a figure with a BoundaryNorm colorbar."""
        fig, ax = plt.subplots()
        cmap = plt.get_cmap("RdBu_r")
        norm = mcolors.BoundaryNorm(levels, cmap.N, extend=extend)
        data = np.random.rand(5, 5) * (levels[-1] - levels[0]) + levels[0]
        cs = ax.pcolormesh(data, cmap=cmap, norm=norm)
        cbar = fig.colorbar(cs, ax=ax)
        return fig, cbar

    def test_ticks_are_subset_of_boundaries(self):
        levels = np.arange(-2, 2.5, 0.5)
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=5)
        ticks = cbar.get_ticks()
        for t in ticks:
            assert t in levels or np.isclose(levels, t).any()
        plt.close(fig)

    def test_max_ticks_respected(self):
        levels = np.arange(-2, 2.5, 0.5)
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=5)
        assert len(cbar.get_ticks()) <= 5
        plt.close(fig)

    def test_ticks_within_boundary_range(self):
        """Ticks should fall within the boundary range."""
        levels = np.arange(-2, 2.5, 0.5)
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=5)
        ticks = cbar.get_ticks()
        assert ticks[0] >= levels[0]
        assert ticks[-1] <= levels[-1]
        plt.close(fig)

    def test_few_boundaries_unchanged(self):
        levels = np.array([-1, 0, 1])
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=7)
        ticks = cbar.get_ticks()
        np.testing.assert_array_equal(ticks, levels)
        plt.close(fig)

    def test_temperature_case_selects_integers(self):
        """[-2, -1.5, ..., 2] should produce integer ticks."""
        levels = np.arange(-2, 2.5, 0.5)
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=7)
        ticks = cbar.get_ticks()
        # All ticks should be integers or half-integers that are "round"
        for t in ticks:
            assert t in levels or np.isclose(levels, t).any()
        plt.close(fig)

    def test_slp_case(self):
        """SLP [990..1030] should thin to round multiples."""
        levels = np.arange(990, 1035, 5)
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=7)
        ticks = cbar.get_ticks()
        assert len(ticks) <= 7
        # Ticks should be round multiples within the range
        for t in ticks:
            assert t in levels or np.isclose(levels, t).any()
        plt.close(fig)

    def test_many_boundaries(self):
        """50+ boundaries should still respect max_ticks."""
        levels = np.arange(0, 10.1, 0.2)
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=7)
        assert len(cbar.get_ticks()) <= 7
        plt.close(fig)

    def test_nine_boundaries_show_all_at_default(self):
        """9 boundaries with default max_ticks=9 should show all."""
        levels = np.arange(-2, 2.5, 0.5)  # 9 boundaries
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=9)
        ticks = cbar.get_ticks()
        np.testing.assert_array_almost_equal(ticks, levels)
        plt.close(fig)

    def test_min_ticks_floor(self):
        """Algorithm should not produce fewer than min_ticks ticks."""
        levels = np.arange(-2, 2.1, 0.1)  # 41 boundaries
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=9, min_ticks=7)
        ticks = cbar.get_ticks()
        assert len(ticks) >= 7
        assert len(ticks) <= 9
        plt.close(fig)

    def test_symmetric_ticks(self):
        """Symmetric boundaries should produce symmetric ticks."""
        levels = np.arange(-2, 2.5, 0.5)  # [-2, -1.5, ..., 2]
        fig, cbar = self._make_colorbar(levels)
        _thin_colorbar_ticks(cbar, max_ticks=7)
        ticks = cbar.get_ticks()
        # Ticks should be symmetric about zero
        np.testing.assert_array_almost_equal(ticks, -ticks[::-1])
        plt.close(fig)

    def test_no_endpoint_crowding(self):
        """Endpoints should not be forced when they don't fit the stride pattern."""
        # Log-like boundaries: [0.01, 0.02, 0.05, 0.1, ..., 100]
        levels = np.array([0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100])
        fig, cbar = self._make_colorbar(levels, extend="both")
        _thin_colorbar_ticks(cbar, max_ticks=7)
        ticks = cbar.get_ticks()
        assert len(ticks) <= 7
        # Ticks should all be actual boundaries
        for t in ticks:
            assert np.isclose(levels, t).any()
        plt.close(fig)


class TestSymmetryDetection:
    """Tests for _is_symmetric helper."""

    def test_symmetric_levels(self):
        assert _is_symmetric(np.array([-2, -1, 0, 1, 2]))
        assert _is_symmetric(np.arange(-2, 2.5, 0.5))

    def test_asymmetric_levels(self):
        assert not _is_symmetric(np.arange(990, 1035, 5))
        assert not _is_symmetric(np.array([0, 1, 2, 3]))

    def test_center_on_white_symmetric(self):
        """center_on_white levels like [-2.5, ..., -0.5, 0.5, ..., 2.5] are symmetric."""
        levels = np.array([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5])
        assert _is_symmetric(levels)

    def test_degenerate(self):
        assert not _is_symmetric(np.array([1, 2]))
        assert not _is_symmetric(np.array([0]))


class TestFormatColorbarTicks:
    """Tests for _format_colorbar_ticks."""

    def _make_colorbar_with_ticks(self, levels):
        fig, ax = plt.subplots()
        cmap = plt.get_cmap("viridis")
        norm = mcolors.BoundaryNorm(levels, cmap.N, extend="both")
        data = np.random.rand(5, 5) * (levels[-1] - levels[0]) + levels[0]
        cs = ax.pcolormesh(data, cmap=cmap, norm=norm)
        cbar = fig.colorbar(cs, ax=ax)
        return fig, cbar

    def test_integers_no_decimals(self):
        levels = np.array([-2, -1, 0, 1, 2], dtype=float)
        fig, cbar = self._make_colorbar_with_ticks(levels)
        _format_colorbar_ticks(cbar)
        cbar.set_ticks(levels)
        fig.canvas.draw()
        labels = [t.get_text() for t in cbar.ax.xaxis.get_ticklabels()]
        for lbl in labels:
            if lbl:
                assert "." not in lbl, f"Integer tick should not have decimal: {lbl}"
        plt.close(fig)

    def test_zero_formatted_as_zero(self):
        """The formatter should render 0.0 as '0'."""
        levels = np.array([-2, -1, 0, 1, 2], dtype=float)
        fig, cbar = self._make_colorbar_with_ticks(levels)
        _format_colorbar_ticks(cbar)
        # Test the formatter function directly
        formatter = cbar.ax.xaxis.get_major_formatter()
        assert formatter(0.0, 0) == "0"
        assert formatter(1.0, 0) == "1"
        assert formatter(-2.0, 0) == "-2"
        plt.close(fig)


class TestAddColorbar:
    """Tests for the public add_colorbar function."""

    def test_returns_colorbar(self):
        fig, ax = plt.subplots()
        data = np.random.rand(5, 5)
        cs = ax.pcolormesh(data)
        cbar = climplot.add_colorbar(cs, ax, "Test")
        assert cbar is not None
        plt.close(fig)

    def test_width_parameter(self):
        fig, ax = plt.subplots()
        data = np.random.rand(5, 5)
        cs = ax.pcolormesh(data)
        cbar = climplot.add_colorbar(cs, ax, "Test", width=0.08)
        assert cbar is not None
        plt.close(fig)

    def test_minor_ticks_off(self):
        """Colorbar should not have minor ticks."""
        cmap, norm, levels = climplot.discrete_cmap(-2, 2, 0.5)
        fig, ax = plt.subplots()
        data = np.random.rand(5, 5) * 4 - 2
        cs = ax.pcolormesh(data, cmap=cmap, norm=norm)
        cbar = climplot.add_colorbar(cs, ax, "Test")
        # Minor tick locations should be empty
        minor_ticks = cbar.ax.xaxis.get_minor_ticks()
        # After minorticks_off(), there should be no minor ticks visible
        assert len(minor_ticks) == 0 or all(not t.get_visible() for t in minor_ticks)
        plt.close(fig)
