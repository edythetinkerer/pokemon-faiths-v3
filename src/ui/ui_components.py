"""
Shared UI Components for Pokemon Faiths
Eliminates code duplication across different game states
"""

import pygame
import math
from constants import Colors

class Button:
    """Reusable button component with hover effects and animations"""
    
    # Class constants for magic numbers
    EXPAND_WIDTH = 20
    EXPAND_HEIGHT = 10
    GLOW_OFFSET = 10
    GLOW_BASE_ALPHA = 100
    
    def __init__(self, x, y, width, height, text, font_size=40):
        if width <= 0 or height <= 0:
            raise ValueError("Button width and height must be positive")
        if not text:
            raise ValueError("Button text cannot be empty")
            
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.font = pygame.font.SysFont("georgia", font_size, bold=True)
        self.is_hovered = False
        
        # Use centralized colors
        self.normal_color = Colors.BUTTON_NORMAL
        self.hover_color = Colors.BUTTON_HOVER
        self.text_color = Colors.BUTTON_TEXT_NORMAL
        self.hover_text_color = Colors.BUTTON_TEXT_HOVER
        
    def draw(self, surface, time):
        """Draw button with hover effects and animations"""
        # Button background with enhanced hover effects
        if self.is_hovered:
            # Pulse effect for glow intensity
            pulse = (math.sin(time * 3) + 1) / 2  # Slightly faster pulse
            color = self.hover_color
            text_color = self.hover_text_color
            
            # Grow effect
            expanded_rect = self.rect.inflate(self.EXPAND_WIDTH, self.EXPAND_HEIGHT)
            
            # Draw outer glow first (larger, more transparent)
            outer_glow_surf = pygame.Surface((expanded_rect.width + self.GLOW_OFFSET * 4, 
                                           expanded_rect.height + self.GLOW_OFFSET * 4), pygame.SRCALPHA)
            outer_glow_alpha = int(50 * pulse)  # Subtle outer glow
            pygame.draw.rect(outer_glow_surf, (*color, outer_glow_alpha), outer_glow_surf.get_rect(), border_radius=20)
            surface.blit(outer_glow_surf, (expanded_rect.x - self.GLOW_OFFSET * 2, expanded_rect.y - self.GLOW_OFFSET * 2))
            
            # Draw main button
            pygame.draw.rect(surface, color, expanded_rect, border_radius=10)
            
            # Add bright border
            border_color = (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40))
            pygame.draw.rect(surface, border_color, expanded_rect, width=2, border_radius=10)
            
            # Inner glow effect
            inner_glow_surf = pygame.Surface((expanded_rect.width + self.GLOW_OFFSET * 2, 
                                           expanded_rect.height + self.GLOW_OFFSET * 2), pygame.SRCALPHA)
            inner_glow_alpha = int(self.GLOW_BASE_ALPHA * pulse)
            pygame.draw.rect(inner_glow_surf, (*color, inner_glow_alpha), inner_glow_surf.get_rect(), border_radius=15)
            surface.blit(inner_glow_surf, (expanded_rect.x - self.GLOW_OFFSET, expanded_rect.y - self.GLOW_OFFSET))
        else:
            color = self.normal_color
            text_color = self.text_color
            # Draw normal button with subtle border
            pygame.draw.rect(surface, color, self.rect, border_radius=10)
            # Add subtle border for normal state
            border_color = (color[0] + 20, color[1] + 20, color[2] + 20)
            pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=10)
        
        # Text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events for button interaction"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Only register click if mouse is actually over the button
            # This prevents "void clicks" from activating keyboard-highlighted buttons
            if self.rect.collidepoint(event.pos):
                return True
        return False

class GradientBackground:
    """Pre-rendered gradient background to improve performance"""
    
    def __init__(self, width, height, top_color=None, bottom_color=None):
        self.width = width
        self.height = height
        self.top_color = top_color or Colors.BACKGROUND_TOP
        self.bottom_color = bottom_color or Colors.BACKGROUND_BOTTOM
        self.surface = self._create_gradient()
    
    def _create_gradient(self):
        """Pre-render the gradient surface"""
        surface = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            ratio = y / self.height
            r = int(self.top_color[0] * (1 - ratio) + self.bottom_color[0] * ratio)
            g = int(self.top_color[1] * (1 - ratio) + self.bottom_color[1] * ratio)
            b = int(self.top_color[2] * (1 - ratio) + self.bottom_color[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.width, y))
        return surface
    
    def draw(self, target_surface):
        """Draw the pre-rendered gradient"""
        target_surface.blit(self.surface, (0, 0))

class VignetteEffect:
    """Reusable vignette effect for atmospheric darkening"""
    
    def __init__(self, width, height, intensity=0.8):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        if not 0.0 <= intensity <= 1.0:
            raise ValueError("Intensity must be between 0.0 and 1.0")
            
        self.width = width
        self.height = height
        self.intensity = intensity
        self.surface = self._create_vignette()
        # Cache for dynamic vignette to avoid recreating every frame
        self._dynamic_cache = {}
        self._cache_max_size = 10
    
    def _create_vignette(self):
        """Create the vignette surface"""
        vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        center_x = self.width // 2
        center_y = self.height // 2
        max_radius = min(self.width, self.height) // 2
        
        for i in range(max_radius, 0, -2):
            alpha = int(255 * (1 - (i / max_radius))**2 * self.intensity)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (center_x, center_y), i)
        return vignette
    
    def draw(self, target_surface):
        """Draw the vignette effect"""
        target_surface.blit(self.surface, (0, 0))
    
    def create_dynamic_vignette(self, time, animation_intensity=5):
        """Create an animated vignette with caching to improve performance"""
        # Create cache key based on time (rounded to reduce cache misses)
        cache_key = round(time * 10) / 10  # Round to 0.1 second precision
        
        # Check cache first
        if cache_key in self._dynamic_cache:
            return self._dynamic_cache[cache_key]
        
        # Create new vignette
        vignette = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Subtle animation based on time
        animation_offset = math.sin(time * 0.5) * animation_intensity
        center_x = self.width // 2 + animation_offset
        center_y = self.height // 2 + animation_offset * 0.5
        max_radius = min(self.width, self.height) // 2
        
        for i in range(max_radius, 0, -2):
            alpha = int(255 * (1 - (i / max_radius))**2 * self.intensity)
            # Add subtle variation to vignette intensity
            alpha_variation = int(alpha * (0.9 + 0.1 * math.sin(time * 0.3)))
            pygame.draw.circle(vignette, (0, 0, 0, alpha_variation), (int(center_x), int(center_y)), i)
        
        # Cache the result (with size limit)
        if len(self._dynamic_cache) >= self._cache_max_size:
            # Remove oldest entry
            oldest_key = min(self._dynamic_cache.keys())
            del self._dynamic_cache[oldest_key]
        
        self._dynamic_cache[cache_key] = vignette
        return vignette
