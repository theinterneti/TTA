"""

# Logseq: [[TTA.dev/Player_experience/Production_readiness]]
Production readiness validation and optimization system.

This module provides comprehensive production readiness checks including
performance validation, security assessment, monitoring setup, and
deployment verification.
"""

import asyncio
import contextlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp
import psutil

from .monitoring.benchmarking import BenchmarkSuite, LoadTester, PerformanceBenchmark
from .monitoring.logging_config import get_logger, setup_logging
from .monitoring.metrics_collector import get_metrics_collector
from .monitoring.performance_monitor import get_performance_monitor
from .security.input_validator import get_security_validator

logger = get_logger(__name__)


class ReadinessLevel(str, Enum):
    """Production readiness levels."""

    NOT_READY = "not_ready"
    BASIC = "basic"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class CheckCategory(str, Enum):
    """Categories of readiness checks."""

    PERFORMANCE = "performance"
    SECURITY = "security"
    MONITORING = "monitoring"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    COMPLIANCE = "compliance"


@dataclass
class ReadinessCheck:
    """Individual readiness check."""

    name: str
    category: CheckCategory
    description: str
    required_level: ReadinessLevel
    passed: bool = False
    score: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass
class ReadinessReport:
    """Comprehensive readiness assessment report."""

    timestamp: datetime
    overall_level: ReadinessLevel
    overall_score: float
    checks: list[ReadinessCheck] = field(default_factory=list)
    category_scores: dict[CheckCategory, float] = field(default_factory=dict)
    critical_issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_level": self.overall_level.value,
            "overall_score": self.overall_score,
            "category_scores": {k.value: v for k, v in self.category_scores.items()},
            "critical_issues": self.critical_issues,
            "recommendations": self.recommendations,
            "checks": [
                {
                    "name": check.name,
                    "category": check.category.value,
                    "description": check.description,
                    "required_level": check.required_level.value,
                    "passed": check.passed,
                    "score": check.score,
                    "details": check.details,
                    "recommendations": check.recommendations,
                    "execution_time": check.execution_time,
                }
                for check in self.checks
            ],
        }


