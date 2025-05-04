# Python Version Support

## Supported Python Versions

This project requires Python 3.10 or higher. We have officially abandoned support for Python 3.9 and below.

### Why Python 3.10+?

Python 3.10 introduced several features that improve code quality and developer experience:

1. **Union Type Operator (`|`)**: Allows for more concise type hints
   ```python
   # Python 3.10+
   def process(value: str | int) -> None: ...

   # Python 3.9 and below
   from typing import Union
   def process(value: Union[str, int]) -> None: ...
   ```

2. **Pattern Matching**: Provides a more elegant way to handle complex conditional logic
3. **Better Error Messages**: Improved error messages help with debugging
4. **Performance Improvements**: General performance enhancements

### Configuration

The project is configured to require Python 3.10+ in the following ways:

1. In `pyproject.toml`:
   ```toml
   [project]
   requires-python = ">=3.10"
   ```

2. In CI workflow (`.github/workflows/ci.yml`):
   ```yaml
   strategy:
     matrix:
       python-version: ['3.10', '3.11', '3.12']
   ```

3. In Black configuration:
   ```toml
   [tool.black]
   target-version = ["py310", "py311", "py312"]
   ```

## Future Python Support

As new Python versions are released, we will evaluate adding support for them while maintaining backward compatibility with Python 3.10 for a reasonable period.
