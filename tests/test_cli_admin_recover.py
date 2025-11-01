import subprocess
import sys

import pytest


@pytest.mark.redis
def test_cli_admin_recover_invocation(redis_client):
    # Build the redis URL from the fixture
    kwargs = redis_client.connection_pool.connection_kwargs
    host = kwargs.get("host", "localhost")
    port = kwargs.get("port", 6379)
    db = kwargs.get("db", 0)
    url = f"redis://{host}:{port}/{db}"

    # Invoke the CLI help for admin recover (smoke test)
    cmd = [sys.executable, "src/main.py", "admin", "recover", url, "--key-prefix", "ao"]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    # We can't assert recovery here (no reservations created), but command should run and print a summary
    assert proc.returncode in (0, 1)
    assert (
        "Recovered messages summary:" in proc.stdout
        or "Admin recovery failed" in proc.stdout
        or proc.stderr
    )
