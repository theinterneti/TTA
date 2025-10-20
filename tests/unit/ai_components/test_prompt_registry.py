"""
Unit tests for PromptRegistry.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.ai_components.prompts import PromptMetrics, PromptRegistry, PromptTemplate


@pytest.fixture
def temp_prompts_dir():
    """Create a temporary prompts directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()

        # Create directory structure
        versions_dir = prompts_dir / "versions" / "v1.0.0"
        versions_dir.mkdir(parents=True)
        active_dir = prompts_dir / "active"
        active_dir.mkdir()

        # Create test prompt
        test_prompt = {
            "version": "1.0.0",
            "created_at": "2025-01-20",
            "author": "test",
            "description": "Test prompt",
            "agent_type": "test_agent",
            "template": "Test prompt with {variable1} and {variable2}",
            "variables": ["variable1", "variable2"],
            "performance_baseline": {
                "avg_tokens": 100,
                "avg_latency_ms": 500,
                "quality_score": 8.0,
                "cost_per_call_usd": 0.0001,
            },
            "metadata": {"test_key": "test_value"},
        }

        with open(versions_dir / "test_prompt.yaml", "w") as f:
            yaml.dump(test_prompt, f)

        # Create registry
        registry = {
            "prompts": {
                "test_prompt": {
                    "description": "Test prompt",
                    "agent_type": "test_agent",
                    "active_version": "1.0.0",
                    "versions": [
                        {
                            "version": "1.0.0",
                            "created_at": "2025-01-20",
                            "status": "active",
                            "performance": {
                                "avg_tokens": 100,
                                "avg_latency_ms": 500,
                                "quality_score": 8.0,
                                "cost_per_call_usd": 0.0001,
                            },
                        }
                    ],
                }
            },
            "changelog": [],
        }

        with open(prompts_dir / "registry.yaml", "w") as f:
            yaml.dump(registry, f)

        yield prompts_dir


def test_prompt_registry_initialization(temp_prompts_dir):
    """Test PromptRegistry initialization."""
    registry = PromptRegistry(temp_prompts_dir)

    assert registry.prompts_dir == temp_prompts_dir
    assert "test_prompt" in registry.active_versions
    assert registry.active_versions["test_prompt"] == "1.0.0"


def test_load_prompt(temp_prompts_dir):
    """Test loading a prompt template."""
    registry = PromptRegistry(temp_prompts_dir)

    template = registry.load_prompt("test_prompt")

    assert template.prompt_id == "test_prompt"
    assert template.version == "1.0.0"
    assert template.agent_type == "test_agent"
    assert "variable1" in template.variables
    assert "variable2" in template.variables


def test_load_prompt_specific_version(temp_prompts_dir):
    """Test loading a specific prompt version."""
    registry = PromptRegistry(temp_prompts_dir)

    template = registry.load_prompt("test_prompt", version="1.0.0")

    assert template.version == "1.0.0"


def test_load_prompt_not_found(temp_prompts_dir):
    """Test loading a non-existent prompt."""
    registry = PromptRegistry(temp_prompts_dir)

    with pytest.raises(ValueError, match="No active version found"):
        registry.load_prompt("nonexistent_prompt")


def test_render_prompt(temp_prompts_dir):
    """Test rendering a prompt with variables."""
    registry = PromptRegistry(temp_prompts_dir)

    rendered = registry.render_prompt(
        "test_prompt", variable1="value1", variable2="value2"
    )

    assert "value1" in rendered
    assert "value2" in rendered
    assert rendered == "Test prompt with value1 and value2"


def test_render_prompt_missing_variable(temp_prompts_dir):
    """Test rendering a prompt with missing variables."""
    registry = PromptRegistry(temp_prompts_dir)

    with pytest.raises(ValueError, match="Missing required variables"):
        registry.render_prompt("test_prompt", variable1="value1")


def test_record_metrics(temp_prompts_dir):
    """Test recording prompt metrics."""
    registry = PromptRegistry(temp_prompts_dir)

    # Record some metrics
    registry.record_metrics(
        "test_prompt",
        tokens=150,
        latency_ms=600,
        cost_usd=0.0002,
        quality_score=8.5,
    )

    metrics = registry.get_metrics("test_prompt")

    assert metrics.total_calls == 1
    assert metrics.total_tokens == 150
    assert metrics.avg_latency_ms == 600
    assert metrics.avg_quality_score == 8.5


