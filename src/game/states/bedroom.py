"""
Bedroom Scene for Pokemon Faiths
Main gameplay scene with interaction system and teleportation
"""

import pygame
from constants import (
    DEFAULT_SCREEN_WIDTH as SCREEN_WIDTH, 
    DEFAULT_SCREEN_HEIGHT as SCREEN_HEIGHT,
    TILE_SIZE, GAME_WIDTH, GAME_HEIGHT,
    BORDER_THICKNESS,
    INTERACTION_RANGE_DEFAULT, INTERACTION_TEXT_AUTO_CLOSE_TIME, INTERACTION_PROMPT_Y_OFFSET
)
from core.asset_manager import get_asset_manager
from core.logger import get_logger
from core.save_manager import get_save_manager
from core.entities import Player, Camera
from core.game_debugger import GameDebugger
from core.pause_menu import PauseMenu
from core.visual_effects import GlobalEffects
from core.frame_smoother import FrameTimeSmoother

logger = get_logger('Bedroom')

class BedroomScene:
    """Main bedroom gameplay scene with interaction system"""
    
    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, save_data=None):
        # Core pygame setup
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Pokemon Faiths - Bedroom")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Save system
        self.save_manager = get_save_manager()
        self.save_data = save_data
        
        # Scene state
        self.paused = False
        self.debug_mode = False
        self.teleport_to_outside = False
        self.start_battle = False
        self.return_to_menu = False
        self.pause_menu = None
        
        # Interaction system
        self.interaction_mode = False
        self.interaction_text = ""
        self.interaction_timer = 0
        self.nearby_object = None
        self.show_e_prompt = False
        self.player_locked = False  # Lock player during interactions
        
        # Eye opening effect (only on first time)
        self.eye_opening = save_data is None or not save_data.get('progress', {}).get('bedroom_visited', False)
        self.eye_opening_timer = 0
        self.eye_opening_duration = 3000  # 3 seconds in milliseconds
        
        # Load assets and setup scene
        self._load_assets()
        self._setup_map()
        self._setup_player()
        
        # Initialize systems
        self.camera = Camera(self.player, GAME_WIDTH, GAME_HEIGHT)
        self.debugger = GameDebugger(self.clock)
        self.global_effects = GlobalEffects(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frame_smoother = FrameTimeSmoother(max_dt=0.05)
        
        logger.info("Bedroom scene initialized")

    def _load_assets(self):
        """Load bedroom-specific assets with proper error handling"""
        try:
            asset_manager = get_asset_manager()
            
            # Organize assets by type
            self.assets = {
                'floor': [],
                'wall': None,
                'rug_teleport': None,
                'bed': None,
                'table': None,
                'bookshelf': None,
                'chest': None,
                'calendar': None
            }
            
            # Load floor tiles
            for i in range(1, 4):
                tile_name = f'damaged_wood_tile{"" if i == 1 else i}.png'
                tile_path = f'assets/images/{tile_name}'
                scaled_tile = asset_manager.load_image(tile_path, (TILE_SIZE, TILE_SIZE))
                self.assets['floor'].append(scaled_tile)
            
            self.assets['wall'] = self.assets['floor'][0]
            self.assets['rug_teleport'] = asset_manager.load_image('assets/images/rug_tile.png', (TILE_SIZE, TILE_SIZE))
            
            # Load furniture with safe aspect ratio scaling
            def scale_with_aspect(path, target_width=None, target_height=None):
                """Safely scale image maintaining aspect ratio"""
                img = asset_manager.load_image(path)
                if img.get_width() == 32 and img.get_height() == 32:
                    # This is a placeholder, just return it
                    return img
                
                orig_w, orig_h = img.get_size()
                
                if target_width and not target_height:
                    aspect = orig_h / orig_w
                    new_size = (target_width, int(target_width * aspect))
                elif target_height and not target_width:
                    aspect = orig_w / orig_h
                    new_size = (int(target_height * aspect), target_height)
                else:
                    new_size = (target_width or orig_w, target_height or orig_h)
                
                return asset_manager.load_image(path, new_size)
            
            # Load furniture
            self.assets['bed'] = scale_with_aspect('assets/images/damaged_bed.png', target_width=50)
            self.assets['table'] = scale_with_aspect('assets/images/damaged_table.png', target_width=40)
            self.assets['bookshelf'] = scale_with_aspect('assets/images/damaged_bookshelf.png', target_height=50)
            self.assets['chest'] = scale_with_aspect('assets/images/wood_chest.png', target_width=35)
            self.assets['calendar'] = asset_manager.load_image('assets/images/calendar.png', (24, 20))
            
            logger.info("Bedroom assets loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load bedroom assets: {e}")
            self._create_placeholder_assets()

    def _create_placeholder_assets(self):
        """Create placeholder assets if loading fails"""
        placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE))
        placeholder.fill((255, 0, 255))  # Magenta placeholder
        
        self.assets = {
            'floor': [placeholder],
            'wall': placeholder,
            'rug_teleport': placeholder,
            'bed': placeholder,
            'table': placeholder,
            'bookshelf': placeholder,
            'chest': placeholder,
            'calendar': placeholder
        }
        logger.warning("Using placeholder assets due to loading failure")

    def _setup_map(self):
        """Setup bedroom layout with improved collision system"""
        self.map_width = 14  # Increased for better spacing
        self.map_height = 12
        
        self.collision_rects = []
        self.furniture_sprites = pygame.sprite.Group()
        
        # PROPER border collision - tight to walls
        border_thickness = 4
        
        # Top wall
        self.collision_rects.append(pygame.Rect(0, 0, self.map_width * TILE_SIZE, border_thickness))
        # Bottom wall  
        self.collision_rects.append(pygame.Rect(0, self.map_height * TILE_SIZE - border_thickness, 
                                               self.map_width * TILE_SIZE, border_thickness))
        # Left wall
        self.collision_rects.append(pygame.Rect(0, 0, border_thickness, self.map_height * TILE_SIZE))
        # Right wall
        self.collision_rects.append(pygame.Rect(self.map_width * TILE_SIZE - border_thickness, 0, 
                                               border_thickness, self.map_height * TILE_SIZE))
        
        # Setup furniture with better layout
        self._setup_furniture()
        
        # Teleport rug (centered at bottom, in front of doorway)
        self.rug_teleport_pos = (
            (self.map_width // 2) * TILE_SIZE - TILE_SIZE // 2,
            (self.map_height - 2) * TILE_SIZE
        )
        self.rug_teleport_rect = pygame.Rect(
            self.rug_teleport_pos[0], 
            self.rug_teleport_pos[1], 
            TILE_SIZE * 2,  # Wider rug
            TILE_SIZE
        )
        
        logger.debug(f"Improved bedroom map: {self.map_width}x{self.map_height}")

    def _setup_furniture(self):
        """Setup furniture with improved layout and precise collision boxes"""
        
        # BED - Top left corner against walls
        bed_sprite = pygame.sprite.Sprite()
        bed_sprite.image = self.assets['bed']
        bed_sprite.rect = bed_sprite.image.get_rect(topleft=(1.5 * TILE_SIZE, 1 * TILE_SIZE))
        bed_sprite.draw = lambda surface, camera: surface.blit(bed_sprite.image, bed_sprite.rect.topleft - camera.offset)
        self.furniture_sprites.add(bed_sprite)
        # Tight collision - only bed frame
        self.collision_rects.append(bed_sprite.rect.inflate(-12, -16))
        
        # TABLE - Left side, below bed
        table_sprite = pygame.sprite.Sprite()
        table_sprite.image = self.assets['table']
        table_sprite.rect = table_sprite.image.get_rect(topleft=(2 * TILE_SIZE, 5 * TILE_SIZE))
        table_sprite.draw = lambda surface, camera: surface.blit(table_sprite.image, table_sprite.rect.topleft - camera.offset)
        self.furniture_sprites.add(table_sprite)
        # Table collision - only solid parts
        self.collision_rects.append(pygame.Rect(
            table_sprite.rect.x + 5,
            table_sprite.rect.y + 10,
            table_sprite.rect.width - 10,
            table_sprite.rect.height - 15
        ))
        
        # CALENDAR - Wall mounted above table
        calendar_sprite = pygame.sprite.Sprite()
        calendar_sprite.image = self.assets['calendar']
        calendar_sprite.rect = calendar_sprite.image.get_rect(center=(
            table_sprite.rect.centerx,
            table_sprite.rect.top - 15
        ))
        calendar_sprite.draw = lambda surface, camera: surface.blit(calendar_sprite.image, calendar_sprite.rect.topleft - camera.offset)
        self.furniture_sprites.add(calendar_sprite)
        # No collision for wall-mounted items
        
        # BOOKSHELF - Right wall, top corner
        bookshelf_sprite = pygame.sprite.Sprite()
        bookshelf_sprite.image = self.assets['bookshelf']
        bookshelf_sprite.rect = bookshelf_sprite.image.get_rect(topleft=(
            (self.map_width - 3) * TILE_SIZE,
            1.5 * TILE_SIZE
        ))
        bookshelf_sprite.draw = lambda surface, camera: surface.blit(bookshelf_sprite.image, bookshelf_sprite.rect.topleft - camera.offset)
        self.furniture_sprites.add(bookshelf_sprite)
        # Bookshelf collision - leave room to walk behind
        self.collision_rects.append(pygame.Rect(
            bookshelf_sprite.rect.x + 8,
            bookshelf_sprite.rect.y + 5,
            bookshelf_sprite.rect.width - 16,
            bookshelf_sprite.rect.height - 10
        ))
        
        # CHEST - Right wall, bottom
        chest_sprite = pygame.sprite.Sprite()
        chest_sprite.image = self.assets['chest']
        chest_sprite.rect = chest_sprite.image.get_rect(topleft=(
            (self.map_width - 2.5) * TILE_SIZE,
            7 * TILE_SIZE
        ))
        chest_sprite.draw = lambda surface, camera: surface.blit(chest_sprite.image, chest_sprite.rect.topleft - camera.offset)
        self.furniture_sprites.add(chest_sprite)
        # Chest collision - only bottom half (lid can be walked "under")
        self.collision_rects.append(pygame.Rect(
            chest_sprite.rect.x + 4,
            chest_sprite.rect.centery,
            chest_sprite.rect.width - 8,
            chest_sprite.rect.height // 2
        ))
        
        # Interactive objects dictionary
        self.interactive_objects = {
            'bed': {
                'sprite': bed_sprite,
                'description': "A worn mattress on a creaking frame. You've had better sleep on cold ground.",
                'interaction_range': 45
            },
            'table': {
                'sprite': table_sprite,
                'description': "Scratches and stains tell stories of countless meals eaten alone.",
                'interaction_range': 40
            },
            'calendar': {
                'sprite': calendar_sprite,
                'description': "23 days marked with X's. Exile Day approaches. Your heart sinks.",
                'interaction_range': 35
            },
            'bookshelf': {
                'sprite': bookshelf_sprite,
                'description': "Old survival guides and medical texts. Knowledge bought with others' suffering.",
                'interaction_range': 40
            },
            'chest': {
                'sprite': chest_sprite,
                'description': "Locked tight. Something rattles inside when you shake it. The key is long gone.",
                'interaction_range': 40
            },
            'rug': {
                'sprite': None,
                'description': "The rug shimmers faintly. You feel drawn to step outside...",
                'interaction_range': 30
            }
        }

    def _setup_player(self):
        """Setup player with position from save data or default"""
        if self.save_data and 'progress' in self.save_data and 'bedroom_position' in self.save_data['progress']:
            pos = self.save_data['progress']['bedroom_position']
            logger.info(f"Loading player position from save: ({pos['x']}, {pos['y']})")
            self.player = Player(pos['x'], pos['y'])
        else:
            logger.info("Starting player at default position")
            spawn_x = 6 * TILE_SIZE  # Center of room
            spawn_y = 6 * TILE_SIZE  # Middle of room
            self.player = Player(spawn_x, spawn_y)

    def handle_events(self):
        """Handle bedroom-specific events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received")
                self._save_game()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.interaction_mode:
                        # Close interaction and unlock player
                        self.interaction_mode = False
                        self.interaction_text = ""
                        self.player_locked = False
                        continue
                    if self.paused:
                        self.paused = False
                        self.pause_menu = None
                        logger.info("Game unpaused")
                    else:
                        self.paused = True
                        self.pause_menu = PauseMenu(self.save_data, "Bedroom")
                        logger.info("Game paused - ESC detected")
                    continue  # Don't process this ESC event further
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.toggle_sprint()

            # Handle pause menu (only if NOT the ESC key that opened it)
            if self.paused and self.pause_menu:
                result = self.pause_menu.handle_input(event)
                if result == 'resume':
                    self.paused = False
                    self.pause_menu = None
                elif result == 'settings':
                    try:
                        from core.settings_menu import SettingsMenu
                        settings = SettingsMenu()
                        settings.run(self.screen)
                        # Return to pause menu after settings
                        logger.info("Settings menu closed")
                    except Exception as e:
                        logger.error(f"Failed to open settings: {e}")
                elif result == 'quit':
                    self._save_game()
                    self.return_to_menu = True
                    self.running = False
                    logger.info("Returning to main menu")
                continue
            
            # Scene-specific events (only when not paused)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self._handle_interaction_key()
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                    logger.info(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
                elif event.key == pygame.K_F2:
                    self._take_screenshot()
                elif event.key == pygame.K_F3:
                    self._log_game_state()
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                        logger.info("Switched to windowed mode")
                    else:
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                        logger.info("Switched to fullscreen mode")

    def _handle_interaction_key(self):
        """Handle E key for interactions"""
        if self.interaction_mode:
            # Close interaction text and unlock player
            self.interaction_mode = False
            self.interaction_text = ""
            self.player_locked = False
        elif self.nearby_object:
            # Interact with nearby object and lock player
            self.player_locked = True
            self._handle_interaction()

    def _handle_interaction(self):
        """Handle interaction with nearby object"""
        if self.nearby_object and self.nearby_object in self.interactive_objects:
            obj_data = self.interactive_objects[self.nearby_object]

            self.interaction_text = obj_data['description']
            self.interaction_mode = True
            self.interaction_timer = 0
            logger.info(f"Player interacted with {self.nearby_object}")

    def _take_screenshot(self):
        """Take a screenshot for debugging"""
        if self.debugger:
            self.debugger.take_screenshot(self.game_surface, "bedroom_debug")
            logger.info("Screenshot taken")

    def _log_game_state(self):
        """Log current game state for debugging"""
        if self.debugger:
            self.debugger.log_game_state(
                self.player.rect, 
                self.camera.offset, 
                self.furniture_sprites.sprites(), 
                self.collision_rects
            )
            logger.info("Game state logged")

    def _save_game(self):
        """Save current game state"""
        if self.save_data and self.save_manager:
            try:
                # Update player position
                self.save_data['progress']['bedroom_position'] = {
                    'x': self.player.rect.centerx,
                    'y': self.player.rect.centery
                }
                self.save_data['progress']['bedroom_visited'] = True
                self.save_data['progress']['current_scene'] = 'bedroom'
                
                self.save_manager.save_game(self.save_data)
                logger.info("Game saved successfully")
            except Exception as e:
                logger.error(f"Failed to save game: {e}")
        else:
            logger.warning("No save data or save manager available")


    def update(self, dt):
        """Update bedroom scene logic"""
        if self.paused:
            if self.pause_menu:
                self.pause_menu.update(dt)
            return
            
        if self.eye_opening:
            self.eye_opening_timer += dt * 1000  # Convert to milliseconds
            if self.eye_opening_timer >= self.eye_opening_duration:
                self.eye_opening = False
                logger.info("Eye opening animation complete")
            return
        
        # Only allow player movement if not locked in interaction
        if not self.player_locked:
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.collision_rects, dt)
        
        # Update camera
        self.camera.update(dt)
        
        # Check for interactions
        self._check_interactions()
        
        # Don't auto-close interaction text - player must manually dismiss
        # Removed: interaction timer auto-close logic
        
        # Check for teleport
        self._check_teleport()

    def _check_interactions(self):
        """Check if player is near any interactive objects"""
        self.nearby_object = None
        self.show_e_prompt = False
        
        player_center = self.player.rect.center
        
        for obj_name, obj_data in self.interactive_objects.items():
            # Special case for rug
            if obj_name == 'rug':
                obj_rect = self.rug_teleport_rect
            else:
                obj_rect = obj_data['sprite'].rect
            
            # Calculate distance
            obj_center = obj_rect.center
            distance = ((player_center[0] - obj_center[0]) ** 2 + 
                       (player_center[1] - obj_center[1]) ** 2) ** 0.5
            
            # Check if within interaction range
            if distance <= obj_data['interaction_range']:
                self.nearby_object = obj_name
                self.show_e_prompt = True
                break

    def _check_teleport(self):
        """Check if player is on the teleport rug"""
        if self.player.rect.colliderect(self.rug_teleport_rect):
            logger.info("Player stepped on teleport rug - going outside!")

            # Set spawn position for outside scene (in front of house door)
            if self.save_data:
                # Player's house is at tile (8, 3) in outside map
                # House is 120px wide, positioned at 8 * 16 = 128px
                house_x = 8 * TILE_SIZE
                house_y = 3 * TILE_SIZE
                house_width = 120
                house_height = 100

                # Spawn player at center of house door, just below it
                spawn_x = house_x + (house_width // 2)
                spawn_y = house_y + house_height + 20  # 20 pixels below house

                self.save_data['progress']['outside_position'] = {
                    'x': spawn_x,
                    'y': spawn_y
                }
                self.save_manager.save_game(self.save_data)
                logger.info(f"Set outside spawn to: ({spawn_x}, {spawn_y})")

            self.teleport_to_outside = True
            self.running = False

    def draw(self):
        """Render bedroom scene"""
        # Clear surface
        self.game_surface.fill((30, 25, 35))
        
        # Draw map
        self._draw_map()
        
        # Draw sprites with depth sorting
        self._draw_sprites()
        
        # Draw debug overlay
        if self.debug_mode and self.debugger:
            self.debugger.draw_debug_overlay(
                self.game_surface, 
                self.player.rect, 
                self.camera.offset, 
                self.furniture_sprites.sprites(), 
                self.collision_rects
            )
        
        # Scale to screen
        scaled_surface = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        
        # Apply film grain effect
        self.global_effects.apply_full_effects(self.screen)
        
        # Draw eye opening effect
        if self.eye_opening:
            self._draw_eye_opening_effect()
        
        # Draw UI elements
        if not self.paused:
            self._draw_instructions()
        
        # Draw interaction UI
        if self.show_e_prompt and not self.interaction_mode and not self.paused:
            self._draw_e_prompt()
        
        if self.interaction_mode and not self.paused:
            self._draw_interaction_text()
        
        # Draw pause menu
        if self.paused and self.pause_menu:
            self.pause_menu.draw(self.screen)
        
        pygame.display.flip()

    def _draw_map(self):
        """Draw floor and wall tiles"""
        cam_offset = self.camera.offset
        
        # Draw floor tiles
        for y in range(self.map_height):
            for x in range(self.map_width):
                pos_x = x * TILE_SIZE - cam_offset.x
                pos_y = y * TILE_SIZE - cam_offset.y
                floor_tile = self.assets['floor'][(x + y) % len(self.assets['floor'])]
                self.game_surface.blit(floor_tile, (pos_x, pos_y))
        
        # Draw wall tiles at borders
        for y in range(self.map_height):
            for x in range(self.map_width):
                if y == 0 or y == self.map_height - 1 or x == 0 or x == self.map_width - 1:
                    pos_x = x * TILE_SIZE - cam_offset.x
                    pos_y = y * TILE_SIZE - cam_offset.y
                    self.game_surface.blit(self.assets['wall'], (pos_x, pos_y))
        
        # Draw teleport rug
        rug_pos_x = self.rug_teleport_pos[0] - cam_offset.x
        rug_pos_y = self.rug_teleport_pos[1] - cam_offset.y
        self.game_surface.blit(self.assets['rug_teleport'], (rug_pos_x, rug_pos_y))

    def _draw_sprites(self):
        """Draw all sprites with proper depth sorting"""
        all_sprites = [('player', self.player)]
        
        for sprite in self.furniture_sprites.sprites():
            all_sprites.append(('furniture', sprite))
        
        # Sort by depth (y-position)
        for sprite_type, sprite in all_sprites:
            if hasattr(sprite, 'visual_rect'):
                sprite._sort_key = sprite.visual_rect.bottom
            else:
                sprite._sort_key = sprite.rect.bottom
        
        all_sprites.sort(key=lambda item: item[1]._sort_key)
        
        # Draw all sprites
        for sprite_type, sprite in all_sprites:
            sprite.draw(self.game_surface, self.camera)

    def _draw_eye_opening_effect(self):
        """Draw eye opening fade effect"""
        progress = min(self.eye_opening_timer / self.eye_opening_duration, 1.0)
        alpha = int(255 * (1.0 - progress))
        if alpha > 0:
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.fill((0, 0, 0))
            black_surface.set_alpha(alpha)
            self.screen.blit(black_surface, (0, 0))

    def _draw_instructions(self):
        """Draw control instructions"""
        font = pygame.font.Font(None, 24)
        instructions = [
            "WASD/Arrow Keys - Move",
            "E - Interact",
            "ESC - Pause",
            "F1 - Debug Mode"
        ]

        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (10, SCREEN_HEIGHT - 100 + i * 20))

        # Show player position and speed for debugging
        keys = pygame.key.get_pressed()
        direction = ""
        if keys[pygame.K_UP]: direction += "UP "
        if keys[pygame.K_DOWN]: direction += "DOWN "
        if keys[pygame.K_LEFT]: direction += "LEFT "
        if keys[pygame.K_RIGHT]: direction += "RIGHT "
        if keys[pygame.K_w]: direction += "W "
        if keys[pygame.K_s]: direction += "S "
        if keys[pygame.K_a]: direction += "A "
        if keys[pygame.K_d]: direction += "D "

        pos_text = font.render(f"Pos: ({self.player.rect.x}, {self.player.rect.y})", True, (255, 255, 100))
        dir_text = font.render(f"Keys: {direction}", True, (255, 255, 100))
        self.screen.blit(pos_text, (10, 10))
        self.screen.blit(dir_text, (10, 35))

    def _draw_e_prompt(self):
        """Draw 'Press E to interact' prompt"""
        font = pygame.font.Font(None, 30)
        text = font.render("[E] Interact", True, (220, 200, 180))
        
        text_rect = text.get_rect()
        text_rect.centerx = SCREEN_WIDTH // 2
        text_rect.bottom = SCREEN_HEIGHT - 60
        
        # Atmospheric background
        bg_rect = text_rect.inflate(30, 15)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.fill((20, 18, 25))
        bg_surface.set_alpha(200)
        self.screen.blit(bg_surface, bg_rect.topleft)
        
        # Subtle border
        pygame.draw.rect(self.screen, (120, 100, 80), bg_rect, 2)
        
        self.screen.blit(text, text_rect)

    def _draw_interaction_text(self):
        """Draw atmospheric interaction text box"""
        font = pygame.font.Font(None, 28)
        
        # Word wrap the text
        words = self.interaction_text.split(' ')
        lines = []
        current_line = []
        max_width = SCREEN_WIDTH - 200
        
        for word in words:
            # Handle newlines in the text
            if '\n' in word:
                parts = word.split('\n')
                for i, part in enumerate(parts):
                    if i > 0:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = []
                    if part:
                        current_line.append(part)
            else:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate text box size
        line_height = font.get_height() + 8
        text_height = len(lines) * line_height + 80
        text_width = SCREEN_WIDTH - 160
        
        # Center the box but lower on screen
        box_rect = pygame.Rect(
            (SCREEN_WIDTH - text_width) // 2,
            SCREEN_HEIGHT - text_height - 120,  # Moved down, 120px from bottom
            text_width,
            text_height
        )
        
        # Draw dark atmospheric background with border
        bg_surface = pygame.Surface((box_rect.width, box_rect.height))
        bg_surface.fill((15, 12, 18))
        bg_surface.set_alpha(245)
        self.screen.blit(bg_surface, box_rect.topleft)
        
        # Draw ornate border
        border_color = (120, 100, 80)
        pygame.draw.rect(self.screen, border_color, box_rect, 4)
        # Inner border
        inner_rect = box_rect.inflate(-8, -8)
        pygame.draw.rect(self.screen, (80, 70, 60), inner_rect, 2)
        
        # Draw text lines with better spacing
        y_offset = box_rect.top + 25
        for line in lines:
            text_surface = font.render(line, True, (230, 220, 210))
            text_rect = text_surface.get_rect()
            text_rect.centerx = box_rect.centerx
            text_rect.top = y_offset
            self.screen.blit(text_surface, text_rect)
            y_offset += line_height
        
        # Draw control hint at bottom
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("[E] or [ESC] to close", True, (180, 160, 140))
        hint_rect = hint_text.get_rect()
        hint_rect.centerx = box_rect.centerx
        hint_rect.bottom = box_rect.bottom - 15
        self.screen.blit(hint_text, hint_rect)


    def run(self):
        """Main game loop"""
        pygame.event.clear()
        logger.info("Bedroom scene started")
        
        while self.running:
            raw_dt = self.clock.tick(60) / 1000.0
            dt = self.frame_smoother.smooth_dt(raw_dt)  # Smooth frame time
            self.handle_events()
            self.update(dt)
            self.draw()
        
        logger.info("Bedroom scene exited")

        # Return dict with exit info
        return {
            'teleport_outside': self.teleport_to_outside,
            'start_battle': self.start_battle,
            'return_to_menu': self.return_to_menu
        }

    def cleanup(self):
        """Cleanup bedroom scene resources"""
        logger.debug("Cleaning up bedroom scene")
        # Mark bedroom as visited and save position
        if self.save_data:
            self.save_data['progress']['bedroom_visited'] = True
            self.save_data['progress']['bedroom_position'] = {
                'x': self.player.rect.centerx,
                'y': self.player.rect.centery
            }
            self.save_data['progress']['current_scene'] = 'bedroom'