#!/usr/bin/env python3
"""
Import TTA Grafana Dashboards into operational Grafana instance
Phase 2: Frontend Analytics Integration
"""

import json
import sys
from pathlib import Path

import requests


class GrafanaDashboardImporter:
    def __init__(self, grafana_url: str, username: str, password: str):
        self.grafana_url = grafana_url.rstrip("/")
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def import_dashboard(self, dashboard_file: Path) -> dict:
        """Import a single dashboard from JSON file"""
        try:
            with open(dashboard_file) as f:
                dashboard_json = json.load(f)

            # Prepare dashboard for import
            import_payload = {
                "dashboard": dashboard_json,
                "overwrite": True,
                "inputs": [],
                "folderId": 0,
            }

            # Remove id to allow Grafana to assign new one
            if "id" in import_payload["dashboard"]:
                del import_payload["dashboard"]["id"]

            # Import dashboard
            response = self.session.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=import_payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "dashboard": dashboard_file.name,
                    "id": result.get("id"),
                    "uid": result.get("uid"),
                    "url": result.get("url"),
                    "message": "Dashboard imported successfully",
                }
            return {
                "success": False,
                "dashboard": dashboard_file.name,
                "error": f"HTTP {response.status_code}: {response.text}",
            }

        except Exception as e:
            return {
                "success": False,
                "dashboard": dashboard_file.name,
                "error": f"Exception: {str(e)}",
            }

    def import_all_dashboards(self, dashboard_dir: Path) -> list:
        """Import all dashboard JSON files from directory"""
        results = []

        # Find all JSON dashboard files
        dashboard_files = list(dashboard_dir.glob("tta-*.json"))

        if not dashboard_files:
            print(f"No TTA dashboard files found in {dashboard_dir}")
            return results

        print(f"Found {len(dashboard_files)} TTA dashboard files to import:")
        for file in dashboard_files:
            print(f"  - {file.name}")

        # Import each dashboard
        for dashboard_file in dashboard_files:
            print(f"\nImporting {dashboard_file.name}...")
            result = self.import_dashboard(dashboard_file)
            results.append(result)

            if result["success"]:
                print(f"✅ {result['message']}")
                print(f"   Dashboard ID: {result.get('id')}")
                print(f"   Dashboard UID: {result.get('uid')}")
                print(f"   Dashboard URL: {result.get('url')}")
            else:
                print(f"❌ Failed to import {dashboard_file.name}")
                print(f"   Error: {result['error']}")

        return results

    def test_connection(self) -> bool:
        """Test connection to Grafana"""
        try:
            response = self.session.get(f"{self.grafana_url}/api/health")
            if response.status_code == 200:
                health_data = response.json()
                print(
                    f"✅ Connected to Grafana {health_data.get('version', 'unknown')}"
                )
                return True
            print(f"❌ Failed to connect to Grafana: HTTP {response.status_code}")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def list_existing_dashboards(self) -> list:
        """List existing dashboards"""
        try:
            response = self.session.get(f"{self.grafana_url}/api/search?type=dash-db")
            if response.status_code == 200:
                dashboards = response.json()
                print(f"📊 Found {len(dashboards)} existing dashboards:")
                for dashboard in dashboards:
                    print(
                        f"  - {dashboard.get('title', 'Untitled')} (ID: {dashboard.get('id')}, UID: {dashboard.get('uid')})"
                    )
                return dashboards
            print(f"❌ Failed to list dashboards: HTTP {response.status_code}")
            return []
        except Exception as e:
            print(f"❌ Error listing dashboards: {e}")
            return []


def main():
    # Configuration
    GRAFANA_URL = "http://localhost:3003"
    USERNAME = "admin"
    PASSWORD = "tta-admin-2024"
    DASHBOARD_DIR = Path("monitoring/grafana/dashboards")

    print("🚀 TTA Grafana Dashboard Importer - Phase 2")
    print("=" * 50)

    # Initialize importer
    importer = GrafanaDashboardImporter(GRAFANA_URL, USERNAME, PASSWORD)

    # Test connection
    print("Testing Grafana connection...")
    if not importer.test_connection():
        print(
            "❌ Cannot connect to Grafana. Please ensure it's running on http://localhost:3003"
        )
        sys.exit(1)

    # List existing dashboards
    print("\nListing existing dashboards...")
    existing_dashboards = importer.list_existing_dashboards()

    # Import TTA dashboards
    print(f"\nImporting TTA dashboards from {DASHBOARD_DIR}...")
    if not DASHBOARD_DIR.exists():
        print(f"❌ Dashboard directory not found: {DASHBOARD_DIR}")
        sys.exit(1)

    results = importer.import_all_dashboards(DASHBOARD_DIR)

    # Summary
    print("\n" + "=" * 50)
    print("📊 IMPORT SUMMARY")
    print("=" * 50)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"✅ Successfully imported: {len(successful)} dashboards")
    print(f"❌ Failed imports: {len(failed)} dashboards")

    if successful:
        print("\n🎯 Successfully imported dashboards:")
        for result in successful:
            print(
                f"  - {result['dashboard']} (ID: {result.get('id')}, UID: {result.get('uid')})"
            )

    if failed:
        print("\n⚠️  Failed dashboard imports:")
        for result in failed:
            print(f"  - {result['dashboard']}: {result['error']}")

    if successful:
        print(f"\n🌐 Access dashboards at: {GRAFANA_URL}/dashboards")
        print("📊 Phase 2: Dashboard Integration - COMPLETE")

    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