def test_record_multiple_metrics(temp_prompts_dir):
    """Test recording multiple prompt calls."""
    registry = PromptRegistry(temp_prompts_dir)

    # Record multiple calls
    for i in range(5):
        registry.record_metrics(
            "test_prompt",
            tokens=100 + i * 10,
            latency_ms=500 + i * 50,
            cost_usd=0.0001,
            quality_score=8.0 + i * 0.1,
        )

    metrics = registry.get_metrics("test_prompt")

    assert metrics.total_calls == 5
    assert metrics.avg_tokens == 120  # (100+110+120+130+140)/5
    assert metrics.avg_latency_ms == 600  # (500+550+600+650+700)/5


def test_record_error_metrics(temp_prompts_dir):
    """Test recording error metrics."""
    registry = PromptRegistry(temp_prompts_dir)

    # Record successful call
    registry.record_metrics("test_prompt", tokens=100, latency_ms=500, cost_usd=0.0001)

    # Record error call
    registry.record_metrics(
        "test_prompt", tokens=0, latency_ms=0, cost_usd=0.0, error=True
    )

    metrics = registry.get_metrics("test_prompt")

    assert metrics.total_calls == 2
    assert metrics.error_count == 1
    assert metrics.error_rate == 50.0


def test_get_baseline_scores(temp_prompts_dir):
    """Test getting baseline performance scores."""
    registry = PromptRegistry(temp_prompts_dir)

    baseline = registry.get_baseline_scores("test_prompt")

    assert baseline["avg_tokens"] == 100
    assert baseline["avg_latency_ms"] == 500
    assert baseline["quality_score"] == 8.0


def test_list_prompts(temp_prompts_dir):
    """Test listing all prompts."""
    registry = PromptRegistry(temp_prompts_dir)

    prompts = registry.list_prompts()

    assert "test_prompt" in prompts


def test_export_metrics(temp_prompts_dir):
    """Test exporting metrics."""
    registry = PromptRegistry(temp_prompts_dir)

    # Record some metrics
    registry.record_metrics(
        "test_prompt", tokens=150, latency_ms=600, cost_usd=0.0002, quality_score=8.5
    )

    exported = registry.export_metrics()

    assert "test_prompt:1.0.0" in exported
    assert exported["test_prompt:1.0.0"]["total_calls"] == 1


def test_prompt_template_hash():
    """Test prompt template hash generation."""
    template = PromptTemplate(
        prompt_id="test",
        version="1.0.0",
        template="Test {var}",
        variables=["var"],
        description="Test",
        agent_type="test",
        created_at="2025-01-20",
        author="test",
        performance_baseline={},
    )

    hash1 = template.get_hash()
    hash2 = template.get_hash()

    assert hash1 == hash2
    assert len(hash1) == 16


def test_prompt_metrics_calculations():
    """Test PromptMetrics calculations."""
    metrics = PromptMetrics(prompt_id="test", version="1.0.0")

    # Record calls
    metrics.record_call(tokens=100, latency_ms=500, cost_usd=0.0001, quality_score=8.0)
    metrics.record_call(tokens=200, latency_ms=600, cost_usd=0.0002, quality_score=9.0)

    assert metrics.total_calls == 2
    assert metrics.avg_tokens == 150
    assert metrics.avg_latency_ms == 550
    assert abs(metrics.avg_cost_usd - 0.00015) < 1e-10  # Float comparison
    assert metrics.avg_quality_score == 8.5
    assert metrics.error_rate == 0.0


def test_prompt_metrics_to_dict():
    """Test PromptMetrics to_dict conversion."""
    metrics = PromptMetrics(prompt_id="test", version="1.0.0")
    metrics.record_call(tokens=100, latency_ms=500, cost_usd=0.0001, quality_score=8.0)

    metrics_dict = metrics.to_dict()

    assert metrics_dict["prompt_id"] == "test"
    assert metrics_dict["version"] == "1.0.0"
    assert metrics_dict["total_calls"] == 1
    assert metrics_dict["avg_tokens"] == 100

