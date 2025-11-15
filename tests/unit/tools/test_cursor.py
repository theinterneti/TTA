"""
Unit tests for cursor system (Phase 3 Tool Optimization).

Security-focused tests with property-based testing using Hypothesis.
Target: 100% coverage for security-critical code.
"""

import time

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.agent_orchestration.tools.cursor import (
    CursorData,
    CursorManager,
    get_cursor_manager,
    set_cursor_manager,
)


class TestCursorData:
    """Tests for CursorData model."""

    def test_valid_cursor_data(self):
        """Test creating valid cursor data."""
        data = CursorData(offset=100, filters={"status": "active"})
        assert data.offset == 100
        assert data.filters == {"status": "active"}
        assert data.sort_key is None

    def test_negative_offset_rejected(self):
        """Test negative offset is rejected."""
        with pytest.raises(ValueError):
            CursorData(offset=-1)


class TestCursorManager:
    """Tests for CursorManager."""

    def test_encode_decode_roundtrip(self):
        """Test encoding and decoding cursor."""
        manager = CursorManager(secret_key="test-secret", ttl_seconds=3600)
        data = CursorData(offset=50, filters={"status": "active"})

        cursor = manager.encode_cursor(data)
        decoded = manager.decode_cursor(cursor)

        assert decoded.offset == data.offset
        assert decoded.filters == data.filters

    def test_cursor_format(self):
        """Test cursor has correct format (base64.signature)."""
        manager = CursorManager(secret_key="test-secret")
        data = CursorData(offset=100)

        cursor = manager.encode_cursor(data)
        assert "." in cursor
        parts = cursor.split(".")
        assert len(parts) == 2

    def test_tampered_cursor_rejected(self):
        """Test tampered cursor is rejected."""
        manager = CursorManager(secret_key="test-secret")
        data = CursorData(offset=100)

        cursor = manager.encode_cursor(data)
        # Tamper with cursor by modifying the first character
        tampered = "X" + cursor[1:]

        with pytest.raises(ValueError, match="signature verification failed"):
            manager.decode_cursor(tampered)

    def test_expired_cursor_rejected(self):
        """Test expired cursor is rejected."""
        manager = CursorManager(secret_key="test-secret", ttl_seconds=1)
        data = CursorData(offset=100)

        cursor = manager.encode_cursor(data)
        time.sleep(2)  # Wait for expiration

        with pytest.raises(ValueError, match="Cursor expired"):
            manager.decode_cursor(cursor)

    def test_future_timestamp_rejected(self):
        """Test cursor with future timestamp is rejected."""
        manager = CursorManager(secret_key="test-secret")
        # Create cursor with future timestamp
        data = CursorData(offset=100, timestamp=time.time() + 3600)

        cursor = manager.encode_cursor(data)

        with pytest.raises(ValueError, match="timestamp is in the future"):
            manager.decode_cursor(cursor)

    def test_invalid_cursor_format(self):
        """Test invalid cursor formats are rejected."""
        manager = CursorManager(secret_key="test-secret")

        with pytest.raises(ValueError, match="missing signature separator"):
            manager.decode_cursor("no_dot_separator")

        with pytest.raises(ValueError, match="exactly one '.' separator"):
            manager.decode_cursor("too.many.dots")

    def test_is_valid_cursor(self):
        """Test is_valid_cursor method."""
        manager = CursorManager(secret_key="test-secret")
        data = CursorData(offset=100)

        cursor = manager.encode_cursor(data)
        assert manager.is_valid_cursor(cursor) is True
        assert manager.is_valid_cursor("invalid") is False

    def test_create_cursor_convenience(self):
        """Test create_cursor convenience method."""
        manager = CursorManager(secret_key="test-secret")

        cursor = manager.create_cursor(
            offset=50, filters={"status": "active"}, sort_key="name"
        )
        decoded = manager.decode_cursor(cursor)

        assert decoded.offset == 50
        assert decoded.filters == {"status": "active"}
        assert decoded.sort_key == "name"

    def test_different_secret_keys_incompatible(self):
        """Test cursors from different secret keys are incompatible."""
        manager1 = CursorManager(secret_key="secret1")
        manager2 = CursorManager(secret_key="secret2")

        data = CursorData(offset=100)
        cursor = manager1.encode_cursor(data)

        with pytest.raises(ValueError, match="signature verification failed"):
            manager2.decode_cursor(cursor)


class TestCursorManagerPropertyBased:
    """Property-based tests for CursorManager using Hypothesis."""

    @given(
        offset=st.integers(min_value=0, max_value=10000),
        filter_key=st.text(min_size=1, max_size=20),
        filter_value=st.text(max_size=50),
    )
    @settings(max_examples=50, deadline=1000)
    def test_encode_decode_property(self, offset, filter_key, filter_value):
        """Property: Encoding then decoding returns original data."""
        manager = CursorManager(secret_key="test-secret", ttl_seconds=3600)
        data = CursorData(offset=offset, filters={filter_key: filter_value})

        cursor = manager.encode_cursor(data)
        decoded = manager.decode_cursor(cursor)

        assert decoded.offset == data.offset
        assert decoded.filters == data.filters

    @given(offset=st.integers(min_value=0, max_value=10000))
    @settings(max_examples=50, deadline=1000)
    def test_cursor_always_has_signature(self, offset):
        """Property: All cursors have signature separator."""
        manager = CursorManager(secret_key="test-secret")
        data = CursorData(offset=offset)

        cursor = manager.encode_cursor(data)
        assert "." in cursor
        assert len(cursor.split(".")) == 2

    @given(
        offset=st.integers(min_value=0, max_value=10000),
        tamper_index=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=50, deadline=1000)
    def test_tampering_always_detected(self, offset, tamper_index):
        """Property: Any tampering is detected."""
        manager = CursorManager(secret_key="test-secret")
        data = CursorData(offset=offset)

        cursor = manager.encode_cursor(data)
        if len(cursor) > tamper_index:
            # Tamper with cursor
            cursor_list = list(cursor)
            cursor_list[tamper_index] = "X" if cursor_list[tamper_index] != "X" else "Y"
            tampered = "".join(cursor_list)

            with pytest.raises(ValueError):
                manager.decode_cursor(tampered)


class TestGlobalCursorManager:
    """Tests for global cursor manager functions."""

    def test_get_cursor_manager_singleton(self):
        """Test get_cursor_manager returns singleton."""
        manager1 = get_cursor_manager()
        manager2 = get_cursor_manager()
        assert manager1 is manager2

    def test_set_cursor_manager(self):
        """Test set_cursor_manager overrides global instance."""
        custom_manager = CursorManager(secret_key="custom-secret")
        set_cursor_manager(custom_manager)

        manager = get_cursor_manager()
        assert manager is custom_manager

        # Reset for other tests
        set_cursor_manager(CursorManager())
