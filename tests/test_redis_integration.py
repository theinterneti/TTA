import os
import pytest


@pytest.mark.redis
def test_redis_container_basic(redis_client):
    # Basic set/get
    redis_client.set("tta:test:key", "value")
    assert redis_client.get("tta:test:key") == b"value"


@pytest.mark.redis
def test_redis_container_expiry(redis_client):
    redis_client.set("tta:test:ttl", "1", ex=1)
    assert redis_client.exists("tta:test:ttl") == 1
    import time
    time.sleep(1.2)
    assert redis_client.exists("tta:test:ttl") == 0

