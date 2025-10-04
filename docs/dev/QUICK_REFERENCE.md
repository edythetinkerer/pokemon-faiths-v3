# 🎮 Pokémon Faiths - Quick Reference Card

## 📁 Project Files

**Documentation:**
- `README.md` - Project overview & controls
- `ARCHITECTURE.md` - System design with diagrams
- `forclaude.txt` - Complete design vision (39KB!)
- `COMPREHENSIVE_AUDIT.md` - Full code analysis & fixes
- `NEXT_STEPS.md` - Detailed implementation guide
- `TODO.md` - Clean task list
- `IMPLEMENTATION_SUMMARY.md` - What's done so far

**Core Systems:**
- `main.py` - Game loop & state machine
- `constants.py` - All game constants (ADJUST SPEEDS HERE!)
- `core/pokemon.py` - Veteran System ⭐
- `core/moves.py` - Move database & type chart
- `core/entities.py` - Player, Camera, GameObject
- `core/save_manager.py` - Save/load system
- `core/asset_manager.py` - Image/audio caching

**Scenes:**
- `game/states/start_screen.py` - Cinematic candle menu
- `game/states/intro_sequence.py` - Character creation
- `game/states/bedroom.py` - Indoor area (cleaned up!)
- `game/states/outside.py` - Village with houses
- `game/states/cave.py` - Dark cave with old man
- `game/states/battle.py` - Turn-based combat

---

## 🎯 What to Build Next (Priority Order)

1. **Wild Encounter System** - `core/wild_encounters.py`
2. **Battle Integration** - Connect encounters to battles
3. **Starter Pokemon** - Create on first battle
4. **Cave Veteran** - Reward for taking pokéball
5. **Catch Mechanic** - Add to battle menu

**Full implementation code provided in `COMPREHENSIVE_AUDIT.md`**

---

## 🔧 Quick Fixes

### Make Movement Feel Better
**File:** `constants.py`
```python
PLAYER_SPEED = 2.2  # Change from 1.4
ANIMATION_SPEED = 0.20  # Change from 0.15
```

### Enable Smooth Camera
**File:** `core/entities.py` (in Camera.__init__)
```python
self.smoothing = True
self.smoothing_speed = 5.0
```

---

## 🎮 Controls

**Movement:** WASD or Arrow Keys  
**Sprint:** Hold Shift  
**Interact:** E  
**Pause:** ESC  
**Debug:** F1  
**Screenshot:** F2  
**Log State:** F3  
**Fullscreen:** F11  

---

## 🏗️ Architecture Quick Reference

### Game Flow
```
Start Screen → Character Creation → Bedroom
                                    ↓
                              Outside ↔ Cave
                                    ↓
                              Wild Encounters
                                    ↓
                               Battle Scene
                                    ↓
                         Return to Exploration
```

### Battle System
```
Player Pokemon ←→ Battle Scene ←→ Enemy Pokemon
       ↓              ↓                ↓
  Move Selection   Execute        AI Decision
       ↓              ↓                ↓
   Damage Calc → Descriptive → Injury Check
                   States
       ↓
  Battle Log Entry → Veteran Score Update
```

### Save Data Structure
```json
{
  "player": {
    "name": "string",
    "gender": "string"
  },
  "pokemon": {
    "party": [
      {
        "id": 1,
        "species": "Charmander",
        "nickname": "Charmy",
        "age": 1,
        "battle_log": [],
        "injuries": [],
        "has_vos": false
      }
    ]
  },
  "progress": {
    "current_scene": "bedroom",
    "bedroom_position": {"x": 204, "y": 204},
    "bedroom_visited": true
  }
}
```

---

## 🐛 Debug Commands

**F1** - Toggle debug overlay (shows FPS, collisions, positions)  
**F2** - Take screenshot (saved to `/screenshots/`)  
**F3** - Log game state to console & log file  

**View logs:** Check `/logs/` directory

---

## 📊 Key Metrics

**Total Lines:** ~8,500  
**Development Time:** 2 days (as of Oct 3, 2025)  
**Core Systems:** 100% complete ✅  
**Content:** 10% complete  
**Polish:** 30% complete  

**Time to Playable:** ~1 week  
**Time to Demo:** ~2-3 weeks  

---

## 💡 Quick Tips

1. **Always test after changes** - Run the game frequently
2. **Use the logger** - Helps debug issues quickly
3. **Check the audit** - Full code examples for every feature
4. **Start simple** - Get it working, polish later
5. **Playtest yourself** - Trust your own feel

---

## 🎨 Design Principles

1. **Consequence > Convenience** - Every choice matters
2. **Player Skill = Progression** - Not grinding
3. **Survival First** - Retreat is valid
4. **History Shapes Identity** - Battle log tells stories
5. **Interaction-First** - Active engagement always

---

## 🔥 Core Innovation: Veteran System

**Instead of XP/Levels:**
- Circular battle log (max 200 entries)
- Exponential decay (recent battles matter most)
- Score = (Combat Exp + Adaptation) - (Trauma + Injuries)
- Permanent injuries never decay
- Dual progression: Can get stronger AND weaker

**This is what makes your game unique!**

---

## 📚 Where to Find Help

**Code Examples:** `COMPREHENSIVE_AUDIT.md`  
**Implementation Guide:** `NEXT_STEPS.md`  
**Task List:** `TODO.md`  
**Design Philosophy:** `forclaude.txt`  
**What's Done:** `IMPLEMENTATION_SUMMARY.md`  

---

## 🚀 Quick Start Command

```bash
python main.py
```

**Or double-click:** `run_game.bat`

---

## ⚠️ Common Issues & Solutions

### "Asset not found" errors
**Fix:** Check `assets/` folder structure matches code paths

