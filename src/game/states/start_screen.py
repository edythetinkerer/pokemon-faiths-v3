#!/usr/bin/env python3
"""
Pokémon Faiths - Cinematic Start Screen
A complete from-scratch rebuild focusing on a hyper-realistic, atmospheric candle
and dynamic lighting effects.

Features:
- Procedurally generated candle body and wax drips for organic look.
- Multi-layered, physics-based flame with realistic flickering and swaying.
- Dynamic soft glow that illuminates the scene realistically.
- Particle system for subtle smoke wisps.
- Heat haze distortion effect above the flame.
- Text that is dynamically lit by the candle's flicker.
- Enhanced cinematic vignette and overall atmosphere.
"""

import pygame
import sys
import math
import random
import opensimplex
from datetime import datetime
from constants import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, FPS, Colors
from ui.ui_components import Button, GradientBackground, VignetteEffect
from core.logger import get_logger
from core.save_manager import get_save_manager

logger = get_logger('StartScreen')

class Particle:
    """A class for managing smoke particles and embers."""
    def __init__(self, x, y, base_radius, lifetime, color):
        self.x = x
        self.y = y
        self.start_x = x
        self.base_radius = base_radius
        self.lifetime = lifetime
        self.life = lifetime
        self.color = color
        self.velocity_y = -random.uniform(0.5, 1.2)
        # Perlin noise for subtle side-to-side drift
        self.noise_offset = random.uniform(0, 1000)

    def update(self, dt):
        """Update particle position, size, and lifetime."""
        self.life -= dt
        self.y += self.velocity_y * dt * 60  # Scale velocity by dt
        # Use Perlin noise to create a gentle, natural drift
        self.x = self.start_x + opensimplex.noise2(self.y * 0.01 + self.noise_offset, 0) * 15

    def draw(self, surface):
        """Draw the particle with fading alpha."""
        if self.life > 0:
            life_ratio = self.life / self.lifetime
            # Particle shrinks and fades over its lifetime
            radius = self.base_radius * life_ratio
            alpha = int(255 * life_ratio * 0.5) # Make smoke semi-transparent
            
            particle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*self.color, alpha), (radius, radius), radius)
            surface.blit(particle_surf, (self.x - radius, self.y - radius))

class SmokeSystem:
    """Manages the particle system for smoke effects."""
    def __init__(self, max_particles=75, removal_threshold=0.1):
        self.particles = []
        self.max_particles = max_particles
        self.removal_threshold = removal_threshold
        self.spawn_timer = 0
        self.smoke_color = (50, 50, 50)
    
    def update(self, dt, spawn_x, spawn_y):
        """Update particle system."""
        # Spawn new particles
        self.spawn_timer += dt
        if self.spawn_timer > 0.1:
            self.spawn_timer = 0
            self.particles.append(Particle(spawn_x, spawn_y, random.randint(2, 4), 5, self.smoke_color))
        
        # Limit particle count
        if len(self.particles) > self.max_particles:
            self.particles.sort(key=lambda p: p.life, reverse=True)
            excess = len(self.particles) - self.max_particles
            self.particles = self.particles[:-excess]
        
        # Update and remove dead particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= self.removal_threshold:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface)

