"""
Genesis Session — the five-act metamorphic onboarding for TTA.

The Genesis Agent assembles the WorldSeed through a conversation that begins
as a setup wizard and ends with the player already inside their world.

See: docs/design/genesis-session.md
"""

from .narrator_voice import NARRATOR_VOICES, NarratorVoiceProfile, get_system_prompt
from .session_state import (
    ACT_TRANSITIONS,
    ACT_TURN_TARGETS,
    Act,
    GenesisSessionState,
    Turn,
)

__all__ = [
    "Act",
    "ACT_TRANSITIONS",
    "ACT_TURN_TARGETS",
    "GenesisSessionState",
    "Turn",
    "NARRATOR_VOICES",
    "NarratorVoiceProfile",
    "get_system_prompt",
]
