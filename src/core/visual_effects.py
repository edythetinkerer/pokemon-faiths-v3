"""
Visual Effects System for Pokemon Faiths
Centralized filter and visual effect management
"""

import pygame
import random
from typing import Tuple, Optional

class VisualEffects:
    """Manages visual filters and effects"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        
        # Pre-rendered effects (created once for performance)
        self.vignette_cache = {}
        self.film_grain_cache = None
        
    def create_vignette(self, intensity: float = 0.5, color: Tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
        """
        Create a vignette overlay (darkened edges)
        
        Args:
            intensity: 0.0 (no vignette) to 1.0 (strong vignette)
            color: RGB color for the vignette
        
        Returns:
            Surface with vignette effect
        """
        # Check cache
        cache_key = (intensity, color)
        if cache_key in self.vignette_cache:
            return self.vignette_cache[cache_key]
        
        vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        center_x = self.width // 2
        center_y = self.height // 2
        max_radius = max(self.width, self.height) * 0.7
        
        # Create radial gradient
        for y in range(0, self.height, 2):  # Sample every 2 pixels for performance
            for x in range(0, self.width, 2):
                # Distance from center
                dx = x - center_x
                dy = y - center_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Calculate alpha based on distance
                normalized = min(distance / max_radius, 1.0)
                alpha = int(normalized ** 2 * 255 * intensity)  # Quadratic falloff
                
                # Draw 2x2 block for performance
                rect = pygame.Rect(x, y, 2, 2)
                pygame.draw.rect(vignette, (*color, alpha), rect)
        
        # Cache and return
        self.vignette_cache[cache_key] = vignette
        return vignette
    
    def create_film_grain(self, density: float = 0.01, intensity: int = 40) -> pygame.Surface:
        """
        Create ANIMATED film grain texture (generates new each time)
        
        Args:
            density: Percentage of pixels with grain (0.0 to 1.0)
            intensity: Brightness of grain pixels (0-255)
        
        Returns:
            Surface with film grain
        """
        # DON'T cache - create new grain each frame for animation
        grain = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        num_grains = int(self.width * self.height * density)
        
        for _ in range(num_grains):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # Random intensity variation
            grain_intensity = random.randint(intensity // 2, intensity)
            grain.set_at((x, y), (grain_intensity, grain_intensity, grain_intensity, 100))
        
        return grain
    
    def apply_color_tint(self, surface: pygame.Surface, color: Tuple[int, int, int], 
                        intensity: float = 0.3) -> None:
        """
        Apply a color tint overlay to a surface
        
        Args:
            surface: Surface to tint
            color: RGB color to tint with
            intensity: Strength of tint (0.0 to 1.0)
        """
        tint = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        alpha = int(255 * intensity)
        tint.fill((*color, alpha))
        surface.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    def apply_vignette(self, surface: pygame.Surface, intensity: float = 0.5) -> None:
        """Apply vignette to a surface"""
        vignette = self.create_vignette(intensity)
        surface.blit(vignette, (0, 0))
    
    def apply_film_grain(self, surface: pygame.Surface, density: float = 0.01) -> None:
        """Apply film grain to a surface"""
        grain = self.create_film_grain(density)
        grain.set_alpha(30)  # Subtle grain
        surface.blit(grain, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def darken_surface(self, surface: pygame.Surface, factor: float = 0.5) -> pygame.Surface:
        """
        Darken a surface by a factor
        
        Args:
            surface: Surface to darken
            factor: 0.0 (black) to 1.0 (original brightness)
        
        Returns:
            Darkened surface
        """
        darkened = surface.copy()
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha = int(255 * (1 - factor))
        overlay.fill((0, 0, 0, alpha))
        darkened.blit(overlay, (0, 0))
        return darkened
    
    def create_radial_light(self, radius: int, color: Tuple[int, int, int] = (255, 200, 100),
                           intensity: float = 1.0) -> pygame.Surface:
        """
        Create a radial light source (for player glow, etc.)
        
        Args:
            radius: Radius of the light
            color: RGB color of the light
            intensity: Brightness multiplier (0.0 to 1.0)
        
        Returns:
            Surface with radial light
        """
        light = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        for y in range(radius * 2):
            for x in range(radius * 2):
                # Distance from center
                dx = x - radius
                dy = y - radius
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < radius:
                    # Calculate alpha based on distance
                    normalized = distance / radius
                    alpha = int((1 - normalized ** 2) * 255 * intensity)
                    light.set_at((x, y), (*color, alpha))
        
        return light
    
    def clear_cache(self):
        """Clear cached effects (useful if resolution changes)"""
        self.vignette_cache.clear()
        self.film_grain_cache = None


class GlobalEffects:
    """Global effects for entire game (all scenes)"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.effects = VisualEffects(screen_width, screen_height)
        
        # Grain settings - PRE-GENERATE for smooth frame times
        self.grain_density = 0.008
        self.grain_intensity = 70
        self.grain_frame_skip = 3
        self.grain_frame_counter = 0
        
        # PRE-GENERATE 10 grain textures instead of creating each frame
        self.grain_textures = []
        for _ in range(10):
            grain = self.effects.create_film_grain(density=self.grain_density, intensity=self.grain_intensity)
            grain.set_alpha(40)
            self.grain_textures.append(grain)
        self.grain_index = 0
        
        # Dark fantasy color filter (pre-created)
        self.color_filter = self._create_dark_fantasy_filter(screen_width, screen_height)
    
    def _create_dark_fantasy_filter(self, width: int, height: int) -> pygame.Surface:
        """Create dark fantasy color overlay (Bloodborne-inspired purple-blue tint)"""
        filter_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Bloodborne-style purple-blue tint (balanced visibility and performance)
        tint_color = (60, 45, 85, 35)  # RGBA - visible purple tint
        filter_surf.fill(tint_color)
        
        return filter_surf
    
    def apply_film_grain(self, surface: pygame.Surface):
        """Apply animated film grain (cycles through pre-generated textures)"""
        self.grain_frame_counter += 1
        if self.grain_frame_counter >= self.grain_frame_skip:
            # Cycle to next grain texture
            self.grain_index = (self.grain_index + 1) % len(self.grain_textures)
            self.grain_frame_counter = 0
        
        # Blit current grain texture
        surface.blit(self.grain_textures[self.grain_index], (0, 0), special_flags=pygame.BLEND_ADD)
    
    def apply_dark_fantasy_filter(self, surface: pygame.Surface, intensity: float = 1.0):
        """Apply dark fantasy color grading (purple/blue tint)"""
        # Filter already has alpha built in, just blit it
        surface.blit(self.color_filter, (0, 0))
    
    def apply_full_effects(self, surface: pygame.Surface):
        """Apply both grain and color filter"""
        self.apply_dark_fantasy_filter(surface)
        self.apply_film_grain(surface)


