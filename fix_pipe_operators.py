#!/usr/bin/env python3
"""Script to replace pipe operators with Union types for Python 3.9 compatibility."""

import os
import re
import sys

# Regular expression to match type annotations with pipe operators
# This regex looks for type annotations like "Type1 | Type2" or "Type1 | Type2 | None"
PIPE_REGEX = r"(\w+(?:\[\w+\])?) *\| *(\w+(?:\[\w+\])?)(?: *\| *(\w+(?:\[\w+\])?))?"


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def fix_file(file_path: str) -> Tuple[int, List[str]]:
    """Fix pipe operators in the given file.

    Returns:
        Tuple containing the number of replacements made and a list of the replacements.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Find all instances of pipe operators in type annotations
    matches = re.finditer(
        r"(\w+(?:\[\w+\])?) *\| *(\w+(?:\[\w+\])?)(?: *\| *(\w+(?:\[\w+\])?))?", content
    )

    replacements = []
    replacement_count = 0

    # Process each match
    for match in matches:
        # Get the matched types
        types = [t for t in match.groups() if t is not None]

        # Create the Union replacement
        if len(types) == 2:
            replacement = f"Union[{types[0]}, {types[1]}]"
        elif len(types) == 3:
            replacement = f"Union[{types[0]}, {types[1]}, {types[2]}]"
        else:
            continue

        # Add to replacements list
        replacements.append((match.group(0), replacement))
        replacement_count += 1

    # Apply replacements in reverse order to avoid messing up indices
    for old, new in reversed(replacements):
        content = content.replace(old, new)

    # Add Union import if needed
    if replacement_count > 0 and "from typing import Union" not in content:
        # Check if there's already a typing import
        typing_import_match = re.search(r"from typing import (.*)", content)
        if typing_import_match:
            # Add Union to existing typing import
            existing_imports = typing_import_match.group(1)
            if "Union" not in existing_imports:
                if existing_imports.endswith(","):
                    new_imports = f"{existing_imports} Union"
                else:
                    new_imports = f"{existing_imports}, Union"
                content = content.replace(
                    typing_import_match.group(0), f"from typing import {new_imports}"
                )
        else:
            # Add new typing import at the top of the file
            content = "from typing import Union\n" + content

    # Write the modified content back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return replacement_count, [f"{old} -> {new}" for old, new in replacements]


def main() -> None:
    """Main function."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    python_files = find_python_files(directory)
    total_replacements = 0

    for file_path in python_files:
        replacements, replacement_list = fix_file(file_path)
        if replacements > 0:
            print(f"Fixed {replacements} pipe operators in {file_path}")
            for replacement in replacement_list:
                print(f"  {replacement}")
            total_replacements += replacements

    print(f"\nTotal replacements: {total_replacements}")


if __name__ == "__main__":
    main()
