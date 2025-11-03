# Japanese Tokenizer Design Document

## Overview

The Japanese Tokenizer is a modular component that processes Japanese text files and extracts individual words (tokens) using the Sudachi morphological analyzer. The system is designed as a reusable Python module that can be integrated into the existing txt-to-anki application architecture while maintaining high code quality standards.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Text File     │───▶│ Japanese         │───▶│ Token List      │
│   (.txt)        │    │ Tokenizer        │    │ (structured)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Sudachi Engine   │
                       │ (SudachiPy)      │
                       └──────────────────┘
```

### Module Structure

```
src/txt_to_anki/
├── tokenizer/
│   ├── __init__.py
│   ├── japanese_tokenizer.py    # Main tokenizer class
│   ├── token_models.py          # Data models for tokens
│   ├── exceptions.py            # Custom exceptions
│   └── filters/                 # Stretch goal: filtering system
│       ├── __init__.py
│       ├── protocol.py          # TokenFilter protocol definition
│       ├── pos_filters.py       # Part-of-speech based filters
│       ├── length_filters.py    # Length-based filters
│       └── deduplication.py     # Duplicate removal filters
```

## Components and Interfaces

### 1. JapaneseTokenizer Class

**Purpose**: Main interface for Japanese text tokenization

**Key Methods**:
```python
class JapaneseTokenizer:
    def __init__(self, mode: TokenizationMode = TokenizationMode.MEDIUM) -> None
    def tokenize_file(self, file_path: Path) -> List[Token]
    def tokenize_text(self, text: str) -> List[Token]
    # Filtering methods (stretch goals):
    # def add_filter(self, filter_impl: TokenFilter) -> None
    # def set_filters(self, filters: List[TokenFilter]) -> None
    # def apply_filters(self, tokens: List[Token]) -> List[Token]
```

**Configuration Options**:
- Tokenization mode (A/B/C corresponding to short/medium/long units)
- Part-of-speech filtering
- Minimum frequency thresholds
- Duplicate removal settings

### 2. Token Data Model

**Purpose**: Structured representation of extracted tokens

```python
@dataclass
class Token:
    surface: str           # Original word form (e.g., "食べた", "食べている")
    reading: str           # Katakana reading
    part_of_speech: str    # POS tag
    base_form: str         # Dictionary form (e.g., "食べる" for all forms)
    normalized_form: str   # Sudachi's normalized form
    features: List[str]    # Additional linguistic features
    position: int          # Position in original text
    
    @property
    def dictionary_form(self) -> str:
        """Returns the dictionary form, prioritizing base_form over surface."""
        return self.base_form if self.base_form else self.surface
```

### 3. Token Filtering System (Stretch Goal)

**Purpose**: Protocol-based filtering system for extensible token processing

*Note: This is a stretch goal to be implemented after core tokenization functionality is complete.*

```python
from typing import Protocol, List

class TokenFilter(Protocol):
    """Protocol for token filtering implementations."""
    
    def filter(self, tokens: List[Token]) -> List[Token]:
        """Filter tokens based on specific criteria."""
        ...

