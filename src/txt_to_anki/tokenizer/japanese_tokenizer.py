"""Japanese text tokenizer implementation.

This module provides the main JapaneseTokenizer class that uses Sudachi
for morphological analysis and token extraction from Japanese text.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from sudachipy import Dictionary  # type: ignore[import-untyped]
from sudachipy.tokenizer import Tokenizer as SudachiTokenizer  # type: ignore[import-untyped]

from txt_to_anki.tokenizer.exceptions import (
    FileProcessingError,
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

    def tokenize_file(self, file_path: Path | str) -> list[Token]:
        """Tokenize Japanese text from a file.

        Args:
            file_path: Path to the text file to tokenize (Path object or string)

        Returns:
            List of Token objects with linguistic metadata

        Raises:
            FileProcessingError: If file cannot be read or has encoding issues
            TokenizationError: If tokenization fails

        Example:
            >>> tokenizer = JapaneseTokenizer()
            >>> tokens = tokenizer.tokenize_file("japanese_text.txt")
            >>> len(tokens) > 0
            True
        """
        # Convert string to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Validate file exists
        if not file_path.exists():
            raise FileProcessingError(
                f"File not found: {file_path}\n"
                f"Please check that the file path is correct and the file exists."
            )

        # Validate it's a file (not a directory)
        if not file_path.is_file():
            raise FileProcessingError(
                f"Path is not a file: {file_path}\n"
                f"Please provide a path to a text file, not a directory."
            )

        # Try to read the file with UTF-8 encoding
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise FileProcessingError(
                f"File encoding error: {file_path}\n"
                f"The file is not valid UTF-8. Please convert the file to UTF-8 encoding.\n"
                f"You can use tools like 'iconv' or text editors to convert the encoding.\n"
                f"Original error: {e}"
            ) from e
        except PermissionError as e:
            raise FileProcessingError(
                f"Permission denied: {file_path}\n"
                f"You don't have permission to read this file.\n"
                f"Please check file permissions."
            ) from e
        except OSError as e:
            raise FileProcessingError(
                f"Error reading file: {file_path}\n"
                f"An OS error occurred while reading the file.\n"
                f"Original error: {e}"
            ) from e

        # Validate file is not empty
        if not text or not text.strip():
            raise FileProcessingError(
                f"File is empty or contains only whitespace: {file_path}\n"
                f"Please provide a file with Japanese text content."
            )

        # Tokenize the text
        try:
            return self.tokenize_text(text)
        except TokenizationError:
            # Re-raise tokenization errors as-is
            raise
        except Exception as e:
            raise FileProcessingError(
                f"Unexpected error processing file: {file_path}\n"
                f"Original error: {e}"
            ) from e
