"""
Consumer Contract Tests for Frontend Model Management.

This module defines the API contracts that the frontend expects from the
Model Management backend API. These contracts are validated against the
actual backend implementation.
"""

import pytest

# Note: pact-python requires specific setup. For now, we'll create a simplified
# version that can be enhanced with full Pact integration later.
# Full Pact integration requires:
# 1. Pact mock server running
# 2. Pact broker for contract sharing (optional)
# 3. Provider state setup endpoints

try:
    from pact import Consumer, EachLike, Like, Provider, Term

    PACT_AVAILABLE = True
except ImportError:
    PACT_AVAILABLE = False
    pytest.skip("pact-python not available", allow_module_level=True)


# ============================================================================
# Pact Setup
# ============================================================================

if PACT_AVAILABLE:
    pact = Consumer("TTA-Frontend").has_pact_with(
        Provider("ModelManagementAPI"),
        pact_dir="tests/contracts/pacts",
        host_name="localhost",
        port=1234,
    )


# ============================================================================
# Contract Tests
# ============================================================================


@pytest.mark.contract
@pytest.mark.skipif(not PACT_AVAILABLE, reason="pact-python not available")
class TestModelManagementAPIContract:
    """Contract tests for Model Management API."""

    def test_get_available_models_contract(self):
        """Contract: GET /api/v1/models returns list of available models."""
        expected_response = {
            "models": EachLike(
                {
                    "model_id": Like("meta-llama/llama-3.1-8b-instruct:free"),
                    "name": Like("Llama 3.1 8B Instruct"),
                    "provider_type": Like("openrouter"),
                    "description": Like("Free model for testing"),
                    "context_length": Like(8192),
                    "cost_per_token": Like(0.0),
                    "is_free": Like(True),
                    "capabilities": EachLike("chat"),
                    "therapeutic_safety_score": Like(8.0),
                    "performance_score": Like(7.5),
                }
            )
        }

        (
            pact.given("models are available")
            .upon_receiving("a request for available models")
            .with_request("GET", "/api/v1/models")
            .will_respond_with(200, body=expected_response)
        )

        with pact:
            import requests

            response = requests.get(f"{pact.uri}/api/v1/models")

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            assert len(data["models"]) > 0
            assert "model_id" in data["models"][0]
            assert "name" in data["models"][0]
            assert "provider_type" in data["models"][0]

    def test_get_available_models_empty_contract(self):
        """Contract: GET /api/v1/models returns empty list when no models available."""
        expected_response = {"models": []}

        (
            pact.given("no models are available")
            .upon_receiving("a request for available models when none exist")
            .with_request("GET", "/api/v1/models")
            .will_respond_with(200, body=expected_response)
        )

        with pact:
            import requests

            response = requests.get(f"{pact.uri}/api/v1/models")

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            assert len(data["models"]) == 0

    def test_get_free_models_contract(self):
        """Contract: GET /api/v1/models?free_only=true returns only free models."""
        expected_response = {
            "models": EachLike(
                {
                    "model_id": Like("meta-llama/llama-3.1-8b-instruct:free"),
                    "name": Like("Llama 3.1 8B Instruct"),
                    "provider_type": Like("openrouter"),
                    "is_free": Like(True),
                    "cost_per_token": Like(0.0),
                }
            )
        }

        (
            pact.given("free models are available")
            .upon_receiving("a request for free models only")
            .with_request("GET", "/api/v1/models", query={"free_only": "true"})
            .will_respond_with(200, body=expected_response)
        )

        with pact:
            import requests

            response = requests.get(f"{pact.uri}/api/v1/models?free_only=true")

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            # All models should be free
            for model in data["models"]:
                assert model["is_free"] is True
                assert model["cost_per_token"] == 0.0


