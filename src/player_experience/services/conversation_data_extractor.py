"""
Conversation Data Extractor

This module provides functionality to extract and validate character data
from conversation history, mapping conversational responses to character
model fields with intelligent parsing and validation.
"""

import logging
import re
from typing import Any

from ..models.conversation_state import (
    CollectedData,
    ConversationMessage,
    ConversationState,
)
from ..services.conversation_scripts import ConversationStage

logger = logging.getLogger(__name__)


class ConversationDataExtractor:
    """Extracts character data from conversation history."""

    def __init__(self):
        self.extraction_patterns = self._initialize_extraction_patterns()
        self.validation_rules = self._initialize_validation_rules()

    def _initialize_extraction_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize patterns for extracting data from conversational responses."""
        return {
            "name": {
                "patterns": [
                    r"(?:call me|name is|i'm|i am)\s+([a-zA-Z\s\-']+)",
                    r"my name is\s+([a-zA-Z\s\-']+)",
                    r"you can call me\s+([a-zA-Z\s\-']+)",
                ],
                "cleanup": lambda x: re.sub(r"[^a-zA-Z\s\-\']", "", x).strip(),
            },
            "age_range": {
                "patterns": [
                    r"\b(child|kid|young)\b",
                    r"\b(teen|teenager|adolescent)\b",
                    r"\b(adult|grown)\b",
                    r"\b(elder|senior|older)\b",
                ],
                "mapping": {
                    "child": ["child", "kid", "young"],
                    "teen": ["teen", "teenager", "adolescent"],
                    "adult": ["adult", "grown"],
                    "elder": ["elder", "senior", "older"],
                },
            },
            "gender_identity": {
                "patterns": [
                    r"(?:i identify as|i am|i'm)\s+([\w\-\s]+)",
                    r"my gender is\s+([\w\-\s]+)",
                    r"gender.*?(?:is|:)\s*([\w\-\s]+)",
                ],
                "cleanup": lambda x: x.strip().lower(),
            },
            "personality_traits": {
                "patterns": [
                    r"i am\s+([\w\s,]+?)(?:\.|$)",
                    r"i'm\s+([\w\s,]+?)(?:\.|$)",
                    r"describe.*?me.*?as\s+([\w\s,]+?)(?:\.|$)",
                    r"personality.*?(?:is|:)\s*([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "core_values": {
                "patterns": [
                    r"(?:value|important|matters?).*?(?:is|are|:)\s*([\w\s,]+?)(?:\.|$)",
                    r"(?:believe in|care about)\s+([\w\s,]+?)(?:\.|$)",
                    r"principles.*?(?:are|:)\s*([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "strengths_and_skills": {
                "patterns": [
                    r"(?:good at|skilled at|talented at)\s+([\w\s,]+?)(?:\.|$)",
                    r"(?:strengths?|abilities?).*?(?:are|:)\s*([\w\s,]+?)(?:\.|$)",
                    r"i can\s+([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "primary_concerns": {
                "patterns": [
                    r"(?:struggling with|worried about|concerned about)\s+([\w\s,]+?)(?:\.|$)",
                    r"(?:problems?|issues?|challenges?).*?(?:are|:)\s*([\w\s,]+?)(?:\.|$)",
                    r"(?:anxiety|depression|stress).*?(?:about|with)\s+([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "life_goals": {
                "patterns": [
                    r"(?:want to|hope to|goal is to)\s+([\w\s,]+?)(?:\.|$)",
                    r"(?:goals?|dreams?).*?(?:are|:)\s*([\w\s,]+?)(?:\.|$)",
                    r"(?:achieve|accomplish)\s+([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "therapeutic_goals": {
                "patterns": [
                    r"(?:therapy|therapeutic|healing).*?(?:goal|want|hope).*?(?:is|to)\s+([\w\s,]+?)(?:\.|$)",
                    r"(?:work on|improve|change)\s+([\w\s,]+?)(?:\.|$)",
                    r"success.*?(?:would be|looks like)\s+([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "preferred_intensity": {
                "patterns": [
                    r"\b(gentle|slow|easy|gradual)\b",
                    r"\b(balanced|moderate|medium|steady)\b",
                    r"\b(intensive|intense|fast|challenging|deep)\b",
                ],
                "mapping": {
                    "low": ["gentle", "slow", "easy", "gradual"],
                    "medium": ["balanced", "moderate", "medium", "steady"],
                    "high": ["intensive", "intense", "fast", "challenging", "deep"],
                },
            },
            "comfort_zones": {
                "patterns": [
                    r"(?:comfortable with|safe.*?discussing|okay.*?talking about)\s+([\w\s,]+?)(?:\.|$)",
                    r"(?:comfort zones?|safe topics?).*?(?:are|:)\s*([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "challenge_areas": {
                "patterns": [
                    r"(?:ready to.*?work on|challenge.*?myself.*?with|push.*?myself.*?on)\s+([\w\s,]+?)(?:\.|$)",
                    r"(?:difficult|hard|challenging).*?(?:areas?|topics?).*?(?:are|:)\s*([\w\s,]+?)(?:\.|$)",
                ],
                "list_separators": [",", "and", "or", ";"],
            },
            "readiness_level": {
                "patterns": [
                    r"(\d+)(?:%|/10|/100)",
                    r"\b(very ready|completely ready|fully ready)\b",
                    r"\b(ready|prepared)\b",
                    r"\b(somewhat|partially|kind of)\b",
                    r"\b(not very|barely|slightly)\b",
                    r"\b(not ready|unprepared)\b",
                ],
                "mapping": {
                    0.9: ["very ready", "completely ready", "fully ready"],
                    0.7: ["ready", "prepared"],
                    0.5: ["somewhat", "partially", "kind of"],
                    0.3: ["not very", "barely", "slightly"],
                    0.1: ["not ready", "unprepared"],
                },
            },
        }

    def _initialize_validation_rules(self) -> dict[str, dict[str, Any]]:
        """Initialize validation rules for extracted data."""
        return {
            "name": {
                "min_length": 2,
                "max_length": 50,
                "pattern": r"^[a-zA-Z\s\-']+$",
                "required": True,
            },
            "age_range": {
                "valid_values": ["child", "teen", "adult", "elder"],
                "required": True,
            },
            "gender_identity": {"min_length": 1, "max_length": 50, "required": False},
            "readiness_level": {"min_value": 0.0, "max_value": 1.0, "required": False},
            "preferred_intensity": {
                "valid_values": ["low", "medium", "high"],
                "required": False,
            },
        }

    def extract_data_from_conversation(
        self, conversation_state: ConversationState
    ) -> CollectedData:
        """
        Extract character data from conversation history.

        Args:
            conversation_state: Current conversation state with message history

        Returns:
            CollectedData object with extracted information
        """
        collected_data = CollectedData()

        # Process messages by stage for context-aware extraction
        messages_by_stage = self._group_messages_by_stage(
            conversation_state.message_history
        )

        for stage, messages in messages_by_stage.items():
            user_messages = [msg for msg in messages if msg.sender == "user"]
            combined_text = " ".join([msg.content for msg in user_messages])

            # Extract data based on conversation stage
            stage_data = self._extract_stage_data(stage, combined_text)
            self._merge_extracted_data(collected_data, stage_data)

        # Post-process and validate extracted data
        self._post_process_data(collected_data)

        logger.info(
            f"Extracted data from {len(conversation_state.message_history)} messages"
        )
        return collected_data

    def _group_messages_by_stage(
        self, messages: list[ConversationMessage]
    ) -> dict[ConversationStage, list[ConversationMessage]]:
        """Group messages by conversation stage."""
        grouped = {}
        current_stage = ConversationStage.WELCOME

        for message in messages:
            # Update current stage if message has stage metadata
            if (
                hasattr(message, "metadata")
                and message.metadata
                and "stage" in message.metadata
            ):
                try:
                    current_stage = ConversationStage(message.metadata["stage"])
                except ValueError:
                    pass  # Keep current stage if invalid

            if current_stage not in grouped:
                grouped[current_stage] = []
            grouped[current_stage].append(message)

        return grouped

    def _extract_stage_data(
        self, stage: ConversationStage, text: str
    ) -> dict[str, Any]:
        """Extract data relevant to a specific conversation stage."""
        stage_data = {}

        # Define which fields to extract for each stage
        stage_field_mapping = {
            ConversationStage.WELCOME: ["name"],
            ConversationStage.IDENTITY: ["age_range", "gender_identity"],
            ConversationStage.APPEARANCE: ["physical_description", "clothing_style"],
            ConversationStage.BACKGROUND: ["backstory", "personality_traits"],
            ConversationStage.VALUES: [
                "core_values",
                "strengths_and_skills",
                "life_goals",
            ],
            ConversationStage.CONCERNS: ["primary_concerns"],
            ConversationStage.GOALS: ["therapeutic_goals"],
            ConversationStage.PREFERENCES: [
                "preferred_intensity",
                "comfort_zones",
                "challenge_areas",
            ],
            ConversationStage.READINESS: ["readiness_level"],
        }

        fields_to_extract = stage_field_mapping.get(stage, [])

        for field in fields_to_extract:
            if field in self.extraction_patterns:
                extracted_value = self._extract_field_value(field, text)
                if extracted_value is not None:
                    stage_data[field] = extracted_value

        return stage_data

    def _extract_field_value(self, field: str, text: str) -> Any:
        """Extract value for a specific field from text."""
        pattern_config = self.extraction_patterns.get(field, {})
        patterns = pattern_config.get("patterns", [])

        text_lower = text.lower()

        # Try each pattern
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                if field in [
                    "personality_traits",
                    "core_values",
                    "strengths_and_skills",
                    "primary_concerns",
                    "life_goals",
                    "therapeutic_goals",
                    "comfort_zones",
                    "challenge_areas",
                ]:
                    # Handle list fields
                    return self._extract_list_values(
                        matches, pattern_config.get("list_separators", [","])
                    )
                elif field in ["age_range", "preferred_intensity"]:
                    # Handle mapped fields
                    return self._map_extracted_value(
                        matches[0], pattern_config.get("mapping", {})
                    )
                elif field == "readiness_level":
                    # Handle readiness level
                    return self._extract_readiness_level(
                        matches[0], pattern_config.get("mapping", {})
                    )
                else:
                    # Handle single value fields
                    value = matches[0]
                    cleanup_func = pattern_config.get("cleanup")
                    if cleanup_func:
                        value = cleanup_func(value)
                    return value

        # Special handling for direct text fields
        if field in ["physical_description", "backstory"]:
            return text.strip() if text.strip() else None

        return None

    def _extract_list_values(
        self, matches: list[str], separators: list[str]
    ) -> list[str]:
        """Extract list values from matched text."""
        all_items = []

        for match in matches:
            # Split by separators
            items = [match]
            for separator in separators:
                new_items = []
                for item in items:
                    new_items.extend([i.strip() for i in item.split(separator)])
                items = new_items

            # Clean and filter items
            cleaned_items = [item.strip() for item in items if item.strip()]
            all_items.extend(cleaned_items)

        return list(set(all_items))  # Remove duplicates

    def _map_extracted_value(
        self, value: str, mapping: dict[str, list[str]]
    ) -> str | None:
        """Map extracted value using provided mapping."""
        value_lower = value.lower()

        for mapped_value, keywords in mapping.items():
            if any(keyword in value_lower for keyword in keywords):
                return mapped_value

        return None

    def _extract_readiness_level(
        self, value: str, mapping: dict[float, list[str]]
    ) -> float | None:
        """Extract readiness level from text."""
        # Try numeric extraction first
        numeric_match = re.search(r"(\d+)", value)
        if numeric_match:
            num = int(numeric_match.group(1))
            if num <= 10:
                return num / 10.0
            elif num <= 100:
                return num / 100.0

        # Try mapping
        value_lower = value.lower()
        for level, keywords in mapping.items():
            if any(keyword in value_lower for keyword in keywords):
                return level

        return None

    def _merge_extracted_data(
        self, collected_data: CollectedData, stage_data: dict[str, Any]
    ) -> None:
        """Merge extracted stage data into collected data."""
        for field, value in stage_data.items():
            if hasattr(collected_data, field):
                current_value = getattr(collected_data, field)

                if isinstance(current_value, list):
                    # Merge lists
                    if isinstance(value, list):
                        current_value.extend(value)
                    else:
                        current_value.append(value)
                    # Remove duplicates
                    setattr(collected_data, field, list(set(current_value)))
                elif current_value is None or current_value == "":
                    # Set value if not already set
                    setattr(collected_data, field, value)

    def _post_process_data(self, collected_data: CollectedData) -> None:
        """Post-process and clean extracted data."""
        # Clean name
        if collected_data.name:
            collected_data.name = re.sub(r"\s+", " ", collected_data.name).strip()

        # Validate and clean lists
        for field_name in [
            "personality_traits",
            "core_values",
            "strengths_and_skills",
            "primary_concerns",
            "life_goals",
            "therapeutic_goals",
            "comfort_zones",
            "challenge_areas",
        ]:
            field_value = getattr(collected_data, field_name, [])
            if field_value:
                # Remove empty strings and duplicates
                cleaned = list(
                    set([item.strip() for item in field_value if item.strip()])
                )
                setattr(collected_data, field_name, cleaned)

    def validate_extracted_data(
        self, collected_data: CollectedData
    ) -> tuple[bool, list[str]]:
        """
        Validate extracted data against validation rules.

        Args:
            collected_data: Data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for field_name, rules in self.validation_rules.items():
            value = getattr(collected_data, field_name, None)

            # Check required fields
            if rules.get("required", False) and not value:
                errors.append(f"{field_name} is required")
                continue

            if value is None:
                continue

            # Check string length
            if isinstance(value, str):
                min_length = rules.get("min_length")
                max_length = rules.get("max_length")

                if min_length and len(value) < min_length:
                    errors.append(
                        f"{field_name} must be at least {min_length} characters"
                    )

                if max_length and len(value) > max_length:
                    errors.append(
                        f"{field_name} must be no more than {max_length} characters"
                    )

                # Check pattern
                pattern = rules.get("pattern")
                if pattern and not re.match(pattern, value):
                    errors.append(f"{field_name} contains invalid characters")

            # Check valid values
            valid_values = rules.get("valid_values")
            if valid_values and value not in valid_values:
                errors.append(f"{field_name} must be one of: {', '.join(valid_values)}")

            # Check numeric ranges
            if isinstance(value, (int, float)):
                min_value = rules.get("min_value")
                max_value = rules.get("max_value")

                if min_value is not None and value < min_value:
                    errors.append(f"{field_name} must be at least {min_value}")

                if max_value is not None and value > max_value:
                    errors.append(f"{field_name} must be no more than {max_value}")

        return len(errors) == 0, errors
