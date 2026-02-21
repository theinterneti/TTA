"""

# Logseq: [[TTA.dev/Packages/Tta-ai-framework/Src/Tta_ai/Orchestration/Validators]]
Validation helpers for agent orchestration data structures (Task 2.1).
"""

from __future__ import annotations

from pydantic import ValidationError

from .models import AgentMessage


def validate_agent_message(msg: AgentMessage) -> tuple[bool, str | None]:
    try:
        # Pydantic will raise if invalid
        AgentMessage(**msg.model_dump())
        return True, None
    except ValidationError as e:
        return False, str(e)
