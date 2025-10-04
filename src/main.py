#!/usr/bin/env python3
"""
Pokemon Faiths - Main Launcher
A dark Pokemon-style game with atmospheric storytelling
"""

import pygame
import sys
from constants import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT
from core.logger import init_logger, get_logger
from core.save_manager import get_save_manager

# Initialize logging system
init_logger(log_to_file=True)
logger = get_logger('Main')

class GameStateManager:
    """Manages game state transitions and error handling"""
    
    def __init__(self):
        self.screen_width = DEFAULT_SCREEN_WIDTH
        self.screen_height = DEFAULT_SCREEN_HEIGHT
        self.save_manager = get_save_manager()
        
    def initialize_pygame(self):
        """Initialize pygame systems with proper error handling"""
        try:
            pygame.init()
            pygame.mixer.init()
            logger.info("Pygame initialized successfully")
            return True
        except pygame.error as e:
            logger.error(f"Failed to initialize pygame: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during pygame initialization: {e}")
            return False
    
    def run_start_screen(self):
        """Run the start screen and return user choice"""
        try:
            from game.states.start_screen import PokemonStartScreen
            start_screen = PokemonStartScreen()
            return start_screen.run()
        except ImportError as e:
            logger.error(f"Failed to import start screen module: {e}")
            return None
        except pygame.error as e:
            logger.error(f"Pygame error in start screen: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in start screen: {e}")
            return None
    
    def run_intro_sequence(self):
        """Run character creation sequence"""
        try:
            from game.states.intro_sequence import IntroSequence
            intro = IntroSequence(self.screen_width, self.screen_height)
            return intro.run()
        except ImportError as e:
            logger.error(f"Failed to import intro sequence module: {e}")
            return None
        except pygame.error as e:
            logger.error(f"Pygame error in intro sequence: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in intro sequence: {e}")
            return None
    
    def run_bedroom_scene(self, save_data=None):
        """Run the bedroom gameplay scene"""
        try:
            from game.states.bedroom import BedroomScene
            bedroom = BedroomScene(self.screen_width, self.screen_height, save_data)
            result = bedroom.run()
            bedroom.cleanup()  # Cleanup resources
            return result
        except ImportError as e:
            logger.error(f"Failed to import bedroom scene module: {e}")
            return False
        except pygame.error as e:
            logger.error(f"Pygame error in bedroom scene: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in bedroom scene: {e}")
            return False
    
    def run_outside_scene(self, save_data=None):
        """Run the outside gameplay scene"""
        try:
            from game.states.outside import OutsideScene
            player_name = save_data['player']['name'] if save_data else "Player"
            outside = OutsideScene(self.screen_width, self.screen_height, save_data, player_name)
            result = outside.run()
            outside.cleanup()  # Cleanup resources
            return result
        except ImportError as e:
            logger.error(f"Failed to import outside scene module: {e}")
            return False
        except pygame.error as e:
            logger.error(f"Pygame error in outside scene: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in outside scene: {e}")
            return False

    def run_cave_scene(self, save_data=None):
        """Run the cave gameplay scene"""
        try:
            from game.states.cave import CaveScene
            player_name = save_data['player']['name'] if save_data else "Player"
            cave = CaveScene(self.screen_width, self.screen_height, save_data, player_name)
            result = cave.run()
            cave.cleanup()  # Cleanup resources
            return result
        except ImportError as e:
            logger.error(f"Failed to import cave scene module: {e}")
            return {'error': True}
        except pygame.error as e:
            logger.error(f"Pygame error in cave scene: {e}")
            return {'error': True}
        except Exception as e:
            logger.error(f"Unexpected error in cave scene: {e}")
            return {'error': True}
    
    def run_battle_scene(self, save_data=None):
        """Run the battle scene"""
        try:
            from game.states.battle import BattleScene
            from core.pokemon import Pokemon
            
            # Get battle data from save
            if not save_data or 'battle' not in save_data:
                logger.error("No battle data found!")
                return {'error': True}
            
            battle_data = save_data['battle']
            
            # Get player's first Pokemon
            if 'party' not in save_data or len(save_data['party']) == 0:
                logger.error("Player has no Pokemon!")
                return {'error': True}
            
            player_pokemon_data = save_data['party'][0]
            enemy_pokemon_data = battle_data['opponent']
            
            # Create Pokemon objects (this game uses Veteran System, not levels)
            player_pokemon = Pokemon(
                species=player_pokemon_data['name'],
                nickname=player_pokemon_data.get('nickname', player_pokemon_data['name'])
            )
            # Set HP
            player_pokemon.current_hp_percent = (player_pokemon_data['hp'] / player_pokemon_data['max_hp']) * 100
            
            enemy_pokemon = Pokemon(
                species=enemy_pokemon_data['name'],
                nickname=enemy_pokemon_data['name']
            )
            enemy_pokemon.current_hp_percent = 100
            
            # Start battle
            battle = BattleScene(player_pokemon, enemy_pokemon, self.screen_width, self.screen_height)
            battle_outcome = battle.run()
            
            # Update player Pokemon HP in save
            new_hp = int((player_pokemon.current_hp_percent / 100) * player_pokemon_data['max_hp'])
            save_data['party'][0]['hp'] = max(0, new_hp)
            
            # Clear battle data
            if 'battle' in save_data:
                del save_data['battle']
            
            self.save_manager.save_game(save_data)
            
            logger.info(f"Battle ended with outcome: {battle_outcome}")
            return {'battle_outcome': battle_outcome}
            
        except Exception as e:
            logger.error(f"Battle error: {e}", exc_info=True)
            return {'error': True}