# Future filter implementations (stretch goals):
# - ParticleFilter: Remove particles (は, が, を, etc.)
# - LengthFilter: Filter by minimum character length
# - POSFilter: Filter by part-of-speech tags
# - DuplicationFilter: Remove duplicates based on dictionary form
```

### 4. Exception Handling

**Custom Exceptions**:
- `TokenizerInitializationError`: Sudachi setup failures
- `FileProcessingError`: File reading/encoding issues
- `TokenizationError`: Processing failures for specific text

## Data Models

### Input Processing Flow

1. **File Reading**: UTF-8 encoded text files
2. **Text Preprocessing**: 
   - Encoding validation and conversion
   - Japanese text detection and extraction
   - Whitespace normalization
3. **Tokenization**: Sudachi processing with selected mode
4. **Post-processing**: Filtering and deduplication
5. **Output**: Structured token list

### Token Metadata

Each token includes comprehensive linguistic information:
- **Surface Form**: Exact text as it appears (e.g., "食べた", "食べている", "食べます")
- **Reading**: Pronunciation in katakana
- **Part of Speech**: Detailed grammatical classification
- **Base Form**: Dictionary/lemma form (e.g., "食べる" for all conjugated forms)
- **Normalized Form**: Sudachi's normalized representation
- **Position**: Character offset in original text
- **Features**: Additional morphological features

### Verb Form Normalization

Sudachi automatically provides dictionary forms for all inflected words:
- **Conjugated Verbs**: "食べた" → "食べる", "行きます" → "行く"
- **Adjective Forms**: "美しかった" → "美しい", "大きな" → "大きい"
- **Irregular Forms**: "来た" → "来る", "した" → "する"
- **Compound Verbs**: "食べ始めた" → "食べ始める"

This ensures vocabulary extraction focuses on base forms for effective learning.

## Error Handling

### Error Categories

1. **Initialization Errors**
   - Missing Sudachi installation
   - Dictionary loading failures
   - Configuration issues

2. **Input Validation Errors**
   - File not found or unreadable
   - Encoding issues (non-UTF-8)
   - Empty or invalid input

3. **Processing Errors**
   - Sudachi analysis failures
   - Memory limitations for large files
   - Partial processing failures

### Error Recovery Strategies

- **Graceful Degradation**: Continue processing when individual segments fail
- **Detailed Logging**: Comprehensive error information for debugging
- **User-Friendly Messages**: Clear explanations with suggested solutions
- **Fallback Mechanisms**: Alternative processing for problematic text segments

## Testing Strategy

### Unit Testing Approach

1. **Component Testing**
   - Individual tokenizer methods
   - Filter functionality
   - Data model validation
   - Exception handling paths

2. **Integration Testing**
   - End-to-end file processing
   - Sudachi integration
   - Filter combinations
   - Large file handling

3. **Test Data Strategy**
   - Sample Japanese text files with various scripts
   - Edge cases (mixed languages, special characters)
   - Performance test files (large documents)
   - Malformed input files

### Test Coverage Requirements

- Minimum 90% code coverage
- All error paths tested
- Performance benchmarks for large files
- Memory usage validation

## Implementation Considerations

### Dependencies

- **SudachiPy**: Core tokenization engine
- **SudachiDict**: Japanese dictionary (core or full)
- **pathlib**: File system operations
- **typing**: Type annotations
- **dataclasses**: Data model definitions

### Performance Optimization

- **Lazy Loading**: Initialize Sudachi only when needed
- **Batch Processing**: Process large files in chunks
- **Memory Management**: Clear intermediate results
- **Caching**: Reuse tokenizer instances

### Configuration Management

- **Default Settings**: Sensible defaults for common use cases
- **Environment Variables**: Optional configuration overrides
- **Validation**: Input parameter validation
- **Documentation**: Clear configuration examples

## Integration Points

### With Existing Codebase

- **Import Structure**: Clean module imports following project conventions
- **Type Safety**: Full type hint coverage
- **Error Patterns**: Consistent with existing error handling
- **Logging**: Integration with project logging system
- **Testing**: Follows established testing patterns

### Future Extensions

- **Multiple Languages**: Framework for adding other tokenizers
- **Custom Dictionaries**: Support for domain-specific vocabularies
- **Custom Filters**: Easy addition of new filter implementations via Protocol
- **Filter Composition**: Combining multiple filters with logical operators
- **Performance Monitoring**: Metrics collection for optimization

### Core Usage Examples

```python
# Basic tokenization (MVP functionality)
tokenizer = JapaneseTokenizer()
tokens = tokenizer.tokenize_file(Path("japanese_text.txt"))

# Access token information
for token in tokens:
    print(f"Surface: {token.surface}")
    print(f"Dictionary form: {token.dictionary_form}")
    print(f"Reading: {token.reading}")
    print(f"POS: {token.part_of_speech}")

# Tokenize text directly
text = "今日は良い天気ですね。"
tokens = tokenizer.tokenize_text(text)
```

### Future Filter Usage (Stretch Goals)

```python
# These features will be implemented after core functionality:
# tokenizer.add_filter(ParticleFilter())
# tokenizer.add_filter(LengthFilter(min_length=2))
# tokenizer.set_filters([ParticleFilter(), DuplicationFilter()])
```