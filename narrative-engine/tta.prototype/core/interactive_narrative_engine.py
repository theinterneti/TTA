"""
Interactive Narrative Engine for TTA Prototype

This module implements the core interactive narrative engine that manages session lifecycle,
narrative progression tracking, and integration with the existing LangGraph engine for
agent orchestration.

Classes:
    InteractiveNarrativeEngine: Core storytelling system that manages narrative flow and user interactions
    NarrativeResponse: Response object containing narrative content and metadata
    UserChoice: Represents a user's choice in the narrative
    NarrativeEvent: Represents an event in the narrative progression
"""

import logging

# Import existing TTA components
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add tta.dev to path for LangGraph engine access
tta_dev_path = Path(__file__).parent.parent.parent / "tta.dev"
if str(tta_dev_path) not in sys.path:
    sys.path.append(str(tta_dev_path))

try:
    from core.langgraph_engine import (
        AgentState,
        CharacterState,
        GameState,
        create_workflow,
    )
except ImportError:
    logging.warning("Could not import LangGraph engine - using fallback implementations")
    # Fallback implementations will be defined below

# Import data models
try:
    from tta.prototype.database.neo4j_schema import Neo4jManager

    # Import database components
    from tta.prototype.database.redis_cache_enhanced import RedisCache
    from tta.prototype.models.data_models import (
        CharacterState as PrototypeCharacterState,
    )
    from tta.prototype.models.data_models import (
        EmotionalState,
        NarrativeContext,
        SessionState,
        TherapeuticProgress,
    )
except ImportError:
    # Fallback for when running from within the tta.prototype directory
    try:
        from models.data_models import CharacterState as PrototypeCharacterState
        from models.data_models import (
            EmotionalState,
            NarrativeContext,
            SessionState,
            TherapeuticProgress,
        )

        from database.neo4j_schema import Neo4jManager

        # Import database components
        from database.redis_cache_enhanced import RedisCache
    except ImportError as e:
        logging.warning(f"Could not import data models or database components: {e}")
        # Define minimal fallback classes
        from dataclasses import dataclass, field
        from datetime import datetime
        from enum import Enum
        from typing import Any

        class EmotionalStateType(Enum):
            CALM = "calm"
            ANXIOUS = "anxious"
            DEPRESSED = "depressed"
            EXCITED = "excited"
            ANGRY = "angry"
            CONFUSED = "confused"
            HOPEFUL = "hopeful"
            OVERWHELMED = "overwhelmed"

        @dataclass
        class EmotionalState:
            primary_emotion: EmotionalStateType = EmotionalStateType.CALM
            intensity: float = 0.5
            timestamp: datetime = field(default_factory=datetime.now)

            def validate(self):
                return True

        @dataclass
        class TherapeuticProgress:
            user_id: str = ""
            overall_progress_score: float = 0.0
            therapeutic_goals: list = field(default_factory=list)

            def validate(self):
                return True

        @dataclass
        class NarrativeContext:
            session_id: str = ""
            current_location_id: str = ""
            recent_events: list[str] = field(default_factory=list)
            user_choice_history: list[dict[str, Any]] = field(default_factory=list)

            def validate(self):
                return True

            def add_choice(self, choice_text: str, choice_id: str, consequences: list[str]):
                choice = {
                    "choice_id": choice_id,
                    "choice_text": choice_text,
                    "consequences": consequences,
                    "timestamp": datetime.now().isoformat()
                }
                self.user_choice_history.append(choice)

        @dataclass
        class SessionState:
            session_id: str = ""
            user_id: str = ""
            current_scenario_id: str = ""
            current_location_id: str = ""
            narrative_position: int = 0
            character_states: dict = field(default_factory=dict)
            user_inventory: list[str] = field(default_factory=list)
            therapeutic_progress: TherapeuticProgress | None = None
            emotional_state: EmotionalState | None = None
            narrative_context: NarrativeContext | None = None
            created_at: datetime = field(default_factory=datetime.now)
            last_updated: datetime = field(default_factory=datetime.now)

            def validate(self):
                return True

        class RedisCache:
            def __init__(self):
                pass

            def set_session_state(self, session_id: str, session_state: SessionState):
                pass

            def get_session_state(self, session_id: str):
                return None

        class Neo4jManager:
            def __init__(self):
                pass

