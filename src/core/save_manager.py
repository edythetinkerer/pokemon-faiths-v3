"""
Save System for Pokemon Faiths
Handles game state persistence
"""

import json
import os
from datetime import datetime
from .logger import get_logger

logger = get_logger('SaveManager')

class SaveManager:
    """Manages game save data"""
    
    SAVE_DIR = 'data/saves'
    SAVE_FILE = 'save_data.json'
    
    def __init__(self):
        self.save_path = os.path.join(self.SAVE_DIR, self.SAVE_FILE)
        self._ensure_save_directory()
    
    def _ensure_save_directory(self):
        """Create saves directory if it doesn't exist"""
        try:
            os.makedirs(self.SAVE_DIR, exist_ok=True)
            logger.debug(f"Save directory ready: {self.SAVE_DIR}")
        except Exception as e:
            logger.error(f"Failed to create save directory: {e}")
    
    def save_exists(self):
        """Check if a save file exists"""
        exists = os.path.exists(self.save_path)
        logger.debug(f"Save file exists: {exists}")
        return exists
    
    def create_new_save(self, player_name, player_gender='male'):
        """Create a new save file with initial data"""
        try:
            save_data = {
                'version': '0.1.0',
                'created_at': datetime.now().isoformat(),
                'last_played': datetime.now().isoformat(),
                'player': {
                    'name': player_name,
                    'gender': player_gender,
                },
                'progress': {
                    'current_scene': 'bedroom',
                    'bedroom_position': {'x': 6 * 34, 'y': 6 * 34},
                    'bedroom_visited': False,
                    'intro_completed': True,
                },
                'pokemon': {
                    'party': [],  # Will be populated after starter choice
                    'storage': [],
                    'next_id': 1  # For unique Pokemon IDs
                },
                'flags': {
                    'has_starter': False,
                    'first_battle_complete': False
                },
                'playtime_seconds': 0
            }
            
            self.save_game(save_data)
            logger.info(f"New save created for player: {player_name}")
            return save_data
            
        except Exception as e:
            logger.error(f"Failed to create new save: {e}")
            return None
    
    def save_game(self, save_data):
        """Save game data to file"""
        try:
            # Update last played timestamp
            save_data['last_played'] = datetime.now().isoformat()
            
            with open(self.save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info("Game saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False
    
    def load_game(self):
        """Load game data from file"""
        try:
            if not self.save_exists():
                logger.warning("No save file found")
                return None
            
            with open(self.save_path, 'r') as f:
                save_data = json.load(f)
            
            # Backward compatibility - add missing fields for old saves
            if 'progress' not in save_data:
                save_data['progress'] = {}
            
            # Add missing progress fields with defaults
            progress = save_data['progress']
            if 'current_scene' not in progress:
                progress['current_scene'] = 'bedroom'
            if 'bedroom_position' not in progress:
                progress['bedroom_position'] = {'x': 6 * 34, 'y': 6 * 34}  # Safe center position
            if 'outside_position' not in progress:
                # Position in front of house door (house at ~3 tiles, door + 40px = in front)
                progress['outside_position'] = {'x': 6 * 34, 'y': 3 * 34 + 40}  # In front of door
            if 'bedroom_visited' not in progress:
                progress['bedroom_visited'] = True  # Assume visited for old saves
            
            # Force update old saves to use new teleport positions
            # This ensures old saves work with the new teleport system
            if save_data.get('version', '0.0.0') < '0.3.1':
                progress['bedroom_position'] = {'x': 6 * 34, 'y': 6 * 34}
                progress['outside_position'] = {'x': 6 * 34, 'y': 3 * 34 + 40}  # In front of door
                save_data['version'] = '0.3.1'
                logger.info("Updated old save to new teleport system (in front of door)")
                # Save the updated version
                self.save_game(save_data)
            
            logger.info(f"Game loaded successfully (Player: {save_data['player']['name']})")
            return save_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Save file corrupted: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return None
    
    def update_progress(self, key, value):
        """Update a specific progress value"""
        try:
            save_data = self.load_game()
            if save_data is None:
                logger.error("Cannot update progress: no save file")
                return False
            
            save_data['progress'][key] = value
            return self.save_game(save_data)
            
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
            return False
    
    def update_player_position(self, x, y):
        """Update player position in save file"""
        try:
            save_data = self.load_game()
            if save_data is None:
                return False
            
            save_data['progress']['bedroom_position'] = {'x': x, 'y': y}
            return self.save_game(save_data)
            
        except Exception as e:
            logger.error(f"Failed to update player position: {e}")
            return False
    
    def delete_save(self):
        """Delete the save file"""
        try:
            if self.save_exists():
                os.remove(self.save_path)
                logger.info("Save file deleted")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete save file: {e}")
            return False
    
    def get_save_info(self):
        """Get basic info about the save without loading everything"""
        try:
            save_data = self.load_game()
            if save_data is None:
                return None
            
            return {
                'player_name': save_data['player']['name'],
                'last_played': save_data['last_played'],
                'current_scene': save_data['progress']['current_scene'],
                'playtime': save_data.get('playtime_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get save info: {e}")
            return None

# Global save manager instance
_save_manager = None

def get_save_manager():
    """Get the global save manager instance"""
    global _save_manager
    if _save_manager is None:
        _save_manager = SaveManager()
    return _save_manager

