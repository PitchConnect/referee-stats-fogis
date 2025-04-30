I've identified and fixed the issue with the CI checks. The problem was that pyupgrade was expecting Python 3.10+ type hints (using the pipe operator `|` instead of `Optional`, `Dict`, etc.), but we had some files still using the older syntax.

I've run pyupgrade on all Python files to ensure they use the correct syntax for Python 3.10+. This should fix the CI checks.

To catch this issue locally in the future, make sure to run the pyupgrade check as part of the run_checks.sh script:

```bash
pyupgrade --py310-plus $(find referee_stats_fogis tests -name "*.py")
```
