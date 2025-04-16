# Contributing to Referee Stats FOGIS

Thank you for considering contributing to Referee Stats FOGIS! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/referee-stats-fogis.git`
3. Create a virtual environment: `python -m venv .venv`
4. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
5. Install development dependencies: `make dev-install` or `pip install -e ".[dev]"`
6. Install pre-commit hooks: `pre-commit install`

## Development Workflow

1. Create a new branch for your feature or bugfix: `git checkout -b feature-name`
2. Make your changes
3. Run the tests: `make test` or `pytest`
4. Format your code: `make format` or `black . && isort .`
5. Run linting checks: `make lint` or `flake8 referee_stats_fogis tests && mypy referee_stats_fogis`
6. Commit your changes: `git commit -m "Description of changes"`
7. Push your branch: `git push origin feature-name`
8. Create a pull request

## Code Style

This project follows these code style guidelines:

- [Black](https://black.readthedocs.io/en/stable/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [flake8](https://flake8.pycqa.org/en/latest/) for linting
- [mypy](https://mypy.readthedocs.io/en/stable/) for type checking

The pre-commit hooks will automatically check and fix many style issues when you commit.

## Testing

All new features should include tests. Run the tests with:

```bash
pytest
```

## Documentation

Please update the documentation when adding or modifying features. Documentation is written in Markdown and should be clear and concise.

## Pull Request Process

1. Ensure your code passes all tests and linting checks
2. Update the documentation if necessary
3. Update the README.md if necessary
4. The pull request will be reviewed by maintainers
5. Address any feedback from the review
6. Once approved, your pull request will be merged

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.
