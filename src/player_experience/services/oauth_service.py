"""
OAuth 2.0 Service for TTA Platform

Comprehensive OAuth 2.0 implementation with PKCE support for casual players/patients
while maintaining HIPAA-compliant JWT authentication for clinical users.
"""

import base64
import hashlib
import logging
import secrets
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import httpx
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""

    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"
    FACEBOOK = "facebook"


class AuthenticationMethod(str, Enum):
    """Authentication methods for dual authentication system."""

    JWT_CLINICAL = "jwt_clinical"  # HIPAA-compliant for clinical users
    OAUTH_CASUAL = "oauth_casual"  # OAuth for casual players/patients


@dataclass
class OAuthProviderConfig:
    """OAuth provider configuration."""

    provider: OAuthProvider
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    user_info_url: str
    scopes: list[str]
    redirect_uri: str
    enabled: bool = True


@dataclass
class PKCEChallenge:
    """PKCE challenge for OAuth security."""

    code_verifier: str
    code_challenge: str
    code_challenge_method: str = "S256"
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(
        default_factory=lambda: datetime.utcnow() + timedelta(minutes=10)
    )


@dataclass
class OAuthState:
    """OAuth state for CSRF protection."""

    state: str
    provider: OAuthProvider
    redirect_uri: str
    interface_type: str  # patient, clinical, admin, etc.
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(
        default_factory=lambda: datetime.utcnow() + timedelta(minutes=10)
    )


@dataclass
class OAuthTokens:
    """OAuth tokens from provider."""

    access_token: str
    refresh_token: str | None
    token_type: str
    expires_in: int
    scope: str | None
    id_token: str | None  # For OpenID Connect
    expires_at: datetime = field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=1)
    )


@dataclass
class OAuthUserInfo:
    """User information from OAuth provider."""

    provider: OAuthProvider
    provider_user_id: str
    email: str
    name: str | None
    given_name: str | None
    family_name: str | None
    picture: str | None
    locale: str | None
    verified_email: bool = False
    raw_data: dict[str, Any] = field(default_factory=dict)


