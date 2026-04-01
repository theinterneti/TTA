"""
# Logseq: [[TTA/Components/Guide/Prompt]]
Guide prompt builder — injects Guide voice and intervention instructions
into NGA system prompts.
"""

from __future__ import annotations

import logging

from .intervention import InterventionType

logger = logging.getLogger(__name__)


# Intervention instruction fragments injected into NGA system prompt
_INTERVENTION_INSTRUCTIONS: dict[InterventionType, str] = {
    InterventionType.NONE: "",
    InterventionType.SENSORY_PAUSE: (
        "Mid-scene, weave in one brief sensory moment of beauty or stillness "
        "(a shaft of light, distant birdsong, the smell of rain) before continuing. "
        "Do not explain it; let it breathe."
    ),
    InterventionType.SOFT_PROMPT: (
        "At the very end of your response, add one gentle question from the Guide — "
        "story-adjacent, never clinical. Examples: 'What did that stir in you?' or "
        "'Is there something your character is carrying that hasn't been named yet?'"
    ),
    InterventionType.COMPANION_SHIFT: (
        "Shift the Guide's voice from narrator to companion. The Guide speaks directly "
        "to the player — warm, unhurried, not clinical. Acknowledge what the character "
        "has been through. Offer a moment of grounding before continuing the story. "
        "Use 'I notice...' or 'Take a moment...' language."
    ),
    InterventionType.BREAK_CHARACTER: (
        "STOP the narrative. The Guide speaks directly, outside the story: "
        "'I want to pause here for a moment. If any of this is touching something "
        "real for you, support is available. In the US: 988 Lifeline (call or text 988). "
        "You are not alone. Take all the time you need.' Then gently offer to return."
    ),
}

# Clinical language patterns the Guide must never use
_CLINICAL_PATTERNS = [
    "diagnose",
    "diagnosis",
    "disorder",
    "symptom",
    "treatment",
    "therapy session",
    "therapist",
    "you should feel",
    "you need to",
    "clinically",
    "psychiatric",
    "medically",
]


class GuidePromptBuilder:
    """Assembles NGA system prompt fragments for the Guide voice."""

    def build_voice_fragment(self, guide_voice_params: dict) -> str:
        """Build the base voice instruction from GuideVoice params dict.

        Args:
            guide_voice_params: Dict with keys: tone, formality,
                intervention_style, reflection_frequency (all strings).

        Returns:
            System prompt fragment string.
        """
        tone = guide_voice_params.get("tone", "warm-ancient")
        formality = guide_voice_params.get("formality", "neutral")
        reflection_frequency = guide_voice_params.get(
            "reflection_frequency", "occasional"
        )

        return (
            f"You are the Guide — the voice of this world. "
            f"Your tone is {tone}, your register is {formality}. "
            f"You are wise and warm; you never diagnose, never say 'you should feel', "
            f"never reference real-world therapy directly. All language stays "
            f"story-adjacent. Reflection prompts appear {reflection_frequency}."
        )

    def build_intervention_fragment(self, intervention_type: InterventionType) -> str:
        """Return the intervention instruction for this turn (empty if NONE)."""
        return _INTERVENTION_INSTRUCTIONS.get(intervention_type, "")

    def validate_no_clinical_language(self, text: str) -> list[str]:
        """Return list of clinical patterns found in text (empty = clean)."""
        found = []
        text_lower = text.lower()
        for pattern in _CLINICAL_PATTERNS:
            if pattern in text_lower:
                found.append(pattern)
        return found

    def build_full_system_addition(
        self,
        guide_voice_params: dict,
        intervention_type: InterventionType,
    ) -> str:
        """Combine voice fragment + intervention instruction into one string."""
        parts = [self.build_voice_fragment(guide_voice_params)]
        intervention = self.build_intervention_fragment(intervention_type)
        if intervention:
            parts.append(f"\n\nGUIDE INTERVENTION THIS TURN:\n{intervention}")
        return "\n".join(parts)