### Movement feels sluggish
**Fix:** Change `PLAYER_SPEED` to 2.2 in `constants.py`

### Battle doesn't start from encounters
**Fix:** Not implemented yet - see `COMPREHENSIVE_AUDIT.md` Fix #1

### Cave pokéball does nothing
**Fix:** Not implemented yet - see `COMPREHENSIVE_AUDIT.md` Fix #3

### Save file corrupted
**Fix:** Delete `saves/save_data.json` and start fresh

---

## 🎯 Current Status Summary

### ✅ WORKING
- Core Veteran System (battle logging, injuries, scores)
- Turn-based battle scene (complete UI, no HP bars)
- Three connected areas (Bedroom → Outside → Cave)
- Save/load system with position tracking
- Player movement and collision
- Interaction system
- Pause menu with settings
- Asset caching
- Debug tools
- Atmospheric UI and effects

### ⚠️ NEEDS WORK
- Wild encounter system (not implemented)
- Battle integration into main loop (not connected)
- Catch mechanic (not implemented)
- Party management (basic structure only)
- Starter Pokémon creation (not implemented)
- Cave veteran reward (flags work, no Pokemon given)
- Movement speed (too slow, easy fix)

### 🔮 PLANNED
- More wild Pokémon species
- Item system (Potions, Pokéballs)
- Party UI
- Move expansion (20-30 total)
- NPC trainers
- More areas to explore
- VoS (Will of Struggler) acquisition
- Prosthetics system

---

## 💾 Save File Locations

**Save Data:** `saves/save_data.json`  
**Logs:** `logs/game_YYYYMMDD_HHMMSS.log`  
**Screenshots:** `screenshots/`  
**Settings:** `settings.json`  

---

## 🎨 Customization Quick Reference

### Adjust Movement Speed
**File:** `constants.py`
```python
PLAYER_SPEED = 2.2  # Higher = faster
SPRINT_MULTIPLIER = 1.5  # Sprint boost
```

### Change Encounter Rate
**File:** `core/wild_encounters.py` (when created)
```python
base_encounter_rate = 0.05  # 5% per step
```

### Adjust Injury Thresholds
**File:** `core/pokemon.py`
```python
INJURY_THRESHOLD_MINOR = 60
INJURY_THRESHOLD_MAJOR = 80
INJURY_THRESHOLD_CATASTROPHIC = 95
```

### Battle Log Size
**File:** `core/pokemon.py`
```python
MAX_BATTLE_LOG_SIZE = 200  # Circular buffer size
RECENT_BATTLES_WEIGHT = 50  # How many battles matter most
```

---

## 🧪 Testing Checklist

Before implementing a feature, test:
- [ ] Does it run without errors?
- [ ] Does it integrate with saves?
- [ ] Does it work after reload?
- [ ] Is logging working properly?
- [ ] Does it feel good to the player?

---

## 📝 Code Style Notes

- **Logging:** Use `logger.info()`, `logger.warning()`, `logger.error()`
- **Constants:** ALL_CAPS in `constants.py`
- **Asset Loading:** Always use `get_asset_manager()`
- **Save/Load:** Always use `get_save_manager()`
- **Error Handling:** Try/except with logger for all I/O
- **Comments:** Explain WHY, not WHAT

---

## 🎮 Playtesting Focus Areas

When testing, focus on:
1. **Feel** - Is movement responsive?
2. **Clarity** - Are descriptive states clear?
3. **Consequence** - Do injuries feel meaningful?
4. **Progression** - Does Veteran Score change noticeably?
5. **Story** - Do battles create emergent narratives?

---

## 🏆 Success Criteria

**Minimum Viable Game (Week 1):**
- Player can explore 3 areas
- Wild encounters work
- Battles are winnable
- Can catch 1-2 Pokémon
- Save/load preserves progress
- Veteran Score changes over time

**Demo Ready (Week 3):**
- 15+ minute gameplay loop
- Party of 3-4 Pokémon buildable
- Injuries create stories
- Movement feels polished
- Cave veteran reward works
- 10+ wild species

**Full Release (2-3 months):**
- Multiple areas to explore
- NPC trainers
- Complete Pokédex (20-30 species)
- VoS system
- Item crafting
- Rich environmental storytelling

---

## 🚨 Critical Rules

1. **Never show HP numbers** - Always use descriptive text
2. **Every battle matters** - Update battle log after each fight
3. **Injuries are permanent** - No revives, no healing major injuries
4. **Death is final** - No Phoenix Downs
5. **Retreat is valid** - Not a failure, a survival tactic
6. **History shapes identity** - Battle log tells each Pokémon's story

---

## 💪 Your Unique Selling Points

1. **No grinding** - Skill-based progression
2. **Dual progression** - Can get stronger AND weaker
3. **Emergent storytelling** - Every Pokémon tells unique tale
4. **Real consequences** - Injuries and death are permanent
5. **No numbers** - Descriptive states create immersion
6. **Dark atmosphere** - Mature, survival-focused tone

**These are what make Pokémon Faiths special!**

---

## 🔗 Important Links

All code examples: `COMPREHENSIVE_AUDIT.md`  
Implementation guide: `NEXT_STEPS.md`  
Task breakdown: `TODO.md`  
Design vision: `forclaude.txt`  

---

**Last Updated:** October 3, 2025  
**Project Status:** Foundation Complete, Building Gameplay  
**Next Milestone:** Wild Encounters + Battle Integration  

---

## 🎉 You've Got This!

Your foundation is **rock solid**. The Veteran System is genuinely innovative. The battle system works perfectly. All the hard architectural decisions are done.

Now it's just about connecting the pieces and adding content.

**Start with wild encounters. Everything else flows from there.**

Good luck! 🚀
