"""Data models for Japanese tokens.

This module defines the Token dataclass that represents an individual word
extracted from Japanese text with its linguistic metadata.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Token:
    """Represents a single token extracted from Japanese text.

    Attributes:
        surface: Original word form as it appears in text (e.g., "食べた", "食べている")
        reading: Katakana reading of the token
        part_of_speech: Part-of-speech tag from Sudachi
        base_form: Dictionary/lemma form (e.g., "食べる" for all conjugated forms)
        normalized_form: Sudachi's normalized representation
        features: Additional linguistic features from Sudachi
        position: Character offset in the original text
    """

    surface: str
    reading: str
    part_of_speech: str
    base_form: str
    normalized_form: str
    features: list[str]
    position: int

    @property
    def dictionary_form(self) -> str:
        """Returns the dictionary form, prioritizing base_form over surface.

        Returns:
            The base form if available, otherwise the surface form.
        """
        return self.base_form if self.base_form else self.surface