class Candle:
    """Manages the candle body and wax drips."""
    def __init__(self, x, y, width, height, wax_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.wax_color = wax_color
        self.body_points = self._create_body()
        self.drips = self._create_drips()
        self.body_surface = None
        self.drip_surfaces = []
        self._precompute_surfaces()
    
    def _create_body(self):
        """Create candle body points."""
        points = []
        segments = 20
        for i in range(segments + 1):
            y = self.y - (self.height * (i / segments))
            x_offset = opensimplex.noise2(y * 0.05, 0) * 5
            x_left = self.x - self.width / 2 + x_offset
            x_right = self.x + self.width / 2 + x_offset
            if i == 0:
                points.insert(0, (x_right, y))
                points.append((x_left, y))
            else:
                points.insert(0, (x_right, y))
                points.append((x_left, y))
        return points
    
    def _create_drips(self):
        """Create wax drips."""
        drips = []
        for _ in range(5):
            drip_points = []
            start_x = self.x + random.uniform(-1, 1) * (self.width / 2)
            start_y = self.y - self.height + random.randint(5, 20)
            length = random.randint(20, 80)
            width = random.randint(4, 8)
            
            drip_points.append((start_x, start_y))
            for i in range(1, 20):
                y = start_y + (length / 20) * i
                x_offset = opensimplex.noise2(y * 0.1, 0) * (width * 0.5)
                drip_points.append((start_x + x_offset, y))
            drips.append(drip_points)
        return drips
    
    def _precompute_surfaces(self):
        """Pre-render candle surfaces."""
        # Body surface
        self.body_surface = pygame.Surface((1366, 768), pygame.SRCALPHA)
        pygame.draw.polygon(self.body_surface, self.wax_color, self.body_points)
        
        # Drip surfaces with shadows
        for drip in self.drips:
            drip_surf = pygame.Surface((1366, 768), pygame.SRCALPHA)
            shadow_color = (int(self.wax_color[0] * 0.6), 
                          int(self.wax_color[1] * 0.6), 
                          int(self.wax_color[2] * 0.6))
            shadow_points = [(x + 2, y + 2) for x, y in drip]
            pygame.draw.lines(drip_surf, shadow_color, False, shadow_points, width=max(2, int(drip[0][0] % 10)))
            pygame.draw.lines(drip_surf, self.wax_color, False, drip, width=max(2, int(drip[0][0] % 10)))
            self.drip_surfaces.append(drip_surf)
    
    def draw(self, surface):
        """Draw candle elements."""
        for drip_surf in self.drip_surfaces:
            surface.blit(drip_surf, (0, 0))
        surface.blit(self.body_surface, (0, 0))

class Flame:
    """Manages the flame effects and lighting with beat-based movement."""
    def __init__(self, x, y, colors, noise_cache):
        self.x = x
        self.y = y
        self.colors = colors
        self.noise_cache = noise_cache
        self.noise_index = 0
        
        # Beat-based movement
        self.beat_time = 0
        self.beat_interval = 1.2  # Slower beat interval
        self.beat_phase = 0
        self.beat_amplitude = 8    # Reduced movement range
        self.beat_intensity = 0    # Current beat intensity
        self.current_intensity = 0 # For smooth transitions
        
        # Smooth transitions
        self.current_sway = 0
        self.target_sway = 0
        self.sway_speed = 0.2
    
    def update(self, time):
        """Update flame animation with smoother beat-based movement."""
        self.time = time
        
        # Natural flame movement (reduced amplitude)
        natural_sway = self.noise_cache[self.noise_index % len(self.noise_cache)] * 4
        self.noise_index += 1
        
        # Smoother beat-based movement
        self.beat_time += 0.016  # Assuming 60 FPS
        beat_progress = (self.beat_time % self.beat_interval) / self.beat_interval
        self.beat_phase = math.sin(beat_progress * math.pi * 2)
        
        # Smooth out the beat intensity
        target_intensity = abs(self.beat_phase) * 0.3
        intensity_diff = target_intensity - self.current_intensity
        self.current_intensity += intensity_diff * 0.1  # Smooth transition
        
        # Combine natural and beat-based movement
        beat_sway = self.beat_phase * self.beat_amplitude
        self.target_sway = natural_sway + beat_sway
        
        # Even smoother sway transition
        sway_diff = self.target_sway - self.current_sway
        self.current_sway += sway_diff * 0.1  # Slower transition
        
        # Update beat intensity for glow effect
        self.beat_intensity = self.current_intensity
        
        # Base flame flicker
        base_flicker = self.noise_cache[(self.noise_index + 10) % len(self.noise_cache)]
        fast_flicker = self.noise_cache[(self.noise_index + 20) % len(self.noise_cache)] * 0.3
        natural_flicker = (base_flicker + fast_flicker + 1) / 2
        
        # Combine natural flicker with beat intensity
        flicker = max(0.1, min(1.0, natural_flicker + self.beat_intensity))
        
        # Color variations
        saturation_boost = 1.0 + self.beat_intensity + (self.noise_cache[(self.noise_index + 40) % len(self.noise_cache)] * 0.1)
        
        return self.current_sway, flicker, saturation_boost
    
    def draw(self, surface, sway, flicker, saturation_boost):
        """Draw flame and glow effects."""
        flame_height = 120 + 40 * flicker
        flame_width = 80 + 20 * flicker
        
        # Keep flame base at candle position, only top sways
        flame_base_x = self.x
        flame_top_x = self.x + sway
        
        # Enhanced light scattering
        glow_radius = 300 + 100 * flicker
        glow_alpha = 40 + 30 * flicker
        
        for i in range(3):
            layer_radius = glow_radius - (i * 50)
            layer_alpha = int(glow_alpha * (1 - i * 0.3))
            if layer_radius > 0 and layer_alpha > 0:
                glow_surf = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
                glow_color = self.colors[1]
                if i == 0:
                    glow_color = (max(0, min(255, int(glow_color[0] * saturation_boost))), 
                                max(0, min(255, int(glow_color[1] * saturation_boost))), 
                                max(0, min(255, int(glow_color[2] * saturation_boost))))
                pygame.draw.circle(glow_surf, (*glow_color, max(0, min(255, layer_alpha))), (layer_radius, layer_radius), layer_radius)
                surface.blit(glow_surf, (flame_top_x - layer_radius, self.y - flame_height/2 - layer_radius))
        
        # Flame layers
        flame_layers = [
            (flame_width * 1.5, flame_height * 1.2, self.colors[2], 150),
            (flame_width, flame_height, self.colors[1], 200),
            (flame_width * 0.5, flame_height * 0.7, self.colors[0], 255),
        ]
        
        for w, h, color, alpha in flame_layers:
            flame_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            enhanced_color = (
                max(0, min(255, int(color[0] * saturation_boost))),
                max(0, min(255, int(color[1] * saturation_boost))),
                max(0, min(255, int(color[2] * saturation_boost)))
            )
            pygame.draw.ellipse(flame_surf, (*enhanced_color, max(0, min(255, int(alpha * flicker)))), (0, 0, w, h))
            # Calculate x position based on height (more sway at top of flame)
            height_ratio = (self.y - h - self.y) / flame_height  # 0 at bottom, 1 at top
            current_x = flame_base_x + (flame_top_x - flame_base_x) * height_ratio
            surface.blit(flame_surf, (current_x - w/2, self.y - h))
        
        return flicker

class TextUI:
    """Manages text rendering and lighting effects."""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.logo_font = pygame.font.SysFont("georgia", 100, bold=True)
        self.text_font = pygame.font.SysFont("georgia", 38)
        self.copyright_font = pygame.font.SysFont("arial", 22)
        self.text_color = (200, 170, 140)      # Slightly darker text
        self.dark_text_color = (100, 80, 60)  # Darker secondary text
    
    def draw(self, surface, flicker_intensity, time):
        """Draw all text elements with dynamic lighting."""
        base_brightness = 0.7
        flicker_boost = 0.4 * flicker_intensity
        brightness = base_brightness + flicker_boost
        
        lit_text_color = (
            max(0, min(255, int(self.text_color[0] * brightness))),
            max(0, min(255, int(self.text_color[1] * brightness))),
            max(0, min(255, int(self.text_color[2] * brightness)))
        )
        
        # Logo
        logo_text = self.logo_font.render("POKÉMON FAITHS", True, lit_text_color)
        logo_rect = logo_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        surface.blit(logo_text, logo_rect)
        
        # Press any key text
        fade_alpha = (math.sin(time * 1.5) + 1) / 2 * 255
        start_text_surf = self.text_font.render("Press Any Key to Start", True, self.dark_text_color)
        start_text_surf.set_alpha(fade_alpha)
        start_text_rect = start_text_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 200))
        surface.blit(start_text_surf, start_text_rect)
        
        # Copyright
        copyright_surf = self.copyright_font.render(f"© {datetime.now().year} EdySoft. All Rights Reserved.", True, (100, 90, 80))
        copyright_rect = copyright_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        surface.blit(copyright_surf, copyright_rect)

