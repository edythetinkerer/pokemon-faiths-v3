# Pokémon Faiths

A dark Pokémon-style game with atmospheric storytelling, built with Python and Pygame.

## 🎮 Quick Start

```bash
# Install dependencies
pip install pygame

# Run the game
python run.py
```

## ✨ Features

- **Atmospheric Gameplay**: Dark, immersive world with rich storytelling
- **Character System**: Player creation with name and gender selection
- **Interactive Environment**: Explore and interact with objects in detailed scenes
- **Save System**: Persistent game progress with automatic saving
- **Multiple Scenes**: Bedroom, Outside Village, Cave exploration
- **Debug Tools**: Built-in debugging system with F1-F3 hotkeys
- **Smooth Movement**: 8-directional movement with sprint toggle
- **Audio System**: Background music and sound effects

## 🎯 Controls

### Gameplay
| Action | Key(s) |
|--------|--------|
| Move | WASD / Arrow Keys |
| Sprint | Shift (toggle) |
| Interact | E |
| Pause | ESC |
| Fullscreen | F11 |

### Debug (Developer Mode)
| Action | Key |
|--------|-----|
| Toggle Debug Overlay | F1 |
| Take Screenshot | F2 |
| Log Game State | F3 |

### Menu Navigation
- **Arrow Keys**: Navigate options
- **Enter**: Select
- **ESC**: Back/Cancel

## 📁 Project Structure

```
Faith/
├── run.py                 # 🚀 Main launcher (START HERE)
├── src/                   # Source code
│   ├── main.py           # Game entry point
│   ├── constants.py      # Game constants
│   ├── core/             # Core systems
│   │   ├── asset_manager.py   # Asset loading
│   │   ├── audio_manager.py   # Audio system
│   │   ├── save_manager.py    # Save/load
│   │   ├── logger.py          # Logging
│   │   ├── entities.py        # Game entities
│   │   ├── game_debugger.py   # Debug tools
│   │   ├── pause_menu.py      # Pause menu
│   │   ├── settings_menu.py   # Settings
│   │   ├── pokemon.py         # Pokémon system
│   │   └── moves.py           # Battle moves
│   ├── game/             # Game states
│   │   └── states/
│   │       ├── start_screen.py    # Main menu
│   │       ├── intro_sequence.py  # Character creation
│   │       ├── bedroom.py         # Bedroom scene
│   │       ├── outside.py         # Village scene
│   │       ├── cave.py            # Cave scene
│   │       └── battle.py          # Battle system
│   └── ui/               # UI components
│       └── ui_components.py
├── assets/               # Game assets
│   ├── audio/           # Music and SFX
│   ├── images/          # Tiles and objects
│   └── sprites/         # Character sprites
├── data/                # Game data
│   └── saves/           # Save files
├── logs/                # Game logs
├── docs/                # Documentation
│   ├── dev/             # Developer docs
│   └── user/            # User guides
└── tests/               # Test files
```

## 🎨 Game Scenes

### 1. Start Screen
- New Game
- Continue Game
- Settings
- Quit

### 2. Character Creation
- Enter player name
- Select gender
- Begin adventure

### 3. Bedroom
- Interactive furniture
- Examine objects
- Teleport outside

### 4. Outside Village
- Explore village map
- Enter houses
- Access cave

### 5. Cave
- Dark atmosphere
- Find old man's corpse
- Obtain mysterious Pokéball

### 6. Battle System (In Development)
- Turn-based combat
- Pokémon moves
- Type advantages

## 💾 Save System

- **Location**: `data/saves/save_data.json`
- **Auto-save**: On quit and scene transitions
- **Tracks**:
  - Player name and gender
  - Current position in each scene
  - Story progress flags
  - Pokémon party
  - Inventory items

## 🔧 Development

### Adding New Scenes

1. Create scene file in `src/game/states/`:
```python
class NewScene:
    def __init__(self, width, height, save_data=None):
        # Initialize scene
        
    def handle_events(self):
        # Handle input
        
    def update(self, dt):
        # Update logic
        
    def draw(self):
        # Render scene
        
    def run(self):
        # Main game loop
        return {'scene_result': value}
```

