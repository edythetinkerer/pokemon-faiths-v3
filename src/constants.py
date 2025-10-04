"""
Game Constants for Pokemon Faiths
Centralized configuration to avoid hardcoding values across files
"""

from typing import Tuple

# Screen Settings
DEFAULT_SCREEN_WIDTH = 1366
DEFAULT_SCREEN_HEIGHT = 768
FPS = 60

# Tile Settings
TILE_SIZE = 34
PLAYER_SIZE = 48
PLAYER_SPEED = 1.4

# Game Surface Settings (for bedroom scene)
GAME_WIDTH = 480
GAME_HEIGHT = 270

# Animation Constants
ANIMATION_SPEED = 0.15
PARTICLE_SPAWN_INTERVAL = 0.1
PARTICLE_MAX_COUNT = 75

# UI Constants
BUTTON_BORDER_RADIUS = 10
VIGNETTE_INTENSITY = 0.8
GLOW_BORDER_RADIUS = 15

# Timing Constants (previously magic numbers)
EYE_OPENING_DURATION = 3000  # 3 seconds in milliseconds
FADE_SPEED = 2.0
TEXT_SPEED = 2  # Characters per frame
MAX_NAME_CHARS = 12

# Flame Animation Constants
FLAME_BASE_HEIGHT = 120
FLAME_HEIGHT_VARIATION = 40
FLAME_BASE_WIDTH = 80
FLAME_WIDTH_VARIATION = 20
BEAT_INTERVAL = 1.2  # Seconds
BEAT_AMPLITUDE = 8   # Pixels

# Candle Constants
CANDLE_WIDTH = 300
CANDLE_HEIGHT = 800
WICK_HEIGHT = 30
WICK_WIDTH = 6

# Elder Animation Constants
ELDER_BOB_SPEED = 1.5
ELDER_BOB_AMPLITUDE = 3

# Player Movement Constants (for bedroom scene)
PLAYER_COLLISION_WIDTH = 12
PLAYER_COLLISION_HEIGHT = 8
PLAYER_VISUAL_SIZE = 48

# Collision and Wall Constants
WALL_THICKNESS = 8
COLLISION_INSET = 8
DOORWAY_WIDTH = 16
BORDER_THICKNESS = 5

# Interaction System Constants
INTERACTION_RANGE_DEFAULT = 35
INTERACTION_TEXT_AUTO_CLOSE_TIME = 5.0
INTERACTION_PROMPT_Y_OFFSET = 60

# House Collision Constants
HOUSE_WALL_THICKNESS = 3
HOUSE_COLLISION_INSET = 8
HOUSE_DOORWAY_WIDTH = 16

# Scene Transition Constants
FADE_DURATION = 0.5
SCENE_TRANSITION_SPEED = 2.0

def validate_screen_dimensions(width: int, height: int) -> bool:
    """Validate screen dimensions are reasonable"""
    return 640 <= width <= 7680 and 480 <= height <= 4320

def validate_volume(volume: float) -> bool:
    """Validate audio volume is in valid range"""
    return 0.0 <= volume <= 1.0

# Color Themes
class Colors:
    # Dark atmospheric theme
    BACKGROUND_TOP = (5, 2, 8)
    BACKGROUND_BOTTOM = (20, 10, 15)
    
    # UI Colors
    TEXT_PRIMARY = (200, 170, 140)
    TEXT_SECONDARY = (150, 140, 130)
    TEXT_DARK = (100, 80, 60)
    
    # Button Colors
    BUTTON_NORMAL = (100, 80, 60)
    BUTTON_HOVER = (200, 170, 140)
    BUTTON_TEXT_NORMAL = (200, 170, 140)
    BUTTON_TEXT_HOVER = (20, 10, 15)
    
    # Candle Colors
    CANDLE_WAX = (180, 165, 150)
    CANDLE_WICK = (20, 15, 10)
    FLAME_CORE = (255, 255, 200)
    FLAME_MID = (255, 160, 80)
    FLAME_OUTER = (255, 80, 20)

# Audio Settings
class Audio:
    MUSIC_VOLUME = 0.3
    SFX_VOLUME = 0.5

# Battle System Constants
BATTLE_TRANSITION_SPEED = 1.5
BATTLE_TEXT_SPEED = 50  # Characters per second
BATTLE_MOVE_ANIMATION_DURATION = 1.0

# Veteran System Constants
MAX_BATTLE_LOG_SIZE = 200
DECAY_RATE = 0.95  # Exponential decay per battle
INJURY_THRESHOLD_MAJOR = 0.5  # 50% damage in one hit
INJURY_THRESHOLD_CATASTROPHIC = 0.75  # 75% damage

# Will of the Struggler
VOS_PROBABILITY = 0.0000001  # 1 in 10 million
VOS_BOND_THRESHOLD = 50  # Minimum bond strength
VOS_BATTLES_REQUIRED = 50  # Minimum battles together