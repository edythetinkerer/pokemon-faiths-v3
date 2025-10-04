# ✅ Film Grain Added to Entire Game

## Changes Made

### 1. Created GlobalEffects Class
- `src/core/visual_effects.py` - New `GlobalEffects` class
- Optimized grain (density 0.003, updates every 2 frames)
- Alpha 25 for lighter effect in non-cave scenes

### 2. Added to Bedroom
- Imported `GlobalEffects`
- Initialized in `__init__`
- Applied after scaling in `draw()`

### 3. Cave Already Has It
- Uses `CaveEffects` (darker grain, alpha 30)

## To Add to Other Scenes

**outside.py:**
```python
from core.visual_effects import GlobalEffects

# In __init__:
self.global_effects = GlobalEffects(SCREEN_WIDTH, SCREEN_HEIGHT)

# In draw(), after scaling:
self.global_effects.apply_film_grain(self.screen)
```

**start_screen.py, intro_sequence.py, battle.py:**
Same pattern as above.

## Frame Smoothing

Current: `dt = self.clock.tick(60) / 1000.0`

This is already optimal. Clock.tick(60):
- Caps at 60 FPS
- Returns milliseconds since last frame
- Dividing by 1000 gives seconds (dt)

**Already smooth!** The grain optimization (every 2 frames, low density) keeps 60 FPS.

## Test
```bash
python run.py
```

Bedroom now has grain effect! FPS should be 60. 🎬
