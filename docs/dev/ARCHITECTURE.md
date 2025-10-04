# Pokémon Faiths - Battle System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         MAIN GAME LOOP                          │
│                          (main.py)                              │
└────────────┬────────────────────────────────────────┬───────────┘
             │                                        │
             ▼                                        ▼
    ┌────────────────┐                      ┌────────────────┐
    │ Start Screen   │                      │  Intro         │
    │ (Menu)         │                      │  Sequence      │
    └────────────────┘                      └────────────────┘
             │
             ▼
    ┌────────────────────────────────────────────────────┐
    │            GAME STATE MACHINE                      │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
    │  │ Bedroom  │◄─┤  Battle  │  │ Outside  │        │
    │  │  Scene   │─►│  Scene   │◄─┤  Scene   │        │
    │  └──────────┘  └──────────┘  └──────────┘        │
    └────────────────────────────────────────────────────┘
             │              │              │
             └──────────────┴──────────────┘
                            │
                    ┌───────▼────────┐
                    │  Save Manager  │
                    └────────────────┘
```

---

## Core Systems Architecture

### 1. Pokemon System (`core/pokemon.py`)

```
┌───────────────────────────────────────────────────────────┐
│                      POKEMON CLASS                        │
├───────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐     │
│  │         BATTLE LOG (Circular Buffer)            │     │
│  │  ┌──────────────────────────────────────────┐   │     │
│  │  │ Entry 1: {timestamp, moves, damage...}   │   │     │
│  │  │ Entry 2: {timestamp, moves, damage...}   │   │     │
│  │  │ Entry 3: {timestamp, moves, damage...}   │   │     │
│  │  │              ...                         │   │     │
│  │  │ Entry 200: {timestamp, moves, damage...} │   │     │
│  │  └──────────────────────────────────────────┘   │     │
│  │         ▼ Exponential Decay Applied ▼           │     │
│  └─────────────────────────────────────────────────┘     │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────┐     │
│  │       VETERAN SCORE CALCULATION                 │     │
│  │  ┌────────────────────────────────────────┐     │     │
│  │  │ Combat Experience (from wins, tactics) │     │     │
│  │  │ + Adaptation Score (effective moves)   │     │     │
│  │  │ - Trauma Score (damage, defeats)       │     │     │
│  │  │ - Injury Severity (permanent injuries) │     │     │
│  │  │ = Effective Veteran Score              │     │     │
│  │  └────────────────────────────────────────┘     │     │
│  └─────────────────────────────────────────────────┘     │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────┐     │
│  │        DESCRIPTIVE STATE SYSTEM                 │     │
│  │  ┌────────────────────────────────────────┐     │     │
│  │  │ current_hp_percent → Text Description  │     │     │
│  │  │ 90-100%: "Standing strong"             │     │     │
│  │  │ 30-50%:  "Staggered"                   │     │     │
│  │  │ 0-10%:   "On the brink of collapse"    │     │     │
│  │  └────────────────────────────────────────┘     │     │
│  └─────────────────────────────────────────────────┘     │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────┐     │
│  │          INJURY SYSTEM                          │     │
│  │  ┌────────────────────────────────────────┐     │     │
│  │  │ Threshold Check (60/80/95 damage)      │     │     │
│  │  │ ▼ Trigger Injury                       │     │     │
│  │  │ Store in permanent_injuries[]          │     │     │
│  │  │ Apply Stat Modifiers                   │     │     │
│  │  │ Update Descriptive State               │     │     │
│  │  └────────────────────────────────────────┘     │     │
│  └─────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────┘
```

---

### 2. Move System (`core/moves.py`)

```
┌─────────────────────────────────────────────────────┐
│              MOVE DATABASE                          │
├─────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐      │
│  │  Tackle   │  │   Bite    │  │  Ember    │  ... │
│  │ (Normal)  │  │  (Dark)   │  │  (Fire)   │      │
│  │ Power: 40 │  │ Power: 60 │  │ Power: 40 │      │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘      │
│        └────────────┬──────────────┘               │
│                     ▼                               │
│  ┌─────────────────────────────────────────┐       │
│  │     MOVE.EXECUTE(attacker, defender)    │       │
│  ├─────────────────────────────────────────┤       │
│  │ 1. Check accuracy (hit/miss)            │       │
│  │ 2. Get type effectiveness (TypeChart)   │       │
│  │ 3. Calculate damage (HIDDEN)            │       │
│  │ 4. Apply to defender.take_damage()      │       │
│  │ 5. Return narrative description         │       │
│  └─────────────────────────────────────────┘       │
│                     │                               │
│                     ▼                               │
│  ┌─────────────────────────────────────────┐       │
│  │          NARRATIVE OUTPUT               │       │
│  │  "A solid Tackle!"                      │       │
│  │  "It's very effective!"                 │       │
│  │  "Enemy state: Staggered..."            │       │
│  └─────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

