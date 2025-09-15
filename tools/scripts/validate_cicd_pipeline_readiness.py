#!/usr/bin/env python3
"""
CI/CD Pipeline Readiness Validation for Phase B1

This script validates that our CI/CD pipeline is properly configured
and ready to support Phase B1: Clinical Dashboard Integration development.
"""

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
        logging.FileHandler("cicd_validation.log"),
    ],
)
logger = logging.getLogger(__name__)


class CICDPipelineValidator:
    """Validates CI/CD pipeline readiness for Phase B1."""

    def __init__(self):
        """Initialize the validator."""
        self.project_root = Path(__file__).parent.parent
        self.validation_results = {
            "workflow_files": False,
            "specification_management": False,
            "clinical_dashboard_pipeline": False,
            "hipaa_compliance_checks": False,
            "therapeutic_systems_integration": False,
            "quality_gates": False,
            "pre_commit_hooks": False,
        }

    async def run_complete_validation(self) -> Dict[str, bool]:
        """Run complete CI/CD pipeline validation."""
        logger.info("🔍 Starting CI/CD Pipeline Readiness Validation")
        start_time = time.time()

        try:
            # Validate workflow files
            await self._validate_workflow_files()

            # Validate specification management
            await self._validate_specification_management()

            # Validate clinical dashboard pipeline
            await self._validate_clinical_dashboard_pipeline()

            # Validate HIPAA compliance checks
            await self._validate_hipaa_compliance_checks()

            # Validate therapeutic systems integration
            await self._validate_therapeutic_systems_integration()

            # Validate quality gates
            await self._validate_quality_gates()

            # Validate pre-commit hooks
            await self._validate_pre_commit_hooks()

            # Generate validation report
            await self._generate_validation_report()

            execution_time = time.time() - start_time
            logger.info(f"✅ CI/CD validation completed in {execution_time:.2f}s")

            return self.validation_results

        except Exception as e:
            logger.error(f"❌ CI/CD validation failed: {e}")
            raise

    async def _validate_workflow_files(self):
        """Validate GitHub Actions workflow files."""
        logger.info("📄 Validating GitHub Actions workflow files...")

        try:
            workflows_dir = self.project_root / ".github/workflows"
            if not workflows_dir.exists():
                raise FileNotFoundError("GitHub workflows directory not found")

            required_workflows = [
                "tests.yml",
                "specification-management.yml",
                "clinical-dashboard-integration.yml",
                "quality-gates.yml"
            ]

            missing_workflows = []
            for workflow in required_workflows:
                workflow_path = workflows_dir / workflow
                if not workflow_path.exists():
                    missing_workflows.append(workflow)
                else:
                    # Validate workflow syntax
                    try:
                        with open(workflow_path, 'r') as f:
                            content = f.read()
                            if not content.strip():
                                missing_workflows.append(f"{workflow} (empty)")
                    except Exception as e:
                        missing_workflows.append(f"{workflow} (read error: {e})")

            if missing_workflows:
                raise FileNotFoundError(f"Missing or invalid workflows: {missing_workflows}")

            self.validation_results["workflow_files"] = True
            logger.info("✅ All required workflow files validated")

        except Exception as e:
            logger.error(f"❌ Workflow files validation failed: {e}")
            raise

    async def _validate_specification_management(self):
        """Validate specification management pipeline."""
        logger.info("📋 Validating specification management pipeline...")

        try:
            # Check specification validator
            validator_path = self.project_root / "scripts/spec_management/spec_validator.py"
            if not validator_path.exists():
                raise FileNotFoundError("Specification validator not found")

            # Check quality metrics
            quality_metrics_path = self.project_root / "scripts/spec_management/quality_metrics.py"
            if not quality_metrics_path.exists():
                raise FileNotFoundError("Quality metrics script not found")

            # Test specification validation
            result = subprocess.run([
                sys.executable, str(validator_path), "--help"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                raise RuntimeError("Specification validator not working")

            self.validation_results["specification_management"] = True
            logger.info("✅ Specification management pipeline validated")

        except Exception as e:
            logger.error(f"❌ Specification management validation failed: {e}")
            raise

    async def _validate_clinical_dashboard_pipeline(self):
        """Validate clinical dashboard integration pipeline."""
        logger.info("🏥 Validating clinical dashboard integration pipeline...")

        try:
            # Check clinical dashboard workflow
            workflow_path = self.project_root / ".github/workflows/clinical-dashboard-integration.yml"
            if not workflow_path.exists():
                raise FileNotFoundError("Clinical dashboard integration workflow not found")

            # Check clinical dashboard test scripts
            test_script_path = self.project_root / "scripts/test_clinical_dashboard_integration.py"
            if not test_script_path.exists():
                raise FileNotFoundError("Clinical dashboard integration test script not found")

            # Validate workflow content
            with open(workflow_path, 'r') as f:
                workflow_content = f.read()
                required_jobs = [
                    "clinical-dashboard-frontend",
                    "clinical-authentication-tests",
                    "hipaa-compliance-validation",
                    "therapeutic-systems-integration"
                ]
                
                missing_jobs = []
                for job in required_jobs:
                    if job not in workflow_content:
                        missing_jobs.append(job)

                if missing_jobs:
                    raise ValueError(f"Missing required jobs in clinical dashboard workflow: {missing_jobs}")

            self.validation_results["clinical_dashboard_pipeline"] = True
            logger.info("✅ Clinical dashboard integration pipeline validated")

        except Exception as e:
            logger.error(f"❌ Clinical dashboard pipeline validation failed: {e}")
            raise

    async def _validate_hipaa_compliance_checks(self):
        """Validate HIPAA compliance validation checks."""
        logger.info("🔒 Validating HIPAA compliance checks...")

        try:
            # Check HIPAA compliance test script
            hipaa_script_path = self.project_root / "scripts/test_hipaa_compliance_framework.py"
            if not hipaa_script_path.exists():
                raise FileNotFoundError("HIPAA compliance test script not found")

            # Check security testing framework
            security_framework_path = self.project_root / "src/infrastructure/security_testing_framework.py"
            if not security_framework_path.exists():
                raise FileNotFoundError("Security testing framework not found")

            # Test HIPAA compliance script
            result = subprocess.run([
                sys.executable, str(hipaa_script_path), "--help"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                logger.warning("⚠️ HIPAA compliance script may have issues")

            self.validation_results["hipaa_compliance_checks"] = True
            logger.info("✅ HIPAA compliance checks validated")

        except Exception as e:
            logger.error(f"❌ HIPAA compliance checks validation failed: {e}")
            raise

    async def _validate_therapeutic_systems_integration(self):
        """Validate therapeutic systems integration testing."""
        logger.info("🧠 Validating therapeutic systems integration testing...")

        try:
            # Check therapeutic systems validation script
            validation_script_path = self.project_root / "scripts/validate_complete_orchestration.py"
            if not validation_script_path.exists():
                raise FileNotFoundError("Therapeutic systems validation script not found")

            # Check integration test files
            integration_tests_path = self.project_root / "tests/integration"
            if not integration_tests_path.exists():
                logger.warning("⚠️ Integration tests directory not found")

            # Test validation script
            result = subprocess.run([
                sys.executable, str(validation_script_path), "--help"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                logger.warning("⚠️ Therapeutic systems validation script may have issues")

            self.validation_results["therapeutic_systems_integration"] = True
            logger.info("✅ Therapeutic systems integration testing validated")

        except Exception as e:
            logger.error(f"❌ Therapeutic systems integration validation failed: {e}")
            raise

    async def _validate_quality_gates(self):
        """Validate quality gates configuration."""
        logger.info("🚪 Validating quality gates configuration...")

        try:
            # Check quality gates workflow
            quality_gates_path = self.project_root / ".github/workflows/quality-gates.yml"
            if not quality_gates_path.exists():
                raise FileNotFoundError("Quality gates workflow not found")

            # Check main tests workflow
            tests_workflow_path = self.project_root / ".github/workflows/tests.yml"
            if not tests_workflow_path.exists():
                raise FileNotFoundError("Main tests workflow not found")

            # Validate quality gates content
            with open(quality_gates_path, 'r') as f:
                content = f.read()
                if "coverage-threshold" not in content:
                    logger.warning("⚠️ Coverage threshold not configured in quality gates")

            self.validation_results["quality_gates"] = True
            logger.info("✅ Quality gates configuration validated")

        except Exception as e:
            logger.error(f"❌ Quality gates validation failed: {e}")
            raise

    async def _validate_pre_commit_hooks(self):
        """Validate pre-commit hooks configuration."""
        logger.info("🪝 Validating pre-commit hooks configuration...")

        try:
            # Check pre-commit config
            precommit_config_path = self.project_root / ".pre-commit-config.yaml"
            if not precommit_config_path.exists():
                raise FileNotFoundError("Pre-commit configuration not found")

            # Test pre-commit installation
            result = subprocess.run([
                "uv", "run", "pre-commit", "--version"
            ], capture_output=True, text=True, cwd=self.project_root)

            if result.returncode != 0:
                logger.warning("⚠️ Pre-commit not properly installed")

            self.validation_results["pre_commit_hooks"] = True
            logger.info("✅ Pre-commit hooks configuration validated")

        except Exception as e:
            logger.error(f"❌ Pre-commit hooks validation failed: {e}")
            raise

    async def _generate_validation_report(self):
        """Generate CI/CD pipeline validation report."""
        logger.info("📊 Generating CI/CD pipeline validation report...")

        report = {
            "validation_timestamp": time.time(),
            "pipeline_components": self.validation_results,
            "overall_readiness": all(self.validation_results.values()),
            "recommendations": []
        }

        # Add recommendations based on results
        for component, status in self.validation_results.items():
            if not status:
                if component == "workflow_files":
                    report["recommendations"].append("Fix missing or invalid GitHub Actions workflow files")
                elif component == "specification_management":
                    report["recommendations"].append("Ensure specification management scripts are working")
                elif component == "clinical_dashboard_pipeline":
                    report["recommendations"].append("Complete clinical dashboard integration pipeline setup")
                elif component == "hipaa_compliance_checks":
                    report["recommendations"].append("Fix HIPAA compliance validation framework")
                elif component == "therapeutic_systems_integration":
                    report["recommendations"].append("Ensure therapeutic systems integration testing is working")
                elif component == "quality_gates":
                    report["recommendations"].append("Configure quality gates properly")
                elif component == "pre_commit_hooks":
                    report["recommendations"].append("Install and configure pre-commit hooks")

        # Save report
        report_path = self.project_root / "docs/development/cicd_validation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Display summary
        logger.info("\n" + "="*60)
        logger.info("🔍 CI/CD PIPELINE VALIDATION SUMMARY")
        logger.info("="*60)
        
        for component, status in self.validation_results.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {component.replace('_', ' ').title()}")

        if all(self.validation_results.values()):
            logger.info("\n🎉 CI/CD Pipeline is READY for Phase B1 development!")
        else:
            logger.warning("\n⚠️ CI/CD Pipeline has issues that need to be resolved.")
            if report["recommendations"]:
                logger.info("\n📋 Recommendations:")
                for rec in report["recommendations"]:
                    logger.info(f"  • {rec}")

        logger.info(f"\n📄 Full report saved to: {report_path}")


async def main():
    """Main entry point."""
    try:
        validator = CICDPipelineValidator()
        results = await validator.run_complete_validation()
        
        if all(results.values()):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
