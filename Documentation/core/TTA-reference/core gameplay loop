TTA - Core Gameplay Loop
1. Introduction
This document outlines the Therapeutic Text Adventure (TTA) core gameplay loop. It describes the ideal player experience, encompassing all aspects of interaction with the game world, AI agents, and narrative systems. This document is a guide for future development, providing a framework for designing and implementing game mechanics, AI agent behaviors, and content generation strategies.
2. Core Principles
The core gameplay loop is guided by the following principles:

Player Agency: The player's choices should have meaningful consequences, shaping the narrative, the game world, and character relationships.
AI-Driven Immersive and Dynamic Narrative: The game should leverage AI agents to generate dynamic and emergent narratives tailored to the player and their character, their individual journey.
Therapeutic Integration: The game should subtly integrate therapeutic concepts and techniques, encouraging self-reflection, emotional processing, and personal growth.
Ethical AI: The AI agents should be designed and trained to avoid harmful stereotypes, biases, and unethical behavior.
Emergent Gameplay: The game should encourage unexpected events and interactions that arise from the interplay of player choices, AI agent actions, and the dynamic game world.
3. Core Loop Components
The core gameplay loop consists of the following components:

Player Input: The player enters a text command describing their desired action.
Input Processing (IPA):
The Input Processor Agent (IPA), parses the player's input, identifies the intent, and extracts key entities.
IPA determines if player input is valid (is it interpretable? Can it be linked to the current context? etc.)
The IPA uses Natural Language Processing (NLP) techniques to understand the player's command.
IPA updates the game state to the editor.
AI Agent Orchestration:


LangGraph manages the workflow, activating the appropriate AI agents based on the IPA's output and the current game state.


AI Agent Processing (Qwen2.5):
The activated AI agent (e.g., NGA, WBA, CCA, LKA) processes the input and generates a response, adhering to metaconcepts.
The AI agent may use tools (defined via LangChain) to query the knowledge graph, update the game state, or access external resources (e.g., web APIs for "Our Universe" and "Alternate Earths" settings).
The AI agent utilizes Chain-of-Retrieval Augmented Generation (CoRAG) to iteratively refine its response, generating sub-queries and retrieving relevant information from the knowledge graph.
Qwen2.5 has capabilities for structured output.
Output Generation (NGA):
The Narrative Generator Agent (NGA) synthesizes information from other agents and generates the final text output presented to the player.
The NGA ensures that the output is consistent with established lore, character personalities, and metaconcepts.
The game presents the generated text to the player through the user interface.
Data Storage (Neo4j):
The Neo4j database stores and updates player profiles, world data, character data, and the ongoing narrative.
The knowledge graph is continuously expanded and refined based on player actions, AI agent interactions, and new content.
4. AI Agent Roles and Responsibilities
The following AI agents play key roles in the core gameplay loop:

Input Processor Agent (IPA): Parses player input, identifies intent, extracts key entities, and validates information.
Narrative Generator Agent (NGA): Generates descriptive text, character dialogue, and narrative events. Synthesizes information from other agents and ensures narrative consistency.
World Builder Agent (WBA): Generates descriptions of locations, environments, and objects. Manages the dynamic evolution of the game world.
Character Creator Agent (CCA): Generates character backstories, personalities, motivations, and relationships.
Lore Keeper Agent (LKA): Checks for consistency between generated content and existing lore. Expands the lore based on new information and player actions.
Nexus Manager Agent (NMA): Manages the connections between universes, allowing players to move between different game worlds. Facilitates cross-player interactions and the sharing of content.
5. Example Gameplay Scenarios
To illustrate the core gameplay loop, let's consider a few example scenarios:

Exploration:

Player Input: go north
IPA: Parses the input, identifies the intent ("move"), and extracts the direction ("north").
LangGraph: Activates the WBA.
WBA: Queries the knowledge graph to determine the location to the north. Generates a description of the new location, incorporating details about the environment, characters, and objects.
NGA: Presents the generated description to the player.

Interaction:

