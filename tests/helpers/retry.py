"""
Retry helper utilities for tests.

Provides a :func:`wait_until` coroutine that replaces hard-coded
``time.sleep()`` calls with a polling loop powered by *tenacity*.
"""

from __future__ import annotations

from typing import Any, Callable

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)


def retry_with_backoff(
    *,
    max_attempts: int = 5,
    max_delay: float = 10.0,
    retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
):
    """Decorator: retry a *sync* or *async* function with exponential back-off.

    Usage::

        @retry_with_backoff(max_attempts=3)
        def flaky_check(): ...
    """
    return retry(
        retry=retry_if_exception_type(retry_on),
        stop=stop_after_attempt(max_attempts) | stop_after_delay(max_delay),
        wait=wait_exponential(multiplier=0.1, max=2),
        reraise=True,
    )


async def wait_until(
    predicate: Callable[[], Any],
    *,
    timeout: float = 5.0,
    interval: float = 0.1,
) -> Any:
    """Poll *predicate* until it returns a truthy value or *timeout* expires.

    This is a direct replacement for ``time.sleep(N)`` patterns where the
    test is waiting for some asynchronous side-effect.

    Usage::

        value = await wait_until(lambda: cache.get("key"), timeout=3.0)
    """
    import asyncio

    deadline = asyncio.get_running_loop().time() + timeout
    last_result = None
    while asyncio.get_running_loop().time() < deadline:
        last_result = predicate()
        if last_result:
            return last_result
        await asyncio.sleep(interval)
    return last_result
