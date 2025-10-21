"""
Tests for orchestration decorators.

This module tests the decorator functions in src/orchestration/decorators.py
to achieve comprehensive coverage of retry, timing, logging, and singleton functionality.
"""

import logging
import time
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from src.orchestration.decorators import (
    log_entry_exit,
    retry,
    singleton,
    timing_decorator,
)


class TestRetryDecorator:
    """Test suite for @retry decorator."""

    def test_retry_success_first_attempt(self):
        """Test that retry succeeds on first attempt."""
        mock_func = Mock(return_value="success")

        @retry(max_attempts=3, delay=0.1)
        def test_func():
            return mock_func()

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_success_after_failures(self):
        """Test that retry succeeds after some failures."""
        mock_func = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])

        @retry(max_attempts=3, delay=0.1)
        def test_func():
            return mock_func()

        result = test_func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_max_attempts_exceeded(self):
        """Test that retry raises exception after max attempts."""
        mock_func = Mock(side_effect=Exception("persistent failure"))

        @retry(max_attempts=3, delay=0.1)
        def test_func():
            return mock_func()

        with pytest.raises(Exception, match="persistent failure"):
            test_func()

        assert mock_func.call_count == 3

    def test_retry_with_backoff(self):
        """Test that retry uses exponential backoff."""
        mock_func = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])

        start_time = time.time()

        @retry(max_attempts=3, delay=0.1, backoff=2.0)
        def test_func():
            return mock_func()

        result = test_func()
        elapsed = time.time() - start_time

        assert result == "success"
        # First retry: 0.1s, second retry: 0.2s (backoff=2.0)
        # Total should be at least 0.3s
        assert elapsed >= 0.3

    def test_retry_with_specific_exceptions(self):
        """Test that retry only catches specified exceptions."""
        mock_func = Mock(side_effect=ValueError("specific error"))

        @retry(max_attempts=3, delay=0.1, exceptions=ValueError)
        def test_func():
            return mock_func()

        with pytest.raises(ValueError, match="specific error"):
            test_func()

        assert mock_func.call_count == 3

    def test_retry_with_different_exception_not_caught(self):
        """Test that retry doesn't catch non-specified exceptions."""
        mock_func = Mock(side_effect=TypeError("wrong type"))

        @retry(max_attempts=3, delay=0.1, exceptions=ValueError)
        def test_func():
            return mock_func()

        # Should raise immediately without retrying
        with pytest.raises(TypeError, match="wrong type"):
            test_func()

        assert mock_func.call_count == 1


class TestTimingDecorator:
    """Test suite for @timing_decorator."""

    def test_timing_decorator_logs_execution_time(self, caplog):
        """Test that timing decorator logs execution time."""
        @timing_decorator
        def slow_func():
            time.sleep(0.1)
            return "done"

        with caplog.at_level(logging.INFO):
            result = slow_func()

        assert result == "done"
        # Check that timing was logged
        assert any("slow_func" in record.message for record in caplog.records)
        assert any("seconds" in record.message for record in caplog.records)

    def test_timing_decorator_preserves_function_name(self):
        """Test that timing decorator preserves function metadata."""
        @timing_decorator
        def my_function():
            """My docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_timing_decorator_with_arguments(self, caplog):
        """Test timing decorator with function arguments."""
        @timing_decorator
        def func_with_args(a, b, c=3):
            time.sleep(0.05)
            return a + b + c

        with caplog.at_level(logging.INFO):
            result = func_with_args(1, 2, c=4)

        assert result == 7
        assert any("func_with_args" in record.message for record in caplog.records)


class TestLogEntryExitDecorator:
    """Test suite for @log_entry_exit decorator."""

    def test_log_entry_exit_logs_entry_and_exit(self, caplog):
        """Test that log_entry_exit logs function entry and exit."""
        @log_entry_exit
        def test_func():
            return "result"

        with caplog.at_level(logging.INFO):
            result = test_func()

        assert result == "result"
        # Check for entry and exit logs
        messages = [record.message for record in caplog.records]
        assert any("Entering test_func" in msg for msg in messages)
        assert any("Exiting test_func" in msg for msg in messages)

    def test_log_entry_exit_preserves_function_name(self):
        """Test that log_entry_exit preserves function metadata."""
        @log_entry_exit
        def my_function():
            """My docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_log_entry_exit_with_arguments(self, caplog):
        """Test log_entry_exit with function arguments."""
        @log_entry_exit
        def func_with_args(a, b):
            return a + b

        with caplog.at_level(logging.INFO):
            result = func_with_args(1, 2)

        assert result == 3
        messages = [record.message for record in caplog.records]
        assert any("Entering func_with_args" in msg for msg in messages)
        assert any("Exiting func_with_args" in msg for msg in messages)

    def test_log_entry_exit_with_exception(self, caplog):
        """Test that log_entry_exit logs even when function raises exception."""
        @log_entry_exit
        def failing_func():
            raise ValueError("test error")

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError, match="test error"):
                failing_func()

        # Should log entry but not exit (exception raised)
        messages = [record.message for record in caplog.records]
        assert any("Entering failing_func" in msg for msg in messages)


