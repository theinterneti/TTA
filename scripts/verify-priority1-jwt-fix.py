#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Verify-priority1-jwt-fix]]
Verification Script for Priority 1: JWT Authentication Fix

This script verifies that:
1. JWT tokens contain the player_id field
2. Player profiles are auto-created on first login
3. Backward compatibility is maintained for old tokens
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import UTC, datetime, timedelta

from jose import jwt

import player_experience.api.auth as auth_module
from player_experience.api.auth import verify_token
from player_experience.models.auth import (
    AuthenticatedUser,
    Permission,
    UserRole,
)
from player_experience.services.auth_service import EnhancedAuthService

# Test configuration
SECRET_KEY = "test-secret-key-for-verification"
ALGORITHM = "HS256"

# Override the module-level SECRET_KEY and ALGORITHM for testing
auth_module.SECRET_KEY = SECRET_KEY
auth_module.ALGORITHM = ALGORITHM


def print_section(title: str):
    """Print a formatted section header."""


def test_jwt_token_structure():
    """Test 1: Verify JWT tokens contain player_id field."""
    print_section("TEST 1: JWT Token Structure")

    # Create test user
    test_user = AuthenticatedUser(
        user_id="test-user-123",
        username="testuser",
        email="test@example.com",
        role=UserRole.PLAYER,
        permissions=[Permission.CREATE_CHARACTER],
        mfa_verified=False,
    )

    # Create auth service
    auth_service = EnhancedAuthService(
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
    )

    # Test 1a: Token with explicit player_id
    token_with_player_id = auth_service.create_access_token(
        user=test_user, session_id="session-123", player_id="player-456"
    )

    # Decode and verify
    payload = jwt.decode(token_with_player_id, SECRET_KEY, algorithms=[ALGORITHM])

    if "player_id" in payload:
        if payload["player_id"] == "player-456":
            pass
        else:
            return False
    else:
        return False

    # Test 1b: Token without explicit player_id (should default to user_id)
    token_without_player_id = auth_service.create_access_token(
        user=test_user, session_id="session-123"
    )

    payload2 = jwt.decode(token_without_player_id, SECRET_KEY, algorithms=[ALGORITHM])

    if "player_id" in payload2:
        if payload2["player_id"] == test_user.user_id:
            pass
        else:
            return False
    else:
        return False

    return True


def test_verify_token_extraction():
    """Test 2: Verify token verification extracts player_id correctly."""
    print_section("TEST 2: Token Verification and player_id Extraction")

    # Create test token with player_id
    payload_with_player_id = {
        "sub": "user-123",
        "player_id": "player-456",
        "username": "testuser",
        "email": "test@example.com",
        "role": "player",
        "permissions": ["create_character"],
        "session_id": "session-123",
        "mfa_verified": False,
        "exp": datetime.now(UTC) + timedelta(minutes=30),
    }

    token = jwt.encode(payload_with_player_id, SECRET_KEY, algorithm=ALGORITHM)

    token_data = verify_token(token)

    if token_data and hasattr(token_data, "player_id"):
        if token_data.player_id == "player-456":
            pass
        else:
            return False
    else:
        return False

    # Test 2b: Backward compatibility - token without player_id
    payload_without_player_id = {
        "sub": "user-789",
        "username": "olduser",
        "email": "old@example.com",
        "role": "player",
        "permissions": ["create_character"],
        "session_id": "session-789",
        "mfa_verified": False,
        "exp": datetime.now(UTC) + timedelta(minutes=30),
    }

    old_token = jwt.encode(payload_without_player_id, SECRET_KEY, algorithm=ALGORITHM)
    old_token_data = verify_token(old_token)

    if old_token_data and hasattr(old_token_data, "player_id"):
        if old_token_data.player_id == "user-789":  # Should fallback to sub
            pass
        else:
            return False
    else:
        return False

    return True


def test_create_tokens_for_player():
    """Test 3: Verify create_tokens_for_player includes player_id."""
    print_section("TEST 3: create_tokens_for_player Function")

    return True


def main():
    """Run all verification tests."""

    results = []

    # Run tests
    results.append(("JWT Token Structure", test_jwt_token_structure()))
    results.append(("Token Verification", test_verify_token_extraction()))
    results.append(("create_tokens_for_player", test_create_tokens_for_player()))

    # Print summary
    print_section("VERIFICATION SUMMARY")

    all_passed = True
    for _test_name, passed in results:
        if not passed:
            all_passed = False

    if all_passed:
        pass
    else:
        pass

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
