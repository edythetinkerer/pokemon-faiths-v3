# Pokémon Faiths - TODO List
*Clean, prioritized task list*

---

## 🔥 CRITICAL (Do First - Week 1)

- [ ] **Wild Encounter System**
  - [ ] Create `core/wild_encounters.py`
  - [ ] Add encounter tables for Outside/Cave
  - [ ] Create 6 enemy templates (weak/moderate/veteran)
  - [ ] Add step counter to scenes
  - [ ] Test: Walk → Encounter triggers

- [ ] **Battle Integration**
  - [ ] Modify `outside.py` to check encounters
  - [ ] Modify `cave.py` to check encounters
  - [ ] Update `main.py` to handle `trigger_battle` result
  - [ ] Create helper functions for Pokemon save/load
  - [ ] Test: Encounter → Battle → Return to exploration

- [ ] **Starter Pokemon**
  - [ ] Create starter on first battle
  - [ ] Save to party in save_data
  - [ ] Load from save on subsequent battles
  - [ ] Test: New game → Encounter → Starter created

- [ ] **Cave Veteran Reward**
  - [ ] Update `cave.py` `_take_pokeball()` with veteran creation code
  - [ ] Create Arcanine with 99 age, injuries, battle log
  - [ ] Add to party as second slot
  - [ ] Test: Take pokéball → Receive "Old Warrior"

- [ ] **Catch Mechanic**
  - [ ] Add "Catch" option to battle action menu
  - [ ] Implement catch rate calculation
  - [ ] Add caught Pokemon to party
  - [ ] Handle party full (6 max)
  - [ ] Test: Battle → Catch → Pokemon added to party

---

## ⚡ HIGH PRIORITY (Week 2)

- [ ] **Movement Polish**
  - [ ] Change `PLAYER_SPEED` from 1.4 to 2.2
  - [ ] Change `ANIMATION_SPEED` from 0.15 to 0.20
  - [ ] Enable camera smoothing
  - [ ] Test feel with movement

- [ ] **Party UI**
  - [ ] Create `party_menu.py`
  - [ ] Add "Party" to pause menu
  - [ ] List all party Pokemon
  - [ ] Show descriptive stats (no numbers)
  - [ ] View injuries and battle history
  - [ ] Switch active Pokemon
  - [ ] Test: ESC → Party → View → Switch

- [ ] **Move Expansion**
  - [ ] Add 15-20 more moves to `moves.py`
  - [ ] Include status moves (buffs/debuffs)
  - [ ] Assign moves to species
  - [ ] Balance damage through playtesting
  - [ ] Test: Battles feel varied

---

## 📦 MEDIUM PRIORITY (Week 3-4)

- [ ] **More Wild Pokemon**
  - [ ] Add 8-10 more species
  - [ ] Assign to locations
  - [ ] Create rare veteran spawns (5%)
  - [ ] Test encounter variety

- [ ] **Item System**
  - [ ] Create `items.py` with Item class
  - [ ] Add Potion (heal outside battle)
  - [ ] Add Pokéball (catch item)
  - [ ] Create inventory UI
  - [ ] Add item usage in battle
  - [ ] Test: Use Potion → Pokemon heals

- [ ] **Save After Battle**
  - [ ] Auto-save after each battle
  - [ ] Update battle log in save file
  - [ ] Test: Battle → Quit → Load → Battle log persists

- [ ] **Injury Balancing**
  - [ ] Playtest injury threshold values
  - [ ] Adjust if triggering too often/rarely
  - [ ] Test various battle scenarios

---

## 🎨 LOW PRIORITY (Polish)

- [ ] **UI Polish**
  - [ ] Improve interaction text boxes
  - [ ] Add animation to E prompt
  - [ ] Polish pause menu transitions
  - [ ] Add sound effects

- [ ] **More Interactive Objects**
  - [ ] Add lore objects to scenes
  - [ ] Create item pickups in world
  - [ ] Add optional NPC dialogue

- [ ] **Performance**
  - [ ] Profile frame rate
  - [ ] Optimize asset loading
  - [ ] Reduce memory usage

---

## 🔮 FUTURE FEATURES (Post-MVP)

- [ ] **NPC Trainers**
  - [ ] Create trainer class
  - [ ] Add dialogue system
  - [ ] Scripted battles
  - [ ] Rewards for winning

- [ ] **More Areas**
  - [ ] Forest scene
  - [ ] Mountain scene
  - [ ] Abandoned village
  - [ ] Each with unique encounters

- [ ] **Evolution**
  - [ ] Based on Veteran Score
  - [ ] Requires high Combat Experience
  - [ ] Optional, not required

- [ ] **VoS System**
  - [ ] Detect catastrophic events
  - [ ] Track bond strength
  - [ ] Probability check
  - [ ] VoS visual effects

- [ ] **Prosthetics**
  - [ ] VoS-only system
  - [ ] Crafting/finding
  - [ ] Reduces injury penalties
  - [ ] Side effects

---

## ✅ COMPLETED

- [x] Core Veteran System
- [x] Battle scene with descriptive states
- [x] Pokemon class with battle logging
- [x] Move system with type effectiveness
- [x] Injury system (6 types)
- [x] Save/load system
- [x] Asset manager with caching
- [x] Three connected scenes (Bedroom/Outside/Cave)
- [x] Teleport system between scenes
- [x] Interaction system
- [x] Pause menu
- [x] Debug tools (F1-F3)
- [x] Player movement (4-directional)
- [x] Camera system
- [x] Eye opening intro effect
- [x] Cave old man pokéball (flags work, needs reward implementation)
- [x] Remove test chest battle trigger

---

## 📅 Suggested Schedule

### Week 1: Core Gameplay
**Mon:** Wild encounters + Battle integration  
**Tue:** Starter Pokemon + Testing  
**Wed:** Cave veteran reward  
**Thu:** Catch mechanic  
**Fri:** Testing & bug fixing  

### Week 2: Polish
**Mon:** Movement feel  
**Tue-Wed:** Party UI  
**Thu-Fri:** Move expansion & balancing  

### Week 3: Content
**Mon-Tue:** More Pokemon species  
**Wed-Thu:** Item system  
**Fri:** Playtesting  

---

## 🎯 Current Milestone: Make It Playable

**Goal:** 10+ minute gameplay loop with:
- Wild encounters
- Battle system
- Starter Pokemon
- Catch mechanic
- Cave veteran reward

**When complete:** Game transitions from tech demo to actual game

---

**Updated:** October 3, 2025  
**Status:** Foundation complete, building gameplay
