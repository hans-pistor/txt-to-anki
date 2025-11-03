"""Japanese text tokenizer implementation.

This module provides the main JapaneseTokenizer class that uses Sudachi
for morphological analysis and token extraction from Japanese text.
"""

from __future__ import annotations

import re
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

# Type hint for filter protocol
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from txt_to_anki.tokenizer.filters.protocol import TokenFilter


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

    # Japanese character ranges for validation
    _HIRAGANA_RANGE = r"[\u3040-\u309F]"
    _KATAKANA_RANGE = r"[\u30A0-\u30FF]"
    _KANJI_RANGE = r"[\u4E00-\u9FFF]"
    _JAPANESE_PATTERN = re.compile(
        f"({_HIRAGANA_RANGE}|{_KATAKANA_RANGE}|{_KANJI_RANGE})+"
    )

    def __init__(
        self,
        mode: TokenizationMode = TokenizationMode.MEDIUM,
        dictionary_type: str = "full",
        require_japanese: bool = True,
    ) -> None:
        """Initialize the Japanese tokenizer.

        Args:
            mode: Tokenization granularity mode (default: MEDIUM)
            dictionary_type: Sudachi dictionary type - "full", "core", or "small" (default: "full")
            require_japanese: Whether to require Japanese text in input (default: True)

        Raises:
            TokenizerInitializationError: If Sudachi cannot be initialized
        """
        self.mode = mode
        self.dictionary_type = dictionary_type
        self.require_japanese = require_japanese
        self._tokenizer: SudachiTokenizer | None = None
        self._filters: list[TokenFilter] = []
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

    def _contains_japanese(self, text: str) -> bool:
        """Check if text contains Japanese characters.

        Args:
            text: Text to check

        Returns:
            True if text contains hiragana, katakana, or kanji characters
        """
        return bool(self._JAPANESE_PATTERN.search(text))

    def _validate_text_content(self, text: str, source: str = "input") -> None:
        """Validate that text contains Japanese characters.

        Args:
            text: Text to validate
            source: Description of the text source for error messages

        Raises:
            TokenizationError: If text contains no Japanese characters and require_japanese is True
        """
        if self.require_japanese and not self._contains_japanese(text):
            raise TokenizationError(
                f"No Japanese text detected in {source}.\n"
                f"The text appears to contain no hiragana, katakana, or kanji characters.\n"
                f"Suggestions:\n"
                f"  - Verify the file contains Japanese text\n"
                f"  - Check if the file encoding is correct (should be UTF-8)\n"
                f"  - If processing mixed-language text, set require_japanese=False"
            )

    def _is_likely_binary(self, file_path: Path) -> bool:
        """Check if a file is likely binary (non-text) content.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file appears to be binary
        """
        try:
            # Read first 8KB to check for binary content
            with open(file_path, "rb") as f:
                chunk = f.read(8192)

            # Check for null bytes (common in binary files)
            if b"\x00" in chunk:
                return True

            # Check for high ratio of non-printable characters
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
            non_text = sum(1 for byte in chunk if byte not in text_chars)

            # If more than 30% non-text characters, likely binary
            return len(chunk) > 0 and non_text / len(chunk) > 0.3

        except Exception:
            # If we can't read the file, assume it might be binary
            return False

    def add_filter(self, filter_impl: TokenFilter) -> None:
        """Add a filter to be applied to tokenization results.

        Filters are applied in the order they are added. Each filter receives
        the output of the previous filter.

        Args:
            filter_impl: A TokenFilter implementation to add

        Example:
            >>> from txt_to_anki.tokenizer.filters import ParticleFilter, PunctuationFilter
            >>> tokenizer = JapaneseTokenizer()
            >>> tokenizer.add_filter(ParticleFilter())
            >>> tokenizer.add_filter(PunctuationFilter())
            >>> tokens = tokenizer.tokenize_text("私は学生です。")
            >>> # Particles and punctuation will be filtered out
        """
        self._filters.append(filter_impl)

    def set_filters(self, filters: list[TokenFilter]) -> None:
        """Set the complete list of filters, replacing any existing filters.

        Args:
            filters: List of TokenFilter implementations

        Example:
            >>> from txt_to_anki.tokenizer.filters import ParticleFilter, PunctuationFilter
            >>> tokenizer = JapaneseTokenizer()
            >>> tokenizer.set_filters([ParticleFilter(), PunctuationFilter()])
        """
        self._filters = filters.copy()

    def clear_filters(self) -> None:
        """Remove all filters from the tokenizer.

        Example:
            >>> tokenizer = JapaneseTokenizer()
            >>> tokenizer.add_filter(ParticleFilter())
            >>> tokenizer.clear_filters()
            >>> # No filters will be applied
        """
        self._filters.clear()

    def apply_filters(self, tokens: list[Token]) -> list[Token]:
        """Apply all configured filters to a list of tokens.

        Filters are applied sequentially in the order they were added.
        Each filter receives the output of the previous filter.

        Args:
            tokens: List of tokens to filter

        Returns:
            Filtered list of tokens

        Example:
            >>> tokenizer = JapaneseTokenizer()
            >>> tokenizer.add_filter(ParticleFilter())
            >>> raw_tokens = tokenizer.tokenize_text("私は学生です", apply_filters=False)
            >>> filtered_tokens = tokenizer.apply_filters(raw_tokens)
        """
        result = tokens
        for filter_impl in self._filters:
            result = filter_impl.filter(result)
        return result

    def tokenize_text(
        self, text: str, partial_ok: bool = False, apply_filters: bool = True
    ) -> list[Token]:
        """Tokenize Japanese text into individual tokens.

        Args:
            text: Japanese text to tokenize
            partial_ok: If True, continue processing even if some segments fail (default: False)
            apply_filters: If True, apply configured filters to results (default: True)

        Returns:
            List of Token objects with linguistic metadata

        Raises:
            TokenizationError: If tokenization fails and partial_ok is False

        Example:
            >>> tokenizer = JapaneseTokenizer()
            >>> tokens = tokenizer.tokenize_text("食べた")
            >>> tokens[0].dictionary_form
            '食べる'
        """
        if not text or not text.strip():
            return []

        if self._tokenizer is None:
            raise TokenizationError(
                "Tokenizer not initialized.\n"
                "This is an internal error. Please report this issue."
            )

        # Validate text contains Japanese if required
        self._validate_text_content(text, "input text")

        try:
            morphemes = self._tokenizer.tokenize(text)
            tokens: list[Token] = []

            for morpheme in morphemes:
                try:
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

                except Exception as e:
                    if partial_ok:
                        # Log the error but continue processing
                        # In production, this would use proper logging
                        continue
                    else:
                        raise TokenizationError(
                            f"Failed to process token at position {morpheme.begin()}: {e}\n"
                            f"Surface form: {morpheme.surface()}\n"
                            f"Suggestion: Try setting partial_ok=True to skip problematic tokens"
                        ) from e

            # Apply filters if requested
            if apply_filters:
                tokens = self.apply_filters(tokens)

            return tokens

        except TokenizationError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            raise TokenizationError(
                f"Failed to tokenize text: {e}\n"
                f"Suggestions:\n"
                f"  - Verify the text is valid Japanese\n"
                f"  - Check for unusual characters or formatting\n"
                f"  - Try with a different tokenization mode\n"
                f"  - Set partial_ok=True to skip problematic segments"
            ) from e

    def tokenize_file(
        self,
        file_path: Path | str,
        partial_ok: bool = False,
        apply_filters: bool = True,
    ) -> list[Token]:
        """Tokenize Japanese text from a file.

        Args:
            file_path: Path to the text file to tokenize (Path object or string)
            partial_ok: If True, continue processing even if some segments fail (default: False)
            apply_filters: If True, apply configured filters to results (default: True)

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
                f"Suggestions:\n"
                f"  - Check that the file path is correct\n"
                f"  - Verify the file exists in the specified location\n"
                f"  - Use an absolute path if the relative path is unclear"
            )

        # Validate it's a file (not a directory)
        if not file_path.is_file():
            raise FileProcessingError(
                f"Path is not a file: {file_path}\n"
                f"The specified path points to a directory, not a file.\n"
                f"Suggestion: Provide a path to a text file, not a directory."
            )

        # Check if file is likely binary
        if self._is_likely_binary(file_path):
            raise FileProcessingError(
                f"File appears to be binary (non-text): {file_path}\n"
                f"This tokenizer only processes text files.\n"
                f"Suggestions:\n"
                f"  - Verify the file is a text file (.txt, .md, etc.)\n"
                f"  - Check if the file is corrupted\n"
                f"  - Ensure the file is not a compressed archive or image"
            )

        # Try to read the file with UTF-8 encoding
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            # Try to detect the actual encoding
            error_position = getattr(e, "start", 0)
            raise FileProcessingError(
                f"File encoding error: {file_path}\n"
                f"The file is not valid UTF-8 (error at byte {error_position}).\n"
                f"Suggestions:\n"
                f"  - Convert the file to UTF-8 encoding\n"
                f"  - Use 'iconv -f SHIFT-JIS -t UTF-8 input.txt > output.txt' for Japanese files\n"
                f"  - Use a text editor like VS Code to convert encoding\n"
                f"  - Common Japanese encodings: Shift-JIS, EUC-JP, ISO-2022-JP"
            ) from e
        except PermissionError as e:
            raise FileProcessingError(
                f"Permission denied: {file_path}\n"
                f"You don't have permission to read this file.\n"
                f"Suggestions:\n"
                f"  - Check file permissions with 'ls -l {file_path}'\n"
                f"  - Use 'chmod +r {file_path}' to add read permission\n"
                f"  - Verify you have access to the parent directory"
            ) from e
        except OSError as e:
            raise FileProcessingError(
                f"Error reading file: {file_path}\n"
                f"An OS error occurred while reading the file.\n"
                f"Suggestions:\n"
                f"  - Check if the file system is accessible\n"
                f"  - Verify disk space is available\n"
                f"  - Ensure the file is not locked by another process\n"
                f"Original error: {e}"
            ) from e

        # Validate file is not empty
        if not text or not text.strip():
            raise FileProcessingError(
                f"File is empty or contains only whitespace: {file_path}\n"
                f"Suggestion: Provide a file with Japanese text content."
            )

        # Tokenize the text
        try:
            return self.tokenize_text(
                text, partial_ok=partial_ok, apply_filters=apply_filters
            )
        except TokenizationError as e:
            # Add file context to tokenization errors
            raise TokenizationError(
                f"Error tokenizing file: {file_path}\n{str(e)}"
            ) from e
        except Exception as e:
            raise FileProcessingError(
                f"Unexpected error processing file: {file_path}\n"
                f"Original error: {e}\n"
                f"Suggestion: Please report this issue with the file details"
            ) from e
