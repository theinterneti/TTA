"""Conftest for agent_orchestration tests.

Most tests here require tta_ai (from the TTA.dev sibling repo) and Redis.
When tta_ai is not installed (e.g. in a dev environment without TTA.dev cloned),
all tests in this directory are skipped rather than erroring on collection.
"""

import pytest

# Skip this entire directory if tta_ai is not installed.
# In CI, TTA.dev is cloned before running tests so tta_ai is always available.
# Locally, clone TTA.dev as a sibling: git clone .../TTA.dev ../TTA.dev && uv sync
pytest.importorskip("tta_ai")
