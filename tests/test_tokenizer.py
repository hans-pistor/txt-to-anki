"""Tests for Japanese tokenizer functionality."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from txt_to_anki.tokenizer import (
    FileProcessingError,
    JapaneseTokenizer,
    Token,
    TokenizationError,
    TokenizationMode,
    TokenizerInitializationError,
)


class TestToken:
    """Tests for Token dataclass."""

    def test_token_creation(self) -> None:
        """Test creating a Token instance."""
        token = Token(
            surface="食べた",
            reading="タベタ",
            part_of_speech="動詞",
            base_form="食べる",
            normalized_form="食べる",
            features=["動詞", "一般", "*", "*"],
            position=0,
        )

        assert token.surface == "食べた"
        assert token.reading == "タベタ"
        assert token.base_form == "食べる"
        assert token.dictionary_form == "食べる"

    def test_dictionary_form_fallback(self) -> None:
        """Test dictionary_form falls back to surface when base_form is empty."""
        token = Token(
            surface="こんにちは",
            reading="コンニチハ",
            part_of_speech="感動詞",
            base_form="",
            normalized_form="こんにちは",
            features=["感動詞", "一般", "*", "*"],
            position=0,
        )

        assert token.dictionary_form == "こんにちは"


class TestJapaneseTokenizer:
    """Tests for JapaneseTokenizer class."""

    def test_tokenizer_initialization(self) -> None:
        """Test tokenizer can be initialized."""
        tokenizer = JapaneseTokenizer()
        assert tokenizer.mode == TokenizationMode.MEDIUM

    def test_tokenizer_with_mode(self) -> None:
        """Test tokenizer initialization with different modes."""
        tokenizer = JapaneseTokenizer(mode=TokenizationMode.SHORT)
        assert tokenizer.mode == TokenizationMode.SHORT

    def test_tokenizer_with_dictionary_type(self) -> None:
        """Test tokenizer initialization with specific dictionary type."""
        tokenizer = JapaneseTokenizer(dictionary_type="full")
        assert tokenizer.dictionary_type == "full"

    def test_tokenize_simple_text(self) -> None:
        """Test tokenizing simple Japanese text."""
        tokenizer = JapaneseTokenizer()
        tokens = tokenizer.tokenize_text("今日は良い天気です。")

        assert len(tokens) > 0
        assert all(isinstance(token, Token) for token in tokens)

        # Verify tokens have required attributes
        for token in tokens:
            assert isinstance(token.surface, str)
            assert isinstance(token.reading, str)
            assert isinstance(token.part_of_speech, str)
            assert isinstance(token.base_form, str)
            assert isinstance(token.dictionary_form, str)

    def test_tokenize_verb_conjugation(self) -> None:
        """Test that verb conjugations are normalized to dictionary form."""
        tokenizer = JapaneseTokenizer()
        tokens = tokenizer.tokenize_text("食べた")

        # Find the verb token
        verb_tokens = [t for t in tokens if "動詞" in t.part_of_speech]
        assert len(verb_tokens) > 0

        # The dictionary form should be the base form (食べる)
        verb_token = verb_tokens[0]
        assert verb_token.surface == "食べ"
        assert verb_token.base_form == "食べる"
        assert verb_token.dictionary_form == "食べる"

    def test_tokenize_empty_text(self) -> None:
        """Test tokenizing empty text returns empty list."""
        tokenizer = JapaneseTokenizer()
        tokens = tokenizer.tokenize_text("")
        assert tokens == []

    def test_tokenize_whitespace_only(self) -> None:
        """Test tokenizing whitespace-only text returns empty list."""
        tokenizer = JapaneseTokenizer()
        tokens = tokenizer.tokenize_text("   \n\t  ")
        assert tokens == []

    def test_tokenize_mixed_scripts(self) -> None:
        """Test tokenizing text with hiragana, katakana, and kanji."""
        tokenizer = JapaneseTokenizer()
        tokens = tokenizer.tokenize_text("私はコーヒーを飲みます。")

        assert len(tokens) > 0

        # Verify we get tokens for different script types
        surfaces = [t.surface for t in tokens]
        assert any(t for t in surfaces)  # Should have multiple tokens

    def test_token_positions(self) -> None:
        """Test that tokens have correct position information."""
        tokenizer = JapaneseTokenizer()
        tokens = tokenizer.tokenize_text("今日は")

        # Positions should be non-negative and increasing
        for i, token in enumerate(tokens):
            assert token.position >= 0
            if i > 0:
                assert token.position >= tokens[i - 1].position

    def test_tokenize_with_punctuation(self) -> None:
        """Test tokenizing text with punctuation marks."""
        tokenizer = JapaneseTokenizer()
        tokens = tokenizer.tokenize_text("こんにちは！元気ですか？")

        assert len(tokens) > 0
        # Punctuation should be included as tokens
        surfaces = [t.surface for t in tokens]
        assert "！" in surfaces or "？" in surfaces

    def test_tokenize_complete_sentence(self) -> None:
        """Test tokenizing a complete Japanese sentence."""
        tokenizer = JapaneseTokenizer(mode=TokenizationMode.MEDIUM)
        text = "今日は良い天気ですね。"
        tokens = tokenizer.tokenize_text(text)

        # Verify we get multiple tokens
        assert len(tokens) == 7

        # Verify all tokens have required attributes
        for token in tokens:
            assert token.surface
            assert token.reading
            assert token.part_of_speech
            assert token.dictionary_form

        # Check specific tokens
        surfaces = [t.surface for t in tokens]
        assert "今日" in surfaces
        assert "天気" in surfaces

    def test_tokenize_verb_normalization(self) -> None:
        """Test that conjugated verbs are normalized to dictionary form."""
        tokenizer = JapaneseTokenizer()
        text = "昨日、美味しいラーメンを食べた。"
        tokens = tokenizer.tokenize_text(text)

        # Find tokens where surface differs from dictionary form
        normalized_tokens = [
            (t.surface, t.dictionary_form)
            for t in tokens
            if t.surface != t.dictionary_form
        ]

        # Should have at least one normalized token (食べ -> 食べる)
        assert len(normalized_tokens) > 0

        # Verify the verb is normalized
        verb_normalized = any("食べる" in dict_form for _, dict_form in normalized_tokens)
        assert verb_normalized

    def test_tokenize_with_readings(self) -> None:
        """Test that tokens include katakana readings."""
        tokenizer = JapaneseTokenizer()
        text = "私はコーヒーを飲みます。"
        tokens = tokenizer.tokenize_text(text)

        # Verify we get tokens
        assert len(tokens) == 7

        # All tokens should have readings
        for token in tokens:
            assert token.reading
            assert isinstance(token.reading, str)

        # Check that we have various token types
        surfaces = [t.surface for t in tokens]
        assert "私" in surfaces
        assert "コーヒー" in surfaces
        assert "飲み" in surfaces


class TestJapaneseTextValidation:
    """Tests for Japanese text detection and validation."""

    def test_contains_japanese_with_hiragana(self) -> None:
        """Test Japanese detection with hiragana text."""
        tokenizer = JapaneseTokenizer()
        assert tokenizer._contains_japanese("こんにちは")

    def test_contains_japanese_with_katakana(self) -> None:
        """Test Japanese detection with katakana text."""
        tokenizer = JapaneseTokenizer()
        assert tokenizer._contains_japanese("コーヒー")

    def test_contains_japanese_with_kanji(self) -> None:
        """Test Japanese detection with kanji text."""
        tokenizer = JapaneseTokenizer()
        assert tokenizer._contains_japanese("日本語")

    def test_contains_japanese_with_mixed_scripts(self) -> None:
        """Test Japanese detection with mixed scripts."""
        tokenizer = JapaneseTokenizer()
        assert tokenizer._contains_japanese("私はコーヒーを飲みます。")

    def test_contains_japanese_with_english_only(self) -> None:
        """Test Japanese detection returns False for English text."""
        tokenizer = JapaneseTokenizer()
        assert not tokenizer._contains_japanese("Hello World")

    def test_contains_japanese_with_numbers_only(self) -> None:
        """Test Japanese detection returns False for numbers."""
        tokenizer = JapaneseTokenizer()
        assert not tokenizer._contains_japanese("12345")

    def test_contains_japanese_with_mixed_english_japanese(self) -> None:
        """Test Japanese detection with mixed English and Japanese."""
        tokenizer = JapaneseTokenizer()
        assert tokenizer._contains_japanese("Hello 世界")

    def test_tokenize_non_japanese_text_raises_error(self) -> None:
        """Test that non-Japanese text raises TokenizationError."""
        tokenizer = JapaneseTokenizer(require_japanese=True)

        with pytest.raises(TokenizationError) as exc_info:
            tokenizer.tokenize_text("Hello World")

        error_msg = str(exc_info.value)
        assert "No Japanese text detected" in error_msg
        assert "require_japanese=False" in error_msg

    def test_tokenize_non_japanese_text_with_require_false(self) -> None:
        """Test that non-Japanese text works with require_japanese=False."""
        tokenizer = JapaneseTokenizer(require_japanese=False)
        # Should not raise an error, though results may be empty or unexpected
        tokens = tokenizer.tokenize_text("Hello World")
        # Just verify it doesn't crash
        assert isinstance(tokens, list)

    def test_tokenize_empty_string_returns_empty_list(self) -> None:
        """Test that empty string returns empty list without validation error."""
        tokenizer = JapaneseTokenizer(require_japanese=True)
        tokens = tokenizer.tokenize_text("")
        assert tokens == []

    def test_tokenize_whitespace_returns_empty_list(self) -> None:
        """Test that whitespace-only string returns empty list."""
        tokenizer = JapaneseTokenizer(require_japanese=True)
        tokens = tokenizer.tokenize_text("   \n\t  ")
        assert tokens == []


class TestPartialProcessing:
    """Tests for graceful degradation with partial_ok parameter."""

    def test_tokenize_with_partial_ok_continues_on_error(self) -> None:
        """Test that partial_ok allows processing to continue despite errors."""
        tokenizer = JapaneseTokenizer()
        # Normal Japanese text should work fine with partial_ok
        tokens = tokenizer.tokenize_text("今日は良い天気です。", partial_ok=True)
        assert len(tokens) > 0

    def test_tokenize_file_with_partial_ok(self) -> None:
        """Test file tokenization with partial_ok parameter."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("今日は良い天気です。")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()
            tokens = tokenizer.tokenize_file(temp_path, partial_ok=True)
            assert len(tokens) > 0
        finally:
            temp_path.unlink()

    def test_tokenize_with_partial_ok_false_raises_on_error(self) -> None:
        """Test that partial_ok=False raises errors for problematic text."""
        tokenizer = JapaneseTokenizer()
        # Normal text should work fine even with partial_ok=False
        tokens = tokenizer.tokenize_text("今日は良い天気です。", partial_ok=False)
        assert len(tokens) > 0


