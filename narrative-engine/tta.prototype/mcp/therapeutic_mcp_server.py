"""
Therapeutic MCP Server

This module provides an MCP server specifically designed for therapeutic text adventure tools.
It exposes therapeutic tools as MCP tools and resources for external integration.

Classes:
    TherapeuticMCPServer: MCP server for therapeutic tools
"""

import json
import logging
from datetime import datetime
from typing import Any

from fastmcp import FastMCP

from .therapeutic_tools import (
    TherapeuticContext,
    get_therapeutic_tools_manager,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TherapeuticMCPServer:
    """
    MCP server for therapeutic text adventure tools.

    This server exposes therapeutic tools as MCP tools and provides
    resources for therapeutic content and user progress tracking.
    """

    def __init__(self,
                 server_name: str = "Therapeutic Text Adventure MCP Server",
                 server_description: str = "MCP server providing therapeutic tools for text adventures"):
        """
        Initialize the therapeutic MCP server.

        Args:
            server_name: Name of the MCP server
            server_description: Description of the MCP server
        """
        self.server_name = server_name
        self.server_description = server_description

        # Initialize the MCP server
        self.mcp = FastMCP(
            self.server_name,
            description=self.server_description,
            dependencies=["fastmcp"]
        )

        # Get therapeutic tools manager
        self.tools_manager = get_therapeutic_tools_manager()

        # Register MCP tools and resources
        self._register_therapeutic_tools()
        self._register_therapeutic_resources()
        self._register_therapeutic_prompts()

        logger.info(f"TherapeuticMCPServer initialized: {self.server_name}")

    def _register_therapeutic_tools(self):
        """Register therapeutic tools as MCP tools."""

        @self.mcp.tool(name="analyze_emotional_state")
        async def analyze_emotional_state(
            user_id: str,
            session_id: str,
            current_emotional_state: str,
            narrative_context: str = "",
            user_history: str = "{}"
        ) -> str:
            """
            Analyze the emotional state of a user based on their input and context.

            Args:
                user_id: Unique identifier for the user
                session_id: Unique identifier for the current session
                current_emotional_state: Description of the user's current emotional state
                narrative_context: Current narrative context or recent story events
                user_history: JSON string containing user's therapeutic history

            Returns:
                JSON string containing emotional analysis results
            """
            try:
                # Parse user history
                history_dict = json.loads(user_history) if user_history else {}

                # Create therapeutic context
                context = TherapeuticContext(
                    user_id=user_id,
                    session_id=session_id,
                    current_emotional_state=current_emotional_state,
                    narrative_context=narrative_context,
                    user_history=history_dict,
                    therapeutic_goals=history_dict.get("therapeutic_goals", [])
                )

                # Process the request
                response = self.tools_manager.process_therapeutic_request(
                    "emotional_state_analyzer",
                    context
                )

                # Return formatted response
                return json.dumps({
                    "tool_name": response.tool_name,
                    "response_type": response.response_type,
                    "analysis": json.loads(response.content) if response.response_type != "error" else response.content,
                    "confidence": response.confidence,
                    "therapeutic_value": response.therapeutic_value,
                    "metadata": response.metadata,
                    "timestamp": response.timestamp.isoformat()
                }, indent=2)

            except Exception as e:
                logger.error(f"Error in analyze_emotional_state: {e}")
                return json.dumps({
                    "error": str(e),
                    "tool_name": "emotional_state_analyzer",
                    "response_type": "error"
                })

        @self.mcp.tool(name="generate_coping_strategies")
        async def generate_coping_strategies(
            user_id: str,
            session_id: str,
            current_emotional_state: str,
            narrative_context: str = "",
            user_history: str = "{}"
        ) -> str:
            """
            Generate personalized coping strategies based on emotional state and context.

            Args:
                user_id: Unique identifier for the user
                session_id: Unique identifier for the current session
                current_emotional_state: Description of the user's current emotional state
                narrative_context: Current narrative context or recent story events
                user_history: JSON string containing user's therapeutic history

            Returns:
                JSON string containing coping strategy recommendations
            """
            try:
                # Parse user history
                history_dict = json.loads(user_history) if user_history else {}

                # Create therapeutic context
                context = TherapeuticContext(
                    user_id=user_id,
                    session_id=session_id,
                    current_emotional_state=current_emotional_state,
                    narrative_context=narrative_context,
                    user_history=history_dict,
                    therapeutic_goals=history_dict.get("therapeutic_goals", [])
                )

                # Process the request
                response = self.tools_manager.process_therapeutic_request(
                    "coping_strategy_generator",
                    context
                )

                # Return formatted response
                return json.dumps({
                    "tool_name": response.tool_name,
                    "response_type": response.response_type,
                    "strategies": json.loads(response.content) if response.response_type != "error" else response.content,
                    "confidence": response.confidence,
                    "therapeutic_value": response.therapeutic_value,
                    "metadata": response.metadata,
                    "timestamp": response.timestamp.isoformat()
                }, indent=2)

            except Exception as e:
                logger.error(f"Error in generate_coping_strategies: {e}")
                return json.dumps({
                    "error": str(e),
                    "tool_name": "coping_strategy_generator",
                    "response_type": "error"
                })

        @self.mcp.tool(name="get_tool_recommendations")
        async def get_tool_recommendations(
            user_id: str,
            session_id: str,
            current_emotional_state: str,
            narrative_context: str = "",
            therapeutic_goals: str = "[]"
        ) -> str:
            """
            Get recommendations for which therapeutic tools to use based on context.

            Args:
                user_id: Unique identifier for the user
                session_id: Unique identifier for the current session
                current_emotional_state: Description of the user's current emotional state
                narrative_context: Current narrative context or recent story events
                therapeutic_goals: JSON array of therapeutic goals

            Returns:
                JSON string containing tool recommendations
            """
            try:
                # Parse therapeutic goals
                goals_list = json.loads(therapeutic_goals) if therapeutic_goals else []

                # Create therapeutic context
                context = TherapeuticContext(
                    user_id=user_id,
                    session_id=session_id,
                    current_emotional_state=current_emotional_state,
                    narrative_context=narrative_context,
                    user_history={},
                    therapeutic_goals=goals_list
                )

                # Get recommendations
                recommendations = self.tools_manager.get_tool_recommendations(context)

                # Get tool information
                tool_info = {tool["name"]: tool for tool in self.tools_manager.list_tools()}

                # Format response
                recommended_tools = []
                for tool_name in recommendations:
                    if tool_name in tool_info:
                        recommended_tools.append({
                            "name": tool_name,
                            "description": tool_info[tool_name]["description"],
                            "usage_count": tool_info[tool_name]["usage_count"],
                            "success_rate": tool_info[tool_name]["success_rate"]
                        })

                return json.dumps({
                    "recommended_tools": recommended_tools,
                    "context_analysis": {
                        "primary_emotional_indicators": self._extract_emotional_indicators(current_emotional_state),
                        "narrative_themes": self._extract_narrative_themes(narrative_context),
                        "therapeutic_focus": goals_list
                    },
                    "timestamp": datetime.now().isoformat()
                }, indent=2)

            except Exception as e:
                logger.error(f"Error in get_tool_recommendations: {e}")
                return json.dumps({
                    "error": str(e),
                    "recommended_tools": []
                })

        @self.mcp.tool(name="validate_therapeutic_content")
        async def validate_therapeutic_content(
            content: str,
            content_type: str = "narrative",
            target_audience: str = "general",
            therapeutic_goals: str = "[]"
        ) -> str:
            """
            Validate therapeutic content for appropriateness and effectiveness.

            Args:
                content: Content to validate
                content_type: Type of content (narrative, dialogue, intervention)
                target_audience: Target audience (general, anxiety, depression, etc.)
                therapeutic_goals: JSON array of therapeutic goals

            Returns:
                JSON string containing validation results
            """
            try:
                # Parse therapeutic goals
                goals_list = json.loads(therapeutic_goals) if therapeutic_goals else []

                # Perform content validation
                validation_results = self._validate_content(content, content_type, target_audience, goals_list)

                return json.dumps(validation_results, indent=2)

            except Exception as e:
                logger.error(f"Error in validate_therapeutic_content: {e}")
                return json.dumps({
                    "error": str(e),
                    "is_valid": False,
                    "validation_score": 0.0
                })

    def _register_therapeutic_resources(self):
        """Register therapeutic resources."""

        @self.mcp.resource("therapeutic://tools")
        def get_therapeutic_tools() -> str:
            """Get information about all available therapeutic tools."""
            tools_info = self.tools_manager.list_tools()
            usage_stats = self.tools_manager.get_usage_statistics()

            # Combine tool info with usage stats
            for tool in tools_info:
                tool_name = tool["name"]
                if tool_name in usage_stats:
                    tool.update(usage_stats[tool_name])

            return json.dumps({
                "tools": tools_info,
                "total_tools": len(tools_info),
                "server_info": {
                    "name": self.server_name,
                    "description": self.server_description
                }
            }, indent=2)

        @self.mcp.resource("therapeutic://guidelines")
        def get_therapeutic_guidelines() -> str:
            """Get therapeutic guidelines and best practices."""
            guidelines = {
                "emotional_safety": [
                    "Always prioritize user emotional safety",
                    "Avoid triggering or harmful content",
                    "Provide crisis resources when needed",
                    "Respect user boundaries and consent"
                ],
                "therapeutic_principles": [
                    "Use evidence-based interventions",
                    "Maintain therapeutic boundaries",
                    "Focus on user empowerment",
                    "Encourage professional help when appropriate"
                ],
                "narrative_integration": [
                    "Embed therapeutic content naturally in story",
                    "Maintain narrative immersion",
                    "Use characters to model healthy behaviors",
                    "Provide choice and agency to users"
                ],
                "crisis_indicators": [
                    "Expressions of self-harm or suicide",
                    "Severe emotional distress",
                    "Substance abuse mentions",
                    "Trauma-related triggers"
                ],
                "referral_guidelines": [
                    "Encourage professional help for severe symptoms",
                    "Provide crisis hotline information",
                    "Suggest therapy or counseling resources",
                    "Maintain clear boundaries about AI limitations"
                ]
            }

            return json.dumps(guidelines, indent=2)

        @self.mcp.resource("therapeutic://usage-stats")
        def get_usage_statistics() -> str:
            """Get usage statistics for therapeutic tools."""
            stats = self.tools_manager.get_usage_statistics()

            # Calculate overall statistics
            total_uses = sum(tool_stats["total_uses"] for tool_stats in stats.values())
            total_successes = sum(tool_stats["success_count"] for tool_stats in stats.values())
            overall_success_rate = total_successes / total_uses if total_uses > 0 else 0.0

            return json.dumps({
                "overall_statistics": {
                    "total_tool_uses": total_uses,
                    "total_successes": total_successes,
                    "overall_success_rate": overall_success_rate,
                    "active_tools": len([name for name, stats in stats.items() if stats["total_uses"] > 0])
                },
                "tool_statistics": stats,
                "last_updated": datetime.now().isoformat()
            }, indent=2)

    def _register_therapeutic_prompts(self):
        """Register therapeutic prompts."""

        @self.mcp.prompt()
        def therapeutic_session_prompt() -> str:
            """Create a prompt for starting a therapeutic text adventure session."""
            return """
            I'd like to start a therapeutic text adventure session. Please help me create an engaging narrative experience that incorporates evidence-based therapeutic interventions.

            The session should:
            1. Begin with an emotional check-in to understand the user's current state
            2. Create an immersive story world that feels safe and supportive
            3. Introduce characters who can model healthy coping strategies
            4. Provide meaningful choices that promote therapeutic growth
            5. Integrate therapeutic techniques naturally into the narrative

            Please use the therapeutic tools available through this MCP server to:
            - Analyze the user's emotional state
            - Generate appropriate coping strategies
            - Validate therapeutic content for safety and effectiveness
            - Recommend the most suitable therapeutic approaches

            Remember to prioritize user safety, maintain therapeutic boundaries, and encourage professional help when appropriate.
            """

        @self.mcp.prompt()
        def crisis_support_prompt() -> str:
            """Create a prompt for crisis support situations."""
            return """
            A user appears to be in emotional distress or crisis. Please help me provide appropriate support while maintaining safety and therapeutic boundaries.

            Priority actions:
            1. Assess the severity of the situation
            2. Provide immediate emotional support and validation
            3. Offer grounding techniques and coping strategies
            4. Provide crisis resources and professional referrals
            5. Ensure user safety is the top priority

            Use the therapeutic tools to:
            - Analyze emotional indicators for crisis markers
            - Generate immediate coping strategies
            - Validate any interventions for appropriateness

            Remember: AI cannot replace professional crisis intervention. Always encourage users to seek immediate professional help for serious mental health crises.
            """

        @self.mcp.prompt()
        def narrative_therapy_integration_prompt() -> str:
            """Create a prompt for integrating therapy into narrative content."""
            return """
            I need to integrate therapeutic interventions into a text adventure narrative in a way that feels natural and engaging.

            The integration should:
            1. Maintain story immersion and flow
            2. Use characters and situations to demonstrate therapeutic concepts
            3. Provide opportunities for users to practice coping skills
            4. Reinforce positive behavioral changes through story outcomes
            5. Allow users to explore different approaches safely

            Please use the therapeutic tools to:
            - Identify appropriate therapeutic techniques for the current context
            - Generate narrative scenarios that support therapeutic goals
            - Validate content for therapeutic effectiveness and safety

            The goal is to create a seamless blend of engaging storytelling and meaningful therapeutic support.
            """

    def _extract_emotional_indicators(self, emotional_state: str) -> list[str]:
        """Extract emotional indicators from text."""
        indicators = []
        emotional_state_lower = emotional_state.lower()

        # Define emotional keywords
        emotion_keywords = {
            "anxiety": ["anxious", "worried", "nervous", "panic", "stress", "overwhelmed"],
            "depression": ["sad", "hopeless", "empty", "worthless", "tired", "alone"],
            "anger": ["angry", "frustrated", "mad", "furious", "irritated"],
            "fear": ["afraid", "scared", "terrified", "frightened"],
            "joy": ["happy", "excited", "joyful", "pleased", "content"],
            "calm": ["peaceful", "relaxed", "serene", "tranquil", "composed"]
        }

        for emotion, keywords in emotion_keywords.items():
            if any(keyword in emotional_state_lower for keyword in keywords):
                indicators.append(emotion)

        return indicators

    def _extract_narrative_themes(self, narrative_context: str) -> list[str]:
        """Extract narrative themes from context."""
        themes = []
        context_lower = narrative_context.lower()

        # Define theme keywords
        theme_keywords = {
            "conflict": ["fight", "argument", "conflict", "disagreement", "tension"],
            "loss": ["death", "loss", "goodbye", "ending", "separation"],
            "growth": ["learning", "growing", "developing", "improving", "progress"],
            "relationship": ["friend", "family", "love", "connection", "bond"],
            "challenge": ["difficult", "hard", "struggle", "obstacle", "problem"],
            "hope": ["hope", "future", "possibility", "dream", "aspiration"]
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in context_lower for keyword in keywords):
                themes.append(theme)

        return themes

    def _validate_content(self, content: str, content_type: str, target_audience: str, therapeutic_goals: list[str]) -> dict[str, Any]:
        """Validate therapeutic content."""
        validation_results = {
            "is_valid": True,
            "validation_score": 0.8,  # Default score
            "warnings": [],
            "recommendations": [],
            "therapeutic_alignment": 0.7
        }

        content_lower = content.lower()

        # Check for potentially harmful content
        harmful_indicators = ["suicide", "self-harm", "violence", "abuse", "trauma"]
        for indicator in harmful_indicators:
            if indicator in content_lower:
                validation_results["warnings"].append(f"Contains potentially sensitive content: {indicator}")
                validation_results["validation_score"] -= 0.2

        # Check for therapeutic value
        therapeutic_indicators = ["coping", "support", "growth", "healing", "understanding"]
        therapeutic_count = sum(1 for indicator in therapeutic_indicators if indicator in content_lower)

        if therapeutic_count > 0:
            validation_results["therapeutic_alignment"] = min(0.5 + (therapeutic_count * 0.1), 1.0)

        # Generate recommendations
        if validation_results["validation_score"] < 0.6:
            validation_results["recommendations"].append("Consider revising content to reduce potentially harmful elements")

        if validation_results["therapeutic_alignment"] < 0.5:
            validation_results["recommendations"].append("Consider adding more therapeutic elements to support user growth")

        # Final validation
        validation_results["is_valid"] = (
            validation_results["validation_score"] >= 0.5 and
            len(validation_results["warnings"]) == 0
        )

        return validation_results

    def run(self, host: str = "localhost", port: int = 8000, **kwargs):
        """
        Run the therapeutic MCP server.

        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional arguments for the MCP server
        """
        logger.info(f"Starting Therapeutic MCP Server on {host}:{port}")
        self.mcp.run(host=host, port=port, **kwargs)


def create_therapeutic_mcp_server(
    server_name: str = "Therapeutic Text Adventure MCP Server",
    server_description: str = "MCP server providing therapeutic tools for text adventures"
) -> TherapeuticMCPServer:
    """
    Create a therapeutic MCP server.

    Args:
        server_name: Name of the MCP server
        server_description: Description of the MCP server

    Returns:
        TherapeuticMCPServer: Configured MCP server instance
    """
    return TherapeuticMCPServer(server_name, server_description)


# Example usage
if __name__ == "__main__":
    # Create and run the therapeutic MCP server
    server = create_therapeutic_mcp_server()
    server.run(host="localhost", port=8001)
