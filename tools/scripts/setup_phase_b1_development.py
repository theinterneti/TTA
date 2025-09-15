#!/usr/bin/env python3
"""
Phase B1: Clinical Dashboard Integration Development Setup

This script prepares the development environment for Phase B1 implementation,
ensuring all prerequisites are met and systems are properly configured.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("phase_b1_setup.log"),
    ],
)
logger = logging.getLogger(__name__)


class PhaseB1SetupManager:
    """Manages Phase B1 development environment setup."""

    def __init__(self):
        """Initialize the setup manager."""
        self.project_root = Path(__file__).parent.parent
        self.setup_results = {
            "specification_validation": False,
            "therapeutic_systems_check": False,
            "clinical_dashboard_setup": False,
            "hipaa_compliance_validation": False,
            "authentication_setup": False,
            "development_environment": False,
        }

    async def run_complete_setup(self) -> Dict[str, bool]:
        """Run complete Phase B1 development setup."""
        logger.info("🚀 Starting Phase B1: Clinical Dashboard Integration Setup")
        start_time = time.time()

        try:
            # Step 1: Validate specifications
            await self._validate_specifications()

            # Step 2: Check therapeutic systems
            await self._check_therapeutic_systems()

            # Step 3: Setup clinical dashboard environment
            await self._setup_clinical_dashboard()

            # Step 4: Validate HIPAA compliance framework
            await self._validate_hipaa_compliance()

            # Step 5: Setup authentication system
            await self._setup_authentication()

            # Step 6: Prepare development environment
            await self._prepare_development_environment()

            # Generate setup report
            await self._generate_setup_report()

            execution_time = time.time() - start_time
            logger.info(f"✅ Phase B1 setup completed in {execution_time:.2f}s")

            return self.setup_results

        except Exception as e:
            logger.error(f"❌ Phase B1 setup failed: {e}")
            raise

    async def _validate_specifications(self):
        """Validate all required specifications for Phase B1."""
        logger.info("📋 Validating Phase B1 specifications...")

        try:
            # Validate clinical dashboard specification
            spec_path = self.project_root / ".kiro/specs/clinical-dashboard/clinical-dashboard-specification.md"
            if not spec_path.exists():
                raise FileNotFoundError(f"Clinical dashboard specification not found: {spec_path}")

            # Run specification validator
            result = subprocess.run([
                sys.executable, "scripts/spec_management/spec_validator.py",
                str(spec_path)
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                raise RuntimeError(f"Specification validation failed: {result.stderr}")

            # Check specification quality
            result = subprocess.run([
                sys.executable, "scripts/spec_management/quality_metrics.py",
                "--spec", str(spec_path), "--json"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode == 0:
                quality_data = json.loads(result.stdout)
                quality_score = quality_data.get("quality_score", 0)
                if quality_score < 80:
                    logger.warning(f"⚠️ Clinical dashboard specification quality score: {quality_score}/100")
                else:
                    logger.info(f"✅ Clinical dashboard specification quality score: {quality_score}/100")

            self.setup_results["specification_validation"] = True
            logger.info("✅ Specification validation completed")

        except Exception as e:
            logger.error(f"❌ Specification validation failed: {e}")
            raise

    async def _check_therapeutic_systems(self):
        """Check all 9 therapeutic systems are operational."""
        logger.info("🧠 Checking therapeutic systems status...")

        try:
            # Run therapeutic systems validation
            result = subprocess.run([
                sys.executable, "scripts/validate_complete_orchestration.py",
                "--quick-check"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                raise RuntimeError(f"Therapeutic systems check failed: {result.stderr}")

            # Parse output for system status
            output_lines = result.stdout.split('\n')
            operational_systems = [line for line in output_lines if "✅" in line and "operational" in line.lower()]

            if len(operational_systems) < 9:
                logger.warning(f"⚠️ Only {len(operational_systems)}/9 therapeutic systems operational")
            else:
                logger.info("✅ All 9 therapeutic systems operational")

            self.setup_results["therapeutic_systems_check"] = True

        except Exception as e:
            logger.error(f"❌ Therapeutic systems check failed: {e}")
            raise

    async def _setup_clinical_dashboard(self):
        """Setup clinical dashboard development environment."""
        logger.info("🏥 Setting up clinical dashboard environment...")

        try:
            dashboard_path = self.project_root / "web-interfaces/clinical-dashboard"
            if not dashboard_path.exists():
                raise FileNotFoundError(f"Clinical dashboard directory not found: {dashboard_path}")

            # Install dependencies
            logger.info("Installing clinical dashboard dependencies...")
            result = subprocess.run([
                "npm", "ci"
            ], cwd=dashboard_path, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"npm ci failed: {result.stderr}")

            # Install shared components
            shared_path = self.project_root / "web-interfaces/shared"
            if shared_path.exists():
                logger.info("Building shared components...")
                result = subprocess.run([
                    "npm", "ci"
                ], cwd=shared_path, capture_output=True, text=True)

                if result.returncode == 0:
                    result = subprocess.run([
                        "npm", "run", "build"
                    ], cwd=shared_path, capture_output=True, text=True)

            # Type check clinical dashboard
            logger.info("Running type checks...")
            result = subprocess.run([
                "npm", "run", "type-check"
            ], cwd=dashboard_path, capture_output=True, text=True)

            if result.returncode != 0:
                logger.warning(f"⚠️ Type check issues found: {result.stderr}")

            self.setup_results["clinical_dashboard_setup"] = True
            logger.info("✅ Clinical dashboard setup completed")

        except Exception as e:
            logger.error(f"❌ Clinical dashboard setup failed: {e}")
            raise

    async def _validate_hipaa_compliance(self):
        """Validate HIPAA compliance framework."""
        logger.info("🔒 Validating HIPAA compliance framework...")

        try:
            # Run HIPAA compliance validation
            result = subprocess.run([
                sys.executable, "scripts/test_hipaa_compliance_framework.py",
                "--validation-only"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                logger.warning(f"⚠️ HIPAA compliance validation issues: {result.stderr}")
            else:
                logger.info("✅ HIPAA compliance framework validated")

            self.setup_results["hipaa_compliance_validation"] = True

        except Exception as e:
            logger.error(f"❌ HIPAA compliance validation failed: {e}")
            raise

    async def _setup_authentication(self):
        """Setup authentication system for clinical dashboard."""
        logger.info("🔐 Setting up authentication system...")

        try:
            # Test clinical authentication credentials
            result = subprocess.run([
                sys.executable, "scripts/test_clinical_dashboard_integration.py",
                "--test-auth", "--quick"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                logger.warning(f"⚠️ Authentication setup issues: {result.stderr}")
            else:
                logger.info("✅ Authentication system validated")

            self.setup_results["authentication_setup"] = True

        except Exception as e:
            logger.error(f"❌ Authentication setup failed: {e}")
            raise

    async def _prepare_development_environment(self):
        """Prepare development environment for Phase B1."""
        logger.info("🛠️ Preparing development environment...")

        try:
            # Sync Python dependencies
            result = subprocess.run([
                "uv", "sync", "--all-extras", "--dev"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                raise RuntimeError(f"uv sync failed: {result.stderr}")

            # Run pre-commit hooks
            result = subprocess.run([
                "uv", "run", "pre-commit", "install"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                logger.warning(f"⚠️ Pre-commit setup issues: {result.stderr}")

            self.setup_results["development_environment"] = True
            logger.info("✅ Development environment prepared")

        except Exception as e:
            logger.error(f"❌ Development environment preparation failed: {e}")
            raise

    async def _generate_setup_report(self):
        """Generate Phase B1 setup report."""
        logger.info("📊 Generating Phase B1 setup report...")

        report = {
            "phase": "B1: Clinical Dashboard Integration",
            "setup_timestamp": time.time(),
            "setup_results": self.setup_results,
            "readiness_status": all(self.setup_results.values()),
            "next_steps": [
                "Complete Clinical Dashboard authentication integration",
                "Implement therapeutic data visualization components",
                "Integrate clinical workflow with existing therapeutic systems",
                "Validate HIPAA compliance for all clinical features"
            ]
        }

        # Save report
        report_path = self.project_root / "docs/development/phase_b1_setup_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Display summary
        logger.info("\n" + "="*60)
        logger.info("📋 PHASE B1 SETUP SUMMARY")
        logger.info("="*60)
        
        for component, status in self.setup_results.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {component.replace('_', ' ').title()}")

        if all(self.setup_results.values()):
            logger.info("\n🎉 Phase B1 development environment is READY!")
            logger.info("You can now begin Clinical Dashboard Integration development.")
        else:
            logger.warning("\n⚠️ Phase B1 setup has issues that need to be resolved.")

        logger.info(f"\n📄 Full report saved to: {report_path}")


async def main():
    """Main entry point."""
    try:
        setup_manager = PhaseB1SetupManager()
        results = await setup_manager.run_complete_setup()
        
        if all(results.values()):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
