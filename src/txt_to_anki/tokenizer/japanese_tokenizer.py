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

    Sudachi provides three tokenization modes that control how text is segmented
    into tokens. The modes differ in their treatment of compound words and
    multi-morpheme expressions.

    Attributes:
        SHORT: Mode A - Short unit tokenization (finest granularity)
            Splits text into the smallest meaningful units. Compound words and
            multi-morpheme expressions are broken down into individual morphemes.
            Best for: Detailed linguistic analysis, learning individual morphemes.
            Example: "東京都" → ["東京", "都"] (Tokyo + Metropolitan)

        MEDIUM: Mode B - Medium unit tokenization (balanced, default)
            Provides balanced tokenization suitable for most use cases. Keeps
            common compound words together while splitting complex expressions.
            Best for: General vocabulary extraction, Anki deck creation.
            Example: "東京都" → ["東京都"] (Tokyo Metropolitan)

        LONG: Mode C - Long unit tokenization (coarsest granularity)
            Keeps compound words and multi-morpheme expressions together as
            single tokens. Produces fewer, longer tokens.
            Best for: Reading comprehension, phrase-level vocabulary.
            Example: "国際連合" → ["国際連合"] (United Nations as one token)

    Mode Comparison Example:
        Text: "国際連合本部ビルに行きました。"
        (I went to the United Nations Headquarters building.)

        SHORT mode (Mode A):
            ["国際", "連合", "本部", "ビル", "に", "行き", "まし", "た", "。"]
            (9 tokens - finest granularity)

        MEDIUM mode (Mode B):
            ["国際連合", "本部", "ビル", "に", "行き", "まし", "た", "。"]
            (8 tokens - balanced)

        LONG mode (Mode C):
            ["国際連合本部ビル", "に", "行きました", "。"]
            (4 tokens - coarsest granularity)

    Choosing a Mode:
        - Use SHORT for learning individual kanji compounds and morphemes
        - Use MEDIUM (default) for general vocabulary extraction
        - Use LONG for learning phrases and compound expressions
    """

    SHORT = "A"
    MEDIUM = "B"
    LONG = "C"


class JapaneseTokenizer:
    """Japanese text tokenizer using Sudachi morphological analyzer.

    This class provides methods to tokenize Japanese text into individual words
    with comprehensive linguistic metadata including dictionary forms, readings,
    and part-of-speech information.

    The tokenizer supports three granularity modes (SHORT, MEDIUM, LONG) that
    control how compound words and multi-morpheme expressions are segmented.
    See TokenizationMode for detailed mode descriptions.

    Attributes:
        mode: The tokenization mode (SHORT, MEDIUM, or LONG)
        dictionary_type: The Sudachi dictionary type being used

    Examples:
        Basic usage with default MEDIUM mode:
            >>> tokenizer = JapaneseTokenizer()
            >>> tokens = tokenizer.tokenize_text("今日は良い天気ですね。")
            >>> for token in tokens:
            ...     print(f"{token.surface} -> {token.dictionary_form}")
            今日 -> 今日
            は -> は
            良い -> 良い
            天気 -> 天気
            です -> です
            ね -> ね
            。 -> 。

        Using SHORT mode for finest granularity:
            >>> tokenizer = JapaneseTokenizer(mode=TokenizationMode.SHORT)
            >>> tokens = tokenizer.tokenize_text("東京都に行きました。")
            >>> [t.surface for t in tokens]
            ['東京', '都', 'に', '行き', 'まし', 'た', '。']

        Using LONG mode for coarsest granularity:
            >>> tokenizer = JapaneseTokenizer(mode=TokenizationMode.LONG)
            >>> tokens = tokenizer.tokenize_text("東京都に行きました。")
            >>> [t.surface for t in tokens]
            ['東京都', 'に', '行きました', '。']

        Processing a file:
            >>> tokenizer = JapaneseTokenizer()
            >>> tokens = tokenizer.tokenize_file("japanese_text.txt")
            >>> print(f"Extracted {len(tokens)} tokens")

        Extracting vocabulary with dictionary forms:
            >>> tokenizer = JapaneseTokenizer(mode=TokenizationMode.MEDIUM)
            >>> tokens = tokenizer.tokenize_text("食べました")
            >>> vocab = {t.dictionary_form for t in tokens if t.part_of_speech == "動詞"}
            >>> print(vocab)
            {'食べる'}
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
