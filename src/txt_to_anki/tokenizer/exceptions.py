"""Custom exceptions for the tokenizer module.

This module defines custom exception classes for handling tokenization errors.
"""

from __future__ import annotations


class TokenizerError(Exception):
    """Base exception for tokenizer-related errors."""

    pass


class TokenizerInitializationError(TokenizerError):
    """Raised when the tokenizer fails to initialize.

    This typically occurs when Sudachi or its dictionary cannot be loaded.
    """

    pass


class TokenizationError(TokenizerError):
    """Raised when text tokenization fails.

    This occurs when Sudachi cannot process the provided text.
    """

    pass


class FileProcessingError(TokenizerError):
    """Raised when file processing fails.

    This occurs for file reading, encoding, or validation issues.
    """

    pass
