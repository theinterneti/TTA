#!/usr/bin/env python3
"""
TTA Health Check Service
Provides Prometheus-compatible health check metrics for TTA services
"""

import asyncio
import logging
import time
from typing import Any

import psycopg2
import redis
import requests
import uvicorn
import yaml
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from neo4j import GraphDatabase
from prometheus_client import Counter, Gauge, Info, generate_latest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
service_up = Gauge(
    "tta_service_up",
    "Service health status (1=up, 0=down)",
    ["service", "instance", "environment"],
)
service_response_time = Gauge(
    "tta_service_response_time_seconds",
    "Service response time in seconds",
    ["service", "instance", "environment"],
)
health_check_total = Counter(
    "tta_health_checks_total",
    "Total number of health checks performed",
    ["service", "status"],
)
service_info = Info(
    "tta_service_info", "Service information", ["service", "instance", "environment"]
)


class HealthChecker:
    """Health check service for TTA infrastructure"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.services = self.config.get("services", {})
        self.metrics_config = self.config.get("metrics", {})

        # Set up logging
        log_config = self.config.get("logging", {})
        logging.getLogger().setLevel(getattr(logging, log_config.get("level", "INFO")))

        logger.info(f"Initialized health checker for {len(self.services)} services")

    async def check_redis_health(
        self, service_name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Check Redis service health"""
        start_time = time.time()
        try:
            r = redis.Redis(
                host=config["host"],
                port=config["port"],
                socket_timeout=config.get("timeout", 5),
                socket_connect_timeout=config.get("timeout", 5),
            )

            # Simple ping test
            r.ping()

            # Get basic info
            info = r.info()
            response_time = time.time() - start_time

            return {
                "status": "up",
                "response_time": response_time,
                "details": {
                    "version": info.get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                },
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Redis health check failed for {service_name}: {e}")
            return {"status": "down", "response_time": response_time, "error": str(e)}

    async def check_neo4j_health(
        self, service_name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Check Neo4j service health"""
        start_time = time.time()
        try:
            auth_config = config.get("auth", {})
            driver = GraphDatabase.driver(
                f"bolt://{config['host']}:{config['port']}",
                auth=(
                    auth_config.get("username", "neo4j"),
                    auth_config.get("password", "password"),
                ),
                connection_timeout=config.get("timeout", 10),
            )

            # Simple connectivity test
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]

                # Get database info
                db_info = session.run(
                    "CALL dbms.components() YIELD name, versions, edition"
                )
                components = list(db_info)

            driver.close()
            response_time = time.time() - start_time

            return {
                "status": "up",
                "response_time": response_time,
                "details": {
                    "components": [dict(record) for record in components]
                    if components
                    else [],
                    "test_query_result": test_value,
                },
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Neo4j health check failed for {service_name}: {e}")
            return {"status": "down", "response_time": response_time, "error": str(e)}

    async def check_postgres_health(
        self, service_name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Check PostgreSQL service health"""
        start_time = time.time()
        try:
            auth_config = config.get("auth", {})
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                user=auth_config.get("username", "postgres"),
                password=auth_config.get("password", "password"),
                database=auth_config.get("database", "postgres"),
                connect_timeout=config.get("timeout", 10),
            )

            # Simple connectivity test
            cursor = conn.cursor()
            cursor.execute("SELECT version(), current_database(), current_user")
            version_info = cursor.fetchone()

            cursor.close()
            conn.close()
            response_time = time.time() - start_time

            return {
                "status": "up",
                "response_time": response_time,
                "details": {
                    "version": version_info[0] if version_info else "unknown",
                    "database": version_info[1] if version_info else "unknown",
                    "user": version_info[2] if version_info else "unknown",
                },
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"PostgreSQL health check failed for {service_name}: {e}")
            return {"status": "down", "response_time": response_time, "error": str(e)}

    async def check_http_health(
        self, service_name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Check HTTP service health"""
        start_time = time.time()
        try:
            response = requests.get(
                config["url"], timeout=config.get("timeout", 10), allow_redirects=True
            )

            response_time = time.time() - start_time
            expected_status = config.get("expected_status", [200])

            if response.status_code in expected_status:
                return {
                    "status": "up",
                    "response_time": response_time,
                    "details": {
                        "status_code": response.status_code,
                        "content_length": len(response.content),
                        "headers": dict(response.headers),
                    },
                }
            return {
                "status": "down",
                "response_time": response_time,
                "error": f"Unexpected status code: {response.status_code}",
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"HTTP health check failed for {service_name}: {e}")
            return {"status": "down", "response_time": response_time, "error": str(e)}

    async def check_service_health(
        self, service_name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Check health of a single service based on its type"""
        service_type = config.get("type", "http")

        if service_type == "redis":
            return await self.check_redis_health(service_name, config)
        if service_type == "neo4j":
            return await self.check_neo4j_health(service_name, config)
        if service_type == "postgres":
            return await self.check_postgres_health(service_name, config)
        if service_type == "http":
            return await self.check_http_health(service_name, config)
        return {
            "status": "down",
            "response_time": 0,
            "error": f"Unknown service type: {service_type}",
        }

    async def update_metrics(self, service_name: str, result: dict[str, Any]):
        """Update Prometheus metrics based on health check result"""
        environment = "staging"
        instance = f"{service_name}-staging"

        # Update service status
        status_value = 1 if result["status"] == "up" else 0
        service_up.labels(
            service=service_name, instance=instance, environment=environment
        ).set(status_value)

        # Update response time
        service_response_time.labels(
            service=service_name, instance=instance, environment=environment
        ).set(result["response_time"])

        # Update counter
        health_check_total.labels(service=service_name, status=result["status"]).inc()

        # Update service info if available
        if "details" in result:
            details = result["details"]
            info_dict = {
                "status": result["status"],
                "last_check": str(int(time.time())),
            }

            # Add service-specific info
            if "version" in details:
                info_dict["version"] = str(details["version"])
            if "status_code" in details:
                info_dict["status_code"] = str(details["status_code"])

            service_info.labels(
                service=service_name, instance=instance, environment=environment
            ).info(info_dict)

    async def run_health_checks(self):
        """Run health checks for all configured services"""
        logger.info("Starting health check cycle")

        tasks = []
        for service_name, config in self.services.items():
            task = asyncio.create_task(self.check_service_health(service_name, config))
            tasks.append((service_name, task))

        # Wait for all health checks to complete
        for service_name, task in tasks:
            try:
                result = await task
                await self.update_metrics(service_name, result)
                logger.info(
                    f"Health check completed for {service_name}: {result['status']} ({result['response_time']:.3f}s)"
                )
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                # Update metrics with failure
                await self.update_metrics(
                    service_name,
                    {"status": "down", "response_time": 0, "error": str(e)},
                )

    async def start_monitoring(self, interval: int = 30):
        """Start continuous health monitoring"""
        logger.info(f"Starting health monitoring with {interval}s interval")

        while True:
            try:
                await self.run_health_checks()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retrying


# FastAPI app for metrics endpoint
app = FastAPI(title="TTA Health Check Service", version="1.0.0")


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.get("/health")
async def health():
    """Health check endpoint for the health checker itself"""
    return {"status": "healthy", "service": "tta-health-checker"}


async def main():
    """Main function to start the health check service"""
    # Initialize health checker
    health_checker = HealthChecker()

    # Start Prometheus metrics server
    metrics_port = health_checker.metrics_config.get("port", 8080)

    # Start health monitoring in background
    monitoring_task = asyncio.create_task(health_checker.start_monitoring())

    # Start FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=metrics_port, log_level="info")
    server = uvicorn.Server(config)

    logger.info(f"Starting TTA Health Check Service on port {metrics_port}")

    # Run both monitoring and web server
    await asyncio.gather(monitoring_task, server.serve())


if __name__ == "__main__":
    asyncio.run(main())
