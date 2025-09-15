"""
Enhanced conftest utilities with improved Testcontainers reliability.

This module provides enhanced fixtures and utilities that can be used alongside or as replacements
for the existing conftest.py fixtures, with improved error handling and reliability.
"""

import logging
import os
import time
from functools import wraps

import pytest

from .testcontainer_reliability import (
    ContainerHealthError,
    ContainerTimeoutError,
    Neo4jHealthChecker,
    RedisHealthChecker,
    enhanced_neo4j_container_setup,
    enhanced_redis_container_setup,
    retry_with_backoff,
)

logger = logging.getLogger(__name__)


def skip_if_container_unavailable(container_type: str):
    """
    Decorator to skip tests if container is unavailable.
    
    Args:
        container_type: Type of container ('neo4j' or 'redis')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ContainerHealthError, ContainerTimeoutError) as e:
                pytest.skip(f"{container_type} container unavailable: {e}")
        return wrapper
    return decorator


def wait_for_service_ready(service_url: str, timeout: int = 30, check_interval: float = 1.0):
    """
    Wait for a service to become ready.
    
    Args:
        service_url: URL of the service to check
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        
    Returns:
        bool: True if service is ready, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Basic connectivity check - can be enhanced per service type
            if "neo4j" in service_url.lower():
                from neo4j import GraphDatabase
                driver = GraphDatabase.driver(service_url, auth=("neo4j", "testpassword"))
                driver.verify_connectivity()
                driver.close()
                return True
            elif "redis" in service_url.lower():
                import redis
                client = redis.from_url(service_url)
                client.ping()
                client.close()
                return True
            else:
                # Generic HTTP check
                import requests
                response = requests.get(service_url, timeout=5)
                if response.status_code < 500:
                    return True
        except Exception as e:
            logger.debug(f"Service not ready: {e}")
            
        time.sleep(check_interval)
    
    return False


@retry_with_backoff(max_attempts=3, base_delay=1.0)
def enhanced_service_health_check(service_type: str, connection_params: dict):
    """
    Enhanced health check for various service types.
    
    Args:
        service_type: Type of service ('neo4j', 'redis', etc.)
        connection_params: Connection parameters for the service
        
    Returns:
        bool: True if service is healthy
        
    Raises:
        ContainerHealthError: If service is unhealthy
    """
    try:
        if service_type == "neo4j":
            health_checker = Neo4jHealthChecker()
            return health_checker.check_health(
                connection_params.get("uri"),
                connection_params.get("username", "neo4j"),
                connection_params.get("password", "testpassword")
            )
        elif service_type == "redis":
            health_checker = RedisHealthChecker()
            return health_checker.check_health(connection_params.get("uri"))
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    except Exception as e:
        raise ContainerHealthError(f"{service_type} health check failed: {e}") from e


def get_container_logs(container, lines: int = 50):
    """
    Get container logs for debugging.
    
    Args:
        container: Container instance
        lines: Number of lines to retrieve
        
    Returns:
        str: Container logs
    """
    try:
        if hasattr(container, 'get_logs'):
            return container.get_logs(tail=lines)
        elif hasattr(container, 'logs'):
            return container.logs(tail=lines)
        else:
            return "Logs not available for this container type"
    except Exception as e:
        return f"Error retrieving logs: {e}"


def diagnose_container_failure(container, service_type: str):
    """
    Diagnose container failure and provide helpful information.
    
    Args:
        container: Failed container instance
        service_type: Type of service that failed
        
    Returns:
        dict: Diagnostic information
    """
    diagnosis = {
        "service_type": service_type,
        "container_status": "unknown",
        "logs": "unavailable",
        "ports": "unknown",
        "recommendations": []
    }
    
    try:
        # Get container status
        if hasattr(container, 'get_container_host_ip'):
            diagnosis["host"] = container.get_container_host_ip()
        
        # Get logs
        diagnosis["logs"] = get_container_logs(container)
        
        # Get port information
        if hasattr(container, 'get_exposed_port'):
            try:
                if service_type == "neo4j":
                    diagnosis["ports"] = {
                        "bolt": container.get_exposed_port(7687),
                        "http": container.get_exposed_port(7474)
                    }
                elif service_type == "redis":
                    diagnosis["ports"] = {
                        "redis": container.get_exposed_port(6379)
                    }
            except Exception:
                diagnosis["ports"] = "port_detection_failed"
        
        # Add recommendations based on common issues
        if "Connection refused" in diagnosis["logs"]:
            diagnosis["recommendations"].append("Service may not be fully started")
        if "Authentication failed" in diagnosis["logs"]:
            diagnosis["recommendations"].append("Check authentication credentials")
        if "timeout" in diagnosis["logs"].lower():
            diagnosis["recommendations"].append("Increase timeout or check resource constraints")
            
    except Exception as e:
        diagnosis["diagnosis_error"] = str(e)
    
    return diagnosis