---

### 3. Battle Scene (`game/states/battle.py`)

```
┌────────────────────────────────────────────────────────┐
│                   BATTLE SCENE                         │
├────────────────────────────────────────────────────────┤
│  PHASE: move_select                                    │
│  ┌──────────────────────────────────────────────┐     │
│  │  ┌────────────┐       ┌────────────────┐     │     │
│  │  │   Action   │       │  Player        │     │     │
│  │  │   Menu     │       │  Pokemon       │     │     │
│  │  ├────────────┤       │  State Text    │     │     │
│  │  │ ► Fight    │       └────────────────┘     │     │
│  │  │   Switch   │                              │     │
│  │  │   Retreat  │       ┌────────────────┐     │     │
│  │  │   Info     │       │  Enemy         │     │     │
│  │  └────────────┘       │  Pokemon       │     │     │
│  │                       │  State Text    │     │     │
│  │  ┌────────────────────────────────┐   │     │     │
│  │  │  Message Box                   │   │     │     │
│  │  │  "What will you do?"           │   │     │     │
│  │  └────────────────────────────────┘   │     │     │
│  └──────────────────────────────────────────────┘     │
│                     │                                  │
│                     ▼ Player selects "Fight"           │
│  ┌──────────────────────────────────────────────┐     │
│  │  ┌────────────┐                              │     │
│  │  │   Moves    │                              │     │
│  │  ├────────────┤                              │     │
│  │  │ ► Tackle   │                              │     │
│  │  │   Ember    │                              │     │
│  │  │   Scratch  │                              │     │
│  │  │   Bite     │                              │     │
│  │  └────────────┘                              │     │
│  └──────────────────────────────────────────────┘     │
│                     │                                  │
│                     ▼ Move selected                    │
│  ──────────────────────────────────────────────────   │
│  PHASE: animating                                      │
│  ┌──────────────────────────────────────────────┐     │
│  │  Execute Player Move                         │     │
│  │  ▼                                            │     │
│  │  Enemy takes damage                          │     │
│  │  ▼                                            │     │
│  │  Check for injury                            │     │
│  │  ▼                                            │     │
│  │  Execute Enemy Move (AI chooses)             │     │
│  │  ▼                                            │     │
│  │  Player takes damage                         │     │
│  │  ▼                                            │     │
│  │  Check for injury                            │     │
│  └──────────────────────────────────────────────┘     │
│                     │                                  │
│                     ▼                                  │
│  ──────────────────────────────────────────────────   │
│  PHASE: result                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │  Show outcome message                        │     │
│  │  "Tackle connects!"                          │     │
│  │  "Enemy state: Staggered..."                 │     │
│  │                                               │     │
│  │  Press any key to continue...                │     │
│  └──────────────────────────────────────────────┘     │
│                     │                                  │
│                     ▼ Check if battle over             │
│  ┌──────────────────────────────────────────────┐     │
│  │  If Pokemon fainted/killed → FINISHED        │     │
│  │  Else → Return to move_select                │     │
│  └──────────────────────────────────────────────┘     │
│                     │                                  │
│                     ▼ Battle ends                      │
│  ──────────────────────────────────────────────────   │
│  PHASE: finished                                       │
│  ┌──────────────────────────────────────────────┐     │
│  │  Generate Battle Log Entry                   │     │
│  │  ▼                                            │     │
│  │  Add to Pokemon.battle_log                   │     │
│  │  ▼                                            │     │
│  │  Recalculate Veteran Score                   │     │
│  │  ▼                                            │     │
│  │  Return to Bedroom                           │     │
│  └──────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
```

---

## Data Flow: Complete Battle Sequence

```
1. TRIGGER
   Bedroom → Player interacts with chest
   ▼
   bedroom.start_battle = True
   ▼
   main.py detects battle flag

2. BATTLE INITIALIZATION
   main.py creates:
   - Player Pokemon (from save or new starter)
   - Enemy Pokemon (stats defined)
   ▼
   BattleScene(player_pokemon, enemy_pokemon)

3. BATTLE LOOP
   ┌─────────────────────────┐
   │ Player selects move     │
   ▼                         │
   │ Move.execute()          │
   ▼                         │
   │ Damage calculation      │
   ▼                         │
   │ enemy.take_damage()     │
   ▼                         │
   │ Check for injury        │
   ▼                         │
   │ Enemy AI selects move   │
   ▼                         │
   │ Move.execute()          │
   ▼                         │
   │ player.take_damage()    │
   ▼                         │
   │ Check for injury        │
   ▼                         │
   │ Check if battle over    │
   └─────────────────────────┘
   │ If not over, repeat
   ▼ If over:

4. BATTLE END
   battle.get_battle_log_entry()
   ▼
   Returns:
   {
     opponent_id, opponent_veterancy,
     moves_used[], damage_taken{}, damage_dealt,
     status_events[], outcome,
     player_tactics[], environment[]
   }
   ▼
   player_pokemon.add_battle_entry(log_entry)
   ▼
   player_pokemon.calculate_veteran_score()

5. RETURN TO BEDROOM
   main.py: current_scene = 'bedroom'
   ▼
   Save data updated with:
   - Updated Pokemon battle log
   - New Veteran Score
   - Any new injuries
```

