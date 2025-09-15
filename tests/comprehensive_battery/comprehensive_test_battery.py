"""
Comprehensive Test Battery Orchestrator

Main orchestrator for executing comprehensive tests across all categories:
- Standard user interaction flows
- Adversarial and edge case testing  
- Load and stress testing
- Data pipeline validation
- Dashboard verification
"""

import asyncio
import logging
import time
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import redis.asyncio as aioredis
from neo4j import AsyncGraphDatabase

# Import mock services
from .mocks.mock_services import MockServiceManager

from .common import TestResult, TestCategory, TestStatus
from .test_suites.standard_test_suite import StandardTestSuite
from .test_suites.adversarial_test_suite import AdversarialTestSuite
from .test_suites.load_stress_test_suite import LoadStressTestSuite
from .validators.data_pipeline_validator import DataPipelineValidator
from .validators.dashboard_validator import DashboardValidator
from .utils.test_data_generator import TestDataGenerator
from .utils.metrics_collector import TestMetricsCollector
from .utils.report_generator import TestReportGenerator

logger = logging.getLogger(__name__)


@dataclass
class TestBatteryConfig:
    """Configuration for comprehensive test battery."""
    # Mock mode settings
    mock_mode: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'force_mock': False,
        'log_mock_operations': True,
        'mock_data_size': 'medium',
        'preserve_mock_data': False
    })

    # Database connections
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    redis_url: str = "redis://localhost:6379"

    # Test execution settings
    max_concurrent_tests: int = 4
    test_timeout_seconds: int = 1800  # 30 minutes
    cleanup_between_tests: bool = True
    
    # Test categories to run
    run_standard_tests: bool = True
    run_adversarial_tests: bool = True
    run_load_stress_tests: bool = True
    run_data_pipeline_validation: bool = True
    run_dashboard_verification: bool = True
    
    # Load testing parameters
    max_concurrent_users: int = 100
    load_test_duration_minutes: int = 10
    
    # Results and reporting
    results_directory: str = "./testing/results/comprehensive_battery"
    generate_detailed_reports: bool = True
    capture_screenshots: bool = True


