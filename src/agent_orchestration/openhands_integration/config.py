"""
Configuration models for OpenHands integration.

Provides:
- OpenHandsConfig: SDK client configuration
- OpenHandsModelConfig: Model metadata
- OpenHandsIntegrationConfig: Complete integration configuration
- FREE_MODELS: Catalog of free OpenRouter models
- ModelRegistry: YAML-based model registry with filtering and prioritization
"""

from __future__ import annotations

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, ValidationError, field_validator

logger = logging.getLogger(__name__)


# ============================================================================
# Registry Models
# ============================================================================


class CompatibilityStatus(str, Enum):
    """Model compatibility status."""

    VERIFIED = "verified"
    UNTESTED = "untested"
    INCOMPATIBLE = "incompatible"
    RATE_LIMITED = "rate_limited"


class QualityTier(str, Enum):
    """Model quality tier."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ModelRegistryEntry(BaseModel):
    """Single model entry in the registry."""

    model_id: str = Field(description="OpenRouter model identifier with prefix")
    display_name: str = Field(description="Human-readable model name")
    provider: str = Field(description="Model provider (DeepSeek, Qwen, etc.)")
    compatibility_status: CompatibilityStatus = Field(
        description="Compatibility status"
    )
    quality_tier: QualityTier = Field(description="Quality classification")
    context_window: int = Field(description="Maximum context tokens", gt=0)
    supports_system_prompt: bool = Field(
        description="Whether model supports system prompts"
    )
    known_issues: list[str] = Field(
        default_factory=list, description="Known compatibility issues"
    )
    last_tested: str | None = Field(
        default=None, description="Last test date (ISO format)"
    )
    validation_notes: str | None = Field(
        default=None, description="Testing observations"
    )
    expected_latency_ms: int | None = Field(
        default=None, description="Expected latency range", gt=0
    )
    capabilities: list[str] = Field(
        default_factory=list, description="Model capabilities"
    )


class ModelRegistry(BaseModel):
    """Complete model registry."""

    version: str = Field(description="Registry schema version")
    last_updated: str = Field(description="Last update date (ISO format)")
    description: str = Field(description="Registry description")
    models: dict[str, ModelRegistryEntry] = Field(
        description="Model entries by ID"
    )


# ============================================================================
# Legacy Models (for backward compatibility)
# ============================================================================


class OpenHandsModelConfig(BaseModel):
    """Configuration for a specific OpenRouter model."""

    model_id: str = Field(description="OpenRouter model identifier")
    display_name: str = Field(description="Human-readable model name")
    context_tokens: int = Field(description="Maximum context tokens")
    is_free: bool = Field(description="Whether model is free tier")
    recommended: bool = Field(default=False, description="Recommended for TTA")


# ============================================================================
# Registry Loading and Fallback
# ============================================================================

# Global registry cache
_registry_cache: ModelRegistry | None = None
_registry_loaded: bool = False


def get_hardcoded_fallback_models() -> list[str]:
    """
    Get hardcoded fallback models (minimal verified set).

    Returns:
        List of model IDs that are known to work
    """
    return [
        "openrouter/deepseek/deepseek-chat",  # Verified working
        "openrouter/qwen/qwen3-coder:free",  # Rate-limited but functional
    ]


def load_model_registry() -> ModelRegistry | None:
    """
    Load model registry from YAML file with error handling.

    Returns:
        ModelRegistry instance or None on failure
    """
    registry_path = Path(__file__).parent / "free_models_registry.yaml"

    try:
        if not registry_path.exists():
            logger.warning(f"Registry file not found: {registry_path}")
            return None

        with registry_path.open(encoding="utf-8") as f:
            registry_data = yaml.safe_load(f)

        if not registry_data:
            logger.warning("Empty registry file")
            return None

        # Validate with Pydantic
        registry = ModelRegistry(**registry_data)
        logger.info(f"Loaded registry with {len(registry.models)} models")
        return registry

    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in registry: {e}")
        return None
    except ValidationError as e:
        logger.error(f"Registry validation error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading registry: {e}")
        return None


def get_model_registry() -> ModelRegistry | None:
    """
    Get model registry (singleton with lazy loading).

    Returns:
        ModelRegistry instance or None if loading failed
    """
    global _registry_cache, _registry_loaded

    if not _registry_loaded:
        _registry_cache = load_model_registry()
        _registry_loaded = True

    return _registry_cache


def _clear_registry_cache() -> None:
    """Clear registry cache (for testing purposes)."""
    global _registry_cache, _registry_loaded
    _registry_cache = None
    _registry_loaded = False


# ============================================================================
# Model Filtering and Prioritization
# ============================================================================


def filter_models(
    registry: ModelRegistry | None = None,
    compatibility_statuses: list[CompatibilityStatus] | None = None,
    providers: list[str] | None = None,
    quality_tiers: list[QualityTier] | None = None,
    min_context_window: int = 0,
    require_system_prompt: bool = True,
    exclude_incompatible: bool = True,
    capabilities: list[str] | None = None,
) -> list[ModelRegistryEntry]:
    """
    Filter models based on criteria.

    Args:
        registry: ModelRegistry instance (uses singleton if None)
        compatibility_statuses: List of acceptable statuses (default: verified, rate_limited)
        providers: List of acceptable providers (default: all)
        quality_tiers: List of acceptable quality tiers (default: all)
        min_context_window: Minimum context window size (default: 0)
        require_system_prompt: Require system prompt support (default: True)
        exclude_incompatible: Exclude incompatible models (default: True)
        capabilities: Required capabilities (default: none)

    Returns:
        List of filtered ModelRegistryEntry objects

    Example:
        >>> # Get only verified high-quality models
        >>> models = filter_models(
        ...     compatibility_statuses=[CompatibilityStatus.VERIFIED],
        ...     quality_tiers=[QualityTier.HIGH]
        ... )
    """
    # Get registry (use provided or load singleton)
    if registry is None:
        registry = get_model_registry()

    # If no registry, return empty list (will trigger fallback)
    if registry is None:
        logger.warning("No registry available for filtering")
        return []

    # Default filters
    if compatibility_statuses is None:
        compatibility_statuses = [
            CompatibilityStatus.VERIFIED,
            CompatibilityStatus.RATE_LIMITED,
        ]

    # Filter models
    filtered = []
    for model_id, model in registry.models.items():
        # Filter by compatibility status
        if model.compatibility_status not in compatibility_statuses:
            continue

        # Exclude incompatible if requested
        if (
            exclude_incompatible
            and model.compatibility_status == CompatibilityStatus.INCOMPATIBLE
        ):
            continue

        # Filter by provider
        if providers and model.provider not in providers:
            continue

        # Filter by quality tier
        if quality_tiers and model.quality_tier not in quality_tiers:
            continue

        # Filter by context window
        if model.context_window < min_context_window:
            continue

        # Filter by system prompt support
        if require_system_prompt and not model.supports_system_prompt:
            continue

        # Filter by capabilities
        if capabilities:
            if not all(cap in model.capabilities for cap in capabilities):
                continue

        filtered.append(model)

    logger.info(
        f"Filtered {len(filtered)} models from {len(registry.models)} total"
    )
    return filtered


def prioritize_models(models: list[ModelRegistryEntry]) -> list[str]:
    """
    Prioritize models based on weighted scoring algorithm.

    Scoring:
        - Status weights: verified=100, untested=50, rate_limited=25, incompatible=0
        - Quality weights: high=30, medium=20, low=10
        - Provider diversity bonus: +10 for underrepresented providers (count <= 2)

    Args:
        models: List of ModelRegistryEntry objects to prioritize

    Returns:
        List of model IDs ordered by priority (highest first)

    Example:
        >>> filtered = filter_models()
        >>> prioritized = prioritize_models(filtered)
        >>> # Returns: ['openrouter/deepseek/deepseek-chat', ...]
    """
    if not models:
        return []

    # Status weights
    status_weights = {
        CompatibilityStatus.VERIFIED: 100,
        CompatibilityStatus.UNTESTED: 50,
        CompatibilityStatus.RATE_LIMITED: 25,
        CompatibilityStatus.INCOMPATIBLE: 0,
    }

    # Quality weights
    quality_weights = {
        QualityTier.HIGH: 30,
        QualityTier.MEDIUM: 20,
        QualityTier.LOW: 10,
    }

    # Calculate provider diversity bonus
    provider_counts: dict[str, int] = {}
    for model in models:
        provider_counts[model.provider] = (
            provider_counts.get(model.provider, 0) + 1
        )

    # Score each model
    scored_models = []
    for model in models:
        score = 0

        # Status weight
        score += status_weights.get(model.compatibility_status, 0)

        # Quality weight
        score += quality_weights.get(model.quality_tier, 0)

        # Provider diversity bonus (favor underrepresented providers)
        if provider_counts[model.provider] <= 2:
            score += 10

        scored_models.append((score, model.model_id))
        logger.debug(f"Model {model.model_id}: score={score}")

    # Sort by score (descending)
    scored_models.sort(key=lambda x: x[0], reverse=True)

    # Return ordered model IDs
    prioritized = [model_id for score, model_id in scored_models]
    logger.info(f"Prioritized {len(prioritized)} models")
    return prioritized


def get_fallback_model_chain(
    compatibility_statuses: list[CompatibilityStatus] | None = None,
    providers: list[str] | None = None,
    quality_tiers: list[QualityTier] | None = None,
    min_context_window: int = 0,
    require_system_prompt: bool = True,
    max_models: int = 5,
) -> list[str]:
    """
    Get prioritized fallback model chain.

    Args:
        compatibility_statuses: List of acceptable statuses (default: verified, rate_limited)
        providers: List of acceptable providers (default: all)
        quality_tiers: List of acceptable quality tiers (default: all)
        min_context_window: Minimum context window size (default: 0)
        require_system_prompt: Require system prompt support (default: True)
        max_models: Maximum number of models to return (default: 5)

    Returns:
        List of model IDs ordered by priority (always returns at least hardcoded fallback)

    Example:
        >>> # Get top 5 verified models
        >>> chain = get_fallback_model_chain(
        ...     compatibility_statuses=[CompatibilityStatus.VERIFIED],
        ...     max_models=5
        ... )
        >>> # Returns: ['openrouter/deepseek/deepseek-chat', ...]
    """
    # Load registry
    registry = get_model_registry()

    # Filter models
    filtered = filter_models(
        registry=registry,
        compatibility_statuses=compatibility_statuses,
        providers=providers,
        quality_tiers=quality_tiers,
        min_context_window=min_context_window,
        require_system_prompt=require_system_prompt,
    )

    # Prioritize models
    prioritized = prioritize_models(filtered)

    # Limit to max_models
    chain = prioritized[:max_models]

    # If empty, use hardcoded fallback
    if not chain:
        logger.warning("No models matched filters, using hardcoded fallback")
        chain = get_hardcoded_fallback_models()

    logger.info(f"Fallback chain: {chain}")
    return chain


# Preset mapping (for backward compatibility)
PRESET_TO_MODEL_ID = {
    "deepseek-v3": "openrouter/deepseek/deepseek-chat-v3.1:free",
    "mistral-small": "openrouter/mistralai/mistral-small-3.2-24b-instruct:free",
    "gemini-flash": "openrouter/google/gemini-2.0-flash-exp:free",
    "llama-scout": "openrouter/meta-llama/llama-4-scout:free",
    "deepseek-r1": "openrouter/deepseek/deepseek-r1-0528-qwen3-8b:free",
}


def get_model_by_preset(preset: str) -> str:
    """
    Get model ID by preset name (backward compatibility).

    Args:
        preset: Preset name (deepseek-v3, mistral-small, etc.)

    Returns:
        Model ID for the preset

    Example:
        >>> model_id = get_model_by_preset("deepseek-v3")
        >>> # Returns: "openrouter/deepseek/deepseek-chat-v3.1:free"
    """
    model_id = PRESET_TO_MODEL_ID.get(preset)
    if model_id is None:
        logger.warning(f"Unknown preset '{preset}', using default")
        return PRESET_TO_MODEL_ID["gemini-flash"]
    return model_id


# ============================================================================
# Legacy Free Model Catalog (for backward compatibility)
# ============================================================================

# Free model catalog
FREE_MODELS = {
    "deepseek-v3": OpenHandsModelConfig(
        model_id="openrouter/deepseek/deepseek-chat-v3.1:free",
        display_name="DeepSeek Chat V3.1 (Free)",
        context_tokens=64_000,
        is_free=True,
        recommended=True,  # Default choice
    ),
    "mistral-small": OpenHandsModelConfig(
        model_id="openrouter/mistralai/mistral-small-3.2-24b-instruct:free",
        display_name="Mistral Small 3.2 24B (Free)",
        context_tokens=32_000,
        is_free=True,
        recommended=False,  # Fallback option
    ),
    "gemini-flash": OpenHandsModelConfig(
        model_id="openrouter/google/gemini-2.0-flash-exp:free",
        display_name="Google Gemini 2.0 Flash",
        context_tokens=1_000_000,
        is_free=True,
        recommended=False,
    ),
    "llama-scout": OpenHandsModelConfig(
        model_id="openrouter/meta-llama/llama-4-scout:free",
        display_name="Meta Llama 4 Scout (17B)",
        context_tokens=190_000_000,
        is_free=True,
        recommended=False,  # Experimental
    ),
    "deepseek-r1": OpenHandsModelConfig(
        model_id="openrouter/deepseek/deepseek-r1-0528-qwen3-8b:free",
        display_name="DeepSeek R1 Qwen3 (8B)",
        context_tokens=32_000,
        is_free=True,
        recommended=False,
    ),
}


class OpenHandsConfig(BaseModel):
    """Configuration for OpenHands SDK client."""

    api_key: SecretStr = Field(
        description="OpenRouter API key (from environment or secrets manager)"
    )
    model: str = Field(
        default="openrouter/mistralai/mistral-small-3.2-24b-instruct:free",
        description="OpenRouter model to use (free models recommended)",
    )
    base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL",
    )
    workspace_path: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Workspace directory for OpenHands execution",
    )
    cli_mode: bool = Field(
        default=True, description="Enable CLI mode for agent"
    )
    usage_id: str = Field(
        default="tta-openhands", description="Usage identifier for tracking"
    )
    timeout_seconds: float = Field(
        default=300.0,
        ge=10.0,
        le=3600.0,
        description="Task execution timeout in seconds",
    )


class OpenHandsIntegrationConfig(BaseModel):
    """
    Complete configuration for OpenHands integration.

    Supports:
    - Environment variable loading
    - Model selection and validation
    - Workspace configuration
    - Timeout and retry settings
    - Circuit breaker configuration
    """

    # API Configuration
    api_key: SecretStr = Field(
        description="OpenRouter API key (from OPENROUTER_API_KEY env var)"
    )
    base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL",
    )

    # Model Selection
    model_preset: Literal[
        "deepseek-v3", "mistral-small", "gemini-flash", "llama-scout", "deepseek-r1"
    ] = Field(default="gemini-flash", description="Model preset to use (free models only)")
    custom_model_id: str | None = Field(
        default=None, description="Custom model ID (overrides preset)"
    )

    # Workspace Configuration
    workspace_root: Path = Field(
        default_factory=lambda: Path.cwd() / "openhands_workspace",
        description="Root directory for OpenHands workspaces",
    )
    workspace_isolation: bool = Field(
        default=True, description="Create isolated workspace per task"
    )

    # Execution Settings
    default_timeout_seconds: float = Field(
        default=300.0,
        ge=10.0,
        le=3600.0,
        description="Default task execution timeout",
    )
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum retry attempts"
    )
    retry_base_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Base delay for exponential backoff (seconds)",
    )

    # Circuit Breaker Settings
    circuit_breaker_enabled: bool = Field(
        default=True, description="Enable circuit breaker for fault tolerance"
    )
    circuit_breaker_failure_threshold: int = Field(
        default=5, ge=1, le=20, description="Failures before opening circuit"
    )
    circuit_breaker_timeout_seconds: int = Field(
        default=60, ge=10, le=600, description="Timeout before attempting recovery"
    )

    # Feature Flags
    enable_real_agent: bool = Field(
        default=True, description="Use real OpenHands SDK (false for testing)"
    )
    fallback_to_mock: bool = Field(
        default=False, description="Fall back to mock responses on failure"
    )

    # Docker Runtime Configuration (NEW - resolves file creation limitation)
    use_docker_runtime: bool = Field(
        default=False,
        description="Use Docker runtime for full tool access (bash, file operations). "
        "Default False for backward compatibility with SDK mode.",
    )
    docker_image: str = Field(
        default="docker.all-hands.dev/all-hands-ai/openhands:0.54",
        description="OpenHands Docker image for runtime mode",
    )
    docker_runtime_image: str = Field(
        default="docker.all-hands.dev/all-hands-ai/runtime:0.54-nikolaik",
        description="Sandbox runtime image for Docker mode",
    )
    docker_timeout: float = Field(
        default=600.0,
        ge=10.0,
        le=3600.0,
        description="Docker execution timeout (seconds)",
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """Validate API key is not empty."""
        if not v.get_secret_value():
            raise ValueError("OpenRouter API key is required")
        return v

    @field_validator("workspace_root")
    @classmethod
    def ensure_workspace_exists(cls, v: Path) -> Path:
        """Ensure workspace directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    def get_model_config(self) -> OpenHandsModelConfig:
        """
        Get model configuration based on preset or custom ID.

        Uses registry when available, falls back to FREE_MODELS.

        Returns:
            OpenHandsModelConfig instance
        """
        # Custom model ID always takes precedence
        if self.custom_model_id:
            logger.info(f"Using custom model ID: {self.custom_model_id}")

            # Try to get from registry first
            registry = get_model_registry()
            if registry and self.custom_model_id in registry.models:
                entry = registry.models[self.custom_model_id]
                logger.info(
                    f"Found custom model in registry: {entry.display_name}"
                )
                return OpenHandsModelConfig(
                    model_id=entry.model_id,
                    display_name=entry.display_name,
                    context_tokens=entry.context_window,
                    is_free=True,
                    recommended=False,
                )

            # Fallback to conservative defaults
            logger.warning(
                f"Custom model {self.custom_model_id} not in registry, using defaults"
            )
            return OpenHandsModelConfig(
                model_id=self.custom_model_id,
                display_name=self.custom_model_id,
                context_tokens=64_000,  # Conservative default
                is_free=True,
                recommended=False,
            )

        # Resolve preset to model ID
        model_id = get_model_by_preset(self.model_preset)
        logger.info(
            f"Resolved preset '{self.model_preset}' to model ID: {model_id}"
        )

        # Try to get from registry
        registry = get_model_registry()
        if registry and model_id in registry.models:
            entry = registry.models[model_id]
            logger.info(f"Found model in registry: {entry.display_name}")
            return OpenHandsModelConfig(
                model_id=entry.model_id,
                display_name=entry.display_name,
                context_tokens=entry.context_window,
                is_free=True,
                recommended=entry.compatibility_status
                == CompatibilityStatus.VERIFIED,
            )

        # Fallback to FREE_MODELS
        logger.warning(
            f"Model {model_id} not in registry, using FREE_MODELS fallback"
        )
        return FREE_MODELS[self.model_preset]

    def to_client_config(self) -> OpenHandsConfig:
        """
        Convert to OpenHandsConfig for use with OpenHandsClient.

        Returns:
            OpenHandsConfig instance
        """
        model_config = self.get_model_config()
        return OpenHandsConfig(
            api_key=self.api_key,
            model=model_config.model_id,
            base_url=self.base_url,
            workspace_path=self.workspace_root,
            timeout_seconds=self.default_timeout_seconds,
        )

    @classmethod
    def from_env(cls, env_file: Path | str | None = None) -> OpenHandsIntegrationConfig:
        """
        Load configuration from environment variables.

        Automatically loads .env file from project root if present.

        Environment Variables:
            OPENROUTER_API_KEY: Required API key
            OPENHANDS_MODEL: Model preset (default: gemini-flash)
            OPENHANDS_BASE_URL: API base URL (default: https://openrouter.ai/api/v1)
            OPENHANDS_WORKSPACE_ROOT: Workspace root directory
            OPENHANDS_TIMEOUT: Default timeout in seconds
            OPENHANDS_ENABLE_CIRCUIT_BREAKER: Enable circuit breaker (true/false)
            OPENHANDS_USE_DOCKER_RUNTIME: Use Docker runtime mode (true/false, default: false)
            OPENHANDS_DOCKER_IMAGE: Docker image for runtime mode
            OPENHANDS_DOCKER_RUNTIME_IMAGE: Sandbox runtime image
            OPENHANDS_DOCKER_TIMEOUT: Docker execution timeout

        Args:
            env_file: Path to .env file (default: searches project root)

        Returns:
            OpenHandsIntegrationConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        # Load .env file if not already loaded
        if env_file:
            load_dotenv(env_file, override=False)
        else:
            # Search for .env in common locations
            env_paths = [
                Path.cwd() / ".env",  # Current directory
                Path(__file__).parent.parent.parent / ".env",  # Project root
            ]
            for env_path in env_paths:
                if env_path.exists():
                    logger.info(f"Loading .env file from: {env_path}")
                    load_dotenv(env_path, override=False)
                    break

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required. "
                "Get your API key from https://openrouter.ai/keys"
            )

        return cls(
            api_key=SecretStr(api_key),
            base_url=os.getenv(
                "OPENHANDS_BASE_URL", "https://openrouter.ai/api/v1"
            ),
            model_preset=os.getenv("OPENHANDS_MODEL", "gemini-flash"),
            workspace_root=Path(
                os.getenv("OPENHANDS_WORKSPACE_ROOT", "./openhands_workspace")
            ),
            default_timeout_seconds=float(os.getenv("OPENHANDS_TIMEOUT", "300.0")),
            circuit_breaker_enabled=os.getenv(
                "OPENHANDS_ENABLE_CIRCUIT_BREAKER", "true"
            ).lower()
            == "true",
            enable_real_agent=os.getenv(
                "OPENHANDS_ENABLE_REAL_AGENT", "true"
            ).lower()
            == "true",
            # Docker runtime configuration
            use_docker_runtime=os.getenv(
                "OPENHANDS_USE_DOCKER_RUNTIME", "false"
            ).lower()
            == "true",
            docker_image=os.getenv(
                "OPENHANDS_DOCKER_IMAGE",
                "docker.all-hands.dev/all-hands-ai/openhands:0.54",
            ),
            docker_runtime_image=os.getenv(
                "OPENHANDS_DOCKER_RUNTIME_IMAGE",
                "docker.all-hands.dev/all-hands-ai/runtime:0.54-nikolaik",
            ),
            docker_timeout=float(os.getenv("OPENHANDS_DOCKER_TIMEOUT", "600.0")),
        )

