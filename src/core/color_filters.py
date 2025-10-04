"""
Color Filter System for Pokemon Faiths
Applies atmospheric color overlays and effects to scenes
"""

import pygame
from typing import Tuple, Optional
from .logger import get_logger

logger = get_logger('ColorFilters')

class ColorFilter:
    """Manages color filters and visual effects for scenes"""
    
    # Predefined filter presets
    PRESETS = {
        'none': {'color': (0, 0, 0), 'alpha': 0, 'blend': pygame.BLEND_RGBA_MULT},
        
        # Darkness and shadow filters
        'dark': {'color': (40, 40, 60), 'alpha': 120, 'blend': pygame.BLEND_RGBA_MULT},
        'very_dark': {'color': (20, 20, 30), 'alpha': 160, 'blend': pygame.BLEND_RGBA_MULT},
        'night': {'color': (15, 15, 40), 'alpha': 140, 'blend': pygame.BLEND_RGBA_MULT},
        'cave': {'color': (10, 10, 15), 'alpha': 180, 'blend': pygame.BLEND_RGBA_MULT},
        
        # Atmospheric filters
        'sepia': {'color': (255, 200, 150), 'alpha': 80, 'blend': pygame.BLEND_RGBA_MULT},
        'old_photo': {'color': (255, 220, 180), 'alpha': 100, 'blend': pygame.BLEND_RGBA_MULT},
        'fog': {'color': (200, 200, 220), 'alpha': 60, 'blend': pygame.BLEND_RGBA_ADD},
        'mist': {'color': (180, 190, 200), 'alpha': 40, 'blend': pygame.BLEND_RGBA_ADD},
        
        # Mood filters
        'melancholy': {'color': (100, 100, 150), 'alpha': 70, 'blend': pygame.BLEND_RGBA_MULT},
        'despair': {'color': (60, 60, 80), 'alpha': 100, 'blend': pygame.BLEND_RGBA_MULT},
        'horror': {'color': (80, 40, 40), 'alpha': 90, 'blend': pygame.BLEND_RGBA_MULT},
        'dread': {'color': (40, 20, 50), 'alpha': 110, 'blend': pygame.BLEND_RGBA_MULT},
        
        # Time of day filters
        'dawn': {'color': (255, 200, 150), 'alpha': 50, 'blend': pygame.BLEND_RGBA_MULT},
        'dusk': {'color': (200, 120, 80), 'alpha': 70, 'blend': pygame.BLEND_RGBA_MULT},
        'sunset': {'color': (255, 150, 100), 'alpha': 60, 'blend': pygame.BLEND_RGBA_MULT},
        'moonlight': {'color': (100, 100, 180), 'alpha': 90, 'blend': pygame.BLEND_RGBA_MULT},
        
        # Special effects
        'red_tint': {'color': (255, 100, 100), 'alpha': 60, 'blend': pygame.BLEND_RGBA_MULT},
        'blue_tint': {'color': (100, 100, 255), 'alpha': 60, 'blend': pygame.BLEND_RGBA_MULT},
        'green_tint': {'color': (100, 255, 100), 'alpha': 60, 'blend': pygame.BLEND_RGBA_MULT},
        'purple_haze': {'color': (150, 100, 200), 'alpha': 70, 'blend': pygame.BLEND_RGBA_MULT},
        
        # Intensity filters
        'slight_dark': {'color': (80, 80, 90), 'alpha': 50, 'blend': pygame.BLEND_RGBA_MULT},
        'moderate_dark': {'color': (60, 60, 70), 'alpha': 90, 'blend': pygame.BLEND_RGBA_MULT},
        'heavy_dark': {'color': (30, 30, 40), 'alpha': 140, 'blend': pygame.BLEND_RGBA_MULT},
        
        # Dramatic filters
        'ominous': {'color': (50, 40, 60), 'alpha': 100, 'blend': pygame.BLEND_RGBA_MULT},
        'eerie': {'color': (80, 100, 120), 'alpha': 80, 'blend': pygame.BLEND_RGBA_MULT},
        'sinister': {'color': (60, 30, 40), 'alpha': 110, 'blend': pygame.BLEND_RGBA_MULT},
    }
    
    def __init__(self, surface_size: Tuple[int, int]):
        """
        Initialize color filter system
        
        Args:
            surface_size: (width, height) of the surface to apply filters to
        """
        self.surface_size = surface_size
        self.current_filter = 'none'
        self.custom_filter = None
        self.transition_active = False
        self.transition_progress = 0.0
        self.transition_duration = 0.0
        self.transition_from = None
        self.transition_to = None
        
        logger.info(f"Color filter system initialized for {surface_size[0]}x{surface_size[1]} surface")
    
    def set_filter(self, preset_name: str, instant: bool = True):
        """
        Set a color filter by preset name
        
        Args:
            preset_name: Name of the preset filter
            instant: If True, apply immediately. If False, can be used with transitions
        """
        if preset_name not in self.PRESETS:
            logger.warning(f"Unknown filter preset: {preset_name}")
            return
        
        if instant:
            self.current_filter = preset_name
            self.custom_filter = None
            self.transition_active = False
            logger.debug(f"Applied filter: {preset_name}")
        else:
            # Set up for transition
            self.transition_to = preset_name
    
    def set_custom_filter(self, color: Tuple[int, int, int], alpha: int, 
                         blend_mode: int = pygame.BLEND_RGBA_MULT):
        """
        Set a custom color filter
        
        Args:
            color: RGB color tuple (0-255 for each)
            alpha: Transparency (0-255, 0 = transparent, 255 = opaque)
            blend_mode: Pygame blend mode constant
        """
        self.custom_filter = {
            'color': color,
            'alpha': alpha,
            'blend': blend_mode
        }
        self.current_filter = 'custom'
        self.transition_active = False
        logger.debug(f"Applied custom filter: {color} @ {alpha} alpha")
    
    def transition_to(self, target_filter: str, duration: float):
        """
        Smoothly transition to a new filter
        
        Args:
            target_filter: Name of the target preset filter
            duration: Transition duration in seconds
        """
        if target_filter not in self.PRESETS:
            logger.warning(f"Cannot transition to unknown filter: {target_filter}")
            return
        
        self.transition_from = self.current_filter
        self.transition_to = target_filter
        self.transition_duration = duration
        self.transition_progress = 0.0
        self.transition_active = True
        logger.info(f"Starting filter transition: {self.transition_from} -> {target_filter} ({duration}s)")
    
    def update(self, dt: float):
        """
        Update filter transitions
        
        Args:
            dt: Delta time in seconds
        """
        if not self.transition_active:
            return
        
        self.transition_progress += dt
        
        if self.transition_progress >= self.transition_duration:
            # Transition complete
            self.current_filter = self.transition_to
            self.transition_active = False
            self.transition_progress = 0.0
            logger.debug(f"Filter transition complete: {self.current_filter}")
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Apply the current filter to a surface
        
        Args:
            surface: The pygame surface to apply the filter to
            
        Returns:
            The surface with filter applied (modifies in place and returns)
        """
        if self.transition_active:
            # Blend between two filters during transition
            progress = min(self.transition_progress / self.transition_duration, 1.0)
            filter_data = self._interpolate_filters(progress)
        elif self.custom_filter:
            filter_data = self.custom_filter
        else:
            filter_data = self.PRESETS[self.current_filter]
        
        # Don't apply if it's the 'none' filter
        if filter_data['alpha'] == 0:
            return surface
        
        # Create overlay surface
        overlay = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        overlay.fill((*filter_data['color'], filter_data['alpha']))
        
        # Apply overlay with blend mode
        surface.blit(overlay, (0, 0), special_flags=filter_data['blend'])
        
        return surface
    
    def _interpolate_filters(self, progress: float) -> dict:
        """
        Interpolate between two filters for smooth transitions
        
        Args:
            progress: Transition progress (0.0 to 1.0)
            
        Returns:
            Interpolated filter data dictionary
        """
        from_filter = self.PRESETS.get(self.transition_from, self.PRESETS['none'])
        to_filter = self.PRESETS[self.transition_to]
        
        # Interpolate color
        color = tuple(
            int(from_filter['color'][i] + (to_filter['color'][i] - from_filter['color'][i]) * progress)
            for i in range(3)
        )
        
        # Interpolate alpha
        alpha = int(from_filter['alpha'] + (to_filter['alpha'] - from_filter['alpha']) * progress)
        
        return {
            'color': color,
            'alpha': alpha,
            'blend': to_filter['blend']  # Use target blend mode
        }
    
    def get_current_filter(self) -> str:
        """Get the name of the current filter"""
        return self.current_filter
    
    def is_transitioning(self) -> bool:
        """Check if a filter transition is in progress"""
        return self.transition_active
    
    @staticmethod
    def list_presets() -> list:
        """Get a list of all available filter presets"""
        return list(ColorFilter.PRESETS.keys())
    
    @staticmethod
    def get_preset_info(preset_name: str) -> Optional[dict]:
        """Get information about a specific preset"""
        return ColorFilter.PRESETS.get(preset_name)


# Convenience function for quick filter application
def apply_filter(surface: pygame.Surface, preset_name: str) -> pygame.Surface:
    """
    Quick function to apply a filter to a surface
    
    Args:
        surface: Surface to apply filter to
        preset_name: Name of the preset filter
        
    Returns:
        The filtered surface
    """
    filter_system = ColorFilter(surface.get_size())
    filter_system.set_filter(preset_name)
    return filter_system.apply(surface)


# Global filter instance for shared use
_global_filter = None

def get_color_filter(surface_size: Tuple[int, int]) -> ColorFilter:
    """Get or create the global color filter instance"""
    global _global_filter
    if _global_filter is None or _global_filter.surface_size != surface_size:
        _global_filter = ColorFilter(surface_size)
    return _global_filter
