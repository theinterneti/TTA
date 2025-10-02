"""
OpenRouter Authentication Router

Provides secure authentication endpoints for OpenRouter integration including:
- API key validation and secure storage
- OAuth 2.0 flow with PKCE
- Session management
- User info retrieval
"""

import base64
import hashlib
import logging
import os
import secrets
from typing import Any
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openrouter/auth", tags=["openrouter-auth"])

# Security
security = HTTPBearer(auto_error=False)

# Encryption for API keys (in production, use proper key management)
ENCRYPTION_KEY = os.getenv("OPENROUTER_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key for development (in production, use proper key management)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    logger.warning(
        "Using generated encryption key for development. Use proper key management in production."
    )

fernet = Fernet(
    ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY
)

# OpenRouter OAuth configuration
OPENROUTER_CLIENT_ID = os.getenv("OPENROUTER_CLIENT_ID")
OPENROUTER_CLIENT_SECRET = os.getenv("OPENROUTER_CLIENT_SECRET")
OPENROUTER_REDIRECT_URI = os.getenv(
    "OPENROUTER_REDIRECT_URI",
    "http://localhost:8080/api/v1/openrouter/auth/oauth/callback",
)

# In-memory storage (in production, use Redis or database)
user_sessions: dict[str, dict[str, Any]] = {}
oauth_states: dict[str, dict[str, Any]] = {}


class ApiKeyValidationRequest(BaseModel):
    api_key: str = Field(..., min_length=1)
    validate_only: bool = False


class ApiKeyValidationResponse(BaseModel):
    valid: bool
    user: dict[str, Any] | None = None
    error: str | None = None


class OAuthInitiateResponse(BaseModel):
    auth_url: str
    code_verifier: str
    state: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str


class OAuthCallbackResponse(BaseModel):
    success: bool
    user: dict[str, Any] | None = None
    session_id: str | None = None
    error: str | None = None


def generate_code_verifier() -> str:
    """Generate a code verifier for PKCE."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")


def generate_code_challenge(verifier: str) -> str:
    """Generate a code challenge from verifier for PKCE."""
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for secure storage."""
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage."""
    return fernet.decrypt(encrypted_key.encode()).decode()


async def validate_openrouter_api_key(api_key: str) -> dict[str, Any]:
    """Validate an OpenRouter API key and get user info."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "valid": True,
                    "user": {
                        "id": data.get("data", {}).get("id"),
                        "email": data.get("data", {}).get("email"),
                        "name": data.get("data", {}).get("label", "OpenRouter User"),
                        "credits": data.get("data", {}).get("credit_balance", 0),
                        "usage": {
                            "requests": data.get("data", {})
                            .get("usage", {})
                            .get("requests", 0),
                            "tokens": data.get("data", {})
                            .get("usage", {})
                            .get("tokens", 0),
                        },
                    },
                }
            else:
                return {"valid": False, "error": "Invalid API key"}

    except Exception as e:
        logger.error(f"API key validation failed: {e}")
        return {"valid": False, "error": str(e)}


def get_session_id(request: Request) -> str | None:
    """Get session ID from request cookies."""
    return request.cookies.get("openrouter_session_id")


def create_session(user_data: dict[str, Any], api_key: str | None = None) -> str:
    """Create a new user session."""
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "user": user_data,
        "created_at": secrets.token_hex(8),  # Simplified timestamp
        "auth_method": "oauth" if not api_key else "api_key",
    }

    if api_key:
        session_data["encrypted_api_key"] = encrypt_api_key(api_key)

    user_sessions[session_id] = session_data
    return session_id


@router.post("/validate-key", response_model=ApiKeyValidationResponse)
async def validate_api_key(
    request: ApiKeyValidationRequest, http_request: Request, response: Response
):
    """Validate an OpenRouter API key."""
    try:
        validation_result = await validate_openrouter_api_key(request.api_key)

        if validation_result["valid"] and not request.validate_only:
            # Store the API key securely in session
            session_id = create_session(validation_result["user"], request.api_key)

            # Set secure session cookie
            response.set_cookie(
                key="openrouter_session_id",
                value=session_id,
                httponly=True,
                secure=True,  # Use HTTPS in production
                samesite="lax",
                max_age=86400,  # 24 hours
            )

        return ApiKeyValidationResponse(
            valid=validation_result["valid"],
            user=validation_result.get("user"),
            error=validation_result.get("error"),
        )

    except Exception as e:
        logger.error(f"API key validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key validation failed",
        ) from e


