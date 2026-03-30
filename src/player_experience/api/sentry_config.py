"""

# Logseq: [[TTA.dev/Player_experience/Api/Sentry_config]]
Sentry configuration for error monitoring and performance tracking.

This module handles the initialization and configuration of Sentry SDK
for the TTA Player Experience Interface API.
"""

import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from .config import APISettings

logger = logging.getLogger(__name__)


def init_sentry(settings: APISettings) -> None:
    """
    Initialize Sentry SDK with appropriate configuration.

    Args:
        settings: API settings containing Sentry configuration
    """
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not configured, skipping Sentry initialization")
        return

    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    # Configure FastAPI integration
    fastapi_integration = FastApiIntegration()

    # Configure Starlette integration
    starlette_integration = StarletteIntegration(transaction_style="endpoint")

    # Configure database integrations
    sqlalchemy_integration = SqlalchemyIntegration()
    redis_integration = RedisIntegration()

    # Initialize Sentry
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        integrations=[
            logging_integration,
            fastapi_integration,
            starlette_integration,
            sqlalchemy_integration,
            redis_integration,
        ],
        # Performance monitoring
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        # Data privacy settings
        send_default_pii=settings.sentry_send_default_pii,
        # Additional configuration for therapeutic application
        before_send=_before_send_filter,
        before_send_transaction=_before_send_transaction_filter,
        # Release tracking (can be set via environment variable)
        release=None,  # Will be auto-detected from git or environment
        # Additional options for better error context
        attach_stacktrace=True,
        send_client_reports=True,
        # Logging configuration
        debug=settings.debug,
        enable_logs=settings.sentry_enable_logs,
    )

    logger.info(
        f"Sentry initialized for environment '{settings.sentry_environment}' "
        f"with traces_sample_rate={settings.sentry_traces_sample_rate}"
    )


def _before_send_filter(event, hint):
    """
    Filter sensitive data before sending to Sentry.

    This is critical for a therapeutic application to ensure
    no sensitive user data is accidentally sent to Sentry.

    Args:
        event: Sentry event data
        hint: Additional context about the event

    Returns:
        Modified event or None to drop the event
    """
    # Remove sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["authorization", "cookie", "x-api-key", "x-auth-token"]

        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"

    # Remove sensitive query parameters
    if "request" in event and "query_string" in event["request"]:
        # Filter out any query parameters that might contain sensitive data
        query_string = event["request"]["query_string"]
        if query_string and any(
            param in query_string.lower()
            for param in ["token", "key", "secret", "password"]
        ):
            event["request"]["query_string"] = "[Filtered]"

    # Remove sensitive form data
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            sensitive_fields = [
                "password",
                "token",
                "secret",
                "api_key",
                "therapeutic_notes",
            ]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "[Filtered]"

    # Filter out therapeutic session content from exception messages
    if "exception" in event:
        for exception in event["exception"]["values"]:
            if "value" in exception:
                # Replace any potential therapeutic content patterns
                exception["value"] = _sanitize_therapeutic_content(exception["value"])

    return event


def _before_send_transaction_filter(event, hint):
    """
    Filter transaction data before sending to Sentry.

    Args:
        event: Sentry transaction event
        hint: Additional context

    Returns:
        Modified event or None to drop the event
    """
    # Remove sensitive transaction data
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            sensitive_fields = ["therapeutic_content", "user_input", "session_notes"]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "[Filtered]"

    return event


def _sanitize_therapeutic_content(text: str) -> str:
    """
    Sanitize text that might contain therapeutic content.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text with therapeutic content removed
    """
    if not text:
        return text

    # List of patterns that might indicate therapeutic content
    therapeutic_patterns = [
        "therapeutic session",
        "patient said",
        "user shared",
        "emotional state",
        "mental health",
        "therapy note",
        "session transcript",
    ]

    text_lower = text.lower()
    for pattern in therapeutic_patterns:
        if pattern in text_lower:
            return "[Therapeutic content filtered for privacy]"

    return text


def capture_therapeutic_error(
    error: Exception,
    context: dict | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
) -> None:
    """
    Capture an error with therapeutic application context.

    This function provides a safe way to report errors while
    ensuring no sensitive therapeutic data is included.

    Args:
        error: The exception to report
        context: Additional context (will be sanitized)
        user_id: User ID (will be hashed for privacy)
        session_id: Session ID (will be hashed for privacy)
    """
    with sentry_sdk.push_scope() as scope:
        # Add sanitized context
        if context:
            sanitized_context = {
                key: (
                    _sanitize_therapeutic_content(str(value))
                    if isinstance(value, str)
                    else value
                )
                for key, value in context.items()
                if key not in ["therapeutic_content", "user_input", "session_notes"]
            }
            scope.set_context("application_context", sanitized_context)

        # Add hashed user/session IDs for tracking without exposing actual IDs
        if user_id:
            import hashlib

            hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
            scope.set_user({"id": hashed_user_id})

        if session_id:
            import hashlib

            hashed_session_id = hashlib.sha256(session_id.encode()).hexdigest()[:16]
            scope.set_tag("session_hash", hashed_session_id)

        # Add therapeutic application tags
        scope.set_tag("application", "tta-therapeutic")
        scope.set_tag("component", "player-experience")

        sentry_sdk.capture_exception(error)


def capture_therapeutic_message(
    message: str, level: str = "info", context: dict | None = None
) -> None:
    """
    Capture a message with therapeutic application context.

    Args:
        message: Message to capture
        level: Log level (info, warning, error)
        context: Additional context (will be sanitized)
    """
    with sentry_sdk.push_scope() as scope:
        # Add sanitized context
        if context:
            sanitized_context = {
                key: (
                    _sanitize_therapeutic_content(str(value))
                    if isinstance(value, str)
                    else value
                )
                for key, value in context.items()
                if key not in ["therapeutic_content", "user_input", "session_notes"]
            }
            scope.set_context("application_context", sanitized_context)

        # Add therapeutic application tags
        scope.set_tag("application", "tta-therapeutic")
        scope.set_tag("component", "player-experience")

        sentry_sdk.capture_message(message, level=level)  # type: ignore[arg-type]
