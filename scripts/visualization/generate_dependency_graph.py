#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Visualization/Generate_dependency_graph]]
Dependency Graph Visualization for TTA Monorepo

Analyzes Python imports to build and visualize dependency relationships
between packages and components.

Usage:
    python scripts/visualization/generate_dependency_graph.py
"""

import ast
import json
import sys
from pathlib import Path


class DependencyAnalyzer:
    """Analyzes Python code to extract dependency information."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.dependencies: dict[str, set[str]] = {}

    def analyze_file(self, file_path: Path) -> set[str]:
        """Extract imports from a Python file."""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])

            return imports
        except Exception:
            return set()

    def analyze_package(self, package_path: Path, package_name: str):
        """Analyze all Python files in a package."""
        python_files = list(package_path.glob("**/*.py"))
        all_imports = set()

        for py_file in python_files:
            imports = self.analyze_file(py_file)
            all_imports.update(imports)

        # Filter to only TTA packages
        tta_imports = {
            imp for imp in all_imports if imp in ["tta_ai", "tta_narrative", "src"]
        }

        self.dependencies[package_name] = tta_imports

    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram from dependencies."""
        lines = ["graph TD"]

        # Define nodes
        lines.append("    tta_ai[TTA AI Framework]")
        lines.append("    tta_narrative[TTA Narrative Engine]")
        lines.append("    tta_app[TTA Application]")

        # Define relationships
        if (
            "tta-narrative-engine" in self.dependencies
            and "tta_ai" in self.dependencies["tta-narrative-engine"]
        ):
            lines.append("    tta_narrative --> tta_ai")

        if "tta-app" in self.dependencies:
            if "tta_ai" in self.dependencies["tta-app"]:
                lines.append("    tta_app --> tta_ai")
            if "tta_narrative" in self.dependencies["tta-app"]:
                lines.append("    tta_app --> tta_narrative")

        # Add styling
        lines.append("")
        lines.append("    classDef framework fill:#e1f5ff,stroke:#01579b")
        lines.append("    classDef engine fill:#f3e5f5,stroke:#4a148c")
        lines.append("    classDef app fill:#e8f5e9,stroke:#1b5e20")
        lines.append("    class tta_ai framework")
        lines.append("    class tta_narrative engine")
        lines.append("    class tta_app app")

        return "\n".join(lines)

    def generate_report(self) -> dict:
        """Generate dependency report."""
        return {
            "packages": list(self.dependencies.keys()),
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "summary": {
                "total_packages": len(self.dependencies),
                "total_dependencies": sum(len(v) for v in self.dependencies.values()),
            },
        }


def main():
    repo_root = Path(__file__).resolve().parents[2]
    analyzer = DependencyAnalyzer(repo_root)

    # Analyze packages
    packages = {
        "tta-ai-framework": repo_root / "packages/tta-ai-framework/src",
        "tta-narrative-engine": repo_root / "packages/tta-narrative-engine/src",
        "tta-app": repo_root / "src",
    }

    for name, path in packages.items():
        if path.exists():
            analyzer.analyze_package(path, name)

    # Generate Mermaid diagram
    mermaid_content = analyzer.generate_mermaid()
    mermaid_file = repo_root / "docs/architecture/dependency-graph.mmd"
    mermaid_file.parent.mkdir(parents=True, exist_ok=True)
    mermaid_file.write_text(mermaid_content)

    # Generate markdown documentation
    md_content = f"""# TTA Dependency Graph

## Package Dependencies

```mermaid
{mermaid_content}
```

## Dependency Details

### TTA AI Framework (`tta-ai-framework`)
- **Purpose**: Reusable AI infrastructure
- **Components**: Agent orchestration, model management, prompt registry
- **Dependencies**: None (base package)

### TTA Narrative Engine (`tta-narrative-engine`)
- **Purpose**: Reusable narrative generation system
- **Components**: Scene generation, narrative orchestration, coherence validation
- **Dependencies**: TTA AI Framework

### TTA Application (`tta-app`)
- **Purpose**: TTA-specific application code
- **Components**: Player experience, API gateway, therapeutic systems
- **Dependencies**: TTA AI Framework, TTA Narrative Engine

## Analysis Report

```json
{json.dumps(analyzer.generate_report(), indent=2)}
```

Generated: {Path(__file__).name}
"""

    md_file = repo_root / "docs/architecture/dependency-graph.md"
    md_file.write_text(md_content)

    sys.stdout.write("✓ Dependency graph generated:\n")
    sys.stdout.write(f"  - Mermaid: {mermaid_file}\n")
    sys.stdout.write(f"  - Documentation: {md_file}\n")


if __name__ == "__main__":
    main()
