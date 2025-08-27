"""
Tests for the API Gateway validation middleware.

This module contains unit tests for enhanced validation middleware,
schema validation, security checks, and therapeutic safety validation.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException

from src.api_gateway.middleware.validation_middleware import (
    ValidationMiddleware, ValidationConfig, ValidationRule, ValidationType, ValidationSeverity
)
from src.api_gateway.models import GatewayRequest, RequestMethod, AuthContext, UserPermissions, UserRole


@pytest.fixture
def validation_config():
    """Create validation configuration for testing."""
    return ValidationConfig(
        enabled=True,
        fail_fast=False,
        log_validation_errors=True,
        return_detailed_errors=True,
        therapeutic_validation_required=True,
        max_request_size=1024 * 1024,  # 1MB for testing
        max_json_depth=5,
        max_array_length=100,
        max_string_length=1000
    )


@pytest.fixture
def validation_middleware(validation_config):
    """Create validation middleware for testing."""
    return ValidationMiddleware(validation_config)


@pytest.fixture
def mock_gateway_request():
    """Create a mock gateway request."""
    return GatewayRequest(
        correlation_id=str(uuid4()),
        method=RequestMethod.POST,
        path="/api/test",
        client_ip="127.0.0.1",
        headers={"content-type": "application/json"},
        body={"message": "test message", "user_id": "123"},
        auth_context={
            "user_id": "123",
            "username": "test_user",
            "role": "patient",
            "therapeutic_context": True
        }
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
            "message": "I'm feeling really hopeless today",
            "session_id": "session-123",
            "mood_score": 3
        },
        auth_context={
            "user_id": "123",
            "username": "test_user",
            "role": "patient",
            "therapeutic_context": True,
            "therapeutic_session_id": "session-123"
        }
    )


class TestValidationMiddleware:
    """Test cases for ValidationMiddleware."""
    
    @pytest.mark.asyncio
    async def test_validate_request_success(self, validation_middleware, mock_gateway_request):
        """Test successful request validation."""
        result = await validation_middleware.validate_request(mock_gateway_request)
        
        assert result == mock_gateway_request
        assert result.correlation_id == mock_gateway_request.correlation_id
    
    @pytest.mark.asyncio
    async def test_validate_request_with_json_schema(self, validation_middleware, mock_gateway_request):
        """Test request validation with JSON schema."""
        # Add a schema validation rule
        schema_rule = ValidationRule(
            name="test_schema",
            description="Test JSON schema validation",
            validation_type=ValidationType.SCHEMA,
            severity=ValidationSeverity.ERROR,
            path_patterns=["/api/test"],
            json_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "user_id": {"type": "string"}
                },
                "required": ["message", "user_id"]
            }
        )
        validation_middleware.add_validation_rule(schema_rule)
        
        result = await validation_middleware.validate_request(mock_gateway_request)
        assert result == mock_gateway_request
    
    @pytest.mark.asyncio
    async def test_validate_request_schema_failure(self, validation_middleware, mock_gateway_request):
        """Test request validation with schema failure."""
        # Add a schema validation rule that will fail
        schema_rule = ValidationRule(
            name="test_schema_fail",
            description="Test JSON schema validation failure",
            validation_type=ValidationType.SCHEMA,
            severity=ValidationSeverity.ERROR,
            path_patterns=["/api/test"],
            json_schema={
                "type": "object",
                "properties": {
                    "required_field": {"type": "string"}
                },
                "required": ["required_field"]
            }
        )
        validation_middleware.add_validation_rule(schema_rule)
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(mock_gateway_request)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validate_request_size_limits(self, validation_middleware):
        """Test request size validation."""
        # Create request with large body
        large_body = {"data": "x" * 2000}  # Exceeds max_string_length
        large_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/test",
            client_ip="127.0.0.1",
            body=large_body
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(large_request)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validate_request_security_sql_injection(self, validation_middleware):
        """Test SQL injection detection."""
        # Create request with SQL injection attempt
        malicious_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/test",
            client_ip="127.0.0.1",
            body={"query": "SELECT * FROM users WHERE id = 1 OR 1=1"}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(malicious_request)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validate_request_security_xss(self, validation_middleware):
        """Test XSS detection."""
        # Create request with XSS attempt
        malicious_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/test",
            client_ip="127.0.0.1",
            body={"content": "<script>alert('xss')</script>"}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(malicious_request)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validate_therapeutic_content(self, validation_middleware, therapeutic_gateway_request):
        """Test therapeutic content validation."""
        result = await validation_middleware.validate_request(therapeutic_gateway_request)
        
        # Should not raise exception but should detect crisis content
        assert result == therapeutic_gateway_request
        # Crisis mode should be set due to "hopeless" keyword
        assert result.auth_context.get("crisis_mode") is True
    
    @pytest.mark.asyncio
    async def test_validate_crisis_detection(self, validation_middleware):
        """Test crisis content detection."""
        crisis_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/therapeutic/session",
            client_ip="127.0.0.1",
            body={
                "message": "I want to kill myself tonight",
                "session_id": "session-123"
            },
            auth_context={
                "user_id": "123",
                "username": "test_user",
                "therapeutic_context": True
            }
        )
        
        with patch('src.api_gateway.middleware.validation_middleware.logger') as mock_logger:
            result = await validation_middleware.validate_request(crisis_request)
            
            # Should log critical crisis alert
            mock_logger.critical.assert_called()
            assert result.auth_context.get("crisis_mode") is True
    
    @pytest.mark.asyncio
    async def test_validate_therapeutic_field_patterns(self, validation_middleware):
        """Test therapeutic field pattern validation."""
        # Create request with invalid therapeutic field format
        invalid_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/therapeutic/session",
            client_ip="127.0.0.1",
            body={
                "mood_score": "invalid",  # Should be 1-10
                "session_id": "session-123"
            },
            auth_context={"therapeutic_context": True}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(invalid_request)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validate_json_depth_limit(self, validation_middleware):
        """Test JSON depth limit validation."""
        # Create deeply nested JSON
        deep_json = {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": "too deep"}}}}}}
        deep_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/test",
            client_ip="127.0.0.1",
            body=deep_json
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(deep_request)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validate_array_length_limit(self, validation_middleware):
        """Test array length limit validation."""
        # Create request with large array
        large_array_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/test",
            client_ip="127.0.0.1",
            body={"items": list(range(150))}  # Exceeds max_array_length of 100
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(large_array_request)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_validate_path_traversal(self, validation_middleware):
        """Test path traversal detection."""
        malicious_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/test",
            client_ip="127.0.0.1",
            body={"file_path": "../../../etc/passwd"}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await validation_middleware.validate_request(malicious_request)
        
        assert exc_info.value.status_code == 400
    
    def test_add_validation_rule(self, validation_middleware):
        """Test adding custom validation rule."""
        initial_count = len(validation_middleware.validation_rules)
        
        custom_rule = ValidationRule(
            name="custom_rule",
            description="Custom validation rule",
            validation_type=ValidationType.CONTENT,
            severity=ValidationSeverity.WARNING
        )
        
        validation_middleware.add_validation_rule(custom_rule)
        
        assert len(validation_middleware.validation_rules) == initial_count + 1
        assert custom_rule in validation_middleware.validation_rules
    
    def test_remove_validation_rule(self, validation_middleware):
        """Test removing validation rule."""
        # Add a rule first
        custom_rule = ValidationRule(
            name="removable_rule",
            description="Rule to be removed",
            validation_type=ValidationType.CONTENT,
            severity=ValidationSeverity.INFO
        )
        validation_middleware.add_validation_rule(custom_rule)
        
        initial_count = len(validation_middleware.validation_rules)
        
        # Remove the rule
        result = validation_middleware.remove_validation_rule("removable_rule")
        
        assert result is True
        assert len(validation_middleware.validation_rules) == initial_count - 1
        
        # Try to remove non-existent rule
        result = validation_middleware.remove_validation_rule("non_existent")
        assert result is False
    
    def test_get_validation_stats(self, validation_middleware):
        """Test getting validation statistics."""
        stats = validation_middleware.get_validation_stats()
        
        assert "total_rules" in stats
        assert "enabled_rules" in stats
        assert "rules_by_type" in stats
        assert "rules_by_severity" in stats
        assert "config" in stats
        
        assert isinstance(stats["total_rules"], int)
        assert isinstance(stats["enabled_rules"], int)
        assert isinstance(stats["rules_by_type"], dict)
        assert isinstance(stats["rules_by_severity"], dict)
        assert isinstance(stats["config"], dict)
    
    @pytest.mark.asyncio
    async def test_fail_fast_behavior(self, validation_config):
        """Test fail-fast behavior."""
        validation_config.fail_fast = True
        middleware = ValidationMiddleware(validation_config)
        
        # Create request that will trigger multiple validation errors
        bad_request = GatewayRequest(
            correlation_id=str(uuid4()),
            method=RequestMethod.POST,
            path="/api/test",
            client_ip="127.0.0.1",
            body={"query": "SELECT * FROM users", "content": "<script>alert('xss')</script>"}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await middleware.validate_request(bad_request)
        
        # Should fail on first critical error
        assert exc_info.value.status_code == 400
