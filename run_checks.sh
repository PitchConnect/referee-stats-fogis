#!/bin/bash
# Run all CI checks locally

set -e

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
