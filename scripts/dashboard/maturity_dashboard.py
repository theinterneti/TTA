#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Dashboard/Maturity_dashboard]]
Component Maturity Dashboard for TTA Monorepo

Visualizes component maturity status across all packages with interactive filtering.

Usage:
    python scripts/dashboard/maturity_dashboard.py          # Launch web dashboard
    python scripts/dashboard/maturity_dashboard.py --cli    # CLI output
    python scripts/dashboard/maturity_dashboard.py --html   # Generate static HTML
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table


@dataclass
class ComponentMaturity:
    """Component maturity information."""

    name: str
    package: str
    stage: str
    coverage: float | None
    test_pass_rate: float | None
    linting_status: str
    type_checking_status: str
    promotion_blockers: list[str]
    last_updated: str | None
    file_path: str


class MaturityParser:
    """Parses MATURITY.md files to extract component information."""

    STAGE_PATTERN = r"\*\*Current Stage:\*\*\s+(\w+)"
    COVERAGE_PATTERN = r"Coverage:\s+([\d.]+)%"
    BLOCKERS_PATTERN = r"##\s+Promotion Blockers\s+(.*?)(?=##|$)"

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.components: list[ComponentMaturity] = []

    def find_maturity_files(self) -> list[Path]:
        """Find all MATURITY.md files in the repository."""
        maturity_files = []

        # Search in packages
        packages_dir = self.repo_root / "packages"
        if packages_dir.exists():
            maturity_files.extend(packages_dir.glob("**/MATURITY.md"))

        # Search in src/components
        components_dir = self.repo_root / "src/components"
        if components_dir.exists():
            maturity_files.extend(components_dir.glob("**/MATURITY.md"))

        return maturity_files

    def parse_maturity_file(self, file_path: Path) -> ComponentMaturity | None:
        """Parse a single MATURITY.md file."""
        try:
            content = file_path.read_text()

            # Determine package and component name
            relative_path = file_path.relative_to(self.repo_root)
            parts = relative_path.parts

            if parts[0] == "packages":
                package = parts[1]
                component = parts[-2] if len(parts) > 3 else parts[1]
            elif parts[0] == "src" and parts[1] == "components":
                package = "tta-app"
                component = parts[2] if len(parts) > 3 else "unknown"
            else:
                package = "unknown"
                component = "unknown"

            # Extract stage
            stage_match = re.search(self.STAGE_PATTERN, content)
            stage = stage_match.group(1) if stage_match else "Unknown"

            # Extract coverage
            coverage_match = re.search(self.COVERAGE_PATTERN, content)
            coverage = float(coverage_match.group(1)) if coverage_match else None

            # Extract promotion blockers
            blockers_match = re.search(self.BLOCKERS_PATTERN, content, re.DOTALL)
            blockers = []
            if blockers_match:
                blockers_text = blockers_match.group(1)
                blockers = [
                    line.strip("- ").strip()
                    for line in blockers_text.split("\n")
                    if line.strip().startswith("-")
                ]

            # Extract quality metrics
            linting_status = "✓" if "linting: pass" in content.lower() else "✗"
            type_checking_status = (
                "✓" if "type checking: pass" in content.lower() else "✗"
            )

            return ComponentMaturity(
                name=component,
                package=package,
                stage=stage,
                coverage=coverage,
                test_pass_rate=None,  # Could be extracted if available
                linting_status=linting_status,
                type_checking_status=type_checking_status,
                promotion_blockers=blockers,
                last_updated=None,  # Could be extracted from git
                file_path=str(file_path.relative_to(self.repo_root)),
            )
        except Exception as e:
            sys.stderr.write(f"Error parsing {file_path}: {e}\n")
            return None

    def parse_all(self) -> list[ComponentMaturity]:
        """Parse all MATURITY.md files."""
        maturity_files = self.find_maturity_files()

        for file_path in maturity_files:
            component = self.parse_maturity_file(file_path)
            if component:
                self.components.append(component)

        return self.components