# Import narrative branching system
try:
    from tta.prototype.core.narrative_branching import (
        ChoiceOption as BranchingChoiceOption,
    )
    from tta.prototype.core.narrative_branching import NarrativeBranchingChoice
except ImportError:
    try:
        from core.narrative_branching import ChoiceOption as BranchingChoiceOption
        from core.narrative_branching import NarrativeBranchingChoice
    except ImportError:
        logging.warning("Could not import narrative branching system")
        NarrativeBranchingChoice = None
        BranchingChoiceOption = None

# Import LangGraph integration
try:
    from tta.prototype.core.langgraph_integration import (
        TherapeuticAgentOrchestrator,
        TherapeuticContext,
    )
except ImportError:
    try:
        from core.langgraph_integration import (
            TherapeuticAgentOrchestrator,
            TherapeuticContext,
        )
    except ImportError:
        logging.warning("Could not import LangGraph integration")
        TherapeuticAgentOrchestrator = None
        TherapeuticContext = None

logger = logging.getLogger(__name__)


@dataclass
class UserChoice:
    """Represents a user's choice in the narrative."""
    choice_id: str
    choice_text: str
    choice_type: str = "dialogue"  # dialogue, action, movement, etc.
    metadata: dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class NarrativeEvent:
    """Represents an event in the narrative progression."""
    event_id: str
    event_type: str
    description: str
    participants: list[str] = None
    location_id: str = ""
    metadata: dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class NarrativeResponse:
    """Response object containing narrative content and metadata."""
    content: str
    response_type: str = "narrative"  # narrative, choice_prompt, error, etc.
    choices: list[dict[str, Any]] = None
    metadata: dict[str, Any] = None
    session_id: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if self.choices is None:
            self.choices = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class InteractiveNarrativeEngine:
    """
    Core storytelling system that manages narrative flow and user interactions.

    This class provides session lifecycle management, narrative progression tracking,
    and integration with the existing LangGraph engine for agent orchestration.
    """

    def __init__(self, redis_cache: RedisCache | None = None,
                 neo4j_manager: Neo4jManager | None = None):
        """
        Initialize the Interactive Narrative Engine.

        Args:
            redis_cache: Redis cache instance for session management
            neo4j_manager: Neo4j manager for knowledge graph operations
        """
        self.redis_cache = redis_cache
        self.neo4j_manager = neo4j_manager
        self.active_sessions: dict[str, SessionState] = {}

        # Initialize narrative branching system
        self.branching_system = None
        if NarrativeBranchingChoice:
            try:
                self.branching_system = NarrativeBranchingChoice()
                logger.info("Narrative branching system initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize narrative branching system: {e}")

        # Initialize therapeutic agent orchestrator
        self.therapeutic_orchestrator = None
        if TherapeuticAgentOrchestrator:
            try:
                self.therapeutic_orchestrator = TherapeuticAgentOrchestrator()
                logger.info("Therapeutic agent orchestrator initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize therapeutic agent orchestrator: {e}")

        # Initialize LangGraph workflow if available
        self.langgraph_workflow = None
        self.langgraph_tools = None

        if neo4j_manager:
            try:
                self.langgraph_workflow, self.langgraph_tools = create_workflow(neo4j_manager)
                logger.info("LangGraph workflow initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize LangGraph workflow: {e}")

        logger.info("InteractiveNarrativeEngine initialized")

    def start_session(self, user_id: str, scenario_id: str = "default") -> SessionState:
        """
        Start a new therapeutic narrative session.

        Args:
            user_id: Unique identifier for the user
            scenario_id: Identifier for the initial scenario

        Returns:
            SessionState: New session state object

        Raises:
            ValueError: If user_id is empty or invalid
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create initial session state
        session_state = SessionState(
            session_id=session_id,
            user_id=user_id,
            current_scenario_id=scenario_id,
            current_location_id="starting_location",
            narrative_position=0
        )

        # Initialize narrative context
        narrative_context = NarrativeContext(
            session_id=session_id,
            current_location_id="starting_location"
        )
        session_state.narrative_context = narrative_context

        # Initialize therapeutic progress if not exists
        if not session_state.therapeutic_progress:
            session_state.therapeutic_progress = TherapeuticProgress(user_id=user_id)

        # Initialize emotional state
        session_state.emotional_state = EmotionalState()

        # Validate session state
        session_state.validate()

        # Store in active sessions
        self.active_sessions[session_id] = session_state

        # Cache in Redis if available
        if self.redis_cache:
            try:
                self.redis_cache.set_session_state(session_id, session_state)
                logger.info(f"Session {session_id} cached in Redis")
            except Exception as e:
                logger.warning(f"Could not cache session in Redis: {e}")

        logger.info(f"Started new session {session_id} for user {user_id}")
        return session_state

    def get_session(self, session_id: str) -> SessionState | None:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Optional[SessionState]: Session state if found, None otherwise
        """
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Try to load from Redis cache
        if self.redis_cache:
            try:
                session_state = self.redis_cache.get_session_state(session_id)
                if session_state:
                    self.active_sessions[session_id] = session_state
                    logger.info(f"Loaded session {session_id} from Redis cache")
                    return session_state
            except Exception as e:
                logger.warning(f"Could not load session from Redis: {e}")

        logger.warning(f"Session {session_id} not found")
        return None

    def process_user_choice(self, session_id: str, choice: UserChoice) -> NarrativeResponse:
        """
        Process a user's choice and generate the next narrative response.

        Args:
            session_id: Session identifier
            choice: User's choice object

        Returns:
            NarrativeResponse: Generated narrative response

        Raises:
            ValueError: If session not found or choice is invalid
        """
        # Get session state
        session_state = self.get_session(session_id)
        if not session_state:
            raise ValueError(f"Session {session_id} not found")

        # Validate choice
        if not choice.choice_text or not choice.choice_text.strip():
            return NarrativeResponse(
                content="I didn't understand that. Could you please try again?",
                response_type="error",
                session_id=session_id
            )

        try:
            # Process choice through therapeutic orchestrator if available
            if self.therapeutic_orchestrator and TherapeuticContext:
                try:
                    # Create therapeutic context
                    therapeutic_context = TherapeuticContext(
                        session_id=session_id,
                        user_emotional_state={
                            session_state.emotional_state.primary_emotion.value: session_state.emotional_state.intensity
                        } if session_state.emotional_state else {},
                        therapeutic_goals=["general_wellbeing"],  # Could be extracted from therapeutic progress
                        current_location=session_state.current_location_id,
                        available_characters=list(session_state.character_states.keys()),
                        character_relationships=dict.fromkeys(session_state.character_states.keys(), 0.5)
                    )

                    # Process through therapeutic orchestrator
                    agent_response, updated_context = self.therapeutic_orchestrator.process_user_interaction(
                        choice.choice_text, therapeutic_context
                    )

                    # Add choice to narrative context
                    if session_state.narrative_context:
                        session_state.narrative_context.add_choice(
                            choice.choice_text,
                            choice.choice_id,
                            [f"therapeutic_value_{agent_response.therapeutic_value:.2f}"]
                        )

                    # Create narrative response from agent response
                    narrative_response = NarrativeResponse(
                        content=agent_response.content,
                        response_type="narrative",
                        choices=self._generate_choice_options(session_state, None),
                        session_id=session_id,
                        metadata={
                            "agent_type": agent_response.agent_type,
                            "therapeutic_value": agent_response.therapeutic_value,
                            "agent_metadata": agent_response.metadata
                        }
                    )

                except Exception as e:
                    logger.warning(f"Error processing choice with therapeutic orchestrator: {e}")
                    # Fall back to branching system
                    narrative_response = self._process_with_branching_system(session_state, choice, session_id)

            # Process choice through narrative branching system if available
            elif self.branching_system and BranchingChoiceOption:
                narrative_response = self._process_with_branching_system(session_state, choice, session_id)
            else:
                # Add choice to narrative context
                if session_state.narrative_context:
                    session_state.narrative_context.add_choice(
                        choice.choice_text,
                        choice.choice_id,
                        []  # consequences will be determined by processing
                    )

                # Process choice through LangGraph if available
                narrative_response = self._process_choice_with_langgraph(session_state, choice)

            # Update session state
            session_state.narrative_position += 1
            session_state.last_updated = datetime.now()

            # Update cache
            if self.redis_cache:
                try:
                    self.redis_cache.set_session_state(session_id, session_state)
                except Exception as e:
                    logger.warning(f"Could not update session cache: {e}")

            logger.info(f"Processed choice for session {session_id}: {choice.choice_text[:50]}...")
            return narrative_response

        except Exception as e:
            logger.error(f"Error processing user choice: {e}")
            return NarrativeResponse(
                content="Something went wrong while processing your choice. Please try again.",
                response_type="error",
                session_id=session_id
            )

    def _process_choice_with_langgraph(self, session_state: SessionState, choice: UserChoice) -> NarrativeResponse:
        """
        Process user choice using the LangGraph engine.

        Args:
            session_state: Current session state
            choice: User's choice

        Returns:
            NarrativeResponse: Generated response
        """
        if not self.langgraph_workflow:
            # Fallback to simple processing
            return self._process_choice_fallback(session_state, choice)

        try:
            # Convert session state to LangGraph format
            current_location = session_state.current_location_id or "starting_location"

            # Execute LangGraph workflow
            agent_state = self.langgraph_workflow(choice.choice_text, current_location)

            # Extract response from agent state
            response_content = agent_state.response if hasattr(agent_state, 'response') else "You continue your adventure."

            # Generate choices based on parsed input
            choices = self._generate_choice_options(session_state, agent_state)

            return NarrativeResponse(
                content=response_content,
                response_type="narrative",
                choices=choices,
                session_id=session_state.session_id,
                metadata={
                    "agent_state": {
                        "current_agent": getattr(agent_state, 'current_agent', 'unknown'),
                        "parsed_input": getattr(agent_state, 'parsed_input', {}),
                        "turn_count": getattr(agent_state, 'turn_count', session_state.narrative_position)
                    }
                }
            )

        except Exception as e:
            logger.error(f"Error in LangGraph processing: {e}")
            return self._process_choice_fallback(session_state, choice)

    def _process_choice_fallback(self, session_state: SessionState, choice: UserChoice) -> NarrativeResponse:
        """
        Fallback choice processing when LangGraph is not available.

        Args:
            session_state: Current session state
            choice: User's choice

        Returns:
            NarrativeResponse: Generated response
        """
        # Simple rule-based processing
        choice_lower = choice.choice_text.lower().strip()

        if choice_lower in ["look", "look around", "examine area"]:
            content = f"You look around the {session_state.current_location_id}. The area is peaceful and inviting."
            choices = [
                {"id": "explore", "text": "Explore the area further"},
                {"id": "rest", "text": "Take a moment to rest and reflect"},
                {"id": "continue", "text": "Continue on your journey"}
            ]
        elif choice_lower in ["help", "what can i do"]:
            content = "You can explore your surroundings, interact with characters, or reflect on your experiences. What would you like to do?"
            choices = [
                {"id": "look", "text": "Look around"},
                {"id": "think", "text": "Take time to think"},
                {"id": "move", "text": "Move to a new area"}
            ]
        else:
            # Generic response
            content = f"You {choice.choice_text}. The experience gives you a moment to reflect on your journey."
            choices = [
                {"id": "continue", "text": "Continue your story"},
                {"id": "reflect", "text": "Reflect on what just happened"},
                {"id": "look", "text": "Look around"}
            ]

        return NarrativeResponse(
            content=content,
            response_type="narrative",
            choices=choices,
            session_id=session_state.session_id
        )

    def _generate_choice_options(self, session_state: SessionState, agent_state: Any) -> list[dict[str, Any]]:
        """
        Generate choice options based on current state.

        Args:
            session_state: Current session state
            agent_state: LangGraph agent state

        Returns:
            List[Dict[str, Any]]: List of choice options
        """
        # Use narrative branching system if available
        if self.branching_system:
            try:
                # Prepare narrative context for branching system
                narrative_context = {
                    "session_id": session_state.session_id,
                    "location_id": session_state.current_location_id,
                    "characters": list(session_state.character_states.keys()),
                    "emotional_state": {
                        "primary_emotion": session_state.emotional_state.primary_emotion.value if session_state.emotional_state else "calm",
                        "intensity": session_state.emotional_state.intensity if session_state.emotional_state else 0.5
                    },
                    "therapeutic_opportunities": []
                }

                # Add therapeutic opportunities based on emotional state
                if session_state.emotional_state and session_state.emotional_state.intensity > 0.6:
                    if session_state.emotional_state.primary_emotion.value in ["anxious", "overwhelmed"]:
                        narrative_context["therapeutic_opportunities"].append("anxiety_management")
                    elif session_state.emotional_state.primary_emotion.value in ["depressed", "sad"]:
                        narrative_context["therapeutic_opportunities"].append("emotional_regulation")

                # Generate choices using branching system
                choice_options = self.branching_system.generate_choice_options(narrative_context)

                # Convert to simple dict format
                choices = []
                for choice_option in choice_options:
                    choices.append({
                        "id": choice_option.choice_id,
                        "text": choice_option.choice_text,
                        "type": choice_option.choice_type.value,
                        "therapeutic_weight": choice_option.therapeutic_weight,
                        "emotional_tone": choice_option.emotional_tone
                    })

                return choices

            except Exception as e:
                logger.warning(f"Error using narrative branching system: {e}")
                # Fall back to simple generation

        # Fallback choice generation
        # Extract intent from parsed input if available
        parsed_input = getattr(agent_state, 'parsed_input', {})
        intent = parsed_input.get('intent', 'unknown')

        # Generate contextual choices based on intent
        if intent == "look":
            return [
                {"id": "explore", "text": "Explore the area more thoroughly"},
                {"id": "interact", "text": "Look for someone to talk to"},
                {"id": "move", "text": "Move to a different area"}
            ]
        elif intent == "move":
            return [
                {"id": "look", "text": "Look around the new area"},
                {"id": "rest", "text": "Take a moment to rest"},
                {"id": "continue", "text": "Keep moving forward"}
            ]
        elif intent == "talk":
            return [
                {"id": "continue_conversation", "text": "Continue the conversation"},
                {"id": "ask_question", "text": "Ask a question"},
                {"id": "end_conversation", "text": "End the conversation politely"}
            ]
        else:
            # Default choices
            return [
                {"id": "continue", "text": "Continue your journey"},
                {"id": "reflect", "text": "Take time to reflect"},
                {"id": "look", "text": "Look around"}
            ]

    def get_current_scenario(self, session_id: str) -> dict[str, Any] | None:
        """
        Get the current scenario state for a session.

        Args:
            session_id: Session identifier

        Returns:
            Optional[Dict[str, Any]]: Current scenario data or None if session not found
        """
        session_state = self.get_session(session_id)
        if not session_state:
            return None

        return {
            "session_id": session_id,
            "scenario_id": session_state.current_scenario_id,
            "location_id": session_state.current_location_id,
            "narrative_position": session_state.narrative_position,
            "character_states": {
                char_id: {
                    "name": char_state.name,
                    "current_mood": char_state.current_mood,
                    "therapeutic_role": char_state.therapeutic_role
                }
                for char_id, char_state in session_state.character_states.items()
            },
            "therapeutic_progress": {
                "overall_progress_score": session_state.therapeutic_progress.overall_progress_score if session_state.therapeutic_progress else 0.0,
                "active_goals": len(session_state.therapeutic_progress.therapeutic_goals) if session_state.therapeutic_progress else 0
            } if session_state.therapeutic_progress else None,
            "emotional_state": {
                "primary_emotion": session_state.emotional_state.primary_emotion.value if session_state.emotional_state else "calm",
                "intensity": session_state.emotional_state.intensity if session_state.emotional_state else 0.5
            } if session_state.emotional_state else None
        }

    def advance_narrative(self, session_id: str, narrative_event: NarrativeEvent) -> bool:
        """
        Advance the narrative based on a specific event.

        Args:
            session_id: Session identifier
            narrative_event: Event to process

        Returns:
            bool: True if narrative was advanced successfully, False otherwise
        """
        session_state = self.get_session(session_id)
        if not session_state:
            logger.error(f"Session {session_id} not found for narrative advancement")
            return False

        try:
            # Add event to narrative context
            if session_state.narrative_context:
                session_state.narrative_context.recent_events.append(narrative_event.description)

                # Update location if event specifies one
                if narrative_event.location_id:
                    session_state.current_location_id = narrative_event.location_id
                    session_state.narrative_context.current_location_id = narrative_event.location_id

            # Update narrative position
            session_state.narrative_position += 1
            session_state.last_updated = datetime.now()

            # Update cache
            if self.redis_cache:
                try:
                    self.redis_cache.set_session_state(session_id, session_state)
                except Exception as e:
                    logger.warning(f"Could not update session cache: {e}")

            logger.info(f"Advanced narrative for session {session_id} with event: {narrative_event.event_type}")
            return True

        except Exception as e:
            logger.error(f"Error advancing narrative: {e}")
            return False

    def end_session(self, session_id: str) -> bool:
        """
        End a narrative session and clean up resources.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if session was ended successfully, False otherwise
        """
        try:
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            # Remove from Redis cache if configured to do so
            if self.redis_cache:
                try:
                    # Note: We might want to keep session data for historical purposes
                    # For now, we'll just mark it as ended rather than deleting
                    session_state = self.redis_cache.get_session_state(session_id)
                    if session_state:
                        session_state.last_updated = datetime.now()
                        # Add an "ended" flag to metadata if needed
                        self.redis_cache.set_session_state(session_id, session_state)
                except Exception as e:
                    logger.warning(f"Could not update session end status in cache: {e}")

            logger.info(f"Ended session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False

    def get_active_session_count(self) -> int:
        """
        Get the number of currently active sessions.

        Returns:
            int: Number of active sessions
        """
        return len(self.active_sessions)

    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up inactive sessions older than the specified age.

        Args:
            max_age_hours: Maximum age in hours for keeping sessions active

        Returns:
            int: Number of sessions cleaned up
        """
        current_time = datetime.now()
        sessions_to_remove = []

        for session_id, session_state in self.active_sessions.items():
            age_hours = (current_time - session_state.last_updated).total_seconds() / 3600
            if age_hours > max_age_hours:
                sessions_to_remove.append(session_id)

        # Remove inactive sessions
        for session_id in sessions_to_remove:
            self.end_session(session_id)

        logger.info(f"Cleaned up {len(sessions_to_remove)} inactive sessions")
        return len(sessions_to_remove)

    def _generate_response_from_consequence(self, session_state: SessionState, choice: UserChoice, consequence) -> NarrativeResponse:
        """
        Generate a narrative response based on choice consequences.

        Args:
            session_state: Current session state
            choice: User's choice
            consequence: Choice consequence from branching system

        Returns:
            NarrativeResponse: Generated narrative response
        """
        try:
            # Generate response content based on consequence
            if consequence.consequence_type.value == "therapeutic":
                if "reduced_anxiety" in consequence.narrative_flags:
                    content = f"You {choice.choice_text.lower()}. As you do this, you feel a sense of calm washing over you. Your breathing becomes more steady and your mind feels clearer."
                elif "increased_mindfulness" in consequence.narrative_flags:
                    content = f"You {choice.choice_text.lower()}. This moment of mindfulness helps you become more aware of your surroundings and your inner state."
                elif "emotional_awareness" in consequence.narrative_flags:
                    content = f"You {choice.choice_text.lower()}. Taking time to acknowledge your feelings helps you understand yourself better."
                else:
                    content = f"You {choice.choice_text.lower()}. This therapeutic action brings you a sense of progress and self-care."

            elif consequence.consequence_type.value == "relationship":
                if consequence.affected_entities:
                    character = consequence.affected_entities[0]
                    content = f"You {choice.choice_text.lower()}. {character.title()} responds warmly to your interaction, and you feel a stronger connection forming."
                else:
                    content = f"You {choice.choice_text.lower()}. This social interaction helps you feel more connected and understood."

            elif consequence.consequence_type.value == "world_state":
                if consequence.world_state_changes.get("player_moved"):
                    content = f"You {choice.choice_text.lower()}. The change of scenery gives you a fresh perspective and new opportunities to explore."
                else:
                    content = f"You {choice.choice_text.lower()}. Your action changes something about your environment in a meaningful way."

            else:
                # Default response
                content = f"You {choice.choice_text.lower()}. The experience gives you a moment to reflect on your journey and consider your next steps."

            # Generate new choice options based on updated state
            choices = self._generate_choice_options(session_state, None)

            return NarrativeResponse(
                content=content,
                response_type="narrative",
                choices=choices,
                session_id=session_state.session_id,
                metadata={
                    "consequence_type": consequence.consequence_type.value,
                    "therapeutic_impact": consequence.therapeutic_impact,
                    "emotional_impact": consequence.emotional_impact,
                    "narrative_flags": consequence.narrative_flags
                }
            )

        except Exception as e:
            logger.error(f"Error generating response from consequence: {e}")
            # Fall back to simple response
            return NarrativeResponse(
                content=f"You {choice.choice_text.lower()}. Your action has an impact on your journey.",
                response_type="narrative",
                choices=[
                    {"id": "continue", "text": "Continue your journey"},
                    {"id": "reflect", "text": "Take time to reflect"}
                ],
                session_id=session_state.session_id
            )

    def _process_with_branching_system(self, session_state: SessionState, choice: UserChoice, session_id: str) -> NarrativeResponse:
        """Process choice with narrative branching system."""
        try:
            # Convert UserChoice to BranchingChoiceOption
            # Try to determine therapeutic weight and choice type from choice text/type
            therapeutic_weight = 0.0
            choice_type_enum = None

            # Import choice type enum
            try:
                from core.narrative_branching import ChoiceType
                if choice.choice_type == "therapeutic":
                    choice_type_enum = ChoiceType.THERAPEUTIC
                    therapeutic_weight = 0.7  # Default therapeutic weight
                elif choice.choice_type == "dialogue":
                    choice_type_enum = ChoiceType.DIALOGUE
                    therapeutic_weight = 0.4
                elif choice.choice_type == "reflection":
                    choice_type_enum = ChoiceType.REFLECTION
                    therapeutic_weight = 0.5
                else:
                    choice_type_enum = ChoiceType.ACTION
                    therapeutic_weight = 0.2
            except ImportError:
                pass

            branching_choice = BranchingChoiceOption(
                choice_id=choice.choice_id,
                choice_text=choice.choice_text,
                choice_type=choice_type_enum or BranchingChoiceOption.__dataclass_fields__['choice_type'].default,
                therapeutic_weight=therapeutic_weight,
                metadata=choice.metadata
            )

            # Prepare context for branching system
            branching_context = {
                "session_id": session_id,
                "location_id": session_state.current_location_id,
                "characters": list(session_state.character_states.keys()),
                "emotional_state": {
                    "primary_emotion": session_state.emotional_state.primary_emotion.value if session_state.emotional_state else "calm",
                    "intensity": session_state.emotional_state.intensity if session_state.emotional_state else 0.5
                }
            }

            # Process choice and get consequences
            consequence = self.branching_system.process_user_choice(branching_choice, branching_context)

            # Add choice to narrative context with consequences
            if session_state.narrative_context:
                session_state.narrative_context.add_choice(
                    choice.choice_text,
                    choice.choice_id,
                    consequence.narrative_flags
                )

            # Generate narrative response based on consequences
            return self._generate_response_from_consequence(session_state, choice, consequence)

        except Exception as e:
            logger.error(f"Error in branching system processing: {e}")
            return self._process_choice_fallback(session_state, choice)
