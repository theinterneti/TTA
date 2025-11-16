#!/usr/bin/env python3
"""
Start Phase 3 Analytics Services for Testing

This script starts the Phase 3 analytics services in a simplified mode
for integration testing with the existing TTA system.
"""

import subprocess
import sys
import time
from pathlib import Path

import requests


def start_service_in_background(service_file: str, port: int, service_name: str):
    """Start a service in the background."""
    print(f"🚀 Starting {service_name} on port {port}...")

    # Start the service
    process = subprocess.Popen(
        [sys.executable, service_file], cwd=Path(__file__).parent
    )

    # Wait a moment for startup
    time.sleep(3)

    # Check if service is running
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} started successfully on port {port}")
            return process
        print(f"❌ {service_name} health check failed")
        return None
    except Exception as e:
        print(f"❌ {service_name} failed to start: {e}")
        return None


def main():
    """Start all Phase 3 analytics services."""
    print("🎯 Starting Phase 3 Analytics Services for Testing")
    print("=" * 50)

    services = []

    # Start Analytics Aggregation Service
    aggregation_process = start_service_in_background(
        "src/analytics/services/aggregation_service.py",
        8095,
        "Analytics Aggregation Service",
    )
    if aggregation_process:
        services.append(aggregation_process)

    # Start Advanced Reporting Service
    reporting_process = start_service_in_background(
        "src/analytics/services/reporting_service.py",
        8096,
        "Advanced Reporting Service",
    )
    if reporting_process:
        services.append(reporting_process)

    # Start Real-time Monitoring Service
    monitoring_process = start_service_in_background(
        "src/analytics/services/realtime_monitoring_service.py",
        8097,
        "Real-time Monitoring Service",
    )
    if monitoring_process:
        services.append(monitoring_process)

    if services:
        print(f"\n🎉 Successfully started {len(services)} Phase 3 analytics services!")
        print("\n🌐 Service Access Points:")
        print("  - Analytics Aggregation: http://localhost:8095")
        print("  - Advanced Reporting: http://localhost:8096")
        print("  - Real-time Monitoring: http://localhost:8097")
        print(
            "\n⚠️  Services are running in background. Use Ctrl+C to stop this script."
        )
        print("   Note: Services will continue running after script exits.")

        try:
            # Keep script running
            while True:
                time.sleep(10)
                # Check if services are still running
                for i, process in enumerate(services):
                    if process.poll() is not None:
                        print(f"⚠️  Service {i + 1} has stopped")
        except KeyboardInterrupt:
            print("\n🛑 Stopping Phase 3 analytics services...")
            for process in services:
                process.terminate()
            print("✅ All services stopped")
    else:
        print("❌ Failed to start Phase 3 analytics services")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
