# Referee Stats FOGIS

A tool to track and analyze referee statistics from FOGIS.

## Features (Planned)

- Fetch all matches refereed
- Track statistics about co-referees, players, cards, goals, etc.
- Generate reports and insights

## Development

This project uses a comprehensive set of tools to ensure code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing
- **pre-commit**: Git hooks

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

## License

MIT
