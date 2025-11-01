"""
TTA Home Lab Load Testing Configuration
Comprehensive load testing for multi-user scenarios and performance validation
"""

import logging
import random
import time

from locust import HttpUser, between, events, task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTAUser(HttpUser):
    """Simulated TTA user for load testing"""

    wait_time = between(2, 8)  # Wait 2-8 seconds between tasks

    def on_start(self):
        """Initialize user session"""
        self.user_id = f"load_test_user_{random.randint(1000, 9999)}"
        self.character_id = None
        self.session_id = None
        self.auth_token = None

        # Authenticate user
        self.authenticate()

        # Create a character
        self.create_character()

        logger.info(f"User {self.user_id} initialized")

    def authenticate(self):
        """Authenticate the test user"""
        auth_data = {
            "username": self.user_id,
            "password": "test_password_123",
            "email": f"{self.user_id}@loadtest.local",
        }

        # Register user (may fail if already exists, that's OK)
        self.client.post("/api/v1/auth/register", json=auth_data, catch_response=True)

        # Login user
        login_data = {"username": self.user_id, "password": "test_password_123"}

        with self.client.post(
            "/api/v1/auth/login", json=login_data, catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.client.headers.update(
                    {"Authorization": f"Bearer {self.auth_token}"}
                )
                response.success()
            else:
                logger.error(
                    f"Authentication failed for {self.user_id}: {response.text}"
                )
                response.failure("Authentication failed")

    def create_character(self):
        """Create a test character"""
        if not self.auth_token:
            return

        character_data = {
            "name": f"TestChar_{random.randint(100, 999)}",
            "background": "A brave adventurer seeking knowledge and growth",
            "personality_traits": ["curious", "determined", "empathetic"],
            "therapeutic_goals": ["stress_management", "confidence_building"],
            "appearance": {
                "description": "A determined individual with kind eyes",
                "avatar_url": None,
            },
        }

        with self.client.post(
            "/api/v1/characters", json=character_data, catch_response=True
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.character_id = data.get("character_id")
                response.success()
                logger.info(
                    f"Character created for {self.user_id}: {self.character_id}"
                )
            else:
                logger.error(
                    f"Character creation failed for {self.user_id}: {response.text}"
                )
                response.failure("Character creation failed")

    @task(3)
    def browse_dashboard(self):
        """Browse the player dashboard"""
        if not self.auth_token:
            return

        with self.client.get(
            "/api/v1/players/dashboard", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Dashboard access failed: {response.status_code}")

    @task(2)
    def view_characters(self):
        """View character list"""
        if not self.auth_token:
            return

        with self.client.get("/api/v1/characters", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Character list access failed: {response.status_code}"
                )

    @task(2)
    def browse_worlds(self):
        """Browse available worlds"""
        if not self.auth_token:
            return

        with self.client.get("/api/v1/worlds", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"World list access failed: {response.status_code}")

    @task(5)
    def start_chat_session(self):
        """Start a chat session"""
        if not self.auth_token or not self.character_id:
            return

        session_data = {
            "character_id": self.character_id,
            "world_id": "default_world",
            "session_type": "narrative",
        }

        with self.client.post(
            "/api/v1/sessions", json=session_data, catch_response=True
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.session_id = data.get("session_id")
                response.success()

                # Send a few messages in the session
                self.send_chat_messages()
            else:
                response.failure(f"Session creation failed: {response.status_code}")

    def send_chat_messages(self):
        """Send chat messages in the current session"""
        if not self.session_id:
            return

        messages = [
            "Hello, I'm ready to begin my adventure!",
            "What should I do first?",
            "I want to explore the world around me.",
            "Can you tell me more about this place?",
            "I'm feeling curious about what lies ahead.",
        ]

        for i in range(random.randint(2, 4)):
            message = random.choice(messages)
            message_data = {"content": message, "message_type": "user"}

            with self.client.post(
                f"/api/v1/sessions/{self.session_id}/messages",
                json=message_data,
                catch_response=True,
            ) as response:
                if response.status_code == 201:
                    response.success()
                    # Wait for AI response
                    time.sleep(random.uniform(1, 3))
                else:
                    response.failure(f"Message send failed: {response.status_code}")
                    break

    @task(1)
    def view_progress(self):
        """View progress and achievements"""
        if not self.auth_token:
            return

        with self.client.get("/api/v1/progress", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Progress access failed: {response.status_code}")

    @task(1)
    def health_check(self):
        """Perform health check"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    def on_stop(self):
        """Clean up when user stops"""
        logger.info(f"User {self.user_id} stopping")


class AdminUser(HttpUser):
    """Simulated admin user for administrative load testing"""

    wait_time = between(5, 15)
    weight = 1  # Lower weight than regular users

    def on_start(self):
        """Initialize admin session"""
        self.admin_id = f"admin_user_{random.randint(100, 999)}"
        self.auth_token = None
        self.authenticate_admin()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        # This would use admin credentials in a real scenario
        pass

    @task(1)
    def view_system_metrics(self):
        """View system metrics"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics access failed: {response.status_code}")


# Event handlers for custom metrics
@events.request.add_listener
def on_request(
    request_type, name, response_time, response_length, exception, context, **kwargs
):
    """Custom request handler for additional metrics"""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test start handler"""
    logger.info("TTA Load Test Starting")
    logger.info(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test stop handler"""
    logger.info("TTA Load Test Completed")

    # Log final statistics
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"Max response time: {stats.total.max_response_time:.2f}ms")


# Custom user classes for different scenarios
class HighActivityUser(TTAUser):
    """User with high activity levels"""

    wait_time = between(1, 3)
    weight = 2


class LowActivityUser(TTAUser):
    """User with low activity levels"""

    wait_time = between(10, 30)
    weight = 1


class MobileUser(TTAUser):
    """Simulated mobile user with different patterns"""

    wait_time = between(3, 10)
    weight = 3

    @task(1)
    def mobile_specific_task(self):
        """Mobile-specific behavior"""
        # Simulate mobile app behavior
        self.browse_dashboard()
        time.sleep(1)
        self.view_characters()
