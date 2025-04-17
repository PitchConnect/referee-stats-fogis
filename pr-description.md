# Set up comprehensive CI pipeline

This PR addresses issue #9 by setting up a comprehensive CI pipeline that aligns with our pre-commit hooks.

## Changes

- Updated CI workflow to run on both main and develop branches
- Added all code quality checks that match the pre-commit configuration:
  - black (with --preview flag)
  - isort
  - flake8
  - mypy
  - pyupgrade
  - docformatter
  - autoflake
- Added test coverage reporting with Codecov
- Added build and packaging verification with build and twine
- Added status badges to the README.md
- Added documentation about the relationship between pre-commit hooks and CI checks
- Created a branch protection workflow file

## Testing

The CI pipeline will run automatically when this PR is created, which will validate the changes.

Fixes #9