---

## Key Design Patterns Used

### 1. **Singleton Pattern**
- `AssetManager` - Single instance loads/caches assets
- `MoveDatabase` - Single move repository
- `TypeChart` - Single type effectiveness system
- `SaveManager` - Single save file handler

### 2. **State Machine Pattern**
- Main game loop switches between scenes
- Battle phases: move_select → animating → result → finished
- Clear state transitions prevent bugs

### 3. **Observer Pattern** (Implicit)
- Battle log entries observe all combat events
- Veteran Score automatically recalculates when log changes
- Injury system observes damage thresholds

### 4. **Circular Buffer Pattern**
- Battle log uses `collections.deque(maxlen=200)`
- Oldest entries automatically removed
- Constant memory usage regardless of battles fought

### 5. **Strategy Pattern**
- Different injury types use same interface
- Different outcomes (win/retreat/faint/death) handled uniformly
- Easy to add new moves, injuries, tactics

---

## Memory Management

```
Pokemon Instance Memory Footprint:
├─ battle_log: ~200 entries × ~500 bytes = ~100 KB
├─ permanent_injuries: ~5 injuries × ~200 bytes = ~1 KB
├─ stats & scores: ~500 bytes
└─ TOTAL per Pokemon: ~102 KB

Party of 6 Pokemon: ~612 KB
Multiple saves: Negligible (logs stored in save files)

Expected total memory usage: <50 MB for full game
```

---

## Performance Considerations

### ✅ Optimizations Implemented
1. **Asset Caching** - Images loaded once, reused
2. **Circular Buffer** - Fixed memory, no unbounded growth
3. **Lazy Calculation** - Veteran Score only calculated after battles
4. **Pre-rendered UI** - Boxes/gradients created once

### 🔮 Future Optimizations
1. **Move pooling** - Reuse move objects instead of creating new
2. **Battle log compression** - Compress old entries (>100 battles)
3. **Sprite batching** - Draw multiple sprites in one call
4. **Sound effect pooling** - Limit concurrent SFX

---

## Testing Architecture

```
┌────────────────────────────────────────┐
│      test_battle_system.py             │
├────────────────────────────────────────┤
│ test_pokemon_creation()                │
│   └─> Verifies descriptive states      │
│                                         │
│ test_moves()                            │
│   └─> Verifies move database           │
│                                         │
│ test_battle_simulation()                │
│   └─> Simulates 3-round combat         │
│   └─> Tests move execution             │
│   └─> Tests injury triggering          │
│                                         │
│ test_battle_log()                       │
│   └─> Simulates 5 battles              │
│   └─> Verifies score calculations      │
│   └─> Tests decay function             │
│                                         │
│ test_injury_system()                    │
│   └─> Tests threshold triggering       │
│   └─> Verifies stat modifiers          │
│   └─> Tests permanent storage          │
└────────────────────────────────────────┘
```

---

## File Dependencies

```
main.py
├── game/states/start_screen.py
├── game/states/intro_sequence.py
├── game/states/bedroom.py
│   ├── core/entities.py (Player, Camera)
│   ├── core/asset_manager.py
│   ├── core/save_manager.py
│   └── core/pause_menu.py
└── game/states/battle.py
    ├── core/pokemon.py
    │   └── core/logger.py
    └── core/moves.py
        ├── core/logger.py
        └── (uses Pokemon class)

constants.py (imported by all)
```

---

## Future Architecture Considerations

### When adding Party System:
```
save_data['party'] = [
    Pokemon(...),  # Starter
    Pokemon(...),  # Caught wild
    Pokemon(...),  # Caught wild
]
```

### When adding VoS System:
```
Pokemon.has_vos = True
Pokemon.vos_acquired_timestamp = time.time()
Pokemon.vos_trigger_event = "party_wipe_survival"
```

### When adding Prosthetics:
```
Pokemon.prosthetics = [
    {
        'type': 'mechanical_leg',
        'body_location': 'left_leg',
        'stat_bonuses': {'speed': +5},
        'side_effects': ['energy_drain']
    }
]
```

---

This architecture is **modular**, **extensible**, and **aligned with the design document** principles! 🎯