@router.post("/oauth/initiate", response_model=OAuthInitiateResponse)
async def initiate_oauth():
    """Initiate OAuth flow with OpenRouter."""
    if not OPENROUTER_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OAuth not configured. Please set OPENROUTER_CLIENT_ID.",
        )

    try:
        # Generate PKCE parameters
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        state = secrets.token_urlsafe(32)

        # Store OAuth state
        oauth_states[state] = {
            "code_verifier": code_verifier,
            "created_at": secrets.token_hex(8),  # Simplified timestamp
        }

        # Build authorization URL
        auth_params = {
            "client_id": OPENROUTER_CLIENT_ID,
            "redirect_uri": OPENROUTER_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        auth_url = f"https://openrouter.ai/oauth/authorize?{urlencode(auth_params)}"

        return OAuthInitiateResponse(
            auth_url=auth_url, code_verifier=code_verifier, state=state
        )

    except Exception as e:
        logger.error(f"OAuth initiation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth initiation failed",
        ) from e


@router.post("/oauth/callback", response_model=OAuthCallbackResponse)
async def oauth_callback(request: OAuthCallbackRequest, response: Response):
    """Handle OAuth callback from OpenRouter."""
    try:
        # Validate state
        if request.state not in oauth_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state"
            )

        stored_verifier = oauth_states[request.state]["code_verifier"]
        if stored_verifier != request.code_verifier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code verifier"
            )

        # Exchange code for token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://openrouter.ai/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": OPENROUTER_CLIENT_ID,
                    "client_secret": OPENROUTER_CLIENT_SECRET,
                    "code": request.code,
                    "redirect_uri": OPENROUTER_REDIRECT_URI,
                    "code_verifier": request.code_verifier,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )

            if token_response.status_code != 200:
                return OAuthCallbackResponse(
                    success=False, error="Token exchange failed"
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")

            # Get user info
            user_response = await client.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0,
            )

            if user_response.status_code != 200:
                return OAuthCallbackResponse(
                    success=False, error="Failed to get user info"
                )

            user_data = user_response.json()
            user_info = {
                "id": user_data.get("data", {}).get("id"),
                "email": user_data.get("data", {}).get("email"),
                "name": user_data.get("data", {}).get("label", "OpenRouter User"),
                "credits": user_data.get("data", {}).get("credit_balance", 0),
                "usage": {
                    "requests": user_data.get("data", {})
                    .get("usage", {})
                    .get("requests", 0),
                    "tokens": user_data.get("data", {})
                    .get("usage", {})
                    .get("tokens", 0),
                },
            }

            # Create session
            session_id = create_session(user_info)

            # Set secure session cookie
            response.set_cookie(
                key="openrouter_session_id",
                value=session_id,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=86400,
            )

            # Clean up OAuth state
            del oauth_states[request.state]

            return OAuthCallbackResponse(
                success=True, user=user_info, session_id=session_id
            )

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return OAuthCallbackResponse(success=False, error=str(e))


@router.get("/user-info")
async def get_user_info(request: Request):
    """Get current user information."""
    session_id = get_session_id(request)
    if not session_id or session_id not in user_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    session_data = user_sessions[session_id]
    return {"user": session_data["user"]}


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout and clear session."""
    session_id = get_session_id(request)
    if session_id and session_id in user_sessions:
        del user_sessions[session_id]

    response.delete_cookie("openrouter_session_id")
    return {"message": "Logged out successfully"}


@router.get("/status")
async def auth_status(request: Request):
    """Get authentication status."""
    session_id = get_session_id(request)
    if not session_id or session_id not in user_sessions:
        return {"authenticated": False, "auth_method": None, "user": None}

    session_data = user_sessions[session_id]
    return {
        "authenticated": True,
        "auth_method": session_data["auth_method"],
        "user": session_data["user"],
    }
