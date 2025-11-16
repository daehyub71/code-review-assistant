# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Code Review Assistant** is a PySide6 (Qt6) desktop application that provides AI-powered code review across multiple programming languages. It analyzes code against 8 standardized quality categories and generates improvement suggestions using LLM APIs (OpenAI GPT-5 or Anthropic Claude).

**Current Status**: Skeleton project - implementation files are empty. See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for complete specification.

**Key Features**:
- Multi-language support (Phase 1: C#, Java, Python, Vue.js)
- 8-category code analysis framework
- Real-time cost monitoring (token usage + estimated API costs)
- Before/After code editor with syntax highlighting
- Korean-only UI
- Batch file/folder analysis

## Architecture

### Three-Layer Structure

```
┌─────────────────────────────────────┐
│  Presentation Layer (PySide6)       │
│  - app/ui/main_window.py            │
│  - app/ui/language_selector.py      │
│  - app/ui/cost_monitor.py           │
│  - app/ui/before_after_editor.py    │
│  - app/ui/result_panel.py           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Business Logic Layer               │
│  - app/core/prompt_builder.py       │
│    (loads language-specific prompts)│
│  - app/core/batch_analyzer.py       │
│  - app/core/report_generator.py     │
│  - app/core/cost_calculator.py      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  API Integration Layer              │
│  - app/core/api_client.py           │
│    (OpenAI/Claude streaming)        │
│  - app/utils/token_counter.py       │
│    (tiktoken for cost estimation)   │
└─────────────────────────────────────┘
```

### Review Category System

The core design uses **8 standardized categories** that map differently per language:

1. **Null/Undefined Safety**: C# `?.`, Java `Optional<T>`, Python type hints, Vue optional chaining
2. **Exception/Error Handling**: try-catch patterns, specific exception types
3. **Resource Management**: C# `using`, Java try-with-resources, Python `with`, Vue cleanup hooks
4. **Performance Optimization**: Language-specific idioms (LINQ, Stream API, comprehensions, computed properties)
5. **Security Best Practices**: SQL injection, XSS, input validation
6. **Naming Conventions**: PascalCase/camelCase/snake_case per language standards
7. **Code Documentation**: XML comments, JavaDoc, docstrings, JSDoc
8. **Configuration Management**: appsettings.json, .properties, .env files

**Template Structure**:
```
resources/templates/review_categories/
├── csharp/
│   ├── null_reference.md
│   ├── exception_handling.md
│   ├── resource_management.md
│   ├── performance.md
│   ├── security.md
│   ├── naming_convention.md
│   ├── code_documentation.md
│   └── hardcoding_to_config.md
├── java/
├── python/
└── vue/
```

Each template contains language-specific review guidance for that category.

### Language Configuration System

Language metadata is stored in YAML files:

```
resources/languages/
├── csharp.yaml
├── java.yaml
├── python.yaml
└── vue.yaml
```

Each YAML defines:
- `display_name`: UI label (e.g., "C#", "Java")
- `file_extensions`: [".cs", ".csproj"] or [".java"] etc.
- `comment_style`: "//" or "#"
- `doc_style`: "///" or "/**/" or `"""` or "/** */"
- `keywords`: Language-specific keywords for syntax highlighting

**Loading**: `app/models/language.py` → `LanguageConfig.load(Language.PYTHON)` reads YAML

## Development Commands

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Main entry point
python app/main.py
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_prompt_builder.py -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run UI tests (requires pytest-qt)
pytest tests/test_language_selector.py -v
```

### Environment Variables

Create `.env` file (see `.env.example`):

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-mini  # or gpt-4o-mini

# Anthropic (alternative)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku

# Cost monitoring
USD_TO_KRW_RATE=1340  # Exchange rate for cost display
DAILY_BUDGET_USD=10.00  # Optional daily spending limit
```

## Key Design Decisions

### 1. Single Language Per Session
- User explicitly selects one language via dropdown (no auto-detection)
- Batch folder analysis assumes all files are the same language
- Simplifies prompt construction and avoids mixed-language confusion

### 2. Cost-First Design
- Real-time token counting using `tiktoken` (debounced 500ms)
- Display both USD and KRW costs before API call
- Track historical costs in SQLite (`app/db/report_history.py`)
- Optional budget warnings/limits

### 3. Template-Based Prompts
- No hardcoded prompts in Python code
- All review guidance in Markdown templates (`resources/templates/`)
- `PromptBuilder` dynamically assembles prompts from templates based on selected language + enabled categories
- Easy to add new languages without touching code

### 4. PySide6 (Qt6) for Desktop
- Native desktop performance (vs. Electron)
- Rich text editing with Pygments syntax highlighting
- Professional UI controls (QComboBox, QTextEdit, QSplitter)
- Cross-platform (macOS, Windows, Linux)

### 5. Streaming API Responses
- Use OpenAI/Claude streaming for real-time feedback
- Update result panel incrementally as LLM generates response
- Better UX for long reviews (3-5 seconds typical)

## Implementation Priorities

### Phase 1: Core Features (Current)
**Focus**: Get C#, Java, Python, Vue working with cost monitoring

**Critical Path**:
1. Implement `app/models/language.py` (Language enum + LanguageConfig loader)
2. Create YAML configs for 4 languages in `resources/languages/`
3. Write 8 category templates per language (32 Markdown files total)
4. Implement `app/core/cost_calculator.py` (token counting + pricing)
5. Build `app/ui/language_selector.py` (QComboBox widget)
6. Build `app/ui/cost_monitor.py` (status bar with token/cost display)
7. Implement `app/core/prompt_builder.py` (template assembly)
8. Implement `app/core/api_client.py` (OpenAI/Claude streaming)
9. Wire up main window (`app/ui/main_window.py`)

**Testing Checkpoints**:
- Language selector correctly maps dropdown to `Language` enum
- Cost calculator accurately counts tokens (test with known strings)
- Prompt builder loads correct templates based on language
- API client successfully streams responses
- UI updates cost estimate on code input (debounced)

### Phase 2-3: Expansion
- See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for TypeScript, Go, React, framework-specific reviews

## Working with Templates

### Template Naming Convention

Templates must match this exact pattern:
```
resources/templates/review_categories/{language}/{category}.md
```

Where:
- `{language}` = Language.value ("csharp", "java", "python", "vue")
- `{category}` = snake_case category name

**Correct**:
- `resources/templates/review_categories/python/null_reference.md` ✓
- `resources/templates/review_categories/java/exception_handling.md` ✓

**Incorrect**:
- `resources/templates/python/NullReference.md` ✗ (wrong path depth)
- `resources/templates/review_categories/Python/null_reference.md` ✗ (capitalized language)

### Template Format

Each template should be Markdown with this structure:

```markdown
# {Category Name} - {Language}

## What to Check
- Specific patterns to look for
- Common mistakes in this language

## Best Practices
- Recommended approaches
- Language-specific idioms

## Example

**Before**:
```{language}
// Bad code example
```

**After**:
```{language}
// Improved code example
```

## References
- Language documentation links
- Style guide references
```

### Loading Templates in Code

```python
from app.models.language import Language

def load_template(language: Language, category: str) -> str:
    """Load review template for given language and category"""
    path = f"resources/templates/review_categories/{language.value}/{category}.md"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
```

## Database Schema

SQLite database for review history (`app/db/report_history.py`):

```sql
CREATE TABLE review_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    language TEXT NOT NULL,           -- "csharp", "java", etc.
    model TEXT NOT NULL,               -- "gpt-5-mini", "claude-3-5-haiku"
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_cost_usd REAL,
    file_count INTEGER DEFAULT 1,
    enabled_categories TEXT,           -- JSON array: ["null_reference", "security"]
    report_path TEXT                   -- Path to saved .md report
);
```

**Query Examples**:
```sql
-- Daily spending
SELECT DATE(timestamp) as date, SUM(total_cost_usd) as cost
FROM review_history
WHERE timestamp >= DATE('now', '-7 days')
GROUP BY DATE(timestamp);

-- Most expensive reviews
SELECT timestamp, language, file_count, total_cost_usd
FROM review_history
ORDER BY total_cost_usd DESC
LIMIT 10;
```

## Performance Targets

- **Single file analysis**: 3-5 seconds (using gpt-5-mini)
- **Token counting**: <100ms (debounced UI updates)
- **UI responsiveness**: 60 FPS (Qt6 performance)
- **Batch 10 files**: 30-60 seconds (parallel API calls if possible)
- **Memory usage**: <500MB

## Testing Strategy

### Unit Tests
- `tests/test_language_selector.py`: Language enum mapping
- `tests/test_cost_calculator.py`: Token counting accuracy, cost calculations
- `tests/test_prompt_builder.py`: Template loading, prompt assembly
- `tests/test_api_client.py`: Mock API responses, streaming

### Integration Tests
- End-to-end: Select language → Load code → Analyze → Verify report format
- Cost tracking: Verify SQLite inserts after each analysis
- Batch processing: Multiple files, single language, correct cost aggregation

### UI Tests (pytest-qt)
- Language selector widget: Dropdown selection triggers correct Language enum
- Cost monitor: Updates on text input, displays correct KRW conversion
- Before/After editor: Syntax highlighting changes when language switches

## Common Pitfalls

### 1. Language Case Sensitivity
**Wrong**:
```python
Language("Python")  # ValueError: "Python" not in enum
```
**Correct**:
```python
Language.PYTHON  # Use enum directly
# or
Language("python")  # Lowercase string value
```

### 2. Template Path Construction
**Wrong**:
```python
path = f"resources/templates/{language}/{category}.md"  # Missing review_categories/
```
**Correct**:
```python
path = f"resources/templates/review_categories/{language.value}/{category}.md"
```

### 3. Token Counting for Non-OpenAI Models
`tiktoken` only works for OpenAI models. For Claude:
```python
# Use anthropic's tokenizer
from anthropic import Anthropic
client = Anthropic()
tokens = client.count_tokens(text)
```

### 4. UI Thread Blocking
API calls take 3-5 seconds. Always use QThread or async:
```python
# Wrong: Blocks UI
response = openai_client.chat.completions.create(...)

# Correct: Use QThread
class AnalysisWorker(QThread):
    def run(self):
        response = openai_client.chat.completions.create(...)
        self.finished.emit(response)
```

## Reference Project

This architecture is based on: https://github.com/daehyub71/csharp-code-reviewer-api

Key differences:
- Desktop app (PySide6) vs. FastAPI server
- Multi-language vs. C#-only
- Cost monitoring (new feature)
- Template-based prompts vs. hardcoded

## File Naming Conventions

- **Python modules**: `snake_case.py` (e.g., `cost_calculator.py`)
- **Classes**: `PascalCase` (e.g., `CostCalculator`, `LanguageConfig`)
- **Functions/methods**: `snake_case` (e.g., `count_tokens()`, `load_template()`)
- **UI widgets**: `PascalCase` + `Widget` suffix (e.g., `LanguageSelectorWidget`)
- **Test files**: `test_{module}.py` (e.g., `test_cost_calculator.py`)
- **Templates**: `{category_name}.md` in lowercase snake_case
- **YAML configs**: `{language}.yaml` in lowercase

## Documentation

- **Project Plan**: [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) - Complete specification
- **README.md**: User-facing setup and usage instructions
- **This file**: Developer guidance for Claude Code

When implementing features, always check PROJECT_PLAN.md for detailed specifications (UI mockups, data models, week-by-week milestones).
