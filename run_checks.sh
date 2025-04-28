#!/bin/bash
# Run all CI checks locally

set -e

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc) -eq 1 ]]; then
    echo "Error: This project requires Python 3.10 or higher. You are using Python $PYTHON_VERSION."
    echo "Please use a compatible Python version to run these checks."
    exit 1
fi

echo "Running flake8..."
flake8 referee_stats_fogis tests

echo "Running black..."
black --check --preview referee_stats_fogis tests

echo "Running isort..."
isort --check referee_stats_fogis tests

echo "Running mypy..."
mypy --config-file=.mypy.ini referee_stats_fogis

echo "Running pyupgrade..."
pyupgrade --py310-plus $(find referee_stats_fogis tests -name "*.py")

echo "Running docformatter..."
docformatter --check --wrap-summaries=88 --wrap-descriptions=88 $(find referee_stats_fogis tests -name "*.py")

echo "Running autoflake..."
autoflake --check --remove-all-unused-imports --remove-unused-variables --expand-star-imports --remove-duplicate-keys $(find referee_stats_fogis tests -name "*.py")

echo "All checks passed!"
