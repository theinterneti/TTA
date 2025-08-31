"""
Authentication and authorization utilities for the Player Experience API.

This module provides JWT token handling, password hashing, and authentication
decorators for securing API endpoints.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..models.player import PlayerProfile
from .config import settings

# Configuration - Use settings from config module
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class AuthorizationError(Exception):
    """Raised when authorization fails."""

    pass


class Token(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""

    player_id: str | None = None
    username: str | None = None
    email: str | None = None
    exp: datetime | None = None


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: The plain text password

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: The data to encode in the token

    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token to verify

    Returns:
        TokenData: The decoded token data

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        player_id: str = payload.get("sub")
        username: str = payload.get("username")
        email: str = payload.get("email")
        exp_timestamp: int = payload.get("exp")

        if player_id is None:
            raise AuthenticationError("Invalid token: missing player ID")

        exp = (
            datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_timestamp
            else None
        )

        return TokenData(player_id=player_id, username=username, email=email, exp=exp)
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def create_tokens_for_player(player: PlayerProfile) -> Token:
    """
    Create access and refresh tokens for a player.

    Args:
        player: The player profile

    Returns:
        Token: The token response with access and refresh tokens
    """
    token_data = {
        "sub": player.player_id,
        "username": player.username,
        "email": player.email,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
    )


async def get_current_player(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Get the current authenticated player from the JWT token.

    Args:
        credentials: The HTTP authorization credentials

    Returns:
        TokenData: The current player's token data

    Raises:
        HTTPException: If authentication fails
    """
    try:
        token_data = verify_token(credentials.credentials)

        # Check if token is expired
        if token_data.exp and datetime.now(timezone.utc) > token_data.exp:
            raise AuthenticationError("Token has expired")

        return token_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_player(
    current_player: TokenData = Depends(get_current_player),
) -> TokenData:
    """
    Get the current active player (additional validation can be added here).

    Args:
        current_player: The current player from token

    Returns:
        TokenData: The current active player's token data
    """
    # Additional validation can be added here, such as:
    # - Check if player is still active in database
    # - Check if player has required permissions
    # - Rate limiting per player

    return current_player


def require_player_access(player_id: str):
    """
    Dependency to require access to a specific player's resources.

    Args:
        player_id: The player ID to check access for

    Returns:
        Callable: A dependency function that validates player access
    """

    async def check_player_access(
        current_player: TokenData = Depends(get_current_active_player),
    ) -> TokenData:
        if current_player.player_id != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources",
            )
        return current_player

    return check_player_access


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    async def authenticate_player(username: str, password: str) -> PlayerProfile | None:
        """
        Authenticate a player with username and password.

        Args:
            username: The player's username
            password: The player's password

        Returns:
            Optional[PlayerProfile]: The player profile if authentication succeeds, None otherwise

        Note:
            This is a placeholder implementation. In a real application, this would
            query the database to verify credentials.
        """
        # TODO: Implement actual player authentication with database
        # This is a placeholder implementation

        # For now, we'll create a mock authentication
        # In production, this should:
        # 1. Query the database for the player by username
        # 2. Verify the password hash
        # 3. Return the player profile if valid

        return None

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Token:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            Token: New access and refresh tokens

        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            # Verify this is a refresh token
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")

            player_id = payload.get("sub")
            username = payload.get("username")
            email = payload.get("email")

            if not player_id:
                raise AuthenticationError("Invalid refresh token")

            # Create new tokens
            token_data = {
                "sub": player_id,
                "username": username,
                "email": email,
            }

            access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)

            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except JWTError as e:
            raise AuthenticationError(f"Invalid refresh token: {str(e)}")
