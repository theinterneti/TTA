import pytest

from tta_ai.orchestration.tools.models import ToolParameter, ToolPolicy, ToolSpec


def test_tool_spec_semver_and_param_limits():
    params = [
        ToolParameter(name=f"p{i}", required=True, schema={"type": "string"})
        for i in range(3)
    ]
    spec = ToolSpec(
        name="kg.query",
        version="1.2.3",
        description="Query the knowledge graph",
        parameters=params,
        returns_schema={"type": "object"},
        capabilities=["kg_read"],
        safety_flags=[],
    )
    h = spec.signature_hash()
    assert isinstance(h, str) and len(h) == 16

    # too many params should fail
    with pytest.raises(Exception):
        ToolSpec(
            name="x",
            version="1.0.0",
            description="d",
            parameters=[ToolParameter(name=f"q{i}", schema={}) for i in range(20)],
        )


def test_tool_policy_safety_flags():
    policy = ToolPolicy(
        allow_network_tools=False, allow_filesystem_tools=False, max_schema_depth=3
    )
    spec = ToolSpec(
        name="net.fetch",
        description="fetch network resource",
        version="1.0.0",
        parameters=[ToolParameter(name="url", schema={"type": "string"})],
        safety_flags=["network"],
    )
    with pytest.raises(Exception):
        policy.check_safety(spec)

    policy2 = ToolPolicy(allow_network_tools=True)
    policy2.check_safety(spec)  # should not raise