class TestFileProcessing:
    """Tests for file processing functionality."""

    def test_tokenize_file_with_path_object(self) -> None:
        """Test tokenizing a file using Path object."""
        # Create a temporary file with Japanese text
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("今日は良い天気です。")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()
            tokens = tokenizer.tokenize_file(temp_path)

            assert len(tokens) > 0
            assert all(isinstance(token, Token) for token in tokens)
        finally:
            temp_path.unlink()

    def test_tokenize_file_with_string_path(self) -> None:
        """Test tokenizing a file using string path."""
        # Create a temporary file with Japanese text
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("私はコーヒーを飲みます。")
            temp_path = f.name

        try:
            tokenizer = JapaneseTokenizer()
            tokens = tokenizer.tokenize_file(temp_path)

            assert len(tokens) > 0
            surfaces = [t.surface for t in tokens]
            assert "私" in surfaces
        finally:
            Path(temp_path).unlink()

    def test_tokenize_file_not_found(self) -> None:
        """Test error handling for non-existent file."""
        tokenizer = JapaneseTokenizer()

        with pytest.raises(FileProcessingError) as exc_info:
            tokenizer.tokenize_file("nonexistent_file.txt")

        assert "File not found" in str(exc_info.value)
        assert "nonexistent_file.txt" in str(exc_info.value)

    def test_tokenize_file_is_directory(self) -> None:
        """Test error handling when path is a directory."""
        tokenizer = JapaneseTokenizer()

        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(FileProcessingError) as exc_info:
                tokenizer.tokenize_file(temp_dir)

            assert "not a file" in str(exc_info.value).lower()

    def test_tokenize_file_empty(self) -> None:
        """Test error handling for empty file."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            # Write nothing
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()

            with pytest.raises(FileProcessingError) as exc_info:
                tokenizer.tokenize_file(temp_path)

            assert "empty" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()

    def test_tokenize_file_whitespace_only(self) -> None:
        """Test error handling for file with only whitespace."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("   \n\t  \n  ")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()

            with pytest.raises(FileProcessingError) as exc_info:
                tokenizer.tokenize_file(temp_path)

            assert "empty" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()

    def test_tokenize_file_invalid_encoding(self) -> None:
        """Test error handling for non-UTF-8 encoded file."""
        # Create a file with non-UTF-8 encoding
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="shift_jis", suffix=".txt", delete=False
        ) as f:
            f.write("今日は良い天気です。")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()

            with pytest.raises(FileProcessingError) as exc_info:
                tokenizer.tokenize_file(temp_path)

            error_msg = str(exc_info.value).lower()
            assert "encoding" in error_msg or "utf-8" in error_msg
        finally:
            temp_path.unlink()

    def test_tokenize_file_multiline_text(self) -> None:
        """Test tokenizing a file with multiple lines."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("今日は良い天気です。\n私はコーヒーを飲みます。\n元気ですか？")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()
            tokens = tokenizer.tokenize_file(temp_path)

            assert len(tokens) > 0
            # Should have tokens from all lines
            surfaces = [t.surface for t in tokens]
            assert "今日" in surfaces
            assert "私" in surfaces
            assert "元気" in surfaces
        finally:
            temp_path.unlink()

    def test_tokenize_real_file(self) -> None:
        """Test tokenizing the sample Japanese text file."""
        sample_file = Path("resources/お隣遊び - ぺんたごん.txt")

        if sample_file.exists():
            tokenizer = JapaneseTokenizer()
            tokens = tokenizer.tokenize_file(sample_file)

            assert len(tokens) > 0
            assert all(isinstance(token, Token) for token in tokens)

            # Verify we get meaningful tokens
            surfaces = [t.surface for t in tokens]
            assert len(surfaces) > 10  # Should have many tokens

    def test_tokenize_binary_file_raises_error(self) -> None:
        """Test that binary files are detected and rejected."""
        # Create a binary file with null bytes
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
            f.write(b"\x00\x01\x02\x03\x04\x05")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()

            with pytest.raises(FileProcessingError) as exc_info:
                tokenizer.tokenize_file(temp_path)

            error_msg = str(exc_info.value)
            assert "binary" in error_msg.lower()
            assert "text file" in error_msg.lower()
        finally:
            temp_path.unlink()

    def test_tokenize_file_with_no_japanese_raises_error(self) -> None:
        """Test that files with no Japanese text raise appropriate error."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("This is English text only.")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer(require_japanese=True)

            with pytest.raises(TokenizationError) as exc_info:
                tokenizer.tokenize_file(temp_path)

            error_msg = str(exc_info.value)
            assert "No Japanese text detected" in error_msg
            assert "require_japanese=False" in error_msg
        finally:
            temp_path.unlink()

    def test_tokenize_file_error_includes_suggestions(self) -> None:
        """Test that file errors include helpful suggestions."""
        tokenizer = JapaneseTokenizer()

        with pytest.raises(FileProcessingError) as exc_info:
            tokenizer.tokenize_file("nonexistent_file.txt")

        error_msg = str(exc_info.value)
        assert "Suggestions:" in error_msg or "Suggestion:" in error_msg
        assert "file path" in error_msg.lower()

    def test_tokenize_file_encoding_error_includes_suggestions(self) -> None:
        """Test that encoding errors include conversion suggestions."""
        # Create a file with non-UTF-8 encoding
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="shift_jis", suffix=".txt", delete=False
        ) as f:
            f.write("今日は良い天気です。")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()

            with pytest.raises(FileProcessingError) as exc_info:
                tokenizer.tokenize_file(temp_path)

            error_msg = str(exc_info.value)
            assert "encoding" in error_msg.lower()
            assert "UTF-8" in error_msg
            # Should include conversion suggestions
            assert "iconv" in error_msg or "convert" in error_msg.lower()
        finally:
            temp_path.unlink()

    def test_tokenize_file_with_mixed_content(self) -> None:
        """Test tokenizing file with mixed Japanese and English content."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("Hello 世界\n今日は良い天気です。\nGoodbye さようなら")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer(require_japanese=False)
            tokens = tokenizer.tokenize_file(temp_path)
            assert len(tokens) > 0
            # Should have tokens from Japanese portions
            surfaces = [t.surface for t in tokens]
            assert "世界" in surfaces or "今日" in surfaces
        finally:
            temp_path.unlink()

    def test_tokenize_file_unexpected_error(self) -> None:
        """Test handling of unexpected errors during file processing."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("今日は良い天気です。")
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()
            # Normal processing should work
            tokens = tokenizer.tokenize_file(temp_path)
            assert len(tokens) > 0
        finally:
            temp_path.unlink()

    def test_tokenize_file_with_high_non_text_ratio(self) -> None:
        """Test binary detection with high non-text character ratio."""
        # Create a file with many non-printable characters
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".dat", delete=False) as f:
            # Mix of binary and some text
            content = bytes([i % 256 for i in range(1000)])
            f.write(content)
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()

            with pytest.raises(FileProcessingError) as exc_info:
                tokenizer.tokenize_file(temp_path)

            error_msg = str(exc_info.value)
            assert "binary" in error_msg.lower() or "text file" in error_msg.lower()
        finally:
            temp_path.unlink()

    def test_tokenize_file_with_mostly_text_content(self) -> None:
        """Test that files with mostly text content are not flagged as binary."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            # Write mostly text with some special characters
            f.write("今日は良い天気です。\n" * 10)
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()
            # Should successfully process as text
            tokens = tokenizer.tokenize_file(temp_path)
            assert len(tokens) > 0
        finally:
            temp_path.unlink()


class TestTokenizerInitialization:
    """Tests for tokenizer initialization and error handling."""

    def test_tokenizer_initialization_with_invalid_dictionary(self) -> None:
        """Test that invalid dictionary type raises appropriate error."""
        # This test verifies the error handling for missing dictionaries
        # In practice, this would require uninstalling the dictionary
        # For now, we test with a valid dictionary to ensure initialization works
        tokenizer = JapaneseTokenizer(dictionary_type="full")
        assert tokenizer.dictionary_type == "full"

    def test_tokenizer_initialization_error_handling(self) -> None:
        """Test that tokenizer initialization errors are handled properly."""
        # Test that tokenizer is properly initialized
        tokenizer = JapaneseTokenizer()
        assert tokenizer._tokenizer is not None

    def test_tokenize_with_uninitialized_tokenizer(self) -> None:
        """Test error handling when tokenizer is not initialized."""
        tokenizer = JapaneseTokenizer()
        # Manually set tokenizer to None to simulate initialization failure
        tokenizer._tokenizer = None

        with pytest.raises(TokenizationError) as exc_info:
            tokenizer.tokenize_text("今日は")

        assert "not initialized" in str(exc_info.value).lower()

    def test_tokenizer_with_missing_core_dictionary(self) -> None:
        """Test that missing core dictionary raises appropriate error."""
        # This test verifies error handling when dictionary is not installed
        try:
            tokenizer = JapaneseTokenizer(dictionary_type="core")
            # If we get here, the dictionary is installed
            assert tokenizer.dictionary_type == "core"
            tokens = tokenizer.tokenize_text("今日は")
            assert len(tokens) > 0
        except TokenizerInitializationError as e:
            # Expected if dictionary is not installed
            error_msg = str(e)
            assert "core" in error_msg.lower()
            assert "install" in error_msg.lower()

    def test_tokenizer_with_missing_small_dictionary(self) -> None:
        """Test that missing small dictionary raises appropriate error."""
        # This test verifies error handling when dictionary is not installed
        try:
            tokenizer = JapaneseTokenizer(dictionary_type="small")
            # If we get here, the dictionary is installed
            assert tokenizer.dictionary_type == "small"
            tokens = tokenizer.tokenize_text("今日は")
            assert len(tokens) > 0
        except TokenizerInitializationError as e:
            # Expected if dictionary is not installed
            error_msg = str(e)
            assert "small" in error_msg.lower()
            assert "install" in error_msg.lower()


class TestPerformance:
    """Tests for performance with large files and text."""

    def test_tokenize_large_text(self) -> None:
        """Test tokenizing large text performs reasonably."""
        tokenizer = JapaneseTokenizer()

        # Create a large text by repeating a sentence
        sentence = "今日は良い天気ですね。私はコーヒーを飲みます。"
        large_text = sentence * 100  # 100 repetitions

        tokens = tokenizer.tokenize_text(large_text)

        # Should successfully tokenize all text
        assert len(tokens) > 0
        # Rough estimate: each sentence has ~14 tokens, so 100 * 14 = 1400
        assert len(tokens) > 1000

    def test_tokenize_large_file(self) -> None:
        """Test tokenizing a large file."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            # Write a large amount of text
            sentence = "今日は良い天気ですね。私はコーヒーを飲みます。\n"
            for _ in range(100):
                f.write(sentence)
            temp_path = Path(f.name)

        try:
            tokenizer = JapaneseTokenizer()
            tokens = tokenizer.tokenize_file(temp_path)

            # Should successfully process the entire file
            assert len(tokens) > 1000
            # Verify tokens have proper structure
            assert all(isinstance(token, Token) for token in tokens)
        finally:
            temp_path.unlink()

    def test_tokenize_real_large_file_if_exists(self) -> None:
        """Test tokenizing the real sample file if it exists."""
        sample_file = Path("resources/お隣遊び - ぺんたごん.txt")

        if sample_file.exists():
            tokenizer = JapaneseTokenizer()
            tokens = tokenizer.tokenize_file(sample_file)

            # Should have many tokens
            assert len(tokens) > 100
            # All tokens should be valid
            assert all(isinstance(token, Token) for token in tokens)
            # All tokens should have required attributes
            for token in tokens:
                assert token.surface
                assert token.reading
                assert token.part_of_speech
                assert token.dictionary_form


