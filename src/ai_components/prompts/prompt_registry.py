"""
Prompt Registry for centralized prompt management and versioning.

Provides:
- Version-controlled prompt loading
- Performance tracking and baselines
- A/B testing support
- Prompt template rendering
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class PromptMetrics:
    """Performance metrics for a prompt."""

    prompt_id: str
    version: str
    total_calls: int = 0
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    total_cost_usd: float = 0.0
    quality_scores: list[float] = field(default_factory=list)
    error_count: int = 0
    last_updated: float = field(default_factory=time.time)

    @property
    def avg_tokens(self) -> float:
        """Average tokens per call."""
        return self.total_tokens / max(self.total_calls, 1)

    @property
    def avg_latency_ms(self) -> float:
        """Average latency in milliseconds."""
        return self.total_latency_ms / max(self.total_calls, 1)

    @property
    def avg_cost_usd(self) -> float:
        """Average cost per call in USD."""
        return self.total_cost_usd / max(self.total_calls, 1)

    @property
    def avg_quality_score(self) -> float:
        """Average quality score."""
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores) / len(self.quality_scores)

    @property
    def error_rate(self) -> float:
        """Error rate as a percentage."""
        return (self.error_count / max(self.total_calls, 1)) * 100

    def record_call(
        self,
        tokens: int,
        latency_ms: float,
        cost_usd: float,
        quality_score: float | None = None,
        error: bool = False,
    ) -> None:
        """Record a prompt call with metrics."""
        self.total_calls += 1
        self.total_tokens += tokens
        self.total_latency_ms += latency_ms
        self.total_cost_usd += cost_usd

        if quality_score is not None:
            self.quality_scores.append(quality_score)

        if error:
            self.error_count += 1

        self.last_updated = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "prompt_id": self.prompt_id,
            "version": self.version,
            "total_calls": self.total_calls,
            "avg_tokens": self.avg_tokens,
            "avg_latency_ms": self.avg_latency_ms,
            "avg_cost_usd": self.avg_cost_usd,
            "avg_quality_score": self.avg_quality_score,
            "error_rate": self.error_rate,
            "last_updated": self.last_updated,
        }


@dataclass
class PromptTemplate:
    """A versioned prompt template."""

    prompt_id: str
    version: str
    template: str
    variables: list[str]
    description: str
    agent_type: str
    created_at: str
    author: str
    performance_baseline: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs: Any) -> str:
        """Render the prompt template with variables."""
        # Validate all required variables are provided
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(
                f"Missing required variables for prompt '{self.prompt_id}': {missing_vars}"
            )

        # Render template
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Error rendering prompt '{self.prompt_id}': {e}") from e

    def get_hash(self) -> str:
        """Get a hash of the prompt template for deduplication."""
        content = f"{self.prompt_id}:{self.version}:{self.template}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "prompt_id": self.prompt_id,
            "version": self.version,
            "template": self.template,
            "variables": self.variables,
            "description": self.description,
            "agent_type": self.agent_type,
            "created_at": self.created_at,
            "author": self.author,
            "performance_baseline": self.performance_baseline,
            "metadata": self.metadata,
        }


class PromptRegistry:
    """
    Central registry for managing versioned prompts.

    Features:
    - Load prompts from YAML files
    - Version management with active version tracking
    - Performance metrics collection
    - A/B testing support
    - Prompt template rendering
    """

    def __init__(self, prompts_dir: str | Path | None = None):
        """
        Initialize the prompt registry.

        Args:
            prompts_dir: Path to prompts directory. Defaults to src/ai_components/prompts/
        """
        if prompts_dir is None:
            # Default to src/ai_components/prompts/
            prompts_dir = Path(__file__).parent
        else:
            prompts_dir = Path(prompts_dir)

        self.prompts_dir = prompts_dir
        self.versions_dir = prompts_dir / "versions"
        self.active_dir = prompts_dir / "active"
        self.registry_file = prompts_dir / "registry.yaml"

        # Loaded prompts and metrics
        self.prompts: dict[
            str, dict[str, PromptTemplate]
        ] = {}  # {prompt_id: {version: template}}
        self.active_versions: dict[str, str] = {}  # {prompt_id: active_version}
        self.metrics: dict[str, PromptMetrics] = {}  # {prompt_id:version: metrics}

        # Load registry
        self._load_registry()

    def _load_registry(self) -> None:
        """Load the prompt registry from YAML."""
        if not self.registry_file.exists():
            logger.warning(f"Registry file not found: {self.registry_file}")
            return

        with self.registry_file.open(encoding="utf-8") as f:
            registry_data = yaml.safe_load(f)

        if not registry_data or "prompts" not in registry_data:
            logger.warning("Empty or invalid registry file")
            return

        # Load active versions
        for prompt_id, prompt_info in registry_data["prompts"].items():
            self.active_versions[prompt_id] = prompt_info.get("active_version", "1.0.0")

        logger.info(f"Loaded registry with {len(self.active_versions)} prompts")

    def load_prompt(self, prompt_id: str, version: str | None = None) -> PromptTemplate:
        """
        Load a prompt template by ID and version.

        Args:
            prompt_id: The prompt identifier
            version: The version to load. If None, loads active version.

        Returns:
            PromptTemplate instance

        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If prompt is invalid
        """
        # Use active version if not specified
        if version is None:
            version = self.active_versions.get(prompt_id)
            if version is None:
                raise ValueError(f"No active version found for prompt '{prompt_id}'")

        # Check cache
        cache_key = f"{prompt_id}:{version}"
        if prompt_id in self.prompts and version in self.prompts[prompt_id]:
            return self.prompts[prompt_id][version]

        # Load from file
        prompt_file = self.versions_dir / f"v{version}" / f"{prompt_id}.yaml"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        with prompt_file.open(encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)

        # Create template
        template = PromptTemplate(
            prompt_id=prompt_id,
            version=prompt_data["version"],
            template=prompt_data["template"],
            variables=prompt_data.get("variables", []),
            description=prompt_data.get("description", ""),
            agent_type=prompt_data.get("agent_type", "unknown"),
            created_at=prompt_data.get("created_at", ""),
            author=prompt_data.get("author", "unknown"),
            performance_baseline=prompt_data.get("performance_baseline", {}),
            metadata=prompt_data.get("metadata", {}),
        )

        # Cache template
        if prompt_id not in self.prompts:
            self.prompts[prompt_id] = {}
        self.prompts[prompt_id][version] = template

        # Initialize metrics if not exists
        if cache_key not in self.metrics:
            self.metrics[cache_key] = PromptMetrics(
                prompt_id=prompt_id,
                version=version,
            )

        logger.info(f"Loaded prompt '{prompt_id}' version {version}")
        return template

    def get_active_version(self, prompt_id: str) -> str:
        """Get the active version for a prompt."""
        version = self.active_versions.get(prompt_id)
        if version is None:
            raise ValueError(f"No active version found for prompt '{prompt_id}'")
        return version

    def render_prompt(
        self, prompt_id: str, version: str | None = None, **kwargs: Any
    ) -> str:
        """
        Render a prompt with variables.

        Args:
            prompt_id: The prompt identifier
            version: The version to use. If None, uses active version.
            **kwargs: Variables to render the prompt with

        Returns:
            Rendered prompt string
        """
        template = self.load_prompt(prompt_id, version)
        return template.render(**kwargs)

    def record_metrics(
        self,
        prompt_id: str,
        version: str | None = None,
        tokens: int = 0,
        latency_ms: float = 0.0,
        cost_usd: float = 0.0,
        quality_score: float | None = None,
        error: bool = False,
    ) -> None:
        """Record performance metrics for a prompt call."""
        if version is None:
            version = self.get_active_version(prompt_id)

        cache_key = f"{prompt_id}:{version}"
        if cache_key not in self.metrics:
            self.metrics[cache_key] = PromptMetrics(
                prompt_id=prompt_id,
                version=version,
            )

        self.metrics[cache_key].record_call(
            tokens=tokens,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            quality_score=quality_score,
            error=error,
        )

    def get_metrics(self, prompt_id: str, version: str | None = None) -> PromptMetrics:
        """Get performance metrics for a prompt."""
        if version is None:
            version = self.get_active_version(prompt_id)

        cache_key = f"{prompt_id}:{version}"
        if cache_key not in self.metrics:
            self.metrics[cache_key] = PromptMetrics(
                prompt_id=prompt_id,
                version=version,
            )

        return self.metrics[cache_key]

    def get_baseline_scores(
        self, prompt_id: str, version: str | None = None
    ) -> dict[str, Any]:
        """Get baseline performance scores for a prompt."""
        template = self.load_prompt(prompt_id, version)
        return template.performance_baseline

    def list_prompts(self) -> list[str]:
        """List all available prompt IDs."""
        return list(self.active_versions.keys())

    def list_versions(self, prompt_id: str) -> list[str]:
        """List all available versions for a prompt."""
        if prompt_id not in self.prompts:
            # Try to discover versions from filesystem
            versions = []
            for version_dir in self.versions_dir.glob("v*"):
                prompt_file = version_dir / f"{prompt_id}.yaml"
                if prompt_file.exists():
                    versions.append(version_dir.name[1:])  # Remove 'v' prefix
            return sorted(versions)

        return sorted(self.prompts[prompt_id].keys())

    def export_metrics(self) -> dict[str, Any]:
        """Export all metrics as a dictionary."""
        return {
            cache_key: metrics.to_dict() for cache_key, metrics in self.metrics.items()
        }
