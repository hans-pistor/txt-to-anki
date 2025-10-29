# TXT-to-Anki Sentence Card Generator Specification

## 1. Vision & Goals
- **Primary Objective:** Transform a long-form plain-text book into a curated Anki deck composed of sentence cards suitable for language learning.
- **User Value:** Enable learners to mine example sentences from novels or other texts, optionally enrich them with metadata (translations, vocabulary focus), and export them into Anki with minimal manual effort.
- **Scope (MVP):**
  - Accept UTF-8 (and detect/convert other encodings) `.txt` books.
  - Segment text into clean sentences.
  - Filter/select sentences according to configurable rules.
  - Produce an Anki `.apkg` deck (using `genanki` or similar) with basic fields (Expression, Meaning/Notes, Source).
- **Out of Scope (initially):**
  - OCR, PDF parsing, or image-based books.
  - Automatic audio generation.
  - Fully automated human-quality translations (may rely on external APIs or placeholders).

## 2. User Stories
1. **Sentence Miner:** “As a language learner, I want to import a text file and get a deck where each card shows a sentence from the book so I can study them in Anki.”
2. **Curator:** “As a user, I want to adjust filtering rules (length, vocabulary, frequency) to avoid overly long or trivial sentences.”
3. **Annotator:** “As a bilingual reader, I want to add manual translations or glosses to individual sentences before export.”
4. **Batch Processor (stretch):** “As a power user, I want to process multiple books at once and generate separate decks.”

## 3. Functional Requirements
### Input Handling
- Accept file path via CLI.
- Detect encoding (`chardet`/`charset-normalizer`), normalize to UTF-8, strip BOM.
- Optional metadata via CLI/config (`--title`, `--author`, `--language`, `--source-url`).

### Preprocessing
- Normalize whitespace (collapse consecutive spaces, unify line endings).
- Remove Project Gutenberg headers/footers or similar boilerplate (configurable regex templates).

### Sentence Segmentation
- Support language-specific sentence splitting:
  - Default: punctuation-based splitter (`nltk`, `syntok`, or `sentence-splitter`).
  - Japanese & Chinese: integrate `fugashi`/`nagisa` or `sudachipy` for sentence boundary detection without spaces.
- Expose segmentation module as interface so new languages can plug in.

### Sentence Filtering
- Configurable min/max character length.
- Deduplicate sentences (exact or fuzzy).
- Exclude sentences containing blacklisted patterns (e.g., formatting artifacts).
- Optional frequency-based selection (e.g., keep sentences with target vocabulary list).

### Metadata Enrichment
- Optional translation field:
  - CLI flags for manual import (`--translations-file`) or API-based generation (pluggable translator interface; stub for MVP).
- Source metadata: chapter/line numbers if derivable, otherwise fallback to sequential index.
- Optional keywords/glosses via morphological analyzer (stretch goal).

### Deck Assembly
- Card model fields: `Expression`, `Meaning/Notes`, `Source`.
- Template: Front shows sentence; Back shows translation/notes plus source info.
- Tagging: auto-tag with book title, language, optional user tags.
- Export deck to `.apkg`; optionally emit intermediary CSV/TSV.

### CLI UX
- Command: `txt_to_anki build [OPTIONS] <input.txt>`
- Options for output path, config file, dry-run preview, sentence limit, random sampling, logging verbosity.
- Progress reporting (e.g., sentence count, filtered count).

### Configuration
- Support global/local YAML config overriding defaults (language, filters, translator settings).
- Allow CLI flags to override config values.

## 4. System Architecture

```
+-------------------+
| CLI / Entry Point |
+-------------------+
          |
          v
+-------------------+      +------------------+
| Config Manager    | ---> | Language Profiles|
+-------------------+      +------------------+
          |
          v
+-------------------+
| Pipeline Orchestrator |
+-------------------+
   | ingest -> preprocess -> segment -> filter -> enrich -> export
```

### Key Modules
1. `cli/` – Click/Typer command definitions, config loading.
2. `config/` – Schema definitions, validation (pydantic/dataclasses).
3. `ingest/reader.py` – File loading, encoding normalization.
4. `preprocess/cleaner.py` – Whitespace normalization, boilerplate removal.
5. `segmenter/base.py` – Abstract interface; language-specific implementations in `segmenter/`.
6. `filters/` – Reusable sentence filter classes (length, blacklist, dedupe).
7. `enrich/` – Translators, glossers, metadata builders.
8. `deck/exporter.py` – `genanki` deck creation, ID management, asset bundling.
9. `logging/` – Structured logging (rich/loguru optional).
10. `data/models.py` – Sentence record dataclass (fields: id, text, source_ref, notes, tags).

