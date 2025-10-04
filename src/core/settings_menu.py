"""
Settings Menu for Pokemon Faiths
Simple settings overlay matching the game's dark atmospheric style
"""

import pygame
import json
import os
from constants import DEFAULT_SCREEN_WIDTH as SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT as SCREEN_HEIGHT
from .logger import get_logger
from .audio_manager import get_audio_manager

logger = get_logger('Settings')

SETTINGS_FILE = 'settings.json'

def load_settings_on_startup():
    """Load and apply settings on game startup"""
    audio_manager = get_audio_manager()

    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                music_volume = settings.get('music_volume', 70) / 100.0
                sfx_volume = settings.get('sfx_volume', 70) / 100.0

                audio_manager.set_music_volume(music_volume)
                audio_manager.set_sfx_volume(sfx_volume)

                logger.info(f"Loaded settings: Music={music_volume*100:.0f}%, SFX={sfx_volume*100:.0f}%")
        except Exception as e:
            logger.error(f"Failed to load settings on startup: {e}")

class SettingsMenu:
    """Settings menu with volume and display options"""

    def __init__(self):
        # Get audio manager
        self.audio_manager = get_audio_manager()

        # Settings state
        self.selected_index = 0
        self.options = [
            'Music Volume',
            'SFX Volume',
            'Fullscreen',
            'Back'
        ]

        # Load settings from file or use current values
        self._load_settings()

        # Apply loaded settings
        self.audio_manager.set_music_volume(self.music_volume / 100.0)
        self.audio_manager.set_sfx_volume(self.sfx_volume / 100.0)

        # Fonts
        self.title_font = pygame.font.SysFont("georgia", 64, bold=True)
        self.option_font = pygame.font.SysFont("georgia", 32)
        self.value_font = pygame.font.SysFont("georgia", 28)
        self.hint_font = pygame.font.SysFont("georgia", 20)

        # Colors (matching pause menu)
        self.bg_color = (15, 10, 20, 230)
        self.title_color = (220, 190, 160)
        self.normal_color = (140, 120, 100)
        self.selected_color = (255, 220, 180)
        self.border_color = (100, 80, 60)
        self.shadow_color = (5, 2, 8)

        # Menu dimensions
        self.menu_width = 600
        self.menu_height = 500
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2

        # Animation
        self.time = 0

        # Running state
        self.running = True
        self.result = None

    def _load_settings(self):
        """Load settings from file or use defaults"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    self.music_volume = settings.get('music_volume', 70)
                    self.sfx_volume = settings.get('sfx_volume', 70)
                    self.fullscreen = settings.get('fullscreen', True)
                    logger.info("Settings loaded from file")
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                self._set_default_settings()
        else:
            self._set_default_settings()

    def _set_default_settings(self):
        """Set default settings"""
        self.music_volume = 70
        self.sfx_volume = 70
        self.fullscreen = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN

    def _save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'music_volume': self.music_volume,
                'sfx_volume': self.sfx_volume,
                'fullscreen': self.fullscreen
            }
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info("Settings saved to file")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def handle_input(self, event):
        """Handle settings menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self._adjust_value(-1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self._adjust_value(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.options[self.selected_index] == 'Back':
                    self.running = False
                elif self.options[self.selected_index] == 'Fullscreen':
                    self._toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def _adjust_value(self, direction):
        """Adjust the selected setting value"""
        option = self.options[self.selected_index]

        if option == 'Music Volume':
            self.music_volume = max(0, min(100, self.music_volume + direction * 5))
            # Apply to audio manager (convert 0-100 to 0.0-1.0)
            self.audio_manager.set_music_volume(self.music_volume / 100.0)
            logger.info(f"Music volume: {self.music_volume}%")
        elif option == 'SFX Volume':
            self.sfx_volume = max(0, min(100, self.sfx_volume + direction * 5))
            # Apply to audio manager (convert 0-100 to 0.0-1.0)
            self.audio_manager.set_sfx_volume(self.sfx_volume / 100.0)
            logger.info(f"SFX volume: {self.sfx_volume}%")

            # Play a test sound effect to hear the change
            self.audio_manager.play_sfx('button_click')

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        screen = pygame.display.get_surface()

        if self.fullscreen:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            logger.info("Switched to fullscreen")
        else:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            logger.info("Switched to windowed mode")

    def update(self, dt):
        """Update animations"""
        self.time += dt

    def draw(self, screen):
        """Draw the settings menu"""
        import math

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Shadow
        shadow_offset = 8
        shadow_surface = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        shadow_surface.fill((*self.shadow_color, 150))
        screen.blit(shadow_surface, (self.menu_x + shadow_offset, self.menu_y + shadow_offset))

        # Menu background
        menu_surface = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        menu_surface.fill(self.bg_color)

        # Borders
        pygame.draw.rect(menu_surface, self.border_color, menu_surface.get_rect(), 4)
        inner_rect = pygame.Rect(6, 6, self.menu_width - 12, self.menu_height - 12)
        pygame.draw.rect(menu_surface, (30, 20, 35), inner_rect, 2)

        screen.blit(menu_surface, (self.menu_x, self.menu_y))

        # Title
        title_offset = math.sin(self.time * 2) * 2
        title_text = self.title_font.render("— SETTINGS —", True, self.title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, self.menu_y + 70 + title_offset))

        # Glow
        glow_text = self.title_font.render("— SETTINGS —", True, (255, 200, 150, 100))
        glow_rect = glow_text.get_rect(center=(title_rect.centerx, title_rect.centery + 2))
        screen.blit(glow_text, glow_rect)
        screen.blit(title_text, title_rect)

        # Decorative line
        line_y = self.menu_y + 120
        pygame.draw.line(screen, self.border_color,
                        (self.menu_x + 80, line_y),
                        (self.menu_x + self.menu_width - 80, line_y), 2)

        # Settings options
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_index else self.normal_color
            option_text = self.option_font.render(option, True, color)
            option_y = self.menu_y + 180 + i * 70
            option_rect = option_text.get_rect(midleft=(self.menu_x + 100, option_y))

            # Selection indicator
            if i == self.selected_index:
                pulse = math.sin(self.time * 4) * 3
                selection_rect = pygame.Rect(
                    option_rect.left - 20 - pulse,
                    option_rect.top - 8,
                    self.menu_width - 160 + pulse * 2,
                    option_rect.height + 16
                )
                pygame.draw.rect(screen, self.border_color, selection_rect, 2)

                # Arrow
                indicator_text = self.option_font.render("►", True, color)
                indicator_rect = indicator_text.get_rect(center=(option_rect.left - 40, option_rect.centery))
                screen.blit(indicator_text, indicator_rect)

            screen.blit(option_text, option_rect)

            # Draw value/control
            if option == 'Music Volume':
                value_text = f"{self.music_volume}%"
                self._draw_value_bar(screen, option_rect, self.music_volume, color)
            elif option == 'SFX Volume':
                value_text = f"{self.sfx_volume}%"
                self._draw_value_bar(screen, option_rect, self.sfx_volume, color)
            elif option == 'Fullscreen':
                value_text = "ON" if self.fullscreen else "OFF"
                value_render = self.value_font.render(value_text, True, color)
                value_rect = value_render.get_rect(midright=(self.menu_x + self.menu_width - 100, option_y))
                screen.blit(value_render, value_rect)

        # Decorative line
        line_y = self.menu_y + self.menu_height - 70
        pygame.draw.line(screen, self.border_color,
                        (self.menu_x + 80, line_y),
                        (self.menu_x + self.menu_width - 80, line_y), 2)

        # Controls hint
        hint_text = self.hint_font.render("↑↓ Navigate  •  ←→ Adjust  •  Enter/ESC Back", True, self.normal_color)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, self.menu_y + self.menu_height - 35))
        screen.blit(hint_text, hint_rect)

    def _draw_value_bar(self, screen, option_rect, value, color):
        """Draw volume bar"""
        bar_width = 150
        bar_height = 12
        bar_x = self.menu_x + self.menu_width - 100 - bar_width
        bar_y = option_rect.centery - bar_height // 2

        # Background bar
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 30, 35), bg_rect)
        pygame.draw.rect(screen, self.border_color, bg_rect, 2)

        # Fill bar
        fill_width = int((value / 100) * (bar_width - 4))
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x + 2, bar_y + 2, fill_width, bar_height - 4)
            pygame.draw.rect(screen, color, fill_rect)

        # Value text
        value_text = self.value_font.render(f"{value}%", True, color)
        value_rect = value_text.get_rect(midleft=(bar_x + bar_width + 15, bar_y + bar_height // 2))
        screen.blit(value_text, value_rect)

    def run(self, screen):
        """Run the settings menu"""
        clock = pygame.time.Clock()

        while self.running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_input(event)

            self.update(dt)
            self.draw(screen)
            pygame.display.flip()

        # Save settings when closing
        self._save_settings()

        return self.result
