"""Tests for scripts/check_agent_docs.py budget enforcement."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[3] / "scripts" / "check_agent_docs.py"


def run_check(tmp_path: Path, files: dict[str, str]) -> tuple[int, str]:
    """Write files to tmp_path and run the checker against them."""
    for name, content in files.items():
        (tmp_path / name).write_text(content)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


def make_lines(n: int) -> str:
    return "\n".join(f"line {i}" for i in range(n))


class TestBudgetEnforcement:
    def test_passes_when_all_files_under_budget(self, tmp_path: Path) -> None:
        files = {
            "CLAUDE.md": make_lines(80),
            "AGENTS.md": make_lines(70),
        }
        returncode, _ = run_check(tmp_path, files)
        assert returncode == 0

    def test_fails_when_file_over_budget(self, tmp_path: Path) -> None:
        files = {
            "CLAUDE.md": make_lines(101),
            "AGENTS.md": make_lines(70),
        }
        returncode, output = run_check(tmp_path, files)
        assert returncode != 0
        assert "CLAUDE.md" in output

    def test_reports_exact_line_count(self, tmp_path: Path) -> None:
        files = {"CLAUDE.md": make_lines(110)}
        _, output = run_check(tmp_path, files)
        assert "110" in output

    def test_reports_all_over_budget_files(self, tmp_path: Path) -> None:
        files = {
            "CLAUDE.md": make_lines(105),
            "AGENTS.md": make_lines(120),
        }
        _, output = run_check(tmp_path, files)
        assert "CLAUDE.md" in output
        assert "AGENTS.md" in output

    def test_missing_file_is_skipped_not_error(self, tmp_path: Path) -> None:
        # Only CLAUDE.md present — missing files are just skipped
        files = {"CLAUDE.md": make_lines(50)}
        returncode, _ = run_check(tmp_path, files)
        assert returncode == 0

    def test_exactly_100_lines_passes(self, tmp_path: Path) -> None:
        files = {"CLAUDE.md": make_lines(100)}
        returncode, _ = run_check(tmp_path, files)
        assert returncode == 0

    def test_101_lines_fails(self, tmp_path: Path) -> None:
        files = {"CLAUDE.md": make_lines(101)}
        returncode, _ = run_check(tmp_path, files)
        assert returncode != 0