2. Add transition logic in `src/main.py`

3. Update save system if needed

### Adding New Assets

1. Place files in appropriate `assets/` subdirectory
2. Load using `get_asset_manager()`:
```python
from core.asset_manager import get_asset_manager

asset_manager = get_asset_manager()
image = asset_manager.load_image('assets/images/my_image.png')
sound = asset_manager.load_sound('assets/audio/sfx/my_sound.wav')
```

### Logging

All modules use the centralized logger:
```python
from core.logger import get_logger

logger = get_logger('MyModule')
logger.info("Something happened")
logger.warning("Something might be wrong")
logger.error("Something went wrong")
```

Logs are saved to `logs/game_YYYYMMDD_HHMMSS.log`

## 🐛 Debugging

### Debug Mode (F1)
- Shows FPS and performance metrics
- Displays collision boxes
- Shows player coordinates
- Camera offset information

### Screenshots (F2)
- Saved to `screenshots/` directory
- Named with timestamp
- Captures current game view

### State Logging (F3)
- Logs detailed game state to console
- Includes all entity positions
- Shows active collision rectangles
- Useful for debugging positioning issues

## 🧪 Testing

```bash
# Run movement tests
python tests/test_movement.py

# Run arrow key tests
python tests/test_arrow_keys.py

# Run battle system tests
python tests/test_battle_system.py
```

## 📚 Documentation

- **Developer Docs**: See `docs/dev/` for technical documentation
  - `ARCHITECTURE.md` - System architecture
  - `QUICK_REFERENCE.md` - Quick reference guide
  - `TODO.md` - Development roadmap
  
- **User Docs**: See `docs/user/` for player guides (coming soon)

## 🚀 Running the Game

### Method 1: Using run.py (Recommended)
```bash
python run.py
```

### Method 2: Using Python module
```bash
python -m src.main
```

### Method 3: Batch file (Windows)
```bash
run_game.bat
```

## 🔧 Technical Details

- **Engine**: Pygame
- **Python Version**: 3.7+
- **Screen Resolution**: 1920x1080 (fullscreen)
- **Internal Resolution**: 680x380 (scaled)
- **Tile Size**: 34x34 pixels
- **FPS Target**: 60
- **Save Format**: JSON
- **Audio**: pygame.mixer (MP3, WAV support)

## 📋 Requirements

- Python 3.7 or higher
- pygame 2.0+

Install with:
```bash
pip install -r requirements.txt
```

## 🐛 Known Issues

None at this time! The game is fully operational.

See `GAME_STATUS.md` for detailed status information.

## 📝 Recent Updates

### Latest (October 3, 2025)
- ✅ Completed project reorganization
- ✅ All files moved to `src/` structure
- ✅ All imports working correctly
- ✅ All game systems tested and operational
- ✅ Cave scene with old man interaction
- ✅ Pokéball pickup mechanic
- ✅ Sprint toggle system

### Previous Updates
- Added outside village scene
- Implemented teleportation system
- Added pause menu with settings
- Created save/load system
- Built character creation sequence

## 🎯 Roadmap

### Version 0.2 (Current)
- [x] Complete file reorganization
- [x] Multiple interconnected scenes
- [x] Save system
- [x] Basic interaction system
- [ ] Complete battle system
- [ ] Add more NPCs

### Version 0.3 (Planned)
- [ ] Quest system
- [ ] Inventory UI
- [ ] More Pokémon species
- [ ] Expanded world map
- [ ] More story content

### Version 1.0 (Future)
- [ ] Complete story campaign
- [ ] Full battle system with all types
- [ ] Trading system
- [ ] Multiple save slots
- [ ] Achievement system

## 🤝 Contributing

This is a personal project, but suggestions and bug reports are welcome!

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- Built with Pygame
- Inspired by Pokémon series
- Created as a dark, atmospheric take on the monster-catching genre

---

**Status**: 🟢 Fully Operational  
**Last Updated**: October 3, 2025  
**Version**: 0.2.0
