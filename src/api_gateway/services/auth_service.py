"""
Authentication service for the API Gateway.

This module provides JWT authentication services that integrate with
the TTA authentication system for token validation and user management.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from ..config import get_gateway_settings
from ..models import AuthContext, AuthenticationRequest, AuthenticationResponse, TokenValidationResult


logger = logging.getLogger(__name__)


class GatewayAuthService:
    """
    Gateway authentication service.
    
    Provides JWT token validation and authentication context management
    that integrates with the TTA Player Experience authentication system.
    """
    
    def __init__(self):
        """Initialize the gateway authentication service."""
        self.settings = get_gateway_settings()
        self._tta_auth_service = None
    
    async def authenticate_request(self, auth_request: AuthenticationRequest) -> AuthenticationResponse:
        """
        Authenticate a request using JWT token.
        
        Args:
            auth_request: Authentication request with token and context
            
        Returns:
            AuthenticationResponse: Authentication result
        """
        try:
            # Validate the token
            validation_result = await self.validate_token(auth_request.token)
            
            if not validation_result.valid:
                return AuthenticationResponse(
                    success=False,
                    error=validation_result.error,
                    error_code="INVALID_TOKEN"
                )
            
            # Create authentication context
            auth_context = await self._create_auth_context_from_validation(
                validation_result,
                auth_request
            )
            
            return AuthenticationResponse(
                success=True,
                auth_context=auth_context
            )
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthenticationResponse(
                success=False,
                error=f"Authentication failed: {str(e)}",
                error_code="AUTH_ERROR"
            )
    
    async def validate_token(self, token: str) -> TokenValidationResult:
        """
        Validate a JWT token using the TTA authentication system.
        
        Args:
            token: JWT token to validate
            
        Returns:
            TokenValidationResult: Token validation result
        """
        try:
            # Get TTA auth service
            tta_auth_service = await self._get_tta_auth_service()
            
            # Validate token using TTA auth service
            authenticated_user = tta_auth_service.verify_access_token(token)
            
            # Convert to gateway format
            from ..middleware.auth import AuthenticationMiddleware
            auth_middleware = AuthenticationMiddleware(None)
            gateway_permissions = auth_middleware._convert_tta_permissions_to_gateway_permissions(
                authenticated_user.permissions,
                authenticated_user.role
            )
            
            return TokenValidationResult(
                valid=True,
                user_id=UUID(authenticated_user.user_id),
                username=authenticated_user.username,
                permissions=gateway_permissions,
                expires_at=None  # TTA tokens include expiration in payload
            )
            
        except Exception as e:
            logger.debug(f"Token validation failed: {e}")
            return TokenValidationResult(
                valid=False,
                error=str(e)
            )
    
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Optional[str]: New access token if successful
        """
        try:
            # Get TTA auth service
            tta_auth_service = await self._get_tta_auth_service()
            
            # Use TTA auth service to refresh token
            # Note: This would need to be implemented in the TTA auth service
            # For now, return None to indicate refresh not supported
            logger.warning("Token refresh not yet implemented")
            return None
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    async def validate_user_permissions(self, auth_context: AuthContext, 
                                      required_permission: str,
                                      service_name: Optional[str] = None) -> bool:
        """
        Validate user permissions for a specific action.
        
        Args:
            auth_context: User authentication context
            required_permission: Required permission level
            service_name: Optional service name for service-specific permissions
            
        Returns:
            bool: True if user has required permissions
        """
        try:
            # Check general permissions
            from ..models import PermissionLevel
            
            if required_permission == "read":
                has_permission = PermissionLevel.READ in auth_context.permissions.permissions
            elif required_permission == "write":
                has_permission = PermissionLevel.WRITE in auth_context.permissions.permissions
            elif required_permission == "admin":
                has_permission = PermissionLevel.ADMIN in auth_context.permissions.permissions
            elif required_permission == "therapeutic":
                has_permission = PermissionLevel.THERAPEUTIC in auth_context.permissions.permissions
            elif required_permission == "crisis":
                has_permission = PermissionLevel.CRISIS in auth_context.permissions.permissions
            else:
                has_permission = False
            
            # Check service-specific permissions if service name provided
            if service_name and service_name in auth_context.permissions.service_access:
                service_permissions = auth_context.permissions.service_access[service_name]
                has_service_permission = required_permission in service_permissions
                has_permission = has_permission and has_service_permission
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Permission validation error: {e}")
            return False
    
    async def check_therapeutic_context(self, auth_context: AuthContext) -> bool:
        """
        Check if the authentication context is in a therapeutic context.
        
        Args:
            auth_context: User authentication context
            
        Returns:
            bool: True if in therapeutic context
        """
        return auth_context.is_therapeutic_context()
    
    async def check_crisis_mode(self, auth_context: AuthContext) -> bool:
        """
        Check if the authentication context is in crisis mode.
        
        Args:
            auth_context: User authentication context
            
        Returns:
            bool: True if in crisis mode
        """
        return auth_context.crisis_mode or auth_context.requires_elevated_permissions()
    
    async def _get_tta_auth_service(self):
        """Get or create TTA authentication service instance."""
        if self._tta_auth_service is None:
            try:
                from src.player_experience.services.auth_service import AuthService
                self._tta_auth_service = AuthService()
            except ImportError as e:
                logger.error(f"Failed to import TTA AuthService: {e}")
                raise Exception("TTA authentication service not available")
        
        return self._tta_auth_service
    
    async def _create_auth_context_from_validation(self, 
                                                 validation_result: TokenValidationResult,
                                                 auth_request: AuthenticationRequest) -> AuthContext:
        """
        Create authentication context from token validation result.
        
        Args:
            validation_result: Token validation result
            auth_request: Original authentication request
            
        Returns:
            AuthContext: Authentication context
        """
        # Determine therapeutic context
        is_therapeutic = (
            auth_request.therapeutic_context or
            validation_result.permissions.is_therapeutic_user()
        )
        
        # Determine safety level
        safety_level = 1
        if validation_result.permissions.role.value == "patient":
            safety_level = 4 if is_therapeutic else 3
        elif validation_result.permissions.role.value == "therapist":
            safety_level = 2
        
        return AuthContext(
            user_id=validation_result.user_id,
            username=validation_result.username,
            authenticated=True,
            auth_method="jwt",
            permissions=validation_result.permissions,
            client_ip=auth_request.client_ip,
            user_agent=auth_request.user_agent,
            authenticated_at=datetime.now(timezone.utc),
            expires_at=validation_result.expires_at,
            in_therapeutic_session=is_therapeutic,
            safety_level=safety_level,
            metadata={
                "service_name": auth_request.service_name,
                "gateway_version": "1.0.0"
            }
        )


# Global instance
gateway_auth_service = GatewayAuthService()
