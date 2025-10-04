"""
Battle Scene for Pokemon Faiths
Turn-based combat with descriptive states (NO HP BARS)
"""

import pygame
from constants import (
    DEFAULT_SCREEN_WIDTH as SCREEN_WIDTH,
    DEFAULT_SCREEN_HEIGHT as SCREEN_HEIGHT,
    GAME_WIDTH, GAME_HEIGHT
)
from core.logger import get_logger
from core.pokemon import Pokemon
from core.moves import get_move_database, get_type_chart, Move
from core.visual_effects import GlobalEffects
from core.frame_smoother import FrameTimeSmoother
from typing import List, Optional

logger = get_logger('Battle')

class BattleScene:
    """
    Turn-based battle scene
    Key principle: Player sees descriptive states, NOT numbers
    """

    def __init__(self, player_pokemon: Pokemon, enemy_pokemon: Pokemon,
                 screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        # Core pygame setup
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Pokemon Faiths - Battle")
        self.clock = pygame.time.Clock()
        self.running = True

        # Battle participants
        self.player_pokemon = player_pokemon
        self.enemy_pokemon = enemy_pokemon

        # Move database and type chart
        self.move_db = get_move_database()
        self.type_chart = get_type_chart()

        # Battle state
        self.battle_phase = 'move_select'  # 'move_select', 'animating', 'result', 'finished'
        self.selected_move_index = 0
        self.battle_log_entries = []  # For creating final battle log entry
        self.battle_outcome = None  # 'win', 'retreat', 'faint', 'killed'

        # UI state
        self.message = "What will you do?"
        self.message_timer = 0
        self.show_retreat_prompt = False

        # Animation state
        self.animation_timer = 0
        self.animation_duration = 2000  # 2 seconds for attack animation

        # Action menu
        self.action_menu = ['Fight', 'Switch', 'Retreat', 'Info']
        self.action_selected_index = 0
        self.current_menu = 'action'  # 'action' or 'moves'

        # Colors (dark theme)
        self.bg_color = (25, 20, 30)
        self.text_color = (220, 220, 220)
        self.highlight_color = (255, 200, 100)
        self.box_color = (40, 35, 50)
        self.border_color = (200, 200, 200)

        # Player's available moves (for now, get random moves)
        self.player_moves = self._get_pokemon_moves(player_pokemon)
        
        # Visual effects and frame smoothing
        self.global_effects = GlobalEffects(screen_width, screen_height)
        self.frame_smoother = FrameTimeSmoother(max_dt=0.05)

        logger.info(f"Battle started: {player_pokemon.nickname} vs {enemy_pokemon.nickname}")

    def _get_pokemon_moves(self, pokemon: Pokemon) -> List[Move]:
        """Get moves for a Pokemon (for now, random selection)"""
        # TODO: Store moves on Pokemon itself
        return self.move_db.get_random_moves(4)

    def handle_events(self):
        """Handle battle input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received during battle")
                self.running = False
                self.battle_outcome = 'retreat'

            elif event.type == pygame.KEYDOWN:
                if self.battle_phase == 'move_select':
                    self._handle_menu_input(event.key)
                elif self.battle_phase == 'result':
                    # Any key advances from result screen
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
                        self._check_battle_end()

    def _handle_menu_input(self, key):
        """Handle menu navigation"""
        if self.current_menu == 'action':
            # Navigate action menu
            if key == pygame.K_UP or key == pygame.K_w:
                self.action_selected_index = (self.action_selected_index - 1) % len(self.action_menu)
            elif key == pygame.K_DOWN or key == pygame.K_s:
                self.action_selected_index = (self.action_selected_index + 1) % len(self.action_menu)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE or key == pygame.K_e:
                self._execute_action(self.action_menu[self.action_selected_index])

        elif self.current_menu == 'moves':
            # Navigate move menu
            if key == pygame.K_UP or key == pygame.K_w:
                self.selected_move_index = (self.selected_move_index - 1) % len(self.player_moves)
            elif key == pygame.K_DOWN or key == pygame.K_s:
                self.selected_move_index = (self.selected_move_index + 1) % len(self.player_moves)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE or key == pygame.K_e:
                self._execute_player_move()
            elif key == pygame.K_ESCAPE:
                # Back to action menu
                self.current_menu = 'action'
                self.message = "What will you do?"

    def _execute_action(self, action: str):
        """Execute selected action"""
        if action == 'Fight':
            self.current_menu = 'moves'
            self.message = "Choose a move"
        elif action == 'Retreat':
            self._attempt_retreat()
        elif action == 'Switch':
            self.message = "No other Pokemon available!"
            # TODO: Implement party switching
        elif action == 'Info':
            self._show_pokemon_info()

    def _execute_player_move(self):
        """Execute the player's selected move"""
        move = self.player_moves[self.selected_move_index]
        logger.info(f"{self.player_pokemon.nickname} uses {move.name}")

        # Execute player's move
        result = move.execute(self.player_pokemon, self.enemy_pokemon, self.type_chart)

        # Store result
        self.battle_log_entries.append({
            'actor': 'player',
            'move': move.name,
            'result': result
        })

        # Update message
        self.message = result['narrative']
        if result.get('injury_occurred'):
            self.message += f"\n\n{result['injury_description']}"

        # Change to animation phase
        self.battle_phase = 'animating'
        self.animation_timer = 0

    def _execute_enemy_move(self):
        """Enemy AI chooses and executes a move"""
        # Simple AI: random move for now
        import random
        enemy_moves = self._get_pokemon_moves(self.enemy_pokemon)
        move = random.choice(enemy_moves)

        logger.info(f"{self.enemy_pokemon.nickname} uses {move.name}")

        # Execute enemy's move
        result = move.execute(self.enemy_pokemon, self.player_pokemon, self.type_chart)

        # Store result
        self.battle_log_entries.append({
            'actor': 'enemy',
            'move': move.name,
            'result': result
        })

        # Update message
        enemy_message = f"Enemy {self.enemy_pokemon.nickname} used {move.name}!\n"
        enemy_message += result['narrative']

        if result.get('injury_occurred'):
            enemy_message += f"\n\n{result['injury_description']}"

        self.message = enemy_message

    def _attempt_retreat(self):
        """Attempt to retreat from battle"""
        # Check if retreat is safe
        if self.player_pokemon.current_hp_percent < 20:
            self.message = "You carefully retreat, saving your Pokemon from certain death."
        else:
            self.message = "You retreat from battle. Better to preserve life than risk it all."

        logger.info(f"{self.player_pokemon.nickname} retreated from battle")
        self.battle_outcome = 'retreat'
        self.battle_phase = 'finished'
        self.running = False

    def _show_pokemon_info(self):
        """Show information about current Pokemon"""
        injuries = self.player_pokemon._get_injury_descriptions()
        injury_text = f" — {injuries}" if injuries else ""

        info = f"{self.player_pokemon.nickname}\n"
        info += f"State: {self.player_pokemon.get_descriptive_state()}"
        info += injury_text

        self.message = info

    def _check_battle_end(self):
        """Check if battle should end"""
        # Check if player Pokemon fainted/died
        if not self.player_pokemon.is_conscious:
            if self.player_pokemon.is_alive:
                self.battle_outcome = 'faint'
                self.message = f"{self.player_pokemon.nickname} fainted but still breathes..."
            else:
                self.battle_outcome = 'killed'
                self.message = f"{self.player_pokemon.nickname} has fallen... permanently."
            self.battle_phase = 'finished'
            self.running = False
            logger.warning(f"Player Pokemon defeated: {self.battle_outcome}")
            return

        # Check if enemy Pokemon fainted/died
        if not self.enemy_pokemon.is_conscious:
            self.battle_outcome = 'win'
            self.message = f"Enemy {self.enemy_pokemon.nickname} has been defeated!"
            self.battle_phase = 'finished'
            self.running = False
            logger.info("Player won the battle")
            return

        # Continue battle - back to move select
        self.battle_phase = 'move_select'
        self.current_menu = 'action'
        self.message = "What will you do?"

    def update(self, dt):
        """Update battle logic"""
        if self.battle_phase == 'animating':
            self.animation_timer += dt * 1000

            if self.animation_timer >= self.animation_duration:
                # Animation done, check if enemy should attack
                last_entry = self.battle_log_entries[-1]

                if last_entry['actor'] == 'player':
                    # Enemy's turn
                    self._execute_enemy_move()
                    self.animation_timer = 0  # Reset for enemy animation
                else:
                    # Both turns done, show result
                    self.battle_phase = 'result'

    def draw(self):
        """Render battle scene"""
        # Clear
        self.game_surface.fill(self.bg_color)

        # Draw battle background
        self._draw_battle_background()

        # Draw Pokemon (simplified for now - just boxes)
        self._draw_pokemon_representations()

        # Draw state descriptions
        self._draw_state_descriptions()

        # Draw UI based on phase
        if self.battle_phase in ['move_select', 'result']:
            if self.current_menu == 'action':
                self._draw_action_menu()
            elif self.current_menu == 'moves':
                self._draw_move_menu()

        # Draw message box
        self._draw_message_box()

        # Scale to screen
        scaled_surface = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        
        # Apply dark fantasy effects
        self.global_effects.apply_full_effects(self.screen)

        pygame.display.flip()

    def _draw_battle_background(self):
        """Draw simple battle background"""
        # Ground
        pygame.draw.rect(self.game_surface, (60, 50, 40),
                        (0, GAME_HEIGHT // 2, GAME_WIDTH, GAME_HEIGHT // 2))

        # Sky
        pygame.draw.rect(self.game_surface, (40, 35, 55),
                        (0, 0, GAME_WIDTH, GAME_HEIGHT // 2))

    def _draw_pokemon_representations(self):
        """Draw Pokemon (placeholder boxes for now)"""
        # Player Pokemon (bottom left)
        player_box = pygame.Rect(50, GAME_HEIGHT - 120, 80, 80)
        pygame.draw.rect(self.game_surface, (100, 100, 150), player_box)
        pygame.draw.rect(self.game_surface, self.border_color, player_box, 2)

        # Enemy Pokemon (top right)
        enemy_box = pygame.Rect(GAME_WIDTH - 130, 40, 80, 80)
        pygame.draw.rect(self.game_surface, (150, 100, 100), enemy_box)
        pygame.draw.rect(self.game_surface, self.border_color, enemy_box, 2)

        # Draw names
        font = pygame.font.Font(None, 20)

        player_name = font.render(self.player_pokemon.nickname, True, self.text_color)
        self.game_surface.blit(player_name, (player_box.centerx - player_name.get_width() // 2,
                                            player_box.bottom + 5))

        enemy_name = font.render(f"Enemy {self.enemy_pokemon.nickname}", True, self.text_color)
        self.game_surface.blit(enemy_name, (enemy_box.centerx - enemy_name.get_width() // 2,
                                           enemy_box.top - 20))

    def _draw_state_descriptions(self):
        """Draw descriptive state text (NO HP BARS)"""
        font = pygame.font.Font(None, 18)

        # Player Pokemon state
        player_state = self.player_pokemon.get_descriptive_state()
        player_text = font.render(player_state, True, self.text_color)
        self.game_surface.blit(player_text, (10, GAME_HEIGHT - 30))

        # Enemy Pokemon state
        enemy_state = self.enemy_pokemon.get_descriptive_state()
        enemy_text = font.render(enemy_state, True, self.text_color)
        self.game_surface.blit(enemy_text, (GAME_WIDTH - enemy_text.get_width() - 10, 10))

    def _draw_action_menu(self):
        """Draw action selection menu"""
        menu_box = pygame.Rect(GAME_WIDTH - 120, GAME_HEIGHT - 130, 110, 120)
        pygame.draw.rect(self.game_surface, self.box_color, menu_box)
        pygame.draw.rect(self.game_surface, self.border_color, menu_box, 2)

        font = pygame.font.Font(None, 22)
        y_offset = menu_box.top + 10

        for i, action in enumerate(self.action_menu):
            color = self.highlight_color if i == self.action_selected_index else self.text_color
            text = font.render(action, True, color)
            self.game_surface.blit(text, (menu_box.left + 10, y_offset))
            y_offset += 25

    def _draw_move_menu(self):
        """Draw move selection menu"""
        menu_box = pygame.Rect(GAME_WIDTH - 200, GAME_HEIGHT - 130, 190, 120)
        pygame.draw.rect(self.game_surface, self.box_color, menu_box)
        pygame.draw.rect(self.game_surface, self.border_color, menu_box, 2)

        font = pygame.font.Font(None, 20)
        y_offset = menu_box.top + 10

        for i, move in enumerate(self.player_moves):
            color = self.highlight_color if i == self.selected_move_index else self.text_color
            text = font.render(f"{move.name} ({move.move_type})", True, color)
            self.game_surface.blit(text, (menu_box.left + 10, y_offset))
            y_offset += 25

        # ESC hint
        hint_font = pygame.font.Font(None, 16)
        hint = hint_font.render("ESC - Back", True, (150, 150, 150))
        self.game_surface.blit(hint, (menu_box.left + 10, menu_box.bottom - 20))

    def _draw_message_box(self):
        """Draw message/narrative box"""
        box_height = 80
        message_box = pygame.Rect(10, GAME_HEIGHT - box_height - 10, GAME_WIDTH - 140, box_height)
        pygame.draw.rect(self.game_surface, self.box_color, message_box)
        pygame.draw.rect(self.game_surface, self.border_color, message_box, 3)

        # Word wrap message
        font = pygame.font.Font(None, 20)
        lines = self._wrap_text(self.message, font, message_box.width - 20)

        y_offset = message_box.top + 10
        for line in lines[:3]:  # Max 3 lines
            text = font.render(line, True, self.text_color)
            self.game_surface.blit(text, (message_box.left + 10, y_offset))
            y_offset += 22

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit in box"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
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

        return lines

    def run(self):
        """Main battle loop"""
        logger.info("Battle loop started")

        while self.running:
            raw_dt = self.clock.tick(60) / 1000.0
            dt = self.frame_smoother.smooth_dt(raw_dt)
            self.handle_events()
            self.update(dt)
            self.draw()

        logger.info(f"Battle ended: {self.battle_outcome}")
        return self.battle_outcome

    def get_battle_log_entry(self) -> dict:
        """
        Generate battle log entry for Pokemon's battle history
        Format from design doc Section 7
        """
        # Compile moves used
        moves_used = []
        for entry in self.battle_log_entries:
            if entry['actor'] == 'player':
                moves_used.append({
                    'move': entry['move'],
                    'effective': entry['result']['effectiveness'] >= 1.5
                })

        # Calculate total damage taken
        total_damage = 0
        status_events = []
        for entry in self.battle_log_entries:
            if entry['actor'] == 'enemy':
                total_damage += entry['result']['damage']

                # Check for status events
                if entry['result'].get('injury_occurred'):
                    status_events.append('injury')

        # Create log entry
        log_entry = {
            'opponent_id': self.enemy_pokemon.species,
            'opponent_veterancy': self.enemy_pokemon.get_effective_veteran_score() / 100,
            'moves_used': moves_used,
            'damage_taken': {
                'amount': total_damage,
                'type': 'mixed',  # TODO: Track specific types
                'location': 'body'
            },
            'damage_dealt': sum(e['result']['damage'] for e in self.battle_log_entries
                               if e['actor'] == 'player'),
            'status_events': status_events,
            'outcome': self.battle_outcome,
            'player_tactics': [],  # TODO: Analyze tactics from move choices
            'environment': ['training_grounds']  # TODO: Pass environment
        }

        return log_entry
