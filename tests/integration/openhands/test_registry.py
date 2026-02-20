"""

# Logseq: [[TTA.dev/Tests/Integration/Openhands/Test_registry]]
Unit tests for OpenHands model registry system.

Tests:
- Registry loading and validation
- Model filtering by various criteria
- Model prioritization algorithm
- Fallback chain generation
- Backward compatibility with legacy presets
- Error handling and graceful degradation
"""

from unittest.mock import patch

import pytest

from src.agent_orchestration.openhands_integration.config import (
    CompatibilityStatus,
    ModelRegistry,
    ModelRegistryEntry,
    QualityTier,
    _clear_registry_cache,
    filter_models,
    get_fallback_model_chain,
    get_hardcoded_fallback_models,
    get_model_by_preset,
    get_model_registry,
    load_model_registry,
    prioritize_models,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_registry():
    """Create a mock registry for testing."""
    return ModelRegistry(
        version="1.0.0",
        last_updated="2025-10-25",
        description="Test registry",
        models={
            "openrouter/test/verified-high": ModelRegistryEntry(
                model_id="openrouter/test/verified-high",
                display_name="Verified High Quality",
                provider="TestProvider",
                compatibility_status=CompatibilityStatus.VERIFIED,
                quality_tier=QualityTier.HIGH,
                context_window=64000,
                supports_system_prompt=True,
                capabilities=["code", "reasoning"],
            ),
            "openrouter/test/verified-medium": ModelRegistryEntry(
                model_id="openrouter/test/verified-medium",
                display_name="Verified Medium Quality",
                provider="TestProvider",
                compatibility_status=CompatibilityStatus.VERIFIED,
                quality_tier=QualityTier.MEDIUM,
                context_window=32000,
                supports_system_prompt=True,
                capabilities=["code"],
            ),
            "openrouter/test/rate-limited": ModelRegistryEntry(
                model_id="openrouter/test/rate-limited",
                display_name="Rate Limited Model",
                provider="OtherProvider",
                compatibility_status=CompatibilityStatus.RATE_LIMITED,
                quality_tier=QualityTier.HIGH,
                context_window=64000,
                supports_system_prompt=True,
                known_issues=["Rate limiting"],
                capabilities=["code"],
            ),
            "openrouter/test/untested": ModelRegistryEntry(
                model_id="openrouter/test/untested",
                display_name="Untested Model",
                provider="TestProvider",
                compatibility_status=CompatibilityStatus.UNTESTED,
                quality_tier=QualityTier.HIGH,
                context_window=64000,
                supports_system_prompt=True,
                capabilities=["code", "reasoning"],
            ),
            "openrouter/test/incompatible": ModelRegistryEntry(
                model_id="openrouter/test/incompatible",
                display_name="Incompatible Model",
                provider="TestProvider",
                compatibility_status=CompatibilityStatus.INCOMPATIBLE,
                quality_tier=QualityTier.LOW,
                context_window=8000,
                supports_system_prompt=False,
                known_issues=["No system prompt support"],
                capabilities=[],
            ),
        },
    )


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear registry cache before each test."""
    _clear_registry_cache()
    yield
    _clear_registry_cache()


# ============================================================================
# Registry Loading Tests
# ============================================================================


def test_load_valid_registry():
    """Test loading a valid registry file."""
    registry = load_model_registry()
    assert registry is not None
    assert registry.version == "1.1.0"
    assert len(registry.models) >= 11  # Registry grows as models are added
    assert "openrouter/deepseek/deepseek-chat" in registry.models


def test_load_missing_file():
    """Test loading when registry file is missing."""
    with patch("pathlib.Path.exists", return_value=False):
        registry = load_model_registry()
        assert registry is None


def test_get_registry_singleton():
    """Test registry singleton behavior."""
    registry1 = get_model_registry()
    registry2 = get_model_registry()
    assert registry1 is registry2  # Same instance


def test_hardcoded_fallback():
    """Test hardcoded fallback models."""
    fallback = get_hardcoded_fallback_models()
    assert len(fallback) == 2
    assert "openrouter/deepseek/deepseek-chat" in fallback
    assert "openrouter/qwen/qwen3-coder:free" in fallback


# ============================================================================
# Filtering Tests
# ============================================================================


def test_filter_by_status(mock_registry):
    """Test filtering by compatibility status."""
    filtered = filter_models(
        registry=mock_registry,
        compatibility_statuses=[CompatibilityStatus.VERIFIED],
    )
    assert len(filtered) == 2
    assert all(m.compatibility_status == CompatibilityStatus.VERIFIED for m in filtered)


def test_filter_by_provider(mock_registry):
    """Test filtering by provider."""
    filtered = filter_models(
        registry=mock_registry,
        providers=["OtherProvider"],
    )
    assert len(filtered) == 1
    assert filtered[0].provider == "OtherProvider"


def test_filter_by_quality(mock_registry):
    """Test filtering by quality tier."""
    filtered = filter_models(
        registry=mock_registry,
        quality_tiers=[QualityTier.HIGH],
    )
    assert len(filtered) >= 2
    assert all(m.quality_tier == QualityTier.HIGH for m in filtered)


def test_filter_by_context_window(mock_registry):
    """Test filtering by minimum context window."""
    filtered = filter_models(
        registry=mock_registry,
        min_context_window=50000,
    )
    assert all(m.context_window >= 50000 for m in filtered)


def test_filter_by_system_prompt(mock_registry):
    """Test filtering by system prompt support."""
    filtered = filter_models(
        registry=mock_registry,
        require_system_prompt=True,
    )
    assert all(m.supports_system_prompt for m in filtered)


def test_filter_exclude_incompatible(mock_registry):
    """Test excluding incompatible models."""
    filtered = filter_models(
        registry=mock_registry,
        exclude_incompatible=True,
    )
    assert all(
        m.compatibility_status != CompatibilityStatus.INCOMPATIBLE for m in filtered
    )


def test_filter_by_capabilities(mock_registry):
    """Test filtering by required capabilities."""
    filtered = filter_models(
        registry=mock_registry,
        capabilities=["reasoning"],
    )
    assert all("reasoning" in m.capabilities for m in filtered)


def test_filter_empty_registry():
    """Test filtering with no registry."""
    # Create an empty registry
    empty_registry = ModelRegistry(
        version="1.0.0",
        last_updated="2025-10-25",
        description="Empty registry",
        models={},
    )
    filtered = filter_models(registry=empty_registry)
    assert filtered == []


# ============================================================================
# Prioritization Tests
# ============================================================================


def test_prioritization_algorithm(mock_registry):
    """Test model prioritization scoring."""
    models = list(mock_registry.models.values())
    prioritized = prioritize_models(models)

    # Verified high-quality should be first
    assert "verified-high" in prioritized[0]

    # Incompatible should be last
    assert "incompatible" in prioritized[-1]


def test_prioritization_empty_list():
    """Test prioritization with empty list."""
    prioritized = prioritize_models([])
    assert prioritized == []


# ============================================================================
# Fallback Chain Tests
# ============================================================================


def test_get_fallback_chain(mock_registry):
    """Test getting fallback model chain."""
    with patch(
        "src.agent_orchestration.openhands_integration.config.get_model_registry",
        return_value=mock_registry,
    ):
        chain = get_fallback_model_chain(max_models=3)
        assert len(chain) <= 3
        assert all(isinstance(model_id, str) for model_id in chain)


def test_get_fallback_chain_empty_filters():
    """Test fallback chain with filters that match nothing."""
    chain = get_fallback_model_chain(
        compatibility_statuses=[CompatibilityStatus.INCOMPATIBLE],
        quality_tiers=[QualityTier.LOW],
        max_models=5,
    )
    # Should return hardcoded fallback
    assert len(chain) >= 2
    assert "openrouter/deepseek/deepseek-chat" in chain


# ============================================================================
# Backward Compatibility Tests
# ============================================================================


def test_legacy_presets():
    """Test all legacy preset mappings."""
    presets = [
        "deepseek-v3",
        "mistral-small",
        "gemini-flash",
        "llama-scout",
        "deepseek-r1",
    ]
    for preset in presets:
        model_id = get_model_by_preset(preset)
        assert model_id.startswith("openrouter/")


def test_unknown_preset():
    """Test handling of unknown preset."""
    model_id = get_model_by_preset("unknown-preset")
    # Should return default (gemini-flash)
    assert "gemini" in model_id.lower()


# ============================================================================
# Integration Tests
# ============================================================================


def test_registry_with_real_file():
    """Test loading and using the actual registry file."""
    registry = load_model_registry()
    assert registry is not None

    # Test filtering
    filtered = filter_models(
        registry=registry,
        compatibility_statuses=[CompatibilityStatus.VERIFIED],
    )
    assert len(filtered) > 0

    # Test prioritization
    prioritized = prioritize_models(filtered)
    assert len(prioritized) > 0


def test_model_selection_integration():
    """Test complete model selection workflow."""
    # Get fallback chain
    chain = get_fallback_model_chain(max_models=5)
    assert len(chain) > 0

    # Verify all models have openrouter/ prefix
    assert all(model_id.startswith("openrouter/") for model_id in chain)