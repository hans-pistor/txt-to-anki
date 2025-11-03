"""Part-of-speech based token filters.

This module provides filters that remove tokens based on their
part-of-speech tags and linguistic characteristics.
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


class PunctuationFilter:
    """Filter that removes punctuation tokens from token lists.

    This filter removes common Japanese and ASCII punctuation marks including:
    - Japanese punctuation: 。、！？「」『』（）【】・ー～
    - ASCII punctuation: . , ! ? " ' ( ) [ ] - etc.

    Useful for vocabulary extraction where punctuation marks are not needed.

    Example:
        >>> tokenizer = JapaneseTokenizer()
        >>> tokenizer.add_filter(PunctuationFilter())
        >>> tokens = tokenizer.tokenize_text("こんにちは。元気ですか？")
        >>> # "。" and "？" will be filtered out
    """

    # Common Japanese and ASCII punctuation characters
    _PUNCTUATION_CHARS = {
        # Japanese punctuation
        "。",
        "、",
        "！",
        "？",
        "「",
        "」",
        "『",
        "』",
        "（",
        "）",
        "【",
        "】",
        "・",
        "ー",
        "～",
        "…",
        "‥",
        # ASCII punctuation
        ".",
        ",",
        "!",
        "?",
        '"',
        "'",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "-",
        "_",
        ":",
        ";",
        "/",
        "\\",
        "|",
    }

    def filter(self, tokens: list[Token]) -> list[Token]:
        """Remove punctuation tokens from the list.

        Args:
            tokens: List of tokens to filter

        Returns:
            List of tokens with punctuation removed
        """
        return [
            token
            for token in tokens
            if token.surface not in self._PUNCTUATION_CHARS
            and token.part_of_speech != "補助記号"  # Supplementary symbol POS tag
        ]
