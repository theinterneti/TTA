#!/usr/bin/env python3
"""
Neo4j Authentication Resolution Script

This script helps resolve Neo4j authentication issues by testing different
credential combinations and providing guidance for setup.
"""

import logging
import subprocess
import sys
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jAuthResolver:
    """Resolves Neo4j authentication issues."""

    def __init__(self):
        self.neo4j_http_url = "http://localhost:7474"
        self.neo4j_bolt_url = "bolt://localhost:7687"

    def check_neo4j_service(self) -> bool:
        """Check if Neo4j service is running."""
        logger.info("🔍 Checking Neo4j service status...")

        try:
            # Check HTTP interface
            response = requests.get(f"{self.neo4j_http_url}/db/data/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Neo4j HTTP interface is accessible")
                return True
            if response.status_code == 401:
                logger.info("✅ Neo4j is running but requires authentication")
                return True
            logger.warning(f"⚠️  Neo4j HTTP returned {response.status_code}")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Neo4j service is not running or not accessible")
            return False
        except Exception as e:
            logger.error(f"❌ Neo4j service check failed: {e}")
            return False

    def test_credentials(self, username: str, password: str) -> bool:
        """Test Neo4j credentials."""
        logger.info(f"🔑 Testing credentials: {username}/{'*' * len(password)}")

        try:
            # Test with HTTP API
            response = requests.get(
                f"{self.neo4j_http_url}/db/data/",
                auth=(username, password),
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"✅ Credentials work: {username}")
                return True
            if response.status_code == 401:
                logger.warning(f"❌ Invalid credentials: {username}")
                return False
            logger.warning(f"⚠️  Unexpected response: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"❌ Credential test failed: {e}")
            return False

    def try_common_credentials(self) -> tuple[str, str] | None:
        """Try common Neo4j credential combinations."""
        logger.info("🔍 Trying common Neo4j credentials...")

        common_credentials = [
            ("neo4j", "password"),
            ("neo4j", "neo4j"),
            ("neo4j", "admin"),
            ("neo4j", ""),
            ("admin", "password"),
            ("admin", "admin"),
        ]

        for username, password in common_credentials:
            if self.test_credentials(username, password):
                return (username, password)

        logger.warning("❌ No common credentials worked")
        return None

    def reset_neo4j_password(self) -> bool:
        """Attempt to reset Neo4j password."""
        logger.info("🔧 Attempting to reset Neo4j password...")

        try:
            # Try to reset using neo4j-admin (if available)
            reset_commands = [
                ["neo4j-admin", "set-initial-password", "password"],
                ["docker", "exec", "neo4j", "neo4j-admin", "set-initial-password", "password"],
            ]

            for cmd in reset_commands:
                try:
                    logger.info(f"Trying: {' '.join(cmd)}")
                    result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)

                    if result.returncode == 0:
                        logger.info("✅ Password reset successful")
                        return True
                    logger.warning(f"Reset attempt failed: {result.stderr}")

                except FileNotFoundError:
                    logger.debug(f"Command not found: {cmd[0]}")
                    continue
                except Exception as e:
                    logger.warning(f"Reset attempt error: {e}")
                    continue

            logger.error("❌ All password reset attempts failed")
            return False

        except Exception as e:
            logger.error(f"❌ Password reset failed: {e}")
            return False

    def provide_setup_guidance(self):
        """Provide guidance for Neo4j setup."""
        logger.info("\n" + "=" * 60)
        logger.info("🛠️  NEO4J SETUP GUIDANCE")
        logger.info("=" * 60)

        logger.info("\n📋 Manual Setup Options:")
        logger.info("\n1. Docker Neo4j Setup:")
        logger.info("   docker run -d \\")
        logger.info("     --name neo4j \\")
        logger.info("     -p 7474:7474 -p 7687:7687 \\")
        logger.info("     -e NEO4J_AUTH=neo4j/password \\")
        logger.info("     neo4j:latest")

        logger.info("\n2. Local Neo4j Installation:")
        logger.info("   - Download from: https://neo4j.com/download/")
        logger.info("   - Set initial password: neo4j-admin set-initial-password password")
        logger.info("   - Start service: neo4j start")

        logger.info("\n3. Update .env file:")
        logger.info("   NEO4J_URI=bolt://localhost:7687")
        logger.info("   NEO4J_USERNAME=neo4j")
        logger.info("   NEO4J_PASSWORD=password")

        logger.info("\n4. Test connection:")
        logger.info("   python3 scripts/resolve_neo4j_auth.py")

    def run_complete_diagnosis(self) -> dict:
        """Run complete Neo4j authentication diagnosis."""
        logger.info("🎯 Neo4j Authentication Diagnosis")
        logger.info("=" * 50)

        results = {}

        # Check service
        results["service_running"] = self.check_neo4j_service()

        if not results["service_running"]:
            logger.error("❌ Neo4j service is not running")
            self.provide_setup_guidance()
            return results

        # Try credentials
        working_creds = self.try_common_credentials()
        results["credentials_found"] = working_creds is not None

        if working_creds:
            username, password = working_creds
            logger.info(f"✅ Working credentials found: {username}/{password}")

            # Update .env file
            env_file = Path(".env")
            if env_file.exists():
                logger.info("📝 Updating .env file with working credentials...")

                # Read current content
                with open(env_file) as f:
                    content = f.read()

                # Update or add Neo4j credentials
                lines = content.split('\n')
                updated_lines = []
                neo4j_vars_updated = set()

                for line in lines:
                    if line.startswith('NEO4J_USERNAME='):
                        updated_lines.append(f'NEO4J_USERNAME={username}')
                        neo4j_vars_updated.add('username')
                    elif line.startswith('NEO4J_PASSWORD='):
                        updated_lines.append(f'NEO4J_PASSWORD={password}')
                        neo4j_vars_updated.add('password')
                    elif line.startswith('NEO4J_URI='):
                        updated_lines.append('NEO4J_URI=bolt://localhost:7687')
                        neo4j_vars_updated.add('uri')
                    else:
                        updated_lines.append(line)

                # Add missing variables
                if 'username' not in neo4j_vars_updated:
                    updated_lines.append(f'NEO4J_USERNAME={username}')
                if 'password' not in neo4j_vars_updated:
                    updated_lines.append(f'NEO4J_PASSWORD={password}')
                if 'uri' not in neo4j_vars_updated:
                    updated_lines.append('NEO4J_URI=bolt://localhost:7687')

                # Write back
                with open(env_file, 'w') as f:
                    f.write('\n'.join(updated_lines))

                logger.info("✅ .env file updated with working credentials")

            results["env_updated"] = True
        else:
            logger.warning("❌ No working credentials found")

            # Try password reset
            if self.reset_neo4j_password():
                # Test again with default password
                if self.test_credentials("neo4j", "password"):
                    logger.info("✅ Password reset successful, credentials now work")
                    results["credentials_found"] = True
                    results["password_reset"] = True

            if not results.get("credentials_found", False):
                self.provide_setup_guidance()

        return results

def main():
    """Main execution."""
    resolver = Neo4jAuthResolver()
    results = resolver.run_complete_diagnosis()

    logger.info("\n" + "=" * 50)
    logger.info("📊 DIAGNOSIS RESULTS")
    logger.info("=" * 50)

    for key, value in results.items():
        status = "✅ SUCCESS" if value else "❌ FAILED"
        logger.info(f"{key.replace('_', ' ').title():20} : {status}")

    if results.get("credentials_found", False):
        logger.info("\n🎉 Neo4j authentication resolved!")
        logger.info("You can now proceed with TTA system startup.")
        return 0
    logger.error("\n⚠️  Neo4j authentication still needs attention.")
    logger.info("Please follow the setup guidance above.")
    return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Diagnosis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