def main():
    """Main entry point for Pokemon Faiths"""
    logger.info("=== Pokemon Faiths Starting ===")
    game_manager = GameStateManager()
    
    # Initialize pygame with error handling
    if not game_manager.initialize_pygame():
        logger.critical("Failed to initialize game systems")
        return 1

    # Load settings
    try:
        from core.settings_menu import load_settings_on_startup
        load_settings_on_startup()
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")

    try:
        # Main menu loop - allows returning to start screen
        main_menu_active = True

        while main_menu_active:
            # Run start screen
            result = game_manager.run_start_screen()

            # Handle user choice with specific error handling
            if result == "new_game":
                logger.info("Starting new game...")
                # Run character creation
                player_data = game_manager.run_intro_sequence()

                if player_data:
                    logger.info(f"Character created: {player_data['name']}")
                
                    # Create save file
                    save_data = game_manager.save_manager.create_new_save(
                        player_data['name'], 
                        player_data['gender']
                    )
                
                    if save_data:
                        logger.info("Save file created, starting game loop...")
                        # Game loop - teleport between bedroom and outside
                        current_scene = 'bedroom'
                        game_running = True
                    
                        while game_running:
                            if current_scene == 'bedroom':
                                result = game_manager.run_bedroom_scene(save_data)
                                if result.get('return_to_menu'):
                                    logger.info("Returning to main menu...")
                                    game_running = False
                                    # Stay in main_menu_active loop
                                elif result.get('teleport_outside'):
                                    logger.info("Teleporting to outside scene...")
                                    current_scene = 'outside'
                                else:
                                    # Player closed window
                                    game_running = False
                                    main_menu_active = False  # Exit completely
                        
                            elif current_scene == 'outside':
                                result = game_manager.run_outside_scene(save_data)
                                if result.get('return_to_menu'):
                                    logger.info("Returning to main menu...")
                                    game_running = False
                                    # Stay in main_menu_active loop
                                elif result.get('return_to_bedroom'):
                                    logger.info("Returning to bedroom...")
                                    current_scene = 'bedroom'
                                elif result.get('enter_cave'):
                                    logger.info("Entering cave...")
                                    current_scene = 'cave'
                                else:
                                    # Player closed window
                                    game_running = False
                                    main_menu_active = False  # Exit completely

                            elif current_scene == 'cave':
                                result = game_manager.run_cave_scene(save_data)
                                if result.get('return_to_menu'):
                                    logger.info("Returning to main menu...")
                                    game_running = False
                                    # Stay in main_menu_active loop
                                elif result.get('exit_cave'):
                                    logger.info("Exiting cave...")
                                    current_scene = 'outside'
                                elif result.get('start_battle'):
                                    logger.info("Starting battle from cave...")
                                    # Run battle
                                    battle_result = game_manager.run_battle_scene(save_data)
                                    if battle_result.get('error'):
                                        logger.error("Battle error, returning to cave")
                                    # After battle, return to cave
                                    current_scene = 'cave'
                                else:
                                    # Player closed window
                                    game_running = False
                                    main_menu_active = False  # Exit completely
                    else:
                        logger.error("Failed to create save file")
                        return 1
                else:
                    logger.info("Character creation was cancelled or failed")
                
            elif result == "continue":
                logger.info("Loading saved game...")
                save_data = game_manager.save_manager.load_game()
            
                if save_data:
                    logger.info(f"Loaded save for: {save_data['player']['name']}")
                
                    # Determine starting scene from save
                    current_scene = save_data.get('progress', {}).get('current_scene', 'bedroom')
                    game_running = True
                
                    while game_running:
                        if current_scene == 'bedroom':
                            result = game_manager.run_bedroom_scene(save_data)
                            if result.get('return_to_menu'):
                                logger.info("Returning to main menu...")
                                game_running = False
                                # Stay in main_menu_active loop
                            elif result.get('teleport_outside'):
                                logger.info("Teleporting to outside scene...")
                                current_scene = 'outside'
                            else:
                                # Player closed window
                                game_running = False
                                main_menu_active = False  # Exit completely

                        elif current_scene == 'outside':
                            result = game_manager.run_outside_scene(save_data)
                            if result.get('return_to_menu'):
                                logger.info("Returning to main menu...")
                                game_running = False
                                # Stay in main_menu_active loop
                            elif result.get('return_to_bedroom'):
                                logger.info("Returning to bedroom...")
                                current_scene = 'bedroom'
                            elif result.get('enter_cave'):
                                logger.info("Entering cave...")
                                current_scene = 'cave'
                            else:
                                # Player closed window
                                game_running = False
                                main_menu_active = False  # Exit completely

                        elif current_scene == 'cave':
                            result = game_manager.run_cave_scene(save_data)
                            if result.get('return_to_menu'):
                                logger.info("Returning to main menu...")
                                game_running = False
                                # Stay in main_menu_active loop
                            elif result.get('exit_cave'):
                                logger.info("Exiting cave...")
                                current_scene = 'outside'
                            elif result.get('start_battle'):
                                logger.info("Starting battle from cave...")
                                # Run battle
                                battle_result = game_manager.run_battle_scene(save_data)
                                if battle_result.get('error'):
                                    logger.error("Battle error, returning to cave")
                                # After battle, return to cave
                                current_scene = 'cave'
                            else:
                                # Player closed window
                                game_running = False
                                main_menu_active = False  # Exit completely
                else:
                    logger.error("Failed to load save file")
                
            elif result == "settings":
                logger.warning("Settings returned without action")
            elif result is None:
                # User quit from start screen
                logger.info("Game quit by user")
                main_menu_active = False
            else:
                logger.warning(f"Unknown result from start screen: {result}")
                main_menu_active = False
            
    except KeyboardInterrupt:
        logger.info("Game interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.critical(f"Critical unexpected error: {e}", exc_info=True)
        return 1
    finally:
        # Clean shutdown
        try:
            pygame.quit()
            logger.info("=== Pokemon Faiths Shutdown ===")
        except:
            pass  # Ignore errors during cleanup
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