## 5. Data Model

```python
@dataclass
class SentenceCard:
    uid: str                  # stable hash of sentence + source
    sentence: str
    translation: Optional[str]
    notes: Optional[str]
    source_ref: Optional[str] # chapter/page/line
    tags: Set[str]
```

Config schema example:

```yaml
language: ja
filters:
  min_chars: 15
  max_chars: 120
  blacklist_regex:
    - '^\d+$'
segmenter: 'ja_default'
translator:
  provider: 'deepl'
  api_key_env: 'DEEPL_API_KEY'
anki:
  deck_name: 'Book Title (Sentences)'
  model_name: 'Txt2Anki Sentence'
  tags:
    - 'txt-to-anki'
```

## 6. Algorithmic Details
- **Sentence ID Generation:** Use stable hashing (e.g., SHA-1 of normalized sentence + source id) to avoid duplicates across runs.
- **Dedupe Strategy:** Maintain set of hashes; optionally allow fuzzy dedupe via `rapidfuzz` ratio threshold.
- **Boilerplate Removal:** Provide library of regex templates (Project Gutenberg, AO3, etc.); allow user-supplied patterns.
- **Language Profiles:** Each profile defines segmentation strategy, default filters, optional morphological analyzer (e.g., Japanese uses sentence-splitter via `fugashi` and can compute `source_ref` using line numbers).
- **Translation Hook:** Provide synchronous and async interface; default to `None` (manual). Add caching to avoid repeated API calls.

## 7. Error Handling & Logging
- Raise descriptive errors for unsupported encodings, missing dependencies.
- Validate config (type, value ranges) before pipeline start.
- Log pipeline steps with counts (e.g., “Segmented 5,200 sentences; 3,450 retained after filtering”).
- Provide `--strict` (fail on warnings) vs `--relaxed` (skip problematic sentences).

## 8. Testing Strategy
- **Unit Tests:**  
  - Sentence segmentation per language (fixtures with expected splits).  
  - Filter behaviors (length, blacklist).  
  - Exporter ensures `.apkg` file contains expected cards (mock `genanki`).  
  - Config parsing & overrides.
- **Integration Tests:**  
  - End-to-end run on small fixture text (English & Japanese).  
  - CLI invocation using `pytest` + `click.testing`/`typer.testing`.
- **Property-Based Tests (stretch):**  
  - Hypothesis to ensure dedupe and filtering behave over random text.

## 9. Tooling & Dependencies
- Python ≥ 3.11.
- Libraries:
  - `typer`/`click` for CLI.
  - `pydantic` or `pydantic-settings` for config.
  - `sentence-splitter`, `fugashi`, `nagisa`, or `spaCy` depending on language.
  - `genanki` for deck export.
  - `charset-normalizer` for encoding detection.
  - `rapidfuzz` for fuzzy dedupe (optional).
  - `rich` for progress/logging.
- Packaging: `poetry` or `uv` for dependency management (decide during implementation).
- Linting/formatting: `ruff`, `black`, `mypy`.

## 10. Milestones
1. **M1 – Text Pipeline Skeleton**
   - CLI scaffolding, config parsing, plain English segmentation, simple filters, CSV export.
2. **M2 – Anki Export**
   - Integrate `genanki`, produce `.apkg`, add source metadata.
3. **M3 – Language Profiles**
   - Add Japanese support (furigana-friendly segmentation), profile abstraction.
4. **M4 – Enhancements**
   - Translation hooks, deck previews, random sampling, frequency filtering.
5. **M5 – Polishing**
   - Comprehensive tests, documentation, packaging, CI.

## 11. Documentation
- Update README with usage examples, CLI reference, config templates.
- Provide sample configs and example decks in `examples/`.
- Add developer guide covering architecture, testing, contribution workflow.

## 12. Future Extensions
- Web UI for interactive review of sentences before exporting.
- Audio synthesis (Text-to-Speech) integration.
- AnkiConnect sync instead of `.apkg`.
- Support for other input formats (EPUB, Markdown).
- Vocabulary-focused card generation (cloze deletions, highlight target words).

---

## Testing
- No automated tests were executed for this planning task.
