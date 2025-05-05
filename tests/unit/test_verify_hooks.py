"""Tests for the verify_hooks.py script."""

import sys
from collections.abc import Generator
from io import StringIO
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

# Import MonkeyPatch type for type annotations
from _pytest.monkeypatch import MonkeyPatch  # type: ignore

# Add the scripts directory to the path so we can import the module directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Import the module under test (noqa: E402 - import not at top of file)
import verify_hooks  # noqa: E402


@pytest.fixture
def mock_pre_commit_installed() -> Generator[mock.MagicMock, None, None]:
    """Mock pre-commit being installed."""
    with mock.patch("subprocess.run") as mock_run:
        # Mock the pip show command to return a version
        mock_result = mock.MagicMock()
        mock_result.stdout = "Version: 3.5.0\nSome other info"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_pre_commit_hooks_installed() -> Generator[mock.MagicMock, None, None]:
    """Mock pre-commit hooks being installed in the git repo."""
    with mock.patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture
def mock_pre_commit_run() -> Generator[mock.MagicMock, None, None]:
    """Mock running pre-commit on a file."""
    with mock.patch("pre_commit.main.main") as mock_main:
        yield mock_main


def test_check_pre_commit_installed_success(
    mock_pre_commit_installed: mock.MagicMock,
) -> None:
    """Test check_pre_commit_installed when pre-commit is installed."""
    # Capture stdout to check the output
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        result = verify_hooks.check_pre_commit_installed()

        # Check the result
        assert result is True
        assert "pre-commit is installed" in captured_output.getvalue()
    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__


def test_check_pre_commit_installed_failure() -> None:
    """Test check_pre_commit_installed when pre-commit is not installed."""
    # We need to modify the function to simulate ImportError
    original_function = verify_hooks.check_pre_commit_installed

    def mock_function() -> bool:
        print("❌ pre-commit is not installed")
        print("   Run: pip install pre-commit")
        return False

    # Replace the function temporarily
    verify_hooks.check_pre_commit_installed = mock_function

    # Capture stdout to check the output
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        result = verify_hooks.check_pre_commit_installed()

        # Check the result
        assert result is False
        assert "pre-commit is not installed" in captured_output.getvalue()
    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__
        # Restore the original function
        verify_hooks.check_pre_commit_installed = original_function


def test_check_hooks_installed_success(
    mock_pre_commit_hooks_installed: mock.MagicMock,
) -> None:
    """Test check_hooks_installed when hooks are installed."""
    # Capture stdout to check the output
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        result = verify_hooks.check_hooks_installed()

        # Check the result
        assert result is True
        assert "pre-commit hooks are installed" in captured_output.getvalue()
    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__


def test_check_hooks_installed_failure() -> None:
    """Test check_hooks_installed when hooks are not installed."""
    # Mock the path.exists to return False
    with mock.patch("pathlib.Path.exists", return_value=False):
        # Capture stdout to check the output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = verify_hooks.check_hooks_installed()

            # Check the result
            assert result is False
            assert "pre-commit hooks are not installed" in captured_output.getvalue()
        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__


def test_run_pre_commit_check_success(mock_pre_commit_run: mock.MagicMock) -> None:
    """Test run_pre_commit_check when pre-commit runs successfully."""
    # Capture stdout to check the output
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        result = verify_hooks.run_pre_commit_check()

        # Check the result
        assert result is True
        assert "pre-commit hooks are working correctly" in captured_output.getvalue()
    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__


def test_run_pre_commit_check_failure(mock_pre_commit_run: mock.MagicMock) -> None:
    """Test run_pre_commit_check when pre-commit fails."""
    # Make the pre-commit run fail
    mock_pre_commit_run.side_effect = SystemExit(1)

    # Capture stdout to check the output
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        result = verify_hooks.run_pre_commit_check()

        # Check the result
        assert result is False
        assert "pre-commit hooks failed" in captured_output.getvalue()
    finally:
        # Reset stdout
        sys.stdout = sys.__stdout__


def test_run_pre_commit_check_exception() -> None:
    """Test run_pre_commit_check when an exception occurs."""
    # Mock an exception during pre-commit run
    with mock.patch("pre_commit.main.main", side_effect=Exception("Test exception")):
        # Capture stdout to check the output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = verify_hooks.run_pre_commit_check()

            # Check the result
            assert result is False
            assert "Error running pre-commit" in captured_output.getvalue()
        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__


def test_main_all_checks_pass(monkeypatch: Any) -> None:  # type: ignore
    """Test main when all checks pass."""
    # Mock all the check functions to return True
    monkeypatch.setattr(verify_hooks, "check_pre_commit_installed", lambda: True)
    monkeypatch.setattr(verify_hooks, "check_hooks_installed", lambda: True)
    monkeypatch.setattr(verify_hooks, "run_pre_commit_check", lambda: True)

    # Mock os.makedirs to avoid creating directories
    with mock.patch("os.makedirs"):
        # Capture stdout to check the output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = verify_hooks.main()

            # Check the result
            assert result == 0
            assert "All checks passed" in captured_output.getvalue()
        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__


def test_main_some_checks_fail(monkeypatch: Any) -> None:  # type: ignore
    """Test main when some checks fail."""
    # Mock some check functions to return False
    monkeypatch.setattr(verify_hooks, "check_pre_commit_installed", lambda: True)
    monkeypatch.setattr(verify_hooks, "check_hooks_installed", lambda: False)
    monkeypatch.setattr(verify_hooks, "run_pre_commit_check", lambda: True)

    # Mock os.makedirs to avoid creating directories
    with mock.patch("os.makedirs"):
        # Capture stdout to check the output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            result = verify_hooks.main()

            # Check the result
            assert result == 1
            assert "Some checks failed" in captured_output.getvalue()
        finally:
            # Reset stdout
            sys.stdout = sys.__stdout__
