"""Main CLI interface for txt-to-anki."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="txt-to-anki",
    help="Convert plain text files into Anki deck formats for spaced repetition learning.",
)


@app.command()
def convert() -> None:
    """Convert a text file to Anki deck format."""
    typer.echo("Converting text to Anki deck format...")
    # TODO: Implement actual conversion logic
    typer.echo("Conversion complete!")


if __name__ == "__main__":
    app()
