"""

# Logseq: [[TTA.dev/Monitoring/Logging_config]]
Mock logging configuration for TTA containerized deployment.
"""

import logging
from enum import Enum


class LogCategory(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    THERAPEUTIC = "therapeutic"
    API = "api"


class LogContext:
    def __init__(self, **kwargs):
        self.data = kwargs


def get_logger(name):
    """Return a standard Python logger."""
    return logging.getLogger(name)
