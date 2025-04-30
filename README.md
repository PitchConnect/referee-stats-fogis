# Referee Stats FOGIS

[![CI](https://github.com/timmybird/referee-stats-fogis/actions/workflows/ci.yml/badge.svg)](https://github.com/timmybird/referee-stats-fogis/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/timmybird/referee-stats-fogis/branch/main/graph/badge.svg)](https://codecov.io/gh/timmybird/referee-stats-fogis)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tool to track and analyze referee statistics from FOGIS.

## Features (Planned)

- Fetch all matches refereed
- Track statistics about co-referees, players, cards, goals, etc.
- Generate reports and insights
- Import data from FOGIS (see [Data Import Documentation](docs/data_import.md))

## Development

This project uses a comprehensive set of tools to ensure code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing
- **pre-commit**: Git hooks (see [Pre-commit Hooks Documentation](docs/pre_commit_hooks.md))
- **pyupgrade**: Python syntax upgrader
- **docformatter**: Docstring formatter
- **autoflake**: Removes unused imports and variables

### Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`
5. Install pre-commit hooks: `pre-commit install`

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Run linting
flake8

# Run type checking
mypy .
```

### Pre-commit Hooks and CI Pipeline

This project uses pre-commit hooks and a CI pipeline to ensure code quality. The pre-commit hooks run locally before each commit, while the CI pipeline runs on GitHub Actions for pull requests and pushes to main and develop branches.

#### Installing and Using Pre-commit Hooks

Pre-commit hooks are automatically installed when you run `make dev-install`. You can also install them manually:

```bash
# Install pre-commit hooks
make setup-hooks

# Or directly with pre-commit
pre-commit install
```

To verify that pre-commit hooks are installed and working correctly:

```bash
# Verify pre-commit hooks
make verify-hooks

# Or run directly
python scripts/verify_hooks.py
```

To run pre-commit hooks on all files (useful before pushing changes):

```bash
pre-commit run --all-files
```

#### Relationship Between Pre-commit Hooks and CI Checks

The CI pipeline is configured to run the same checks as the pre-commit hooks, ensuring consistency between local development and CI environments. This alignment provides several benefits:

1. **Efficiency**: Issues are caught early in the development process, reducing the need for CI resources.
2. **Consistency**: Developers see the same results locally as they would in CI.
3. **Developer Experience**: Pre-commit hooks catch all issues that the CI would catch, preventing surprises.

If you need to update either the pre-commit hooks or CI checks, make sure to update both to maintain this alignment.

## License

MIT