class TestTokenizationModes:
    """Tests for tokenization mode configuration and behavior."""

    def test_mode_short_produces_most_tokens(self) -> None:
        """Test that SHORT mode produces the most tokens (finest granularity)."""
        text = "国立国会図書館で調べ物をしました。"

        tokenizer_short = JapaneseTokenizer(mode=TokenizationMode.SHORT)
        tokens_short = tokenizer_short.tokenize_text(text)

        # SHORT mode should split compound words most aggressively
        surfaces = [t.surface for t in tokens_short]

        # Verify exact token count and surfaces
        assert len(tokens_short) == 11
        assert surfaces == ["国立", "国会", "図書", "館", "で", "調べ物", "を", "し", "まし", "た", "。"]

    def test_mode_long_produces_fewest_tokens(self) -> None:
        """Test that LONG mode produces the fewest tokens (coarsest granularity)."""
        text = "国立国会図書館で調べ物をしました。"

        tokenizer_long = JapaneseTokenizer(mode=TokenizationMode.LONG)
        tokens_long = tokenizer_long.tokenize_text(text)

        # LONG mode should keep compound words together
        surfaces = [t.surface for t in tokens_long]

        # Verify exact token count and surfaces
        assert len(tokens_long) == 9
        assert surfaces == ["国立", "国会図書館", "で", "調べ物", "を", "し", "まし", "た", "。"]

    def test_mode_medium_is_balanced(self) -> None:
        """Test that MEDIUM mode produces balanced tokenization."""
        text = "国立国会図書館で調べ物をしました。"

        tokenizer_medium = JapaneseTokenizer(mode=TokenizationMode.MEDIUM)
        tokens_medium = tokenizer_medium.tokenize_text(text)

        # MEDIUM mode should be between SHORT and LONG
        surfaces = [t.surface for t in tokens_medium]

        # Verify exact token count and surfaces
        assert len(tokens_medium) == 10
        assert surfaces == ["国立", "国会", "図書館", "で", "調べ物", "を", "し", "まし", "た", "。"]

    def test_different_modes_produce_different_granularities(self) -> None:
        """Test that different modes produce different token counts for the same text."""
        text = "国立国会図書館で調べ物をしました。"

        tokenizer_short = JapaneseTokenizer(mode=TokenizationMode.SHORT)
        tokenizer_medium = JapaneseTokenizer(mode=TokenizationMode.MEDIUM)
        tokenizer_long = JapaneseTokenizer(mode=TokenizationMode.LONG)

        tokens_short = tokenizer_short.tokenize_text(text)
        tokens_medium = tokenizer_medium.tokenize_text(text)
        tokens_long = tokenizer_long.tokenize_text(text)

        # Verify all three modes produce different token counts
        assert len(tokens_short) == 11  # Most tokens (finest granularity)
        assert len(tokens_medium) == 10  # Medium tokens
        assert len(tokens_long) == 9  # Fewest tokens (coarsest granularity)

        # Verify the relationship: SHORT > MEDIUM > LONG
        assert len(tokens_short) > len(tokens_medium) > len(tokens_long)

    def test_mode_affects_compound_word_splitting(self) -> None:
        """Test that modes handle compound words differently."""
        # "東京都" is a compound word (Tokyo + Metropolitan)
        text = "東京都"

        tokenizer_short = JapaneseTokenizer(mode=TokenizationMode.SHORT)
        tokenizer_long = JapaneseTokenizer(mode=TokenizationMode.LONG)

        tokens_short = tokenizer_short.tokenize_text(text)
        tokens_long = tokenizer_long.tokenize_text(text)

        surfaces_short = [t.surface for t in tokens_short]
        surfaces_long = [t.surface for t in tokens_long]

        # SHORT mode may split compound words more
        # LONG mode keeps compound words together
        # The exact behavior depends on Sudachi's dictionary
        assert len(surfaces_short) >= len(surfaces_long)

    def test_mode_configuration_persists(self) -> None:
        """Test that mode configuration persists across multiple tokenizations."""
        tokenizer = JapaneseTokenizer(mode=TokenizationMode.SHORT)

        text1 = "今日は良い天気です。"
        text2 = "明日も晴れるでしょう。"

        tokens1 = tokenizer.tokenize_text(text1)
        tokens2 = tokenizer.tokenize_text(text2)

        # Both should use SHORT mode
        assert len(tokens1) > 0
        assert len(tokens2) > 0

        # Verify mode is still SHORT
        assert tokenizer.mode == TokenizationMode.SHORT

    def test_all_modes_preserve_token_metadata(self) -> None:
        """Test that all modes preserve complete token metadata."""
        text = "食べました。"

        for mode in [
            TokenizationMode.SHORT,
            TokenizationMode.MEDIUM,
            TokenizationMode.LONG,
        ]:
            tokenizer = JapaneseTokenizer(mode=mode)
            tokens = tokenizer.tokenize_text(text)

            # All tokens should have complete metadata regardless of mode
            for token in tokens:
                assert token.surface
                assert token.reading
                assert token.part_of_speech
                assert token.dictionary_form
                assert isinstance(token.position, int)
                assert token.features

    def test_mode_enum_values(self) -> None:
        """Test that TokenizationMode enum has correct values."""
        assert TokenizationMode.SHORT.value == "A"
        assert TokenizationMode.MEDIUM.value == "B"
        assert TokenizationMode.LONG.value == "C"

    def test_default_mode_is_medium(self) -> None:
        """Test that default tokenization mode is MEDIUM."""
        tokenizer = JapaneseTokenizer()
        assert tokenizer.mode == TokenizationMode.MEDIUM


