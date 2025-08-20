# Ensure unittest.mock.Mock supports magic methods in tests that expect context manager behavior
import unittest.mock as _um
_um.Mock = _um.MagicMock  # type: ignore[attr-defined]

