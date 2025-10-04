"""
Centralized Logging System for Pokemon Faiths
Provides consistent logging across all game modules
"""

import logging
import os
from datetime import datetime

class GameLogger:
    """Centralized logging system for the game"""
    
    def __init__(self, log_to_file=True, log_level=logging.INFO):
        self.logger = logging.getLogger('PokemonFaiths')
        self.logger.setLevel(log_level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Console handler with color-coded formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(levelname)-8s | %(name)-15s | %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_to_file:
            try:
                os.makedirs('logs', exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                log_file = os.path.join('logs', f'game_{timestamp}.log')
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)  # File gets everything
                file_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
                
                self.logger.info(f"Logging to file: {log_file}")
            except Exception as e:
                self.logger.warning(f"Could not create log file: {e}")
    
    def get_logger(self, module_name):
        """Get a logger for a specific module"""
        return logging.getLogger(f'PokemonFaiths.{module_name}')

# Global logger instance
_game_logger = None

def init_logger(log_to_file=True, log_level=logging.INFO):
    """Initialize the global logger"""
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger(log_to_file, log_level)
    return _game_logger

def get_logger(module_name='Core'):
    """Get a logger for a specific module"""
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger()
    return _game_logger.get_logger(module_name)

