"""
Minimal alerting interfaces to satisfy monitoring package imports during tests.

These stubs can be expanded later; for now, they provide structure needed by monitoring.__init__.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"


@dataclass
class Alert:
    message: str
    severity: AlertSeverity = AlertSeverity.INFO
    metadata: Optional[Dict[str, Any]] = None


class AlertManager:
    def __init__(self, channels: Optional[List[AlertChannel]] = None) -> None:
        self.channels = channels or [AlertChannel.LOG]

    def send(self, alert: Alert) -> None:
        # Minimal stub for tests. Extend to integrate with logging or external systems as needed.
        pass

