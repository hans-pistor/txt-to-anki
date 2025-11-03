"""Japanese text tokenizer implementation.

This module provides the main JapaneseTokenizer class that uses Sudachi
for morphological analysis and token extraction from Japanese text.
"""

from __future__ import annotations

from enum import Enum

from sudachipy import Dictionary  # type: ignore[import-untyped]
from sudachipy.tokenizer import Tokenizer as SudachiTokenizer  # type: ignore[import-untyped]

from txt_to_anki.tokenizer.exceptions import (
    TokenizationError,
    TokenizerInitializationError,
)
from txt_to_anki.tokenizer.token_models import Token


class TokenizationMode(Enum):
    """Tokenization granularity modes for Sudachi.

    Attributes:
        SHORT: Mode A - Short unit tokenization (finest granularity)
        MEDIUM: Mode B - Medium unit tokenization (balanced)
        LONG: Mode C - Long unit tokenization (coarsest granularity)
    """

    SHORT = "A"
    MEDIUM = "B"
    LONG = "C"


class JapaneseTokenizer:
    """Japanese text tokenizer using Sudachi morphological analyzer.

    This class provides methods to tokenize Japanese text into individual words
    with comprehensive linguistic metadata including dictionary forms, readings,
    and part-of-speech information.

    Attributes:
        mode: The tokenization mode (SHORT, MEDIUM, or LONG)
        dictionary_type: The Sudachi dictionary type being used

    Example:
        >>> tokenizer = JapaneseTokenizer()
        >>> tokens = tokenizer.tokenize_text("今日は良い天気ですね。")
        >>> for token in tokens:
        ...     print(f"{token.surface} -> {token.dictionary_form}")
    """

    def __init__(
        self,
        mode: TokenizationMode = TokenizationMode.MEDIUM,
        dictionary_type: str = "full",
    ) -> None:
        """Initialize the Japanese tokenizer.

        Args:
            mode: Tokenization granularity mode (default: MEDIUM)
            dictionary_type: Sudachi dictionary type - "full", "core", or "small" (default: "full")

        Raises:
            TokenizerInitializationError: If Sudachi cannot be initialized
        """
        self.mode = mode
        self.dictionary_type = dictionary_type
        self._tokenizer: SudachiTokenizer | None = None
        self._initialize_sudachi()

    def _initialize_sudachi(self) -> None:
        """Initialize the Sudachi tokenizer.

        Raises:
            TokenizerInitializationError: If Sudachi initialization fails
        """
        try:
            # Load the specified dictionary
            try:
                dictionary = Dictionary(dict=self.dictionary_type)
            except ModuleNotFoundError as e:
                raise TokenizerInitializationError(
                    f"Sudachi dictionary '{self.dictionary_type}' not found. "
                    f"Please install it with: pip install sudachidict-{self.dictionary_type}"
                ) from e

            # Map our enum to Sudachi's SplitMode
            mode_map = {
                TokenizationMode.SHORT: SudachiTokenizer.SplitMode.A,
                TokenizationMode.MEDIUM: SudachiTokenizer.SplitMode.B,
                TokenizationMode.LONG: SudachiTokenizer.SplitMode.C,
            }

            self._tokenizer = dictionary.create(mode=mode_map[self.mode])

        except Exception as e:
            raise TokenizerInitializationError(
                f"Failed to initialize Sudachi tokenizer: {e}"
            ) from e

    def tokenize_text(self, text: str) -> list[Token]:
        """Tokenize Japanese text into individual tokens.

        Args:
            text: Japanese text to tokenize

        Returns:
            List of Token objects with linguistic metadata

        Raises:
            TokenizationError: If tokenization fails

        Example:
            >>> tokenizer = JapaneseTokenizer()
            >>> tokens = tokenizer.tokenize_text("食べた")
            >>> tokens[0].dictionary_form
            '食べる'
        """
        if not text or not text.strip():
            return []

        if self._tokenizer is None:
            raise TokenizationError("Tokenizer not initialized")

        try:
            morphemes = self._tokenizer.tokenize(text)
            tokens: list[Token] = []

            for morpheme in morphemes:
                # Extract all required information from Sudachi morpheme
                surface = morpheme.surface()
                reading = morpheme.reading_form()
                pos = morpheme.part_of_speech()[0]  # Get primary POS tag
                base_form = morpheme.dictionary_form()
                normalized = morpheme.normalized_form()
                features = list(morpheme.part_of_speech())
                position = morpheme.begin()

                token = Token(
                    surface=surface,
                    reading=reading,
                    part_of_speech=pos,
                    base_form=base_form,
                    normalized_form=normalized,
                    features=features,
                    position=position,
                )
                tokens.append(token)

            return tokens

        except Exception as e:
            raise TokenizationError(f"Failed to tokenize text: {e}") from e
