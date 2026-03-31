"""
# Logseq: [[TTA/Components/First_scene/Models]]
First scene specification — the structured brief passed to NGA for first-scene
prose generation.

Issue: #286
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SceneLocation(BaseModel):
    """The concrete place where the story begins."""

    name: str
    description: str
    atmosphere: str
    time_of_day: str = "dawn"


class SceneHook(BaseModel):
    """The narrative invitation at the end of the first scene."""

    hook_text: str
    hook_type: str = "open"
    # "open"       — player can do anything
    # "decision"   — two clear paths presented
    # "observation"— player notices something that demands response


class FirstSceneSpec(BaseModel):
    """
    Structured specification for NGA to generate the first scene prose.

    Built by FirstSceneSpecBuilder from WorldSeed + PlayerCharacter dict.
    Passed to NGAAgent.generate() as structured context.
    """

    # World context
    world_tone: str
    power_source: str
    world_tagline: str = ""

    # Scene elements
    location: SceneLocation
    protagonist_intro: str
    hook: SceneHook

    # Guide presence
    guide_name: str = ""
    guide_intro_line: str = ""
    guide_entity_type: str = ""

    # Generation params
    target_word_count: int = Field(default=300, gt=0)
    pov: str = "second_person"  # "second_person" | "third_person"

    def to_nga_prompt(self) -> str:
        """Render the spec as a compact NGA system prompt addition."""
        parts = [
            "FIRST SCENE BRIEF",
            f"World tone: {self.world_tone} | Power: {self.power_source}",
        ]
        if self.world_tagline:
            parts.append(f"World: {self.world_tagline}")
        parts += [
            f"Location: {self.location.name} — {self.location.description}",
            f"Atmosphere: {self.location.atmosphere}, {self.location.time_of_day}",
            f"Protagonist: {self.protagonist_intro}",
        ]
        if self.guide_name:
            parts.append(
                f"Guide ({self.guide_entity_type}): {self.guide_name}"
                f' — "{self.guide_intro_line}"'
            )
        parts.append(f"Hook: {self.hook.hook_text}")
        parts.append(
            f"Target length: ~{self.target_word_count} words. POV: {self.pov}."
        )
        return "\n".join(parts)
