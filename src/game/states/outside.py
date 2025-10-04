"""
Outside Area Scene for Pokemon Faiths
First outdoor area - house exterior
"""

import pygame
from constants import (
    DEFAULT_SCREEN_WIDTH as SCREEN_WIDTH, 
    DEFAULT_SCREEN_HEIGHT as SCREEN_HEIGHT,
    TILE_SIZE, GAME_WIDTH, GAME_HEIGHT,
    HOUSE_WALL_THICKNESS, HOUSE_COLLISION_INSET, HOUSE_DOORWAY_WIDTH
)
from core.asset_manager import get_asset_manager
from core.logger import get_logger
from core.entities import Player, Camera
from core.game_debugger import GameDebugger
from core.pause_menu import PauseMenu
from core.visual_effects import GlobalEffects
from core.frame_smoother import FrameTimeSmoother

logger = get_logger('Outside')

class OutsideScene:
    """Outdoor area scene with house exterior"""
    
    def __init__(self, screen_width, screen_height, save_data=None, player_name="Player"):
        # Pygame setup
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Pokemon Faiths - Outside")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Save system
        from core.save_manager import get_save_manager
        self.save_manager = get_save_manager()
        self.save_data = save_data
        self.player_name = player_name
        
        # Debug mode
        self.debug_mode = False
        
        # Import debugger
        try:
            from core.game_debugger import GameDebugger
            self.debugger = GameDebugger(clock=self.clock)
        except ImportError:
            self.debugger = None
        
        # Pause menu state
        self.paused = False
        self.pause_menu = None
        self.return_to_menu = False
        self.enter_cave = False
        
        # Load assets
        self.assets = self._load_assets()
        
        # Setup outdoor map
        self._setup_map()
        
        if save_data and 'progress' in save_data and 'outside_position' in save_data['progress']:
            pos = save_data['progress']['outside_position']
            logger.info(f"Loading outside position from save: ({pos['x']}, {pos['y']})")
            self.player = Player(pos['x'], pos['y'])
        else:
            # Start player in village center (on main road, safe from houses)
            spawn_x = 17 * TILE_SIZE  # Main road center
            spawn_y = 13 * TILE_SIZE  # On horizontal road
            logger.info("Starting player in village center")
            self.player = Player(spawn_x, spawn_y)
        
        self.camera = Camera(self.player)
        
        # Visual effects
        self.global_effects = GlobalEffects(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frame_smoother = FrameTimeSmoother(max_dt=0.05)
        
        # Debug mode
        self.debug_mode = False
        
        # Import debugger
        try:
            from core.game_debugger import GameDebugger
            self.debugger = GameDebugger(clock=self.clock)
        except ImportError:
            self.debugger = None
        
        logger.info("Outside scene initialized")
    
    def _load_assets(self):
        """Load outdoor assets"""
        assets = {
            'grass': [],
            'dirt': None,
            'house': None,
            'rug_return': None,
            'cave_entrance': None
        }

        asset_manager = get_asset_manager()

        # Load grass tiles (3 variations)
        for i in range(1, 4):
            grass_path = f'assets/images/grass_tile{i}.png'
            scaled_tile = asset_manager.load_image(grass_path, (TILE_SIZE, TILE_SIZE))
            assets['grass'].append(scaled_tile)

        # Load dirt road
        assets['dirt'] = asset_manager.load_image('assets/images/dart_road.png', (TILE_SIZE, TILE_SIZE))

        # Load house exterior (scaled down to reasonable size)
        assets['house'] = asset_manager.load_image('assets/images/exterior_house.png', (120, 100))

        # Load return rug (for going back inside)
        assets['rug_return'] = asset_manager.load_image('assets/images/rug_tile.png', (TILE_SIZE, TILE_SIZE))

        # Load cave entrance
        assets['cave_entrance'] = asset_manager.load_image('assets/images/cave_entrance.png', (80, 80))

        logger.info("Outdoor assets loaded")
        return assets
    
    def _setup_map(self):
        """Create large village with multiple houses"""
        # Much bigger map for a village
        self.map_width = 40
        self.map_height = 30

        self.collision_rects = []
        self.furniture_sprites = pygame.sprite.Group()
        self.houses = []  # Track all houses for collision

        # Tight border collisions
        border_thickness = 4

        # Map borders
        self.collision_rects.extend([
            pygame.Rect(0, 0, self.map_width * TILE_SIZE, border_thickness),  # Top
            pygame.Rect(0, self.map_height * TILE_SIZE - border_thickness,
                       self.map_width * TILE_SIZE, border_thickness),  # Bottom
            pygame.Rect(0, 0, border_thickness, self.map_height * TILE_SIZE),  # Left
            pygame.Rect(self.map_width * TILE_SIZE - border_thickness, 0,
                       border_thickness, self.map_height * TILE_SIZE)  # Right
        ])

        # Create village layout with multiple houses
        # House positions (tile coordinates): (x, y, has_door)
        house_positions = [
            (8, 3, True),   # Player's house (top-left area) - ENTRANCE
            (25, 3, False),  # House top-right
            (8, 15, False),  # House mid-left
            (25, 15, False), # House mid-right
            (16, 22, False), # House bottom-center
        ]

        # Create dirt road network
        self.road_tiles = []

        # Horizontal main road (middle of map)
        for x in range(5, 35):
            self.road_tiles.append((x, 12))
            self.road_tiles.append((x, 13))

        # Vertical roads connecting houses
        for y in range(3, 13):
            self.road_tiles.append((12, y))
            self.road_tiles.append((13, y))
            self.road_tiles.append((22, y))
            self.road_tiles.append((23, y))

        # Road to bottom house
        for y in range(13, 23):
            self.road_tiles.append((17, y))
            self.road_tiles.append((18, y))

        # Add houses to map
        for i, (tile_x, tile_y, has_door) in enumerate(house_positions):
            house_sprite = pygame.sprite.Sprite()
            house_sprite.image = self.assets['house']
            house_x = tile_x * TILE_SIZE
            house_y = tile_y * TILE_SIZE
            house_sprite.rect = house_sprite.image.get_rect(topleft=(house_x, house_y))
            house_sprite.draw = lambda surface, camera, hs=house_sprite: surface.blit(
                hs.image, hs.rect.topleft - camera.offset
            )
            self.furniture_sprites.add(house_sprite)

            # Store first house as player house (with entrance)
            if has_door:
                self.house_sprite = house_sprite

            self.houses.append({
                'sprite': house_sprite,
                'has_door': has_door
            })

            # Add collision for this house
            wall_thickness = 5
            inset = 12

            # House walls
            left_wall = pygame.Rect(
                house_sprite.rect.x + inset,
                house_sprite.rect.y + inset,
                wall_thickness,
                house_sprite.rect.height - inset * 2
            )

            right_wall = pygame.Rect(
                house_sprite.rect.right - inset - wall_thickness,
                house_sprite.rect.y + inset,
                wall_thickness,
                house_sprite.rect.height - inset * 2
            )

            top_wall = pygame.Rect(
                house_sprite.rect.x + inset,
                house_sprite.rect.y + inset,
                house_sprite.rect.width - inset * 2,
                wall_thickness
            )

            # Bottom wall - only add doorway for player house
            if has_door:
                doorway_width = 20
                doorway_center = house_sprite.rect.centerx

                bottom_left = pygame.Rect(
                    house_sprite.rect.x + inset,
                    house_sprite.rect.bottom - inset - wall_thickness,
                    (doorway_center - doorway_width // 2) - (house_sprite.rect.x + inset),
                    wall_thickness
                )

                bottom_right = pygame.Rect(
                    doorway_center + doorway_width // 2,
                    house_sprite.rect.bottom - inset - wall_thickness,
                    (house_sprite.rect.right - inset) - (doorway_center + doorway_width // 2),
                    wall_thickness
                )

                self.collision_rects.extend([left_wall, right_wall, top_wall, bottom_left, bottom_right])

                # Doorway teleport trigger (only for player house)
                self.house_doorway_rect = pygame.Rect(
                    doorway_center - 10,
                    house_sprite.rect.bottom - 8,
                    20,
                    12
                )
            else:
                # Solid bottom wall for other houses
                bottom_wall = pygame.Rect(
                    house_sprite.rect.x + inset,
                    house_sprite.rect.bottom - inset - wall_thickness,
                    house_sprite.rect.width - inset * 2,
                    wall_thickness
                )
                self.collision_rects.extend([left_wall, right_wall, top_wall, bottom_wall])

        # Add cave entrance (outside village, beyond top border)
        cave_sprite = pygame.sprite.Sprite()
        cave_sprite.image = self.assets['cave_entrance']
        cave_x = 35 * TILE_SIZE  # Far right, outside village
        cave_y = 1 * TILE_SIZE  # Near top edge
        cave_sprite.rect = cave_sprite.image.get_rect(topleft=(cave_x, cave_y))
        cave_sprite.draw = lambda surface, camera: surface.blit(
            cave_sprite.image, cave_sprite.rect.topleft - camera.offset
        )
        self.furniture_sprites.add(cave_sprite)
        self.cave_sprite = cave_sprite

        # Cave collision (walls around entrance)
        cave_wall_thickness = 5
        cave_inset = 8

        # Left wall of cave
        cave_left = pygame.Rect(
            cave_sprite.rect.x + cave_inset,
            cave_sprite.rect.y + cave_inset,
            cave_wall_thickness,
            cave_sprite.rect.height - cave_inset * 2
        )

        # Right wall of cave
        cave_right = pygame.Rect(
            cave_sprite.rect.right - cave_inset - cave_wall_thickness,
            cave_sprite.rect.y + cave_inset,
            cave_wall_thickness,
            cave_sprite.rect.height - cave_inset * 2
        )

        # Top wall of cave
        cave_top = pygame.Rect(
            cave_sprite.rect.x + cave_inset,
            cave_sprite.rect.y + cave_inset,
            cave_sprite.rect.width - cave_inset * 2,
            cave_wall_thickness
        )

        self.collision_rects.extend([cave_left, cave_right, cave_top])

        # Cave entrance teleport trigger (in front of cave)
        self.cave_entrance_rect = pygame.Rect(
            cave_sprite.rect.centerx - 15,
            cave_sprite.rect.bottom - 10,
            30,
            15
        )

        logger.info(f"Village map created: {self.map_width}x{self.map_height} with {len(self.houses)} houses and cave entrance")
    
    def _draw_map(self):
        """Draw outdoor ground tiles"""
        cam_offset = self.camera.offset

        # Draw grass tiles
        for y in range(self.map_height):
            for x in range(self.map_width):
                pos_x = x * TILE_SIZE - cam_offset.x
                pos_y = y * TILE_SIZE - cam_offset.y

                # Check if this is a road tile
                if (x, y) in self.road_tiles:
                    self.game_surface.blit(self.assets['dirt'], (pos_x, pos_y))
                else:
                    # Use grass variations
                    grass_tile = self.assets['grass'][(x + y) % len(self.assets['grass'])]
                    self.game_surface.blit(grass_tile, (pos_x, pos_y))
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received")
                self._save_game()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.paused:
                        self.paused = False
                        self.pause_menu = None
                    else:
                        self.paused = True
                        self.pause_menu = PauseMenu(self.save_data, "Outside")
                        logger.info("Game paused")
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
            
            # Regular game events
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.debug_mode = not self.debug_mode
                logger.info(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
    
    
    def _save_game(self):
        """Save current position"""
        if self.save_data:
            self.save_data['progress']['outside_position'] = {
                'x': self.player.rect.x,
                'y': self.player.rect.y
            }
            self.save_data['progress']['current_scene'] = 'outside'
            
            if self.save_manager.save_game(self.save_data):
                logger.info("Game saved successfully")
    
    def _check_house_entry(self):
        """Check if player is entering house"""
        if self.player.rect.colliderect(self.house_doorway_rect):
            logger.info("Player entering house door - going to bedroom!")
            # Set the spawn position for bedroom scene (in front of rug)
            if self.save_data:
                # Bedroom map is 14 tiles wide x 12 tiles high
                bedroom_map_width = 14
                bedroom_map_height = 12

                # Spawn at horizontal center of bedroom, above the rug
                spawn_x = (bedroom_map_width * TILE_SIZE) // 2
                spawn_y = (bedroom_map_height - 2) * TILE_SIZE - 30  # 30 pixels above rug

                self.save_data['progress']['bedroom_position'] = {
                    'x': spawn_x,
                    'y': spawn_y
                }
                self.save_manager.save_game(self.save_data)
                logger.info(f"Set bedroom spawn to: ({spawn_x}, {spawn_y})")
            return True
        return False

    def _check_cave_entry(self):
        """Check if player is entering cave"""
        if self.player.rect.colliderect(self.cave_entrance_rect):
            logger.info("Player entering cave!")
            # Set spawn position for cave scene (at entrance/exit)
            if self.save_data:
                cave_width = 20
                cave_height = 10
                # Spawn at bottom center (near exit)
                spawn_x = (cave_width // 2) * TILE_SIZE
                spawn_y = (cave_height - 3) * TILE_SIZE
                self.save_data['progress']['cave_position'] = {
                    'x': spawn_x,
                    'y': spawn_y
                }
                self.save_manager.save_game(self.save_data)
                logger.info(f"Set cave spawn to entrance: ({spawn_x}, {spawn_y})")
            return True
        return False
    
    def update(self, dt):
        """Update game state"""
        if self.paused:
            if self.pause_menu:
                self.pause_menu.update(dt)
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.collision_rects, dt)
        self.camera.update()

        # Check for house entry
        if self._check_house_entry():
            logger.info("Player entering house - teleporting to bedroom")
            self.return_to_bedroom = True
            self.running = False

        # Check for cave entry
        if self._check_cave_entry():
            logger.info("Player entering cave")
            self.enter_cave = True
            self.running = False
    
    
    def draw(self):
        """Render the scene"""
        self.game_surface.fill((40, 35, 30))  # Darker outdoor background
        
        # Draw map
        self._draw_map()
        
        # Draw sprites
        all_sprites = [('player', self.player)]
        for sprite in self.furniture_sprites.sprites():
            all_sprites.append(('furniture', sprite))
        
        # Sort by depth
        for sprite_type, sprite in all_sprites:
            if hasattr(sprite, 'visual_rect'):
                sprite._sort_key = sprite.visual_rect.bottom
            else:
                sprite._sort_key = sprite.rect.bottom
        
        all_sprites.sort(key=lambda item: item[1]._sort_key)
        
        # Draw all sprites
        for sprite_type, sprite in all_sprites:
            if sprite_type == 'player':
                sprite.draw(self.game_surface, self.camera)
            else:
                sprite.draw(self.game_surface, self.camera)
        
        # Debug mode
        if self.debug_mode and self.debugger:
            self.debugger.draw_debug_overlay(
                self.game_surface,
                self.player.rect,
                self.camera.offset,
                self.furniture_sprites.sprites(),
                self.collision_rects
            )
            
            # Show house doorway teleport zone (in debug mode)
            cam_offset = self.camera.offset
            door_screen_rect = pygame.Rect(
                self.house_doorway_rect.x - cam_offset.x,
                self.house_doorway_rect.y - cam_offset.y,
                self.house_doorway_rect.width,
                self.house_doorway_rect.height
            )
            pygame.draw.rect(self.game_surface, (0, 255, 0), door_screen_rect, 3)  # Green door zone
        
        # Scale to screen
        scaled_surface = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        
        # Apply film grain effect
        self.global_effects.apply_full_effects(self.screen)
        
        # Pause menu
        if self.paused and self.pause_menu:
            self.pause_menu.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        pygame.event.clear()
        logger.info("Outside scene started")
        
        self.return_to_bedroom = False
        
        while self.running:
            raw_dt = self.clock.tick(60) / 1000.0
            dt = self.frame_smoother.smooth_dt(raw_dt)
            self.handle_events()
            self.update(dt)
            self.draw()
        
        logger.info("Outside scene exited")

        # Return dict with exit info
        if self.return_to_menu:
            return {'return_to_menu': True}
        elif self.return_to_bedroom:
            return {'return_to_bedroom': True}
        elif self.enter_cave:
            return {'enter_cave': True}
        else:
            return {}
    
    def cleanup(self):
        """Cleanup outside scene resources"""
        logger.debug("Cleaning up outside scene")
        # Save current position
        if self.save_data:
            self.save_data['progress']['outside_position'] = {
                'x': self.player.rect.centerx,
                'y': self.player.rect.centery
            }
            self.save_data['progress']['current_scene'] = 'outside'

