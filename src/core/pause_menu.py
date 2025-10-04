"""
Reusable Pause Menu for Pokemon Faiths
Can be used from any game scene
"""

import pygame
from constants import DEFAULT_SCREEN_WIDTH as SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT as SCREEN_HEIGHT, Colors
from .logger import get_logger
from .save_manager import get_save_manager

logger = get_logger('PauseMenu')

class PauseMenu:
    """Standalone pause menu with dark atmospheric styling"""
    
    def __init__(self, save_data=None, scene_name="Game"):
        self.save_data = save_data
        self.save_manager = get_save_manager()
        self.scene_name = scene_name
        
        # Menu state
        self.selected_index = 0
        self.options = ['Resume', 'Save Game', 'Settings', 'Quit to Menu']
        
        # Fonts
        self.title_font = pygame.font.SysFont("georgia", 64, bold=True)
        self.option_font = pygame.font.SysFont("georgia", 36)
        self.hint_font = pygame.font.SysFont("georgia", 20)

        # Dark atmospheric colors
        self.bg_color = (15, 10, 20, 230)  # Very dark purple, almost opaque
        self.title_color = (220, 190, 160)  # Warm light
        self.normal_color = (140, 120, 100)  # Muted brown
        self.selected_color = (255, 220, 180)  # Bright warm highlight
        self.border_color = (100, 80, 60)  # Dark brown border
        self.shadow_color = (5, 2, 8)  # Deep shadow
        
        # Menu dimensions
        self.menu_width = 500
        self.menu_height = 450
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        
        # Animation
        self.time = 0
        
        # Result
        self.result = None  # 'resume', 'save', 'settings', 'quit'
    
    def handle_input(self, event):
        """Handle menu input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                return 'navigate'
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                return 'navigate'
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self._execute_selection()
            elif event.key == pygame.K_ESCAPE:
                self.result = 'resume'
                return 'resume'
        
        elif event.type == pygame.MOUSEMOTION:
            # Check if mouse is over any option
            mouse_pos = event.pos
            for i, option in enumerate(self.options):
                option_y = self.menu_y + 140 + i * 60
                option_rect = pygame.Rect(self.menu_x + 50, option_y - 20, self.menu_width - 100, 50)
                if option_rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    return 'navigate'
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on an option
            mouse_pos = event.pos
            for i, option in enumerate(self.options):
                option_y = self.menu_y + 140 + i * 60
                option_rect = pygame.Rect(self.menu_x + 50, option_y - 20, self.menu_width - 100, 50)
                if option_rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    return self._execute_selection()
        
        return None
    
    def _execute_selection(self):
        """Execute the selected menu option"""
        option = self.options[self.selected_index]
        
        if option == 'Resume':
            self.result = 'resume'
            return 'resume'
        elif option == 'Save Game':
            if self.save_data and self.save_manager:
                self.save_manager.save_game(self.save_data)
                logger.info("Game saved from pause menu")
            self.result = 'resume'  # Close menu after saving
            return 'resume'
        elif option == 'Settings':
            self.result = 'settings'
            return 'settings'
        elif option == 'Quit to Menu':
            self.result = 'quit'
            return 'quit'
    
    def update(self, dt):
        """Update menu animations"""
        self.time += dt
    
    def draw(self, screen):
        """Draw the pause menu overlay with atmospheric styling"""
        import math

        # Dark vignette overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Shadow for menu (gives depth)
        shadow_offset = 8
        shadow_surface = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        shadow_surface.fill((*self.shadow_color, 150))
        screen.blit(shadow_surface, (self.menu_x + shadow_offset, self.menu_y + shadow_offset))

        # Menu background box with texture
        menu_surface = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        menu_surface.fill(self.bg_color)

        # Inner border (inset effect)
        pygame.draw.rect(menu_surface, self.border_color, menu_surface.get_rect(), 4)
        inner_rect = pygame.Rect(6, 6, self.menu_width - 12, self.menu_height - 12)
        pygame.draw.rect(menu_surface, (30, 20, 35), inner_rect, 2)

        # Draw to screen
        screen.blit(menu_surface, (self.menu_x, self.menu_y))

        # Title with subtle glow effect
        title_offset = math.sin(self.time * 2) * 2
        title_text = self.title_font.render("— PAUSED —", True, self.title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.menu_y + 70 + title_offset))

        # Glow effect (shadow behind title)
        glow_text = self.title_font.render("— PAUSED —", True, (255, 200, 150, 100))
        glow_rect = glow_text.get_rect(center=(title_rect.centerx, title_rect.centery + 2))
        screen.blit(glow_text, glow_rect)
        screen.blit(title_text, title_rect)

        # Decorative line under title
        line_y = self.menu_y + 110
        pygame.draw.line(screen, self.border_color,
                        (self.menu_x + 80, line_y),
                        (self.menu_x + self.menu_width - 80, line_y), 2)

        # Menu options
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_index else self.normal_color
            option_text = self.option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, self.menu_y + 170 + i * 60))

            # Selection box for highlighted item
            if i == self.selected_index:
                # Pulsing selection box
                pulse = math.sin(self.time * 4) * 3
                selection_rect = pygame.Rect(
                    option_rect.left - 20 - pulse,
                    option_rect.top - 8,
                    option_rect.width + 40 + pulse * 2,
                    option_rect.height + 16
                )
                pygame.draw.rect(screen, self.border_color, selection_rect, 2)

                # Arrow indicator
                indicator_text = self.option_font.render("►", True, color)
                indicator_rect = indicator_text.get_rect(center=(option_rect.left - 40, option_rect.centery))
                screen.blit(indicator_text, indicator_rect)

            screen.blit(option_text, option_rect)

        # Decorative line above controls
        line_y = self.menu_y + self.menu_height - 70
        pygame.draw.line(screen, self.border_color,
                        (self.menu_x + 80, line_y),
                        (self.menu_x + self.menu_width - 80, line_y), 2)

        # Controls hint
        hint_text = self.hint_font.render("↑↓ Navigate  •  Enter Select  •  ESC Close", True, self.normal_color)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, self.menu_y + self.menu_height - 35))
        screen.blit(hint_text, hint_rect)