class OAuthService:
    """OAuth 2.0 service with PKCE support for dual authentication system."""

    def __init__(self, encryption_key: bytes | None = None):
        """Initialize OAuth service."""
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

        # In-memory storage for development (use Redis/database in production)
        self.pkce_challenges: dict[str, PKCEChallenge] = {}
        self.oauth_states: dict[str, OAuthState] = {}
        self.oauth_sessions: dict[str, dict[str, Any]] = {}

        # OAuth provider configurations
        self.providers: dict[OAuthProvider, OAuthProviderConfig] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize OAuth provider configurations."""
        # Google OAuth configuration
        self.providers[OAuthProvider.GOOGLE] = OAuthProviderConfig(
            provider=OAuthProvider.GOOGLE,
            client_id="your-google-client-id",  # Configure in production
            client_secret="your-google-client-secret",
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
            scopes=["openid", "email", "profile"],
            redirect_uri="http://localhost:3000/auth/callback/google",
            enabled=True,
        )

        # Microsoft OAuth configuration
        self.providers[OAuthProvider.MICROSOFT] = OAuthProviderConfig(
            provider=OAuthProvider.MICROSOFT,
            client_id="your-microsoft-client-id",
            client_secret="your-microsoft-client-secret",
            authorization_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            user_info_url="https://graph.microsoft.com/v1.0/me",
            scopes=["openid", "email", "profile"],
            redirect_uri="http://localhost:3000/auth/callback/microsoft",
            enabled=True,
        )

        # Apple OAuth configuration
        self.providers[OAuthProvider.APPLE] = OAuthProviderConfig(
            provider=OAuthProvider.APPLE,
            client_id="your-apple-client-id",
            client_secret="your-apple-client-secret",
            authorization_url="https://appleid.apple.com/auth/authorize",
            token_url="https://appleid.apple.com/auth/token",
            user_info_url="",  # Apple provides user info in ID token
            scopes=["name", "email"],
            redirect_uri="http://localhost:3000/auth/callback/apple",
            enabled=True,
        )

        # Facebook OAuth configuration
        self.providers[OAuthProvider.FACEBOOK] = OAuthProviderConfig(
            provider=OAuthProvider.FACEBOOK,
            client_id="your-facebook-client-id",
            client_secret="your-facebook-client-secret",
            authorization_url="https://www.facebook.com/v18.0/dialog/oauth",
            token_url="https://graph.facebook.com/v18.0/oauth/access_token",
            user_info_url="https://graph.facebook.com/v18.0/me",
            scopes=["email", "public_profile"],
            redirect_uri="http://localhost:3000/auth/callback/facebook",
            enabled=True,
        )

    def generate_pkce_challenge(self) -> PKCEChallenge:
        """Generate PKCE challenge for OAuth security."""
        # Generate code verifier (43-128 characters)
        code_verifier = (
            base64.urlsafe_b64encode(secrets.token_bytes(32))
            .decode("utf-8")
            .rstrip("=")
        )

        # Generate code challenge using S256 method
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )

        challenge = PKCEChallenge(
            code_verifier=code_verifier,
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )

        # Store challenge for later verification
        challenge_id = secrets.token_hex(16)
        self.pkce_challenges[challenge_id] = challenge

        logger.info(f"Generated PKCE challenge: {challenge_id}")
        return challenge

    def generate_oauth_state(
        self,
        provider: OAuthProvider,
        redirect_uri: str,
        interface_type: str = "patient",
    ) -> str:
        """Generate OAuth state for CSRF protection."""
        state = secrets.token_hex(16)

        oauth_state = OAuthState(
            state=state,
            provider=provider,
            redirect_uri=redirect_uri,
            interface_type=interface_type,
        )

        self.oauth_states[state] = oauth_state

        logger.info(f"Generated OAuth state for {provider.value}: {state}")
        return state

    def get_authorization_url(
        self,
        provider: OAuthProvider,
        interface_type: str = "patient",
        custom_redirect_uri: str | None = None,
    ) -> dict[str, str]:
        """Get OAuth authorization URL with PKCE."""
        if provider not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        config = self.providers[provider]
        if not config.enabled:
            raise ValueError(f"OAuth provider {provider} is disabled")

        # Generate PKCE challenge
        pkce_challenge = self.generate_pkce_challenge()

        # Generate state for CSRF protection
        redirect_uri = custom_redirect_uri or config.redirect_uri
        state = self.generate_oauth_state(provider, redirect_uri, interface_type)

        # Build authorization URL parameters
        params = {
            "client_id": config.client_id,
            "response_type": "code",
            "scope": " ".join(config.scopes),
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": pkce_challenge.code_challenge,
            "code_challenge_method": pkce_challenge.code_challenge_method,
        }

        # Provider-specific parameters
        if provider == OAuthProvider.GOOGLE:
            params["access_type"] = "offline"  # For refresh token
            params["prompt"] = "consent"
        elif provider == OAuthProvider.MICROSOFT:
            params["response_mode"] = "query"
        elif provider == OAuthProvider.APPLE:
            params["response_mode"] = "form_post"

        authorization_url = (
            f"{config.authorization_url}?{urllib.parse.urlencode(params)}"
        )

        return {
            "authorization_url": authorization_url,
            "state": state,
            "code_challenge": pkce_challenge.code_challenge,
            "provider": provider.value,
        }

    async def exchange_code_for_tokens(
        self,
        provider: OAuthProvider,
        authorization_code: str,
        state: str,
    ) -> OAuthTokens:
        """Exchange authorization code for OAuth tokens."""
        # Validate state
        if state not in self.oauth_states:
            raise ValueError("Invalid or expired OAuth state")

        oauth_state = self.oauth_states[state]
        if oauth_state.provider != provider:
            raise ValueError("OAuth state provider mismatch")

        if datetime.utcnow() > oauth_state.expires_at:
            raise ValueError("OAuth state expired")

        # Find corresponding PKCE challenge
        pkce_challenge = None
        for _challenge_id, challenge in self.pkce_challenges.items():
            if challenge.expires_at > datetime.utcnow():
                pkce_challenge = challenge
                break

        if not pkce_challenge:
            raise ValueError("No valid PKCE challenge found")

        config = self.providers[provider]

        # Prepare token request
        token_data = {
            "grant_type": "authorization_code",
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": authorization_code,
            "redirect_uri": oauth_state.redirect_uri,
            "code_verifier": pkce_challenge.code_verifier,
        }

        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise ValueError(f"Token exchange failed: {response.status_code}")

            token_response = response.json()

        # Create OAuth tokens object
        oauth_tokens = OAuthTokens(
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token"),
            token_type=token_response.get("token_type", "Bearer"),
            expires_in=token_response.get("expires_in", 3600),
            scope=token_response.get("scope"),
            id_token=token_response.get("id_token"),
            expires_at=datetime.utcnow()
            + timedelta(seconds=token_response.get("expires_in", 3600)),
        )

        # Clean up used state and challenge
        del self.oauth_states[state]
        if pkce_challenge:
            # Remove the used challenge
            for challenge_id, challenge in list(self.pkce_challenges.items()):
                if challenge == pkce_challenge:
                    del self.pkce_challenges[challenge_id]
                    break

        logger.info(f"Successfully exchanged code for tokens: {provider.value}")
        return oauth_tokens

    async def get_user_info(
        self,
        provider: OAuthProvider,
        oauth_tokens: OAuthTokens,
    ) -> OAuthUserInfo:
        """Get user information from OAuth provider."""
        config = self.providers[provider]

        if provider == OAuthProvider.APPLE:
            # Apple provides user info in ID token
            return self._parse_apple_id_token(oauth_tokens.id_token)

        # Get user info from provider API
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"{oauth_tokens.token_type} {oauth_tokens.access_token}"
            }

            # Provider-specific user info requests
            if provider == OAuthProvider.FACEBOOK:
                # Facebook requires specific fields
                params = {"fields": "id,name,email,first_name,last_name,picture,locale"}
                response = await client.get(
                    config.user_info_url, headers=headers, params=params
                )
            else:
                response = await client.get(config.user_info_url, headers=headers)

            if response.status_code != 200:
                logger.error(f"User info request failed: {response.text}")
                raise ValueError(f"User info request failed: {response.status_code}")

            user_data = response.json()

        # Parse user info based on provider
        return self._parse_user_info(provider, user_data)

    def _parse_user_info(
        self, provider: OAuthProvider, user_data: dict[str, Any]
    ) -> OAuthUserInfo:
        """Parse user information from provider response."""
        if provider == OAuthProvider.GOOGLE:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data["id"],
                email=user_data.get("email", ""),
                name=user_data.get("name"),
                given_name=user_data.get("given_name"),
                family_name=user_data.get("family_name"),
                picture=user_data.get("picture"),
                locale=user_data.get("locale"),
                verified_email=user_data.get("verified_email", False),
                raw_data=user_data,
            )
        elif provider == OAuthProvider.MICROSOFT:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data["id"],
                email=user_data.get("mail") or user_data.get("userPrincipalName", ""),
                name=user_data.get("displayName"),
                given_name=user_data.get("givenName"),
                family_name=user_data.get("surname"),
                picture=None,  # Microsoft Graph requires separate request
                locale=user_data.get("preferredLanguage"),
                verified_email=True,  # Microsoft emails are verified
                raw_data=user_data,
            )
        elif provider == OAuthProvider.FACEBOOK:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data["id"],
                email=user_data.get("email", ""),
                name=user_data.get("name"),
                given_name=user_data.get("first_name"),
                family_name=user_data.get("last_name"),
                picture=user_data.get("picture", {}).get("data", {}).get("url"),
                locale=user_data.get("locale"),
                verified_email=True,  # Facebook emails are verified
                raw_data=user_data,
            )
        else:
            raise ValueError(f"Unsupported provider for user info parsing: {provider}")

    def _parse_apple_id_token(self, id_token: str | None) -> OAuthUserInfo:
        """Parse Apple ID token for user information."""
        if not id_token:
            raise ValueError("Apple ID token is required")

        # In production, properly verify and decode JWT ID token
        # For now, return minimal user info
        import base64
        import json

        try:
            # Decode JWT payload (without verification for demo)
            payload = id_token.split(".")[1]
            # Add padding if needed
            payload += "=" * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))

            return OAuthUserInfo(
                provider=OAuthProvider.APPLE,
                provider_user_id=decoded.get("sub", ""),
                email=decoded.get("email", ""),
                name=None,  # Apple may not provide name
                given_name=None,
                family_name=None,
                picture=None,
                locale=None,
                verified_email=decoded.get("email_verified", False),
                raw_data=decoded,
            )
        except Exception as e:
            logger.error(f"Failed to parse Apple ID token: {e}")
            raise ValueError("Invalid Apple ID token") from e

    async def refresh_oauth_token(
        self,
        provider: OAuthProvider,
        refresh_token: str,
    ) -> OAuthTokens:
        """Refresh OAuth access token."""
        config = self.providers[provider]

        if provider == OAuthProvider.APPLE:
            # Apple doesn't support refresh tokens in the same way
            raise ValueError("Apple OAuth refresh not supported")

        token_data = {
            "grant_type": "refresh_token",
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.text}")
                raise ValueError(f"Token refresh failed: {response.status_code}")

            token_response = response.json()

        return OAuthTokens(
            access_token=token_response["access_token"],
            refresh_token=token_response.get("refresh_token", refresh_token),
            token_type=token_response.get("token_type", "Bearer"),
            expires_in=token_response.get("expires_in", 3600),
            scope=token_response.get("scope"),
            id_token=token_response.get("id_token"),
            expires_at=datetime.utcnow()
            + timedelta(seconds=token_response.get("expires_in", 3600)),
        )

    def cleanup_expired_challenges(self) -> None:
        """Clean up expired PKCE challenges and OAuth states."""
        now = datetime.utcnow()

        # Clean up expired PKCE challenges
        expired_challenges = [
            challenge_id
            for challenge_id, challenge in self.pkce_challenges.items()
            if now > challenge.expires_at
        ]
        for challenge_id in expired_challenges:
            del self.pkce_challenges[challenge_id]

        # Clean up expired OAuth states
        expired_states = [
            state
            for state, oauth_state in self.oauth_states.items()
            if now > oauth_state.expires_at
        ]
        for state in expired_states:
            del self.oauth_states[state]

        if expired_challenges or expired_states:
            logger.info(
                f"Cleaned up {len(expired_challenges)} expired challenges and {len(expired_states)} expired states"
            )

    def get_provider_config(self, provider: OAuthProvider) -> OAuthProviderConfig:
        """Get OAuth provider configuration."""
        if provider not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        return self.providers[provider]

    def is_provider_enabled(self, provider: OAuthProvider) -> bool:
        """Check if OAuth provider is enabled."""
        return provider in self.providers and self.providers[provider].enabled

    def get_enabled_providers(self) -> list[OAuthProvider]:
        """Get list of enabled OAuth providers."""
        return [
            provider for provider, config in self.providers.items() if config.enabled
        ]

    def encrypt_oauth_tokens(self, tokens: OAuthTokens) -> str:
        """Encrypt OAuth tokens for secure storage."""
        import json

        token_data = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "expires_in": tokens.expires_in,
            "scope": tokens.scope,
            "id_token": tokens.id_token,
            "expires_at": tokens.expires_at.isoformat(),
        }

        encrypted_data = self.fernet.encrypt(json.dumps(token_data).encode())
        return encrypted_data.decode()

    def decrypt_oauth_tokens(self, encrypted_tokens: str) -> OAuthTokens:
        """Decrypt OAuth tokens from secure storage."""
        import json

        decrypted_data = self.fernet.decrypt(encrypted_tokens.encode())
        token_data = json.loads(decrypted_data.decode())

        return OAuthTokens(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            scope=token_data.get("scope"),
            id_token=token_data.get("id_token"),
            expires_at=datetime.fromisoformat(token_data["expires_at"]),
        )

    def validate_oauth_callback(
        self,
        provider: OAuthProvider,
        code: str,
        state: str,
        expected_redirect_uri: str,
    ) -> bool:
        """Validate OAuth callback parameters for security."""
        # Validate state parameter
        if state not in self.oauth_states:
            logger.warning(f"Invalid OAuth state: {state}")
            return False

        oauth_state = self.oauth_states[state]

        # Check provider match
        if oauth_state.provider != provider:
            logger.warning(
                f"OAuth provider mismatch: expected {oauth_state.provider}, got {provider}"
            )
            return False

        # Check redirect URI match
        if oauth_state.redirect_uri != expected_redirect_uri:
            logger.warning("OAuth redirect URI mismatch")
            return False

        # Check expiration
        if datetime.utcnow() > oauth_state.expires_at:
            logger.warning("OAuth state expired")
            return False

        # Validate authorization code format
        if not code or len(code) < 10:
            logger.warning("Invalid authorization code format")
            return False

        return True

    def get_oauth_security_headers(self) -> dict[str, str]:
        """Get security headers for OAuth requests."""
        return {
            "User-Agent": "TTA-OAuth-Client/1.0",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    def log_oauth_security_event(
        self,
        event_type: str,
        provider: OAuthProvider,
        user_id: str | None = None,
        details: dict[str, Any] | None = None,
        severity: str = "info",
    ):
        """Log OAuth security events for audit purposes."""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": f"oauth_{event_type}",
            "provider": provider.value,
            "user_id": user_id,
            "details": details or {},
            "severity": severity,
        }

        logger.info(f"OAuth Security Event: {event_data}")

        # In production, send to security monitoring system
        # self.security_monitor.log_event(event_data)
