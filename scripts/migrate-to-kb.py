#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Migrate-to-kb]]
Documentation migration tool for TTA-notes knowledge base integration.

This script helps migrate TTA documentation from scattered locations into
a centralized Logseq knowledge base structure.

Usage:
    uv run python scripts/migrate-to-kb.py scan
    uv run python scripts/migrate-to-kb.py plan --priority 1
    uv run python scripts/migrate-to-kb.py migrate --priority 1 --dry-run
    uv run python scripts/migrate-to-kb.py validate
    uv run python scripts/migrate-to-kb.py report
"""

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Base paths
REPO_ROOT = Path(__file__).parent.parent
KB_ROOT = REPO_ROOT / ".augment" / "kb"
DOCS_ROOT = REPO_ROOT / "docs"
AUGMENT_ROOT = REPO_ROOT / ".augment"
GITHUB_ROOT = REPO_ROOT / ".github"

# Migration database
MIGRATION_DB = REPO_ROOT / ".augment" / "migration-status.json"


@dataclass
class DocMetadata:
    """Metadata for a documentation file."""

    path: Path
    relative_path: str
    category: str
    priority: int
    doc_type: str
    title: str
    tags: list[str] = field(default_factory=list)
    status: str = "Active"
    repo: str = "theinterneti/TTA"
    created: str | None = None
    updated: str | None = None
    related: list[str] = field(default_factory=list)
    target_path: Path | None = None
    migrated: bool = False
    migration_date: str | None = None


@dataclass
class MigrationStats:
    """Statistics for migration progress."""

    total_files: int = 0
    scanned_files: int = 0
    priority_1: int = 0
    priority_2: int = 0
    priority_3: int = 0
    priority_4: int = 0
    priority_5: int = 0
    priority_6: int = 0
    priority_7: int = 0
    migrated: int = 0
    failed: int = 0
    skipped: int = 0


class DocumentScanner:
    """Scans repository for documentation files."""

    # Only include docs from these directories
    INCLUDE_DIRS = {
        "docs",  # Main documentation
        "scripts",  # Script documentation
        ".augment",  # AI workflow documentation
        ".github",  # GitHub workflows and templates
        "src",  # Source code documentation
        "tests",  # Test documentation
        "testing",  # Testing documentation
        "packages",  # Local packages (not external deps)
    }

    # Exclude these directories
    EXCLUDE_DIRS = {
        "node_modules",
        ".venv",
        "venv",
        "venv-staging",
        ".uv_cache",  # UV package cache
        ".git",
        "__pycache__",
        "build",
        "dist",
        ".pytest_cache",
        ".mypy_cache",
        "htmlcov",
        "backups",  # Backup directories
        "archive",  # Archived content
        "export",  # Export directories
        "list",  # Temporary directories
    }

    EXCLUDE_FILES = {"CHANGELOG.md", "LICENSE.md", "CODE_OF_CONDUCT.md"}

    def __init__(self):
        self.docs: list[DocMetadata] = []
        self.stats = MigrationStats()

    def scan(self) -> list[DocMetadata]:
        """Scan repository for markdown files."""

        markdown_files = list(REPO_ROOT.rglob("*.md"))
        self.stats.total_files = len(markdown_files)

        for md_file in markdown_files:
            if self._should_exclude(md_file):
                continue

            try:
                metadata = self._extract_metadata(md_file)
                self.docs.append(metadata)
                self.stats.scanned_files += 1

                # Update priority counts
                priority_attr = f"priority_{metadata.priority}"
                setattr(
                    self.stats, priority_attr, getattr(self.stats, priority_attr) + 1
                )

            except Exception:
                continue

        return self.docs

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        relative = path.relative_to(REPO_ROOT)
        parts = relative.parts

        # For root-level files, include core docs (README, AGENTS, CLAUDE, GEMINI, etc.)
        if len(parts) == 1:
            return False  # Include root-level markdown files

        # Check if file is in an included directory
        first_dir = parts[0]
        if first_dir not in self.INCLUDE_DIRS:
            return True  # Exclude if not in allowed directories

        # Exclude specific subdirectories even within allowed dirs
        if any(excluded in parts for excluded in self.EXCLUDE_DIRS):
            return True

        # Exclude specific files
        if path.name in self.EXCLUDE_FILES:
            return True

        # Exclude already migrated (in KB)
        return KB_ROOT in path.parents

    def _extract_metadata(self, path: Path) -> DocMetadata:
        """Extract metadata from a documentation file."""
        relative_path = str(path.relative_to(REPO_ROOT))

        # Read file content
        content = path.read_text(encoding="utf-8")

        # Extract title (first # heading or filename)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else path.stem

        # Categorize and prioritize
        category = self._categorize_doc(path, content)
        priority = self._prioritize_doc(path, content, category)
        doc_type = self._determine_doc_type(path, content)

        # Extract existing tags from content
        tags = self._extract_tags(content)

        # Determine target path in KB
        target_path = self._determine_target_path(path, category)

        # Get file timestamps
        stat = path.stat()
        created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d")
        updated = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")

        return DocMetadata(
            path=path,
            relative_path=relative_path,
            category=category,
            priority=priority,
            doc_type=doc_type,
            title=title,
            tags=tags,
            created=created,
            updated=updated,
            target_path=target_path,
        )

    def _categorize_doc(self, path: Path, content: str) -> str:
        """Categorize documentation by namespace."""
        relative = str(path.relative_to(REPO_ROOT))

        # Architecture docs
        if "architecture" in relative.lower() or "design" in relative.lower():
            return "Architecture"

        # Component docs
        if "component" in relative.lower() or "spec" in relative.lower():
            return "Components"

        # Workflow/process docs
        if any(
            word in relative.lower()
            for word in ["workflow", "process", "guide", "contributing"]
        ):
            return "Workflows"

        # Status/tracking docs
        if any(
            word in relative.lower()
            for word in ["status", "progress", "phase", "completion"]
        ):
            return "Status"

        # Reference materials
        if any(
            word in relative.lower() for word in ["quick", "ref", "reference", "cheat"]
        ):
            return "References"

        # Test documentation
        if "test" in relative.lower():
            return "Testing"

        # Research/investigations
        if any(
            word in relative.lower()
            for word in ["research", "investigation", "finding"]
        ):
            return "Research"

        # Default: References
        return "References"

    def _prioritize_doc(self, path: Path, content: str, category: str) -> int:
        """Assign migration priority (1=highest, 7=archive)."""
        relative = str(path.relative_to(REPO_ROOT))

        # Priority 1: Core context files
        priority_1_files = {
            "AGENTS.md",
            "TODO-AUDIT.md",
            "CROSS-REPO-GUIDE.md",
            "GEMINI.md",
            "README.md",
            "CLAUDE.md",
        }
        if path.name in priority_1_files:
            return 1

        # Priority 2: Architecture & design
        if category == "Architecture":
            return 2

        # Priority 3: Component documentation
        if category == "Components":
            return 3

        # Priority 4: Workflows & processes
        if category == "Workflows":
            return 4

        # Priority 5: Status tracking (needs consolidation)
        if category == "Status":
            # Check if outdated (mentioned "complete", "phase", old dates)
            if any(
                word in content.lower() for word in ["completed", "phase 1", "phase 2"]
            ):
                return 7  # Archive
            return 5

        # Priority 6: Reference materials
        if category == "References":
            return 6

        # Priority 7: Archive (old status, investigations, completed work)
        if any(
            word in relative.lower()
            for word in ["finding", "investigation", "old", "deprecated", "archive"]
        ):
            return 7

        # Default: Priority 6
        return 6

    def _determine_doc_type(self, path: Path, content: str) -> str:
        """Determine the type of documentation."""
        content_lower = content.lower()

        if "# specification" in content_lower or ".spec.md" in path.name:
            return "Specification"
        if "quick ref" in content_lower or "reference" in path.name.lower():
            return "Reference"
        if "guide" in content_lower or "tutorial" in content_lower:
            return "Guide"
        if "status" in content_lower or "progress" in content_lower:
            return "Status"
        if "architecture" in content_lower or "design" in content_lower:
            return "Architecture"
        if "workflow" in content_lower or "process" in content_lower:
            return "Workflow"
        if "api" in content_lower and "endpoint" in content_lower:
            return "API"

        return "Documentation"

    def _extract_tags(self, content: str) -> list[str]:
        """Extract existing tags from content."""
        tags = set()

        # Look for existing frontmatter tags
        frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            tag_match = re.search(r"tags:\s*(.+)", frontmatter_match.group(1))
            if tag_match:
                tag_str = tag_match.group(1)
                tags.update(re.findall(r"#(\w+)", tag_str))

        # Add default TTA tag
        tags.add("TTA")

        return sorted(tags)

    def _determine_target_path(self, path: Path, category: str) -> Path:
        """Determine target path in KB structure using Logseq naming convention.

        Pattern: TTA___Category___PageName.md
        This matches TTA.dev pattern: TTA.dev___Architecture___Agent Discoverability.md
        """
        relative = path.relative_to(REPO_ROOT)

        # Extract meaningful page name from path
        parent_parts = relative.parent.parts  # Get parent parts once for all paths
        is_root_file = len(parent_parts) == 0

        if path.stem.upper() == "README":
            # For README files in subdirectories, include more context
            if is_root_file or parent_parts[-1] in {
                ".",
                "recovered-tta-storytelling",
                "TTA",
            }:
                # Root README
                page_name = "Overview"
            elif len(parent_parts) >= 2:
                # Nested README - use last 2 levels for context
                # e.g., docs/ai-framework/agents/README.md -> "Ai Framework Agents"
                context = " ".join(parent_parts[-2:])
                page_name = context.replace("_", " ").replace("-", " ").title()
            else:
                # Single level README - use parent directory
                page_name = parent_parts[-1].replace("_", " ").replace("-", " ").title()
        else:
            # For regular files, use the stem and clean it up
            base_name = path.stem.replace("_", " ").replace("-", " ")

            # For non-root files, always include directory context to prevent collisions
            # This matches real-world TTA.dev patterns where path hierarchy is preserved
            if not is_root_file:
                # Build hierarchical context from parent path
                # e.g., docs/testing/PHASE_2.md -> "Testing Phase 2"
                # e.g., PHASE_2.md (root) -> "Phase 2"
                if len(parent_parts) >= 2:
                    # Use last 2 directory levels for context
                    context = " ".join(parent_parts[-2:])
                elif len(parent_parts) == 1:
                    # Single directory level
                    context = parent_parts[0]
                else:
                    # Root file (but not is_root_file somehow?)
                    context = ""

                if context:
                    context_clean = context.replace("_", " ").replace("-", " ").title()
                    page_name = f"{context_clean} {base_name}"
                else:
                    page_name = base_name
            else:
                # Root file - no context needed
                page_name = base_name

            # Keep acronyms uppercase (like AGENTS, CLAUDE, etc.)
            words = page_name.split()
            page_name = " ".join(
                word if len(word) <= 3 and word.isupper() else word.title()
                for word in words
            )

        # Handle package files - include package name in page title
        if "packages/" in str(relative):
            parts = relative.parts
            pkg_idx = parts.index("packages")
            if len(parts) > pkg_idx + 1:
                pkg_name = parts[pkg_idx + 1]
                # Clean package name
                pkg_clean = pkg_name.replace("_", " ").replace("-", " ").title()
                page_name = f"{pkg_clean} {page_name}"

        # Create Logseq-style filename: TTA___Category___PageName.md
        filename = f"TTA___{category}___{page_name}.md"

        # Handle case-sensitivity collisions by adding file extension context
        # e.g., contributing.md vs CONTRIBUTING.md -> include case hint
        target_path = KB_ROOT / category / filename
        if path.stem != path.stem.lower() and path.stem != path.stem.upper():
            # Mixed case filename - preserve it in page name
            pass
        elif path.stem.isupper() and len(path.stem) > 3:
            # ALL CAPS filename (not an acronym) - add "Document" suffix to distinguish
            # e.g., CONTRIBUTING.md -> "Docs Development Contributing Document"
            filename = f"TTA___{category}___{page_name} Document.md"
            target_path = KB_ROOT / category / filename

        # Return path within category directory (flat structure within each namespace)
        return target_path


class DocumentConverter:
    """Converts documentation to Logseq KB format."""

    def convert(self, metadata: DocMetadata, dry_run: bool = False) -> tuple[bool, str]:
        """Convert a document to KB format."""
        try:
            # Read original content
            content = metadata.path.read_text(encoding="utf-8")

            # Check if already has frontmatter
            has_frontmatter = content.startswith("---\n")

            if has_frontmatter:
                # Update existing frontmatter
                converted = self._update_frontmatter(content, metadata)
            else:
                # Add new frontmatter
                converted = self._add_frontmatter(content, metadata)

            # Convert links
            converted = self._convert_links(converted, metadata)

            # Add wiki-link to title
            converted = self._add_wiki_link(converted, metadata)

            if not dry_run:
                # Write to target location
                metadata.target_path.parent.mkdir(parents=True, exist_ok=True)
                metadata.target_path.write_text(converted, encoding="utf-8")

                # Create stub in original location
                self._create_stub(metadata)

            return True, "Converted successfully"

        except Exception as e:
            return False, f"Conversion failed: {e}"

    def _add_frontmatter(self, content: str, metadata: DocMetadata) -> str:
        """Add Logseq frontmatter to document."""
        frontmatter = [
            "---",
            f"title: {metadata.title}",
            f"tags: {' '.join('#' + tag for tag in metadata.tags)}",
            f"status: {metadata.status}",
            f"repo: {metadata.repo}",
            f"path: {metadata.relative_path}",
            f"created: {metadata.created}",
            f"updated: {metadata.updated}",
        ]

        if metadata.related:
            related_str = ", ".join(f"[[{r}]]" for r in metadata.related)
            frontmatter.append(f"related: {related_str}")

        frontmatter.append("---")
        frontmatter.append("")

        return "\n".join(frontmatter) + content

    def _update_frontmatter(self, content: str, metadata: DocMetadata) -> str:
        """Update existing frontmatter."""
        # For now, just add new frontmatter (can enhance later)
        match = re.match(r"^---\n.*?\n---\n", content, re.DOTALL)
        if match:
            # Remove old frontmatter
            content_without_fm = content[match.end() :]
            return self._add_frontmatter(content_without_fm, metadata)
        return self._add_frontmatter(content, metadata)

    def _convert_links(self, content: str, metadata: DocMetadata) -> str:
        """Convert relative links to appropriate format."""
        # Convert relative markdown links to wiki-links for KB docs
        # This is a simplified conversion - can be enhanced

        def replace_link(match):
            link_text = match.group(1)
            link_target = match.group(2)

            # If it's a relative link to .md file, convert to wiki-link
            if link_target.endswith(".md") and not link_target.startswith("http"):
                # Extract just the filename without path
                target_name = Path(link_target).stem
                return f"[[TTA/{metadata.category}/{target_name}|{link_text}]]"

            # Keep absolute links and non-md links as-is
            return match.group(0)

        # Pattern: [text](link)
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, content)

    def _add_wiki_link(self, content: str, metadata: DocMetadata) -> str:
        """Add wiki-link to title if not present."""
        # Find first heading
        match = re.search(r"^(#\s+)(.+)$", content, re.MULTILINE)
        if match:
            heading_level = match.group(1)
            heading_text = match.group(2)

            # If not already a wiki-link
            if not heading_text.startswith("[["):
                wiki_title = f"TTA/{metadata.category}/{metadata.title}"
                new_heading = f"{heading_level}[[{wiki_title}]]"
                content = (
                    content[: match.start()] + new_heading + content[match.end() :]
                )

        return content

    def _create_stub(self, metadata: DocMetadata):
        """Create stub file in original location pointing to new KB location."""
        stub_content = [
            f"# {metadata.title}",
            "",
            "> ⚠️ **This document has moved!**",
            "> ",
            "> This content is now maintained in the TTA-notes knowledge base:",
            f"> - **New location:** [[TTA/{metadata.category}/{metadata.title}]]",
            f"> - **Path:** `.augment/kb/{metadata.category}/{metadata.title}.md`",
            "> ",
            "> If using Logseq with TTA-notes, you can access it directly in the graph.",
            f"> Otherwise, see: `.augment/kb/{metadata.category}/{metadata.title}.md`",
            "",
            f"**Migration date:** {datetime.now().strftime('%Y-%m-%d')}",
        ]

        # Backup original first
        backup_path = metadata.path.with_suffix(".md.backup")
        shutil.copy2(metadata.path, backup_path)

        # Write stub
        metadata.path.write_text("\n".join(stub_content), encoding="utf-8")


class MigrationManager:
    """Manages the documentation migration process."""

    def __init__(self):
        self.scanner = DocumentScanner()
        self.converter = DocumentConverter()
        self.docs: list[DocMetadata] = []
        self.stats = MigrationStats()

    def load_docs(self) -> list[DocMetadata]:
        """Load scanned documents from cache or scan fresh."""
        if MIGRATION_DB.exists():
            data = json.loads(MIGRATION_DB.read_text())
            self.docs = [
                DocMetadata(
                    path=Path(d["path"]),
                    relative_path=d["relative_path"],
                    category=d["category"],
                    priority=d["priority"],
                    doc_type=d["doc_type"],
                    title=d["title"],
                    tags=d.get("tags", []),
                    status=d.get("status", "Active"),
                    repo=d.get("repo", "theinterneti/TTA"),
                    created=d.get("created"),
                    updated=d.get("updated"),
                    target_path=Path(d["target_path"])
                    if d.get("target_path")
                    else None,
                    migrated=d.get("migrated", False),
                    migration_date=d.get("migration_date"),
                )
                for d in data["docs"]
            ]
        else:
            self.docs = self.scanner.scan()
            self._save_scan_results()

        return self.docs

    def _save_scan_results(self):
        """Save scan results to cache."""
        data = {
            "scan_date": datetime.now().isoformat(),
            "total_files": len(self.docs),
            "docs": [
                {
                    "path": str(d.path),
                    "relative_path": d.relative_path,
                    "category": d.category,
                    "priority": d.priority,
                    "doc_type": d.doc_type,
                    "title": d.title,
                    "tags": d.tags,
                    "status": d.status,
                    "repo": d.repo,
                    "created": d.created,
                    "updated": d.updated,
                    "target_path": str(d.target_path) if d.target_path else None,
                    "migrated": d.migrated,
                    "migration_date": d.migration_date,
                }
                for d in self.docs
            ],
        }

        MIGRATION_DB.parent.mkdir(parents=True, exist_ok=True)
        MIGRATION_DB.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def migrate(self, priority: int | None = None, dry_run: bool = False):
        """Migrate documents to KB."""
        if not self.docs:
            self.load_docs()

        # Filter by priority if specified
        docs_to_migrate = self.docs
        if priority is not None:
            docs_to_migrate = [d for d in self.docs if d.priority == priority]

        # Filter already migrated
        docs_to_migrate = [d for d in docs_to_migrate if not d.migrated]

        if not docs_to_migrate:
            return

        if dry_run:
            pass

        for doc in docs_to_migrate:
            success, message = self.converter.convert(doc, dry_run=dry_run)

            if success:
                if not dry_run:
                    doc.migrated = True
                    doc.migration_date = datetime.now().strftime("%Y-%m-%d")
                    self.stats.migrated += 1
            else:
                self.stats.failed += 1

        if not dry_run:
            self._save_scan_results()


def cmd_scan(args):
    """Scan repository for documentation."""
    manager = MigrationManager()
    docs = manager.scanner.scan()
    manager.docs = docs  # Assign scanned docs to manager
    manager._save_scan_results()


def cmd_plan(args):
    """Show migration plan."""
    manager = MigrationManager()
    manager.load_docs()

    # Filter by priority if specified
    docs = manager.docs
    if args.priority is not None:
        docs = [d for d in docs if d.priority == args.priority]

    # Group by category
    by_category: dict[str, list[DocMetadata]] = {}
    for doc in docs:
        if doc.category not in by_category:
            by_category[doc.category] = []
        by_category[doc.category].append(doc)

    for category in sorted(by_category.keys()):
        for doc in by_category[category][:10]:  # Show first 10
            pass

        if len(by_category[category]) > 10:
            pass


def cmd_migrate(args):
    """Execute migration."""
    manager = MigrationManager()
    manager.migrate(priority=args.priority, dry_run=args.dry_run)


def cmd_validate(args):
    """Validate KB structure and content."""

    if not KB_ROOT.exists():
        return

    # Check namespace directories
    expected_namespaces = [
        "Architecture",
        "Components",
        "Workflows",
        "References",
        "Status",
        "Research",
        "Testing",
    ]

    for namespace in expected_namespaces:
        ns_path = KB_ROOT / namespace
        if ns_path.exists():
            len(list(ns_path.rglob("*.md")))
        else:
            pass


def cmd_report(args):
    """Generate migration report."""
    manager = MigrationManager()
    manager.load_docs()

    total = len(manager.docs)
    migrated = len([d for d in manager.docs if d.migrated])
    total - migrated

    # By priority
    for priority in range(1, 8):
        priority_docs = [d for d in manager.docs if d.priority == priority]
        [d for d in priority_docs if d.migrated]

    # By category
    categories = {d.category for d in manager.docs}
    for category in sorted(categories):
        category_docs = [d for d in manager.docs if d.category == category]
        [d for d in category_docs if d.migrated]


def main():
    parser = argparse.ArgumentParser(
        description="TTA documentation migration tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan command
    subparsers.add_parser("scan", help="Scan repository for documentation")

    # Plan command
    parser_plan = subparsers.add_parser("plan", help="Show migration plan")
    parser_plan.add_argument("--priority", type=int, help="Filter by priority (1-7)")

    # Migrate command
    parser_migrate = subparsers.add_parser("migrate", help="Execute migration")
    parser_migrate.add_argument(
        "--priority", type=int, help="Migrate specific priority only"
    )
    parser_migrate.add_argument(
        "--dry-run", action="store_true", help="Dry run (no changes)"
    )

    # Validate command
    subparsers.add_parser("validate", help="Validate KB structure")

    # Report command
    subparsers.add_parser("report", help="Generate migration report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    command_map = {
        "scan": cmd_scan,
        "plan": cmd_plan,
        "migrate": cmd_migrate,
        "validate": cmd_validate,
        "report": cmd_report,
    }

    command_map[args.command](args)


if __name__ == "__main__":
    main()