class MaturityDashboard:
    """Generates dashboard visualizations."""

    def __init__(self, components: list[ComponentMaturity]):
        self.components = components
        self.console = Console()

    def filter_components(
        self, stage: str | None = None, package: str | None = None
    ) -> list[ComponentMaturity]:
        """Filter components by criteria."""
        filtered = self.components

        if stage:
            filtered = [c for c in filtered if c.stage.lower() == stage.lower()]

        if package:
            filtered = [c for c in filtered if c.package == package]

        return filtered

    def render_cli(self, stage: str | None = None, package: str | None = None):
        """Render dashboard in CLI using rich."""
        filtered = self.filter_components(stage, package)

        # Summary statistics
        self.console.print("\n[bold cyan]Component Maturity Dashboard[/bold cyan]\n")

        stage_counts = {}
        for component in self.components:
            stage_counts[component.stage] = stage_counts.get(component.stage, 0) + 1

        self.console.print("[bold]Summary:[/bold]")
        for stage_name, count in sorted(stage_counts.items()):
            self.console.print(f"  {stage_name}: {count} components")

        # Detailed table
        table = Table(title="\nComponent Details")
        table.add_column("Component", style="cyan")
        table.add_column("Package", style="magenta")
        table.add_column("Stage", style="green")
        table.add_column("Coverage", justify="right")
        table.add_column("Lint", justify="center")
        table.add_column("Type", justify="center")
        table.add_column("Blockers", justify="right")

        for component in filtered:
            coverage_str = f"{component.coverage:.1f}%" if component.coverage else "N/A"
            blockers_str = str(len(component.promotion_blockers))

            # Color code based on stage
            stage_color = {
                "Development": "yellow",
                "Staging": "blue",
                "Production": "green",
            }.get(component.stage, "white")

            table.add_row(
                component.name,
                component.package,
                f"[{stage_color}]{component.stage}[/{stage_color}]",
                coverage_str,
                component.linting_status,
                component.type_checking_status,
                blockers_str,
            )

        self.console.print(table)

        # Show blockers for components with issues
        components_with_blockers = [c for c in filtered if c.promotion_blockers]
        if components_with_blockers:
            self.console.print("\n[bold red]Promotion Blockers:[/bold red]")
            for component in components_with_blockers:
                self.console.print(
                    f"\n[bold]{component.name}[/bold] ({component.package}):"
                )
                for blocker in component.promotion_blockers:
                    self.console.print(f"  • {blocker}")

    def generate_html(self, output_path: Path):
        """Generate static HTML dashboard."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TTA Component Maturity Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card.development { background: #fff3cd; }
        .summary-card.staging { background: #cfe2ff; }
        .summary-card.production { background: #d1e7dd; }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            text-transform: uppercase;
            color: #666;
        }
        .summary-card .count {
            font-size: 36px;
            font-weight: bold;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #007bff;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge.development { background: #ffc107; color: #000; }
        .badge.staging { background: #0d6efd; color: #fff; }
        .badge.production { background: #198754; color: #fff; }
        .status-icon {
            font-size: 18px;
        }
        .blockers {
            margin-top: 30px;
        }
        .blocker-item {
            background: #fff3cd;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
        }
        .blocker-item h4 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .blocker-item ul {
            margin: 0;
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 TTA Component Maturity Dashboard</h1>

        <div class="summary">
"""

        # Add summary cards
        stage_counts = {}
        for component in self.components:
            stage_counts[component.stage] = stage_counts.get(component.stage, 0) + 1

        for stage in ["Development", "Staging", "Production"]:
            count = stage_counts.get(stage, 0)
            html_content += f"""
            <div class="summary-card {stage.lower()}">
                <h3>{stage}</h3>
                <div class="count">{count}</div>
            </div>
"""

        html_content += """
        </div>

        <table>
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Package</th>
                    <th>Stage</th>
                    <th>Coverage</th>
                    <th>Lint</th>
                    <th>Type</th>
                    <th>Blockers</th>
                </tr>
            </thead>
            <tbody>
"""

        # Add component rows
        for component in self.components:
            coverage_str = f"{component.coverage:.1f}%" if component.coverage else "N/A"
            stage_class = component.stage.lower()

            html_content += f"""
                <tr>
                    <td><strong>{component.name}</strong></td>
                    <td>{component.package}</td>
                    <td><span class="badge {stage_class}">{component.stage}</span></td>
                    <td>{coverage_str}</td>
                    <td class="status-icon">{component.linting_status}</td>
                    <td class="status-icon">{component.type_checking_status}</td>
                    <td>{len(component.promotion_blockers)}</td>
                </tr>
"""

        html_content += """
            </tbody>
        </table>
"""

        # Add blockers section
        components_with_blockers = [c for c in self.components if c.promotion_blockers]
        if components_with_blockers:
            html_content += """
        <div class="blockers">
            <h2>⚠️ Promotion Blockers</h2>
"""
            for component in components_with_blockers:
                html_content += f"""
            <div class="blocker-item">
                <h4>{component.name} ({component.package})</h4>
                <ul>
"""
                for blocker in component.promotion_blockers:
                    html_content += f"                    <li>{blocker}</li>\n"

                html_content += """
                </ul>
            </div>
"""

            html_content += """
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        output_path.write_text(html_content)
        sys.stdout.write(f"✓ HTML dashboard generated: {output_path}\n")


def main():
    parser = argparse.ArgumentParser(description="TTA Component Maturity Dashboard")
    parser.add_argument("--cli", action="store_true", help="Display CLI dashboard")
    parser.add_argument("--html", action="store_true", help="Generate static HTML")
    parser.add_argument(
        "--stage", help="Filter by stage (Development, Staging, Production)"
    )
    parser.add_argument("--package", help="Filter by package name")
    parser.add_argument(
        "--output", default="maturity_dashboard.html", help="HTML output file"
    )

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]

    # Parse maturity files
    parser_obj = MaturityParser(repo_root)
    components = parser_obj.parse_all()

    if not components:
        sys.stdout.write("No MATURITY.md files found in the repository.\n")
        return

    # Create dashboard
    dashboard = MaturityDashboard(components)

    if args.html:
        output_path = repo_root / args.output
        dashboard.generate_html(output_path)
    else:
        # Default to CLI
        dashboard.render_cli(stage=args.stage, package=args.package)


if __name__ == "__main__":
    main()
