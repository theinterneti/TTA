#!/usr/bin/env python3
"""
TTA Staging Test User Creation Script
Creates test users for staging environment validation
"""

import asyncio
import json
import logging
import random
import sys
from pathlib import Path

import aiohttp
import click
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

fake = Faker()


class TestUserCreator:
    """Creates test users for TTA staging environment."""

    def __init__(self, api_url: str, timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_api_health(self) -> bool:
        """Check if the API is healthy and accessible."""
        try:
            async with self.session.get(f"{self.api_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(
                        f"API health check passed: {data.get('status', 'unknown')}"
                    )
                    return True
                logger.error(f"API health check failed: HTTP {response.status}")
                return False
        except Exception as e:
            logger.error(f"API health check error: {e}")
            return False

    def generate_user_data(self, user_type: str = "basic") -> dict:
        """Generate realistic test user data."""
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"test_{first_name.lower()}_{last_name.lower()}_{random.randint(1000, 9999)}"
        email = f"{username}@staging.tta"

        user_data = {
            "username": username,
            "email": email,
            "password": "TestPassword123!",
            "first_name": first_name,
            "last_name": last_name,
            "is_test_user": True,
            "test_group": user_type,
            "metadata": {
                "created_by": "test_script",
                "user_type": user_type,
                "fake_data": True,
                "preferences": {
                    "theme": random.choice(["light", "dark"]),
                    "language": "en",
                    "notifications": random.choice([True, False]),
                },
            },
        }

        # Add type-specific data
        if user_type == "admin":
            user_data["metadata"]["admin_level"] = "test_admin"
        elif user_type == "power_user":
            user_data["metadata"]["experience_level"] = "advanced"
        elif user_type == "casual":
            user_data["metadata"]["experience_level"] = "beginner"

        return user_data

    async def create_user(self, user_data: dict) -> dict | None:
        """Create a single test user."""
        try:
            async with self.session.post(
                f"{self.api_url}/api/v1/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    logger.info(f"Created user: {user_data['username']}")
                    return {
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "user_id": result.get("user_id"),
                        "test_group": user_data["test_group"],
                        "created": True,
                    }
                if response.status == 409:
                    logger.warning(f"User already exists: {user_data['username']}")
                    return {
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "user_id": None,
                        "test_group": user_data["test_group"],
                        "created": False,
                        "error": "already_exists",
                    }
                error_text = await response.text()
                logger.error(
                    f"Failed to create user {user_data['username']}: HTTP {response.status} - {error_text}"
                )
                return None
        except Exception as e:
            logger.error(f"Error creating user {user_data['username']}: {e}")
            return None

    async def create_users_batch(
        self, user_configs: list[dict], batch_size: int = 10
    ) -> list[dict]:
        """Create users in batches to avoid overwhelming the API."""
        created_users = []

        for i in range(0, len(user_configs), batch_size):
            batch = user_configs[i : i + batch_size]
            logger.info(f"Creating batch {i // batch_size + 1} ({len(batch)} users)")

            # Create tasks for concurrent execution
            tasks = [self.create_user(user_config) for user_config in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Batch creation error: {result}")
                elif result:
                    created_users.append(result)

            # Small delay between batches
            if i + batch_size < len(user_configs):
                await asyncio.sleep(1)

        return created_users

    async def verify_user_login(self, username: str, password: str) -> bool:
        """Verify that a created user can log in."""
        try:
            login_data = {"username": username, "password": password}

            async with self.session.post(
                f"{self.api_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return "access_token" in result
                return False
        except Exception as e:
            logger.error(f"Login verification error for {username}: {e}")
            return False


def generate_user_distribution(total_count: int) -> list[dict]:
    """Generate a realistic distribution of user types."""
    user_configs = []

    # Distribution: 70% basic, 20% casual, 8% power_user, 2% admin
    basic_count = int(total_count * 0.70)
    casual_count = int(total_count * 0.20)
    power_user_count = int(total_count * 0.08)
    admin_count = max(1, total_count - basic_count - casual_count - power_user_count)

    logger.info(
        f"User distribution: {basic_count} basic, {casual_count} casual, {power_user_count} power_user, {admin_count} admin"
    )

    # Generate user configurations
    for _ in range(basic_count):
        user_configs.append({"type": "basic"})

    for _ in range(casual_count):
        user_configs.append({"type": "casual"})

    for _ in range(power_user_count):
        user_configs.append({"type": "power_user"})

    for _ in range(admin_count):
        user_configs.append({"type": "admin"})

    # Shuffle to randomize creation order
    random.shuffle(user_configs)
    return user_configs


@click.command()
@click.option("--api-url", required=True, help="TTA API base URL")
@click.option("--count", default=50, help="Number of test users to create")
@click.option(
    "--output", default="data/test-users.json", help="Output file for created users"
)
@click.option("--batch-size", default=10, help="Batch size for user creation")
@click.option("--verify-login", is_flag=True, help="Verify login for created users")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
async def main(
    api_url: str,
    count: int,
    output: str,
    batch_size: int,
    verify_login: bool,
    verbose: bool,
):
    """Create test users for TTA staging environment."""

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"Creating {count} test users for {api_url}")

    # Ensure output directory exists
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with TestUserCreator(api_url) as creator:
        # Check API health
        if not await creator.check_api_health():
            logger.error("API health check failed. Exiting.")
            sys.exit(1)

        # Generate user configurations
        user_configs = generate_user_distribution(count)

        # Generate user data
        user_data_list = []
        for config in user_configs:
            user_data = creator.generate_user_data(config["type"])
            user_data_list.append(user_data)

        # Create users
        logger.info(f"Creating {len(user_data_list)} users in batches of {batch_size}")
        created_users = await creator.create_users_batch(user_data_list, batch_size)

        # Verify logins if requested
        if verify_login and created_users:
            logger.info("Verifying user logins...")
            verification_tasks = []

            for user in created_users[
                : min(10, len(created_users))
            ]:  # Verify first 10 users
                if user.get("created"):
                    verification_tasks.append(
                        creator.verify_user_login(user["username"], "TestPassword123!")
                    )

            if verification_tasks:
                verification_results = await asyncio.gather(*verification_tasks)
                successful_logins = sum(verification_results)
                logger.info(
                    f"Login verification: {successful_logins}/{len(verification_results)} successful"
                )

        # Save results
        output_data = {
            "metadata": {
                "total_requested": count,
                "total_created": len([u for u in created_users if u.get("created")]),
                "total_existing": len(
                    [u for u in created_users if not u.get("created")]
                ),
                "api_url": api_url,
                "created_at": fake.iso8601(),
                "batch_size": batch_size,
            },
            "users": created_users,
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"Results saved to {output_path}")
        logger.info(
            f"Successfully created {output_data['metadata']['total_created']} users"
        )

        # Summary
        created_count = output_data["metadata"]["total_created"]
        existing_count = output_data["metadata"]["total_existing"]

        if created_count > 0:
            logger.info(f"✅ Created {created_count} new test users")
        if existing_count > 0:
            logger.info(f"ℹ️  Found {existing_count} existing users")

        if created_count == 0 and existing_count == 0:
            logger.error("❌ No users were created or found")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
