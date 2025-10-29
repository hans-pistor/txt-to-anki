"""Tests for the CLI module."""

from __future__ import annotations

from typer.testing import CliRunner

from txt_to_anki.cli import app


def test_convert_command_basic() -> None:
    """Test basic convert command functionality."""
    runner = CliRunner()

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Converting text to Anki deck format" in result.output
    assert "Conversion complete!" in result.output
