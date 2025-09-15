"""
Tests for Cloud Deployment Manager

This module tests the production deployment infrastructure functionality including
scalable cloud deployment, high availability, and performance optimization.
"""

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.infrastructure.cloud_deployment_manager import (
    CloudDeploymentManager,
    DeploymentConfiguration,
    DeploymentStatus,
    ServiceInstance,
    ServiceType,
)


class TestCloudDeploymentManager:
    """Test Cloud Deployment Manager functionality."""

    @pytest_asyncio.fixture
    async def deployment_manager(self):
        """Create deployment manager instance."""
        config = DeploymentConfiguration(
            deployment_name="test-deployment",
            environment="test",
            min_instances=2,
            max_instances=10,
            max_concurrent_sessions=100
        )
        manager = CloudDeploymentManager(configuration=config)
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.fixture
    def mock_infrastructure_components(self):
        """Create mock infrastructure components."""
        components = {}

        for component_name in [
            "high_availability_controller",
            "security_framework",
            "monitoring_system",
            "performance_optimizer",
            "scalability_manager"
        ]:
            mock_component = AsyncMock()
            mock_component.initialize.return_value = None

            if component_name == "scalability_manager":
                mock_component.configure_auto_scaling.return_value = {
                    "auto_scaling_enabled": True,
                    "min_instances": 2,
                    "max_instances": 10
                }
            elif component_name == "monitoring_system":
                mock_component.configure_deployment_monitoring.return_value = {
                    "metrics_enabled": True,
                    "logging_enabled": True
                }
            elif component_name == "security_framework":
                mock_component.configure_deployment_security.return_value = {
                    "encryption_enabled": True,
                    "hipaa_compliance": True
                }

            components[component_name] = mock_component

        return components

    @pytest.fixture
    def mock_therapeutic_systems(self):
        """Create mock therapeutic systems."""
        systems = {}

        for system_name in [
            "consequence_system",
            "emotional_safety_system",
            "adaptive_difficulty_engine",
            "character_development_system",
            "therapeutic_integration_system",
            "gameplay_loop_controller",
            "replayability_system",
            "collaborative_system",
            "error_recovery_manager"
        ]:
            mock_system = AsyncMock()
            mock_system.health_check.return_value = {"status": "healthy"}
            systems[system_name] = mock_system

        return systems

    @pytest.fixture
    def mock_clinical_dashboard(self):
        """Create mock clinical dashboard manager."""
        dashboard = AsyncMock()
        dashboard.health_check.return_value = {"status": "healthy"}
        return dashboard

    @pytest.mark.asyncio
    async def test_initialization(self, deployment_manager):
        """Test deployment manager initialization."""
        assert deployment_manager.status == DeploymentStatus.ACTIVE
        assert deployment_manager.configuration.deployment_name == "test-deployment"
        assert deployment_manager.configuration.environment == "test"
        assert len(deployment_manager.service_instances) == 0
        assert len(deployment_manager.active_deployments) == 0

        # Should have background tasks running
        assert deployment_manager._deployment_monitoring_task is not None
        assert deployment_manager._health_check_task is not None
        assert deployment_manager._scaling_task is not None

    @pytest.mark.asyncio
    async def test_infrastructure_component_injection(self, deployment_manager, mock_infrastructure_components):
        """Test infrastructure component dependency injection."""
        deployment_manager.inject_infrastructure_components(**mock_infrastructure_components)

        # Should have all components injected
        assert deployment_manager.high_availability_controller is not None
        assert deployment_manager.security_framework is not None
        assert deployment_manager.monitoring_system is not None
        assert deployment_manager.performance_optimizer is not None
        assert deployment_manager.scalability_manager is not None

    @pytest.mark.asyncio
    async def test_therapeutic_systems_injection(self, deployment_manager, mock_therapeutic_systems, mock_clinical_dashboard):
        """Test therapeutic systems dependency injection."""
        deployment_manager.inject_therapeutic_systems(
            clinical_dashboard_manager=mock_clinical_dashboard,
            **mock_therapeutic_systems
        )

        # Should have all systems injected
        assert deployment_manager.clinical_dashboard_manager is not None
        assert len(deployment_manager.therapeutic_systems) == 9
        assert "consequence_system" in deployment_manager.therapeutic_systems
        assert "emotional_safety_system" in deployment_manager.therapeutic_systems

    @pytest.mark.asyncio
    async def test_configuration_validation(self):
        """Test deployment configuration validation."""
        # Test valid configuration
        valid_config = DeploymentConfiguration(
            deployment_name="valid-deployment",
            min_instances=3,
            max_instances=20,
            max_concurrent_sessions=1000
        )
        manager = CloudDeploymentManager(configuration=valid_config)
        await manager.initialize()
        assert manager.status == DeploymentStatus.ACTIVE
        await manager.shutdown()

        # Test invalid configuration - empty name
        invalid_config = DeploymentConfiguration(
            deployment_name="",
            min_instances=1,
            max_instances=5
        )
        manager = CloudDeploymentManager(configuration=invalid_config)

        with pytest.raises(ValueError, match="Deployment name is required"):
            await manager.initialize()

    @pytest.mark.asyncio
    async def test_service_instance_deployment(self, deployment_manager):
        """Test service instance deployment."""
        instance = await deployment_manager._deploy_service_instance(
            service_type=ServiceType.WEB_API,
            service_name="test-api",
            deployment_id="test-deployment-001"
        )

        # Should create service instance
        assert isinstance(instance, ServiceInstance)
        assert instance.service_type == ServiceType.WEB_API
        assert instance.instance_name.startswith("test-api")
        assert instance.status == "running"
        assert instance.health_status == "healthy"
        assert instance.last_health_check is not None

        # Should be stored in service instances
        assert instance.instance_id in deployment_manager.service_instances
        assert deployment_manager.service_instances[instance.instance_id] == instance

        # Should update metrics
        assert deployment_manager.deployment_metrics["active_instances"] == 1

    @pytest.mark.asyncio
    async def test_database_cluster_deployment(self, deployment_manager):
        """Test database cluster deployment."""
        database_instances = await deployment_manager._deploy_database_cluster()

        # Should deploy primary database
        assert len(database_instances) >= 1
        primary_db = database_instances[0]
        assert primary_db.service_type == ServiceType.DATABASE
        assert primary_db.configuration["role"] == "primary"
        assert primary_db.configuration["engine"] == deployment_manager.configuration.database_engine

        # Should deploy replicas if multi-AZ enabled
        if deployment_manager.configuration.database_multi_az:
            assert len(database_instances) > 1
            for replica in database_instances[1:]:
                assert replica.configuration["role"] == "replica"
                assert replica.configuration["primary_instance"] == primary_db.instance_id

    @pytest.mark.asyncio
    async def test_cache_cluster_deployment(self, deployment_manager):
        """Test cache cluster deployment."""
        cache_instances = await deployment_manager._deploy_cache_cluster()

        # Should deploy cache nodes
        assert len(cache_instances) == deployment_manager.configuration.cache_num_cache_nodes

        for instance in cache_instances:
            assert instance.service_type == ServiceType.CACHE
            assert instance.configuration["engine"] == deployment_manager.configuration.cache_engine
            assert instance.configuration["cluster_mode"] is True

    @pytest.mark.asyncio
    async def test_load_balancer_deployment(self, deployment_manager):
        """Test load balancer deployment."""
        load_balancer_instances = await deployment_manager._deploy_load_balancers()

        # Should deploy application and network load balancers
        assert len(load_balancer_instances) == 2

        alb = next(lb for lb in load_balancer_instances if lb.configuration["type"] == "application")
        nlb = next(lb for lb in load_balancer_instances if lb.configuration["type"] == "network")

        assert alb.service_type == ServiceType.LOAD_BALANCER
        assert alb.configuration["scheme"] == "internet-facing"
        assert "target_groups" in alb.configuration

        assert nlb.service_type == ServiceType.LOAD_BALANCER
        assert nlb.configuration["scheme"] == "internal"

    @pytest.mark.asyncio
    async def test_therapeutic_platform_deployment(
        self,
        deployment_manager,
        mock_infrastructure_components,
        mock_therapeutic_systems,
        mock_clinical_dashboard
    ):
        """Test complete therapeutic platform deployment."""
        # Inject dependencies
        deployment_manager.inject_infrastructure_components(**mock_infrastructure_components)
        deployment_manager.inject_therapeutic_systems(
            clinical_dashboard_manager=mock_clinical_dashboard,
            **mock_therapeutic_systems
        )

        # Deploy platform
        deployment_result = await deployment_manager.deploy_therapeutic_platform(
            deployment_name="test-tta-platform",
            environment="test"
        )

        # Should return successful deployment
        assert deployment_result["status"] == "successful"
        assert deployment_result["deployment_name"] == "test-tta-platform"
        assert deployment_result["environment"] == "test"
        assert "deployment_id" in deployment_result
        assert "infrastructure" in deployment_result
        assert "therapeutic_systems" in deployment_result
        assert "clinical_dashboard" in deployment_result

        # Should have infrastructure components
        infrastructure = deployment_result["infrastructure"]
        assert infrastructure["success"] is True
        assert "database_instances" in infrastructure
        assert "cache_instances" in infrastructure
        assert "load_balancer_instances" in infrastructure

        # Should have therapeutic systems
        therapeutic_systems = deployment_result["therapeutic_systems"]
        assert therapeutic_systems["success"] is True
        assert therapeutic_systems["total_systems"] == 9
        assert "deployed_systems" in therapeutic_systems

        # Should have clinical dashboard
        clinical_dashboard = deployment_result["clinical_dashboard"]
        assert clinical_dashboard["success"] is True
        assert "dashboard_instance" in clinical_dashboard

        # Should update metrics
        assert deployment_manager.deployment_metrics["total_deployments"] == 1
        assert deployment_manager.deployment_metrics["successful_deployments"] == 1
        assert deployment_manager.status == DeploymentStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_deployment_validation(self, deployment_manager, mock_therapeutic_systems, mock_clinical_dashboard):
        """Test deployment validation."""
        # Inject systems for validation
        deployment_manager.inject_therapeutic_systems(
            clinical_dashboard_manager=mock_clinical_dashboard,
            **mock_therapeutic_systems
        )

        validation_result = await deployment_manager._validate_deployment("test-deployment-001")

        # Should have validation results
        assert "success" in validation_result
        assert "success_rate" in validation_result
        assert "validations" in validation_result

        validations = validation_result["validations"]
        assert "infrastructure_health" in validations
        assert "service_connectivity" in validations
        assert "performance_benchmarks" in validations
        assert "security_compliance" in validations
        assert "therapeutic_systems_integration" in validations

        # Should pass most validations
        assert validation_result["success_rate"] >= 80.0

    @pytest.mark.asyncio
    async def test_infrastructure_health_validation(self, deployment_manager):
        """Test infrastructure health validation."""
        # Add some healthy instances
        await deployment_manager._deploy_service_instance(
            ServiceType.WEB_API, "api-1", "test-deployment"
        )
        await deployment_manager._deploy_service_instance(
            ServiceType.DATABASE, "db-1", "test-deployment"
        )

        health_result = await deployment_manager._validate_infrastructure_health()

        assert health_result["success"] is True
        assert health_result["health_percentage"] == 100.0
        assert health_result["healthy_instances"] == 2
        assert health_result["total_instances"] == 2

    @pytest.mark.asyncio
    async def test_service_connectivity_validation(self, deployment_manager):
        """Test service connectivity validation."""
        connectivity_result = await deployment_manager._validate_service_connectivity()

        assert connectivity_result["success"] is True
        assert "connectivity_results" in connectivity_result
        assert connectivity_result["successful_connections"] == connectivity_result["total_connections"]

    @pytest.mark.asyncio
    async def test_performance_benchmarks_validation(self, deployment_manager):
        """Test performance benchmarks validation."""
        performance_result = await deployment_manager._validate_performance_benchmarks()

        assert "success" in performance_result
        assert "performance_results" in performance_result
        assert "benchmarks_met" in performance_result

        performance_data = performance_result["performance_results"]
        assert "response_time_ms" in performance_data
        assert "throughput_rps" in performance_data
        assert "concurrent_sessions" in performance_data

        # Should meet performance requirements
        assert performance_data["response_time_ms"] < 100
        assert performance_data["throughput_rps"] > 500
        assert performance_data["concurrent_sessions"] >= 1000

    @pytest.mark.asyncio
    async def test_security_compliance_validation(self, deployment_manager):
        """Test security compliance validation."""
        security_result = await deployment_manager._validate_security_compliance()

        assert security_result["success"] is True
        assert "security_checks" in security_result
        assert security_result["compliance_percentage"] == 100.0

        security_checks = security_result["security_checks"]
        assert security_checks["encryption_at_rest"] is True
        assert security_checks["encryption_in_transit"] is True
        assert security_checks["hipaa_compliance"] is True
        assert security_checks["access_controls"] is True

    @pytest.mark.asyncio
    async def test_therapeutic_systems_integration_validation(self, deployment_manager, mock_therapeutic_systems, mock_clinical_dashboard):
        """Test therapeutic systems integration validation."""
        deployment_manager.inject_therapeutic_systems(
            clinical_dashboard_manager=mock_clinical_dashboard,
            **mock_therapeutic_systems
        )

        integration_result = await deployment_manager._validate_therapeutic_systems_integration()

        assert integration_result["success"] is True
        assert "integration_results" in integration_result
        assert integration_result["successful_integrations"] == 10  # 9 systems + dashboard
        assert integration_result["total_integrations"] == 10

    @pytest.mark.asyncio
    async def test_deployment_failure_handling(self, deployment_manager):
        """Test deployment failure handling."""
        # Test deployment without required systems
        deployment_result = await deployment_manager.deploy_therapeutic_platform(
            deployment_name="failing-deployment",
            environment="test"
        )

        # Should handle missing systems gracefully
        assert "deployment_id" in deployment_result
        assert "infrastructure" in deployment_result
        assert "therapeutic_systems" in deployment_result

        # Therapeutic systems deployment should indicate missing systems
        therapeutic_systems = deployment_result["therapeutic_systems"]
        assert therapeutic_systems["total_systems"] == 0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, deployment_manager, mock_therapeutic_systems, mock_clinical_dashboard):
        """Test performance benchmarks for cloud deployment."""
        deployment_manager.inject_therapeutic_systems(
            clinical_dashboard_manager=mock_clinical_dashboard,
            **mock_therapeutic_systems
        )

        # Test service instance deployment performance
        import time
        start_time = time.perf_counter()

        await deployment_manager._deploy_service_instance(
            ServiceType.THERAPEUTIC_SYSTEMS, "perf-test", "perf-deployment"
        )

        deployment_time = (time.perf_counter() - start_time) * 1000
        assert deployment_time < 500.0  # Should be under 500ms

        # Test validation performance
        start_time = time.perf_counter()

        await deployment_manager._validate_deployment("perf-deployment")

        validation_time = (time.perf_counter() - start_time) * 1000
        assert validation_time < 1000.0  # Should be under 1 second

        # Validate performance requirements are met
        performance_result = await deployment_manager._validate_performance_benchmarks()
        assert performance_result["success"] is True

    @pytest.mark.asyncio
    async def test_e2e_interface_compatibility(self, deployment_manager, mock_therapeutic_systems, mock_clinical_dashboard):
        """Test compatibility with E2E test interface expectations."""
        deployment_manager.inject_therapeutic_systems(
            clinical_dashboard_manager=mock_clinical_dashboard,
            **mock_therapeutic_systems
        )

        # Test deployment (E2E interface)
        deployment_result = await deployment_manager.deploy_therapeutic_platform(
            deployment_name="e2e-test-deployment",
            environment="test"
        )

        # Should match expected structure
        assert "deployment_id" in deployment_result
        assert "deployment_name" in deployment_result
        assert "status" in deployment_result
        assert "infrastructure" in deployment_result
        assert "therapeutic_systems" in deployment_result
        assert "clinical_dashboard" in deployment_result
        assert "validation" in deployment_result

        # Test service instance deployment (E2E interface)
        instance = await deployment_manager._deploy_service_instance(
            ServiceType.WEB_API, "e2e-api", "e2e-deployment"
        )

        # Should match expected structure
        assert hasattr(instance, "instance_id")
        assert hasattr(instance, "service_type")
        assert hasattr(instance, "status")
        assert hasattr(instance, "health_status")
        assert hasattr(instance, "configuration")

        # Test validation (E2E interface)
        validation_result = await deployment_manager._validate_deployment("e2e-deployment")

        # Should match expected structure
        assert "success" in validation_result
        assert "success_rate" in validation_result
        assert "validations" in validation_result
