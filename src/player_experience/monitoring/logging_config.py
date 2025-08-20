"""
Comprehensive logging configuration for production-grade monitoring.

This module provides structured logging, log aggregation, and integration
with monitoring systems for the Player Experience Interface.
"""

import logging
import logging.handlers
import json
import sys
import os
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field, asdict
from pathlib import Path
import threading
import queue
import time

from pythonjsonlogger import jsonlogger


class LogLevel(str, Enum):
    """Log levels for structured logging."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Categories for log messages."""
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    THERAPEUTIC = "therapeutic"
    USER_ACTION = "user_action"
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    WEBSOCKET = "websocket"
    ERROR = "error"
    AUDIT = "audit"


@dataclass
class LogContext:
    """Context information for structured logging."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    therapeutic_session_id: Optional[str] = None
    character_id: Optional[str] = None
    world_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class StructuredLogRecord:
    """Structured log record with enhanced metadata."""
    timestamp: str
    level: str
    logger_name: str
    message: str
    category: LogCategory
    context: LogContext = field(default_factory=LogContext)
    metadata: Dict[str, Any] = field(default_factory=dict)
    exception_info: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        record_dict = {
            "timestamp": self.timestamp,
            "level": self.level,
            "logger": self.logger_name,
            "message": self.message,
            "category": self.category.value,
            **self.context.to_dict(),
            **self.metadata
        }
        
        if self.exception_info:
            record_dict["exception"] = self.exception_info
        
        if self.stack_trace:
            record_dict["stack_trace"] = self.stack_trace
        
        return record_dict


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
        self.service_name = "player-experience-interface"
        self.version = "1.0.0"  # Should be loaded from config
    
    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add service metadata
        log_record['service'] = self.service_name
        log_record['version'] = self.version
        log_record['hostname'] = self.hostname
        log_record['process_id'] = os.getpid()
        log_record['thread_id'] = threading.get_ident()
        
        # Ensure timestamp is in ISO format
        if 'timestamp' not in log_record:
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add severity mapping for external systems
        level_mapping = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3,
            'CRITICAL': 4
        }
        log_record['severity'] = level_mapping.get(record.levelname, 1)
        
        # Add category if available
        if hasattr(record, 'category'):
            log_record['category'] = record.category
        
        # Add context if available
        if hasattr(record, 'context') and record.context:
            log_record.update(record.context.to_dict())
        
        # Add metadata if available
        if hasattr(record, 'metadata') and record.metadata:
            log_record.update(record.metadata)


class SecurityAuditFormatter(StructuredFormatter):
    """Specialized formatter for security audit logs."""
    
    def add_fields(self, log_record, record, message_dict):
        """Add security-specific fields."""
        super().add_fields(log_record, record, message_dict)
        
        # Mark as security audit log
        log_record['audit_type'] = 'security'
        log_record['compliance'] = 'gdpr'
        
        # Add security-specific metadata
        if hasattr(record, 'security_event'):
            log_record['security_event'] = record.security_event
        
        if hasattr(record, 'risk_level'):
            log_record['risk_level'] = record.risk_level


class TherapeuticAuditFormatter(StructuredFormatter):
    """Specialized formatter for therapeutic audit logs."""
    
    def add_fields(self, log_record, record, message_dict):
        """Add therapeutic-specific fields."""
        super().add_fields(log_record, record, message_dict)
        
        # Mark as therapeutic audit log
        log_record['audit_type'] = 'therapeutic'
        log_record['compliance'] = 'hipaa'
        
        # Add therapeutic-specific metadata
        if hasattr(record, 'therapeutic_event'):
            log_record['therapeutic_event'] = record.therapeutic_event
        
        if hasattr(record, 'intervention_type'):
            log_record['intervention_type'] = record.intervention_type
        
        if hasattr(record, 'safety_level'):
            log_record['safety_level'] = record.safety_level


class AsyncLogHandler(logging.Handler):
    """Asynchronous log handler for high-performance logging."""
    
    def __init__(self, target_handler: logging.Handler, queue_size: int = 10000):
        super().__init__()
        self.target_handler = target_handler
        self.queue = queue.Queue(maxsize=queue_size)
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.start_worker()
    
    def start_worker(self):
        """Start the background worker thread."""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.stop_event.clear()
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
    
    def stop_worker(self):
        """Stop the background worker thread."""
        self.stop_event.set()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
    
    def _worker_loop(self):
        """Background worker loop for processing log records."""
        while not self.stop_event.is_set():
            try:
                # Wait for log records with timeout
                try:
                    record = self.queue.get(timeout=1)
                    if record is None:  # Sentinel value to stop
                        break
                    self.target_handler.emit(record)
                    self.queue.task_done()
                except queue.Empty:
                    continue
            except Exception as e:
                # Log to stderr to avoid infinite recursion
                print(f"Error in async log handler: {e}", file=sys.stderr)
    
    def emit(self, record):
        """Emit a log record asynchronously."""
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            # Drop the log record if queue is full
            # In production, you might want to implement a different strategy
            pass
    
    def close(self):
        """Close the handler and clean up resources."""
        self.stop_worker()
        self.target_handler.close()
        super().close()


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str, context: Optional[LogContext] = None):
        self.logger = logging.getLogger(name)
        self.context = context or LogContext()
    
    def _log(self, level: LogLevel, message: str, category: LogCategory = LogCategory.SYSTEM,
            context: Optional[LogContext] = None, metadata: Optional[Dict[str, Any]] = None,
            exc_info: bool = False):
        """Internal logging method with structured data."""
        # Merge contexts
        final_context = LogContext()
        if self.context:
            final_context.__dict__.update(self.context.__dict__)
        if context:
            final_context.__dict__.update({k: v for k, v in context.__dict__.items() if v is not None})
        
        # Create log record
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=getattr(logging, level.value),
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=sys.exc_info() if exc_info else None
        )
        
        # Add structured data
        record.category = category.value
        record.context = final_context
        record.metadata = metadata or {}
        
        # Add exception information if available
        if exc_info and sys.exc_info()[0]:
            record.exception_info = {
                "type": sys.exc_info()[0].__name__,
                "message": str(sys.exc_info()[1]),
                "traceback": traceback.format_exc()
            }
        
        self.logger.handle(record)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM,
             context: Optional[LogContext] = None, metadata: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, category, context, metadata)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM,
            context: Optional[LogContext] = None, metadata: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log(LogLevel.INFO, message, category, context, metadata)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM,
               context: Optional[LogContext] = None, metadata: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log(LogLevel.WARNING, message, category, context, metadata)
    
    def error(self, message: str, category: LogCategory = LogCategory.ERROR,
             context: Optional[LogContext] = None, metadata: Optional[Dict[str, Any]] = None,
             exc_info: bool = True):
        """Log error message."""
        self._log(LogLevel.ERROR, message, category, context, metadata, exc_info)
    
    def critical(self, message: str, category: LogCategory = LogCategory.ERROR,
                context: Optional[LogContext] = None, metadata: Optional[Dict[str, Any]] = None,
                exc_info: bool = True):
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, category, context, metadata, exc_info)
    
    def security_audit(self, message: str, security_event: str, risk_level: str = "medium",
                      context: Optional[LogContext] = None, metadata: Optional[Dict[str, Any]] = None):
        """Log security audit event."""
        audit_metadata = {"security_event": security_event, "risk_level": risk_level}
        if metadata:
            audit_metadata.update(metadata)
        
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=logging.WARNING,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        record.category = LogCategory.SECURITY.value
        record.context = context or self.context
        record.metadata = audit_metadata
        record.security_event = security_event
        record.risk_level = risk_level
        
        self.logger.handle(record)
    
    def therapeutic_audit(self, message: str, therapeutic_event: str, intervention_type: str,
                         safety_level: str = "safe", context: Optional[LogContext] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """Log therapeutic audit event."""
        audit_metadata = {
            "therapeutic_event": therapeutic_event,
            "intervention_type": intervention_type,
            "safety_level": safety_level
        }
        if metadata:
            audit_metadata.update(metadata)
        
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=logging.INFO,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        record.category = LogCategory.THERAPEUTIC.value
        record.context = context or self.context
        record.metadata = audit_metadata
        record.therapeutic_event = therapeutic_event
        record.intervention_type = intervention_type
        record.safety_level = safety_level
        
        self.logger.handle(record)
    
    def with_context(self, **context_updates) -> 'StructuredLogger':
        """Create a new logger with updated context."""
        new_context = LogContext()
        if self.context:
            new_context.__dict__.update(self.context.__dict__)
        new_context.__dict__.update(context_updates)
        return StructuredLogger(self.logger.name, new_context)


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True,
    enable_async: bool = True,
    max_file_size: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 5
) -> Dict[str, logging.Logger]:
    """
    Set up comprehensive logging configuration.
    
    Args:
        log_level: Minimum log level to capture
        log_dir: Directory for log files (defaults to ./logs)
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_json: Enable JSON formatting
        enable_async: Enable asynchronous logging
        max_file_size: Maximum size for log files before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Dictionary of configured loggers
    """
    # Set up log directory
    if log_dir is None:
        log_dir = "./logs"
    
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if enable_json:
        console_formatter = StructuredFormatter()
        file_formatter = StructuredFormatter()
        security_formatter = SecurityAuditFormatter()
        therapeutic_formatter = TherapeuticAuditFormatter()
    else:
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        console_formatter = logging.Formatter(console_format)
        file_formatter = logging.Formatter(console_format)
        security_formatter = logging.Formatter(console_format)
        therapeutic_formatter = logging.Formatter(console_format)
    
    handlers = []
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        if enable_async:
            console_handler = AsyncLogHandler(console_handler)
        
        handlers.append(console_handler)
    
    # File handlers
    if enable_file:
        # Main application log
        app_handler = logging.handlers.RotatingFileHandler(
            log_path / "application.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        app_handler.setFormatter(file_formatter)
        app_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / "error.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setFormatter(file_formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Security audit log
        security_handler = logging.handlers.RotatingFileHandler(
            log_path / "security_audit.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        security_handler.setFormatter(security_formatter)
        security_handler.setLevel(logging.INFO)
        
        # Therapeutic audit log
        therapeutic_handler = logging.handlers.RotatingFileHandler(
            log_path / "therapeutic_audit.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        therapeutic_handler.setFormatter(therapeutic_formatter)
        therapeutic_handler.setLevel(logging.INFO)
        
        # Performance log
        performance_handler = logging.handlers.RotatingFileHandler(
            log_path / "performance.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        performance_handler.setFormatter(file_formatter)
        performance_handler.setLevel(logging.INFO)
        
        if enable_async:
            app_handler = AsyncLogHandler(app_handler)
            error_handler = AsyncLogHandler(error_handler)
            security_handler = AsyncLogHandler(security_handler)
            therapeutic_handler = AsyncLogHandler(therapeutic_handler)
            performance_handler = AsyncLogHandler(performance_handler)
        
        handlers.extend([app_handler, error_handler])
        
        # Set up specialized loggers
        security_logger = logging.getLogger("security")
        security_logger.addHandler(security_handler)
        security_logger.propagate = False
        
        therapeutic_logger = logging.getLogger("therapeutic")
        therapeutic_logger.addHandler(therapeutic_handler)
        therapeutic_logger.propagate = False
        
        performance_logger = logging.getLogger("performance")
        performance_logger.addHandler(performance_handler)
        performance_logger.propagate = False
    
    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Configure specific loggers
    loggers = {
        "root": root_logger,
        "app": logging.getLogger("player_experience"),
        "security": logging.getLogger("security"),
        "therapeutic": logging.getLogger("therapeutic"),
        "performance": logging.getLogger("performance"),
        "database": logging.getLogger("database"),
        "cache": logging.getLogger("cache"),
        "api": logging.getLogger("api"),
        "websocket": logging.getLogger("websocket"),
    }
    
    # Set appropriate levels
    for logger in loggers.values():
        logger.setLevel(getattr(logging, log_level.upper()))
    
    return loggers


def get_logger(name: str, context: Optional[LogContext] = None) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        context: Optional context information
    
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, context)


# Context managers for request-scoped logging

@dataclass
class RequestLoggingContext:
    """Context manager for request-scoped logging."""
    request_id: str
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    
    def __enter__(self) -> LogContext:
        """Enter the context and return log context."""
        return LogContext(
            request_id=self.request_id,
            user_id=self.user_id,
            endpoint=self.endpoint,
            ip_address=self.ip_address
        )
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        pass


def with_request_logging(request_id: str, user_id: Optional[str] = None,
                        endpoint: Optional[str] = None, ip_address: Optional[str] = None):
    """Context manager for request-scoped logging."""
    return RequestLoggingContext(request_id, user_id, endpoint, ip_address)


# Initialize default logging configuration
_logging_initialized = False


def ensure_logging_initialized():
    """Ensure logging is initialized with default configuration."""
    global _logging_initialized
    if not _logging_initialized:
        setup_logging()
        _logging_initialized = True