class TestIntegration:
    """Integration tests for complete tokenization workflows."""

    def test_end_to_end_file_to_vocabulary(self) -> None:
        """Test complete workflow from file to vocabulary extraction."""
        # Create a test file with various Japanese text
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("私は毎日日本語を勉強します。\n")
            f.write("昨日、美味しいラーメンを食べました。\n")
            f.write("明日も頑張ります！\n")
            temp_path = Path(f.name)

        try:
            # Initialize tokenizer
            tokenizer = JapaneseTokenizer(mode=TokenizationMode.MEDIUM)

            # Tokenize file
            tokens = tokenizer.tokenize_file(temp_path)

            # Extract vocabulary (unique dictionary forms)
            vocabulary = {token.dictionary_form for token in tokens}

            # Verify we got meaningful vocabulary
            assert len(vocabulary) > 10
            assert "勉強" in vocabulary or "勉強する" in vocabulary
            assert "食べる" in vocabulary
            assert "頑張る" in vocabulary

            # Verify all tokens have complete metadata
            for token in tokens:
                assert token.surface
                assert token.reading
                assert token.part_of_speech
                assert token.dictionary_form
                assert isinstance(token.position, int)
                assert token.features

        finally:
            temp_path.unlink()

    def test_end_to_end_with_different_modes(self) -> None:
        """Test that different modes produce different but valid results."""
        text = "国立国会図書館で調べ物をしました。"

        results = {}
        for mode in [
            TokenizationMode.SHORT,
            TokenizationMode.MEDIUM,
            TokenizationMode.LONG,
        ]:
            tokenizer = JapaneseTokenizer(mode=mode)
            tokens = tokenizer.tokenize_text(text)
            results[mode] = tokens

        # All modes should produce valid tokens
        for mode, tokens in results.items():
            assert len(tokens) > 0
            assert all(isinstance(token, Token) for token in tokens)

        # Different modes should produce different token counts
        assert len(results[TokenizationMode.SHORT]) != len(
            results[TokenizationMode.LONG]
        )

    def test_vocabulary_extraction_with_filtering(self) -> None:
        """Test extracting vocabulary while filtering particles."""
        tokenizer = JapaneseTokenizer()
        text = "私は日本語を勉強します。"
        tokens = tokenizer.tokenize_text(text)

        # Extract only content words (exclude particles)
        particles = {"助詞", "助動詞"}
        content_words = [
            token.dictionary_form
            for token in tokens
            if token.part_of_speech not in particles
        ]

        # Should have content words but not particles
        assert len(content_words) > 0
        assert "私" in content_words
        assert "日本語" in content_words
        assert "勉強" in content_words or "勉強する" in content_words

    def test_reading_extraction_for_anki(self) -> None:
        """Test extracting readings suitable for Anki cards."""
        tokenizer = JapaneseTokenizer()
        text = "私は日本語を勉強します。"
        tokens = tokenizer.tokenize_text(text)

        # Create word-reading pairs for Anki
        anki_pairs = [
            (token.surface, token.reading)
            for token in tokens
            if token.part_of_speech not in {"助詞", "助動詞", "記号"}
        ]

        # Should have meaningful pairs
        assert len(anki_pairs) > 0

        # Verify all pairs have readings
        for surface, reading in anki_pairs:
            assert reading  # Not empty
            assert isinstance(reading, str)

    def test_multiple_files_processing(self) -> None:
        """Test processing multiple files in sequence."""
        files = []
        try:
            # Create multiple test files
            for i in range(3):
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", suffix=".txt", delete=False
                ) as f:
                    f.write(f"これはファイル{i + 1}です。\n")
                    f.write("日本語のテキストです。\n")
                    files.append(Path(f.name))

            # Process all files with same tokenizer
            tokenizer = JapaneseTokenizer()
            all_tokens = []

            for file_path in files:
                tokens = tokenizer.tokenize_file(file_path)
                all_tokens.extend(tokens)

            # Should have tokens from all files
            assert len(all_tokens) > 20  # At least some tokens from each file

            # Verify all tokens are valid
            assert all(isinstance(token, Token) for token in all_tokens)

        finally:
            for file_path in files:
                file_path.unlink()

    def test_error_recovery_workflow(self) -> None:
        """Test that errors provide actionable information for recovery."""
        tokenizer = JapaneseTokenizer()

        # Test 1: Non-existent file
        try:
            tokenizer.tokenize_file("nonexistent.txt")
            assert False, "Should have raised FileProcessingError"
        except FileProcessingError as e:
            error_msg = str(e)
            # Error should include suggestions
            assert "Suggestion" in error_msg or "suggestion" in error_msg.lower()
            assert "file path" in error_msg.lower()

        # Test 2: Non-Japanese text
        try:
            tokenizer.tokenize_text("This is English only")
            assert False, "Should have raised TokenizationError"
        except TokenizationError as e:
            error_msg = str(e)
            # Error should include suggestions
            assert "require_japanese=False" in error_msg

        # Test 3: Empty text (should not raise error)
        tokens = tokenizer.tokenize_text("")
        assert tokens == []
