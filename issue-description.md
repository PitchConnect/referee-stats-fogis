## Fix failing CI builds

The CI builds are currently failing after the CI pipeline setup. This issue tracks the need to investigate and fix these failures.

### Current Status
- CI builds are failing on both the develop branch and PR builds
- Issue #9 for setting up the CI pipeline has been closed, but the builds are still failing

### Possible Causes
- Package build issues related to the `migrations` directory
- Dependency conflicts
- Configuration issues in the CI workflow

### Next Steps
1. Investigate the specific error messages in the failing builds
2. Fix the identified issues
3. Ensure CI builds pass consistently

This is a follow-up to issue #9 (Set up CI pipeline).
