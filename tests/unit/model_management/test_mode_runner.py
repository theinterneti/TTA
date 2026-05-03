"""Unit tests for ModeRunner."""

from __future__ import annotations

from src.components.model_management.mode_runner import ModeRunner


def test_call_with_meta_is_coroutine():
    """ModeRunner.call_with_meta() must exist and be an async method."""
    import inspect
    runner = ModeRunner()
    assert inspect.iscoroutinefunction(runner.call_with_meta)


def test_call_with_meta_return_type():
    """call_with_meta() must return a 3-tuple of (str, str, str).

    RED: return type annotation is present but not yet verified at runtime.
    We use get_type_hints to confirm the declared return type is correct.
    """
    import inspect
    hints = inspect.get_annotations(ModeRunner.call_with_meta, eval_str=True)
    ret = hints.get("return")
    assert ret is not None, "call_with_meta must have a return type annotation"
    # tuple[str, str, str] — origin is tuple, args are (str, str, str)
    import typing
    origin = getattr(ret, "__origin__", None)
    args = getattr(ret, "__args__", ())
    assert origin is tuple, f"Return type origin must be tuple, got {origin}"
    assert args == (str, str, str), (
        f"Return type must be tuple[str, str, str], got tuple[{args}]"
    )
