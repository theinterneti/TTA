"""
Character Repository for database operations.

This module provides the CharacterRepository class that handles all database
operations for character data, including CRUD operations and queries.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.character import Character

logger = logging.getLogger(__name__)


class CharacterRepository:
    """Repository for character database operations."""
    
    def __init__(self):
        """Initialize the Character Repository."""
        # In-memory storage for now - will be replaced with actual database
        self._characters: Dict[str, Character] = {}
        self._player_characters: Dict[str, List[str]] = {}
        logger.info("CharacterRepository initialized with in-memory storage")
    
    def create_character(self, character: Character) -> Character:
        """
        Create a new character in the database.
        
        Args:
            character: The character to create
            
        Returns:
            The created character
        """
        # Store character
        self._characters[character.character_id] = character
        
        # Update player-character mapping
        if character.player_id not in self._player_characters:
            self._player_characters[character.player_id] = []
        
        self._player_characters[character.player_id].append(character.character_id)
        
        logger.debug(f"Created character {character.character_id} in repository")
        return character
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """
        Get a character by ID.
        
        Args:
            character_id: The character ID
            
        Returns:
            The character if found, None otherwise
        """
        character = self._characters.get(character_id)
        if character and character.is_active:
            return character
        return None
    
    def get_characters_by_player(self, player_id: str) -> List[Character]:
        """
        Get all active characters for a player.
        
        Args:
            player_id: The player ID
            
        Returns:
            List of active characters
        """
        character_ids = self._player_characters.get(player_id, [])
        characters = []
        
        for character_id in character_ids:
            character = self._characters.get(character_id)
            if character and character.is_active:
                characters.append(character)
        
        return characters
    
    def update_character(self, character: Character) -> Character:
        """
        Update an existing character.
        
        Args:
            character: The character to update
            
        Returns:
            The updated character
        """
        if character.character_id not in self._characters:
            raise ValueError(f"Character {character.character_id} not found")
        
        self._characters[character.character_id] = character
        
        logger.debug(f"Updated character {character.character_id} in repository")
        return character
    
    def delete_character(self, character_id: str) -> bool:
        """
        Delete a character (soft delete by marking inactive).
        
        Args:
            character_id: The character ID
            
        Returns:
            True if character was found and deleted, False otherwise
        """
        character = self._characters.get(character_id)
        if not character:
            return False
        
        character.is_active = False
        character.last_active = datetime.now()
        
        logger.debug(f"Deleted character {character_id} in repository")
        return True
    
    def get_character_count_by_player(self, player_id: str) -> int:
        """
        Get the count of active characters for a player.
        
        Args:
            player_id: The player ID
            
        Returns:
            Number of active characters
        """
        return len(self.get_characters_by_player(player_id))
    
    def search_characters(self, player_id: str, name_filter: str = None) -> List[Character]:
        """
        Search characters for a player with optional name filter.
        
        Args:
            player_id: The player ID
            name_filter: Optional name filter
            
        Returns:
            List of matching characters
        """
        characters = self.get_characters_by_player(player_id)
        
        if name_filter:
            name_filter_lower = name_filter.lower()
            characters = [
                char for char in characters 
                if name_filter_lower in char.name.lower()
            ]
        
        return characters
    
    def get_all_characters(self) -> List[Character]:
        """
        Get all active characters (for admin/testing purposes).
        
        Returns:
            List of all active characters
        """
        return [char for char in self._characters.values() if char.is_active]
    
    def clear_all_characters(self) -> None:
        """
        Clear all characters (for testing purposes).
        """
        self._characters.clear()
        self._player_characters.clear()
        logger.debug("Cleared all characters from repository")