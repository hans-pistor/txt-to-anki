"""Tests for Japanese tokenizer functionality."""

from __future__ import annotations


from txt_to_anki.tokenizer import JapaneseTokenizer, Token, TokenizationMode


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
