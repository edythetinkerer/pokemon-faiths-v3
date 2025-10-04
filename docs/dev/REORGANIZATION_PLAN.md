# Pokémon Faiths - Project Reorganization Plan

## 🎯 Goal
Create a clean, professional project structure that separates:
- **User docs** (README, controls) from **dev docs** (architecture, audits)
- **Source code** from **tests** from **build artifacts**
- **Active logs** from **archived logs**
- **Development** from **production** files

---

## 📁 Proposed New Structure

```
Faith/
│
├── README.md                      # User-facing: Quick start, controls, features
├── LICENSE
├── requirements.txt
├── run_game.bat                   # User convenience script
│
├── src/                           # ✨ NEW - All source code
│   ├── main.py
│   ├── constants.py
│   ├── __init__.py
│   │
│   ├── core/                      # Core game systems
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   ├── pokemon.py
│   │   ├── moves.py
│   │   ├── asset_manager.py
│   │   ├── audio_manager.py
│   │   ├── save_manager.py
│   │   ├── logger.py
│   │   ├── game_debugger.py
│   │   ├── pause_menu.py
│   │   └── settings_menu.py
│   │
│   ├── game/                      # Game-specific code
│   │   ├── __init__.py
│   │   └── states/
│   │       ├── __init__.py
│   │       ├── start_screen.py
│   │       ├── intro_sequence.py
│   │       ├── bedroom.py
│   │       ├── outside.py
│   │       ├── cave.py
│   │       └── battle.py
│   │
│   └── ui/                        # ✨ NEW - UI components
│       ├── __init__.py
│       └── ui_components.py
│
├── tests/                         # ✨ NEW - All test files
│   ├── __init__.py
│   ├── test_battle_system.py
│   ├── test_movement.py
│   ├── test_arrow_keys.py
│   └── README.md                  # Testing instructions
│
├── docs/                          # ✨ NEW - All documentation
│   ├── user/                      # User-facing docs
│   │   ├── CONTROLS.md
│   │   └── FAQ.md
│   │
│   └── dev/                       # Developer documentation
│       ├── ARCHITECTURE.md
│       ├── COMPREHENSIVE_AUDIT.md
│       ├── IMPLEMENTATION_SUMMARY.md
│       ├── NEXT_STEPS.md
│       ├── TODO.md
│       ├── QUICK_REFERENCE.md
│       ├── TESTING_GUIDE.md
│       └── forclaude.txt          # Original design doc
│
├── assets/                        # Game assets (unchanged)
│   ├── audio/
│   ├── images/
│   └── sprites/
│
├── data/                          # ✨ NEW - Runtime data
│   ├── saves/                     # Save files
│   ├── settings.json              # User settings
│   └── .gitkeep
│
├── logs/                          # Log files
│   ├── latest.log                 # ✨ Symlink to most recent
│   ├── archive/                   # ✨ OLD - Old logs moved here
│   │   └── YYYY-MM/               # Organized by month
│   └── .gitignore                 # Ignore all logs in git
│
├── screenshots/                   # Debug screenshots
│   └── .gitignore
│
├── backups/                       # ✨ NEW - Code backups
│   └── entities.py.backup
│
├── build/                         # ✨ NEW - Build artifacts (ignored)
│   ├── dist/                      # Compiled executables
│   └── __pycache__/               # Python cache
│
└── .gitignore                     # Properly ignore build artifacts

```

---

## 🔄 Migration Steps

### Phase 1: Create New Directories ✅
```bash
mkdir src
mkdir src/core
mkdir src/game
mkdir src/game/states
mkdir src/ui
mkdir tests
mkdir docs
mkdir docs/user
mkdir docs/dev
mkdir data
mkdir data/saves
mkdir logs/archive
mkdir backups
mkdir build
```

### Phase 2: Move Source Code 📦
```bash
# Move main files to src/
move main.py src/
move constants.py src/

# Move core systems
move core/*.py src/core/

# Move game states
move game/*.py src/game/
move game/states/*.py src/game/states/

# Move UI components
move ui_components.py src/ui/
```

### Phase 3: Move Documentation 📚
```bash
# Dev docs
move ARCHITECTURE.md docs/dev/
move COMPREHENSIVE_AUDIT.md docs/dev/
move IMPLEMENTATION_SUMMARY.md docs/dev/
move NEXT_STEPS.md docs/dev/
move TODO.md docs/dev/
move QUICK_REFERENCE.md docs/dev/
move TESTING_GUIDE.md docs/dev/
move forclaude.txt docs/dev/

# Extract user docs from README (create separate files)
# Keep README.md in root as main entry point
```

### Phase 4: Move Tests 🧪
```bash
move test_*.py tests/
```

### Phase 5: Move Runtime Data 💾
```bash
move saves/* data/saves/
move settings.json data/
```

### Phase 6: Clean Up Logs 🧹
```bash
# Move old logs to archive
move logs/game_202510*.log logs/archive/2025-10/
```

### Phase 7: Move Backups 🗄️
```bash
move *.backup backups/
move settings_menu.py backups/  # Duplicate file
```

### Phase 8: Update Import Paths 🔧
**Critical:** All imports need to be updated after moving files.

