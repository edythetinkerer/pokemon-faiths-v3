"""
Game Debugger for Pokemon Faiths
Provides debugging utilities for development
"""

import pygame
import os
from datetime import datetime

class GameDebugger:
    """Debug utilities for game development"""
    
    def __init__(self, clock=None):
        self.debug_font = pygame.font.SysFont("consolas", 16)
        self.debug_color = (0, 255, 0)  # Green debug text
        self.clock = clock  # Use provided clock for accurate FPS calculation
        self.sound_cache = {}  # Cache for loaded sounds
        
    def take_screenshot(self, surface, filename_prefix="screenshot"):
        """Take a screenshot of the given surface with error handling"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.png"
            
            # Create screenshots directory if it doesn't exist
            os.makedirs("screenshots", exist_ok=True)
            filepath = os.path.join("screenshots", filename)
            
            pygame.image.save(surface, filepath)
            print(f"Screenshot saved: {filepath}")
            return True
        except (OSError, pygame.error) as e:
            print(f"Failed to save screenshot: {e}")
            return False
        
    def log_game_state(self, player_rect, camera_offset, furniture_sprites, collision_rects):
        """Log current game state information"""
        print("\n=== GAME STATE DEBUG ===")
        print(f"Player Position: ({player_rect.x}, {player_rect.y})")
        print(f"Player Size: {player_rect.width}x{player_rect.height}")
        print(f"Camera Offset: ({camera_offset.x}, {camera_offset.y})")
        print(f"Furniture Count: {len(furniture_sprites)}")
        print(f"Collision Rects: {len(collision_rects)}")
        
        # Log furniture positions
        for i, sprite in enumerate(furniture_sprites):
            print(f"Furniture {i}: ({sprite.rect.x}, {sprite.rect.y}) - {sprite.rect.width}x{sprite.rect.height}")
        
        print("========================\n")
        
    def draw_debug_overlay(self, surface, player_rect, camera_offset, furniture_sprites, collision_rects):
        """Draw debug information overlay on the surface"""
        # Use provided clock for accurate FPS, fallback to 0 if none
        fps = self.clock.get_fps() if self.clock else 0.0
        
        debug_info = [
            f"Player: ({player_rect.x}, {player_rect.y})",
            f"Camera: ({camera_offset.x:.1f}, {camera_offset.y:.1f})",
            f"Furniture: {len(furniture_sprites)}",
            f"Collisions: {len(collision_rects)}",
            f"FPS: {fps:.1f}"
        ]
        
        # Draw debug text
        y_offset = 10
        for info in debug_info:
            text_surface = self.debug_font.render(info, True, self.debug_color)
            surface.blit(text_surface, (10, y_offset))
            y_offset += 20
            
    def draw_collision_debug(self, surface, collision_rects, camera_offset, color=(255, 0, 0)):
        """Draw collision rectangles for debugging"""
        for rect in collision_rects:
            # Convert to screen coordinates
            screen_rect = pygame.Rect(
                rect.x - camera_offset.x, 
                rect.y - camera_offset.y, 
                rect.width, 
                rect.height
            )
            pygame.draw.rect(surface, color, screen_rect, 2)
            
    def draw_sprite_bounds(self, surface, sprites, camera_offset, color=(255, 255, 0)):
        """Draw sprite boundaries for debugging"""
        for sprite in sprites:
            screen_rect = pygame.Rect(
                sprite.rect.x - camera_offset.x,
                sprite.rect.y - camera_offset.y,
                sprite.rect.width,
                sprite.rect.height
            )
            pygame.draw.rect(surface, color, screen_rect, 3)
