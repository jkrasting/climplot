"""Tests for climplot.style module."""

import pytest
import matplotlib.pyplot as plt

import climplot


class TestStyle:
    """Tests for style functions."""

    def setup_method(self):
        """Reset style before each test."""
        climplot.reset_style()

    def teardown_method(self):
        """Reset style after each test."""
        climplot.reset_style()

    def test_publication_sets_mode(self):
        """Test that publication() sets the current mode."""
        climplot.publication()
        assert climplot.get_current_mode() == "publication"

    def test_presentation_sets_mode(self):
        """Test that presentation() sets the current mode."""
        climplot.presentation()
        assert climplot.get_current_mode() == "presentation"

    def test_publication_font_sizes(self):
        """Test that publication mode sets correct font sizes."""
        climplot.publication()
        assert plt.rcParams["font.size"] == 10
        assert plt.rcParams["axes.labelsize"] == 10
        assert plt.rcParams["axes.titlesize"] == 11
        assert plt.rcParams["xtick.labelsize"] == 8

    def test_presentation_font_sizes(self):
        """Test that presentation mode sets correct font sizes."""
        climplot.presentation()
        assert plt.rcParams["font.size"] == 14
        assert plt.rcParams["axes.labelsize"] == 14
        assert plt.rcParams["axes.titlesize"] == 16

    def test_publication_dpi(self):
        """Test that publication mode sets 300 DPI."""
        climplot.publication()
        assert plt.rcParams["figure.dpi"] == 300
        assert plt.rcParams["savefig.dpi"] == 300

    def test_presentation_dpi(self):
        """Test that presentation mode sets 150 DPI."""
        climplot.presentation()
        assert plt.rcParams["figure.dpi"] == 150
        assert plt.rcParams["savefig.dpi"] == 150

    def test_reset_style(self):
        """Test that reset_style clears the mode."""
        climplot.publication()
        climplot.reset_style()
        assert climplot.get_current_mode() is None

    def test_get_current_mode_initial(self):
        """Test that initial mode is None."""
        assert climplot.get_current_mode() is None