class CaveEffects:
    """Preset effects for dark fantasy cave atmosphere"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.effects = VisualEffects(screen_width, screen_height)
        
        # Pre-create static effects at screen resolution
        self.cave_vignette = self.effects.create_vignette(intensity=0.4, color=(0, 0, 0))
        self.player_glow = self.effects.create_radial_light(radius=30, color=(120, 90, 60), intensity=0.8)
        
        # PRE-GENERATE grain textures for smooth performance
        self.grain_density = 0.003
        self.grain_intensity = 50
        self.grain_frame_skip = 3
        self.grain_frame_counter = 0
        
        # Pre-generate 10 grain textures
        self.grain_textures = []
        for _ in range(10):
            grain = self.effects.create_film_grain(density=self.grain_density, intensity=self.grain_intensity)
            grain.set_alpha(30)
            self.grain_textures.append(grain)
        self.grain_index = 0
    
    def apply_cave_atmosphere(self, surface: pygame.Surface):
        """Apply cave atmosphere with optimized animated grain"""
        # Apply vignette (static)
        self.cave_vignette.set_alpha(80)
        surface.blit(self.cave_vignette, (0, 0))
        
        # Update grain animation
        self.grain_frame_counter += 1
        if self.grain_frame_counter >= self.grain_frame_skip:
            self.grain_index = (self.grain_index + 1) % len(self.grain_textures)
            self.grain_frame_counter = 0
        
        # Apply pre-generated grain
        surface.blit(self.grain_textures[self.grain_index], (0, 0), special_flags=pygame.BLEND_ADD)
    
    def draw_player_glow(self, surface: pygame.Surface, player_pos: Tuple[int, int]):
        """Draw glow around player"""
        glow_pos = (player_pos[0] - 30, player_pos[1] - 30)
        self.player_glow.set_alpha(120)
        surface.blit(self.player_glow, glow_pos)


# Example usage for other scenes
class DarkFantasyEffects:
    """Preset effects for dark fantasy atmosphere"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.effects = VisualEffects(screen_width, screen_height)
    
    def apply_dark_fantasy_filter(self, surface: pygame.Surface):
        """Apply dark fantasy color grading"""
        # Purple-blue tint
        self.effects.apply_color_tint(surface, (30, 20, 60), intensity=0.15)
        # Light vignette
        self.effects.apply_vignette(surface, intensity=0.3)
        # Subtle grain
        self.effects.apply_film_grain(surface, density=0.005)
