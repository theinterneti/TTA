"""Tests for the retry helpers and quarantine marker."""

import pytest

from tests.helpers.retry import retry_with_backoff, wait_until

pytestmark = pytest.mark.unit


class TestRetryWithBackoff:
    def test_succeeds_without_retry(self):
        """retry_with_backoff returns result immediately when function succeeds on first call."""
        call_count = 0

        @retry_with_backoff(max_attempts=3)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        assert succeed() == "ok"
        assert call_count == 1

    def test_retries_then_succeeds(self):
        """retry_with_backoff retries up to max_attempts and returns result when function eventually succeeds."""
        call_count = 0

        @retry_with_backoff(max_attempts=3)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        assert flaky() == "ok"
        assert call_count == 3

    def test_exhausts_retries(self):
        """retry_with_backoff re-raises the last exception after all attempts are exhausted."""
        @retry_with_backoff(max_attempts=2, max_delay=1.0)
        def always_fail():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError, match="fail"):
            always_fail()


class TestWaitUntil:
    async def test_returns_truthy_value(self):
        """wait_until returns True when condition becomes truthy within timeout."""
        counter = {"n": 0}

        def check():
            counter["n"] += 1
            return counter["n"] >= 3

        result = await wait_until(check, timeout=2.0, interval=0.01)
        assert result is True

    async def test_returns_last_falsy_on_timeout(self):
        """wait_until returns False when condition never becomes truthy before timeout."""
        result = await wait_until(lambda: False, timeout=0.1, interval=0.02)
        assert result is False


class TestQuarantineMarker:
    """Verify that the quarantine marker is registered and usable."""

    @pytest.mark.quarantine
    def test_quarantine_marker_is_registered(self):
        """pytest.mark.quarantine is registered and accepted under --strict-markers without warnings."""
        # This test simply proves the marker doesn't trigger a warning
        # under --strict-markers.  The actual xfail behaviour is
        # applied only when CI=true (see tests/conftest.py).
        pass

    @pytest.mark.flaky
    def test_flaky_marker_is_registered(self):
        """pytest.mark.flaky is registered and accepted under --strict-markers without warnings."""
        pass