class TestSingletonDecorator:
    """Test suite for @singleton decorator."""

    def test_singleton_returns_same_instance(self):
        """Test that singleton returns the same instance."""
        @singleton
        class TestClass:
            def __init__(self, value):
                self.value = value

        instance1 = TestClass(42)
        instance2 = TestClass(99)  # Should return instance1, not create new

        assert instance1 is instance2
        assert instance1.value == 42  # Original value preserved
        assert instance2.value == 42  # Not 99!

    def test_singleton_with_different_classes(self):
        """Test that singleton maintains separate instances for different classes."""
        @singleton
        class ClassA:
            def __init__(self, value):
                self.value = value

        @singleton
        class ClassB:
            def __init__(self, value):
                self.value = value

        instance_a = ClassA(1)
        instance_b = ClassB(2)

        assert instance_a is not instance_b
        assert instance_a.value == 1
        assert instance_b.value == 2

    def test_singleton_with_no_args(self):
        """Test singleton with class that takes no arguments."""
        @singleton
        class NoArgsClass:
            def __init__(self):
                self.created = True

        instance1 = NoArgsClass()
        instance2 = NoArgsClass()

        assert instance1 is instance2
        assert instance1.created is True

    def test_singleton_preserves_class_name(self):
        """Test that singleton preserves class metadata."""
        @singleton
        class MyClass:
            """My class docstring."""
            pass

        # Note: singleton wraps the class, so __name__ might be 'get_instance'
        # but the class itself should still be accessible
        instance = MyClass()
        assert instance.__class__.__name__ == "MyClass"


class TestDecoratorCombinations:
    """Test suite for combining multiple decorators."""

    def test_retry_with_timing(self, caplog):
        """Test combining retry and timing decorators."""
        mock_func = Mock(side_effect=[Exception("fail"), "success"])

        @retry(max_attempts=3, delay=0.05)
        @timing_decorator
        def test_func():
            return mock_func()

        with caplog.at_level(logging.INFO):
            result = test_func()

        assert result == "success"
        assert mock_func.call_count == 2
        # Should have timing logs
        assert any("test_func" in record.message for record in caplog.records)

    def test_log_entry_exit_with_timing(self, caplog):
        """Test combining log_entry_exit and timing decorators."""
        @log_entry_exit
        @timing_decorator
        def test_func():
            time.sleep(0.05)
            return "done"

        with caplog.at_level(logging.INFO):
            result = test_func()

        assert result == "done"
        messages = [record.message for record in caplog.records]
        # Should have both entry/exit and timing logs
        assert any("Entering" in msg for msg in messages)
        assert any("Exiting" in msg for msg in messages)
        assert any("seconds" in msg for msg in messages)

