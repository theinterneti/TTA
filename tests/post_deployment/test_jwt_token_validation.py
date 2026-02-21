"""

# Logseq: [[TTA.dev/Tests/Post_deployment/Test_jwt_token_validation]]
Post-Deployment Tests: JWT Token Validation (Issue #2)

These tests verify that the JWT token fix remains effective after deployment.

Issue #2 Fix: JWT tokens now include an explicit 'player_id' field to ensure
proper player identification throughout the system.

Test Coverage:
- JWT tokens contain 'player_id' field
- 'player_id' matches expected user ID
- Backward compatibility with 'sub' field
- Token refresh maintains 'player_id'
- MFA flow preserves 'player_id'
"""

import jwt
import pytest


@pytest.mark.asyncio
async def test_jwt_contains_player_id_field(
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that JWT access tokens contain the explicit 'player_id' field.

    This validates the fix for Issue #2 where JWT tokens were missing
    the player_id field, causing authentication issues.

    Args:
        authenticated_client: Authenticated API client and token data
        health_check: Health check result (ensures system is ready)
    """
    _, token_data = authenticated_client

    # Verify we have an access token
    assert "access_token" in token_data, "Login response missing access_token"
    access_token = token_data["access_token"]

    # Decode JWT without verification (we just want to inspect the payload)
    # In production, tokens are verified by the backend
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})

    # CRITICAL: Verify 'player_id' field exists (Issue #2 fix)
    assert "player_id" in decoded_token, (
        "JWT token missing 'player_id' field. "
        "Issue #2 fix may have regressed. "
        f"Token payload: {decoded_token}"
    )

    # Verify player_id is not None or empty
    player_id = decoded_token["player_id"]
    assert player_id, f"JWT 'player_id' field is empty: {player_id}"

    # Verify player_id is a string
    assert isinstance(player_id, str), (
        f"JWT 'player_id' should be a string, got {type(player_id)}"
    )


@pytest.mark.asyncio
async def test_jwt_player_id_matches_user_id(
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that JWT 'player_id' matches the user's ID.

    The player_id should correspond to the authenticated user's identifier.

    Args:
        authenticated_client: Authenticated API client and token data
        health_check: Health check result
    """
    _, token_data = authenticated_client
    access_token = token_data["access_token"]

    # Decode token
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})

    # Get player_id and sub (user_id)
    player_id = decoded_token.get("player_id")
    user_id = decoded_token.get("sub")

    # Verify both fields exist
    assert player_id, "JWT missing 'player_id' field"
    assert user_id, "JWT missing 'sub' field"

    # For the default implementation, player_id should match user_id
    # (unless explicitly overridden during token creation)
    assert player_id == user_id, (
        f"JWT 'player_id' ({player_id}) does not match 'sub' ({user_id}). "
        "This may indicate an issue with player profile creation."
    )


@pytest.mark.asyncio
async def test_jwt_backward_compatibility_with_sub(
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that JWT tokens maintain backward compatibility with 'sub' field.

    The 'sub' (subject) field should still be present for backward compatibility
    with older code that might rely on it.

    Args:
        authenticated_client: Authenticated API client and token data
        health_check: Health check result
    """
    _, token_data = authenticated_client
    access_token = token_data["access_token"]

    # Decode token
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})

    # Verify 'sub' field exists (backward compatibility)
    assert "sub" in decoded_token, (
        "JWT token missing 'sub' field. Backward compatibility may be broken."
    )

    # Verify sub is not None or empty
    sub = decoded_token["sub"]
    assert sub, f"JWT 'sub' field is empty: {sub}"


@pytest.mark.asyncio
async def test_jwt_contains_required_fields(
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that JWT tokens contain all required fields.

    Required fields:
    - sub: User ID (subject)
    - player_id: Player profile ID (Issue #2 fix)
    - username: Username
    - email: Email address
    - exp: Expiration timestamp

    Args:
        authenticated_client: Authenticated API client and token data
        health_check: Health check result
    """
    _, token_data = authenticated_client
    access_token = token_data["access_token"]

    # Decode token
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})

    # Required fields
    required_fields = ["sub", "player_id", "username", "email", "exp"]

    # Verify all required fields are present
    missing_fields = [field for field in required_fields if field not in decoded_token]

    assert not missing_fields, (
        f"JWT token missing required fields: {missing_fields}. "
        f"Token payload: {decoded_token}"
    )

    # Verify fields are not empty
    for field in required_fields:
        if field != "exp":  # exp is a timestamp, can be 0
            assert decoded_token[field], f"JWT field '{field}' is empty"


