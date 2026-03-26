#!/usr/bin/env python3
"""TTA TODO and GitHub issue audit tool.

This script scans tracked files for TODO-style comments and combines that view
with live GitHub issues and milestones when the `gh` CLI is available.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class GitHubIssue:
    """Represents a GitHub issue."""

    number: int
    title: str
    state: str
    labels: list[str]
    url: str
    body: str | None = None


@dataclass
class GitHubMilestone:
    """Represents a GitHub milestone."""

    number: int
    title: str
    state: str
    open_issues: int
    closed_issues: int
    due_on: str | None
    url: str


@dataclass
class CodeTODO:
    """Represents a TODO comment in code."""

    file_path: Path
    line_number: int
    content: str
    category: str = "general"
    priority: str = "medium"
    github_issue: int | None = None


@dataclass
class AuditReport:
    """Audit report containing all findings."""

    timestamp: datetime
    github_issues: list[GitHubIssue] = field(default_factory=list)
    github_milestones: list[GitHubMilestone] = field(default_factory=list)
    code_todos: list[CodeTODO] = field(default_factory=list)
    orphaned_todos: list[CodeTODO] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)


class TODOAuditor:
    """Main auditor class for TODO and GitHub issue management."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.todo_patterns = [
            r"#\s*TODO:?\s*(.+)",
            r"TODO\(([^)]+)\):?\s*(.+)",
            r"@todo\s+(.+)",
            r"FIXME:?\s*(.+)",
            r"XXX:?\s*(.+)",
            r"HACK:?\s*(.+)",
        ]
        self.exclude_patterns = [
            "*.pyc",
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            "dist",
            "build",
            "*.log",
            "htmlcov",
        ]

    def _run_command(self, args: list[str]) -> str | None:
        try:
            result = subprocess.run(  # noqa: S603
                args,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return None
        return result.stdout

    def _repo_slug(self) -> str | None:
        remote = self._run_command(["git", "remote", "get-url", "origin"])
        if remote is None:
            return None

        normalized = remote.strip()
        match = re.search(
            r"(?:github\.com[:/])(?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?$",
            normalized,
        )
        if match is None:
            return None
        return f"{match.group('owner')}/{match.group('repo')}"

    def fetch_github_issues(self) -> list[GitHubIssue]:
        """Fetch GitHub issues using gh CLI."""
        output = self._run_command(
            [
                "gh",
                "issue",
                "list",
                "--state",
                "all",
                "--limit",
                "100",
                "--json",
                "number,title,state,labels,url,body",
            ]
        )
        if output is None:
            return []

        try:
            issues_data = json.loads(output)
        except json.JSONDecodeError:
            return []

        issues: list[GitHubIssue] = []
        for issue_data in issues_data:
            labels = [label["name"] for label in issue_data.get("labels", [])]
            issues.append(
                GitHubIssue(
                    number=issue_data["number"],
                    title=issue_data["title"],
                    state=issue_data["state"],
                    labels=labels,
                    url=issue_data["url"],
                    body=issue_data.get("body"),
                )
            )
        return issues

    def fetch_github_milestones(self) -> list[GitHubMilestone]:
        """Fetch GitHub milestones using gh CLI."""
        repo_slug = self._repo_slug()
        if repo_slug is None:
            return []

        output = self._run_command(
            [
                "gh",
                "api",
                f"repos/{repo_slug}/milestones?state=all&per_page=100",
            ]
        )
        if output is None:
            return []

        try:
            milestones_data = json.loads(output)
        except json.JSONDecodeError:
            return []

        return [
            GitHubMilestone(
                number=milestone_data["number"],
                title=milestone_data["title"],
                state=milestone_data["state"],
                open_issues=milestone_data["open_issues"],
                closed_issues=milestone_data["closed_issues"],
                due_on=milestone_data.get("due_on"),
                url=milestone_data["html_url"],
            )
            for milestone_data in milestones_data
        ]

    def scan_code_todos(self) -> list[CodeTODO]:
        """Scan the codebase for TODO comments."""
        todos: list[CodeTODO] = []

        tracked_files = self._run_command(["git", "ls-files"])
        if tracked_files is None:
            files = [
                str(path.relative_to(self.repo_root))
                for path in self.repo_root.rglob("*")
                if path.is_file()
            ]
        else:
            files = [line for line in tracked_files.splitlines() if line]

        for file_rel in files:
            file_path = self.repo_root / file_rel
            if any(file_path.match(pattern) for pattern in self.exclude_patterns):
                continue
            if not self._is_text_file(file_path):
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for line_number, line in enumerate(content.splitlines(), 1):
                for pattern in self.todo_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match is None:
                        continue

                    matched_content = (
                        match.group(2) if len(match.groups()) > 1 else match.group(1)
                    )
                    issue_match = re.search(r"#(\d+)", matched_content)
                    github_issue = int(issue_match.group(1)) if issue_match else None

                    todos.append(
                        CodeTODO(
                            file_path=file_path.relative_to(self.repo_root),
                            line_number=line_number,
                            content=matched_content.strip(),
                            category=self._categorize_todo(file_path, matched_content),
                            priority=self._prioritize_todo(matched_content),
                            github_issue=github_issue,
                        )
                    )
                    break

        return todos

    def find_orphaned_todos(
        self, code_todos: list[CodeTODO], github_issues: list[GitHubIssue]
    ) -> list[CodeTODO]:
        """Find TODOs that reference closed or missing GitHub issues."""
        open_issue_numbers = {
            issue.number for issue in github_issues if issue.state.upper() == "OPEN"
        }
        return [
            todo
            for todo in code_todos
            if todo.github_issue is not None
            and todo.github_issue not in open_issue_numbers
        ]

    def generate_report(self) -> AuditReport:
        """Generate a comprehensive audit report."""
        github_issues = self.fetch_github_issues()
        github_milestones = self.fetch_github_milestones()
        code_todos = self.scan_code_todos()
        orphaned_todos = self.find_orphaned_todos(code_todos, github_issues)

        stats: dict[str, object] = {
            "total_github_issues": len(github_issues),
            "open_github_issues": sum(
                1 for issue in github_issues if issue.state.upper() == "OPEN"
            ),
            "closed_github_issues": sum(
                1 for issue in github_issues if issue.state.upper() == "CLOSED"
            ),
            "total_github_milestones": len(github_milestones),
            "open_github_milestones": sum(
                1
                for milestone in github_milestones
                if milestone.state.upper() == "OPEN"
            ),
            "total_code_todos": len(code_todos),
            "orphaned_todos": len(orphaned_todos),
            "todos_by_priority": self._count_by_priority(code_todos),
            "todos_by_category": self._count_by_category(code_todos),
            "issues_by_label": self._count_by_label(github_issues),
            "top_todo_files": self._count_by_file(code_todos),
        }

        return AuditReport(
            timestamp=datetime.now(UTC),
            github_issues=github_issues,
            github_milestones=github_milestones,
            code_todos=code_todos,
            orphaned_todos=orphaned_todos,
            stats=stats,
        )

    def _is_text_file(self, path: Path) -> bool:
        text_extensions = {
            ".py",
            ".md",
            ".txt",
            ".yml",
            ".yaml",
            ".json",
            ".toml",
            ".sh",
            ".bash",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".css",
            ".html",
            ".xml",
            ".sql",
            ".env",
            ".ini",
            ".cfg",
        }
        return path.suffix.lower() in text_extensions

    def _categorize_todo(self, file_path: Path, content: str) -> str:
        path_str = str(file_path).lower()
        content_lower = content.lower()
        category = "general"

        if "auth" in path_str or "auth" in content_lower:
            category = "authentication"
        elif "test" in path_str:
            category = "testing"
        elif "api" in path_str or "router" in path_str:
            category = "api"
        elif (
            "database" in content_lower
            or "neo4j" in content_lower
            or "redis" in content_lower
        ):
            category = "database"
        elif "narrative" in path_str or "story" in content_lower:
            category = "narrative"
        elif "doc" in path_str or "readme" in path_str:
            category = "documentation"

        return category

    def _prioritize_todo(self, content: str) -> str:
        content_lower = content.lower()
        if any(
            word in content_lower
            for word in ["critical", "urgent", "blocker", "security"]
        ):
            return "high"
        if any(word in content_lower for word in ["important", "soon", "mvp"]):
            return "medium"
        return "low"

    def _count_by_priority(self, todos: list[CodeTODO]) -> dict[str, int]:
        counts = {"high": 0, "medium": 0, "low": 0}
        for todo in todos:
            counts[todo.priority] += 1
        return counts

    def _count_by_category(self, todos: list[CodeTODO]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for todo in todos:
            counts[todo.category] = counts.get(todo.category, 0) + 1
        return counts

    def _count_by_label(self, issues: list[GitHubIssue]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for issue in issues:
            for label in issue.labels:
                counts[label] = counts.get(label, 0) + 1
        return counts

    def _count_by_file(self, todos: list[CodeTODO]) -> list[tuple[str, int]]:
        counts: dict[str, int] = {}
        for todo in todos:
            path_str = str(todo.file_path)
            counts[path_str] = counts.get(path_str, 0) + 1
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def _report_to_dict(report: AuditReport) -> dict[str, object]:
    return {
        "timestamp": report.timestamp.isoformat(),
        "github_issues": [asdict(issue) for issue in report.github_issues],
        "github_milestones": [
            asdict(milestone) for milestone in report.github_milestones
        ],
        "code_todos": [
            {
                **asdict(todo),
                "file_path": str(todo.file_path),
            }
            for todo in report.code_todos
        ],
        "orphaned_todos": [
            {
                **asdict(todo),
                "file_path": str(todo.file_path),
            }
            for todo in report.orphaned_todos
        ],
        "stats": report.stats,
    }


def _write(text: str = "") -> None:
    sys.stdout.write(f"{text}\n")


def _print_todos(todos: list[CodeTODO]) -> None:
    if not todos:
        _write("No TODOs found.")
        return

    for todo in todos:
        issue_ref = f" issue #{todo.github_issue}" if todo.github_issue else ""
        _write(
            f"{todo.file_path}:{todo.line_number} [{todo.priority}/{todo.category}]"
            f"{issue_ref} {todo.content}"
        )


def _print_issues(issues: list[GitHubIssue]) -> None:
    if not issues:
        _write("No GitHub issues returned.")
        return

    for issue in issues:
        labels = ", ".join(issue.labels) if issue.labels else "no-labels"
        _write(f"#{issue.number} [{issue.state.lower()}] {issue.title} ({labels})")


def _print_milestones(milestones: list[GitHubMilestone]) -> None:
    if not milestones:
        _write("No GitHub milestones returned.")
        return

    for milestone in milestones:
        _write(
            f"milestone #{milestone.number} [{milestone.state.lower()}] "
            f"{milestone.title} (open issues: {milestone.open_issues}, "
            f"closed issues: {milestone.closed_issues})"
        )


def _print_report(report: AuditReport) -> None:
    stats = report.stats

    _write("TTA TODO & GitHub Audit")
    _write(f"Generated: {report.timestamp.isoformat()}")
    _write()
    _write("Quick stats")
    _write(f"- Open GitHub issues: {stats['open_github_issues']}")
    _write(f"- Open GitHub milestones: {stats['open_github_milestones']}")
    _write(f"- Code TODOs: {stats['total_code_todos']}")
    _write(f"- Orphaned TODOs: {stats['orphaned_todos']}")
    _write()

    top_files = stats["top_todo_files"]
    if isinstance(top_files, list) and top_files:
        _write("Top TODO files")
        for file_path, count in top_files[:10]:
            _write(f"- {file_path}: {count}")
        _write()

    todos_by_category = stats["todos_by_category"]
    if isinstance(todos_by_category, dict) and todos_by_category:
        _write("TODOs by category")
        for category, count in sorted(
            todos_by_category.items(), key=lambda item: (-item[1], item[0])
        ):
            _write(f"- {category}: {count}")
        _write()

    if report.orphaned_todos:
        _write("Orphaned TODOs")
        _print_todos(report.orphaned_todos[:10])
        _write()

    open_milestones = [
        milestone
        for milestone in report.github_milestones
        if milestone.state.upper() == "OPEN"
    ]
    if open_milestones:
        _write("Open milestones")
        _print_milestones(open_milestones[:10])


def main() -> int:
    parser = argparse.ArgumentParser(description="TTA TODO & GitHub issue audit tool")
    parser.add_argument(
        "command",
        choices=["sync", "scan", "report", "orphans"],
        help="Command to execute",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    auditor = TODOAuditor(PROJECT_ROOT)

    if args.command == "sync":
        issues = auditor.fetch_github_issues()
        milestones = auditor.fetch_github_milestones()
        if args.format == "json":
            payload = {
                "issues": [asdict(issue) for issue in issues],
                "milestones": [asdict(milestone) for milestone in milestones],
            }
            _write(json.dumps(payload, indent=2))
        else:
            _write("GitHub issues")
            _print_issues(issues)
            _write()
            _write("GitHub milestones")
            _print_milestones(milestones)
        return 0

    if args.command == "scan":
        todos = auditor.scan_code_todos()
        if args.format == "json":
            _write(
                json.dumps(
                    [
                        {
                            **asdict(todo),
                            "file_path": str(todo.file_path),
                        }
                        for todo in todos
                    ],
                    indent=2,
                )
            )
        else:
            _print_todos(todos)
        return 0

    if args.command == "orphans":
        issues = auditor.fetch_github_issues()
        todos = auditor.scan_code_todos()
        orphaned = auditor.find_orphaned_todos(todos, issues)
        if args.format == "json":
            _write(
                json.dumps(
                    [
                        {
                            **asdict(todo),
                            "file_path": str(todo.file_path),
                        }
                        for todo in orphaned
                    ],
                    indent=2,
                )
            )
        else:
            _print_todos(orphaned)
        return 0

    report = auditor.generate_report()
    if args.format == "json":
        _write(json.dumps(_report_to_dict(report), indent=2))
    else:
        _print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
