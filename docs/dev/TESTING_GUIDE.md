# Testing Guide - Pokémon Faiths Battle System

## Quick Start

### Run the Game
```bash
python main.py
```

### Run Automated Tests
```bash
python test_battle_system.py
```

---

## In-Game Testing Flow

### 1. Start New Game
- Choose "New Game" from start screen
- Create your character (any name/gender)
- Skip/watch intro sequence

### 2. Bedroom Scene
- You spawn in the bedroom
- **Controls:**
  - `WASD` / `Arrow Keys` - Move
  - `E` - Interact with objects
  - `ESC` - Pause menu
  - `F1` - Debug mode (shows collision boxes)

### 3. Trigger First Battle
- Walk to the **wooden chest** (right side of room)
- When you see "Press E to interact" prompt
- Press `E` → Battle starts!

### 4. Battle Controls
- **Action Menu:**
  - `W/S` or `↑/↓` - Navigate
  - `Enter/Space/E` - Select

- **Actions:**
  - `Fight` → Choose move to attack
  - `Switch` → (Not yet implemented)
  - `Retreat` → **Safely exit battle** (always available!)
  - `Info` → View Pokemon state

- **Move Menu:**
  - `W/S` or `↑/↓` - Select move
  - `Enter/Space/E` - Use move
  - `ESC` - Back to action menu

### 5. What to Watch For

**Descriptive States (NO HP BARS!):**
- "Standing strong, ready for battle" → ~90-100% HP
- "Standing strong but breathing hard" → ~70-90% HP
- "Favoring one side, visibly hurt" → ~50-70% HP
- "Staggered — switch window opens" → ~30-50% HP
- "On the brink of collapse" → ~10-30% HP
- "About to fall — retreat NOW" → <10% HP

**Injury Notifications:**
- Watch for messages like:
  - "Deep scar across body — a permanent reminder of near-death"
  - "Scorched tissue on left_leg — the fire's mark remains"

**Type Effectiveness:**
- "It's devastatingly effective!" → 2x damage
- "It's very effective!" → 1.5x damage
- "It doesn't seem very effective..." → 0.5x damage

### 6. After Battle
- Battle ends with outcome: Win / Retreat / Faint / Death
- Automatically return to bedroom
- Pokemon's battle log is updated
- Veteran Score recalculated

---

## Testing Scenarios

### Scenario 1: Normal Battle (Win)
1. Start battle at chest
2. Choose `Fight` → Select any move
3. Continue attacking until enemy defeated
4. **Expected:** Return to bedroom, Pokemon gains experience

### Scenario 2: Strategic Retreat
1. Start battle
2. Take a few hits (let HP drop to ~50%)
3. Choose `Retreat`
4. **Expected:** Battle ends, return to bedroom, minimal trauma added

### Scenario 3: Trigger Injury
1. Start battle
2. Let enemy hit you multiple times (don't attack, just wait)
3. Eventually enemy will land ~80+ damage hit
4. **Expected:** Injury notification appears, permanent scar recorded

### Scenario 4: Fight Until Faint
1. Start battle
2. Let enemy attack without fighting back
3. Wait until "On the brink of collapse" appears
4. Let one more hit land
5. **Expected:** Pokemon faints, battle ends, heavy trauma recorded

### Scenario 5: Multiple Battles (Veteran Score Evolution)
1. Battle → Win
2. Return to chest → Battle again → Win
3. Repeat 3-5 times
4. **Expected:** Veteran Score increases each time
5. Check logs/game.log to see score progression

---

## Debug Features

### F1 - Debug Mode
- Shows collision boxes (red rectangles)
- Shows player hitbox
- Useful for verifying interactions

### F2 - Screenshot
- Takes screenshot to `screenshots/` folder
- Saves current game state

### F3 - Log State
- Dumps current game state to log file
- Check `logs/game_YYYYMMDD_HHMMSS.log`

---

## Checking Battle Logs (Manual)

### Option 1: Check Log File
```bash
# Open latest log file
ls -lt logs/ | head -2
# Look for lines containing "Veteran Score"
grep "Veteran Score" logs/game_*.log
```

### Option 2: Run Test Script
```bash
python test_battle_system.py
```
This shows:
- Combat Experience score
- Adaptation Score
- Trauma Score
- Injury Severity
- Final Veteran Score

---

## Expected Test Results

### First Battle (Win):
- Combat Experience: ~10-15
- Adaptation Score: ~5-10
- Trauma Score: ~5-15
- **Net Score: ~5-15** (positive)

### First Battle (Retreat at 50% HP):
- Combat Experience: ~3-5
- Trauma Score: ~10-20
- **Net Score: -5 to -10** (negative)

### Multiple Wins (3 battles):
- Combat Experience: ~30-50
- Adaptation Score: ~15-25
- Trauma Score: ~15-30
- **Net Score: ~25-40** (strong positive)

### Battle with Injury:
- Injury Severity: +20 (major) or +50 (catastrophic)
- **Net Score: Reduced by injury amount**
- Stat modifiers applied (check test output)

---

## Common Issues & Solutions

### Issue: Game won't start
**Solution:** Check Python version (need 3.8+), install pygame:
```bash
pip install pygame-ce
```

### Issue: Battle doesn't trigger at chest
**Solution:** Make sure you're close enough (within ~40 pixels), watch for "Press E" prompt

### Issue: Can't see HP changes
**Solution:** This is intentional! Read the descriptive state text, not numbers

### Issue: Battle seems too hard/easy
**Solution:** This is the alpha version. Enemy stats can be adjusted in `main.py` line 105-107

---

## Performance Testing

### FPS Check
- Game should run at stable 60 FPS
- If lower, check `debug_mode` (F1) isn't slowing it down

### Memory Check
- Battle log limited to 200 entries per Pokemon
- Should stay under ~100MB RAM for extended play

---

## Reporting Issues

When reporting bugs, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Log file (`logs/game_*.log`)
4. Screenshot if visual bug (F2)

---

## Advanced Testing: Battle Log Inspection

### Create Test Pokemon with History
```python
from core.pokemon import Pokemon

# Create Pokemon
p = Pokemon("Charmander", "TestMon", 1)

# Simulate 10 battles
for i in range(10):
    entry = {
        'opponent_id': f'Enemy_{i}',
        'opponent_veterancy': 1.0,
        'moves_used': [{'move': 'Tackle', 'effective': True}],
        'damage_taken': {'amount': 20.0, 'type': 'physical', 'location': 'body'},
        'damage_dealt': 30.0,
        'status_events': [],
        'outcome': 'win',
        'player_tactics': [],
        'environment': []
    }
    p.add_battle_entry(entry)
    print(f"Battle {i+1}: Score = {p.get_effective_veteran_score():.1f}")
```

---

## Next Steps After Testing

Once you've verified the vertical slice works:

1. ✅ Test all 4 battle outcomes (win/retreat/faint/death)
2. ✅ Trigger at least one injury
3. ✅ Complete 3+ battles in a row
4. ✅ Verify battle log persists (check with test script)
5. ✅ Try different move combinations

**Then you're ready for Phase 4+ implementation!** 🎮
