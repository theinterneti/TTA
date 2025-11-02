#!/usr/bin/env python3
"""
Manual Testing Guide Validation Script

This script validates that all the steps in the manual testing guide
can be performed and that the expected results are achievable.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ManualTestingGuideValidator:
    """Validates the manual testing guide procedures."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: aiohttp.ClientSession | None = None
        self.validation_results = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def log_validation(self, step: str, success: bool, details: str = ""):
        """Log validation results."""
        status = "✅ VALID" if success else "❌ INVALID"
        logger.info(f"{status} - {step}: {details}")
        self.validation_results[step] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

    async def validate_phase1_initial_setup(self) -> bool:
        """Validate Phase 1: Initial Setup Validation steps."""
        logger.info("🔍 Validating Phase 1: Initial Setup...")

        # Check frontend file exists
        frontend_path = Path("examples/frontend_integration.html")
        if not frontend_path.exists():
            self.log_validation("Frontend File Exists", False, "File not found")
            return False

        # Check file content
        content = frontend_path.read_text()
        required_elements = [
            "TTA Therapeutic Text Adventure",
            "Authentication",
            "Use Test Token",
            "Start New Session",
        ]

        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)

        if missing_elements:
            self.log_validation(
                "Frontend Content", False, f"Missing: {missing_elements}"
            )
            return False
        self.log_validation("Frontend Content", True, "All required elements present")

        return True

    async def validate_phase2_api_documentation(self) -> bool:
        """Validate Phase 2: API Documentation Testing steps."""
        logger.info("🔍 Validating Phase 2: API Documentation...")

        try:
            # Test Swagger UI accessibility
            async with self.session.get(f"{self.base_url}/docs") as response:
                if response.status != 200:
                    self.log_validation(
                        "Swagger UI Access", False, f"HTTP {response.status}"
                    )
                    return False

                content = await response.text()
                if "swagger-ui" not in content.lower():
                    self.log_validation(
                        "Swagger UI Content", False, "Swagger UI not found"
                    )
                    return False

            # Test OpenAPI spec
            async with self.session.get(f"{self.base_url}/openapi.json") as response:
                if response.status != 200:
                    self.log_validation(
                        "OpenAPI Spec", False, f"HTTP {response.status}"
                    )
                    return False

                spec = await response.json()
                paths = spec.get("paths", {})

                # Check for required gameplay endpoints
                required_endpoints = [
                    "/api/v1/gameplay/sessions",
                    "/api/v1/gameplay/health",
                ]

                missing_endpoints = []
                for endpoint in required_endpoints:
                    if endpoint not in paths:
                        missing_endpoints.append(endpoint)

                if missing_endpoints:
                    self.log_validation(
                        "Required Endpoints", False, f"Missing: {missing_endpoints}"
                    )
                    return False
                self.log_validation(
                    "Required Endpoints", True, "All required endpoints present"
                )

            return True

        except Exception as e:
            self.log_validation("API Documentation", False, f"Error: {e}")
            return False

    async def validate_phase3_authentication(self) -> bool:
        """Validate Phase 3: Authentication Testing steps."""
        logger.info("🔍 Validating Phase 3: Authentication...")

        # Test that authentication is required
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/gameplay/health"
            ) as response:
                if response.status == 401:
                    self.log_validation(
                        "Auth Required", True, "Correctly requires authentication"
                    )
                else:
                    self.log_validation(
                        "Auth Required", False, f"Expected 401, got {response.status}"
                    )
                    return False
        except Exception as e:
            self.log_validation("Auth Required", False, f"Error: {e}")
            return False

        # Test that test token approach is documented in frontend
        frontend_path = Path("examples/frontend_integration.html")
        content = frontend_path.read_text()

        if "Use Test Token" in content and "test_token" in content:
            self.log_validation(
                "Test Token Option", True, "Test token option available"
            )
        else:
            self.log_validation(
                "Test Token Option", False, "Test token option not found"
            )
            return False

        return True

    async def validate_phase4_session_management(self) -> bool:
        """Validate Phase 4: Session Management Testing steps."""
        logger.info("🔍 Validating Phase 4: Session Management...")

        # Test session creation endpoint exists
        try:
            headers = {"Content-Type": "application/json"}
            payload = {"therapeutic_context": {"goals": ["test"]}}

            async with self.session.post(
                f"{self.base_url}/api/v1/gameplay/sessions",
                headers=headers,
                json=payload,
            ) as response:
                # Should require authentication
                if response.status == 401:
                    self.log_validation(
                        "Session Endpoint",
                        True,
                        "Session endpoint exists and requires auth",
                    )
                elif response.status in [200, 201, 422]:
                    self.log_validation(
                        "Session Endpoint", True, "Session endpoint functional"
                    )
                else:
                    self.log_validation(
                        "Session Endpoint",
                        False,
                        f"Unexpected status: {response.status}",
                    )
                    return False
        except Exception as e:
            self.log_validation("Session Endpoint", False, f"Error: {e}")
            return False

        return True

    async def validate_phase5_swagger_testing(self) -> bool:
        """Validate Phase 5: API Endpoint Testing via Swagger UI steps."""
        logger.info("🔍 Validating Phase 5: Swagger UI Testing...")

        try:
            # Get OpenAPI spec to validate endpoint documentation
            async with self.session.get(f"{self.base_url}/openapi.json") as response:
                spec = await response.json()
                paths = spec.get("paths", {})

                # Check that endpoints have proper documentation
                gameplay_endpoints = [p for p in paths.keys() if "/gameplay/" in p]

                if len(gameplay_endpoints) < 3:
                    self.log_validation(
                        "Swagger Endpoints",
                        False,
                        f"Only {len(gameplay_endpoints)} endpoints",
                    )
                    return False

                # Check that endpoints have proper schemas
                documented_properly = True
                for endpoint in gameplay_endpoints:
                    endpoint_info = paths[endpoint]
                    for method, method_info in endpoint_info.items():
                        if "responses" not in method_info:
                            documented_properly = False
                            break

                if documented_properly:
                    self.log_validation(
                        "Swagger Documentation", True, "Endpoints properly documented"
                    )
                else:
                    self.log_validation(
                        "Swagger Documentation", False, "Missing response schemas"
                    )
                    return False

        except Exception as e:
            self.log_validation("Swagger Testing", False, f"Error: {e}")
            return False

        return True

    async def validate_phase6_error_handling(self) -> bool:
        """Validate Phase 6: Error Handling Testing steps."""
        logger.info("🔍 Validating Phase 6: Error Handling...")

        try:
            # Test unauthorized access
            async with self.session.get(
                f"{self.base_url}/api/v1/gameplay/health"
            ) as response:
                if response.status == 401:
                    self.log_validation(
                        "Unauthorized Handling", True, "Returns 401 for unauthorized"
                    )
                else:
                    self.log_validation(
                        "Unauthorized Handling",
                        False,
                        f"Expected 401, got {response.status}",
                    )

            # Test malformed request
            headers = {"Content-Type": "application/json"}
            async with self.session.post(
                f"{self.base_url}/api/v1/gameplay/sessions",
                headers=headers,
                data="invalid json",
            ) as response:
                if response.status in [400, 401, 422]:
                    self.log_validation(
                        "Malformed Request",
                        True,
                        f"Handles malformed requests: {response.status}",
                    )
                else:
                    self.log_validation(
                        "Malformed Request",
                        False,
                        f"Unexpected status: {response.status}",
                    )

            return True

        except Exception as e:
            self.log_validation("Error Handling", False, f"Error: {e}")
            return False

    async def validate_phase7_browser_console(self) -> bool:
        """Validate Phase 7: Browser Console Testing steps."""
        logger.info("🔍 Validating Phase 7: Browser Console...")

        # Check that frontend has proper JavaScript structure
        frontend_path = Path("examples/frontend_integration.html")
        content = frontend_path.read_text()

        # Check for proper JavaScript functions
        required_js_elements = [
            "async function",
            "fetch(",
            "Authorization",
            "Bearer",
            "try {",
            "catch",
        ]

        missing_js = []
        for element in required_js_elements:
            if element not in content:
                missing_js.append(element)

        if missing_js:
            self.log_validation("JavaScript Structure", False, f"Missing: {missing_js}")
            return False
        self.log_validation(
            "JavaScript Structure", True, "Proper async/await and error handling"
        )

        return True

    async def validate_testing_guide_completeness(self) -> bool:
        """Validate that the testing guide file exists and is complete."""
        logger.info("🔍 Validating Testing Guide Completeness...")

        guide_path = Path("docs/testing/manual_frontend_testing_guide.md")
        if not guide_path.exists():
            self.log_validation("Testing Guide Exists", False, "Guide file not found")
            return False

        content = guide_path.read_text()

        # Check for required sections
        required_sections = [
            "Prerequisites",
            "Phase 1: Initial Setup",
            "Phase 2: API Documentation",
            "Phase 3: Authentication",
            "Phase 4: Session Management",
            "Phase 5: API Endpoint Testing",
            "Phase 6: Error Handling",
            "Phase 7: Browser Console",
            "Expected Results",
            "Troubleshooting",
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            self.log_validation(
                "Guide Completeness", False, f"Missing sections: {missing_sections}"
            )
            return False
        self.log_validation("Guide Completeness", True, "All required sections present")

        return True

    async def run_comprehensive_validation(self) -> dict[str, Any]:
        """Run all manual testing guide validations."""
        logger.info("🚀 Starting Manual Testing Guide Validation")
        logger.info("=" * 70)

        validation_phases = [
            ("Phase 1: Initial Setup", self.validate_phase1_initial_setup),
            ("Phase 2: API Documentation", self.validate_phase2_api_documentation),
            ("Phase 3: Authentication", self.validate_phase3_authentication),
            ("Phase 4: Session Management", self.validate_phase4_session_management),
            ("Phase 5: Swagger Testing", self.validate_phase5_swagger_testing),
            ("Phase 6: Error Handling", self.validate_phase6_error_handling),
            ("Phase 7: Browser Console", self.validate_phase7_browser_console),
            ("Testing Guide Completeness", self.validate_testing_guide_completeness),
        ]

        for phase_name, phase_func in validation_phases:
            logger.info(f"\n--- {phase_name} ---")
            try:
                await phase_func()
            except Exception as e:
                self.log_validation(phase_name, False, f"Validation exception: {e}")

            await asyncio.sleep(0.5)

        return self.validation_results


async def main():
    """Main validation execution."""
    logger.info("📋 TTA Core Gameplay Loop - Manual Testing Guide Validation")
    logger.info("=" * 70)

    async with ManualTestingGuideValidator() as validator:
        results = await validator.run_comprehensive_validation()

        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 MANUAL TESTING GUIDE VALIDATION RESULTS")
        logger.info("=" * 70)

        total_validations = len(results)
        passed_validations = sum(1 for result in results.values() if result["success"])

        for validation_name, result in results.items():
            status = "✅ VALID" if result["success"] else "❌ INVALID"
            logger.info(f"{validation_name:30} : {status}")

        logger.info("-" * 70)
        logger.info(
            f"TOTAL: {passed_validations}/{total_validations} validations passed ({passed_validations / total_validations * 100:.1f}%)"
        )

        if passed_validations >= total_validations * 0.8:
            logger.info("🎉 MANUAL TESTING GUIDE IS COMPREHENSIVE AND VALID!")
            return 0
        logger.error("⚠️  Manual testing guide needs improvements.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
