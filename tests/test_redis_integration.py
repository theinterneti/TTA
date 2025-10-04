# CI retrigger: ensure sync Redis fixture is used consistently


import pytest


@pytest.mark.redis
def test_redis_container_basic(redis_client_sync):
    # Basic set/get
    redis_client_sync.set("tta:test:key", "value")
    assert redis_client_sync.get("tta:test:key") == b"value"


@pytest.mark.redis
def test_redis_container_expiry(redis_client_sync):
    redis_client_sync.set("tta:test:ttl", "1", ex=1)
    assert redis_client_sync.exists("tta:test:ttl") == 1
    import time

    time.sleep(1.2)
    assert redis_client_sync.exists("tta:test:ttl") == 0
