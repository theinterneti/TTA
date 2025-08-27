"""
Request and response transformation service for the API Gateway.

This module provides comprehensive request/response transformation capabilities
including validation, sanitization, and therapeutic safety processing.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from pydantic import BaseModel, ValidationError

from ..config import get_gateway_settings
from ..models import GatewayRequest, GatewayResponse, AuthContext


logger = logging.getLogger(__name__)


class TransformationRule(BaseModel):
    """Rule for request/response transformation."""
    name: str
    description: Optional[str] = None
    enabled: bool = True
    path_pattern: str
    methods: List[str] = ["*"]
    
    # Request transformations
    request_headers_add: Dict[str, str] = {}
    request_headers_remove: List[str] = []
    request_body_transform: Optional[str] = None  # JSONPath or regex pattern
    
    # Response transformations
    response_headers_add: Dict[str, str] = {}
    response_headers_remove: List[str] = []
    response_body_transform: Optional[str] = None
    
    # Validation rules
    request_validation_schema: Optional[Dict[str, Any]] = None
    response_validation_schema: Optional[Dict[str, Any]] = None
    
    # Therapeutic safety
    therapeutic_content_scan: bool = False
    crisis_detection: bool = False
    sensitive_data_mask: bool = False


class RequestTransformer:
    """
    Request and response transformation service.
    
    Provides comprehensive transformation capabilities including:
    - Header manipulation
    - Body transformation and validation
    - Therapeutic content safety processing
    - Sensitive data masking
    """
    
    def __init__(self):
        """Initialize the request transformer."""
        self.settings = get_gateway_settings()
        self.transformation_rules: List[TransformationRule] = []
        self._sensitive_patterns = self._load_sensitive_patterns()
        self._crisis_keywords = self._load_crisis_keywords()
        
    def _load_sensitive_patterns(self) -> List[re.Pattern]:
        """Load patterns for sensitive data detection."""
        patterns = [
            # Social Security Numbers
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            re.compile(r'\b\d{9}\b'),
            
            # Credit Card Numbers
            re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            
            # Phone Numbers
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            
            # Email Addresses (partial masking)
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # Medical Record Numbers
            re.compile(r'\bMRN[-:\s]?\d+\b', re.IGNORECASE),
            
            # Therapeutic Session IDs (if they follow a pattern)
            re.compile(r'\bSESSION[-_]?\d+\b', re.IGNORECASE),
        ]
        return patterns
    
    def _load_crisis_keywords(self) -> List[str]:
        """Load keywords for crisis detection."""
        return [
            # Self-harm indicators
            "suicide", "kill myself", "end it all", "hurt myself", "self-harm",
            "cutting", "overdose", "jump off", "hang myself",
            
            # Crisis emotional states
            "hopeless", "worthless", "can't go on", "no point", "give up",
            "desperate", "trapped", "unbearable pain",
            
            # Immediate danger
            "right now", "tonight", "today", "this moment", "immediately",
            
            # Substance abuse crisis
            "overdosed", "too many pills", "drinking too much", "can't stop using"
        ]
    
    async def transform_request(self, gateway_request: GatewayRequest) -> GatewayRequest:
        """
        Transform incoming request based on configured rules.
        
        Args:
            gateway_request: Original gateway request
            
        Returns:
            GatewayRequest: Transformed request
        """
        try:
            # Find applicable transformation rules
            applicable_rules = self._find_applicable_rules(
                gateway_request.path, 
                gateway_request.method.value
            )
            
            # Apply transformations
            transformed_request = gateway_request.copy()
            
            for rule in applicable_rules:
                if not rule.enabled:
                    continue
                
                # Transform headers
                transformed_request = self._transform_request_headers(transformed_request, rule)
                
                # Transform body
                transformed_request = await self._transform_request_body(transformed_request, rule)
                
                # Validate request
                if rule.request_validation_schema:
                    await self._validate_request(transformed_request, rule)
                
                # Therapeutic safety processing
                if rule.therapeutic_content_scan or rule.crisis_detection:
                    await self._process_therapeutic_safety(transformed_request, rule)
            
            return transformed_request
            
        except Exception as e:
            logger.error(f"Request transformation failed: {e}")
            # Return original request if transformation fails
            return gateway_request
    
    async def transform_response(self, response_data: bytes, content_type: str,
                               gateway_request: GatewayRequest) -> bytes:
        """
        Transform service response based on configured rules.
        
        Args:
            response_data: Original response data
            content_type: Response content type
            gateway_request: Original gateway request
            
        Returns:
            bytes: Transformed response data
        """
        try:
            # Find applicable transformation rules
            applicable_rules = self._find_applicable_rules(
                gateway_request.path,
                gateway_request.method.value
            )
            
            transformed_data = response_data
            
            for rule in applicable_rules:
                if not rule.enabled:
                    continue
                
                # Transform response body
                transformed_data = await self._transform_response_body(
                    transformed_data, content_type, rule
                )
                
                # Mask sensitive data if required
                if rule.sensitive_data_mask:
                    transformed_data = self._mask_sensitive_data(transformed_data, content_type)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Response transformation failed: {e}")
            # Return original response if transformation fails
            return response_data
    
    def _find_applicable_rules(self, path: str, method: str) -> List[TransformationRule]:
        """Find transformation rules applicable to the request."""
        applicable_rules = []
        
        for rule in self.transformation_rules:
            # Check path pattern
            import fnmatch
            if not fnmatch.fnmatch(path, rule.path_pattern):
                continue
            
            # Check method
            if rule.methods and "*" not in rule.methods and method not in rule.methods:
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    def _transform_request_headers(self, request: GatewayRequest, 
                                 rule: TransformationRule) -> GatewayRequest:
        """Transform request headers based on rule."""
        headers = request.headers.copy()
        
        # Add headers
        for header_name, header_value in rule.request_headers_add.items():
            headers[header_name] = header_value
        
        # Remove headers
        for header_name in rule.request_headers_remove:
            headers.pop(header_name, None)
        
        request.headers = headers
        return request
    
    async def _transform_request_body(self, request: GatewayRequest,
                                    rule: TransformationRule) -> GatewayRequest:
        """Transform request body based on rule."""
        if not request.body or not rule.request_body_transform:
            return request
        
        try:
            # Parse JSON body if applicable
            content_type = request.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                body_data = json.loads(request.body.decode('utf-8'))
                
                # Apply transformation (simplified - could be extended with JSONPath)
                if rule.request_body_transform == "add_timestamp":
                    body_data["_gateway_timestamp"] = datetime.utcnow().isoformat()
                elif rule.request_body_transform == "add_user_context":
                    if request.auth_context:
                        body_data["_user_context"] = {
                            "user_id": request.auth_context.get("user_id"),
                            "role": request.auth_context.get("role"),
                            "therapeutic": request.auth_context.get("therapeutic_context", False)
                        }
                
                request.body = json.dumps(body_data).encode('utf-8')
        
        except Exception as e:
            logger.warning(f"Request body transformation failed: {e}")
        
        return request
    
    async def _transform_response_body(self, response_data: bytes, content_type: str,
                                     rule: TransformationRule) -> bytes:
        """Transform response body based on rule."""
        if not response_data or not rule.response_body_transform:
            return response_data
        
        try:
            if "application/json" in content_type.lower():
                response_json = json.loads(response_data.decode('utf-8'))
                
                # Apply transformation
                if rule.response_body_transform == "add_gateway_metadata":
                    if isinstance(response_json, dict):
                        response_json["_gateway"] = {
                            "transformed": True,
                            "timestamp": datetime.utcnow().isoformat(),
                            "version": "1.0.0"
                        }
                
                return json.dumps(response_json).encode('utf-8')
        
        except Exception as e:
            logger.warning(f"Response body transformation failed: {e}")
        
        return response_data
    
    async def _validate_request(self, request: GatewayRequest, rule: TransformationRule) -> None:
        """Validate request against schema."""
        if not rule.request_validation_schema or not request.body:
            return
        
        try:
            content_type = request.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                body_data = json.loads(request.body.decode('utf-8'))
                
                # Simple validation (could be extended with jsonschema)
                required_fields = rule.request_validation_schema.get("required", [])
                for field in required_fields:
                    if field not in body_data:
                        raise ValidationError(f"Required field '{field}' missing")
        
        except Exception as e:
            logger.error(f"Request validation failed: {e}")
            raise
    
    async def _process_therapeutic_safety(self, request: GatewayRequest,
                                        rule: TransformationRule) -> None:
        """Process therapeutic safety checks."""
        if not request.body:
            return
        
        try:
            # Convert body to text for analysis
            body_text = ""
            content_type = request.headers.get("content-type", "").lower()
            
            if "application/json" in content_type:
                body_data = json.loads(request.body.decode('utf-8'))
                body_text = json.dumps(body_data, indent=2)
            else:
                body_text = request.body.decode('utf-8', errors='ignore')
            
            # Crisis detection
            if rule.crisis_detection:
                crisis_detected = self._detect_crisis_content(body_text)
                if crisis_detected:
                    logger.warning(
                        f"Crisis content detected in request {request.correlation_id}",
                        extra={
                            "correlation_id": request.correlation_id,
                            "user_id": request.auth_context.get("user_id") if request.auth_context else None,
                            "crisis_detected": True,
                            "event_type": "crisis_detection"
                        }
                    )
                    # Set crisis mode flag
                    request.crisis_mode = True
        
        except Exception as e:
            logger.error(f"Therapeutic safety processing failed: {e}")
    
    def _detect_crisis_content(self, text: str) -> bool:
        """Detect crisis-related content in text."""
        text_lower = text.lower()
        
        # Check for crisis keywords
        crisis_score = 0
        for keyword in self._crisis_keywords:
            if keyword in text_lower:
                crisis_score += 1
        
        # Threshold for crisis detection (configurable)
        return crisis_score >= 2
    
    def _mask_sensitive_data(self, data: bytes, content_type: str) -> bytes:
        """Mask sensitive data in response."""
        try:
            if "application/json" in content_type.lower():
                response_json = json.loads(data.decode('utf-8'))
                masked_json = self._mask_json_sensitive_data(response_json)
                return json.dumps(masked_json).encode('utf-8')
            else:
                # Mask in plain text
                text = data.decode('utf-8', errors='ignore')
                masked_text = self._mask_text_sensitive_data(text)
                return masked_text.encode('utf-8')
        
        except Exception as e:
            logger.warning(f"Sensitive data masking failed: {e}")
            return data
    
    def _mask_json_sensitive_data(self, data: Any) -> Any:
        """Recursively mask sensitive data in JSON."""
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if key.lower() in ['ssn', 'social_security', 'credit_card', 'password', 'token']:
                    masked_data[key] = "***MASKED***"
                else:
                    masked_data[key] = self._mask_json_sensitive_data(value)
            return masked_data
        elif isinstance(data, list):
            return [self._mask_json_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            return self._mask_text_sensitive_data(data)
        else:
            return data
    
    def _mask_text_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text using regex patterns."""
        masked_text = text
        
        for pattern in self._sensitive_patterns:
            masked_text = pattern.sub("***MASKED***", masked_text)
        
        return masked_text
    
    def add_transformation_rule(self, rule: TransformationRule) -> None:
        """Add a new transformation rule."""
        self.transformation_rules.append(rule)
        logger.info(f"Added transformation rule: {rule.name}")
    
    def remove_transformation_rule(self, rule_name: str) -> bool:
        """Remove a transformation rule by name."""
        original_count = len(self.transformation_rules)
        self.transformation_rules = [
            rule for rule in self.transformation_rules 
            if rule.name != rule_name
        ]
        
        removed = len(self.transformation_rules) < original_count
        if removed:
            logger.info(f"Removed transformation rule: {rule_name}")
        
        return removed
    
    def get_transformation_rules(self) -> List[TransformationRule]:
        """Get all transformation rules."""
        return self.transformation_rules.copy()
