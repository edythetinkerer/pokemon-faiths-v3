# Performance Tips

## Quick Fixes:
1. **Grain frame skip**: Change from 2 to 3 frames
2. **Lower grain density**: 0.008 → 0.005
3. **Remove effects if needed**: Comment out filter in scenes

## Test with effects OFF:
```python
# In bedroom.py, outside.py:
# self.global_effects.apply_full_effects(self.screen)  # Comment this line
```

If FPS is good without effects, grain is the issue.
