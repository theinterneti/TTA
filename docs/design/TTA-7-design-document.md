Therapeutic Text Adventure (TTA) 7 Design Document
1. Introduction
1.1 Overview
The Therapeutic Text Adventure (TTA) is an innovative platform that merges the immersive nature of text-based adventure games with the potential for self-discovery and healing. Set within an infinite multiverse, TTA provides a personalized and potentially transformative experience for each player. TTA leverages AI agents, dynamic content generation, and a sophisticated knowledge graph to create a unique and engaging experience. This document outlines the core concepts, design principles, system architecture, and development plan for TTA 7.
1.2 Project Goals
To provide a unique, personalized, and potentially healing experience through a text-based adventure.
To use a combination of player choices, AI-driven narratives, and a sophisticated knowledge graph to create a dynamic and responsive game world.
To offer a safe space for players to explore their inner worlds, confront personal challenges, and potentially experience a degree of healing.
To create a "living, breathing world" that responds to player choices, offering a unique and engaging adventure.
1.3 Target Audience
Individuals seeking a personalized, engaging, and potentially therapeutic interactive experience; specifically, individuals who may not have access to or may be resistant to traditional mental health services.
1.4 Design Principles
TTA is guided by several key principles:
Player-Centricity: The player's experience is the top priority.
Concept-Driven Design: The game world is built using universal concepts as its foundation.
AI Collaboration: AI agents are integral partners in crafting dynamic, responsive, and engaging experiences.
Modular Design: The game is structured into manageable modules that can be developed, iterated upon, and expanded independently.
Interconnectedness: The game world is designed to be interconnected, with player actions having meaningful consequences.
Healing Potential: Therapeutic concepts are subtly integrated to support players on their journey of self-discovery.
Emergent Gameplay: The game encourages unexpected events that arise from interactions between players, AI agents, and the game world.
Ethical Considerations: The system adheres to strict ethical guidelines, prioritizing player safety, well-being, and responsible use of AI.
2. Game World and Narrative
2.1 The Multiverse
The core setting of TTA is an infinite multiverse, a vast expanse containing countless parallel universes, each with its own unique physical laws, histories, cultures, and inhabitants. This concept is central to the game, offering a nearly limitless playground for storytelling and diverse experiences. The interconnectedness of these universes allows for emergent gameplay and a sense of a living, breathing world.
2.2 The Nexus
The Nexus is a central hub connecting all universes within the TTA multiverse. It exists outside the boundaries of individual universes, serving as a point of access and transition between them. Each universe has a unique manifestation within the Nexus. The nature of the connection between a universe and the Nexus can vary (one-way, two-way, stable, unstable). The method of travel to and from the Nexus is specified, and there can be limitations or dangers associated with the connection. The Nexus allows for interaction between different universes. The Nexus is managed by the Nexus Manager Agent (NMA). The player will likely encounter the Nexus during the Genesis sequence.
2.3 Connected Universes
Universes are connected to the Nexus and to each other through various means. Connections between universes are essential to player progression, allowing them to move through and influence different worlds. These connections can be stable or unstable, and players may encounter bleedthrough or resonance between universes. Bleedthrough refers to the phenomenon of elements from one universe leaking into another. Resonance is the way in which events or choices in one universe can affect others.
2.4 Universe Details
The TTA multiverse is populated with a variety of unique universes, each with distinct characteristics, history, and themes. The following are some of the initially created universes in TTA:
Aethelgard: A universe characterized by its blend of high fantasy elements and emerging technologies. It has a unique technology and magic system. The world of Aethelgard is a land of diverse regions. It is a world where magic is a tangible force, and technology is still in its early stages of development. Aethelgard will feature various factions with their own agendas and conflicts.
Musketeer Earth: An alternate version of our own planet, set in a fictionalized 17th century. This world is inspired by the historical era, featuring elements of chivalry, political intrigue, romance, and swashbuckling adventure. It incorporates global stories from the 17th century to create a richer, interconnected world. Metaconcepts such as Code of Honor, Balance of Power, and The Price of Progress are central to this world.
Steampunk Earth: Another alternate version of our world, characterized by its unique blend of Victorian-era aesthetics and advanced steam-powered technology. This world will feature elaborate machinery, airships, and mechanical contraptions. It combines the familiar with the fantastical. The social structures, class systems, and scientific ideas of the Victorian era will be explored within this setting.
Post-Apocalyptic Earth: Represents a possible future for our world, one ravaged by a cataclysmic event. The world will be a harsh environment where resources are scarce, and the remnants of civilization struggle to survive.
Our Universe: A representation of our own reality, allowing for the potential to explore familiar locations and events. This universe is enhanced through web resource utilization, providing realistic details about Earth, its history, and its cultures.
Alternate Earths: Linked to individual players, each Alternate Earth is a unique version of our world, shaped by the player's choices and experiences within the TTA multiverse. These worlds reflect the individual player's narrative and provide a personalized and relevant setting for their unique story.
3. Player Experience
3.1 Text-Based Interaction
The game is primarily driven by text-based interaction. Players use text commands to interact with the world, characters, and narrative. The game responds with descriptive text, dialog, and the results of player actions. The player's input is parsed, and the intended action is identified. The core gameplay loop revolves around exploration, interaction, character development, and narrative progression.
3.2 Genesis Sequence
The Genesis Sequence is the initial process for creating a new character (and if desired universes, worlds, locations, themes, etc.). It is a fundamental mechanism of TTA that allows players to define the parameters of their unique game experience. The sequence is guided by the Universe Generator Agent (UGA) and consists of the following steps:
Seed Concept: The player provides a core idea, theme, or concept for the universe.
Universe Parameters: The player and the Universe Generator Agent (UGA) collaborate to define the fundamental laws, properties, and nature of the universe.
World Generation: The World Builder Agent (WBA) generates the initial world(s) within the universe, based on the universe parameters.
Character Generation: The Character Creator Agent (CCA) generates descriptions of initial characters within the world.
Nexus Connection: The Nexus Manager Agent (NMA) establishes a connection between the new universe and the Nexus, creating a unique manifestation of the universe within the Nexus.
3.3 Exploration
Players will uncover the secrets of the multiverse. How their characters own universe is connected to the nexus. That all universes are connected to the Nexus through their individual means. Characters may find themselves moving between different universes via exotic and unique methods. Within each universe, characters will encounter diverse worlds and locations. The Narrative Generator Agent (NGA), in collaboration with the World Builder Agent (WBA) and the Lore Keeper Agent (LKA), generates descriptions of the locations, including their environments, inhabitants, and points of interest. Players can interact with the environment, objects, and characters within the locations using text commands. Game entities are saved into the knowledge graph. High quality materials can be shared with home base if players opt-in.
3.4 Character Development
Players create and develop their own characters, shaping their personalities, skills, and relationships. Character creation begins during the Genesis Sequence, where the player defines some aspects of their character. As players progress, they develop their character's traits and abilities. The character (and player) profile is crucial for personalizing the game experience.
3.5 Dynamic Narrative Progression
The game's narrative unfolds dynamically based on player choices, AI-generated content, and the evolving state of the game world. The game is not a static collection of events but a dynamic world that reacts to the player's actions. Player choices have significant consequences and impact the story's direction and outcomes. The narrative adapts to the player, ensuring a personalized experience.
3.6 Therapeutic Elements
The game incorporates therapeutic concepts and techniques in a subtle manner. This is designed to promote self-discovery, emotional processing, and personal growth. Themes of trauma, addiction, and self-discovery are addressed in a non-intrusive manner. The goal is to provide a space where players can explore their own thoughts and behaviors without judgment.
Our approach is rooted in narrative therapy, which posits that individuals make meaning of their lives through the stories they tell themselves and others. This approach aligns with our understanding that personal experience is interpreted through the lens of narrative. Narrative therapy emphasizes that people are not their problems; rather, problems are separate entities that can be explored and challenged. This approach prioritizes a collaborative, respectful, and optimistically curious environment, where the therapist (or in our case, the game) acts as an investigator or explorer of the client's experience. The client is seen as an equal partner with local knowledge that may initially be inaccessible. This framework aligns with our focus on player agency and collaborative storytelling.
Furthermore, we are aware of the importance of therapeutic documentation, which involves creating tangible records of a player's progress that can be revisited and celebrated. These documents include audio or video tapes, drawings, declarations, declarations, certificates, awards, and letters. While we will not be including physical documentation, our approach to character development, game history, and player choices can function as virtual documentation that reflects a player's unique journey through our multiverse. We plan to create interfaces for users to explore their journey, making progress tangible. By adopting a narrative therapy approach, we aim to help players re-author their personal stories. Through exploring the multiverse and facing challenges, players can externalize their problems, discover hidden talents, and create new, more empowered narratives. This aligns with our design principle of creating meaningful, interconnected experiences.
TTA does not directly present itself as a therapeutic intervention; instead, it offers opportunities for therapeutic exploration within the context of an engaging game. Therapeutic concepts are woven into the game through several mechanisms:
Concept Mapping: We use a knowledge graph to map and relate therapeutic concepts such as "Trauma," "Resilience," "Acceptance," "Self-Compassion," and "Mindfulness". These concepts act as building blocks for the game's worlds, characters, and narratives. By doing this, we allow our AI agents to create rich narratives informed by a therapeutic framework. We intend to use these concepts to generate content in ways that will emphasize exploration of these topics without ever using them as direct instruction.
Dynamic Narrative Generation: AI agents generate dynamic content based on player choices and game context. This means that players are not subject to a predetermined narrative, but their choices and actions will influence the narrative in ways that explore these therapeutic concepts. For example, if a player makes a choice that indicates a need for self-compassion, the game may offer situations where the player is given the opportunity to practice this skill.
Character Arcs: The characters in TTA are designed with depth and complexity, and their arcs often reflect the struggles and growth associated with therapeutic journeys. Characters may face challenges, experience setbacks, and ultimately find ways to overcome their difficulties, thus modeling the therapeutic process. The idea is not to create perfect characters but to create believable ones whose struggles are relatable and can be a source of insight.
Philosophical Dialog: Non-player characters (NPCs) may engage players in philosophical discussions, encouraging self-reflection on their own beliefs and values. These discussions are meant to provoke thought and self-inquiry in ways that resonate with the player’s own experience. The idea is not to instruct the player on what to think, but to create the opportunity for them to consider their own beliefs through the lens of a unique, fictional character.
Hidden Storylines: Secret storylines are revealed to players who explore the game world deeply. These storylines may offer a space for players to explore themes related to trauma, addiction, and self-discovery, while also feeling like a rewarding activity for the player. This method emphasizes exploration and player agency.
These various integration techniques are designed to create a nuanced approach to therapeutic engagement. Players are encouraged to interact with these concepts at their own pace. We do not aim to force them into any type of experience. Our goal is to provide a space for those who seek one.
The game is designed to be a safe, consequence-rich environment where players can explore their inner world and re-author their personal narratives. The game offers a nuanced approach to therapeutic engagement. The approach is rooted in narrative therapy, which posits that individuals make meaning of their lives through the stories they tell themselves and others.
The game incorporates therapeutic concepts and techniques, such as trauma, addiction, and self-discovery, in a subtle manner. This is designed to promote self-discovery, emotional processing, and personal growth. The goal is to provide a space where players can explore their own thoughts and behaviors without judgment.
We are committed to the ethical use of AI and the protection of player privacy. We will continue to refine our approach based on feedback and further development as we iterate and test.
4. Core Gameplay Loop
The core gameplay loop of TTA 7 revolves around the following elements:
Player Input: The player enters a text command describing their desired action.
Input Processing (IPA): The Input Processor Agent (IPA) parses the player's input, identifies the intent, and extracts key entities.
AI Agent Orchestration: LangGraph manages the workflow, activating the appropriate AI agents based on the IPA's output and the current game state.
AI Agent Processing: The activated AI agent processes the input and generates a response, adhering to metaconcepts.
Output Generation (NGA): The Narrative Generator Agent (NGA) synthesizes information from other agents and generates the final text output presented to the player.
Data Storage (Neo4j): The Neo4j database stores and updates player profiles, world data, character data, and the ongoing narrative.
5. System Architecture
TTA 7 is built on a robust architecture designed to support dynamic content generation, persistent game worlds, and complex AI agent interactions. The key components include:
5.1 Technology Stack
Large Language Model (LLM): Qwen2.5 is the primary language model, providing natural language understanding, text generation, and reasoning capabilities.
Orchestration Framework: LangGraph manages the interactions between different AI agent roles and maintains the overall game state.
Knowledge Graph Database: Neo4j stores the game's knowledge graph, representing the game world, its entities, and their relationships.
Agent Framework: LangChain provides tools and abstractions for building applications with LLMs, including tool definition and prompt template management.
Data Validation: Pydantic is used for data validation and settings management, ensuring data consistency and helping structure interactions.
Output Control (Optional): Guidance can be used for more fine-grained control over LLM output.
Web Scraping (Optional): FireCrawl is used to extract information from the web for "Our Universe" and "Alternate Earths" settings.
Machine Learning (Optional): TensorFlow is used for specialized tasks like model training and rejection sampling.
5.2 Modules and Submodules
The system is organized into several modules, each responsible for a specific aspect of the game's functionality:
Storytelling Module:
Narration: Text Generation, Narrative Engine, Concept Library
World Building: Universe Generator, World Builder Agent, Location Generator, Faction Generator, Economy Generator, History Generator
Concepts: Concept Mapping, Concept Application, Concept Exploration
Character Module:
Personality: Personality Generator, Trait System, Relationship System
Connections with the World: Background Generator, Faction Affiliation, Role Generator
Player Module:
Profile: Psychological Profiling, Trauma Tracking, Addiction Tracking, Progress Tracking
Worlds: World Management, Universe Linking, Character Management
AI Agent Module:
Agent Management:
Agent Lifecycle Management: This submodule is responsible for creating, initializing, activating, and terminating AI agents. It manages the agent pool and ensures that agents are available when needed.
Agent Communication: This submodule handles the communication between different AI agents. It defines the message format, manages message queues, and ensures reliable message delivery.
Agent Tools:
Tool Definition: This submodule provides the framework for defining tools that AI agents can use, including specifying the tool's name, description, input parameters, and output format.
Tool Execution: This submodule handles the execution of tools when called by an AI agent, interacting with external systems or the knowledge graph as needed.
Prompt Management:
Prompt Engineering: This submodule focuses on the design and optimization of prompts for each AI agent, including the use of prompt templates, meta-prompts, and dynamic prompt generation techniques.
Prompt Storage: This submodule manages the storage and retrieval of prompts, ensuring that the appropriate prompt is used for each agent in each situation.
Knowledge Graph Module:
Graph Management:
Graph Traversal: This submodule provides functions for navigating the knowledge graph, retrieving information about nodes and relationships, and performing complex graph queries.
Data Validation: This submodule ensures that data being added to the knowledge graph is valid and conforms to the defined schema, maintaining the integrity of the graph.
Relationship Inference: This submodule implements algorithms for inferring new relationships between entities in the knowledge graph based on existing data and predefined rules, expanding the graph's knowledge base.
Schema Definition:
Node Types: This submodule defines the different types of nodes that can exist in the knowledge graph, such as characters, locations, items, and concepts, and their associated properties.
Relationship Types: This submodule defines the different types of relationships that can exist between nodes, such as "is_a," "located_in," and "related_to," and their associated properties.
Property Definitions: This submodule defines the properties that can be associated with nodes and relationships, including their data types, constraints, and descriptions.
Content Moderation Module:
Content Filtering:
Automated Content Filtering: This submodule implements algorithms and techniques for automatically filtering out potentially harmful, inappropriate, or offensive content generated by AI agents.
Human Review (HITL): This submodule provides a mechanism for human moderators to review flagged content and make decisions about its suitability for the game.
Feedback Mechanisms:
Player Reporting: This submodule allows players to report content they find problematic, providing valuable feedback for improving the moderation system.
Moderator Tools: This submodule provides tools for human moderators to efficiently review and manage flagged content, track moderation decisions, and communicate with players.
Therapeutic Module
Intervention Design:
Therapeutic Concept Integration: This submodule focuses on the integration of therapeutic concepts and techniques into the game's narrative, character interactions, and challenges.
Narrative Techniques: This submodule explores the use of narrative techniques to promote self-reflection, emotional processing, and personal growth.
Ethical Protocols:
Player Safety: This submodule defines protocols and procedures for ensuring player safety and well-being, including handling sensitive topics, providing resources, and responding to crises.
Data Privacy: This submodule establishes guidelines for collecting, storing, and using player data in a way that protects their privacy and adheres to ethical principles.
5.3 AI Agent Design
AI agents are integral to the TTA experience, each with specific roles and responsibilities:
Universe Generator Agent (UGA): Guides players through the "Genesis Sequence" to define the parameters of their new universe.
World Builder Agent (WBA): Populates universes with locations, characters, and items.
Character Creator Agent (CCA): Develops characters with unique traits, relationships, and motivations.
Narrative Generator Agent (NGA): Creates dynamic storylines that respond to player choices and the game world.
Lore Keeper Agent (LKA): Ensures consistency of the game's lore.
Input Processor Agent (IPA): Parses and recognizes player input, identifying the player's intent.
Nexus Manager Agent (NMA): Manages the connections between universes within the Nexus.
Player Onboarding Agent (POA): Guides new players through the initial experience.
Nexus Travel Agent (NTA): Manages player travel between universes through the Nexus.
Therapeutic Agent (TA): Provides therapeutic interventions and support.
5.4 AI Agent Interaction Patterns
AI agents communicate and collaborate using several interaction patterns:
Request-Response: One agent requests information or an action from another agent and waits for a response.
Delegation: One agent delegates a complex task to another agent.
Publish-Subscribe: Agents publish events or information, and other agents subscribe to receive notifications about those events.
5.5 Prompt Construction
Prompts are carefully crafted to guide Qwen2.5 in its various agent roles. A prompt typically includes the following components:
Metaconcepts (Global Instructions)
Agent Role and Task Definition
Contextual Information
Available Tools (and Instructions for Use)
Output Format Instructions
Prompt templates are used to manage the complexity of prompt engineering, and dynamic prompt generation techniques are employed for more advanced scenarios.
5.6 Error Handling and Recovery
TTA employs a multi-layered approach to error handling:
Input Validation (Pydantic)
Try-Except Blocks (Python)
Structured Error Responses (JSON)
LangGraph Conditional Edges
Fallback Mechanisms
Human-in-the-Loop (HITL)
Logging
5.7 Knowledge Graph
At the heart of TTA is a sophisticated knowledge graph, built using Neo4j, that stores concepts, attributes, and relationships. The knowledge graph provides a structured context for AI agents and a mechanism to maintain a consistent and coherent game world.
Design Principles: Clarity, Efficiency, Flexibility, Scalability, Consistency, Extensibility.
Node Types: Abstract, AIAgent, Category, Character, Concept, Culture, Event, Faction, Item, Language, Location, Metaconcept, Nexus, Prompt, PromptChain, Region, ReviewProcess, ReviewStep, HumanReviewer, Comment, Information, ValidationLog, TimeSystem, TimePoint, TimeUnit, TimeBranch, TimeZone, Universe, Player.
Relationship Types: A comprehensive set of relationship types is defined to capture the connections between nodes, with properties to provide additional context and information.
5.8 Content Creation and Review
Content Creation Guidelines:
Consistency: All content created for the game (e.g., descriptions, dialogue, concepts) must be consistent with the established lore, rules, and metaconcepts.
Clarity: Content should be written in clear, concise, and unambiguous language.
Engagement: Content should be engaging, immersive, and appropriate for the target audience.
Therapeutic Value: Content should be designed to promote self-reflection, emotional processing, and personal growth, where appropriate.
Ethical Considerations: Content creators must adhere to strict ethical guidelines, avoiding harmful stereotypes, biases, and potentially triggering content.
Style Guide: A detailed style guide will be developed to ensure consistency in tone, style, and formatting across all content.
Rejection Sampling and Data Augmentation:
Purpose: Rejection sampling will be used to improve the quality and diversity of the training data for AI agents, particularly for generating narrative content and dialogue.
Process:
Generate multiple candidate outputs using the AI agent.
Evaluate each candidate based on predefined criteria (e.g., consistency, relevance, engagement, therapeutic value).
Select the candidate that best meets the criteria, or reject all candidates if none meet a minimum threshold.
Data Augmentation: Accepted outputs can be added to the training data to improve the agent's performance over time.
Human Review: Rejected outputs can be reviewed by human editors to identify areas for improvement in the AI agent's generation process.
Test-Time Scaling and Decoding Strategies:
Scaling: Techniques like model parallelism and distributed training will be explored to enable the use of larger and more powerful language models.
Decoding: Different decoding strategies will be evaluated to optimize the balance between creativity, coherence, and computational cost. These strategies may include:
Temperature Sampling: Adjusting the randomness of the generated text.
Top-k Sampling: Limiting the selection of the next token to the k most likely options.
Nucleus Sampling: Limiting the selection to a subset of the most likely options that exceed a certain cumulative probability threshold.
Beam Search: Exploring multiple possible sequences in parallel to find the most likely overall sequence.
Contrastive Search: Encourages diversity by penalizing outputs that are too similar to previous outputs or to the input prompt.
Length Normalization: Adjusts the probabilities of tokens to account for the length of the generated text.
Repetition Penalty: Penalizes the LLM for repeating the same tokens or phrases too often.
Dynamic Decoding: The ideal decoding strategy can vary depending on the context. TTA should aim to dynamically adjust the decoding strategy based on factors like agent role, desired output characteristics, and player preferences.
Guidance: The Guidance library will be used to constrain and guide the language model's generation process, ensuring that it adheres to the defined prompt chains and rules.
6. Therapeutic Integration
TTA is designed to be a safe, consequence-rich environment where players can explore their inner world and re-author their personal narratives. The game offers a nuanced approach to therapeutic engagement:
Theoretical Framework: The approach is rooted in narrative therapy, which posits that individuals make meaning of their lives through the stories they tell themselves and others.
Subtle Integration: Therapeutic concepts are woven into the game through concept mapping, dynamic narrative generation, character arcs, philosophical dialog, and hidden storylines.
Player Choice and Agency: Player agency is foundational, with player decisions shaping their experience and allowing them to reflect on their own decision-making processes, personal values, and approaches to overcoming problems.
AI Collaboration and Therapeutic Guidance: AI agents act as storytellers, world managers, and subtle therapeutic guides, offering cues and prompts in the form of questions and comments embedded in the game text, without direct instruction.
Interconnectedness and Meaningful Consequences: Player actions have consequences that ripple across the game world and the multiverse, providing a sense of agency and ownership.
Ethical Considerations: Ethical considerations are paramount, with a focus on player privacy, avoiding harm, responsible AI, and transparency.
7. Development Plan
TTA is being developed using a phased approach:
Prototype Phase: Develops a basic, functional prototype to demonstrate the core gameplay loop and technical feasibility.
Phase 1 (Core Functionality): Develops the core knowledge graph structure, implements the "Genesis" sequence, basic AI capabilities, and integrates web resources.
Phase 2 (Expansion and Refinement): Expands the knowledge graph, develops more sophisticated prompt chains.
Phase 3: Implements advanced features like the Collective Unconscious, AI-driven therapy, and a universal economy.
Phase 4: Testing, iteration, and refinement.
The development process follows an Agile methodology, with Git for version control, and a combination of communication and project management tools.
8. Ethical Considerations and Player Safety
TTA is committed to ethical AI development and operation, with a strong emphasis on player safety and well-being. Key considerations include:
Privacy and Data Security: Data minimization, anonymization, informed consent, and robust security measures are implemented to protect player data. The use of a local LLM and database enhances privacy.
Bias Mitigation and Inclusivity: The game actively promotes diversity in character representation and uses inclusive language. Bias detection and mitigation strategies are employed, along with ongoing monitoring and community feedback.
Therapeutic Responsibility: TTA is not a replacement for professional therapy. The game provides a safe space for self-discovery and growth, with subtle integration of therapeutic concepts, player agency, and informed consent. Crisis intervention protocols are in place, and collaboration with mental health professionals is ongoing.
Content Moderation and Safety: A robust content moderation system combines AI-driven filtering with human oversight (Human-in-the-Loop, HITL) to address potentially harmful, inappropriate, or inconsistent content. Community guidelines and reporting mechanisms are also in place.
9. Future Development
Potential areas for future development and expansion include:
Enhanced AI Capabilities: More sophisticated NLP models, improved contextual awareness, dynamic prompt generation, and emotional intelligence.
Expanded Gameplay Features: Multiplayer support, procedural generation, crafting and economy systems, a more robust combat system, and mini-games.
Therapeutic Applications: Targeted interventions, collaboration with mental health professionals, and personalized content.
Platform and Accessibility: Mobile app, voice integration, and VR/AR integration.
Community and Modding: User-generated content, modding support, and community building.
