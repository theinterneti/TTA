"""Component Registry for TTA Maturity Tracking."""

# Logseq: [[TTA.dev/Scripts/Registry/Component_registry]]

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Import metrics collector
from scripts.maturity.metrics_collector import collect_metrics_from_metadata

logger = logging.getLogger(__name__)


@dataclass
class ComponentMetadata:
    """Metadata for a single TTA component."""

    name: str  # Component identifier (e.g., 'carbon', 'neo4j')
    display_name: str  # Human-readable name (e.g., 'Carbon Component')
    component_type: str  # core/infrastructure/feature/unknown
    source_path: Path  # Path to component source file
    test_path: Path | None = None  # Path to test file (if exists)
    maturity_file: Path | None = None  # Path to MATURITY.md (if exists)
    owner: str = "unknown"  # Component owner
    functional_group: str = "unknown"  # Functional grouping
    current_stage: str = "Development"  # dev/staging/production
    dependencies: list[str] = field(default_factory=list)  # Component dependencies
    last_metrics: dict[str, Any] | None = None  # Latest metrics (serialized)
    last_updated: str | None = None  # Last metrics collection timestamp (ISO format)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert Path objects to strings
        data["source_path"] = str(self.source_path)
        data["test_path"] = str(self.test_path) if self.test_path else None
        data["maturity_file"] = str(self.maturity_file) if self.maturity_file else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComponentMetadata":
        """Create from dictionary (JSON deserialization)."""
        # Convert string paths back to Path objects
        data["source_path"] = Path(data["source_path"])
        if data.get("test_path"):
            data["test_path"] = Path(data["test_path"])
        if data.get("maturity_file"):
            data["maturity_file"] = Path(data["maturity_file"])
        return cls(**data)


