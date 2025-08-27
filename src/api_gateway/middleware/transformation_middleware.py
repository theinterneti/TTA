"""
Enhanced transformation middleware for the API Gateway.

This module provides comprehensive request/response transformation capabilities
including header manipulation, body transformation, content enrichment,
and therapeutic context enhancement.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from ..models import GatewayRequest, GatewayResponse, AuthContext
from ..config import get_gateway_settings


logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of transformations to perform."""
    HEADER = "header"
    BODY = "body"
    QUERY = "query"
    PATH = "path"
    CONTEXT = "context"
    THERAPEUTIC = "therapeutic"


class TransformationPhase(Enum):
    """When to apply transformations."""
    REQUEST = "request"
    RESPONSE = "response"
    BOTH = "both"


@dataclass
class TransformationRule:
    """Individual transformation rule configuration."""
    name: str
    description: str
    transformation_type: TransformationType
    phase: TransformationPhase
    enabled: bool = True
    priority: int = 100  # Lower numbers execute first
    path_patterns: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=lambda: ["*"])
    
    # Header transformations
    headers_add: Dict[str, str] = field(default_factory=dict)
    headers_remove: List[str] = field(default_factory=list)
    headers_rename: Dict[str, str] = field(default_factory=dict)
    
    # Body transformations
    body_transform_function: Optional[str] = None  # JSONPath or function name
    body_field_mappings: Dict[str, str] = field(default_factory=dict)
    body_field_additions: Dict[str, Any] = field(default_factory=dict)
    body_field_removals: List[str] = field(default_factory=list)
    
    # Query parameter transformations
    query_add: Dict[str, str] = field(default_factory=dict)
    query_remove: List[str] = field(default_factory=list)
    query_rename: Dict[str, str] = field(default_factory=dict)
    
    # Path transformations
    path_rewrite_pattern: Optional[str] = None
    path_rewrite_replacement: Optional[str] = None
    
    # Context enrichment
    add_user_context: bool = False
    add_therapeutic_context: bool = False
    add_timestamp: bool = False
    add_correlation_id: bool = False
    
    # Therapeutic transformations
    therapeutic_session_enrichment: bool = False
    crisis_mode_headers: bool = False
    therapeutic_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationConfig:
    """Configuration for transformation middleware."""
    enabled: bool = True
    preserve_original_headers: bool = True
    add_gateway_headers: bool = True
    therapeutic_enrichment: bool = True
    
    # Default transformations
    default_request_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Gateway-Version": "1.0",
        "X-Gateway-Timestamp": "${timestamp}",
        "X-Request-ID": "${correlation_id}"
    })
    
    default_response_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Gateway-Processed": "true",
        "X-Response-Time": "${response_time}"
    })
    
    # Therapeutic transformations
    therapeutic_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Therapeutic-Context": "${therapeutic_context}",
        "X-Session-ID": "${therapeutic_session_id}",
        "X-Crisis-Mode": "${crisis_mode}"
    })
    
    # Security headers
    security_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block"
    })