class ComprehensiveTestBattery:
    """
    Main orchestrator for comprehensive TTA system testing.
    
    Coordinates execution of all test categories and provides
    comprehensive validation of the entire TTA storytelling pipeline.
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        max_concurrent_tests: int = 5,
        test_timeout_seconds: int = 300,
        neo4j_uri_override: Optional[str] = None,
        redis_url_override: Optional[str] = None,
        force_mock_mode: bool = False
    ):
        # Load configuration from file if provided
        if config_path:
            self.config = self._load_config_from_file(config_path)
        else:
            self.config = TestBatteryConfig()

        # Apply overrides
        if neo4j_uri_override:
            self.config.neo4j_uri = neo4j_uri_override
        if redis_url_override:
            self.config.redis_url = redis_url_override
        if force_mock_mode:
            self.config.mock_mode['force_mock'] = True

        self.config.max_concurrent_tests = max_concurrent_tests
        self.config.test_timeout_seconds = test_timeout_seconds

        self.results: List[TestResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Database connections
        self.neo4j_driver = None
        self.redis_client = None

        # Mock service manager
        self.mock_service_manager = MockServiceManager()
        
        # Test suites
        self.standard_suite: Optional[StandardTestSuite] = None
        self.adversarial_suite: Optional[AdversarialTestSuite] = None
        self.load_stress_suite: Optional[LoadStressTestSuite] = None
        
        # Validators
        self.data_pipeline_validator: Optional[DataPipelineValidator] = None
        self.dashboard_validator: Optional[DashboardValidator] = None
        
        # Utilities
        self.test_data_generator: Optional[TestDataGenerator] = None
        self.metrics_collector: Optional[TestMetricsCollector] = None
        self.report_generator: Optional[TestReportGenerator] = None
        
        self.is_initialized = False

    def _load_config_from_file(self, config_path: str) -> 'TestBatteryConfig':
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)

            # Create config from YAML data
            config = TestBatteryConfig()

            # Mock mode settings
            if 'mock_mode' in config_data:
                mock_config = config_data['mock_mode']
                config.mock_mode.update(mock_config)

            # Database settings
            if 'databases' in config_data:
                db_config = config_data['databases']
                if 'neo4j' in db_config:
                    neo4j_config = db_config['neo4j']
                    config.neo4j_uri = neo4j_config.get('uri', config.neo4j_uri)
                    config.neo4j_user = neo4j_config.get('username', config.neo4j_user)
                    config.neo4j_password = neo4j_config.get('password', config.neo4j_password)

                if 'redis' in db_config:
                    redis_config = db_config['redis']
                    config.redis_url = redis_config.get('url', config.redis_url)

            # Execution settings
            if 'execution' in config_data:
                exec_config = config_data['execution']
                config.max_concurrent_tests = exec_config.get('max_concurrent_tests', config.max_concurrent_tests)
                config.test_timeout_seconds = exec_config.get('test_timeout_seconds', config.test_timeout_seconds)

            return config

        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}. Using defaults.")
            return TestBatteryConfig()

    async def initialize(self) -> bool:
        """Initialize test battery components and connections."""
        try:
            logger.info("Initializing comprehensive test battery...")
            
            # Initialize database connections
            await self._initialize_database_connections()
            
            # Initialize test suites
            await self._initialize_test_suites()
            
            # Initialize validators
            await self._initialize_validators()
            
            # Initialize utilities
            await self._initialize_utilities()
            
            self.is_initialized = True
            logger.info("Comprehensive test battery initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize test battery: {e}")
            return False
    
    async def execute_all_tests(self) -> Dict[str, Any]:
        """Execute all configured test categories."""
        if not self.is_initialized:
            raise RuntimeError("Test battery not initialized. Call initialize() first.")
        
        self.start_time = datetime.utcnow()
        logger.info("Starting comprehensive test battery execution...")
        
        try:
            # Execute test categories in sequence
            if self.config.run_standard_tests:
                await self._execute_standard_tests()
            
            if self.config.run_adversarial_tests:
                await self._execute_adversarial_tests()
            
            if self.config.run_load_stress_tests:
                await self._execute_load_stress_tests()
            
            if self.config.run_data_pipeline_validation:
                await self._execute_data_pipeline_validation()
            
            if self.config.run_dashboard_verification:
                await self._execute_dashboard_verification()
            
            self.end_time = datetime.utcnow()
            
            # Generate comprehensive report
            return await self._generate_final_report()
            
        except Exception as e:
            logger.error(f"Test battery execution failed: {e}")
            self.end_time = datetime.utcnow()
            raise

    async def run_standard_tests(self) -> List[TestResult]:
        """Run standard test suite."""
        logger.info("Starting standard test suite")

        if not self.standard_suite:
            logger.error("Standard test suite not initialized")
            return [TestResult(
                test_name="standard_suite_initialization",
                category=TestCategory.STANDARD,
                status=TestStatus.FAILED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message="Standard test suite not initialized"
            )]

        try:
            return await self.standard_suite.execute_all_tests()
        except Exception as e:
            logger.error(f"Standard test suite failed: {e}")
            return [TestResult(
                test_name="standard_suite_execution",
                category=TestCategory.STANDARD,
                status=TestStatus.FAILED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message=str(e)
            )]

    async def run_adversarial_tests(self) -> List[TestResult]:
        """Run adversarial test suite."""
        logger.info("Starting adversarial test suite")

        if not self.adversarial_suite:
            logger.error("Adversarial test suite not initialized")
            return [TestResult(
                test_name="adversarial_suite_initialization",
                category=TestCategory.ADVERSARIAL,
                status=TestStatus.FAILED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message="Adversarial test suite not initialized"
            )]

        try:
            return await self.adversarial_suite.execute_all_tests()
        except Exception as e:
            logger.error(f"Adversarial test suite failed: {e}")
            return [TestResult(
                test_name="adversarial_suite_execution",
                category=TestCategory.ADVERSARIAL,
                status=TestStatus.FAILED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message=str(e)
            )]

    async def run_load_stress_tests(self) -> List[TestResult]:
        """Run load/stress test suite."""
        logger.info("Starting load/stress test suite")

        if not self.load_stress_suite:
            logger.error("Load/stress test suite not initialized")
            return [TestResult(
                test_name="load_stress_suite_initialization",
                category=TestCategory.LOAD_STRESS,
                status=TestStatus.FAILED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message="Load/stress test suite not initialized"
            )]

        try:
            return await self.load_stress_suite.execute_all_tests()
        except Exception as e:
            logger.error(f"Load/stress test suite failed: {e}")
            return [TestResult(
                test_name="load_stress_suite_execution",
                category=TestCategory.LOAD_STRESS,
                status=TestStatus.FAILED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message=str(e)
            )]

    async def run_data_pipeline_validation(self) -> List[TestResult]:
        """Run data pipeline validation tests."""
        logger.info("Starting data pipeline validation")

        try:
            validator = DataPipelineValidator(
                neo4j_driver=self.neo4j_driver,
                redis_client=self.redis_client,
                config=self.config
            )

            results = await validator.validate_pipeline()

            logger.info(f"Data pipeline validation completed: {len(results)} tests")
            return results

        except Exception as e:
            logger.error(f"Data pipeline validation failed: {e}")
            return [TestResult(
                test_name="data_pipeline_validation_error",
                category=TestCategory.DATA_PIPELINE,
                status=TestStatus.COMPLETED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message=str(e)
            )]

    async def run_dashboard_verification(self) -> List[TestResult]:
        """Run dashboard verification tests."""
        logger.info("Starting dashboard verification")

        try:
            validator = DashboardValidator(config=self.config)

            results = await validator.verify_dashboards()

            logger.info(f"Dashboard verification completed: {len(results)} tests")
            return results

        except Exception as e:
            logger.error(f"Dashboard verification failed: {e}")
            return [TestResult(
                test_name="dashboard_verification_error",
                category=TestCategory.DASHBOARD,
                status=TestStatus.COMPLETED,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                passed=False,
                error_message=str(e)
            )]

    async def cleanup(self):
        """Clean up resources and connections."""
        logger.info("Cleaning up test battery resources...")

        # Close database connections
        if self.neo4j_driver:
            await self.neo4j_driver.close()
        if self.redis_client:
            await self.redis_client.close()

        # Cleanup mock service manager
        if self.mock_service_manager:
            await self.mock_service_manager.cleanup()

        # Cleanup test suites
        if self.standard_suite:
            await self.standard_suite.cleanup()
        if self.adversarial_suite:
            await self.adversarial_suite.cleanup()
        if self.load_stress_suite:
            await self.load_stress_suite.cleanup()
    
    async def _initialize_database_connections(self):
        """Initialize Neo4j and Redis connections with automatic mock fallback."""
        try:
            # Check if mock mode is forced
            mock_config = getattr(self.config, 'mock_mode', {})
            force_mock = mock_config.get('force_mock', False)

            if force_mock:
                logger.info("🎭 Mock mode forced - using mock implementations")
                return await self._initialize_mock_connections()

            # Try to initialize real connections with automatic fallback
            logger.info("Attempting to initialize database connections...")

            # Initialize Neo4j connection with fallback
            logger.info(f"Connecting to Neo4j at {self.config.neo4j_uri}")
            self.neo4j_driver = await self.mock_service_manager.get_neo4j_driver(
                self.config.neo4j_uri,
                auth=(self.config.neo4j_user, self.config.neo4j_password)
            )

            # Initialize Redis connection with fallback
            logger.info(f"Connecting to Redis at {self.config.redis_url}")
            self.redis_client = await self.mock_service_manager.get_redis_client(
                self.config.redis_url
            )

            # Log connection status
            services_status = self.mock_service_manager.get_services_status()
            if services_status['neo4j']['mock'] or services_status['redis']['mock']:
                logger.warning("⚠️  Some services using mock implementations")
                self._log_mock_status()
            else:
                logger.info("✅ All database connections established")

        except Exception as e:
            logger.error(f"Database connection initialization failed: {e}")
            raise

    async def _initialize_mock_connections(self):
        """Initialize mock database connections."""
        try:
            logger.info("🎭 Initializing mock database connections...")

            # Force mock implementations
            from .mocks.mock_neo4j import create_mock_driver
            from .mocks.mock_redis import create_mock_redis_client

            self.neo4j_driver = create_mock_driver(
                self.config.neo4j_uri,
                auth=(self.config.neo4j_user, self.config.neo4j_password)
            )

            self.redis_client = create_mock_redis_client(self.config.redis_url)

            # Update service manager status
            self.mock_service_manager.mock_mode = True
            self.mock_service_manager.services_status['neo4j'] = {
                'available': False, 'mock': True, 'client': self.neo4j_driver
            }
            self.mock_service_manager.services_status['redis'] = {
                'available': False, 'mock': True, 'client': self.redis_client
            }

            logger.info("✅ Mock database connections initialized")
            self._log_mock_status()

        except Exception as e:
            logger.error(f"Mock connection initialization failed: {e}")
            raise

    def _log_mock_status(self):
        """Log mock service status and recommendations."""
        mock_summary = self.mock_service_manager.get_mock_summary()

        logger.info("🎭 Mock Service Status:")
        for service, status in mock_summary['services'].items():
            if status['mock']:
                logger.info(f"  {service}: Mock implementation (Real service error: {status.get('error', 'Unknown')})")
            else:
                logger.info(f"  {service}: Real implementation")

        for recommendation in mock_summary['recommendations']:
            logger.info(f"💡 {recommendation}")
    
    async def _initialize_test_suites(self):
        """Initialize all test suites."""
        self.standard_suite = StandardTestSuite(
            neo4j_driver=self.neo4j_driver,
            redis_client=self.redis_client,
            config=self.config
        )
        
        self.adversarial_suite = AdversarialTestSuite(
            neo4j_driver=self.neo4j_driver,
            redis_client=self.redis_client,
            config=self.config
        )
        
        self.load_stress_suite = LoadStressTestSuite(
            neo4j_driver=self.neo4j_driver,
            redis_client=self.redis_client,
            config=self.config
        )
        
        logger.info("Test suites initialized")
    
    async def _initialize_validators(self):
        """Initialize validation components."""
        self.data_pipeline_validator = DataPipelineValidator(
            neo4j_driver=self.neo4j_driver,
            redis_client=self.redis_client,
            config=self.config
        )
        
        self.dashboard_validator = DashboardValidator(
            config=self.config
        )
        
        logger.info("Validators initialized")
    
    async def _initialize_utilities(self):
        """Initialize utility components."""
        self.test_data_generator = TestDataGenerator(
            neo4j_driver=self.neo4j_driver,
            redis_client=self.redis_client
        )
        
        self.metrics_collector = TestMetricsCollector()
        
        self.report_generator = TestReportGenerator(
            results_directory=self.config.results_directory
        )
        
        logger.info("Utilities initialized")
    
    async def _execute_standard_tests(self):
        """Execute standard test suite."""
        logger.info("Executing standard test suite...")
        results = await self.standard_suite.execute_all_tests()
        self.results.extend(results)
    
    async def _execute_adversarial_tests(self):
        """Execute adversarial test suite."""
        logger.info("Executing adversarial test suite...")
        results = await self.adversarial_suite.execute_all_tests()
        self.results.extend(results)
    
    async def _execute_load_stress_tests(self):
        """Execute load/stress test suite."""
        logger.info("Executing load/stress test suite...")
        results = await self.load_stress_suite.execute_all_tests()
        self.results.extend(results)
    
    async def _execute_data_pipeline_validation(self):
        """Execute data pipeline validation."""
        logger.info("Executing data pipeline validation...")
        results = await self.data_pipeline_validator.validate_pipeline()
        self.results.extend(results)
    
    async def _execute_dashboard_verification(self):
        """Execute dashboard verification."""
        logger.info("Executing dashboard verification...")
        results = await self.dashboard_validator.verify_dashboards()
        self.results.extend(results)
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.passed])
        failed_tests = total_tests - passed_tests
        
        # Generate detailed report
        report = await self.report_generator.generate_comprehensive_report(
            results=self.results,
            start_time=self.start_time,
            end_time=self.end_time,
            config=self.config
        )
        
        summary = {
            "execution_summary": {
                "total_duration_seconds": total_duration,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "category_results": self._summarize_by_category(),
            "detailed_report_path": report.get("report_path"),
            "recommendations": report.get("recommendations", [])
        }
        
        logger.info(f"Test battery completed: {passed_tests}/{total_tests} tests passed")
        return summary
    
    def _summarize_by_category(self) -> Dict[str, Dict[str, Any]]:
        """Summarize results by test category."""
        categories = {}
        
        for category in TestCategory:
            category_results = [r for r in self.results if r.category == category]
            if category_results:
                passed = len([r for r in category_results if r.passed])
                total = len(category_results)
                
                categories[category.value] = {
                    "total_tests": total,
                    "passed_tests": passed,
                    "failed_tests": total - passed,
                    "success_rate": (passed / total * 100) if total > 0 else 0,
                    "avg_duration": sum(r.duration_seconds for r in category_results) / total
                }
        
        return categories
