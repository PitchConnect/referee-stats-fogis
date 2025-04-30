#!/usr/bin/env python3
"""Verify that pre-commit hooks are installed and working.

This script checks if pre-commit is installed and if the hooks are properly set up.
It's meant to be run as part of the CI pipeline to ensure that developers have
pre-commit hooks installed and that they're working correctly.
"""

import os
import sys
from pathlib import Path


def check_pre_commit_installed() -> bool:
    """Check if pre-commit is installed."""
    try:
        # Try to import pre-commit
        pass

        # Get version using sys.executable since the module doesn't expose it directly
        try:
            import subprocess as sp

            result = sp.run(
                [sys.executable, "-m", "pip", "show", "pre-commit"],
                check=True,
                capture_output=True,
                text=True,
            )
            version = "unknown"
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":")[1].strip()
                    break
            print(f"✅ pre-commit is installed (version: {version})")
        except Exception:
            print("✅ pre-commit is installed")
        return True
    except ImportError:
        print("❌ pre-commit is not installed")
        print("   Run: pip install pre-commit")
        return False


def check_hooks_installed() -> bool:
    """Check if pre-commit hooks are installed in the git repository."""
    git_hooks_path = Path(".git/hooks/pre-commit")
    if git_hooks_path.exists():
        print("✅ pre-commit hooks are installed")
        return True
    else:
        print("❌ pre-commit hooks are not installed")
        print("   Run: pre-commit install")
        return False


def run_pre_commit_check() -> bool:
    """Run pre-commit on a sample file to verify it works."""
    print("Running pre-commit check on a sample file...")
    try:
        # Use Python module directly
        import sys

        import pre_commit.main

        # Save original argv and redirect stdout/stderr
        original_argv = sys.argv
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        from io import StringIO

        stdout_capture = StringIO()
        stderr_capture = StringIO()

        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        # Run pre-commit on this file
        sys.argv = ["pre-commit", "run", "--files", "scripts/verify_hooks.py"]
        try:
            pre_commit.main.main()
            success = True
        except SystemExit as e:
            success = e.code == 0
        finally:
            # Restore original stdout/stderr and argv
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.argv = original_argv

        if success:
            print("✅ pre-commit hooks are working correctly")
            return True
        else:
            print("❌ pre-commit hooks failed")
            print(stdout_capture.getvalue())
            print(stderr_capture.getvalue())
            return False
    except Exception as e:
        print(f"❌ Error running pre-commit: {e}")
        return False


def main() -> int:
    """Run all checks and return appropriate exit code."""
    print("Verifying pre-commit hooks setup...")

    # Create the scripts directory if it doesn't exist
    os.makedirs("scripts", exist_ok=True)

    checks = [
        check_pre_commit_installed(),
        check_hooks_installed(),
        run_pre_commit_check(),
    ]

    if all(checks):
        print("\n✅ All checks passed! pre-commit is properly set up.")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