class TransformationMiddleware:
    """
    Enhanced transformation middleware for comprehensive request/response transformation.
    
    Provides header manipulation, body transformation, context enrichment,
    and therapeutic-specific transformations.
    """
    
    def __init__(self, config: Optional[TransformationConfig] = None):
        """
        Initialize transformation middleware.
        
        Args:
            config: Transformation configuration
        """
        self.config = config or TransformationConfig()
        self.settings = get_gateway_settings()
        
        # Transformation rules
        self.transformation_rules: List[TransformationRule] = []
        self._load_default_rules()
        
        # Custom transformation functions
        self.custom_functions: Dict[str, Callable] = {}
        self._register_default_functions()
    
    def _load_default_rules(self) -> None:
        """Load default transformation rules."""
        # Default request header transformations
        self.transformation_rules.append(TransformationRule(
            name="default_request_headers",
            description="Add default gateway headers to requests",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.REQUEST,
            priority=10,
            path_patterns=["*"],
            headers_add=self.config.default_request_headers,
            add_timestamp=True,
            add_correlation_id=True
        ))
        
        # Default response header transformations
        self.transformation_rules.append(TransformationRule(
            name="default_response_headers",
            description="Add default gateway headers to responses",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.RESPONSE,
            priority=10,
            path_patterns=["*"],
            headers_add=self.config.default_response_headers
        ))
        
        # Security headers
        self.transformation_rules.append(TransformationRule(
            name="security_headers",
            description="Add security headers to responses",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.RESPONSE,
            priority=5,
            path_patterns=["*"],
            headers_add=self.config.security_headers
        ))
        
        # Therapeutic context enrichment
        self.transformation_rules.append(TransformationRule(
            name="therapeutic_enrichment",
            description="Add therapeutic context to requests",
            transformation_type=TransformationType.THERAPEUTIC,
            phase=TransformationPhase.REQUEST,
            priority=20,
            path_patterns=["/api/therapeutic/*", "/api/sessions/*", "/api/chat/*"],
            add_therapeutic_context=True,
            therapeutic_session_enrichment=True,
            crisis_mode_headers=True,
            headers_add=self.config.therapeutic_headers
        ))
        
        # Remove hop-by-hop headers
        self.transformation_rules.append(TransformationRule(
            name="remove_hop_by_hop_headers",
            description="Remove hop-by-hop headers",
            transformation_type=TransformationType.HEADER,
            phase=TransformationPhase.BOTH,
            priority=1,
            path_patterns=["*"],
            headers_remove=[
                "connection", "keep-alive", "proxy-authenticate",
                "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
            ]
        ))
        
        # User context enrichment
        self.transformation_rules.append(TransformationRule(
            name="user_context_enrichment",
            description="Add user context to requests",
            transformation_type=TransformationType.CONTEXT,
            phase=TransformationPhase.REQUEST,
            priority=15,
            path_patterns=["*"],
            add_user_context=True,
            body_field_additions={
                "_gateway_context": {
                    "user_id": "${user_id}",
                    "username": "${username}",
                    "role": "${user_role}",
                    "timestamp": "${timestamp}"
                }
            }
        ))
    
    def _register_default_functions(self) -> None:
        """Register default transformation functions."""
        self.custom_functions.update({
            "uppercase": lambda x: str(x).upper(),
            "lowercase": lambda x: str(x).lower(),
            "trim": lambda x: str(x).strip(),
            "mask_email": self._mask_email,
            "mask_phone": self._mask_phone,
            "therapeutic_content_filter": self._therapeutic_content_filter,
            "crisis_content_detector": self._crisis_content_detector
        })
    
    async def transform_request(self, gateway_request: GatewayRequest) -> GatewayRequest:
        """
        Transform incoming request based on configured rules.
        
        Args:
            gateway_request: Original gateway request
            
        Returns:
            GatewayRequest: Transformed request
        """
        try:
            # Find applicable transformation rules for request phase
            applicable_rules = self._find_applicable_rules(
                gateway_request.path,
                gateway_request.method.value,
                TransformationPhase.REQUEST
            )
            
            # Sort rules by priority
            applicable_rules.sort(key=lambda r: r.priority)
            
            # Apply transformations
            transformed_request = gateway_request.copy()
            
            for rule in applicable_rules:
                if not rule.enabled:
                    continue
                
                try:
                    transformed_request = await self._apply_transformation_rule(
                        transformed_request, rule, is_request=True
                    )
                except Exception as e:
                    logger.error(f"Error applying transformation rule '{rule.name}': {e}")
                    # Continue with other rules
            
            return transformed_request
            
        except Exception as e:
            logger.error(f"Error during request transformation: {e}")
            return gateway_request
    
    async def transform_response(self, gateway_response: GatewayResponse, 
                               gateway_request: GatewayRequest) -> GatewayResponse:
        """
        Transform outgoing response based on configured rules.
        
        Args:
            gateway_response: Original gateway response
            gateway_request: Original gateway request for context
            
        Returns:
            GatewayResponse: Transformed response
        """
        try:
            # Find applicable transformation rules for response phase
            applicable_rules = self._find_applicable_rules(
                gateway_request.path,
                gateway_request.method.value,
                TransformationPhase.RESPONSE
            )
            
            # Sort rules by priority
            applicable_rules.sort(key=lambda r: r.priority)
            
            # Apply transformations
            transformed_response = gateway_response.copy()
            
            for rule in applicable_rules:
                if not rule.enabled:
                    continue
                
                try:
                    transformed_response = await self._apply_transformation_rule(
                        transformed_response, rule, is_request=False, 
                        request_context=gateway_request
                    )
                except Exception as e:
                    logger.error(f"Error applying transformation rule '{rule.name}': {e}")
                    # Continue with other rules
            
            return transformed_response
            
        except Exception as e:
            logger.error(f"Error during response transformation: {e}")
            return gateway_response
    
    def _find_applicable_rules(self, path: str, method: str, 
                             phase: TransformationPhase) -> List[TransformationRule]:
        """Find transformation rules applicable to the request."""
        applicable_rules = []
        
        for rule in self.transformation_rules:
            # Check phase match
            if rule.phase not in [phase, TransformationPhase.BOTH]:
                continue
            
            # Check method match
            if rule.methods != ["*"] and method not in rule.methods:
                continue
            
            # Check path pattern match
            if rule.path_patterns:
                path_match = False
                for pattern in rule.path_patterns:
                    if pattern == "*" or re.match(pattern.replace("*", ".*"), path):
                        path_match = True
                        break
                if not path_match:
                    continue
            
            applicable_rules.append(rule)
        
        return applicable_rules

    async def _apply_transformation_rule(self, target: Union[GatewayRequest, GatewayResponse],
                                       rule: TransformationRule, is_request: bool = True,
                                       request_context: Optional[GatewayRequest] = None) -> Union[GatewayRequest, GatewayResponse]:
        """Apply a single transformation rule to request or response."""

        # Header transformations
        if rule.transformation_type in [TransformationType.HEADER, TransformationType.THERAPEUTIC]:
            target = await self._transform_headers(target, rule, is_request, request_context)

        # Body transformations
        if rule.transformation_type in [TransformationType.BODY, TransformationType.THERAPEUTIC]:
            target = await self._transform_body(target, rule, is_request, request_context)

        # Query parameter transformations (request only)
        if is_request and rule.transformation_type == TransformationType.QUERY:
            target = await self._transform_query_params(target, rule)

        # Path transformations (request only)
        if is_request and rule.transformation_type == TransformationType.PATH:
            target = await self._transform_path(target, rule)

        # Context enrichment
        if rule.transformation_type in [TransformationType.CONTEXT, TransformationType.THERAPEUTIC]:
            target = await self._enrich_context(target, rule, is_request, request_context)

        return target

    async def _transform_headers(self, target: Union[GatewayRequest, GatewayResponse],
                               rule: TransformationRule, is_request: bool,
                               request_context: Optional[GatewayRequest] = None) -> Union[GatewayRequest, GatewayResponse]:
        """Transform headers based on rule configuration."""
        if not hasattr(target, 'headers') or target.headers is None:
            target.headers = {}

        # Remove headers
        for header_name in rule.headers_remove:
            target.headers.pop(header_name.lower(), None)

        # Rename headers
        for old_name, new_name in rule.headers_rename.items():
            if old_name.lower() in target.headers:
                target.headers[new_name.lower()] = target.headers.pop(old_name.lower())

        # Add headers with variable substitution
        for header_name, header_value in rule.headers_add.items():
            resolved_value = await self._resolve_variables(
                header_value, target, is_request, request_context
            )
            target.headers[header_name.lower()] = resolved_value

        # Therapeutic-specific headers
        if rule.crisis_mode_headers and hasattr(target, 'auth_context') and target.auth_context:
            if target.auth_context.get('crisis_mode'):
                target.headers['x-crisis-mode'] = 'true'
                target.headers['x-priority'] = 'high'

        return target

    async def _transform_body(self, target: Union[GatewayRequest, GatewayResponse],
                            rule: TransformationRule, is_request: bool,
                            request_context: Optional[GatewayRequest] = None) -> Union[GatewayRequest, GatewayResponse]:
        """Transform body based on rule configuration."""
        if not target.body:
            return target

        try:
            # Parse body if it's a string
            if isinstance(target.body, str):
                body_data = json.loads(target.body)
            else:
                body_data = target.body.copy() if isinstance(target.body, dict) else target.body

            # Remove fields
            if isinstance(body_data, dict):
                for field_name in rule.body_field_removals:
                    body_data.pop(field_name, None)

            # Rename/map fields
            if isinstance(body_data, dict):
                for old_field, new_field in rule.body_field_mappings.items():
                    if old_field in body_data:
                        body_data[new_field] = body_data.pop(old_field)

            # Add fields with variable substitution
            if isinstance(body_data, dict):
                for field_name, field_value in rule.body_field_additions.items():
                    resolved_value = await self._resolve_variables(
                        field_value, target, is_request, request_context
                    )
                    body_data[field_name] = resolved_value

            # Apply custom transformation function
            if rule.body_transform_function and rule.body_transform_function in self.custom_functions:
                transform_func = self.custom_functions[rule.body_transform_function]
                body_data = transform_func(body_data)

            # Update target body
            target.body = body_data

        except json.JSONDecodeError:
            # Skip transformation for non-JSON content
            logger.debug(f"Skipping body transformation for non-JSON content")
        except Exception as e:
            logger.error(f"Error transforming body: {e}")

        return target

    async def _transform_query_params(self, request: GatewayRequest,
                                    rule: TransformationRule) -> GatewayRequest:
        """Transform query parameters based on rule configuration."""
        if not request.query_params:
            request.query_params = {}

        # Remove query parameters
        for param_name in rule.query_remove:
            request.query_params.pop(param_name, None)

        # Rename query parameters
        for old_name, new_name in rule.query_rename.items():
            if old_name in request.query_params:
                request.query_params[new_name] = request.query_params.pop(old_name)

        # Add query parameters with variable substitution
        for param_name, param_value in rule.query_add.items():
            resolved_value = await self._resolve_variables(
                param_value, request, is_request=True
            )
            request.query_params[param_name] = resolved_value

        return request

    async def _transform_path(self, request: GatewayRequest,
                            rule: TransformationRule) -> GatewayRequest:
        """Transform request path based on rule configuration."""
        if rule.path_rewrite_pattern and rule.path_rewrite_replacement:
            try:
                new_path = re.sub(
                    rule.path_rewrite_pattern,
                    rule.path_rewrite_replacement,
                    request.path
                )
                request.path = new_path
            except Exception as e:
                logger.error(f"Error rewriting path: {e}")

        return request

    async def _enrich_context(self, target: Union[GatewayRequest, GatewayResponse],
                            rule: TransformationRule, is_request: bool,
                            request_context: Optional[GatewayRequest] = None) -> Union[GatewayRequest, GatewayResponse]:
        """Enrich target with contextual information."""

        # Add timestamp
        if rule.add_timestamp:
            if hasattr(target, 'headers') and target.headers is not None:
                target.headers['x-gateway-timestamp'] = datetime.utcnow().isoformat()

        # Add correlation ID
        if rule.add_correlation_id and hasattr(target, 'correlation_id'):
            if hasattr(target, 'headers') and target.headers is not None:
                target.headers['x-correlation-id'] = target.correlation_id

        # Add user context
        if rule.add_user_context and hasattr(target, 'auth_context') and target.auth_context:
            if hasattr(target, 'headers') and target.headers is not None:
                target.headers['x-user-id'] = str(target.auth_context.get('user_id', ''))
                target.headers['x-username'] = target.auth_context.get('username', '')
                target.headers['x-user-role'] = target.auth_context.get('role', '')

        # Add therapeutic context
        if rule.add_therapeutic_context:
            context_source = request_context if request_context else target
            if hasattr(context_source, 'auth_context') and context_source.auth_context:
                if hasattr(target, 'headers') and target.headers is not None:
                    target.headers['x-therapeutic-context'] = str(
                        context_source.auth_context.get('therapeutic_context', False)
                    )

        # Therapeutic session enrichment
        if rule.therapeutic_session_enrichment:
            context_source = request_context if request_context else target
            if hasattr(context_source, 'auth_context') and context_source.auth_context:
                session_id = context_source.auth_context.get('therapeutic_session_id')
                if session_id and hasattr(target, 'headers') and target.headers is not None:
                    target.headers['x-therapeutic-session-id'] = session_id

        return target

    async def _resolve_variables(self, value: Any, target: Union[GatewayRequest, GatewayResponse],
                               is_request: bool, request_context: Optional[GatewayRequest] = None) -> Any:
        """Resolve variables in transformation values."""
        if not isinstance(value, str):
            return value

        # Variable substitution patterns
        variables = {
            "${timestamp}": datetime.utcnow().isoformat(),
            "${correlation_id}": getattr(target, 'correlation_id', ''),
            "${user_id}": '',
            "${username}": '',
            "${user_role}": '',
            "${therapeutic_context}": 'false',
            "${therapeutic_session_id}": '',
            "${crisis_mode}": 'false',
            "${response_time}": ''
        }

        # Extract auth context variables
        auth_context = None
        if hasattr(target, 'auth_context') and target.auth_context:
            auth_context = target.auth_context
        elif request_context and hasattr(request_context, 'auth_context') and request_context.auth_context:
            auth_context = request_context.auth_context

        if auth_context:
            variables.update({
                "${user_id}": str(auth_context.get('user_id', '')),
                "${username}": auth_context.get('username', ''),
                "${user_role}": auth_context.get('role', ''),
                "${therapeutic_context}": str(auth_context.get('therapeutic_context', False)),
                "${therapeutic_session_id}": auth_context.get('therapeutic_session_id', ''),
                "${crisis_mode}": str(auth_context.get('crisis_mode', False))
            })

        # Calculate response time for responses
        if not is_request and hasattr(target, 'processing_time'):
            variables["${response_time}"] = f"{target.processing_time:.3f}ms"

        # Substitute variables
        resolved_value = value
        for var_name, var_value in variables.items():
            resolved_value = resolved_value.replace(var_name, str(var_value))

        return resolved_value

    def _mask_email(self, email: str) -> str:
        """Mask email address for privacy."""
        if '@' not in email:
            return email

        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for privacy."""
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) >= 10:
            return f"***-***-{digits_only[-4:]}"
        return "***-****"

    def _therapeutic_content_filter(self, content: Any) -> Any:
        """Filter therapeutic content for safety."""
        if isinstance(content, str):
            # Remove or mask sensitive therapeutic information
            # This is a placeholder - implement based on therapeutic requirements
            return content
        return content

    def _crisis_content_detector(self, content: Any) -> bool:
        """Detect crisis content in text."""
        if not isinstance(content, str):
            return False

        crisis_keywords = [
            "suicide", "kill myself", "end it all", "hurt myself",
            "hopeless", "can't go on", "give up", "desperate"
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in crisis_keywords)

    def add_transformation_rule(self, rule: TransformationRule) -> None:
        """Add a custom transformation rule."""
        self.transformation_rules.append(rule)

    def remove_transformation_rule(self, rule_name: str) -> bool:
        """Remove a transformation rule by name."""
        for i, rule in enumerate(self.transformation_rules):
            if rule.name == rule_name:
                del self.transformation_rules[i]
                return True
        return False

    def register_custom_function(self, name: str, function: Callable) -> None:
        """Register a custom transformation function."""
        self.custom_functions[name] = function

    def get_transformation_stats(self) -> Dict[str, Any]:
        """Get transformation statistics."""
        return {
            "total_rules": len(self.transformation_rules),
            "enabled_rules": len([r for r in self.transformation_rules if r.enabled]),
            "rules_by_type": {
                ttype.value: len([r for r in self.transformation_rules if r.transformation_type == ttype])
                for ttype in TransformationType
            },
            "rules_by_phase": {
                phase.value: len([r for r in self.transformation_rules if r.phase == phase])
                for phase in TransformationPhase
            },
            "custom_functions": len(self.custom_functions),
            "config": {
                "preserve_original_headers": self.config.preserve_original_headers,
                "add_gateway_headers": self.config.add_gateway_headers,
                "therapeutic_enrichment": self.config.therapeutic_enrichment
            }
        }
