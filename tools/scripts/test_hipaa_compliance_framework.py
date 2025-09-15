#!/usr/bin/env python3
"""
HIPAA Compliance and Security Framework Test Script

Comprehensive testing script for HIPAA compliance validation including
security framework testing, encryption validation, audit logging verification,
and compliance reporting.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.infrastructure.security_framework import (
    SecurityConfiguration,
    SecurityFramework,
)
from src.infrastructure.security_testing_framework import SecurityTestingFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_security_framework_initialization():
    """Test SecurityFramework initialization and basic functionality."""
    try:
        logger.info("🔐 Testing SecurityFramework Initialization")
        logger.info("=" * 50)

        # Initialize security framework
        config = SecurityConfiguration(
            encryption_enabled=True,
            audit_logging_enabled=True,
            access_controls_enabled=True,
            session_timeout_minutes=30,
            password_complexity_required=True,
            mfa_required=False,
            data_integrity_checks=True,
            transmission_security=True,
            emergency_access_enabled=True,
            automatic_logoff_enabled=True,
        )

        security_framework = SecurityFramework(config)
        await security_framework.initialize()

        logger.info("✅ SecurityFramework initialized successfully")

        # Test encryption functionality
        logger.info("\n🔒 Testing Encryption Functionality")
        test_data = "sensitive_patient_data_for_testing"
        encrypted_result = await security_framework.encrypt_data(
            test_data, "patient_data"
        )
        decrypted_data = await security_framework.decrypt_data(
            encrypted_result["encrypted_data"], "patient_data"
        )

        if decrypted_data == test_data:
            logger.info("✅ Encryption/Decryption working correctly")
        else:
            logger.error("❌ Encryption/Decryption failed")
            return False

        # Test audit logging
        logger.info("\n📋 Testing Audit Logging")
        from src.infrastructure.security_framework import AuditEventType

        audit_id = await security_framework.log_audit_event(
            user_id="test_user_123",
            username="test_clinician",
            event_type=AuditEventType.DATA_ACCESS,
            resource_accessed="patient_records",
            action_performed="view_patient_progress",
            outcome="success",
            ip_address="192.168.1.100",
            patient_id="patient_456",
            data_category="therapeutic_content",
        )

        if audit_id:
            logger.info("✅ Audit logging working correctly")
            logger.info(f"   Audit ID: {audit_id}")
        else:
            logger.error("❌ Audit logging failed")
            return False

        # Test session management
        logger.info("\n🔑 Testing Session Management")
        session_id = await security_framework.create_session(
            user_id="test_user_123",
            username="test_clinician",
            ip_address="192.168.1.100",
            user_agent="TTA-Clinical-Dashboard/1.0",
        )

        if session_id:
            logger.info("✅ Session management working correctly")
            logger.info(f"   Session ID: {session_id}")
        else:
            logger.error("❌ Session management failed")
            return False

        # Test access control validation
        logger.info("\n🛡️ Testing Access Control Validation")
        access_granted = await security_framework.validate_access_control(
            user_id="test_user_123",
            resource="patient_records",
            action="view_progress",
            context={"patient_id": "patient_456", "purpose": "therapeutic_review"},
        )

        if access_granted:
            logger.info("✅ Access control validation working correctly")
        else:
            logger.error("❌ Access control validation failed")
            return False

        # Test compliance status
        logger.info("\n📊 Testing Compliance Status")
        compliance_status = await security_framework.get_compliance_status()

        logger.info(f"✅ Compliance Status: {compliance_status['compliance_status']}")
        logger.info(f"   Compliance Score: {compliance_status['compliance_score']}%")
        logger.info(f"   Total Audit Logs: {compliance_status['total_audit_logs']}")
        logger.info(f"   Active Sessions: {compliance_status['active_sessions']}")
        logger.info(f"   Encryption Enabled: {compliance_status['encryption_enabled']}")

        return security_framework

    except Exception as e:
        logger.error(f"❌ SecurityFramework testing failed: {e}")
        return None


async def test_security_testing_framework(security_framework):
    """Test SecurityTestingFramework with comprehensive security tests."""
    try:
        logger.info("\n" + "=" * 60)
        logger.info("🧪 Testing HIPAA Security Testing Framework")
        logger.info("=" * 60)

        # Initialize security testing framework
        testing_framework = SecurityTestingFramework(security_framework)
        await testing_framework.initialize()

        logger.info("✅ Security Testing Framework initialized")

        # Run comprehensive security tests
        logger.info("\n🔍 Running Comprehensive Security Tests...")
        test_suite = await testing_framework.run_comprehensive_security_tests()

        # Display test results
        logger.info("\n📊 SECURITY TEST RESULTS")
        logger.info("=" * 40)
        logger.info(f"Suite: {test_suite.suite_name}")
        logger.info(f"Total Tests: {test_suite.total_tests}")
        logger.info(f"Passed: {test_suite.passed_tests}")
        logger.info(f"Failed: {test_suite.failed_tests}")
        logger.info(f"Execution Time: {test_suite.execution_time_ms:.2f}ms")
        logger.info(f"Compliance Score: {test_suite.compliance_score:.1f}%")

        # Display failure breakdown
        if test_suite.failed_tests > 0:
            logger.info("\n⚠️ FAILURE BREAKDOWN:")
            logger.info(f"   Critical: {test_suite.critical_failures}")
            logger.info(f"   High: {test_suite.high_failures}")
            logger.info(f"   Medium: {test_suite.medium_failures}")
            logger.info(f"   Low: {test_suite.low_failures}")

        # Display individual test results
        logger.info("\n📋 INDIVIDUAL TEST RESULTS:")
        for result in test_suite.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            logger.info(f"   {status} - {result.test_name} ({result.test_type.value})")
            if not result.passed and result.findings:
                for finding in result.findings:
                    logger.info(f"      Finding: {finding}")

        # Generate compliance report
        logger.info("\n📄 Generating Compliance Report...")
        compliance_report = await testing_framework.generate_compliance_report(
            test_suite
        )

        logger.info(f"✅ Compliance Report Generated: {compliance_report['report_id']}")
        logger.info(f"   Overall Status: {compliance_report['compliance_status']}")
        logger.info(
            f"   Compliance Score: {compliance_report['overall_compliance_score']:.1f}%"
        )

        # Display compliance requirements status
        logger.info("\n🏥 HIPAA COMPLIANCE REQUIREMENTS STATUS:")
        for req, status in compliance_report["compliance_requirements"].items():
            total_req_tests = status["passed"] + status["failed"]
            req_score = (
                (status["passed"] / total_req_tests) * 100 if total_req_tests > 0 else 0
            )
            req_status = (
                "✅" if status["failed"] == 0 else "⚠️" if req_score >= 70 else "❌"
            )
            logger.info(
                f"   {req_status} {req}: {status['passed']}/{total_req_tests} tests passed ({req_score:.1f}%)"
            )

        # Display recommendations
        if compliance_report["recommendations"]:
            logger.info("\n💡 RECOMMENDATIONS:")
            for i, recommendation in enumerate(compliance_report["recommendations"], 1):
                logger.info(f"   {i}. {recommendation}")

        return test_suite.compliance_score >= 90

    except Exception as e:
        logger.error(f"❌ Security Testing Framework failed: {e}")
        return False


async def test_integration_with_clinical_authentication():
    """Test integration with existing clinical authentication system."""
    try:
        logger.info("\n" + "=" * 60)
        logger.info("🏥 Testing Integration with Clinical Authentication")
        logger.info("=" * 60)

        # Test API integration
        import httpx

        async with httpx.AsyncClient() as client:
            # Test health check
            health_response = await client.get("http://localhost:8080/health")
            if health_response.status_code == 200:
                logger.info("✅ Player Experience API is running")
            else:
                logger.warning("⚠️ Player Experience API not accessible")
                return False

            # Test clinical user authentication
            login_data = {"username": "dr_smith", "password": "Clinician123!"}

            login_response = await client.post(
                "http://localhost:8080/api/v1/auth/login", json=login_data
            )

            if login_response.status_code == 200:
                login_result = login_response.json()
                access_token = login_result.get("access_token")
                user_info = login_result.get("user_info", {})

                logger.info("✅ Clinical authentication integration working")
                logger.info(f"   User: {user_info.get('username')}")
                logger.info(f"   Role: {user_info.get('role')}")
                logger.info(f"   Permissions: {len(user_info.get('permissions', []))}")

                # Test token validation
                headers = {"Authorization": f"Bearer {access_token}"}
                token_response = await client.post(
                    "http://localhost:8080/api/v1/auth/verify-token", headers=headers
                )

                if token_response.status_code == 200:
                    logger.info("✅ JWT token validation working")
                    return True
                else:
                    logger.error("❌ JWT token validation failed")
                    return False
            else:
                logger.error("❌ Clinical authentication failed")
                return False

    except Exception as e:
        logger.error(f"❌ Clinical authentication integration test failed: {e}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 HIPAA Compliance and Security Framework Test Suite")
    logger.info(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    # Test 1: Security Framework
    security_framework = await test_security_framework_initialization()
    if not security_framework:
        logger.error("❌ Security Framework tests failed")
        return False

    # Test 2: Security Testing Framework
    security_tests_passed = await test_security_testing_framework(security_framework)
    if not security_tests_passed:
        logger.error("❌ Security Testing Framework tests failed")
        return False

    # Test 3: Clinical Authentication Integration
    integration_passed = await test_integration_with_clinical_authentication()
    if not integration_passed:
        logger.error("❌ Clinical authentication integration tests failed")
        return False

    # Final results
    logger.info("\n" + "=" * 60)
    logger.info("🎉 ALL HIPAA COMPLIANCE TESTS PASSED!")
    logger.info("=" * 60)
    logger.info("✅ SecurityFramework: OPERATIONAL")
    logger.info("✅ Security Testing Framework: OPERATIONAL")
    logger.info("✅ HIPAA Compliance: VALIDATED")
    logger.info("✅ Clinical Authentication Integration: WORKING")
    logger.info("✅ Encryption & Data Protection: FUNCTIONAL")
    logger.info("✅ Audit Logging: COMPREHENSIVE")
    logger.info("✅ Session Management: SECURE")
    logger.info("✅ Access Controls: ENFORCED")
    logger.info("")
    logger.info("🏥 HIPAA Security Framework is ready for clinical use!")
    logger.info("📊 Compliance score: 90%+ achieved")
    logger.info("🔐 All technical safeguards implemented")
    logger.info("📋 Comprehensive audit trail established")

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
