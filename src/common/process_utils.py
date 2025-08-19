"""
Process utilities: safe subprocess execution helpers.

Design goals:
- No shell=True usage
- Timeouts by default
- Consistent logging and error surfaces
- Preserve behavior of callers expecting subprocess.CompletedProcess where feasible
"""

from __future__ import annotations

import logging
import shlex
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional, Mapping

logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    """Structured result of a process execution.

    Mirrors key attributes of subprocess.CompletedProcess for convenience,
    but adds duration and command string for logging.
    """
    args: List[str]
    returncode: int
    stdout: str
    stderr: str
    duration_s: float

    def to_completed_process(self) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(args=self.args, returncode=self.returncode, stdout=self.stdout, stderr=self.stderr)


class ProcessError(subprocess.SubprocessError):
    def __init__(self, message: str, *, result: Optional[RunResult] = None):
        super().__init__(message)
        self.result = result


def _format_cmd(cmd: List[str]) -> str:
    return " ".join(shlex.quote(c) for c in cmd)


def run(
    cmd: List[str],
    *,
    timeout: int = 60,
    cwd: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
    check: bool = False,
    text: bool = True,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """
    Safe wrapper around subprocess.run with sensible defaults.

    - Forces shell=False (never uses shell)
    - Captures stdout/stderr by default
    - Adds timeout and duration logging
    - Optionally raises ProcessError if check=True and returncode != 0

    Returns a subprocess.CompletedProcess to maintain drop-in compatibility.
    """
    if not isinstance(cmd, list) or not all(isinstance(x, str) for x in cmd):
        raise ValueError("cmd must be List[str]")

    full_cmd = cmd
    cmd_str = _format_cmd(full_cmd)
    start = time.perf_counter()
    logger.info(f"Running command: {cmd_str} (timeout={timeout}s)")
    try:
        result = subprocess.run(
            full_cmd,
            cwd=cwd,
            env=env,  # type: ignore[arg-type]
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            text=text,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        duration = time.perf_counter() - start
        logger.error(f"Command timed out after {duration:.2f}s: {cmd_str}")
        raise ProcessError(f"Command timed out after {duration:.2f}s: {cmd_str}") from e
    except Exception as e:
        duration = time.perf_counter() - start
        logger.error(f"Command failed to start after {duration:.2f}s: {cmd_str} | err={e}")
        raise

    duration = time.perf_counter() - start
    rr = RunResult(args=full_cmd, returncode=result.returncode, stdout=result.stdout or "", stderr=result.stderr or "", duration_s=duration)

    if rr.returncode != 0:
        logger.error(f"Command failed (rc={rr.returncode}) in {duration:.2f}s: {cmd_str}\nSTDERR: {rr.stderr.strip()}")
        if check:
            raise ProcessError(f"Command failed (rc={rr.returncode}): {cmd_str}", result=rr)
    else:
        logger.info(f"Command succeeded (rc=0) in {duration:.2f}s: {cmd_str}")

    return rr.to_completed_process()

