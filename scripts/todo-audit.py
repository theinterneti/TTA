#!/usr/bin/env python3
"""
TTA TODO & GitHub Issue Audit Script

This script provides intelligent management of TODOs and GitHub issues:
- Syncs GitHub issues to Logseq format
- Scans codebase for TODO comments
- Generates status reports
- Identifies stale/orphaned TODOs
- Suggests prioritization

Usage:
    python scripts/todo-audit.py sync        # Sync GitHub issues
    python scripts/todo-audit.py scan        # Scan codebase TODOs
    python scripts/todo-audit.py report      # Generate report
    python scripts/todo-audit.py orphans     # Find orphaned TODOs
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
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
    code_todos: list[CodeTODO] = field(default_factory=list)
    orphaned_todos: list[CodeTODO] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class TODOAuditor:
    """Main auditor class for TODO and GitHub issue management."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.audit_file = repo_root / ".augment" / "TODO-AUDIT.md"
        self.logseq_dir = repo_root / ".augment" / "logseq"

        # TODO patterns to match
        self.todo_patterns = [
            r"#\s*TODO:?\s*(.+)",
            r"TODO\(([^)]+)\):?\s*(.+)",
            r"@todo\s+(.+)",
            r"FIXME:?\s*(.+)",
            r"XXX:?\s*(.+)",
            r"HACK:?\s*(.+)",
        ]

        # File patterns to exclude
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

    def fetch_github_issues(self) -> list[GitHubIssue]:
        """Fetch GitHub issues using gh CLI."""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "list",
                    "--limit",
                    "100",
                    "--json",
                    "number,title,state,labels,url,body",
                ],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

            issues_data = json.loads(result.stdout)
            issues = []

            for issue_data in issues_data:
                labels = [label["name"] for label in issue_data.get("labels", [])]
                issue = GitHubIssue(
                    number=issue_data["number"],
                    title=issue_data["title"],
                    state=issue_data["state"],
                    labels=labels,
                    url=issue_data["url"],
                    body=issue_data.get("body", ""),
                )
                issues.append(issue)

            return issues

        except subprocess.CalledProcessError as e:
            print(f"Error fetching GitHub issues: {e}")
            print("Make sure gh CLI is installed and authenticated")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing GitHub issues: {e}")
            return []

    def scan_code_todos(self) -> list[CodeTODO]:
        """Scan codebase for TODO comments."""
        todos = []

        # Use git ls-files to get tracked files
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            files = result.stdout.strip().split("\n")
        except subprocess.CalledProcessError:
            print("Error listing files, falling back to glob")
            files = [
                str(p.relative_to(self.repo_root))
                for p in self.repo_root.rglob("*")
                if p.is_file()
            ]

        # Scan each file
        for file_rel in files:
            file_path = self.repo_root / file_rel

            # Skip excluded patterns
            if any(file_path.match(pattern) for pattern in self.exclude_patterns):
                continue

            # Only scan text files
            if not self._is_text_file(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in self.todo_patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                content = (
                                    match.group(1) if match.groups() else line.strip()
                                )

                                # Extract GitHub issue reference if present
                                issue_match = re.search(r"#(\d+)", content)
                                github_issue = (
                                    int(issue_match.group(1)) if issue_match else None
                                )

                                # Categorize TODO
                                category = self._categorize_todo(file_path, content)
                                priority = self._prioritize_todo(content)

                                todo = CodeTODO(
                                    file_path=file_path.relative_to(self.repo_root),
                                    line_number=line_num,
                                    content=content.strip(),
                                    category=category,
                                    priority=priority,
                                    github_issue=github_issue,
                                )
                                todos.append(todo)
                                break  # Only match one pattern per line

            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                continue

        return todos

    def find_orphaned_todos(
        self, code_todos: list[CodeTODO], github_issues: list[GitHubIssue]
    ) -> list[CodeTODO]:
        """Find TODOs that reference closed/non-existent GitHub issues."""
        orphaned = []
        issue_numbers = {
            issue.number for issue in github_issues if issue.state == "OPEN"
        }

        for todo in code_todos:
            if todo.github_issue and todo.github_issue not in issue_numbers:
                orphaned.append(todo)

        return orphaned

    def generate_report(self) -> AuditReport:
        """Generate comprehensive audit report."""
        print("🔍 Fetching GitHub issues...")
        github_issues = self.fetch_github_issues()

        print("📝 Scanning codebase for TODOs...")
        code_todos = self.scan_code_todos()

        print("🔗 Finding orphaned TODOs...")
        orphaned_todos = self.find_orphaned_todos(code_todos, github_issues)

        # Calculate statistics
        stats = {
            "total_github_issues": len(github_issues),
            "open_github_issues": sum(1 for i in github_issues if i.state == "OPEN"),
            "total_code_todos": len(code_todos),
            "orphaned_todos": len(orphaned_todos),
            "todos_by_priority": self._count_by_priority(code_todos),
            "todos_by_category": self._count_by_category(code_todos),
            "issues_by_label": self._count_by_label(github_issues),
        }

        report = AuditReport(
            timestamp=datetime.now(),
            github_issues=github_issues,
            code_todos=code_todos,
            orphaned_todos=orphaned_todos,
            stats=stats,
        )

        return report

    def export_to_logseq(self, report: AuditReport):
        """Export audit report to Logseq format."""
        self.logseq_dir.mkdir(parents=True, exist_ok=True)

        # Create pages directory
        pages_dir = self.logseq_dir / "pages"
        pages_dir.mkdir(exist_ok=True)

        # Generate issue pages
        for issue in report.github_issues:
            if issue.state == "OPEN":
                self._create_issue_page(pages_dir, issue, report.code_todos)

        # Generate TODO summary page
        self._create_todo_summary_page(pages_dir, report)

        print(f"✅ Exported to Logseq: {self.logseq_dir}")

    def _create_issue_page(
        self, pages_dir: Path, issue: GitHubIssue, todos: list[CodeTODO]
    ):
        """Create a Logseq page for a GitHub issue."""
        page_name = f"Issue-{issue.number}"
        page_file = pages_dir / f"{page_name}.md"

        # Find related TODOs
        related_todos = [t for t in todos if t.github_issue == issue.number]

        content = f"""---
title: Issue #{issue.number}: {issue.title}
tags: {", ".join(f"#{label}" for label in issue.labels)}
github-issue: {issue.number}
state: {issue.state}
url: {issue.url}
---

# Issue #{issue.number}: {issue.title}

## Details
- **State**: {issue.state}
- **Labels**: {", ".join(issue.labels)}
- **URL**: {issue.url}

## Description
{issue.body or "No description provided"}

## Related Code TODOs
"""

        if related_todos:
            for todo in related_todos:
                content += (
                    f"- TODO [[{todo.file_path}:{todo.line_number}]]: {todo.content}\n"
                )
        else:
            content += "*No related TODOs found in codebase*\n"

        with open(page_file, "w") as f:
            f.write(content)

    def _create_todo_summary_page(self, pages_dir: Path, report: AuditReport):
        """Create a summary page of all TODOs."""
        page_file = pages_dir / "TODO-Summary.md"

        content = f"""---
title: TODO Summary
updated: {report.timestamp.isoformat()}
---

# TODO Summary

Generated: {report.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

## Statistics
- **Total GitHub Issues**: {report.stats["total_github_issues"]}
- **Open GitHub Issues**: {report.stats["open_github_issues"]}
- **Code TODOs**: {report.stats["total_code_todos"]}
- **Orphaned TODOs**: {report.stats["orphaned_todos"]}

## TODOs by Priority
"""
        for priority, count in sorted(report.stats["todos_by_priority"].items()):
            content += f"- **{priority.title()}**: {count}\n"

        content += "\n## TODOs by Category\n"
        for category, count in sorted(report.stats["todos_by_category"].items()):
            content += f"- **{category.title()}**: {count}\n"

        # Add orphaned TODOs section
        if report.orphaned_todos:
            content += "\n## ⚠️ Orphaned TODOs\n"
            content += "*TODOs referencing closed or non-existent issues*\n\n"
            for todo in report.orphaned_todos:
                content += f"- [[{todo.file_path}:{todo.line_number}]]: {todo.content} (refs #[[Issue-{todo.github_issue}]])\n"

        with open(page_file, "w") as f:
            f.write(content)

    def _is_text_file(self, path: Path) -> bool:
        """Check if file is likely a text file."""
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
        """Categorize TODO based on file path and content."""
        path_str = str(file_path).lower()
        content_lower = content.lower()

        if "auth" in path_str or "auth" in content_lower:
            return "authentication"
        if "test" in path_str:
            return "testing"
        if "api" in path_str or "router" in path_str:
            return "api"
        if (
            "database" in content_lower
            or "neo4j" in content_lower
            or "redis" in content_lower
        ):
            return "database"
        if "narrative" in path_str or "story" in content_lower:
            return "narrative"
        if "doc" in path_str or "readme" in path_str:
            return "documentation"
        return "general"

    def _prioritize_todo(self, content: str) -> str:
        """Determine TODO priority from content."""
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
        """Count TODOs by priority."""
        counts = {"high": 0, "medium": 0, "low": 0}
        for todo in todos:
            counts[todo.priority] += 1
        return counts

    def _count_by_category(self, todos: list[CodeTODO]) -> dict[str, int]:
        """Count TODOs by category."""
        counts = {}
        for todo in todos:
            counts[todo.category] = counts.get(todo.category, 0) + 1
        return counts

    def _count_by_label(self, issues: list[GitHubIssue]) -> dict[str, int]:
        """Count issues by label."""
        counts = {}
        for issue in issues:
            for label in issue.labels:
                counts[label] = counts.get(label, 0) + 1
        return counts


def main():
    parser = argparse.ArgumentParser(description="TTA TODO & GitHub Issue Audit Tool")
    parser.add_argument(
        "command",
        choices=["sync", "scan", "report", "orphans", "export"],
        help="Command to execute",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "logseq"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    auditor = TODOAuditor(PROJECT_ROOT)

    if args.command == "sync":
        print("🔄 Syncing GitHub issues...")
        issues = auditor.fetch_github_issues()
        print(f"✅ Fetched {len(issues)} issues")

    elif args.command == "scan":
        print("📝 Scanning codebase for TODOs...")
        todos = auditor.scan_code_todos()
        print(f"✅ Found {len(todos)} TODOs")

        if args.format == "text":
            for todo in todos[:10]:  # Show first 10
                print(
                    f"  {todo.file_path}:{todo.line_number} [{todo.priority}] {todo.content[:60]}..."
                )

    elif args.command == "orphans":
        print("🔗 Finding orphaned TODOs...")
        issues = auditor.fetch_github_issues()
        todos = auditor.scan_code_todos()
        orphaned = auditor.find_orphaned_todos(todos, issues)

        print(f"⚠️  Found {len(orphaned)} orphaned TODOs")
        for todo in orphaned:
            print(f"  {todo.file_path}:{todo.line_number} (refs #{todo.github_issue})")

    elif args.command == "report":
        print("📊 Generating audit report...")
        report = auditor.generate_report()

        print("\n" + "=" * 60)
        print("TTA TODO & ISSUE AUDIT REPORT")
        print("=" * 60)
        print(f"\nGenerated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

        print("GitHub Issues:")
        print(f"  Total: {report.stats['total_github_issues']}")
        print(f"  Open: {report.stats['open_github_issues']}")

        print("\nCode TODOs:")
        print(f"  Total: {report.stats['total_code_todos']}")
        print(f"  High Priority: {report.stats['todos_by_priority']['high']}")
        print(f"  Medium Priority: {report.stats['todos_by_priority']['medium']}")
        print(f"  Low Priority: {report.stats['todos_by_priority']['low']}")

        print(f"\n⚠️  Orphaned TODOs: {report.stats['orphaned_todos']}")

        print("\nTop Issue Labels:")
        for label, count in sorted(
            report.stats["issues_by_label"].items(), key=lambda x: x[1], reverse=True
        )[:5]:
            print(f"  {label}: {count}")

    elif args.command == "export":
        print("📤 Exporting to Logseq...")
        report = auditor.generate_report()
        auditor.export_to_logseq(report)
        print("✅ Export complete!")


if __name__ == "__main__":
    main()
