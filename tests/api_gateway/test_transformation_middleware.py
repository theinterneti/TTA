"""
Tests for the API Gateway transformation middleware.

This module contains unit tests for enhanced transformation middleware,
header manipulation, body transformation, and therapeutic context enrichment.
"""

from uuid import uuid4

import pytest

from src.api_gateway.middleware.transformation_middleware import (
    TransformationConfig,
    TransformationMiddleware,
    TransformationPhase,
    TransformationRule,
    TransformationType,
)
from src.api_gateway.models import GatewayRequest, GatewayResponse, RequestMethod


@pytest.fixture
def transformation_config():
    """Create transformation configuration for testing."""
    return TransformationConfig(
        enabled=True,
        preserve_original_headers=True,
        add_gateway_headers=True,
        therapeutic_enrichment=True,
    )


@pytest.fixture
def transformation_middleware(transformation_config):
    """Create transformation middleware for testing."""
    return TransformationMiddleware(transformation_config)


@pytest.fixture
def mock_gateway_request():
    """Create a mock gateway request."""
    return GatewayRequest(
        correlation_id=str(uuid4()),
        method=RequestMethod.POST,
        path="/api/test",
        client_ip="127.0.0.1",
        headers={"content-type": "application/json", "user-agent": "test-client"},
        body={"message": "test message", "user_id": "123"},
        auth_context={
            "user_id": "123",
            "username": "test_user",
            "role": "patient",
            "therapeutic_context": True,
        },
    )


@pytest.fixture
def mock_gateway_response():
    """Create a mock gateway response."""
    return GatewayResponse(
        status_code=200,
        headers={"content-type": "application/json"},
        body={"result": "success", "data": {"id": "123"}},
        processing_time=50.0,
    )


@pytest.fixture
def therapeutic_gateway_request():
    """Create a therapeutic gateway request."""
    return GatewayRequest(
        correlation_id=str(uuid4()),
        method=RequestMethod.POST,
        path="/api/therapeutic/session",
        client_ip="127.0.0.1",
        headers={"content-type": "application/json"},
        body={
            "message": "I'm feeling better today",
            "session_id": "session-123",
            "mood_score": 7,
        },
        auth_context={
            "user_id": "123",
            "username": "test_user",
            "role": "patient",
            "therapeutic_context": True,
            "therapeutic_session_id": "session-123",
            "crisis_mode": False,
        },
    )