class ProductionReadinessValidator:
    """Comprehensive production readiness validation system."""

    def __init__(
        self, base_url: str = "http://localhost:8080", config_path: str | None = None
    ):
        self.base_url = base_url
        self.config_path = config_path
        self.checks: list[ReadinessCheck] = []

        # Initialize components
        self.performance_monitor = get_performance_monitor()
        self.metrics_collector = get_metrics_collector()
        self.security_validator = get_security_validator()

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration for readiness checks."""
        default_config = {
            "performance": {
                "max_response_time": 2.0,
                "min_throughput": 100.0,
                "max_error_rate": 1.0,
                "max_cpu_usage": 80.0,
                "max_memory_usage": 80.0,
            },
            "security": {
                "require_https": True,
                "require_rate_limiting": True,
                "require_input_validation": True,
                "require_audit_logging": True,
            },
            "monitoring": {
                "require_metrics": True,
                "require_logging": True,
                "require_alerting": True,
                "require_health_checks": True,
            },
            "deployment": {
                "require_docker": True,
                "require_k8s_manifests": True,
                "require_env_configs": True,
                "require_backup_strategy": True,
            },
        }

        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path) as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for category, settings in user_config.items():
                        if category in default_config:
                            default_config[category].update(settings)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")

        return default_config

    async def run_comprehensive_assessment(self) -> ReadinessReport:
        """Run comprehensive production readiness assessment."""
        logger.info("Starting comprehensive production readiness assessment")

        start_time = datetime.utcnow()
        self.checks = []

        # Run all check categories
        await self._run_performance_checks()
        await self._run_security_checks()
        await self._run_monitoring_checks()
        await self._run_deployment_checks()
        await self._run_documentation_checks()
        await self._run_compliance_checks()

        # Generate report
        report = self._generate_report()

        # Save report
        await self._save_report(report)

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Production readiness assessment completed in {execution_time:.2f}s"
        )
        logger.info(f"Overall readiness level: {report.overall_level.value}")
        logger.info(f"Overall score: {report.overall_score:.1f}/100")

        return report

    async def _run_performance_checks(self):
        """Run performance-related readiness checks."""
        logger.info("Running performance checks...")

        # Check 1: API Response Time
        check = ReadinessCheck(
            name="API Response Time",
            category=CheckCategory.PERFORMANCE,
            description="Verify API endpoints respond within acceptable time limits",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            response_times = await self._measure_api_response_times()
            avg_response_time = (
                sum(response_times) / len(response_times)
                if response_times
                else float("inf")
            )
            max_allowed = self.config["performance"]["max_response_time"]

            check.passed = avg_response_time <= max_allowed
            check.score = max(0, 100 - (avg_response_time / max_allowed) * 50)
            check.details = {
                "average_response_time": avg_response_time,
                "max_allowed": max_allowed,
                "sample_count": len(response_times),
                "response_times": response_times[:10],  # First 10 samples
            }

            if not check.passed:
                check.recommendations.append(
                    f"Optimize API endpoints to respond within {max_allowed}s"
                )
                check.recommendations.append("Consider implementing caching strategies")
                check.recommendations.append("Review database query performance")

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}
            check.recommendations.append("Fix API connectivity issues")

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 2: Load Testing
        check = ReadinessCheck(
            name="Load Testing",
            category=CheckCategory.PERFORMANCE,
            description="Verify system can handle expected load",
            required_level=ReadinessLevel.PRODUCTION,
        )

        start_time = time.time()
        try:
            load_test_results = await self._run_load_test()
            min_throughput = self.config["performance"]["min_throughput"]
            max_error_rate = self.config["performance"]["max_error_rate"]

            throughput_ok = load_test_results["throughput"] >= min_throughput
            error_rate_ok = load_test_results["error_rate"] <= max_error_rate

            check.passed = throughput_ok and error_rate_ok
            check.score = (50 if throughput_ok else 0) + (50 if error_rate_ok else 0)
            check.details = load_test_results

            if not throughput_ok:
                check.recommendations.append(
                    f"Improve throughput to at least {min_throughput} RPS"
                )
            if not error_rate_ok:
                check.recommendations.append(
                    f"Reduce error rate to below {max_error_rate}%"
                )

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}
            check.recommendations.append("Set up proper load testing infrastructure")

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 3: Resource Usage
        check = ReadinessCheck(
            name="Resource Usage",
            category=CheckCategory.PERFORMANCE,
            description="Verify system resource usage is within acceptable limits",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            resource_usage = self._measure_resource_usage()
            max_cpu = self.config["performance"]["max_cpu_usage"]
            max_memory = self.config["performance"]["max_memory_usage"]

            cpu_ok = resource_usage["cpu_percent"] <= max_cpu
            memory_ok = resource_usage["memory_percent"] <= max_memory

            check.passed = cpu_ok and memory_ok
            check.score = (
                50 if cpu_ok else max(0, 50 - (resource_usage["cpu_percent"] - max_cpu))
            ) + (
                50
                if memory_ok
                else max(0, 50 - (resource_usage["memory_percent"] - max_memory))
            )
            check.details = resource_usage

            if not cpu_ok:
                check.recommendations.append(f"Optimize CPU usage to below {max_cpu}%")
            if not memory_ok:
                check.recommendations.append(
                    f"Optimize memory usage to below {max_memory}%"
                )

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

    async def _run_security_checks(self):
        """Run security-related readiness checks."""
        logger.info("Running security checks...")

        # Check 1: HTTPS Configuration
        check = ReadinessCheck(
            name="HTTPS Configuration",
            category=CheckCategory.SECURITY,
            description="Verify HTTPS is properly configured",
            required_level=ReadinessLevel.PRODUCTION,
        )

        start_time = time.time()
        try:
            https_status = await self._check_https_configuration()
            check.passed = https_status["enabled"]
            check.score = 100 if check.passed else 0
            check.details = https_status

            if not check.passed:
                check.recommendations.append(
                    "Configure HTTPS with valid SSL certificates"
                )
                check.recommendations.append("Redirect HTTP traffic to HTTPS")
                check.recommendations.append("Implement HSTS headers")

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 2: Rate Limiting
        check = ReadinessCheck(
            name="Rate Limiting",
            category=CheckCategory.SECURITY,
            description="Verify rate limiting is implemented",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            rate_limit_status = await self._check_rate_limiting()
            check.passed = rate_limit_status["enabled"]
            check.score = 100 if check.passed else 0
            check.details = rate_limit_status

            if not check.passed:
                check.recommendations.append("Implement rate limiting middleware")
                check.recommendations.append(
                    "Configure appropriate rate limits per endpoint"
                )
                check.recommendations.append("Add rate limit headers to responses")

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 3: Input Validation
        check = ReadinessCheck(
            name="Input Validation",
            category=CheckCategory.SECURITY,
            description="Verify comprehensive input validation is implemented",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            validation_status = await self._check_input_validation()
            check.passed = validation_status["comprehensive"]
            check.score = validation_status["score"]
            check.details = validation_status

            if not check.passed:
                check.recommendations.extend(
                    validation_status.get("recommendations", [])
                )

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 4: Vulnerability Scan
        check = ReadinessCheck(
            name="Vulnerability Scan",
            category=CheckCategory.SECURITY,
            description="Run automated vulnerability scanning",
            required_level=ReadinessLevel.PRODUCTION,
        )

        start_time = time.time()
        try:
            vuln_results = await self._run_vulnerability_scan()
            critical_vulns = vuln_results.get("critical", 0)
            high_vulns = vuln_results.get("high", 0)

            check.passed = critical_vulns == 0 and high_vulns == 0
            check.score = max(0, 100 - (critical_vulns * 50) - (high_vulns * 20))
            check.details = vuln_results

            if critical_vulns > 0:
                check.recommendations.append(
                    f"Fix {critical_vulns} critical vulnerabilities"
                )
            if high_vulns > 0:
                check.recommendations.append(
                    f"Fix {high_vulns} high-severity vulnerabilities"
                )

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

    async def _run_monitoring_checks(self):
        """Run monitoring-related readiness checks."""
        logger.info("Running monitoring checks...")

        # Check 1: Metrics Collection
        check = ReadinessCheck(
            name="Metrics Collection",
            category=CheckCategory.MONITORING,
            description="Verify comprehensive metrics are being collected",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            metrics_status = self._check_metrics_collection()
            check.passed = metrics_status["enabled"]
            check.score = metrics_status["score"]
            check.details = metrics_status

            if not check.passed:
                check.recommendations.extend(metrics_status.get("recommendations", []))

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 2: Structured Logging
        check = ReadinessCheck(
            name="Structured Logging",
            category=CheckCategory.MONITORING,
            description="Verify structured logging is properly configured",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            logging_status = self._check_logging_configuration()
            check.passed = logging_status["structured"]
            check.score = logging_status["score"]
            check.details = logging_status

            if not check.passed:
                check.recommendations.extend(logging_status.get("recommendations", []))

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 3: Health Checks
        check = ReadinessCheck(
            name="Health Checks",
            category=CheckCategory.MONITORING,
            description="Verify health check endpoints are available",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            health_status = await self._check_health_endpoints()
            check.passed = health_status["available"]
            check.score = 100 if check.passed else 0
            check.details = health_status

            if not check.passed:
                check.recommendations.append(
                    "Implement comprehensive health check endpoints"
                )
                check.recommendations.append("Include dependency health checks")

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

    async def _run_deployment_checks(self):
        """Run deployment-related readiness checks."""
        logger.info("Running deployment checks...")

        # Check 1: Docker Configuration
        check = ReadinessCheck(
            name="Docker Configuration",
            category=CheckCategory.DEPLOYMENT,
            description="Verify Docker configuration is production-ready",
            required_level=ReadinessLevel.PRODUCTION,
        )

        start_time = time.time()
        try:
            docker_status = self._check_docker_configuration()
            check.passed = docker_status["production_ready"]
            check.score = docker_status["score"]
            check.details = docker_status

            if not check.passed:
                check.recommendations.extend(docker_status.get("recommendations", []))

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 2: Environment Configuration
        check = ReadinessCheck(
            name="Environment Configuration",
            category=CheckCategory.DEPLOYMENT,
            description="Verify environment-specific configurations exist",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            env_status = self._check_environment_configuration()
            check.passed = env_status["complete"]
            check.score = env_status["score"]
            check.details = env_status

            if not check.passed:
                check.recommendations.extend(env_status.get("recommendations", []))

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

    async def _run_documentation_checks(self):
        """Run documentation-related readiness checks."""
        logger.info("Running documentation checks...")

        # Check 1: API Documentation
        check = ReadinessCheck(
            name="API Documentation",
            category=CheckCategory.DOCUMENTATION,
            description="Verify comprehensive API documentation exists",
            required_level=ReadinessLevel.BASIC,
        )

        start_time = time.time()
        try:
            api_docs_status = self._check_api_documentation()
            check.passed = api_docs_status["complete"]
            check.score = api_docs_status["score"]
            check.details = api_docs_status

            if not check.passed:
                check.recommendations.extend(api_docs_status.get("recommendations", []))

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

        # Check 2: Deployment Guide
        check = ReadinessCheck(
            name="Deployment Guide",
            category=CheckCategory.DOCUMENTATION,
            description="Verify deployment and operations documentation exists",
            required_level=ReadinessLevel.PRODUCTION,
        )

        start_time = time.time()
        try:
            deploy_docs_status = self._check_deployment_documentation()
            check.passed = deploy_docs_status["complete"]
            check.score = deploy_docs_status["score"]
            check.details = deploy_docs_status

            if not check.passed:
                check.recommendations.extend(
                    deploy_docs_status.get("recommendations", [])
                )

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

    async def _run_compliance_checks(self):
        """Run compliance-related readiness checks."""
        logger.info("Running compliance checks...")

        # Check 1: GDPR Compliance
        check = ReadinessCheck(
            name="GDPR Compliance",
            category=CheckCategory.COMPLIANCE,
            description="Verify GDPR compliance features are implemented",
            required_level=ReadinessLevel.PRODUCTION,
        )

        start_time = time.time()
        try:
            gdpr_status = self._check_gdpr_compliance()
            check.passed = gdpr_status["compliant"]
            check.score = gdpr_status["score"]
            check.details = gdpr_status

            if not check.passed:
                check.recommendations.extend(gdpr_status.get("recommendations", []))

        except Exception as e:
            check.passed = False
            check.score = 0
            check.details = {"error": str(e)}

        check.execution_time = time.time() - start_time
        self.checks.append(check)

    # Helper methods for individual checks

    async def _measure_api_response_times(self) -> list[float]:
        """Measure API response times for key endpoints."""
        endpoints = [
            "/health",
            "/api/v1/players/",
            "/api/v1/characters/",
            "/api/v1/worlds/",
        ]
        response_times = []

        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        await response.text()
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                except Exception as e:
                    logger.warning(
                        f"Failed to measure response time for {endpoint}: {e}"
                    )

        return response_times

    async def _run_load_test(self) -> dict[str, Any]:
        """Run a basic load test."""
        try:
            PerformanceBenchmark(self.base_url)

            # Run a lightweight load test
            config = LoadTester.create_load_test(
                self.base_url, concurrent_users=5, duration=30
            )
            suite = BenchmarkSuite(self.base_url)
            suite.add_benchmark(config)

            results = await suite.run_all()

            if results:
                result = results[0]
                return {
                    "throughput": result.throughput,
                    "error_rate": result.error_rate,
                    "avg_response_time": result.average_response_time,
                    "p95_response_time": result.p95_response_time,
                    "total_requests": result.total_requests,
                    "successful_requests": result.successful_requests,
                }
            return {"error": "No load test results"}

        except Exception as e:
            return {"error": str(e)}

    def _measure_resource_usage(self) -> dict[str, Any]:
        """Measure current system resource usage."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "load_average": (
                psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0]
            ),
            "process_count": len(psutil.pids()),
        }

    async def _check_https_configuration(self) -> dict[str, Any]:
        """Check HTTPS configuration."""
        try:
            https_url = self.base_url.replace("http://", "https://")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{https_url}/health") as response:
                    ssl_info = "N/A"
                    if response.connection and response.connection.transport:
                        ssl_info = str(
                            response.connection.transport.get_extra_info("ssl_object")
                        )
                    return {
                        "enabled": True,
                        "status_code": response.status,
                        "ssl_info": ssl_info,
                    }
        except Exception as e:
            return {"enabled": False, "error": str(e)}

    async def _check_rate_limiting(self) -> dict[str, Any]:
        """Check if rate limiting is implemented."""
        try:
            # Make multiple rapid requests to test rate limiting
            async with aiohttp.ClientSession() as session:
                responses = []
                for _ in range(20):  # Make 20 rapid requests
                    with contextlib.suppress(Exception):
                        async with session.get(f"{self.base_url}/health") as response:
                            responses.append(
                                {
                                    "status": response.status,
                                    "headers": dict(response.headers),
                                }
                            )

                # Check for rate limit headers or 429 responses
                has_rate_limit_headers = any(
                    "x-ratelimit-limit" in resp.get("headers", {})
                    or "x-ratelimit-remaining" in resp.get("headers", {})
                    for resp in responses
                )

                has_429_responses = any(resp.get("status") == 429 for resp in responses)

                return {
                    "enabled": has_rate_limit_headers or has_429_responses,
                    "has_headers": has_rate_limit_headers,
                    "has_429_responses": has_429_responses,
                    "sample_responses": responses[:5],
                }

        except Exception as e:
            return {"enabled": False, "error": str(e)}

    async def _check_input_validation(self) -> dict[str, Any]:
        """Check input validation implementation."""
        try:
            # Test various malicious inputs
            test_inputs = [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "../../../etc/passwd",
                "javascript:alert('xss')",
            ]

            validation_results = []

            async with aiohttp.ClientSession() as session:
                for test_input in test_inputs:
                    try:
                        # Test on a POST endpoint
                        data = {"test_field": test_input}
                        async with session.post(
                            f"{self.base_url}/api/v1/test", json=data
                        ) as response:
                            validation_results.append(
                                {
                                    "input": test_input,
                                    "status": response.status,
                                    "blocked": response.status == 400,
                                }
                            )
                    except Exception:
                        validation_results.append(
                            {
                                "input": test_input,
                                "blocked": True,
                                "error": "Request failed",
                            }
                        )

            blocked_count = sum(
                1 for result in validation_results if result.get("blocked", False)
            )
            score = (blocked_count / len(test_inputs)) * 100

            return {
                "comprehensive": blocked_count == len(test_inputs),
                "score": score,
                "blocked_inputs": blocked_count,
                "total_inputs": len(test_inputs),
                "results": validation_results,
                "recommendations": (
                    [
                        "Implement comprehensive input validation",
                        "Add XSS protection",
                        "Add SQL injection protection",
                        "Add path traversal protection",
                    ]
                    if score < 100
                    else []
                ),
            }

        except Exception as e:
            return {"comprehensive": False, "score": 0, "error": str(e)}

    async def _run_vulnerability_scan(self) -> dict[str, Any]:
        """Run basic vulnerability scanning."""
        try:
            # This is a simplified vulnerability check
            # In production, integrate with proper security scanning tools

            vulnerabilities = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }

            # Check for common security headers
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    headers = response.headers

                    security_headers = [
                        "x-content-type-options",
                        "x-frame-options",
                        "x-xss-protection",
                        "strict-transport-security",
                        "content-security-policy",
                    ]

                    missing_headers = [
                        header for header in security_headers if header not in headers
                    ]

                    vulnerabilities["medium"] += len(missing_headers)

            return vulnerabilities

        except Exception as e:
            return {"error": str(e)}

    def _check_metrics_collection(self) -> dict[str, Any]:
        """Check metrics collection status."""
        try:
            metrics = self.metrics_collector.get_performance_metrics()

            # Check if metrics are being collected
            has_metrics = (
                metrics.request_count > 0
                or metrics.average_response_time > 0
                or metrics.memory_usage_mb > 0
            )

            return {
                "enabled": has_metrics,
                "score": 100 if has_metrics else 0,
                "metrics_available": {
                    "performance": bool(metrics.request_count > 0),
                    "database": bool(
                        self.metrics_collector.get_database_metrics().query_count > 0
                    ),
                    "cache": bool(
                        self.metrics_collector.get_cache_metrics().hit_count > 0
                    ),
                },
                "recommendations": (
                    [
                        "Enable comprehensive metrics collection",
                        "Set up metrics export to monitoring system",
                        "Configure metric retention policies",
                    ]
                    if not has_metrics
                    else []
                ),
            }

        except Exception as e:
            return {"enabled": False, "score": 0, "error": str(e)}

    def _check_logging_configuration(self) -> dict[str, Any]:
        """Check logging configuration."""
        try:
            # Check if structured logging is configured
            log_dir = Path("./logs")
            has_log_files = log_dir.exists() and any(log_dir.glob("*.log"))

            return {
                "structured": has_log_files,
                "score": 100 if has_log_files else 0,
                "log_files": list(log_dir.glob("*.log")) if log_dir.exists() else [],
                "recommendations": (
                    [
                        "Configure structured logging",
                        "Set up log rotation",
                        "Configure log aggregation",
                        "Set up log monitoring and alerting",
                    ]
                    if not has_log_files
                    else []
                ),
            }

        except Exception as e:
            return {"structured": False, "score": 0, "error": str(e)}

    async def _check_health_endpoints(self) -> dict[str, Any]:
        """Check health endpoint availability."""
        try:
            health_endpoints = ["/health", "/api/v1/health", "/healthz"]
            available_endpoints = []

            async with aiohttp.ClientSession() as session:
                for endpoint in health_endpoints:
                    with contextlib.suppress(Exception):
                        async with session.get(
                            f"{self.base_url}{endpoint}"
                        ) as response:
                            if response.status == 200:
                                available_endpoints.append(endpoint)

            return {
                "available": len(available_endpoints) > 0,
                "endpoints": available_endpoints,
                "count": len(available_endpoints),
            }

        except Exception as e:
            return {"available": False, "error": str(e)}

    def _check_docker_configuration(self) -> dict[str, Any]:
        """Check Docker configuration."""
        try:
            dockerfile_path = Path("./Dockerfile")
            docker_compose_path = Path("./docker-compose.yml")

            has_dockerfile = dockerfile_path.exists()
            has_compose = docker_compose_path.exists()

            score = 0
            recommendations = []

            if has_dockerfile:
                score += 50
                # Check Dockerfile best practices
                with open(dockerfile_path) as f:
                    dockerfile_content = f.read()

                    if "USER" not in dockerfile_content:
                        recommendations.append(
                            "Add non-root USER instruction to Dockerfile"
                        )
                    if "HEALTHCHECK" not in dockerfile_content:
                        recommendations.append(
                            "Add HEALTHCHECK instruction to Dockerfile"
                        )
            else:
                recommendations.append("Create production-ready Dockerfile")

            if has_compose:
                score += 50
            else:
                recommendations.append(
                    "Create docker-compose.yml for local development"
                )

            return {
                "production_ready": score >= 80,
                "score": score,
                "has_dockerfile": has_dockerfile,
                "has_compose": has_compose,
                "recommendations": recommendations,
            }

        except Exception as e:
            return {"production_ready": False, "score": 0, "error": str(e)}

    def _check_environment_configuration(self) -> dict[str, Any]:
        """Check environment configuration."""
        try:
            config_dir = Path("./src/player_experience/config")
            env_files = list(config_dir.glob("*.env")) if config_dir.exists() else []

            required_envs = ["development.env", "staging.env", "production.env"]
            available_envs = [f.name for f in env_files]

            missing_envs = [env for env in required_envs if env not in available_envs]
            score = (
                (len(required_envs) - len(missing_envs)) / len(required_envs)
            ) * 100

            return {
                "complete": len(missing_envs) == 0,
                "score": score,
                "available_environments": available_envs,
                "missing_environments": missing_envs,
                "recommendations": [
                    f"Create {env} configuration file" for env in missing_envs
                ],
            }

        except Exception as e:
            return {"complete": False, "score": 0, "error": str(e)}

    def _check_api_documentation(self) -> dict[str, Any]:
        """Check API documentation."""
        try:
            docs_dir = Path("./src/player_experience/docs")
            api_docs = list(docs_dir.glob("api*")) if docs_dir.exists() else []

            has_openapi = any("openapi" in f.name for f in api_docs)
            has_markdown = any(".md" in f.name for f in api_docs)
            has_html = any(".html" in f.name for f in api_docs)

            score = sum([has_openapi * 40, has_markdown * 30, has_html * 30])

            return {
                "complete": score >= 70,
                "score": score,
                "has_openapi": has_openapi,
                "has_markdown": has_markdown,
                "has_html": has_html,
                "recommendations": (
                    [
                        "Generate OpenAPI specification" if not has_openapi else None,
                        "Generate Markdown documentation" if not has_markdown else None,
                        "Generate HTML documentation" if not has_html else None,
                    ]
                    if score < 70
                    else []
                ),
            }

        except Exception as e:
            return {"complete": False, "score": 0, "error": str(e)}

    def _check_deployment_documentation(self) -> dict[str, Any]:
        """Check deployment documentation."""
        try:
            docs_files = [
                Path("./DEPLOYMENT.md"),
                Path("./README.md"),
                Path("./src/player_experience/DEPLOYMENT.md"),
                Path("./docs/deployment.md"),
            ]

            existing_docs = [f for f in docs_files if f.exists()]

            return {
                "complete": len(existing_docs) > 0,
                "score": min(100, len(existing_docs) * 50),
                "existing_files": [str(f) for f in existing_docs],
                "recommendations": (
                    [
                        "Create comprehensive deployment guide",
                        "Document environment setup procedures",
                        "Document troubleshooting procedures",
                        "Document maintenance procedures",
                    ]
                    if len(existing_docs) == 0
                    else []
                ),
            }

        except Exception as e:
            return {"complete": False, "score": 0, "error": str(e)}

    def _check_gdpr_compliance(self) -> dict[str, Any]:
        """Check GDPR compliance features."""
        try:
            # Check for privacy service implementation
            privacy_service_path = Path(
                "./src/player_experience/services/privacy_service.py"
            )
            has_privacy_service = privacy_service_path.exists()

            # Check for data export/deletion endpoints
            # This would require checking the actual API routes

            score = 0
            recommendations = []

            if has_privacy_service:
                score += 60
            else:
                recommendations.append("Implement comprehensive privacy service")

            # Additional GDPR checks would go here

            return {
                "compliant": score >= 80,
                "score": score,
                "has_privacy_service": has_privacy_service,
                "recommendations": recommendations,
            }

        except Exception as e:
            return {"compliant": False, "score": 0, "error": str(e)}

    def _generate_report(self) -> ReadinessReport:
        """Generate comprehensive readiness report."""
        # Calculate category scores
        category_scores = {}
        for category in CheckCategory:
            category_checks = [
                check for check in self.checks if check.category == category
            ]
            if category_checks:
                category_scores[category] = sum(
                    check.score for check in category_checks
                ) / len(category_checks)
            else:
                category_scores[category] = 0

        # Calculate overall score
        overall_score = (
            sum(category_scores.values()) / len(category_scores)
            if category_scores
            else 0
        )

        # Determine readiness level
        if overall_score >= 90:
            overall_level = ReadinessLevel.ENTERPRISE
        elif overall_score >= 75:
            overall_level = ReadinessLevel.PRODUCTION
        elif overall_score >= 50:
            overall_level = ReadinessLevel.BASIC
        else:
            overall_level = ReadinessLevel.NOT_READY

        # Collect critical issues
        critical_issues = []
        for check in self.checks:
            if not check.passed and check.required_level in [
                ReadinessLevel.BASIC,
                ReadinessLevel.PRODUCTION,
            ]:
                critical_issues.append(f"{check.name}: {check.description}")

        # Collect recommendations
        all_recommendations = []
        for check in self.checks:
            if not check.passed:
                all_recommendations.extend(check.recommendations)

        # Remove duplicates
        unique_recommendations = list(set(all_recommendations))

        return ReadinessReport(
            timestamp=datetime.utcnow(),
            overall_level=overall_level,
            overall_score=overall_score,
            checks=self.checks,
            category_scores=category_scores,
            critical_issues=critical_issues,
            recommendations=unique_recommendations,
        )

    async def _save_report(self, report: ReadinessReport):
        """Save readiness report to file."""
        try:
            output_dir = Path("./production_readiness_reports")
            output_dir.mkdir(exist_ok=True)

            timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
            report_file = output_dir / f"readiness_report_{timestamp}.json"

            with open(report_file, "w") as f:
                json.dump(report.to_dict(), f, indent=2, default=str)

            logger.info(f"Production readiness report saved to {report_file}")

        except Exception as e:
            logger.error(f"Failed to save readiness report: {e}")


async def main():
    """Main function for running production readiness assessment."""
    import argparse

    parser = argparse.ArgumentParser(description="Production Readiness Assessment")
    parser.add_argument(
        "--base-url", default="http://localhost:8080", help="Base URL for API testing"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--output",
        default="./production_readiness_reports",
        help="Output directory for reports",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(log_level="INFO", enable_console=True, enable_file=True)

    # Run assessment
    validator = ProductionReadinessValidator(args.base_url, args.config)
    report = await validator.run_comprehensive_assessment()

    # Print summary

    if report.critical_issues:
        for _issue in report.critical_issues[:5]:  # Show first 5
            pass
        if len(report.critical_issues) > 5:
            pass

    if report.recommendations:
        for _rec in report.recommendations[:5]:  # Show first 5
            pass
        if len(report.recommendations) > 5:
            pass


if __name__ == "__main__":
    asyncio.run(main())