@pytest.mark.contract
@pytest.mark.skipif(not PACT_AVAILABLE, reason="pact-python not available")
class TestOpenRouterAuthAPIContract:
    """Contract tests for OpenRouter Authentication API."""

    def test_validate_api_key_contract(self):
        """Contract: POST /api/v1/openrouter/auth/validate-key validates API key."""
        request_body = {
            "api_key": Like("sk-or-v1-test-key-1234567890"),
            "validate_only": Like(False),
        }

        expected_response = {
            "valid": Like(True),
            "user": Like(
                {
                    "id": Like("user-123"),
                    "email": Like("user@example.com"),
                    "name": Like("Test User"),
                }
            ),
            "error": Like(None),
        }

        (
            pact.given("valid API key exists")
            .upon_receiving("a request to validate API key")
            .with_request(
                "POST", "/api/v1/openrouter/auth/validate-key", body=request_body
            )
            .will_respond_with(200, body=expected_response)
        )

        with pact:
            import requests

            response = requests.post(
                f"{pact.uri}/api/v1/openrouter/auth/validate-key",
                json={
                    "api_key": "sk-or-v1-test-key-1234567890",
                    "validate_only": False,
                },
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert "user" in data
            assert data["user"] is not None

    def test_validate_invalid_api_key_contract(self):
        """Contract: POST /api/v1/openrouter/auth/validate-key rejects invalid key."""
        request_body = {"api_key": Like("invalid-key"), "validate_only": Like(True)}

        expected_response = {
            "valid": Like(False),
            "user": Like(None),
            "error": Like("Invalid API key"),
        }

        (
            pact.given("invalid API key provided")
            .upon_receiving("a request to validate invalid API key")
            .with_request(
                "POST", "/api/v1/openrouter/auth/validate-key", body=request_body
            )
            .will_respond_with(200, body=expected_response)
        )

        with pact:
            import requests

            response = requests.post(
                f"{pact.uri}/api/v1/openrouter/auth/validate-key",
                json={"api_key": "invalid-key", "validate_only": True},
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert data["user"] is None
            assert "error" in data

    def test_oauth_initiate_contract(self):
        """Contract: POST /api/v1/openrouter/auth/oauth/initiate starts OAuth flow."""
        expected_response = {
            "auth_url": Term(
                r"https://openrouter\.ai/auth\?.*",
                "https://openrouter.ai/auth?client_id=test&redirect_uri=http://localhost:8080/callback",
            ),
            "code_verifier": Like("random-code-verifier-string"),
            "state": Like("random-state-string"),
        }

        (
            pact.given("OAuth is configured")
            .upon_receiving("a request to initiate OAuth flow")
            .with_request("POST", "/api/v1/openrouter/auth/oauth/initiate")
            .will_respond_with(200, body=expected_response)
        )

        with pact:
            import requests

            response = requests.post(
                f"{pact.uri}/api/v1/openrouter/auth/oauth/initiate"
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "auth_url" in data
            assert "code_verifier" in data
            assert "state" in data
            assert data["auth_url"].startswith("https://openrouter.ai/auth")


@pytest.mark.contract
@pytest.mark.skipif(not PACT_AVAILABLE, reason="pact-python not available")
class TestModelSelectionAPIContract:
    """Contract tests for Model Selection API."""

    def test_select_model_contract(self):
        """Contract: POST /api/v1/models/select selects optimal model."""
        request_body = {
            "task_type": Like("general_chat"),
            "max_latency_ms": Like(5000),
            "min_quality_score": Like(7.0),
            "max_cost_per_token": Like(0.0),
            "required_capabilities": EachLike("chat"),
            "therapeutic_safety_required": Like(True),
        }

        expected_response = {
            "model_id": Like("meta-llama/llama-3.1-8b-instruct:free"),
            "name": Like("Llama 3.1 8B Instruct"),
            "provider_type": Like("openrouter"),
            "is_free": Like(True),
            "performance_score": Like(8.0),
        }

        (
            pact.given("models are available for selection")
            .upon_receiving("a request to select optimal model")
            .with_request("POST", "/api/v1/models/select", body=request_body)
            .will_respond_with(200, body=expected_response)
        )

        with pact:
            import requests

            response = requests.post(
                f"{pact.uri}/api/v1/models/select",
                json={
                    "task_type": "general_chat",
                    "max_latency_ms": 5000,
                    "min_quality_score": 7.0,
                    "max_cost_per_token": 0.0,
                    "required_capabilities": ["chat"],
                    "therapeutic_safety_required": True,
                },
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "model_id" in data
            assert "name" in data
            assert "provider_type" in data
