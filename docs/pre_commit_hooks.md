# Pre-commit Hooks

This document provides detailed information about the pre-commit hooks used in this project.

## What are Pre-commit Hooks?

Pre-commit hooks are scripts that run automatically before a commit is made. They help ensure that code quality standards are met before code is committed to the repository. This prevents low-quality code from being committed and reduces the need for code review comments about style and formatting issues.

## Hooks Used in This Project

This project uses the following pre-commit hooks:

### Code Quality Hooks

- **trailing-whitespace**: Removes trailing whitespace at the end of lines
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML files
- **check-toml**: Validates TOML files
- **check-added-large-files**: Prevents large files from being committed
- **debug-statements**: Checks for debugger imports and py37+ `breakpoint()` calls
- **check-merge-conflict**: Checks for files that contain merge conflict strings

### Python-specific Hooks

- **black**: Formats Python code according to the Black code style
- **isort**: Sorts Python imports
- **flake8**: Lints Python code for style and potential errors
  - **flake8-docstrings**: Checks docstring conventions
  - **flake8-bugbear**: Finds likely bugs and design problems
- **mypy**: Performs static type checking
- **pyupgrade**: Automatically upgrades Python syntax to newer versions
- **docformatter**: Formats docstrings according to PEP 257
- **autoflake**: Removes unused imports and variables

## Installation

Pre-commit hooks are automatically installed when you run `make dev-install`. You can also install them manually:

```bash
# Using make
make setup-hooks

# Or directly with pre-commit
pre-commit install
```

## Verification

To verify that pre-commit hooks are installed and working correctly:

```bash
# Using make
make verify-hooks

# Or directly
python scripts/verify_hooks.py
```

## Running Hooks Manually

You can run pre-commit hooks manually on all files:

```bash
pre-commit run --all-files
```

Or on specific files:

```bash
pre-commit run --files path/to/file1.py path/to/file2.py
```

## Skipping Hooks

In rare cases, you may need to skip pre-commit hooks. This should be done only in exceptional circumstances:

```bash
git commit -m "Your commit message" --no-verify
```

## Updating Hooks

To update the pre-commit hooks to the latest versions:

```bash
pre-commit autoupdate
```

Then commit the updated `.pre-commit-config.yaml` file.

## CI Integration

The CI pipeline verifies that pre-commit hooks pass for all files in the repository. This ensures that all code in the repository meets the quality standards enforced by the hooks.

## Troubleshooting

If you encounter issues with pre-commit hooks:

1. Make sure you have the latest version of pre-commit installed: `pip install --upgrade pre-commit`
2. Try reinstalling the hooks: `pre-commit uninstall && pre-commit install`
3. Check if your Python environment has all the required dependencies: `pip install -e ".[dev]"`
4. Run the verification script: `python scripts/verify_hooks.py`
