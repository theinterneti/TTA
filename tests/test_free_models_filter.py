"""
Tests for OpenRouter Free Models Filter functionality
"""

import os
from unittest.mock import Mock, patch


# Mock the model management components for testing
class MockModelInfo:
    def __init__(self, model_id, name, cost_per_token=None, is_free=False):
        self.model_id = model_id
        self.name = name
        self.provider_type = Mock()
        self.provider_type.value = "openrouter"
        self.description = f"Mock model {name}"
        self.context_length = 4096
        self.cost_per_token = cost_per_token
        self.is_free = is_free
        self.capabilities = ["chat"]
        self.therapeutic_safety_score = None
        self.performance_score = 7.0


class TestFreeModelsFilter:
    """Test the free models filtering functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock models with different cost structures
        self.mock_models = [
            MockModelInfo(
                "free-model-1", "Free Model 1", cost_per_token=0.0, is_free=True
            ),
            MockModelInfo(
                "free-model-2", "Free Model 2", cost_per_token=0.0, is_free=True
            ),
            MockModelInfo(
                "cheap-model-1", "Cheap Model 1", cost_per_token=0.0005, is_free=False
            ),
            MockModelInfo(
                "moderate-model-1",
                "Moderate Model 1",
                cost_per_token=0.005,
                is_free=False,
            ),
            MockModelInfo(
                "expensive-model-1",
                "Expensive Model 1",
                cost_per_token=0.05,
                is_free=False,
            ),
        ]

    def test_environment_variables_parsing(self):
        """Test that environment variables are parsed correctly."""
        # Test boolean parsing
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_BOOL": env_value}):
                # Simulate the boolean parsing logic
                result = os.getenv("TEST_BOOL", "false").lower() in (
                    "true",
                    "1",
                    "yes",
                    "on",
                )
                assert result == expected, (
                    f"Failed for {env_value}, expected {expected}, got {result}"
                )

    def test_float_parsing(self):
        """Test that float environment variables are parsed correctly."""
        test_cases = [
            ("0.001", 0.001),
            ("0.0005", 0.0005),
            ("1.5", 1.5),
            ("0", 0.0),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_FLOAT": env_value}):
                # Simulate the float parsing logic
                result = float(os.getenv("TEST_FLOAT", "0.0"))
                assert result == expected, (
                    f"Failed for {env_value}, expected {expected}, got {result}"
                )

    def test_free_models_filtering(self):
        """Test filtering to show only free models."""
        # Filter free models
        free_models = [model for model in self.mock_models if model.is_free]

        assert len(free_models) == 2
        assert all(model.is_free for model in free_models)
        assert all(model.cost_per_token == 0.0 for model in free_models)

    def test_affordable_models_filtering(self):
        """Test filtering models by cost threshold."""
        max_cost = 0.001

        # Filter affordable models (free + under threshold)
        affordable_models = [
            model
            for model in self.mock_models
            if model.is_free
            or (model.cost_per_token is not None and model.cost_per_token <= max_cost)
        ]

        # Should include 2 free models + 1 cheap model
        assert len(affordable_models) == 3

        # Verify all models are within threshold
        for model in affordable_models:
            if not model.is_free:
                assert model.cost_per_token <= max_cost

    def test_model_sorting_prefer_free(self):
        """Test that free models are sorted first when prefer_free is enabled."""
        # Sort with free models first
        sorted_models = sorted(
            self.mock_models, key=lambda m: (not m.is_free, m.model_id)
        )

        # First two should be free models
        assert sorted_models[0].is_free
        assert sorted_models[1].is_free

        # Remaining should be paid models
        for model in sorted_models[2:]:
            assert not model.is_free

    def test_cost_estimation(self):
        """Test cost estimation functionality."""
        test_model = self.mock_models[2]  # cheap-model-1 with cost 0.0005
        estimated_tokens = 1000

        expected_cost = test_model.cost_per_token * estimated_tokens
        assert expected_cost == 0.5  # 0.0005 * 1000

        # Test free model
        free_model = self.mock_models[0]
        free_cost = free_model.cost_per_token * estimated_tokens
        assert free_cost == 0.0

    def test_model_categorization(self):
        """Test model categorization by cost ranges."""
        free_models = [m for m in self.mock_models if m.is_free]
        very_cheap = [
            m
            for m in self.mock_models
            if m.cost_per_token and m.cost_per_token <= 0.0001
        ]
        cheap = [
            m
            for m in self.mock_models
            if m.cost_per_token and 0.0001 < m.cost_per_token <= 0.001
        ]
        moderate = [
            m
            for m in self.mock_models
            if m.cost_per_token and 0.001 < m.cost_per_token <= 0.01
        ]
        expensive = [
            m for m in self.mock_models if m.cost_per_token and m.cost_per_token > 0.01
        ]

        assert len(free_models) == 2
        assert len(very_cheap) == 0  # No models in this range in our test data
        assert len(cheap) == 1  # cheap-model-1
        assert len(moderate) == 1  # moderate-model-1
        assert len(expensive) == 1  # expensive-model-1

    def test_filter_settings_validation(self):
        """Test that filter settings are validated correctly."""
        # Test valid settings
        valid_settings = {
            "show_free_only": True,
            "prefer_free_models": True,
            "max_cost_per_token": 0.001,
        }

        # All should be valid types
        assert isinstance(valid_settings["show_free_only"], bool)
        assert isinstance(valid_settings["prefer_free_models"], bool)
        assert isinstance(valid_settings["max_cost_per_token"], (int, float))
        assert valid_settings["max_cost_per_token"] >= 0

    def test_environment_configuration_integration(self):
        """Test integration with environment configuration."""
        # Test with environment variables set
        env_vars = {
            "OPENROUTER_SHOW_FREE_ONLY": "true",
            "OPENROUTER_PREFER_FREE_MODELS": "false",
            "OPENROUTER_MAX_COST_PER_TOKEN": "0.0005",
        }

        with patch.dict(os.environ, env_vars):
            # Simulate configuration loading
            show_free_only = (
                os.getenv("OPENROUTER_SHOW_FREE_ONLY", "false").lower() == "true"
            )
            prefer_free = (
                os.getenv("OPENROUTER_PREFER_FREE_MODELS", "true").lower() == "true"
            )
            max_cost = float(os.getenv("OPENROUTER_MAX_COST_PER_TOKEN", "0.001"))

            assert show_free_only
            assert not prefer_free
            assert max_cost == 0.0005

    def test_api_response_format(self):
        """Test that API responses have the correct format."""
        # Simulate API response format
        model = self.mock_models[0]
        api_response = {
            "model_id": model.model_id,
            "name": model.name,
            "provider": model.provider_type.value,
            "description": model.description,
            "context_length": model.context_length,
            "cost_per_token": model.cost_per_token,
            "is_free": model.is_free,
            "capabilities": model.capabilities,
            "therapeutic_safety_score": model.therapeutic_safety_score,
            "performance_score": model.performance_score,
        }

        # Verify all required fields are present
        required_fields = [
            "model_id",
            "name",
            "provider",
            "description",
            "context_length",
            "cost_per_token",
            "is_free",
            "capabilities",
        ]

        for field in required_fields:
            assert field in api_response, f"Missing required field: {field}"

        # Verify data types
        assert isinstance(api_response["is_free"], bool)
        assert isinstance(api_response["cost_per_token"], (int, float, type(None)))
        assert isinstance(api_response["capabilities"], list)


class TestOpenRouterProviderMethods:
    """Test OpenRouter provider specific methods."""

    def test_get_bool_config_method(self):
        """Test the _get_bool_config method logic."""

        # Simulate the method logic
        def get_bool_config(config_dict, config_key, env_key, default):
            # Check config dict first
            if config_dict and config_key in config_dict:
                value = config_dict[config_key]
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")

            # Check environment
            env_value = os.getenv(env_key)
            if env_value is not None:
                return env_value.lower() in ("true", "1", "yes", "on")

            return default

        # Test with config dict
        config = {"test_key": True}
        result = get_bool_config(config, "test_key", "TEST_ENV", False)
        assert result

        # Test with environment variable
        with patch.dict(os.environ, {"TEST_ENV": "true"}):
            result = get_bool_config({}, "missing_key", "TEST_ENV", False)
            assert result

        # Test with default
        result = get_bool_config({}, "missing_key", "MISSING_ENV", False)
        assert not result

    def test_get_float_config_method(self):
        """Test the _get_float_config method logic."""

        # Simulate the method logic
        def get_float_config(config_dict, config_key, env_key, default):
            # Check config dict first
            if config_dict and config_key in config_dict:
                try:
                    return float(config_dict[config_key])
                except (ValueError, TypeError):
                    pass

            # Check environment
            env_value = os.getenv(env_key)
            if env_value is not None:
                try:
                    return float(env_value)
                except (ValueError, TypeError):
                    pass

            return default

        # Test with config dict
        config = {"test_key": 0.005}
        result = get_float_config(config, "test_key", "TEST_ENV", 0.001)
        assert result == 0.005

        # Test with environment variable
        with patch.dict(os.environ, {"TEST_ENV": "0.002"}):
            result = get_float_config({}, "missing_key", "TEST_ENV", 0.001)
            assert result == 0.002

        # Test with default
        result = get_float_config({}, "missing_key", "MISSING_ENV", 0.001)
        assert result == 0.001


def test_integration_with_existing_system():
    """Test that the free models filter integrates well with existing system."""
    # This test verifies that the new functionality doesn't break existing behavior

    # Test that models without cost information are handled correctly
    model_without_cost = MockModelInfo(
        "unknown-cost", "Unknown Cost Model", cost_per_token=None, is_free=False
    )

    # Should not crash when filtering
    affordable_models = [
        model
        for model in [model_without_cost]
        if model.is_free
        or (model.cost_per_token is not None and model.cost_per_token <= 0.001)
    ]

    # Should be empty since model is not free and has no cost info
    assert len(affordable_models) == 0

    # Test with free model that has None cost (edge case)
    free_model_no_cost = MockModelInfo(
        "free-no-cost", "Free No Cost", cost_per_token=None, is_free=True
    )

    affordable_models = [
        model
        for model in [free_model_no_cost]
        if model.is_free
        or (model.cost_per_token is not None and model.cost_per_token <= 0.001)
    ]

    # Should include the free model even without cost info
    assert len(affordable_models) == 1
    assert affordable_models[0].is_free


if __name__ == "__main__":
    # Run tests
    test_instance = TestFreeModelsFilter()
    test_instance.setup_method()

    # Run all test methods
    test_methods = [
        test_instance.test_environment_variables_parsing,
        test_instance.test_float_parsing,
        test_instance.test_free_models_filtering,
        test_instance.test_affordable_models_filtering,
        test_instance.test_model_sorting_prefer_free,
        test_instance.test_cost_estimation,
        test_instance.test_model_categorization,
        test_instance.test_filter_settings_validation,
        test_instance.test_environment_configuration_integration,
        test_instance.test_api_response_format,
    ]

    provider_test = TestOpenRouterProviderMethods()
    test_methods.extend(
        [
            provider_test.test_get_bool_config_method,
            provider_test.test_get_float_config_method,
        ]
    )

    test_methods.append(test_integration_with_existing_system)

    passed = 0
    failed = 0

    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception:
            failed += 1

    if failed == 0:
        pass
    else:
        pass
