"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Tools/Cursor]]
Secure cursor system for pagination (Phase 3 Tool Optimization).

Provides tamper-proof pagination cursors using HMAC-SHA256 signing:
- Cursor encoding/decoding with Base64
- HMAC-SHA256 signature verification
- Timestamp validation (1-hour TTL)
- Secret key management
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import secrets
import time
from typing import Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class CursorData(BaseModel):
    """Data structure for pagination cursor."""

    offset: int = Field(..., ge=0, description="Offset in result set")
    timestamp: float = Field(default_factory=time.time, description="Cursor creation timestamp")
    filters: dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    sort_key: str | None = Field(default=None, description="Sort key for ordering")

    @field_validator("offset")
    @classmethod
    def _validate_offset(cls, v: int) -> int:
        """Validate offset is non-negative."""
        if v < 0:
            raise ValueError("offset must be non-negative")
        return v


class CursorManager:
    """
    Manages secure pagination cursors with HMAC-SHA256 signing.

    Features:
    - Tamper-proof cursors using HMAC-SHA256
    - Base64 encoding for transport
    - Timestamp validation (default 1-hour TTL)
    - Secure secret key management

    Example:
        >>> manager = CursorManager()
        >>> cursor_data = CursorData(offset=50, filters={"status": "active"})
        >>> cursor = manager.encode_cursor(cursor_data)
        >>> decoded = manager.decode_cursor(cursor)
        >>> decoded.offset
        50
    """

    def __init__(
        self,
        secret_key: str | None = None,
        ttl_seconds: int = 3600,
    ):
        """
        Initialize cursor manager.

        Args:
            secret_key: Secret key for HMAC signing. If None, uses TTA_CURSOR_SECRET_KEY
                       environment variable or generates a secure random key.
            ttl_seconds: Time-to-live for cursors in seconds (default: 3600 = 1 hour)
        """
        self.ttl_seconds = ttl_seconds

        # Get or generate secret key
        if secret_key is None:
            secret_key = os.getenv("TTA_CURSOR_SECRET_KEY")
            if secret_key is None:
                # Generate secure random key (32 bytes = 256 bits)
                secret_key = base64.b64encode(secrets.token_bytes(32)).decode("utf-8")
                logger.warning(
                    "No TTA_CURSOR_SECRET_KEY found. Generated random key. "
                    "Set TTA_CURSOR_SECRET_KEY environment variable for production."
                )

        self.secret_key = secret_key.encode("utf-8")

    def encode_cursor(self, cursor_data: CursorData) -> str:
        """
        Encode cursor data with HMAC-SHA256 signature.

        Process:
        1. Serialize cursor data to JSON
        2. Encode JSON as Base64
        3. Generate HMAC-SHA256 signature
        4. Return "base64_data.signature"

        Args:
            cursor_data: Cursor data to encode

        Returns:
            Signed cursor string in format "base64_data.signature"

        Example:
            >>> manager = CursorManager()
            >>> data = CursorData(offset=100)
            >>> cursor = manager.encode_cursor(data)
            >>> "." in cursor
            True
        """
        # Serialize to JSON
        json_data = cursor_data.model_dump_json()

        # Encode as Base64
        base64_data = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.secret_key, base64_data.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Return signed cursor
        return f"{base64_data}.{signature}"

    def decode_cursor(self, cursor: str) -> CursorData:
        """
        Decode and validate signed cursor.

        Process:
        1. Split cursor into base64_data and signature
        2. Verify HMAC-SHA256 signature
        3. Decode Base64 to JSON
        4. Validate timestamp (reject if expired)
        5. Deserialize to CursorData

        Args:
            cursor: Signed cursor string

        Returns:
            Decoded cursor data

        Raises:
            ValueError: If cursor is invalid, tampered, or expired

        Example:
            >>> manager = CursorManager()
            >>> data = CursorData(offset=100)
            >>> cursor = manager.encode_cursor(data)
            >>> decoded = manager.decode_cursor(cursor)
            >>> decoded.offset
            100
        """
        # Split cursor
        if "." not in cursor:
            raise ValueError("Invalid cursor format: missing signature separator")

        parts = cursor.split(".")
        if len(parts) != 2:
            raise ValueError("Invalid cursor format: must have exactly one '.' separator")

        base64_data, provided_signature = parts

        # Verify signature
        expected_signature = hmac.new(
            self.secret_key, base64_data.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(provided_signature, expected_signature):
            logger.warning("Cursor signature verification failed - possible tampering detected")
            raise ValueError("Invalid cursor: signature verification failed")

        # Decode Base64
        try:
            json_data = base64.b64decode(base64_data).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Invalid cursor: Base64 decoding failed - {e}") from e

        # Deserialize to CursorData
        try:
            cursor_data = CursorData.model_validate_json(json_data)
        except Exception as e:
            raise ValueError(f"Invalid cursor: JSON deserialization failed - {e}") from e

        # Validate timestamp
        age_seconds = time.time() - cursor_data.timestamp
        if age_seconds > self.ttl_seconds:
            logger.warning(f"Cursor expired: age={age_seconds:.1f}s, ttl={self.ttl_seconds}s")
            raise ValueError(
                f"Cursor expired: age={age_seconds:.1f}s exceeds TTL of {self.ttl_seconds}s"
            )

        if age_seconds < 0:
            logger.warning("Cursor timestamp is in the future - possible clock skew")
            raise ValueError("Invalid cursor: timestamp is in the future")

        return cursor_data

    def is_valid_cursor(self, cursor: str) -> bool:
        """
        Check if cursor is valid without raising exceptions.

        Args:
            cursor: Cursor string to validate

        Returns:
            True if cursor is valid, False otherwise

        Example:
            >>> manager = CursorManager()
            >>> data = CursorData(offset=100)
            >>> cursor = manager.encode_cursor(data)
            >>> manager.is_valid_cursor(cursor)
            True
            >>> manager.is_valid_cursor("invalid")
            False
        """
        try:
            self.decode_cursor(cursor)
            return True
        except ValueError:
            return False

    def create_cursor(
        self,
        offset: int,
        filters: dict[str, Any] | None = None,
        sort_key: str | None = None,
    ) -> str:
        """
        Create a new cursor with the given parameters.

        Convenience method that creates CursorData and encodes it.

        Args:
            offset: Offset in result set
            filters: Optional filters to apply
            sort_key: Optional sort key

        Returns:
            Encoded cursor string

        Example:
            >>> manager = CursorManager()
            >>> cursor = manager.create_cursor(offset=50, filters={"status": "active"})
            >>> decoded = manager.decode_cursor(cursor)
            >>> decoded.offset
            50
        """
        cursor_data = CursorData(offset=offset, filters=filters or {}, sort_key=sort_key)
        return self.encode_cursor(cursor_data)


# Global cursor manager instance (can be overridden for testing)
_cursor_manager: CursorManager | None = None


def get_cursor_manager() -> CursorManager:
    """
    Get global cursor manager instance.

    Creates instance on first call with default settings.
    Can be overridden for testing by setting module-level _cursor_manager.

    Returns:
        Global CursorManager instance

    Example:
        >>> manager = get_cursor_manager()
        >>> cursor = manager.create_cursor(offset=100)
    """
    global _cursor_manager
    if _cursor_manager is None:
        _cursor_manager = CursorManager()
    return _cursor_manager


def set_cursor_manager(manager: CursorManager) -> None:
    """
    Set global cursor manager instance (for testing).

    Args:
        manager: CursorManager instance to use globally

    Example:
        >>> test_manager = CursorManager(secret_key="test-key", ttl_seconds=60)
        >>> set_cursor_manager(test_manager)
    """
    global _cursor_manager
    _cursor_manager = manager
