"""
TTA Decorators.

This module provides decorators for the TTA orchestration system.
"""

import functools
import inspect
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variables for better type hinting
F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


def log_entry_exit(func: F) -> F:
    """
    Decorator to log function entry and exit.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Exiting {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}")
            raise

    return cast(F, wrapper)


def timing_decorator(func: F) -> F:
    """
    Decorator to measure and log the execution time of a function.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result

    return cast(F, wrapper)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: type[Exception] | list[type[Exception]] = Exception,
) -> Callable[[F], F]:
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Exception(s) to catch and retry on

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Final attempt {attempt}/{max_attempts} for {func.__name__} failed: {e}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} for {func.__name__} failed: {e}"
                    )
                    logger.info(f"Retrying in {current_delay:.2f} seconds...")

                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
            return None

        return cast(F, wrapper)

    return decorator


def validate_args(func: F) -> F:
    """
    Decorator to validate function arguments against type annotations.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """
    signature = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Combine positional and keyword arguments
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Validate each argument
        for param_name, param_value in bound_args.arguments.items():
            param = signature.parameters[param_name]
            if param.annotation != inspect.Parameter.empty:
                # Skip self and cls parameters
                if param_name in ("self", "cls"):
                    continue

                # Check if the value matches the annotation
                if (
                    not isinstance(param_value, param.annotation)
                    and param.annotation is not Any
                ):
                    raise TypeError(
                        f"Argument '{param_name}' must be of type {param.annotation.__name__}, "
                        f"got {type(param_value).__name__}"
                    )

        return func(*args, **kwargs)

    return cast(F, wrapper)


def deprecated(reason: str) -> Callable[[F], F]:
    """
    Decorator to mark functions as deprecated.

    Args:
        reason: Reason for deprecation

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.warning(f"Call to deprecated function {func.__name__}. {reason}")
            return func(*args, **kwargs)

        wrapper.__deprecated__ = True
        wrapper.__deprecated_reason__ = reason
        return cast(F, wrapper)

    return decorator


def singleton(cls: type[T]) -> type[T]:
    """
    Decorator to implement the Singleton pattern.

    Args:
        cls: The class to make a singleton

    Returns:
        The singleton class
    """
    instances: dict[type[Any], Any] = {}

    @functools.wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> T:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    get_instance._instances = instances  # Expose the instances dictionary

    return cast(type[T], get_instance)


def require_config(config_keys: list[str]) -> Callable[[F], F]:
    """
    Decorator to check if required configuration keys are present.

    Args:
        config_keys: List of required configuration keys

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Check if the object has a config attribute
            if not hasattr(self, "config"):
                raise AttributeError(
                    f"{self.__class__.__name__} has no 'config' attribute"
                )

            # Check if all required keys are present
            for key in config_keys:
                if self.config.get(key) is None:
                    raise ValueError(f"Required configuration key '{key}' is missing")

            return func(self, *args, **kwargs)

        return cast(F, wrapper)

    return decorator
