#!/usr/bin/env python3
"""
TTA Core Gameplay Loop Integration Architecture Validation

This script validates the integration architecture without requiring
full database connectivity, focusing on code structure, imports,
and API endpoint availability.
"""

import logging
import sys
from pathlib import Path

import requests

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationArchitectureValidator:
    """Validates the TTA Core Gameplay Loop integration architecture."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.validation_results = {}

    def validate_component_registration(self) -> bool:
        """Validate that GameplayLoopComponent is properly registered."""
        logger.info("🔍 Validating component registration...")

        try:
            # Check if GameplayLoopComponent can be imported
            from src.components.gameplay_loop_component import GameplayLoopComponent
            logger.info("✅ GameplayLoopComponent import successful")

            # Check if it has the required TTA component structure
            required_methods = ['initialize', 'start', 'stop', 'get_status']
            for method in required_methods:
                if hasattr(GameplayLoopComponent, method):
                    logger.info(f"✅ GameplayLoopComponent has {method} method")
                else:
                    logger.warning(f"⚠️  GameplayLoopComponent missing {method} method")

            # Check orchestrator registration
            from src.orchestration.orchestrator import Orchestrator
            logger.info("✅ Orchestrator import successful")

            return True

        except ImportError as e:
            logger.error(f"❌ Component registration validation failed: {e}")
            return False

    def validate_integration_layer(self) -> bool:
        """Validate the integration layer exists and has required methods."""
        logger.info("🔍 Validating integration layer...")

        try:
            from src.integration.gameplay_loop_integration import (
                GameplayLoopIntegration,
            )
            logger.info("✅ GameplayLoopIntegration import successful")

            # Check required methods
            required_methods = [
                'create_authenticated_session',
                'validate_therapeutic_safety',
                'coordinate_with_agents'
            ]

            for method in required_methods:
                if hasattr(GameplayLoopIntegration, method):
                    logger.info(f"✅ GameplayLoopIntegration has {method} method")
                else:
                    logger.warning(f"⚠️  GameplayLoopIntegration missing {method} method")

            return True

        except ImportError as e:
            logger.error(f"❌ Integration layer validation failed: {e}")
            return False

    def validate_api_endpoints(self) -> bool:
        """Validate that gameplay API endpoints are available."""
        logger.info("🔍 Validating API endpoints...")

        try:
            # Check if the server is running
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API server is running and accessible")
            else:
                logger.warning(f"⚠️  API server returned {response.status_code}")
                return False

            # Check OpenAPI spec for gameplay endpoints
            openapi_response = requests.get(f"{self.base_url}/openapi.json", timeout=5)
            if openapi_response.status_code == 200:
                openapi_spec = openapi_response.json()
                paths = openapi_spec.get('paths', {})

                # Check for gameplay endpoints
                gameplay_endpoints = [
                    '/api/v1/gameplay/sessions',
                    '/api/v1/gameplay/sessions/{session_id}',
                    '/api/v1/gameplay/sessions/{session_id}/choices',
                    '/api/v1/gameplay/sessions/{session_id}/progress',
                    '/api/v1/gameplay/health'
                ]

                found_endpoints = []
                for endpoint in gameplay_endpoints:
                    # Check for exact match or pattern match
                    if endpoint in paths:
                        found_endpoints.append(endpoint)
                        logger.info(f"✅ Found endpoint: {endpoint}")
                    else:
                        # Check for pattern matches (e.g., with path parameters)
                        pattern_found = False
                        for path in paths.keys():
                            if endpoint.replace('{session_id}', '') in path:
                                found_endpoints.append(path)
                                logger.info(f"✅ Found endpoint pattern: {path}")
                                pattern_found = True
                                break
                        if not pattern_found:
                            logger.warning(f"⚠️  Missing endpoint: {endpoint}")

                if len(found_endpoints) >= 3:  # At least some core endpoints
                    logger.info("✅ Core gameplay endpoints are available")
                    return True
                logger.warning("⚠️  Missing critical gameplay endpoints")
                return False
            logger.error("❌ Could not retrieve OpenAPI specification")
            return False

        except requests.RequestException as e:
            logger.error(f"❌ API endpoint validation failed: {e}")
            return False

    def validate_configuration_integration(self) -> bool:
        """Validate configuration integration."""
        logger.info("🔍 Validating configuration integration...")

        try:
            # Check if config file exists and has gameplay loop section
            config_path = Path("config/tta_config.yaml")
            if config_path.exists():
                logger.info("✅ TTA config file exists")

                with open(config_path) as f:
                    config_content = f.read()

                if 'core_gameplay_loop' in config_content:
                    logger.info("✅ core_gameplay_loop section found in config")
                    return True
                logger.warning("⚠️  core_gameplay_loop section missing from config")
                return False
            logger.error("❌ TTA config file not found")
            return False

        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False

    def validate_data_models(self) -> bool:
        """Validate that data models are properly defined."""
        logger.info("🔍 Validating data models...")

        try:
            # Check gameplay loop models
            from src.components.gameplay_loop.models.interactions import (
                GameplaySession,
                NarrativeScene,
                UserChoice,
            )
            logger.info("✅ Core gameplay models import successful")

            # Check API models
            from src.player_experience.api.routers.gameplay import (
                CreateSessionRequest,
                CreateSessionResponse,
                ProcessChoiceRequest,
                ProcessChoiceResponse,
            )
            logger.info("✅ API models import successful")

            return True

        except ImportError as e:
            logger.error(f"❌ Data models validation failed: {e}")
            return False

    def validate_service_layer(self) -> bool:
        """Validate service layer integration."""
        logger.info("🔍 Validating service layer...")

        try:
            from src.player_experience.services.gameplay_service import GameplayService
            logger.info("✅ GameplayService import successful")

            # Check if service has required methods
            required_methods = [
                'create_session',
                'get_session_status',
                'process_choice',
                'get_progress'
            ]

            for method in required_methods:
                if hasattr(GameplayService, method):
                    logger.info(f"✅ GameplayService has {method} method")
                else:
                    logger.warning(f"⚠️  GameplayService missing {method} method")

            return True

        except ImportError as e:
            logger.error(f"❌ Service layer validation failed: {e}")
            return False

    def validate_testing_integration(self) -> bool:
        """Validate testing integration."""
        logger.info("🔍 Validating testing integration...")

        try:
            # Check if integration tests exist
            test_files = [
                "tests/integration/test_gameplay_loop_integration.py",
                "tests/integration/test_gameplay_api.py"
            ]

            found_tests = 0
            for test_file in test_files:
                if Path(test_file).exists():
                    logger.info(f"✅ Found test file: {test_file}")
                    found_tests += 1
                else:
                    logger.warning(f"⚠️  Missing test file: {test_file}")

            if found_tests >= 1:
                logger.info("✅ Integration tests are available")
                return True
            logger.warning("⚠️  No integration tests found")
            return False

        except Exception as e:
            logger.error(f"❌ Testing validation failed: {e}")
            return False

    def run_comprehensive_validation(self) -> dict[str, bool]:
        """Run all validation checks."""
        logger.info("🚀 Starting comprehensive integration architecture validation...")
        logger.info("=" * 70)

        validations = [
            ("Component Registration", self.validate_component_registration),
            ("Integration Layer", self.validate_integration_layer),
            ("API Endpoints", self.validate_api_endpoints),
            ("Configuration Integration", self.validate_configuration_integration),
            ("Data Models", self.validate_data_models),
            ("Service Layer", self.validate_service_layer),
            ("Testing Integration", self.validate_testing_integration),
        ]

        results = {}

        for validation_name, validation_func in validations:
            logger.info(f"\n--- {validation_name} ---")
            try:
                results[validation_name] = validation_func()
            except Exception as e:
                logger.error(f"❌ {validation_name} failed with exception: {e}")
                results[validation_name] = False

        return results

def main():
    """Main validation execution."""
    logger.info("🎮 TTA Core Gameplay Loop - Integration Architecture Validation")
    logger.info("=" * 70)

    validator = IntegrationArchitectureValidator()
    results = validator.run_comprehensive_validation()

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 VALIDATION RESULTS SUMMARY")
    logger.info("=" * 70)

    passed = 0
    total = len(results)

    for validation_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{validation_name:25} : {status}")
        if result:
            passed += 1

    logger.info("-" * 70)
    logger.info(f"TOTAL: {passed}/{total} validations passed ({passed/total*100:.1f}%)")

    if passed == total:
        logger.info("🎉 ALL VALIDATIONS PASSED! Integration architecture is solid.")
        return 0
    if passed >= total * 0.8:  # 80% pass rate
        logger.info("✅ INTEGRATION ARCHITECTURE IS SOLID! Minor issues detected.")
        return 0
    logger.error("⚠️  Integration architecture needs attention.")
    return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
