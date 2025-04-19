# Fix CI build issues

This PR addresses issue #11 by fixing the CI build issues that were occurring after setting up the CI pipeline.

## Changes

1. **Fixed package build issues**:
   - Added explicit exclusion of the `migrations` directory in `pyproject.toml`
   - Created a `MANIFEST.in` file to exclude migrations and tests from the package
   - Added package-data and exclude-package-data configurations

2. **Updated CI workflow**:
   - Simplified the dependency installation process
   - Added a verification step to ensure migrations are excluded
   - Fixed the build and test process

3. **Updated dependencies**:
   - Aligned dev dependencies in `pyproject.toml` with what's being used in the CI workflow
   - Added specific version requirements for all dev dependencies

## Testing

The CI pipeline should now run successfully on this PR, which will validate the changes.

Fixes #11
