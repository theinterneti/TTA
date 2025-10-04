import asyncio
import json

import pytest

from src.agent_orchestration.therapeutic_safety import (
    SafetyLevel,
    SafetyRulesProvider,
    SafetyService,
    TherapeuticValidator,
)


def test_validator_default_rules_block_crisis_and_warn_ethics():
    v = TherapeuticValidator()
    r1 = v.validate_text("I want to kill myself")
    assert r1.level == SafetyLevel.BLOCKED
    assert any(f.category == "crisis_detection" for f in r1.findings)

    r2 = v.validate_text("Can you diagnose me?")
    assert r2.level in (SafetyLevel.WARNING, SafetyLevel.BLOCKED)


def test_suggest_alternative_messages():
    v = TherapeuticValidator()
    alt_blocked = v.suggest_alternative(reason=SafetyLevel.BLOCKED, original="...")
    assert "support" in alt_blocked.lower()
    alt_warn = v.suggest_alternative(reason=SafetyLevel.WARNING, original="...")
    assert "responsibly" in alt_warn.lower()


@pytest.mark.asyncio
async def test_safety_rules_provider_fallback_file(tmp_path):
    cfg = {
        "rules": [
            {
                "id": "w",
                "category": "professional_ethics",
                "priority": 1,
                "level": "warning",
                "pattern": "prescribe",
                "flags": "i",
            }
        ]
    }
    p = tmp_path / "rules.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    prov = SafetyRulesProvider(redis_client=None, file_fallback_path=str(p))
    got = await prov.get_config()
    assert got["rules"][0]["id"] == "w"


@pytest.mark.redis
@pytest.mark.asyncio
async def test_safety_rules_provider_reads_redis(redis_client):
    # Write a custom cfg to Redis
    cfg = {
        "rules": [
            {
                "id": "c1",
                "category": "crisis_detection",
                "priority": 99,
                "level": "blocked",
                "pattern": "self harm",
                "flags": "i",
            }
        ]
    }
    await redis_client.set("ao:safety:rules", json.dumps(cfg))
    prov = SafetyRulesProvider(redis_client=redis_client)
    got = await prov.get_config()
    assert any(r.get("id") == "c1" for r in got.get("rules", []))


@pytest.mark.asyncio
async def test_safety_service_disabled_fast_path():
    svc = SafetyService(enabled=False, provider=SafetyRulesProvider(redis_client=None))
    res = await svc.validate_text("anything")
    assert res.level == SafetyLevel.SAFE
    assert any(a.get("event") == "disabled" for a in res.audit)


@pytest.mark.redis
@pytest.mark.asyncio
async def test_safety_service_live_reload(redis_client):
    cfg1 = {
        "rules": [
            {
                "id": "w1",
                "category": "professional_ethics",
                "priority": 1,
                "level": "warning",
                "pattern": "diagnose",
                "flags": "i",
            }
        ]
    }
    await redis_client.set("ao:safety:rules", json.dumps(cfg1))
    svc = SafetyService(
        enabled=True,
        provider=SafetyRulesProvider(redis_client=redis_client, cache_ttl_s=0.1),
    )
    r = await svc.validate_text("Please diagnose me")
    assert r.level == SafetyLevel.WARNING
    # Update cfg to block
    cfg2 = {
        "rules": [
            {
                "id": "b1",
                "category": "crisis_detection",
                "priority": 99,
                "level": "blocked",
                "pattern": "kill myself",
                "flags": "i",
            }
        ]
    }
    await redis_client.set("ao:safety:rules", json.dumps(cfg2))
    await asyncio.sleep(0.12)
    r2 = await svc.validate_text("I want to kill myself")
    assert r2.level == SafetyLevel.BLOCKED
