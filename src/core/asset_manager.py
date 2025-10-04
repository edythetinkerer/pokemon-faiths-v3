"""
Centralized Asset Manager for Pokemon Faiths
Handles loading and caching of images and sounds to improve performance
"""

import pygame
import os
import sys
from typing import Dict, Optional
from .logger import get_logger

logger = get_logger('AssetManager')

class AssetManager:
    """Centralized asset loading and caching system"""
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.base_path = self._get_base_path()
        
    def _get_base_path(self) -> str:
        """Get the correct base path for assets"""
        if getattr(sys, 'frozen', False):
            # Running as executable
            return sys._MEIPASS
        else:
            # Running as script - go up TWO levels from src/core/ to project root
            # __file__ is in src/core/, need to go: src/core/ -> src/ -> project root
            core_dir = os.path.dirname(os.path.abspath(__file__))  # src/core/
            src_dir = os.path.dirname(core_dir)  # src/
            project_root = os.path.dirname(src_dir)  # project root
            return project_root
    
    def load_image(self, relative_path: str, scale_size: Optional[tuple] = None) -> pygame.Surface:
        """
        Load and cache an image with optional scaling
        
        Args:
            relative_path: Path relative to project root - should always start with 'assets/'
            scale_size: Optional (width, height) tuple for scaling
        """
        # Normalize path - ensure it starts with 'assets/'
        if not relative_path.startswith('assets/'):
            relative_path = f'assets/{relative_path}'
        
        # Create cache key including scale size
        cache_key = f"{relative_path}_{scale_size}" if scale_size else relative_path
        
        # Return cached version if available
        if cache_key in self.images:
            return self.images[cache_key]
        
        # Load the image
        full_path = os.path.join(self.base_path, relative_path)
        
        try:
            if not os.path.exists(full_path):
                logger.warning(f"Asset not found: {full_path}")
                # Return a placeholder surface
                surface = pygame.Surface((32, 32))
                surface.fill((255, 0, 255))  # Magenta placeholder
                self.images[cache_key] = surface
                return surface
            
            surface = pygame.image.load(full_path).convert_alpha()
            
            # Apply scaling if requested
            if scale_size:
                surface = pygame.transform.scale(surface, scale_size)
            
            # Cache and return
            self.images[cache_key] = surface
            logger.debug(f"Loaded and cached image: {relative_path}")
            return surface
            
        except pygame.error as e:
            logger.error(f"Error loading image {full_path}: {e}")
            # Return placeholder
            surface = pygame.Surface((32, 32))
            surface.fill((255, 0, 255))
            self.images[cache_key] = surface
            return surface
    
    def load_sound(self, relative_path: str) -> Optional[pygame.mixer.Sound]:
        """
        Load and cache a sound effect
        
        Args:
            relative_path: Path relative to project root (e.g., 'audio/sfx/button_click.wav')
            
        Returns:
            pygame.mixer.Sound or None if loading failed
        """
        # Return cached version if available
        if relative_path in self.sounds:
            return self.sounds[relative_path]
        
        # Load the sound
        full_path = os.path.join(self.base_path, relative_path)
        
        try:
            if not os.path.exists(full_path):
                logger.warning(f"Sound not found: {full_path}")
                return None
            
            sound = pygame.mixer.Sound(full_path)
            self.sounds[relative_path] = sound
            logger.debug(f"Loaded and cached sound: {relative_path}")
            return sound
            
        except pygame.error as e:
            logger.error(f"Error loading sound {full_path}: {e}")
            return None
    
    def preload_assets(self, asset_list: list):
        """
        Preload a list of assets for better performance
        
        Args:
            asset_list: List of tuples (type, path, optional_scale)
                       e.g., [('image', 'wood tiles/bed.png', (50, 30)), ('sound', 'audio/sfx/click.wav')]
        """
        logger.info(f"Preloading {len(asset_list)} assets...")
        for asset_info in asset_list:
            asset_type = asset_info[0]
            path = asset_info[1]
            
            if asset_type == 'image':
                scale = asset_info[2] if len(asset_info) > 2 else None
                self.load_image(path, scale)
            elif asset_type == 'sound':
                self.load_sound(path)
        
        logger.info(f"Preloading complete: {len(asset_list)} assets loaded")
    
    def get_cache_info(self) -> dict:
        """Get information about cached assets"""
        return {
            'images_cached': len(self.images),
            'sounds_cached': len(self.sounds),
            'total_assets': len(self.images) + len(self.sounds)
        }
    
    def clear_cache(self):
        """Clear all cached assets to free memory"""
        self.images.clear()
        self.sounds.clear()
        logger.info("Asset cache cleared")
    
    def clear_images(self):
        """Clear only image cache"""
        self.images.clear()
        logger.info("Image cache cleared")
    
    def clear_sounds(self):
        """Clear only sound cache"""
        self.sounds.clear()
        logger.info("Sound cache cleared")

# Global asset manager instance
_asset_manager = None

def get_asset_manager() -> AssetManager:
    """Get the global asset manager instance, creating it if needed"""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager()
    return _asset_manager

def preload_common_assets():
    """Preload commonly used assets"""
    asset_manager = get_asset_manager()
    
    common_assets = [
        # Wood tiles
        ('image', 'wood tiles/damaged_wood_tile.png', (34, 34)),
        ('image', 'wood tiles/damaged_wood_tile2.png', (34, 34)),
        ('image', 'wood tiles/damaged_wood_tile3.png', (34, 34)),
        
        # Furniture
        ('image', 'wood tiles/damaged_bed.png', (50, None)),  # Width only, preserve aspect
        ('image', 'wood tiles/damaged_table.png', (50, None)),
        ('image', 'wood tiles/damaged_bookshelf.png', (None, 50)),  # Height only
        
        # Character sprites
        ('image', 'character/elder.png'),
        ('image', 'character/rotations/south.png', (48, 48)),
        ('image', 'character/rotations/north.png', (48, 48)),
        ('image', 'character/rotations/east.png', (48, 48)),
        ('image', 'character/rotations/west.png', (48, 48)),
        
        # Audio
        ('sound', 'audio/sfx/button_click.wav'),
    ]
    
    asset_manager.preload_assets(common_assets)
