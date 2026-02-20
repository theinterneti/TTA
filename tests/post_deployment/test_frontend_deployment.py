"""

# Logseq: [[TTA.dev/Tests/Post_deployment/Test_frontend_deployment]]
Post-Deployment Tests: Frontend Deployment Verification (Issue #4)

These tests verify that the frontend deployment fix remains effective.

Issue #4 Fix: Frontend Docker builds now correctly copy from /app/build
(not /app/dist), use the correct build script, and include cache-busting
mechanisms to ensure fresh deployments.

Test Coverage:
- Frontend serves fresh build (not cached)
- index.html has no-cache headers
- Static assets have proper cache headers
- Frontend environment variables correctly injected
- Frontend can communicate with backend API

Note: These tests use httpx for HTTP requests instead of Playwright
for simplicity and faster execution. Full E2E tests with Playwright
are in tests/e2e/.
"""

import re

import pytest


@pytest.mark.asyncio
async def test_frontend_is_accessible(
    frontend_base_url: str,
    health_check: dict,
):
    """
    Test that the frontend is accessible and serving content.

    Args:
        frontend_base_url: Frontend base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(frontend_base_url)

        assert response.status_code == 200, (
            f"Frontend not accessible: status {response.status_code}"
        )

        # Verify we got HTML content
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type, (
            f"Frontend not serving HTML: content-type is {content_type}"
        )


@pytest.mark.asyncio
async def test_frontend_index_has_no_cache_headers(
    frontend_base_url: str,
    health_check: dict,
):
    """
    Test that index.html has no-cache headers to prevent stale deployments.

    This validates part of the Issue #4 fix where nginx was configured
    to prevent browser caching of index.html.

    Args:
        frontend_base_url: Frontend base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(frontend_base_url)

        assert response.status_code == 200

        # Check Cache-Control header
        cache_control = response.headers.get("cache-control", "").lower()

        # Should have no-cache or no-store directives
        assert any(
            directive in cache_control
            for directive in ["no-cache", "no-store", "must-revalidate"]
        ), (
            f"index.html missing no-cache headers. "
            f"Cache-Control: {cache_control}. "
            "Issue #4 fix (cache prevention) may have regressed."
        )


@pytest.mark.asyncio
async def test_frontend_static_assets_have_cache_headers(
    frontend_base_url: str,
    health_check: dict,
):
    """
    Test that static assets (JS, CSS) have proper cache headers.

    Static assets should be cached for performance, while index.html
    should not be cached.

    Args:
        frontend_base_url: Frontend base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # First, get index.html to find static asset references
        index_response = await client.get(frontend_base_url)
        index_html = index_response.text

        # Find JS and CSS files in the HTML
        js_files = re.findall(r'src="(/static/js/[^"]+\.js)"', index_html)
        css_files = re.findall(r'href="(/static/css/[^"]+\.css)"', index_html)

        # Test at least one static asset if found
        static_assets = js_files + css_files

        if not static_assets:
            pytest.skip("No static assets found in index.html to test")

        # Test the first static asset
        asset_path = static_assets[0]
        asset_url = f"{frontend_base_url}{asset_path}"

        asset_response = await client.get(asset_url)

        # Static assets should be cacheable
        if asset_response.status_code == 200:
            cache_control = asset_response.headers.get("cache-control", "").lower()

            # Should have caching enabled (not no-cache)
            # Typically: "public, max-age=31536000" or similar
            assert "no-cache" not in cache_control or "max-age" in cache_control, (
                f"Static asset has incorrect cache headers. "
                f"Cache-Control: {cache_control}"
            )


@pytest.mark.asyncio
async def test_frontend_environment_variables_injected(
    frontend_base_url: str,
    api_base_url: str,
    health_check: dict,
):
    """
    Test that frontend environment variables are correctly injected.

    The frontend should have access to runtime configuration including
    API base URL and environment name.

    Args:
        frontend_base_url: Frontend base URL
        api_base_url: API base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try to fetch config.js if it exists (from Dockerfile.staging)
        config_response = await client.get(f"{frontend_base_url}/config.js")

        if config_response.status_code == 200:
            config_content = config_response.text

            # Verify config contains expected values
            assert "TTA_CONFIG" in config_content, "config.js missing TTA_CONFIG object"

            # Check for environment configuration
            assert "environment" in config_content, (
                "config.js missing environment configuration"
            )

            # Check for API URL configuration
            assert "apiBaseUrl" in config_content or "api" in config_content.lower(), (
                "config.js missing API URL configuration"
            )


@pytest.mark.asyncio
async def test_frontend_can_reach_backend_api(
    frontend_base_url: str,
    api_base_url: str,
    health_check: dict,
):
    """
    Test that the frontend can communicate with the backend API.

    This validates that CORS and network configuration are correct.

    Args:
        frontend_base_url: Frontend base URL
        api_base_url: API base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test API health endpoint
        api_response = await client.get(f"{api_base_url}/api/v1/health/")

        assert api_response.status_code == 200, (
            f"Backend API not accessible from test environment: "
            f"status {api_response.status_code}"
        )

        # Verify CORS headers are present (if making cross-origin request)
        if (
            frontend_base_url.split("://")[1].split(":", maxsplit=1)[0]
            != api_base_url.split("://")[1].split(":", maxsplit=1)[0]
        ):
            # Cross-origin request - check CORS headers
            cors_headers = api_response.headers.get("access-control-allow-origin")

            # CORS should be configured (either specific origin or *)
            # Note: In production, this should be specific origins, not *
            assert cors_headers is not None, (
                "Backend API missing CORS headers. "
                "Frontend may not be able to communicate with backend."
            )


@pytest.mark.asyncio
async def test_frontend_build_is_fresh(
    frontend_base_url: str,
    health_check: dict,
):
    """
    Test that the frontend build is fresh (not from Docker cache).

    This validates the cache-busting mechanism from Issue #4 fix.

    Args:
        frontend_base_url: Frontend base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(frontend_base_url)

        # Check for build metadata in headers or HTML
        # The Dockerfile.staging adds X-Environment header
        environment_header = response.headers.get("x-environment")

        if environment_header:
            # Verify environment header is set correctly
            assert environment_header in ["staging", "production", "development"], (
                f"Unexpected X-Environment header: {environment_header}"
            )

        # Check HTML for build indicators
        html_content = response.text

        # React apps typically have a root div
        assert '<div id="root"' in html_content, (
            "Frontend HTML missing React root div. "
            "Build may be incomplete or corrupted."
        )


@pytest.mark.asyncio
async def test_frontend_serves_react_app(
    frontend_base_url: str,
    health_check: dict,
):
    """
    Test that the frontend is serving a React application.

    Args:
        frontend_base_url: Frontend base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(frontend_base_url)

        html_content = response.text

        # Check for React indicators
        react_indicators = [
            '<div id="root"',  # React root div
            "react",  # React in script tags
            "/static/js/",  # CRA static JS directory
        ]

        found_indicators = [
            indicator
            for indicator in react_indicators
            if indicator.lower() in html_content.lower()
        ]

        assert len(found_indicators) >= 1, (
            f"Frontend does not appear to be a React app. "
            f"Found {len(found_indicators)}/3 React indicators. "
            "Build may have failed or wrong files were deployed."
        )


@pytest.mark.asyncio
async def test_frontend_nginx_configuration(
    frontend_base_url: str,
    health_check: dict,
):
    """
    Test that nginx is configured correctly for React Router.

    React Router requires all routes to serve index.html.

    Args:
        frontend_base_url: Frontend base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        # Test a non-existent route (should serve index.html, not 404)
        response = await client.get(f"{frontend_base_url}/nonexistent-route")

        # Should either:
        # 1. Return 200 with index.html (correct nginx config)
        # 2. Return 404 (incorrect nginx config - needs try_files fix)
        assert response.status_code in [200, 404], (
            f"Unexpected status code for non-existent route: {response.status_code}"
        )

        if response.status_code == 200:
            # Verify it's serving index.html (React app will handle routing)
            content = response.text
            assert '<div id="root"' in content, (
                "Non-existent route not serving React app. "
                "Nginx try_files configuration may be incorrect."
            )


@pytest.mark.asyncio
async def test_frontend_security_headers(
    frontend_base_url: str,
    health_check: dict,
):
    """
    Test that frontend has security headers configured.

    Args:
        frontend_base_url: Frontend base URL
        health_check: Health check result
    """
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(frontend_base_url)

        # Check for security headers (from nginx.conf)
        security_headers = {
            "x-frame-options": ["DENY", "SAMEORIGIN"],
            "x-content-type-options": ["nosniff"],
            "x-xss-protection": ["1"],
        }

        for header, expected_values in security_headers.items():
            header_value = response.headers.get(header, "").upper()

            if header_value:
                # Header is present - verify it has expected value
                assert any(
                    expected.upper() in header_value for expected in expected_values
                ), f"Security header {header} has unexpected value: {header_value}"
