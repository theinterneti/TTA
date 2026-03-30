"""

# Logseq: [[TTA.dev/Tests/Post_deployment/__init__]]
Post-Deployment Integration Tests

This package contains automated integration tests that run after deployment
to verify critical fixes remain effective in production environments.

Test Categories:
- JWT Token Validation (Issue #2)
- Player Profile Auto-Creation (Issue #3)
- Frontend Deployment Verification (Issue #4)

These tests are designed to run against live deployed environments (staging/production)
and validate that recent bug fixes have not regressed.
"""

__version__ = "1.0.0"