class ComponentRegistry:
    """
    Central registry for TTA components with maturity tracking.

    This registry automatically discovers components, collects their metrics,
    and provides a unified interface for querying component status.
    """

    def __init__(self, cache_path: Path | None = None, auto_discover: bool = True):
        """
        Initialize the component registry.

        Args:
            cache_path: Path to cache file (default: scripts/registry/.component_registry.json)
            auto_discover: Whether to auto-discover components on init
        """
        self.cache_path = cache_path or Path(
            "scripts/registry/.component_registry.json"
        )
        self.components: dict[str, ComponentMetadata] = {}
        self.last_discovery: datetime | None = None

        # Try to load from cache first
        if self.cache_path.exists():
            logger.info(f"Loading registry from cache: {self.cache_path}")
            self.load_registry()

        # Discover components if cache doesn't exist or auto_discover is True and cache is stale
        if auto_discover and (not self.cache_path.exists() or self._is_stale()):
            self.refresh()

    def refresh(self) -> None:
        """Re-discover components and update registry."""
        logger.info("Discovering TTA components...")
        self.components = {}
        self._discover_components()
        self.last_discovery = datetime.now()
        logger.info(f"Discovered {len(self.components)} components")

    def _discover_components(self) -> None:
        """Scan codebase to discover all TTA components."""
        src_components = Path("src/components")

        if not src_components.exists():
            logger.warning(f"Components directory not found: {src_components}")
            return

        # Find all *_component.py files
        component_files = list(src_components.glob("**/*_component.py"))
        logger.info(f"Found {len(component_files)} component files")

        for component_file in component_files:
            try:
                component = self._create_component_metadata(component_file)
                self.components[component.name] = component
                logger.debug(f"Registered component: {component.name}")
            except Exception as e:  # noqa: PERF203
                logger.error(f"Failed to process {component_file}: {e}")

    def _create_component_metadata(self, source_path: Path) -> ComponentMetadata:
        """Create component metadata from source file."""
        # Extract component name from filename
        # e.g., carbon_component.py -> carbon
        # e.g., model_management_component.py -> model_management
        filename = source_path.stem  # Remove .py extension
        if filename.endswith("_component"):
            name = filename[: -len("_component")]
        else:
            name = filename

        # Create display name (capitalize and add spaces)
        display_name = name.replace("_", " ").title() + " Component"

        # Find test file
        test_path = self._find_test_file(name)

        # Find MATURITY.md file
        maturity_file = self._find_maturity_file(source_path, name)

        # Parse MATURITY.md for metadata
        owner = "unknown"
        functional_group = "unknown"
        current_stage = "Development"
        component_type = "unknown"

        if maturity_file and maturity_file.exists():
            metadata = self._parse_maturity_metadata(maturity_file)
            owner = metadata.get("owner", owner)
            functional_group = metadata.get("functional_group", functional_group)
            current_stage = metadata.get("current_stage", current_stage)
            component_type = metadata.get("component_type", component_type)

        return ComponentMetadata(
            name=name,
            display_name=display_name,
            component_type=component_type,
            source_path=source_path,
            test_path=test_path,
            maturity_file=maturity_file,
            owner=owner,
            functional_group=functional_group,
            current_stage=current_stage,
        )

    def _find_test_file(self, component_name: str) -> Path | None:
        """Find test file for component."""
        tests_dir = Path("tests")

        # Try multiple patterns
        patterns = [
            f"test_{component_name}.py",  # Dedicated test file
            f"test_{component_name}_*.py",  # Test file with suffix
            "test_components.py",  # Shared test file
        ]

        for pattern in patterns:
            matches = list(tests_dir.glob(f"**/{pattern}"))
            if matches:
                return matches[0]  # Return first match

        return None

    def _find_maturity_file(
        self, source_path: Path, component_name: str
    ) -> Path | None:
        """Find MATURITY.md file for component."""
        # Priority 1: Check in subdirectory named after component
        # e.g., src/components/neo4j/MATURITY.md for neo4j_component.py
        subdir = source_path.parent / component_name / "MATURITY.md"
        if subdir.exists():
            return subdir

        # Priority 2: Check in same directory as source file
        # e.g., src/components/carbon/MATURITY.md for carbon/carbon_component.py
        same_dir = source_path.parent / "MATURITY.md"
        if same_dir.exists() and source_path.parent.name != "components":
            # Only use if not in root components directory (avoid template)
            return same_dir

        return None

    def _parse_maturity_metadata(self, maturity_file: Path) -> dict[str, str]:
        """Parse metadata from MATURITY.md header."""
        metadata = {}

        try:
            content = maturity_file.read_text()

            # Extract metadata from header using regex
            # Format: **Key**: Value or **Key**: **Value**
            patterns = {
                "owner": r"\*\*Owner\*\*:\s*(.+)",
                "functional_group": r"\*\*Functional Group\*\*:\s*(.+)",
                "current_stage": r"\*\*Current Stage\*\*:\s*(?:\*\*)?(.+?)(?:\*\*)?(?:\s|$)",
                "component_type": r"\*\*Type\*\*:\s*(.+)",
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Clean up emoji and extra formatting
                    value = re.sub(r"[🎉⚠️✅❌]", "", value).strip()

                    # For stage, extract just the stage name (remove parenthetical notes)
                    if key == "current_stage":
                        # Extract first word (Development, Staging, Production)
                        stage_match = re.match(
                            r"(Development|Staging|Production)", value, re.IGNORECASE
                        )
                        if stage_match:
                            value = stage_match.group(1)

                    metadata[key] = value

        except Exception as e:
            logger.warning(f"Failed to parse {maturity_file}: {e}")

        return metadata

    def get_all_components(self) -> list[ComponentMetadata]:
        """Get all registered components."""
        return list(self.components.values())

    def get_component(self, name: str) -> ComponentMetadata | None:
        """Get specific component by name."""
        return self.components.get(name)

    def get_components_by_stage(self, stage: str) -> list[ComponentMetadata]:
        """Get components filtered by maturity stage."""
        return [c for c in self.components.values() if c.current_stage == stage]

    def get_promotion_candidates(self) -> list[ComponentMetadata]:
        """
        Get components that meet staging promotion criteria.

        Criteria for Development → Staging:
        - Coverage ≥ 70%
        - 0 linting violations
        - 0 type errors
        - 0 security issues
        - All tests passing
        """
        candidates = []

        for component in self.components.values():
            # Skip if already in staging or production
            if component.current_stage in ["Staging", "Production"]:
                continue

            # Check if metrics are available
            if not component.last_metrics:
                continue

            metrics = component.last_metrics

            # Check all criteria
            coverage_ok = metrics.get("coverage", {}).get("percentage", 0) >= 70.0
            linting_ok = metrics.get("linting", {}).get("total_violations", 1) == 0
            type_check_ok = metrics.get("type_checking", {}).get("errors", 1) == 0
            security_ok = metrics.get("security", {}).get("total_issues", 1) == 0
            tests_ok = metrics.get("tests", {}).get("failed", 1) == 0

            if all([coverage_ok, linting_ok, type_check_ok, security_ok, tests_ok]):
                candidates.append(component)

        return candidates

    def save_registry(self, path: Path | None = None) -> None:
        """Persist registry to JSON file."""
        save_path = path or self.cache_path
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "last_discovery": (
                self.last_discovery.isoformat() if self.last_discovery else None
            ),
            "components": {
                name: component.to_dict() for name, component in self.components.items()
            },
        }

        with save_path.open("w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Registry saved to {save_path}")

    def load_registry(self, path: Path | None = None) -> bool:
        """Load registry from JSON file."""
        load_path = path or self.cache_path

        if not load_path.exists():
            logger.warning(f"Registry cache not found at {load_path}")
            return False

        try:
            with load_path.open() as f:
                data = json.load(f)

            self.last_discovery = (
                datetime.fromisoformat(data["last_discovery"])
                if data.get("last_discovery")
                else None
            )

            self.components = {
                name: ComponentMetadata.from_dict(comp_data)
                for name, comp_data in data.get("components", {}).items()
            }

            logger.info(f"Registry loaded from {load_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return False

    def _is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if registry cache is stale."""
        if not self.last_discovery:
            return True

        age = datetime.now() - self.last_discovery
        return age.total_seconds() > (max_age_hours * 3600)

    def update_all_metrics(self, dry_run: bool = False) -> dict[str, Any]:
        """
        Collect metrics for all components and update registry.

        Args:
            dry_run: If True, collect metrics but don't save to registry

        Returns:
            Dict with results: {updated: [], failed: [], skipped: [], total: int}
        """
        results = {"updated": [], "failed": [], "skipped": [], "total": 0}

        for component in self.get_all_components():
            results["total"] += 1

            try:
                logger.info(f"Collecting metrics for {component.name}...")

                # Collect metrics
                metrics = collect_metrics_from_metadata(component)

                # Convert to dict for storage
                metrics_dict = {
                    "coverage": {
                        "percentage": metrics.coverage.percentage,
                        "lines_covered": metrics.coverage.lines_covered,
                        "lines_total": metrics.coverage.lines_total,
                    },
                    "linting": {
                        "total_violations": metrics.linting.total_violations,
                        "by_rule": metrics.linting.by_rule,
                    },
                    "type_checking": {
                        "errors": metrics.type_checking.errors,
                        "warnings": metrics.type_checking.warnings,
                    },
                    "security": {"total_issues": metrics.security.total_issues},
                    "tests": {
                        "passed": metrics.tests.passed,
                        "failed": metrics.tests.failed,
                        "skipped": metrics.tests.skipped,
                        "total": metrics.tests.total,
                    },
                }

                if not dry_run:
                    # Update component metadata
                    component.last_metrics = metrics_dict
                    component.last_updated = datetime.now().isoformat()

                results["updated"].append(
                    {
                        "name": component.name,
                        "coverage": metrics.coverage.percentage,
                        "meets_staging": metrics.meets_staging_criteria(),
                    }
                )

            except Exception as e:
                logger.error(f"Failed to collect metrics for {component.name}: {e}")
                results["failed"].append({"component": component.name, "error": str(e)})

        # Save updated registry
        if not dry_run and results["updated"]:
            self.save_registry()

        return results