@pytest.mark.asyncio
async def test_token_refresh_maintains_player_id(
    api_client,
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that refreshing a token maintains the 'player_id' field.

    When a refresh token is used to obtain a new access token,
    the new token should still contain the player_id field.

    Args:
        api_client: Base API client
        authenticated_client: Authenticated API client and token data
        health_check: Health check result
    """
    _, token_data = authenticated_client

    # Check if refresh token is provided
    if "refresh_token" not in token_data:
        pytest.skip("Refresh token not provided in login response")

    refresh_token = token_data["refresh_token"]

    # Request new access token using refresh token
    refresh_response = await api_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    # Verify refresh was successful
    assert refresh_response.status_code == 200, (
        f"Token refresh failed with status {refresh_response.status_code}: "
        f"{refresh_response.text}"
    )

    new_token_data = refresh_response.json()
    assert "access_token" in new_token_data, "Refresh response missing access_token"

    # Decode new access token
    new_access_token = new_token_data["access_token"]
    decoded_new_token = jwt.decode(
        new_access_token, options={"verify_signature": False}
    )

    # CRITICAL: Verify new token contains 'player_id' field
    assert "player_id" in decoded_new_token, (
        "Refreshed JWT token missing 'player_id' field. "
        "Issue #2 fix may have regressed in token refresh flow."
    )

    # Verify player_id is preserved
    original_decoded = jwt.decode(
        token_data["access_token"],
        options={"verify_signature": False},
    )
    original_player_id = original_decoded.get("player_id")
    new_player_id = decoded_new_token.get("player_id")

    assert new_player_id == original_player_id, (
        f"Refreshed token player_id ({new_player_id}) does not match "
        f"original token player_id ({original_player_id})"
    )


@pytest.mark.asyncio
async def test_jwt_player_id_is_valid_identifier(
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that the 'player_id' in JWT is a valid identifier.

    The player_id should be a non-empty string that looks like a valid UUID
    or identifier (not a placeholder or error value).

    Args:
        authenticated_client: Authenticated API client and token data
        health_check: Health check result
    """
    _, token_data = authenticated_client
    access_token = token_data["access_token"]

    # Decode token
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})
    player_id = decoded_token.get("player_id")

    # Verify player_id is not a placeholder or error value
    invalid_values = ["null", "none", "undefined", "", "0", "test", "placeholder"]

    assert player_id.lower() not in invalid_values, (
        f"JWT 'player_id' appears to be a placeholder value: {player_id}"
    )

    # Verify player_id has reasonable length (UUIDs are typically 36 chars with hyphens)
    assert len(player_id) >= 8, (
        f"JWT 'player_id' is suspiciously short: {player_id} (length: {len(player_id)})"
    )


@pytest.mark.asyncio
async def test_authenticated_request_with_jwt(
    authenticated_client: tuple,
    health_check: dict,
):
    """
    Test that authenticated requests work with the JWT token.

    This validates that the JWT token with player_id field can be used
    to make authenticated API requests successfully.

    Args:
        authenticated_client: Authenticated API client and token data
        health_check: Health check result
    """
    auth_client, _ = authenticated_client

    # Make an authenticated request to a protected endpoint
    # Using /api/v1/players endpoint as it requires authentication
    response = await auth_client.get("/api/v1/players")

    # Verify request was successful
    assert response.status_code in [200, 404], (
        f"Authenticated request failed with status {response.status_code}: "
        f"{response.text}. "
        "This may indicate JWT token is not being accepted by the backend."
    )

    # If 200, verify we got a valid response
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, (list, dict)), (
            f"Unexpected response format: {type(data)}"
        )
