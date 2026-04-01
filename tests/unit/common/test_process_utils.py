"""
Unit tests for src/common/process_utils.py.

Tests cover:
- Successful command execution
- Non-zero returncode without check= → no exception
- Non-zero returncode with check=True → ProcessError
- Timeout → ProcessError
- Invalid cmd type → ValueError
- RunResult.to_completed_process() round-trip
- capture_output=False (stdout/stderr not captured)
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from src.common.process_utils import ProcessError, RunResult, run

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# RunResult
# ---------------------------------------------------------------------------


class TestRunResult:
    def test_to_completed_process_fields(self):
        """Run Result: to completed process fields."""
        rr = RunResult(
            args=["echo", "hi"],
            returncode=0,
            stdout="hi\n",
            stderr="",
            duration_s=0.01,
        )
        cp = rr.to_completed_process()
        assert isinstance(cp, subprocess.CompletedProcess)
        assert cp.returncode == 0
        assert cp.stdout == "hi\n"
        assert cp.stderr == ""
        assert cp.args == ["echo", "hi"]


# ---------------------------------------------------------------------------
# run() — happy path
# ---------------------------------------------------------------------------


class TestRunSuccess:
    def test_returns_completed_process(self):
        """Run Success: returns completed process."""
        result = run([sys.executable, "-c", "print('hello')"])
        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_stderr_captured(self):
        """Run Success: stderr captured."""
        result = run([sys.executable, "-c", "import sys; sys.stderr.write('err')"])
        assert "err" in result.stderr

    def test_returncode_zero(self):
        """Run Success: returncode zero."""
        result = run([sys.executable, "-c", "pass"])
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# run() — failure handling
# ---------------------------------------------------------------------------


class TestRunFailure:
    def test_nonzero_without_check_does_not_raise(self):
        """Run Failure: nonzero without check does not raise."""
        result = run([sys.executable, "-c", "import sys; sys.exit(2)"])
        assert result.returncode == 2

    def test_nonzero_with_check_raises_process_error(self):
        """Run Failure: nonzero with check raises process error."""
        with pytest.raises(ProcessError) as exc_info:
            run([sys.executable, "-c", "import sys; sys.exit(1)"], check=True)
        assert exc_info.value.result is not None
        assert exc_info.value.result.returncode == 1

    def test_process_error_message_contains_command(self):
        """Run Failure: process error message contains command."""
        with pytest.raises(ProcessError, match="sys.exit"):
            run(
                [sys.executable, "-c", "import sys; sys.exit(1)"],
                check=True,
            )


# ---------------------------------------------------------------------------
# run() — timeout
# ---------------------------------------------------------------------------


class TestRunTimeout:
    def test_timeout_raises_process_error(self):
        """Run Timeout: timeout raises process error."""
        with pytest.raises(ProcessError, match="timed out"):
            run([sys.executable, "-c", "import time; time.sleep(60)"], timeout=1)


# ---------------------------------------------------------------------------
# run() — invalid input
# ---------------------------------------------------------------------------


class TestRunInvalidInput:
    def test_non_list_cmd_raises_value_error(self):
        """Run Invalid Input: non list cmd raises value error."""
        with pytest.raises(ValueError, match="List\\[str\\]"):
            run("echo hello")  # type: ignore[arg-type]

    def test_list_with_non_str_raises_value_error(self):
        """Run Invalid Input: list with non str raises value error."""
        with pytest.raises(ValueError, match="List\\[str\\]"):
            run(["echo", 123])  # type: ignore[list-item]


# ---------------------------------------------------------------------------
# run() — capture_output=False
# ---------------------------------------------------------------------------


class TestRunNoCaptureOutput:
    def test_stdout_none_when_not_captured(self):
        # With capture_output=False, subprocess doesn't capture; result.stdout is None
        """Run No Capture Output: stdout none when not captured."""
        result = run(
            [sys.executable, "-c", "print('x')"],
            capture_output=False,
        )
        # subprocess.CompletedProcess.stdout is None when not capturing
        assert result.stdout is None or result.stdout == ""
