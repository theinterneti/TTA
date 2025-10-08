#!/usr/bin/env python3
"""
Complete TTA Core Gameplay Loop Integration Validation Script

This script performs the complete end-to-end validation of the TTA Core Gameplay Loop
integration, including system startup, database connectivity, and API testing.
"""

import os
import sys
import subprocess
import time
import requests
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TTAIntegrationValidator:
    """Complete TTA Core Gameplay Loop integration validator."""

    def __init__(self):
        self.project_root = project_root
        self.api_base_url = "http://localhost:8000"
        self.validation_results = {}

    def install_dependencies(self) -> bool:
        """Install required Python dependencies."""
        logger.info("🔧 Installing required dependencies...")

        dependencies = [
            "fastapi", "uvicorn", "pydantic", "rich", "aiohttp",
            "requests", "pytest", "pytest-asyncio", "redis", "neo4j"
        ]

        try:
            for dep in dependencies:
                logger.info(f"Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, timeout=60)

                if result.returncode != 0:
                    logger.error(f"Failed to install {dep}: {result.stderr}")
                    return False

            logger.info("✅ All dependencies installed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Dependency installation failed: {e}")
            return False

    def check_environment_config(self) -> bool:
        """Check and setup environment configuration."""
        logger.info("🔍 Checking environment configuration...")

        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if not env_file.exists():
            if env_example.exists():
                logger.info("Creating .env from .env.example...")
                import shutil
                shutil.copy(env_example, env_file)
            else:
                logger.error("❌ No .env.example file found")
                return False

        # Check for required environment variables
        required_vars = [
            "NEO4J_PASSWORD", "REDIS_URL", "JWT_SECRET_KEY"
        ]

        missing_vars = []
        with open(env_file, 'r') as f:
            env_content = f.read()

        for var in required_vars:
            if f"{var}=" not in env_content or f"{var}=your_" in env_content:
                missing_vars.append(var)

        if missing_vars:
            logger.warning(f"⚠️  Missing or placeholder values for: {', '.join(missing_vars)}")
            logger.info("Setting default values for development...")

            # Set development defaults
            defaults = {
                "NEO4J_PASSWORD": "password",
                "REDIS_URL": "redis://localhost:6379",
                "JWT_SECRET_KEY": "development_jwt_secret_key_minimum_32_characters_long"
            }

            with open(env_file, 'a') as f:
                f.write("\n# Development defaults added by validation script\n")
                for var in missing_vars:
                    if var in defaults:
                        f.write(f"{var}={defaults[var]}\n")

        logger.info("✅ Environment configuration ready")
        return True

    def check_database_connectivity(self) -> Dict[str, bool]:
        """Check Redis and Neo4j connectivity."""
        logger.info("🔍 Checking database connectivity...")

        results = {}

        # Test Redis
        try:
            result = subprocess.run(["redis-cli", "ping"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "PONG" in result.stdout:
                logger.info("✅ Redis connection successful")
                results["redis"] = True
            else:
                logger.error("❌ Redis connection failed")
                results["redis"] = False
        except Exception as e:
            logger.error(f"❌ Redis test error: {e}")
            results["redis"] = False

        # Test Neo4j (basic connectivity)
        try:
            # Try to connect to Neo4j HTTP interface
            response = requests.get("http://localhost:7474", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Neo4j HTTP interface accessible")
                results["neo4j_http"] = True
            else:
                logger.warning("⚠️  Neo4j HTTP interface not accessible")
                results["neo4j_http"] = False
        except Exception as e:
            logger.warning(f"⚠️  Neo4j HTTP test: {e}")
            results["neo4j_http"] = False

        return results

    def start_tta_system(self) -> bool:
        """Start the TTA system."""
        logger.info("🚀 Starting TTA system...")

        try:
            # Check if system is already running
            try:
                response = requests.get(f"{self.api_base_url}/docs", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ TTA system is already running")
                    return True
            except:
                pass  # System not running, continue with startup

            # Start the system using the player experience API
            logger.info("Starting FastAPI server...")

            # Use the existing startup script if available
            startup_script = self.project_root / "scripts" / "start_with_gameplay.py"
            if startup_script.exists():
                logger.info("Using existing startup script...")
                # Start in background
                process = subprocess.Popen([
                    sys.executable, str(startup_script)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Wait for startup
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    try:
                        response = requests.get(f"{self.api_base_url}/docs", timeout=2)
                        if response.status_code == 200:
                            logger.info("✅ TTA system started successfully")
                            return True
                    except:
                        continue

                logger.error("❌ TTA system failed to start within timeout")
                return False
            else:
                logger.error("❌ No startup script found")
                return False

        except Exception as e:
            logger.error(f"❌ TTA system startup failed: {e}")
            return False

    def run_architecture_validation(self) -> bool:
        """Run the architecture validation script."""
        logger.info("🔍 Running architecture validation...")

        try:
            validation_script = self.project_root / "scripts" / "validate_integration_architecture.py"
            result = subprocess.run([
                sys.executable, str(validation_script)
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                logger.info("✅ Architecture validation passed")
                return True
            else:
                logger.warning("⚠️  Architecture validation had issues")
                logger.info(f"Output: {result.stdout}")
                return False

        except Exception as e:
            logger.error(f"❌ Architecture validation failed: {e}")
            return False

    def run_api_tests(self) -> bool:
        """Run the API endpoint tests."""
        logger.info("🔍 Running API endpoint tests...")

        try:
            api_test_script = self.project_root / "scripts" / "test_api_endpoints.py"
            result = subprocess.run([
                sys.executable, str(api_test_script)
            ], capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                logger.info("✅ API tests passed")
                return True
            else:
                logger.warning("⚠️  API tests had issues")
                logger.info(f"Output: {result.stdout}")
                return False

        except Exception as e:
            logger.error(f"❌ API tests failed: {e}")
            return False

    def test_frontend_integration(self) -> bool:
        """Test frontend integration capabilities."""
        logger.info("🔍 Testing frontend integration...")

        try:
            # Test basic API endpoints that frontend would use
            endpoints_to_test = [
                "/docs",
                "/openapi.json",
                "/api/v1/gameplay/health"
            ]

            for endpoint in endpoints_to_test:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ Frontend endpoint accessible: {endpoint}")
                else:
                    logger.warning(f"⚠️  Frontend endpoint issue: {endpoint} returned {response.status_code}")
                    return False

            logger.info("✅ Frontend integration endpoints are accessible")
            return True

        except Exception as e:
            logger.error(f"❌ Frontend integration test failed: {e}")
            return False

    def run_complete_validation(self) -> Dict[str, bool]:
        """Run the complete validation sequence."""
        logger.info("🎮 TTA Core Gameplay Loop - Complete Integration Validation")
        logger.info("=" * 70)

        validation_steps = [
            ("Install Dependencies", self.install_dependencies),
            ("Environment Config", self.check_environment_config),
            ("Database Connectivity", lambda: all(self.check_database_connectivity().values())),
            ("Start TTA System", self.start_tta_system),
            ("Architecture Validation", self.run_architecture_validation),
            ("API Tests", self.run_api_tests),
            ("Frontend Integration", self.test_frontend_integration),
        ]

        results = {}

        for step_name, step_func in validation_steps:
            logger.info(f"\n--- {step_name} ---")
            try:
                results[step_name] = step_func()
            except Exception as e:
                logger.error(f"❌ {step_name} failed with exception: {e}")
                results[step_name] = False

        return results

def main():
    """Main validation execution."""
    validator = TTAIntegrationValidator()
    results = validator.run_complete_validation()

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 COMPLETE VALIDATION RESULTS")
    logger.info("=" * 70)

    passed = 0
    total = len(results)

    for step_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{step_name:25} : {status}")
        if result:
            passed += 1

    logger.info("-" * 70)
    logger.info(f"TOTAL: {passed}/{total} steps completed ({passed/total*100:.1f}%)")

    if passed == total:
        logger.info("🎉 COMPLETE VALIDATION SUCCESSFUL! TTA Core Gameplay Loop integration is fully operational.")
        logger.info("\n🌐 Next Steps:")
        logger.info("1. Open http://localhost:8000/docs to explore the API")
        logger.info("2. Open examples/frontend_integration.html to test browser integration")
        logger.info("3. Run integration tests: python3 -m pytest tests/integration/ -v")
        return 0
    else:
        logger.error("⚠️  Validation incomplete. Check the logs above for details.")
        logger.info("\n🔧 Troubleshooting:")
        logger.info("1. Ensure Neo4j and Redis are running")
        logger.info("2. Check database credentials in .env file")
        logger.info("3. Verify all dependencies are installed")
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