Before:
```python
from core.entities import Player
from constants import TILE_SIZE
```

After:
```python
from src.core.entities import Player
from src.constants import TILE_SIZE
```

---

## 📝 Files to Update

### 1. `main.py` → `src/main.py`
Update all imports:
```python
# Old imports
from constants import *
from core.logger import init_logger
from game.states.start_screen import PokemonStartScreen

# New imports
from src.constants import *
from src.core.logger import init_logger
from src.game.states.start_screen import PokemonStartScreen
```

### 2. All scene files (bedroom.py, outside.py, etc.)
Update:
```python
# Old
from constants import TILE_SIZE
from core.asset_manager import get_asset_manager

# New
from src.constants import TILE_SIZE
from src.core.asset_manager import get_asset_manager
```

### 3. `asset_manager.py`
Update base path calculation for new structure:
```python
def _get_base_path(self) -> str:
    """Get the correct base path for assets"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        # Go up from src/ to project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

### 4. `save_manager.py`
Update save directory path:
```python
SAVE_DIR = 'data/saves'  # Was 'saves'
```

### 5. `logger.py`
Update log directory path:
```python
LOG_DIR = 'logs'  # Stays the same, but we'll clean it
```

---

## 🎯 Benefits of New Structure

### For Development
✅ **Clear separation** - Know exactly where everything belongs  
✅ **No clutter** - Backups, tests, docs all organized  
✅ **Professional** - Follows Python best practices  
✅ **Scalable** - Easy to add new modules  

### For Collaboration
✅ **Easy onboarding** - New devs can navigate instantly  
✅ **Clear docs** - Dev vs user docs separated  
✅ **Git-friendly** - .gitignore handles build artifacts  

### For Distribution
✅ **Clean builds** - All source in `src/`  
✅ **Data isolation** - User data in `data/`  
✅ **Asset packaging** - `assets/` stays clean  

---

## 🔒 Updated .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Game Data
data/saves/*.json
!data/saves/.gitkeep
logs/**/*.log
!logs/latest.log
screenshots/*.png

# OS
.DS_Store
Thumbs.db

# Backups
backups/*.backup
*~

# Settings (user-specific)
data/settings.json
```

---

## 📋 Checklist for Reorganization

- [ ] **Backup everything first!** (ZIP the entire project)
- [ ] Create all new directories
- [ ] Move source files to `src/`
- [ ] Move docs to `docs/dev/` and `docs/user/`
- [ ] Move tests to `tests/`
- [ ] Move data to `data/`
- [ ] Archive old logs to `logs/archive/`
- [ ] Move backups to `backups/`
- [ ] Update ALL import statements
- [ ] Update path references (saves, logs, assets)
- [ ] Test that game still runs
- [ ] Test that saves still load
- [ ] Test that logs still write
- [ ] Update README.md with new structure
- [ ] Create .gitignore
- [ ] Commit changes to git

---

## 🎨 Additional Organization Ideas

### 1. Create Development Scripts
```bash
scripts/
├── run.py              # Launch game with proper paths
├── test_all.py         # Run all tests
├── clean_logs.py       # Archive old logs
└── build.py            # Build executable
```

### 2. Configuration Files
```bash
config/
├── development.json    # Dev settings
├── production.json     # Release settings
└── testing.json        # Test configuration
```

### 3. Documentation Index
Create `docs/README.md`:
```markdown
# Documentation Index

## For Users
- [Controls](user/CONTROLS.md) - How to play
- [FAQ](user/FAQ.md) - Common questions

## For Developers
- [Architecture](dev/ARCHITECTURE.md) - System design
- [Quick Reference](dev/QUICK_REFERENCE.md) - Fast lookup
- [TODO](dev/TODO.md) - What needs doing
- [Testing Guide](dev/TESTING_GUIDE.md) - How to test
```

---

## 🚀 After Reorganization

**New developer experience:**
```bash
# Clone project
git clone your-repo

# Install dependencies
pip install -r requirements.txt

# Read user docs
cat README.md

# Read dev docs
cat docs/dev/QUICK_REFERENCE.md

# Run game
python src/main.py

# Run tests
python -m pytest tests/

# Build executable
python scripts/build.py
```

**Clean, professional, organized!**

---

## ⏱️ Time Estimate

**Manual reorganization:** 2-3 hours  
**With automated script:** 30 minutes  
**Testing after migration:** 1 hour  

**Total:** ~4 hours for a professional, maintainable structure

---

## 💡 Recommendation

**Don't reorganize yet!** 

Wait until after you implement wild encounters and get the game playable. Here's why:

1. **You're only 2 days in** - Structure can wait
2. **Core gameplay is more important** - Get it working first
3. **Major refactoring now = risk** - Might break things
4. **Better to organize when stable** - Less moving targets

**Better plan:**
- Implement wild encounters this week (game becomes playable)
- Reorganize next week when code stabilizes
- Use this document as your guide when ready

---

**However, if you want to organize NOW, I can help you do it safely!**

Want me to:
1. Create an automated migration script?
2. Update all the import paths for you?
3. Generate the new directory structure?

Just let me know! 🚀
