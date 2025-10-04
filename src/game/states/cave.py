"""
Cave Interior Scene for Pokemon Faiths
Dark, claustrophobic atmosphere
"""

import pygame
import os
from constants import (
    DEFAULT_SCREEN_WIDTH as SCREEN_WIDTH,
    DEFAULT_SCREEN_HEIGHT as SCREEN_HEIGHT,
    TILE_SIZE, GAME_WIDTH, GAME_HEIGHT
)
from core.asset_manager import get_asset_manager
from core.logger import get_logger
from core.entities import Player, Camera
from core.game_debugger import GameDebugger
from core.pause_menu import PauseMenu
from core.visual_effects import CaveEffects, GlobalEffects
from core.frame_smoother import FrameTimeSmoother

logger = get_logger('Cave')

class CaveScene:
    """Dark cave scene with atmospheric effects"""

    def __init__(self, screen_width, screen_height, save_data=None, player_name="Player"):
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Pokemon Faiths - Cave")
        self.clock = pygame.time.Clock()
        self.running = True

        from core.save_manager import get_save_manager
        self.save_manager = get_save_manager()
        self.save_data = save_data
        self.player_name = player_name

        self.debug_mode = False
        self.debugger = GameDebugger(clock=self.clock)

        self.paused = False
        self.pause_menu = None
        self.return_to_menu = False
        self.exit_cave = False
        self.start_battle = False  # Flag for battle transition

        self.interaction_mode = False
        self.interaction_text = ""
        self.nearby_object = None
        self.show_e_prompt = False
        self.pending_pokeball_take = False
        self.player_locked = False
        
        # Wild encounter system
        self.encounter_step_counter = 0
        self.steps_until_encounter = 0
        self.in_battle = False
        self.last_grass_tile = None  # Track last grass tile for step counting
        self._reset_encounter_counter()

        self.assets = self._load_assets()
        self._setup_map()
        
        # Cave visual effects (use SCREEN size so grain doesn't follow camera)
        self.cave_effects = CaveEffects(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.global_effects = GlobalEffects(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frame_smoother = FrameTimeSmoother(max_dt=0.05)

        if save_data and 'progress' in save_data and 'cave_position' in save_data['progress']:
            pos = save_data['progress']['cave_position']
            self.player = Player(pos['x'], pos['y'])
        else:
            # Spawn at entrance (bottom center)
            spawn_x = (self.map_width // 2) * TILE_SIZE
            spawn_y = (self.map_height - 3) * TILE_SIZE  # Near exit
            logger.info(f"Starting player at cave entrance: ({spawn_x}, {spawn_y})")
            self.player = Player(spawn_x, spawn_y)

        self.camera = Camera(self.player)
        logger.info("Cave scene initialized")

    def _load_assets(self):
        """Load and darken cave assets"""
        assets = {
            'floor': None,  # Cave floor
            'grass': [],  # Grass patches for encounters
            'old_man_with_pokeball': None,
            'old_man_without_pokeball': None
        }
        asset_manager = get_asset_manager()

        # Load cave floor tile
        cave_floor = asset_manager.load_image('assets/images/cave_tile.png', (TILE_SIZE, TILE_SIZE))
        assets['floor'] = self._darken_surface(cave_floor, 0.7)  # Darker cave
        
        # Load grass tiles for encounter zones
        for i in range(1, 4):
            grass_path = f'assets/images/grass_tile{i}.png'
            grass_tile = asset_manager.load_image(grass_path, (TILE_SIZE, TILE_SIZE))
            dark_grass = self._darken_surface(grass_tile, 0.6)  # Very dark grass in cave
            assets['grass'].append(dark_grass)

        try:
            assets['old_man_with_pokeball'] = asset_manager.load_image('assets/images/dead_old_man.png', (TILE_SIZE, TILE_SIZE))
            assets['old_man_without_pokeball'] = asset_manager.load_image('assets/images/dead_old_man_no_pokeball.png', (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            logger.error(f"Failed to load old man sprites: {e}")
            placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE))
            placeholder.fill((100, 50, 50))
            assets['old_man_with_pokeball'] = placeholder
            assets['old_man_without_pokeball'] = placeholder

        return assets
    
    def _darken_surface(self, surface, factor=0.5):
        """Darken surface (0.0=black, 1.0=original)"""
        dark = surface.copy()
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(int(255 * (1 - factor)))
        dark.blit(overlay, (0, 0))
        return dark

    def _setup_map(self):
        """Create cave with grass encounter zones"""
        self.map_width = 20
        self.map_height = 10
        self.collision_rects = []
        self.furniture_sprites = pygame.sprite.Group()

        # Grass patches for encounters (tile coordinates)
        self.grass_tiles = [
            # Left side grass patch
            (5, 3), (6, 3), (7, 3),
            (5, 4), (6, 4), (7, 4),
            (5, 5), (6, 5), (7, 5),
            # Right side grass patch
            (13, 6), (14, 6), (15, 6),
            (13, 7), (14, 7), (15, 7),
            (13, 8), (14, 8), (15, 8),
            # Center grass patch (near middle)
            (9, 4), (10, 4), (11, 4),
            (9, 5), (10, 5), (11, 5),
        ]

        border_thickness = 8
        self.collision_rects.extend([
            pygame.Rect(0, 0, self.map_width * TILE_SIZE, border_thickness),
            pygame.Rect(0, self.map_height * TILE_SIZE - border_thickness, self.map_width * TILE_SIZE, border_thickness),
            pygame.Rect(0, 0, border_thickness, self.map_height * TILE_SIZE),
            pygame.Rect(self.map_width * TILE_SIZE - border_thickness, 0, border_thickness, self.map_height * TILE_SIZE)
        ])

        self.exit_rect = pygame.Rect((self.map_width // 2 - 1) * TILE_SIZE, (self.map_height - 2) * TILE_SIZE, TILE_SIZE * 2, TILE_SIZE)

        self.pokeball_taken = self.save_data.get('progress', {}).get('old_man_pokeball_taken', False) if self.save_data else False

        old_man_sprite = pygame.sprite.Sprite()
        old_man_sprite.image = self.assets['old_man_without_pokeball' if self.pokeball_taken else 'old_man_with_pokeball']
        old_man_x = border_thickness + 15
        old_man_y = (2 * TILE_SIZE) + 10
        old_man_sprite.rect = old_man_sprite.image.get_rect(topleft=(old_man_x, old_man_y))
        old_man_sprite.draw = lambda surface, camera: surface.blit(old_man_sprite.image, old_man_sprite.rect.topleft - camera.offset)
        self.furniture_sprites.add(old_man_sprite)
        self.old_man_sprite = old_man_sprite

        collision_size = 20
        old_man_collision = pygame.Rect(old_man_sprite.rect.centerx - collision_size // 2, old_man_sprite.rect.centery - collision_size // 2 - 8, collision_size, collision_size)
        self.collision_rects.append(old_man_collision)
        
        self.interactive_objects = {
            'old_man': {
                'sprite': old_man_sprite,
                'description': self._get_old_man_description(),
                'interaction_range': 45,
                'action': 'old_man_interaction'
            }
        }

        logger.info(f"Cave map created: {self.map_width}x{self.map_height} with {len(self.grass_tiles)} grass encounter tiles")

    def _draw_map(self):
        """Draw cave floor with grass patches"""
        cam_offset = self.camera.offset
        for y in range(self.map_height):
            for x in range(self.map_width):
                pos_x = x * TILE_SIZE - cam_offset.x
                pos_y = y * TILE_SIZE - cam_offset.y
                
                # Check if this is a grass tile
                if (x, y) in self.grass_tiles:
                    # Draw grass for encounters
                    grass_tile = self.assets['grass'][(x + y) % len(self.assets['grass'])]
                    self.game_surface.blit(grass_tile, (pos_x, pos_y))
                else:
                    # Draw cave floor
                    self.game_surface.blit(self.assets['floor'], (pos_x, pos_y))

    def handle_events(self):
        """Handle input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_game()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.interaction_mode:
                        self.interaction_mode = False
                        self.interaction_text = ""
                        self.pending_pokeball_take = False
                        self.player_locked = False
                        continue
                    self.paused = not self.paused
                    self.pause_menu = PauseMenu(self.save_data, "Cave") if self.paused else None
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.toggle_sprint()
                elif event.key == pygame.K_e:
                    self._handle_interaction_key()
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode

            if self.paused and self.pause_menu:
                result = self.pause_menu.handle_input(event)
                if result == 'resume':
                    self.paused = False
                    self.pause_menu = None
                elif result == 'settings':
                    from core.settings_menu import SettingsMenu
                    SettingsMenu().run(self.screen)
                elif result == 'quit':
                    self._save_game()
                    self.return_to_menu = True
                    self.running = False

    def _handle_interaction_key(self):
        if self.interaction_mode:
            # Check if this is a battle trigger
            if self.in_battle:
                logger.info("Starting battle transition!")
                self.start_battle = True
                self.running = False
                return
            
            if self.pending_pokeball_take:
                self._take_pokeball()
                return
            self.interaction_mode = False
            self.interaction_text = ""
            self.player_locked = False
        elif self.nearby_object:
            self.player_locked = True
            self._handle_interaction()

    def _get_old_man_description(self):
        if self.pokeball_taken:
            return "The old man's body lies still. His empty hand rests where the Pokéball once was."
        return "A dead old man slumped against the wall. His hand clutches a worn Pokéball. It trembles faintly."
    
    def _reset_encounter_counter(self):
        """Reset steps until next encounter (random 5-15 steps)"""
        import random
        self.steps_until_encounter = random.randint(5, 15)
        self.encounter_step_counter = 0
        logger.debug(f"Next encounter in {self.steps_until_encounter} steps")
    
    def _is_on_grass(self):
        """Check if player is standing on grass tile"""
        player_tile_x = self.player.rect.centerx // TILE_SIZE
        player_tile_y = self.player.rect.centery // TILE_SIZE
        return (player_tile_x, player_tile_y) in self.grass_tiles
    
    def _check_wild_encounter(self):
        """Check if wild encounter should trigger"""
        if not self._is_on_grass():
            self.last_grass_tile = None
            return False
        
        # Get current tile
        player_tile_x = self.player.rect.centerx // TILE_SIZE
        player_tile_y = self.player.rect.centery // TILE_SIZE
        current_tile = (player_tile_x, player_tile_y)
        
        # Only count as a step if we moved to a NEW grass tile
        if current_tile != self.last_grass_tile:
            self.last_grass_tile = current_tile
            self.encounter_step_counter += 1
            logger.debug(f"Step {self.encounter_step_counter}/{self.steps_until_encounter}")
            
            # Check if encounter should happen
            if self.encounter_step_counter >= self.steps_until_encounter:
                logger.info("Wild encounter triggered!")
                self._trigger_wild_encounter()
                return True
        
        return False
    
    def _trigger_wild_encounter(self):
        """Trigger a wild Pokemon encounter"""
        import random
        
        # Check if player has Pokemon
        if not self.save_data or 'party' not in self.save_data or len(self.save_data['party']) == 0:
            logger.warning("Player has no Pokemon! Can't battle.")
            self.interaction_text = "A wild Pokemon rustles in the grass...\n\nBut you have no Pokémon to defend yourself!"
            self.interaction_mode = True
            self.player_locked = True
            self._reset_encounter_counter()
            return
        
        # Cave Pokemon pool (corrupted/ghost types fit dark theme)
        cave_pokemon = [
            {'name': 'Zubat', 'level': random.randint(3, 6)},
            {'name': 'Gastly', 'level': random.randint(4, 7)},
            {'name': 'Haunter', 'level': random.randint(5, 8)},
            {'name': 'Misdreavus', 'level': random.randint(4, 7)},
        ]
        
        # Pick random Pokemon
        wild_pokemon_data = random.choice(cave_pokemon)
        logger.info(f"Wild {wild_pokemon_data['name']} (Lv.{wild_pokemon_data['level']}) appeared!")
        
        # Create wild Pokemon instance
        wild_pokemon = self._create_wild_pokemon(wild_pokemon_data['name'], wild_pokemon_data['level'])
        
        # Reset counter for next encounter
        self._reset_encounter_counter()
        
        # Start battle
        self._start_battle(wild_pokemon)
    
    def _create_wild_pokemon(self, name, level):
        """Create a wild Pokemon instance"""
        # Basic Pokemon stats (would normally come from database)
        pokemon_stats = {
            'Zubat': {'hp': 15, 'attack': 8, 'defense': 6, 'speed': 12, 'type': ['Poison', 'Flying']},
            'Gastly': {'hp': 12, 'attack': 10, 'defense': 5, 'speed': 15, 'type': ['Ghost', 'Poison']},
            'Haunter': {'hp': 18, 'attack': 13, 'defense': 8, 'speed': 18, 'type': ['Ghost', 'Poison']},
            'Misdreavus': {'hp': 16, 'attack': 10, 'defense': 10, 'speed': 17, 'type': ['Ghost']},
        }
        
        stats = pokemon_stats.get(name, {'hp': 15, 'attack': 10, 'defense': 8, 'speed': 12, 'type': ['Normal']})
        
        # Scale stats with level
        hp = stats['hp'] + (level * 2)
        attack = stats['attack'] + level
        defense = stats['defense'] + level
        speed = stats['speed'] + level
        
        return {
            'name': name,
            'level': level,
            'hp': hp,
            'max_hp': hp,
            'attack': attack,
            'defense': defense,
            'speed': speed,
            'type': stats['type'],
            'moves': [
                {'name': 'Tackle', 'pp': 35, 'max_pp': 35, 'power': 40, 'type': 'Normal'},
            ],
            'status': None
        }
    
    def _start_battle(self, wild_pokemon):
        """Start a battle with wild Pokemon"""
        logger.info(f"Starting battle with {wild_pokemon['name']}!")
        
        # Save current state before battle
        self._save_game()
        
        # Prepare for battle transition
        self.in_battle = True
        self.player_locked = True
        
        # Store wild Pokemon for battle
        if self.save_data:
            self.save_data['battle'] = {
                'type': 'wild',
                'opponent': wild_pokemon,
                'can_run': True
            }
            self.save_manager.save_game(self.save_data)
        
        # Show transition message
        self.interaction_text = f"A wild {wild_pokemon['name']} appeared!\n\nLevel {wild_pokemon['level']}\n\n[Press E to battle]"
        self.interaction_mode = True
        
        # TODO: Transition to battle scene
        # For now, just show message
        logger.info("Battle system integration pending...")

    def _handle_interaction(self):
        if self.nearby_object in self.interactive_objects:
            obj_data = self.interactive_objects[self.nearby_object]
            if obj_data.get('action') == 'old_man_interaction' and not self.pokeball_taken:
                self.interaction_text = obj_data['description'] + "\n\nTake the Pokéball?\n[E to take | ESC to leave]"
                self.pending_pokeball_take = True
            else:
                self.interaction_text = obj_data['description']
            self.interaction_mode = True

    def _take_pokeball(self):
        if self.save_data:
            self.save_data.setdefault('progress', {})['old_man_pokeball_taken'] = True
            
            # Give player the starter Pokemon (Corrupted Charmander)
            if 'party' not in self.save_data:
                self.save_data['party'] = []
            
            # Create corrupted starter Pokemon
            starter_pokemon = {
                'name': 'Charmander',
                'nickname': 'Ember',
                'level': 5,
                'exp': 0,
                'hp': 25,
                'max_hp': 25,
                'attack': 12,
                'defense': 10,
                'speed': 15,
                'type': ['Fire'],
                'moves': [
                    {'name': 'Scratch', 'pp': 35, 'max_pp': 35, 'power': 40, 'type': 'Normal'},
                    {'name': 'Ember', 'pp': 25, 'max_pp': 25, 'power': 40, 'type': 'Fire'}
                ],
                'status': None,
                'corrupted': True  # Special flag for story purposes
            }
            
            self.save_data['party'].append(starter_pokemon)
            logger.info(f"Player received starter Pokemon: {starter_pokemon['name']} (Corrupted)")
            
            self.save_manager.save_game(self.save_data)
        
        self.pokeball_taken = True
        self.old_man_sprite.image = self.assets['old_man_without_pokeball']
        self.interactive_objects['old_man']['description'] = self._get_old_man_description()
        self.interaction_text = "You pry the Pokéball from his cold fingers. It's warm... Something inside still clings to life.\n\nYou received a Charmander!\n\nSomething feels... wrong about it."
        self.interaction_mode = True
        self.pending_pokeball_take = False

    def _save_game(self):
        if self.save_data:
            self.save_data['progress']['cave_position'] = {'x': self.player.rect.x, 'y': self.player.rect.y}
            self.save_data['progress']['current_scene'] = 'cave'
            self.save_manager.save_game(self.save_data)

    def _check_exit(self):
        if self.player.rect.colliderect(self.exit_rect):
            if self.save_data:
                cave_x = 35 * TILE_SIZE
                cave_y = 1 * TILE_SIZE
                self.save_data['progress']['outside_position'] = {'x': cave_x + 40, 'y': cave_y + 100}
                self.save_manager.save_game(self.save_data)
            return True
        return False

    def _check_interactions(self):
        self.nearby_object = None
        self.show_e_prompt = False
        player_center = self.player.rect.center
        
        for obj_name, obj_data in self.interactive_objects.items():
            obj_center = obj_data['sprite'].rect.center
            distance = ((player_center[0] - obj_center[0]) ** 2 + (player_center[1] - obj_center[1]) ** 2) ** 0.5
            if distance <= obj_data['interaction_range']:
                self.nearby_object = obj_name
                self.show_e_prompt = True
                break

    def update(self, dt):
        if self.paused:
            if self.pause_menu:
                self.pause_menu.update(dt)
            return

        if not self.player_locked:
            # Store old position
            old_x = self.player.rect.x
            old_y = self.player.rect.y
            
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.collision_rects, dt)
            
            # Check if player moved
            if (old_x != self.player.rect.x or old_y != self.player.rect.y):
                # Check for wild encounters when moving on grass
                self._check_wild_encounter()
        
        self.camera.update()
        self._check_interactions()

        if self._check_exit():
            self.exit_cave = True
            self.running = False

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_surface.fill((25, 25, 35))
        self._draw_map()

        all_sprites = [('player', self.player)] + [('furniture', s) for s in self.furniture_sprites.sprites()]
        for _, sprite in all_sprites:
            sprite._sort_key = getattr(sprite, 'visual_rect', sprite.rect).bottom
        all_sprites.sort(key=lambda x: x[1]._sort_key)

        for sprite_type, sprite in all_sprites:
            if sprite_type == 'player':
                player_pos = (sprite.visual_rect.centerx - self.camera.offset.x, sprite.visual_rect.centery - self.camera.offset.y)
                self.cave_effects.draw_player_glow(self.game_surface, player_pos)
            sprite.draw(self.game_surface, self.camera)

        if self.debug_mode and self.debugger:
            self.debugger.draw_debug_overlay(self.game_surface, self.player.rect, self.camera.offset, self.furniture_sprites.sprites(), self.collision_rects)

        # Scale to screen FIRST
        scaled = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))
        
        # Apply cave atmosphere AFTER scaling (on screen, not game surface)
        self.cave_effects.apply_cave_atmosphere(self.screen)
        
        # Add dark fantasy filter for extra atmosphere
        self.global_effects.apply_dark_fantasy_filter(self.screen)

        if self.paused and self.pause_menu:
            self.pause_menu.draw(self.screen)

        if not self.paused:
            if self.show_e_prompt and not self.interaction_mode:
                self._draw_e_prompt()
            if self.interaction_mode:
                self._draw_interaction_text()
            if not self.interaction_mode:
                self._draw_atmosphere_text()

        pygame.display.flip()

    def _draw_e_prompt(self):
        font = pygame.font.Font(None, 30)
        text = font.render("[E] Interact", True, (220, 200, 180))
        text_rect = text.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 60)
        bg_rect = text_rect.inflate(30, 15)
        bg = pygame.Surface((bg_rect.width, bg_rect.height))
        bg.fill((20, 18, 25))
        bg.set_alpha(200)
        self.screen.blit(bg, bg_rect)
        pygame.draw.rect(self.screen, (120, 100, 80), bg_rect, 2)
        self.screen.blit(text, text_rect)

    def _draw_interaction_text(self):
        font = pygame.font.Font(None, 28)
        words = self.interaction_text.split(' ')
        lines = []
        current_line = []
        max_width = SCREEN_WIDTH - 200
        
        for word in words:
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
        if current_line:
            lines.append(' '.join(current_line))
        
        line_height = font.get_height() + 8
        text_height = len(lines) * line_height + 80
        box_rect = pygame.Rect((SCREEN_WIDTH - (SCREEN_WIDTH - 160)) // 2, SCREEN_HEIGHT - text_height - 120, SCREEN_WIDTH - 160, text_height)
        
        bg = pygame.Surface((box_rect.width, box_rect.height))
        bg.fill((15, 12, 18))
        bg.set_alpha(245)
        self.screen.blit(bg, box_rect)
        pygame.draw.rect(self.screen, (120, 100, 80), box_rect, 4)
        pygame.draw.rect(self.screen, (80, 70, 60), box_rect.inflate(-8, -8), 2)
        
        y = box_rect.top + 25
        for line in lines:
            text_surf = font.render(line, True, (230, 220, 210))
            self.screen.blit(text_surf, text_surf.get_rect(centerx=box_rect.centerx, top=y))
            y += line_height
        
        hint = pygame.font.Font(None, 24).render("[E] Take    [ESC] Leave" if self.pending_pokeball_take else "[E] or [ESC] to close", True, (180, 160, 140))
        self.screen.blit(hint, hint.get_rect(centerx=box_rect.centerx, bottom=box_rect.bottom - 15))

    def _draw_atmosphere_text(self):
        font = pygame.font.Font(None, 28)
        text = font.render("The darkness is suffocating...", True, (150, 150, 150))
        alpha = int(150 + 50 * abs((pygame.time.get_ticks() / 2000) % 2 - 1))
        text.set_alpha(alpha)
        self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 50)))

    def run(self):
        pygame.event.clear()
        while self.running:
            raw_dt = self.clock.tick(60) / 1000.0
            dt = self.frame_smoother.smooth_dt(raw_dt)
            self.handle_events()
            self.update(dt)
            self.draw()

        # Return appropriate exit info
        if self.return_to_menu:
            return {'return_to_menu': True}
        elif self.exit_cave:
            return {'exit_cave': True}
        elif self.start_battle:
            return {'start_battle': True}
        else:
            return {}

    def cleanup(self):
        if self.save_data:
            self.save_data['progress']['cave_position'] = {'x': self.player.rect.centerx, 'y': self.player.rect.centery}
            self.save_data['progress']['current_scene'] = 'cave'