Player Input: talk to the guard
IPA: Parses the input, identifies the intent ("talk"), and extracts the target ("the guard").
LangGraph: Activates the NGA.
NGA: Queries the knowledge graph to retrieve information about the guard's personality, current mood, and relevant dialogue options. Generates a greeting from the guard, tailored to the player's past interactions and the current game state.
Player Input: (After the guard's greeting) ask him about the missing artifact
IPA: Parses the input, identifies the intent ("ask"), extracts the topic ("missing artifact"), and identifies the recipient ("the guard").
LangGraph: Activates the NGA.
NGA: Queries the knowledge graph to retrieve information about the missing artifact and the guard's potential knowledge of it. Generates the guard's response, incorporating relevant information, rumors, and potential clues.

Combat:

Player Input: attack the goblin with my sword
IPA: Parses the input, identifies the intent ("attack"), the target ("the goblin"), and the weapon ("my sword").
LangGraph: Activates a Combat Agent (a specialized agent for combat scenarios).
Combat Agent: Queries the knowledge graph to retrieve stats for the player character and the goblin. Simulates the attack, calculating hit chance, damage, and other relevant factors. Generates a description of the attack, incorporating details about the environment, the characters' actions, and the outcome of the attack.
NGA: Presents the generated description to the player.

Therapeutic Intervention:

Player Input: I feel lost and alone
IPA: Parses the input and identifies the player's emotional state ("lost and alone").
LangGraph: Activates a Therapeutic Agent (a specialized agent for therapeutic interactions).
Therapeutic Agent: Queries the knowledge graph to retrieve relevant therapeutic concepts and techniques. Generates a response designed to encourage self-reflection and provide support. The agent might offer a choice: "Would you like to explore those feelings more?" or "Would you like to focus on what gives you strength?". These choices will drive the narrative in different directions.
NGA: Presents the generated response to the player.
6. Metaconcepts and Ethical Considerations
All AI agent actions and content generation must adhere to a set of metaconcepts and ethical guidelines:

Do No Harm: The game should not generate content that is harmful, offensive, or triggers negative emotional responses in players.
Respect Player Agency: The game should respect the player's choices and avoid forcing them into situations that they are uncomfortable with.
Maintain Narrative Consistency: The game should maintain consistency with established lore, character personalities, and the overall narrative arc.
Promote Self-Reflection: The game should encourage players to reflect on their own thoughts, feelings, and experiences.
Provide Support and Encouragement: The game should provide players with support and encouragement, helping them to overcome challenges and achieve their goals.
Protect Player Privacy: The game should protect player privacy and avoid collecting or sharing personal information without their consent.
7. Dynamic Content Generation and the Knowledge Graph
The knowledge graph is the engine that drives dynamic content generation in TTA. By storing information about concepts, entities, relationships, and rules, the knowledge graph provides the context for AI agent actions and narrative generation.

Automated Expansion: The knowledge graph should be automatically expanded based on player actions, AI agent interactions, and new content.
Relationship Inference: The game should use relationship inference techniques to discover new relationships between concepts and entities.
Web Resource Integration: The game should integrate web resources (e.g., Wikipedia, Wikidata) to expand the knowledge graph and provide access to real-world information (particularly for "Our Universe" and "Alternate Earths" settings).
Player Contributions: Players should be able to contribute to the knowledge graph by creating new content, defining relationships, and providing feedback on existing content.
Hybrid Time System: The knowledge graph should incorporate a hybrid time system, allowing for both linear and non-linear narrative progression.
8. Long-Term Goals
The long-term goals for the core gameplay loop include:

Adaptive Difficulty: The game should dynamically adjust the difficulty based on the player's skill level and emotional state.
Personalized Narrative Arcs: The game should generate personalized narrative arcs tailored to the player's individual journey and therapeutic goals.
AI-Driven Therapeutic Support: The game should provide AI-driven therapeutic support, offering personalized guidance and interventions based on the player's needs and preferences. (Note: This will be approached with extreme caution, ethical rigor, and collaboration with mental health professionals.)
Community Features: The game should incorporate community features, allowing players to share their experiences, create content, and collaborate with others.
Cross-Platform Compatibility: The game should be compatible with a variety of platforms, including web browsers, mobile devices, and virtual reality headsets.
Dynamic Metaprompt Selection: Develop algorithms for dynamic metaprompt selection based on player profiles and game state.
9. Conclusion
This document provides a roadmap for the future development of the core gameplay loop in TTA. By adhering to the core principles, implementing the key components, and pursuing the long-term goals, we can create a truly unique and transformative gaming experience. This document should be treated as a living document, subject to continuous review and refinement as the project evolves.