# Button class now imported from ui_components

class PokemonStartScreen:
    """Manages the entire cinematic start screen experience."""
    def __init__(self):
        pygame.init()
        
        # Initialize audio
        from core.audio_manager import get_audio_manager
        self.audio = get_audio_manager()
        self.audio.play_music('menu')  # Start the menu theme
        
        # Check for save file
        self.save_manager = get_save_manager()
        self.has_save = self.save_manager.save_exists()
        logger.info(f"Save file exists: {self.has_save}")

        # Screen settings
        self.SCREEN_WIDTH = DEFAULT_SCREEN_WIDTH
        self.SCREEN_HEIGHT = DEFAULT_SCREEN_HEIGHT
        self.FPS = FPS
        
        # Font settings
        self.title_font = pygame.font.SysFont("georgia", 100, bold=True)
        self.press_enter_font = pygame.font.SysFont("georgia", 38, bold=True)  # Smaller font for "Press Enter"
        self.title_color = (200, 170, 140)
        self.press_enter_color = (150, 140, 130)  # Different shade for better contrast
        # CRASH FIX 1: Use pygame.FULLSCREEN for better compatibility and to avoid
        # potential issues with window positioning that can lead to crashes.
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Pokémon Faiths - Cinematic")
        self.clock = pygame.time.Clock()
        self.running = True

        # Timers for animations, using pygame's time functions is more reliable
        self.time = 0
        
        # Colors - Use centralized theme
        self.BACKGROUND_COLOR_TOP = Colors.BACKGROUND_TOP
        self.BACKGROUND_COLOR_BOTTOM = Colors.BACKGROUND_BOTTOM
        self.CANDLE_WAX_COLOR = Colors.CANDLE_WAX
        self.WICK_COLOR = Colors.CANDLE_WICK
        self.FLAME_COLORS = [
            Colors.FLAME_CORE,  # Core
            Colors.FLAME_MID,   # Mid
            Colors.FLAME_OUTER, # Outer
        ]
        
        # Candle properties - Much larger to fill screen
        self.candle_x = self.SCREEN_WIDTH // 2
        self.candle_y = self.SCREEN_HEIGHT // 2 + 800  # Position so flame is in middle of screen
        self.candle_width = 300  # Much wider
        self.candle_height = 800  # Much taller
        
        # Precomputed noise arrays for performance
        self.noise_cache = []
        self.noise_cache_size = 100
        self._precompute_noise()
        
        # Initialize modular components
        self.candle = Candle(self.candle_x, self.candle_y, self.candle_width, self.candle_height, self.CANDLE_WAX_COLOR)
        self.flame = Flame(self.candle_x, self.candle_y - self.candle_height - 12, self.FLAME_COLORS, self.noise_cache)
        self.smoke_system = SmokeSystem(max_particles=75, removal_threshold=0.1)
        self.text_ui = TextUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Pre-rendered surfaces for optimization
        self.background = GradientBackground(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 
                                           self.BACKGROUND_COLOR_TOP, self.BACKGROUND_COLOR_BOTTOM)
        self.vignette = VignetteEffect(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.blur_surface = None
        self.blur_alpha = 0
        self.show_menu = False
        
        # Create menu buttons
        button_width = 300
        button_height = 60
        start_y = self.SCREEN_HEIGHT // 2 - 50
        spacing = 80
        
        self.buttons = {
            'new_game': Button(
                self.SCREEN_WIDTH // 2 - button_width // 2,
                start_y,
                button_width,
                button_height,
                "New Game"
            ),
            'continue': Button(
                self.SCREEN_WIDTH // 2 - button_width // 2,
                start_y + spacing,
                button_width,
                button_height,
                "Continue"
            ),
            'settings': Button(
                self.SCREEN_WIDTH // 2 - button_width // 2,
                start_y + spacing * 2,
                button_width,
                button_height,
                "Settings"
            )
        }
        
        # Transition effects
        self.fade_alpha = 255
        self.fade_speed = 2.0
        self.is_fading_out = False
        
        # Keyboard navigation
        self.button_names = ['new_game', 'continue', 'settings']
        self.selected_button_index = 0


    # Vignette creation now handled by VignetteEffect class
    
    # Dynamic vignette creation now handled by VignetteEffect class
    
    def _precompute_noise(self):
        """Precompute noise values to reduce per-frame calculations."""
        for i in range(self.noise_cache_size):
            self.noise_cache.append(opensimplex.noise2(i * 0.1, 0))
    
    def _precompute_candle_elements(self):
        """Pre-render static candle elements for performance."""
        # Create candle body surface
        self.candle_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(self.candle_surface, self.CANDLE_WAX_COLOR, self.candle_body_points)
        
        # Create wax drip surfaces with depth effects
        for drip in self.wax_drips:
            drip_surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            # Draw shadow first (darker, offset)
            shadow_color = (int(self.CANDLE_WAX_COLOR[0] * 0.6), 
                          int(self.CANDLE_WAX_COLOR[1] * 0.6), 
                          int(self.CANDLE_WAX_COLOR[2] * 0.6))
            shadow_points = [(x + 2, y + 2) for x, y in drip]
            pygame.draw.lines(drip_surf, shadow_color, False, shadow_points, width=max(2, int(drip[0][0] % 10)))
            # Draw main drip
            pygame.draw.lines(drip_surf, self.CANDLE_WAX_COLOR, False, drip, width=max(2, int(drip[0][0] % 10)))
            self.wax_drip_surfaces.append(drip_surf)

    def create_blur_surface(self):
        """Creates a semi-transparent overlay for blur effect."""
        blur = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        blur.fill((0, 0, 0, 100))  # Semi-transparent black for soft blur
        return blur
    
    def _draw_disabled_button(self, button):
        """Draw a disabled (grayed out) button."""
        # Draw dark, desaturated button
        disabled_color = (60, 50, 40)  # Dark gray-brown
        disabled_text_color = (100, 90, 80)  # Lighter gray
        
        pygame.draw.rect(self.screen, disabled_color, button.rect, border_radius=10)
        
        # Draw text with "No Save" indicator
        text_surface = button.font.render(button.text, True, disabled_text_color)
        text_rect = text_surface.get_rect(center=button.rect.center)
        self.screen.blit(text_surface, text_rect)
        
        # Add small "No Save" text
        small_font = pygame.font.SysFont("georgia", 20)
        no_save_text = small_font.render("(No Save)", True, (80, 70, 60))
        no_save_rect = no_save_text.get_rect(center=(button.rect.centerx, button.rect.bottom + 15))
        self.screen.blit(no_save_text, no_save_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            
            # Show menu only on Enter key
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and not self.show_menu:
                self.show_menu = True
                # Menu activated
                self.audio.play_sfx('button_click')
                # Create blur overlay
                self.blur_surface = self.create_blur_surface()
            
            # Handle button events when menu is shown
            elif self.show_menu:
                # Handle keyboard navigation
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        # Skip disabled buttons
                        original_index = self.selected_button_index
                        for _ in range(len(self.button_names)):
                            self.selected_button_index = (self.selected_button_index - 1) % len(self.button_names)
                            button_name = self.button_names[self.selected_button_index]
                            if not (button_name == 'continue' and not self.has_save):
                                break
                        if self.selected_button_index != original_index:
                            self.audio.play_sfx('button_click')
                    elif event.key == pygame.K_DOWN:
                        # Skip disabled buttons
                        original_index = self.selected_button_index
                        for _ in range(len(self.button_names)):
                            self.selected_button_index = (self.selected_button_index + 1) % len(self.button_names)
                            button_name = self.button_names[self.selected_button_index]
                            if not (button_name == 'continue' and not self.has_save):
                                break
                        if self.selected_button_index != original_index:
                            self.audio.play_sfx('button_click')
                    elif event.key == pygame.K_RETURN:
                        # Select the currently highlighted button
                        button_name = self.button_names[self.selected_button_index]
                        
                        # Don't allow activating Continue if no save
                        if button_name == 'continue' and not self.has_save:
                            logger.warning("Cannot continue: no save file exists")
                            return
                        
                        self.audio.play_sfx('button_click')
                        if button_name == 'settings':
                            from settings_menu import SettingsMenu
                            settings = SettingsMenu()
                            settings.run()
                            # Don't exit the start screen, just return to it
                            return
                        elif button_name == 'new_game':
                            self.menu_selection = button_name
                            self.running = False
                            return
                        elif button_name == 'continue':
                            self.menu_selection = button_name
                            self.running = False
                            return
                
                # Handle mouse events for buttons
                for button_name, button in self.buttons.items():
                    # Skip if Continue button and no save
                    if button_name == 'continue' and not self.has_save:
                        continue
                    
                    if button.handle_event(event):
                        self.audio.play_sfx('button_click')
                        if button_name == 'settings':
                            from settings_menu import SettingsMenu
                            settings = SettingsMenu()
                            settings.run()
                            # Don't exit the start screen, just return to it
                            return
                        elif button_name == 'new_game':
                            self.menu_selection = button_name
                            self.running = False
                            return
                        elif button_name == 'continue':
                            self.menu_selection = button_name
                            self.running = False
                            return

    def update(self, dt):
        """Update all animated elements."""
        self.time += dt
        
        # Fade-out logic removed - buttons now handle their own exit
        
        # Update modular components
        wick_tip_y = self.candle_y - self.candle_height - 12
        self.smoke_system.update(dt, self.candle_x, wick_tip_y)
        self.flame.update(self.time)

    def draw_background(self):
        """Draws the pre-rendered gradient background."""
        self.background.draw(self.screen)
        
    def draw_candle_and_flame(self):
        """Draws the hyper-realistic candle, wick, flame, and lighting."""
        # Draw candle using modular class
        self.candle.draw(self.screen)

        # Draw a shimmering melted wax pool at the top - larger for bigger candle
        pool_rect = pygame.Rect(self.candle_x - 60, self.candle_y - self.candle_height - 15, 120, 30)
        shimmer = (math.sin(self.time * 2) + 1) / 2
        pool_color = (
            min(255, self.CANDLE_WAX_COLOR[0] + 20 + 10 * shimmer),
            min(255, self.CANDLE_WAX_COLOR[1] + 15 + 10 * shimmer),
            min(255, self.CANDLE_WAX_COLOR[2] + 10 + 10 * shimmer)
        )
        pygame.draw.ellipse(self.screen, pool_color, pool_rect)

        # Wick - larger for bigger candle
        wick_rect = pygame.Rect(self.candle_x - 3, self.candle_y - self.candle_height - 30, 6, 30)
        pygame.draw.rect(self.screen, self.WICK_COLOR, wick_rect)

        # Draw flame using modular class
        sway, flicker, saturation_boost = self.flame.update(self.time)
        flicker = self.flame.draw(self.screen, sway, flicker, saturation_boost)
            
        return flicker # Return flicker value for text illumination

    def draw_text(self, flicker_intensity):
        """Draws all text elements, dynamically lit by the candle."""
        # Use modular text UI class
        self.text_ui.draw(self.screen, flicker_intensity, self.time)
        
    def draw_heat_haze(self):
        """Creates a subtle distortion effect above the flame."""
        haze_height = 80
        haze_width = 150
        wick_tip_y = self.candle_y - self.candle_height - 12
        haze_area = pygame.Rect(self.candle_x - haze_width//2, wick_tip_y - haze_height - 50, haze_width, haze_height)
        
        # CRASH FIX 2: The call to subsurface can crash if the calculated rect is
        # even partially outside the screen area. We clamp it to the screen's
        # rectangle first to make it safe.
        safe_haze_area = haze_area.clamp(self.screen.get_rect())

        # Only proceed if the clamped area is valid (has a non-zero size).
        if safe_haze_area.width > 0 and safe_haze_area.height > 0:
            # Capture the screen area behind the haze
            sub_surface = self.screen.subsurface(safe_haze_area).copy()
            
            # Calculate new height for the distortion effect, ensuring it's positive
            new_height = safe_haze_area.height + int(math.sin(self.time*5)*5)
            if new_height <= 0:
                return # Avoids a crash from scaling to a zero or negative size

            # Create a distorted version
            distorted_surf = pygame.transform.scale(sub_surface, (safe_haze_area.width, new_height))
            distorted_surf.set_alpha(100) # Make it subtle
            
            # Blit the distortion effect
            self.screen.blit(distorted_surf, (safe_haze_area.x, safe_haze_area.y - int(math.sin(self.time*5)*2.5)))

    def render(self):
        """The main rendering pipeline."""
        # Draw base scene
        self.draw_background()
        flicker = self.draw_candle_and_flame()
        self.smoke_system.draw(self.screen)
        self.draw_heat_haze()
        
        # Get beat phase from flame for synchronized animation
        beat_phase = self.flame.beat_phase if hasattr(self.flame, 'beat_phase') else math.sin(self.time * 2)
        beat_intensity = abs(beat_phase) * 0.3  # 30% intensity variation
        
        # Draw animated title with smoother movement
        title_y_offset = math.sin(self.time * 0.8) * 3  # Even slower floating
        title_scale = 1.0 + beat_intensity * 0.03  # More subtle pulse with beat
        
        # Create single title text with glow
        title_text = self.title_font.render("POKÉMON FAITHS", True, self.title_color)
        scaled_width = int(title_text.get_width() * title_scale)
        scaled_height = int(title_text.get_height() * title_scale)
        scaled_text = pygame.transform.scale(title_text, (scaled_width, scaled_height))
        
        # Position and draw the text
        title_rect = scaled_text.get_rect(center=(self.SCREEN_WIDTH // 2, 150 + title_y_offset))
        self.screen.blit(scaled_text, title_rect)
        
        # Draw "Press Enter" text with fade effect
        if not self.show_menu:
            press_text = "Press Enter to Start"
            # Combine slow fade with beat pulse
            base_alpha = abs(math.sin(self.time * 1.5))  # Slower fade
            beat_alpha = 0.7 + beat_intensity * 0.3  # Subtle beat influence
            text_alpha = int(base_alpha * beat_alpha * 255)
            
            text_surface = self.press_enter_font.render(press_text, True, self.press_enter_color)
            text_surface.set_alpha(text_alpha)
            text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 150))
            self.screen.blit(text_surface, text_rect)
        
        # Apply dynamic vignette
        dynamic_vignette = self.vignette.create_dynamic_vignette(self.time)
        self.screen.blit(dynamic_vignette, (0, 0))
        
        # If menu is shown, apply blur and draw buttons
        if self.show_menu:
            # Apply blur effect
            if self.blur_surface:
                self.screen.blit(self.blur_surface, (0, 0))
            
            # Draw menu buttons with proper keyboard/mouse interaction
            for i, (button_name, button) in enumerate(self.buttons.items()):
                # Disable Continue button if no save exists
                is_disabled = (button_name == 'continue' and not self.has_save)
                
                # Check if mouse is currently over any button
                mouse_pos = pygame.mouse.get_pos()
                mouse_over_button = button.rect.collidepoint(mouse_pos) and not is_disabled
                
                # Priority: Mouse hover overrides keyboard selection
                if mouse_over_button:
                    button.is_hovered = True
                    # Update keyboard selection to match mouse position
                    self.selected_button_index = i
                elif i == self.selected_button_index and not any(
                    self.buttons[name].rect.collidepoint(mouse_pos) 
                    for name in self.buttons
                ) and not is_disabled:
                    # Only use keyboard selection if mouse isn't over any button and not disabled
                    button.is_hovered = True
                else:
                    button.is_hovered = False
                
                # Draw button differently if disabled
                if is_disabled:
                    self._draw_disabled_button(button)
                else:
                    button.draw(self.screen, self.time)
        
        # Apply fade effect if transitioning
        if self.is_fading_out:
            fade_surf = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_alpha = max(0, min(255, int(255 - self.fade_alpha)))
            fade_surf.fill((0, 0, 0, fade_alpha))
            self.screen.blit(fade_surf, (0, 0))

        pygame.display.flip()

    def run(self):
        """Main application loop."""
        logger.info("Starting Pokémon Faiths start screen...")
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
        
        # Return None if user quit, or the menu selection if they chose an option
        result = getattr(self, 'menu_selection', None)
        logger.info(f"Start screen exited with selection: {result}")
        return result

if __name__ == "__main__":
    try:
        # The opensimplex library is required for this version.
        # You can install it with: pip install opensimplex
        start_screen = PokemonStartScreen()
        start_screen.run()
    except ImportError:
        print("Error: The 'opensimplex' library is required.")
        print("Please install it by running: pip install opensimplex")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        pygame.quit()
        sys.exit(1)