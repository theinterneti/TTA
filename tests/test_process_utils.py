
import pytest

from src.common.process_utils import ProcessError, run


def test_run_success_echo():
    # Use a simple command available in most environments
    result = run(["echo", "hello"], timeout=5)
    assert result.returncode == 0
    assert "hello" in (result.stdout or "")


def test_run_timeout():
    # Use a command that sleeps; timeout shorter than sleep
    with pytest.raises(ProcessError):
        run(["sleep", "2"], timeout=0.5)


def test_run_nonzero_no_check():
    # false exits with non-zero; should not raise when check=False (default)
    result = run(["bash", "-lc", "exit 3"], timeout=5)
    assert result.returncode == 3


def test_run_nonzero_with_check():
    with pytest.raises(ProcessError) as exc:
        run(["bash", "-lc", "exit 2"], timeout=5, check=True)
    assert "rc=2" in str(exc.value) or "Command failed" in str(exc.value)


def test_no_shell_injection():
    # Ensure passing a string raises (we require List[str])
    with pytest.raises(ValueError):
        run("echo hello")  # type: ignore[arg-type]
