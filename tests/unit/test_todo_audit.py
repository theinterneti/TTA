"""Unit tests for scripts/todo-audit.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _load_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "todo-audit.py"
    spec = importlib.util.spec_from_file_location("todo_audit", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


todo_audit = _load_module()


class TestTODOAuditor:
    def test_repo_slug_parses_https_remote(self, monkeypatch, tmp_path):
        auditor = todo_audit.TODOAuditor(tmp_path)

        def fake_run(*args, **kwargs):
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0,
                stdout="https://github.com/theinterneti/TTA.git\n",
                stderr="",
            )

        monkeypatch.setattr(todo_audit.subprocess, "run", fake_run)

        assert auditor._repo_slug() == "theinterneti/TTA"

    def test_generate_report_counts_open_issues_and_milestones(self, tmp_path):
        auditor = todo_audit.TODOAuditor(tmp_path)

        issues = [
            todo_audit.GitHubIssue(
                number=1,
                title="Open issue",
                state="OPEN",
                labels=["bug"],
                url="https://example.test/issues/1",
            ),
            todo_audit.GitHubIssue(
                number=2,
                title="Closed issue",
                state="CLOSED",
                labels=[],
                url="https://example.test/issues/2",
            ),
        ]
        milestones = [
            todo_audit.GitHubMilestone(
                number=1,
                title="MVP",
                state="OPEN",
                open_issues=0,
                closed_issues=2,
                due_on=None,
                url="https://example.test/milestones/1",
            )
        ]
        todos = [
            todo_audit.CodeTODO(
                file_path=Path("src/example.py"),
                line_number=10,
                content="TODO(#1): finish auth",
                category="authentication",
                priority="medium",
                github_issue=1,
            ),
            todo_audit.CodeTODO(
                file_path=Path("src/example.py"),
                line_number=11,
                content="TODO(#999): stale issue",
                category="general",
                priority="low",
                github_issue=999,
            ),
        ]

        auditor.fetch_github_issues = lambda: issues
        auditor.fetch_github_milestones = lambda: milestones
        auditor.scan_code_todos = lambda: todos

        report = auditor.generate_report()

        assert report.stats["open_github_issues"] == 1
        assert report.stats["open_github_milestones"] == 1
        assert report.stats["total_code_todos"] == 2
        assert report.stats["orphaned_todos"] == 1
        assert report.orphaned_todos[0].github_issue == 999

    def test_report_to_dict_serializes_paths_and_timestamp(self, tmp_path):
        auditor = todo_audit.TODOAuditor(tmp_path)
        auditor.fetch_github_issues = lambda: []
        auditor.fetch_github_milestones = lambda: []
        auditor.scan_code_todos = lambda: []

        report = auditor.generate_report()
        payload = todo_audit._report_to_dict(report)

        assert isinstance(payload["timestamp"], str)
        assert payload["code_todos"] == []
