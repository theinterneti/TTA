"""Tests for calculator operations."""

import pytest

from src.test_components.calculator import add, divide, multiply, subtract


class TestAddition:
    """Tests for addition operation."""

    def test_add_positive_numbers(self):
        """Test adding two positive numbers."""
        assert add(2, 3) == 5

    def test_add_negative_numbers(self):
        """Test adding two negative numbers."""
        assert add(-2, -3) == -5

    def test_add_with_zero(self):
        """Test adding with zero."""
        assert add(5, 0) == 5
        assert add(0, 5) == 5


class TestSubtraction:
    """Tests for subtraction operation."""

    def test_subtract_positive_result(self):
        """Test subtraction with positive result."""
        assert subtract(5, 3) == 2

    def test_subtract_negative_result(self):
        """Test subtraction with negative result."""
        assert subtract(3, 5) == -2

    def test_subtract_zero_result(self):
        """Test subtraction resulting in zero."""
        assert subtract(5, 5) == 0


class TestMultiplication:
    """Tests for multiplication operation."""

    def test_multiply_positive_numbers(self):
        """Test multiplying two positive numbers."""
        assert multiply(2, 3) == 6

    def test_multiply_negative_numbers(self):
        """Test multiplying two negative numbers."""
        assert multiply(-2, -3) == 6

    def test_multiply_with_zero(self):
        """Test multiplying with zero."""
        assert multiply(5, 0) == 0
        assert multiply(0, 5) == 0


class TestDivision:
    """Tests for division operation."""

    def test_divide_normal(self):
        """Test normal division."""
        assert divide(6, 2) == 3.0

    def test_divide_negative_numbers(self):
        """Test division with negative numbers."""
        assert divide(-6, 2) == -3.0
        assert divide(6, -2) == -3.0

    def test_divide_by_zero(self):
        """Test division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)
