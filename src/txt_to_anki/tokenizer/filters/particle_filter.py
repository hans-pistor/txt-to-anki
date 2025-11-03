"""Particle filter for removing Japanese particles from token lists.

This module provides a filter that removes Japanese particles (助詞)
from tokenization results.
"""

from __future__ import annotations

from txt_to_anki.tokenizer.token_models import Token


class ParticleFilter:
    """Filter that removes Japanese particles from token lists.

    Japanese particles (助詞) are grammatical markers that indicate
    relationships between words. Common particles include は, が, を, に, で, etc.

    This filter is useful for vocabulary extraction where particles are
    typically not needed for study.

    Example:
        >>> tokenizer = JapaneseTokenizer()
        >>> tokenizer.add_filter(ParticleFilter())
        >>> tokens = tokenizer.tokenize_text("私は学生です")
        >>> # "は" particle will be filtered out
    """

    def filter(self, tokens: list[Token]) -> list[Token]:
        """Remove particle tokens from the list.

        Args:
            tokens: List of tokens to filter

        Returns:
            List of tokens with particles removed
        """
        return [token for token in tokens if token.part_of_speech != "助詞"]