class TestTransformationMiddleware:
    """Test cases for TransformationMiddleware."""

    @pytest.mark.asyncio
    async def test_transform_request_basic(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test basic request transformation."""
        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should add default gateway headers
        assert "x-gateway-version" in result.headers
        assert "x-gateway-timestamp" in result.headers
        assert "x-request-id" in result.headers

        # Should preserve original headers
        assert result.headers["content-type"] == "application/json"
        assert result.headers["user-agent"] == "test-client"

    @pytest.mark.asyncio
    async def test_transform_response_basic(
        self, transformation_middleware, mock_gateway_response, mock_gateway_request
    ):
        """Test basic response transformation."""
        result = await transformation_middleware.transform_response(
            mock_gateway_response, mock_gateway_request
        )

        # Should add default response headers
        assert "x-gateway-processed" in result.headers
        assert "x-response-time" in result.headers

        # Should add security headers
        assert "x-content-type-options" in result.headers
        assert "x-frame-options" in result.headers
        assert "x-xss-protection" in result.headers

        assert result.headers["x-content-type-options"] == "nosniff"
        assert result.headers["x-frame-options"] == "DENY"

    @pytest.mark.asyncio
    async def test_transform_therapeutic_request(
        self, transformation_middleware, therapeutic_gateway_request
    ):
        """Test therapeutic request transformation."""
        result = await transformation_middleware.transform_request(
            therapeutic_gateway_request
        )

        # Should add therapeutic context headers
        assert "x-therapeutic-context" in result.headers
        assert "x-session-id" in result.headers
        assert "x-crisis-mode" in result.headers

        assert result.headers["x-therapeutic-context"] == "True"
        assert result.headers["x-session-id"] == "session-123"
        assert result.headers["x-crisis-mode"] == "False"

    @pytest.mark.asyncio
    async def test_transform_user_context_enrichment(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test user context enrichment."""
        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should add user context headers
        assert "x-user-id" in result.headers
        assert "x-username" in result.headers
        assert "x-user-role" in result.headers

        assert result.headers["x-user-id"] == "123"
        assert result.headers["x-username"] == "test_user"
        assert result.headers["x-user-role"] == "patient"

    @pytest.mark.asyncio
    async def test_transform_body_field_additions(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test body field additions."""
        # Add a custom transformation rule
        body_rule = TransformationRule(
            name="test_body_addition",
            description="Add fields to request body",
            transformation_type=TransformationType.BODY,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            body_field_additions={
                "timestamp": "${timestamp}",
                "gateway_version": "1.0",
            },
        )
        transformation_middleware.add_transformation_rule(body_rule)

        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should add fields to body
        assert "timestamp" in result.body
        assert "gateway_version" in result.body
        assert result.body["gateway_version"] == "1.0"

    @pytest.mark.asyncio
    async def test_transform_body_field_removals(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test body field removals."""
        # Add a custom transformation rule
        removal_rule = TransformationRule(
            name="test_body_removal",
            description="Remove fields from request body",
            transformation_type=TransformationType.BODY,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            body_field_removals=["user_id"],
        )
        transformation_middleware.add_transformation_rule(removal_rule)

        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should remove user_id field
        assert "user_id" not in result.body
        assert "message" in result.body  # Other fields should remain

    @pytest.mark.asyncio
    async def test_transform_body_field_mappings(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test body field mappings/renaming."""
        # Add a custom transformation rule
        mapping_rule = TransformationRule(
            name="test_body_mapping",
            description="Map/rename fields in request body",
            transformation_type=TransformationType.BODY,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            body_field_mappings={"user_id": "userId", "message": "content"},
        )
        transformation_middleware.add_transformation_rule(mapping_rule)

        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should rename fields
        assert "user_id" not in result.body
        assert "message" not in result.body
        assert "userId" in result.body
        assert "content" in result.body
        assert result.body["userId"] == "123"
        assert result.body["content"] == "test message"

    @pytest.mark.asyncio
    async def test_transform_header_operations(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test header add, remove, and rename operations."""
        # Add a custom transformation rule
        header_rule = TransformationRule(
            name="test_header_ops",
            description="Test header operations",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            headers_add={"x-custom-header": "custom-value"},
            headers_remove=["user-agent"],
            headers_rename={"content-type": "content-type-renamed"},
        )
        transformation_middleware.add_transformation_rule(header_rule)

        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should add custom header
        assert "x-custom-header" in result.headers
        assert result.headers["x-custom-header"] == "custom-value"

        # Should remove user-agent header
        assert "user-agent" not in result.headers

        # Should rename content-type header
        assert "content-type" not in result.headers
        assert "content-type-renamed" in result.headers

    @pytest.mark.asyncio
    async def test_transform_query_parameters(self, transformation_middleware):
        """Test query parameter transformations."""
        request_with_query = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.GET,
            path="/api/test",
            client_ip="127.0.0.1",
            query_params={"old_param": "value", "keep_param": "keep"},
        )

        # Add a custom transformation rule
        query_rule = TransformationRule(
            name="test_query_ops",
            description="Test query parameter operations",
            transformation_type=TransformationType.QUERY,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            query_add={"new_param": "new_value"},
            query_remove=["old_param"],
            query_rename={"keep_param": "renamed_param"},
        )
        transformation_middleware.add_transformation_rule(query_rule)

        result = await transformation_middleware.transform_request(request_with_query)

        # Should add new parameter
        assert "new_param" in result.query_params
        assert result.query_params["new_param"] == "new_value"

        # Should remove old parameter
        assert "old_param" not in result.query_params

        # Should rename parameter
        assert "keep_param" not in result.query_params
        assert "renamed_param" in result.query_params
        assert result.query_params["renamed_param"] == "keep"

    @pytest.mark.asyncio
    async def test_transform_path_rewrite(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test path rewriting."""
        # Add a custom transformation rule
        path_rule = TransformationRule(
            name="test_path_rewrite",
            description="Test path rewriting",
            transformation_type=TransformationType.PATH,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            path_rewrite_pattern=r"/api/test",
            path_rewrite_replacement="/api/v2/test",
        )
        transformation_middleware.add_transformation_rule(path_rule)

        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should rewrite path
        assert result.path == "/api/v2/test"

    @pytest.mark.asyncio
    async def test_transform_variable_substitution(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test variable substitution in transformations."""
        # Add a custom transformation rule with variables
        variable_rule = TransformationRule(
            name="test_variables",
            description="Test variable substitution",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            headers_add={
                "x-user": "${username}",
                "x-user-id": "${user_id}",
                "x-correlation": "${correlation_id}",
            },
        )
        transformation_middleware.add_transformation_rule(variable_rule)

        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should substitute variables
        assert result.headers["x-user"] == "test_user"
        assert result.headers["x-user-id"] == "123"
        assert result.headers["x-correlation"] == mock_gateway_request.correlation_id

    @pytest.mark.asyncio
    async def test_transform_custom_function(
        self, transformation_middleware, mock_gateway_request
    ):
        """Test custom transformation function."""

        # Register a custom function
        def uppercase_transform(data):
            if isinstance(data, dict) and "message" in data:
                data["message"] = data["message"].upper()
            return data

        transformation_middleware.register_custom_function(
            "uppercase", uppercase_transform
        )

        # Add a custom transformation rule
        custom_rule = TransformationRule(
            name="test_custom_function",
            description="Test custom transformation function",
            transformation_type=TransformationType.BODY,
            phase=TransformationPhase.REQUEST,
            path_patterns=["/api/test"],
            body_transform_function="uppercase",
        )
        transformation_middleware.add_transformation_rule(custom_rule)

        result = await transformation_middleware.transform_request(mock_gateway_request)

        # Should apply custom transformation
        assert result.body["message"] == "TEST MESSAGE"

    @pytest.mark.asyncio
    async def test_transform_crisis_mode_headers(self, transformation_middleware):
        """Test crisis mode header addition."""
        crisis_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/therapeutic/session",
            client_ip="127.0.0.1",
            body={"message": "crisis message"},
            auth_context={
                "user_id": "123",
                "crisis_mode": True,
                "therapeutic_context": True,
            },
        )

        result = await transformation_middleware.transform_request(crisis_request)

        # Should add crisis mode headers
        assert "x-crisis-mode" in result.headers
        assert "x-priority" in result.headers
        assert result.headers["x-crisis-mode"] == "true"
        assert result.headers["x-priority"] == "high"

    def test_add_transformation_rule(self, transformation_middleware):
        """Test adding custom transformation rule."""
        initial_count = len(transformation_middleware.transformation_rules)

        custom_rule = TransformationRule(
            name="custom_rule",
            description="Custom transformation rule",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.REQUEST,
        )

        transformation_middleware.add_transformation_rule(custom_rule)

        assert len(transformation_middleware.transformation_rules) == initial_count + 1
        assert custom_rule in transformation_middleware.transformation_rules

    def test_remove_transformation_rule(self, transformation_middleware):
        """Test removing transformation rule."""
        # Add a rule first
        custom_rule = TransformationRule(
            name="removable_rule",
            description="Rule to be removed",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.REQUEST,
        )
        transformation_middleware.add_transformation_rule(custom_rule)

        initial_count = len(transformation_middleware.transformation_rules)

        # Remove the rule
        result = transformation_middleware.remove_transformation_rule("removable_rule")

        assert result is True
        assert len(transformation_middleware.transformation_rules) == initial_count - 1

        # Try to remove non-existent rule
        result = transformation_middleware.remove_transformation_rule("non_existent")
        assert result is False

    def test_get_transformation_stats(self, transformation_middleware):
        """Test getting transformation statistics."""
        stats = transformation_middleware.get_transformation_stats()

        assert "total_rules" in stats
        assert "enabled_rules" in stats
        assert "rules_by_type" in stats
        assert "rules_by_phase" in stats
        assert "custom_functions" in stats
        assert "config" in stats

        assert isinstance(stats["total_rules"], int)
        assert isinstance(stats["enabled_rules"], int)
        assert isinstance(stats["rules_by_type"], dict)
        assert isinstance(stats["rules_by_phase"], dict)
        assert isinstance(stats["custom_functions"], int)
        assert isinstance(stats["config"], dict)
