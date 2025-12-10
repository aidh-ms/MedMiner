# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MedMiner leverages large language models (LLMs) and LangGraph to extract and analyze data from medical documents. The project uses a workflow-based architecture to process doctor's letters and extract structured medical information (e.g., medications, diagnoses).

## Development Environment

This project uses a dev container with all necessary tools pre-configured. Use VS Code's "Reopen in Container" feature to get started.

**Package Manager**: `uv` (modern Python package manager)

## Common Commands

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run a single test file
uv run pytest tests/test_file.py

# Run a specific test function
uv run pytest tests/test_file.py::test_function_name
```

### Code Quality
```bash
# Format and lint code
uv run ruff check --fix

# Type checking
uv run ty check

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Documentation
```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## Architecture

### Workflow System

MedMiner uses a **LangGraph-based workflow architecture** where each extraction task is implemented as a compiled state graph with sequential node processing:

1. **Base Workflow** ([src/medminer/workflows/base/workflow.py](src/medminer/workflows/base/workflow.py))
   - `BaseWorkflow`: Abstract base for all workflows
   - `BaseExtractionWorkflow`: Template for extraction tasks, builds a graph with: Extraction → Processing Node(s) → Storage

2. **State Management** ([src/medminer/workflows/base/schema.py](src/medminer/workflows/base/schema.py))
   - `DoctorsLetterState`: Base state with patient_id and letter text
   - `ExtractuionState`: Generic extraction state tracking raw/processed data and output path
   - States are TypedDict subclasses passed through the graph

3. **Node Types** ([src/medminer/workflows/base/node.py](src/medminer/workflows/base/node.py))
   - `InformationExtractor`: Uses LLM with structured output to extract data from text
   - `BaseNode` subclasses: Custom processing nodes (e.g., RxNavLookup for medication enrichment)
   - `DataStorage`: Final node that writes processed data to CSV

### Creating New Workflows

To add a new extraction workflow (e.g., for diagnoses, procedures):

1. Create a new directory under [src/medminer/workflows/](src/medminer/workflows/) (e.g., `diagnoses/`)
2. Define schemas in `schema.py`:
   - Raw extracted data TypedDict
   - Processed data TypedDict (if different from raw)
   - State class extending `ExtractuionState`
   - Response format extending `ResponseFormat`
3. Implement processing nodes in `node.py` by subclassing `BaseNode`
4. Create workflow in `workflow.py`:
   - Subclass `BaseExtractionWorkflow`
   - Set `task_name`, `state_type`, `prompt`, `response_format`
   - Add custom `process_nodes` if needed (default is `NoProcessing`)

**Example**: See [src/medminer/workflows/medications/](src/medminer/workflows/medications/) for a complete implementation that extracts medications and enriches them with RxNorm/ATC codes.

### Settings System

[src/medminer/settings.py](src/medminer/settings.py) provides a singleton `Settings` class (cached) for runtime configuration:
- `register(key, value)`: Set configuration
- `get(key, default)`: Retrieve configuration
- Used for base_dir, split_patient flag, etc.

### Model Configuration

[src/medminer/utils/models.py](src/medminer/utils/models.py) handles LLM provider configuration via environment variables:
- Reads `{PROVIDER}_*` env vars (e.g., `OPENAI_API_KEY`, `OPENAI_MODEL`)
- Currently supports OpenAI provider
- Returns model parameters as dict

## Code Style

- **Line length**: 120 characters
- **Python version**: 3.13+
- **Formatting**: Ruff (similar to Black)
- **Type hints**: Required for all function definitions (mypy strict mode)
- **String quotes**: Double quotes

## Testing Notes

- Test files go in [tests/](tests/) directory
- Use `pytest` with coverage enabled
- Pytest cache and pytest itself configured in [pyproject.toml](pyproject.toml)
- Coverage reports generated as XML to `coverage.xml`

## Dependencies

Key dependencies:
- **LangChain/LangGraph**: LLM orchestration and graph-based workflows
- **Pandas**: Data processing and CSV output
- **Gradio**: UI components (in [src/medminer/ui/](src/medminer/ui/))
- **httpx**: HTTP client for external APIs (e.g., RxNav)

See [pyproject.toml](pyproject.toml) for complete dependency list.
