"""Protocol definition for token filtering.

This module defines the TokenFilter protocol that all filter implementations
must follow. The protocol-based approach allows for flexible, extensible
filtering without requiring inheritance.
"""

from __future__ import annotations

from typing import Protocol

from txt_to_anki.tokenizer.token_models import Token


class TokenFilter(Protocol):
    """Protocol for token filtering implementations.

    Any class that implements a filter method with the correct signature
    can be used as a TokenFilter. This protocol-based approach provides
    flexibility and allows for easy composition of filters.

    Example:
        >>> class MyFilter:
        ...     def filter(self, tokens: list[Token]) -> list[Token]:
        ...         return [t for t in tokens if len(t.surface) > 1]
        ...
        >>> tokenizer = JapaneseTokenizer()
        >>> tokenizer.add_filter(MyFilter())
    """

    def filter(self, tokens: list[Token]) -> list[Token]:
        """Filter tokens based on specific criteria.

        Args:
            tokens: List of tokens to filter

        Returns:
            Filtered list of tokens
        """
        ...
