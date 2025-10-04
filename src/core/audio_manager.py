"""
Simple Audio Manager for Pokemon Faiths
Handles music and sound effects
"""

import pygame
import os
from typing import Dict, Optional
from .logger import get_logger

logger = get_logger('AudioManager')

class AudioManager:
    """Simple audio management system"""
    
    def __init__(self):
        self.music_volume = 0.7
        self.sfx_volume = 0.7
        self.current_music = None
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            logger.info("Audio system initialized successfully")
        except pygame.error as e:
            logger.error(f"Failed to initialize audio: {e}")
    
    def load_sound(self, file_path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound effect"""
        try:
            if file_path not in self.sounds:
                self.sounds[file_path] = pygame.mixer.Sound(file_path)
            return self.sounds[file_path]
        except pygame.error as e:
            logger.error(f"Failed to load sound {file_path}: {e}")
            return None
    
    def play_sfx(self, sound_name: str):
        """Play a sound effect"""
        sound_map = {
            'button_click': 'assets/audio/sfx/button_click.wav'
        }
        
        if sound_name in sound_map:
            sound = self.load_sound(sound_map[sound_name])
            if sound:
                sound.set_volume(self.sfx_volume)
                sound.play()
    
    def play_music(self, music_name: str, loop: int = -1):
        """Play background music with error handling"""
        music_map = {
            'menu': 'assets/audio/music/menu_theme.mp3'
        }
        
        if music_name not in music_map:
            logger.warning(f"Unknown music name: {music_name}")
            return
        
        music_path = music_map[music_name]
        
        # Check if file exists before trying to load
        if not os.path.exists(music_path):
            logger.warning(f"Music file not found: {music_path}")
            return
        
        try:
            if self.current_music != music_path:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loop)
                self.current_music = music_path
                logger.info(f"Playing music: {music_name}")
        except pygame.error as e:
            logger.error(f"Failed to play music {music_name}: {e}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Update volume for all loaded sounds
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

# Global audio manager instance
_audio_manager = None

def get_audio_manager() -> AudioManager:
    """Get the global audio manager instance"""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager
