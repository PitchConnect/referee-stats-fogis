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

## Git Workflow (Gitflow)

This project follows the [Gitflow](https://nvie.com/posts/a-successful-git-branching-model/) branching model:

- `main` - Production-ready code
- `develop` - Latest development changes
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation
- `hotfix/*` - Urgent fixes for production

### Initial Setup for Gitflow

If you're setting up a new repository or working with a repository that doesn't have a develop branch yet:

```bash
# Create develop branch from main
git checkout main
git checkout -b develop
git push -u origin develop
```

### Development Workflow

1. Create a new branch from `develop` for your feature or bugfix:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

2. Make your changes
3. Run the tests: `make test` or `pytest`
4. Format your code: `make format` or `black . && isort .`
5. Run linting checks: `make lint` or `flake8 referee_stats_fogis tests && mypy referee_stats_fogis`
6. Commit your changes: `git commit -m "Description of changes"`
7. Push your branch: `git push origin feature/your-feature-name`
8. Create a pull request against the `develop` branch
9. Link the pull request to any related issues using keywords like "Fixes #123" or "Resolves #456"

## Code Style

This project follows these code style guidelines:

- [Black](https://black.readthedocs.io/en/stable/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [flake8](https://flake8.pycqa.org/en/latest/) for linting
- [mypy](https://mypy.readthedocs.io/en/stable/) for type checking

The pre-commit hooks will automatically check and fix many style issues when you commit.

### Docstrings

All modules, classes, and functions should have docstrings. This project follows the [Google style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) format.

**Module Docstrings:**
```python
"""Module description.

Detailed description of the module's purpose and functionality.
"""
```

**Function/Method Docstrings:**
```python
def function_name(param1: type, param2: type) -> return_type:
    """Short description of the function.

    More detailed description of what the function does and any
    important information about its behavior.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of the return value

    Raises:
        ExceptionType: When and why this exception is raised
    """
```

**Class Docstrings:**
```python
class ClassName:
    """Short description of the class.

    More detailed description of what the class does and any
    important information about its behavior.

    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2
    """
```

Type hints should be used in conjunction with docstrings to provide complete documentation of code behavior.

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
4. Make sure your PR references any related issues (e.g., "Fixes #123")
5. The pull request will be reviewed by maintainers
6. Address any feedback from the review
7. Once approved, your pull request will be merged
8. After merging, delete your feature branch

## Working with Issues

1. **Task Tracking**:
   - Issues contain task lists with checkboxes `- [ ]` for tracking progress
   - Update these checkboxes as you complete tasks by editing the issue
   - This provides clear visibility of progress for all contributors

2. **Issue References**:
   - Always reference the issue you're working on in commit messages (e.g., "#123: Implement database models")
   - When creating branches, include the issue number (e.g., `feature/123-database-models`)

3. **Issue Updates**:
   - Provide regular updates on issues you're working on
   - If you encounter blockers, document them in the issue

## Guidelines for AI Agents

If you're an AI agent contributing to this project, please follow these additional guidelines:

1. **Issue and Branch Management**:
   - Always reference issues in your PRs using keywords like "Fixes #123" or "Resolves #456"
   - When replacing a PR with another one, reference both the issue and the PR being replaced
   - Close issues automatically through PR merges when possible
   - Delete branches after merging to keep the repository clean
   - Update task checkboxes in issues as you complete them

2. **Markdown Handling**:
   - For complex markdown content (PR descriptions, issue templates, etc.), create temporary markdown files and use them as input
   - Use commands like `gh pr create --title "Title" --body-file pr-description.md`
   - Remove these temporary markdown files after use to avoid cluttering the workspace
   - Example workflow:
     ```bash
     # Create a temporary markdown file
     echo "# PR Description\n\nThis PR implements feature X.\n\nFixes #123" > pr-description.md

     # Use it with the GitHub CLI
     gh pr create --title "Implement feature X" --body-file pr-description.md

     # Clean up
     rm pr-description.md
     ```

3. **Communication**:
   - Clearly state what you're doing and why in commit messages and PR descriptions
   - When replacing or closing PRs, explain the reason for doing so
   - Always check CONTRIBUTING.md (this document) for project-specific guidelines

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.
