"""Punctuation filter for removing punctuation marks from token lists.

This module provides a filter that removes common Japanese and ASCII
punctuation marks from tokenization results.
"""

from __future__ import annotations

from txt_to_anki.tokenizer.token_models import Token


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
