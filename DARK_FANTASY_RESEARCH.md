# 🎨 Dark Fantasy Color Grading Research

## Popular Dark Fantasy Color Palettes

### 1. **Bloodborne Style** (Most Popular)
- Deep desaturated colors
- Cool purple-blue shadows
- Warm orange-red highlights
- Colors: Purple (60, 50, 80), Dark Blue (40, 50, 70), Burnt Orange accents

### 2. **Dark Souls Style**
- Muted greens and grays
- Heavy desaturation
- Slight yellow-green tint in shadows
- Colors: Gray-Green (50, 60, 50), Dark Gray (45, 45, 50)

### 3. **Diablo Style**
- Deep reds and blacks
- High contrast
- Crimson shadows
- Colors: Dark Red (60, 30, 40), Black-Red (30, 20, 25)

### 4. **Gothic Horror (Castlevania)**
- Purple and deep blue
- High saturation in shadows
- Dramatic lighting
- Colors: Royal Purple (70, 40, 90), Midnight Blue (30, 40, 70)

### 5. **Modern Dark Fantasy (The Witcher 3)**
- Subtle desaturation
- Cool teal shadows
- Warm midtones
- Colors: Teal (40, 60, 65), Warm Gray (60, 55, 50)

## Recommended for Pokémon Faiths

**Best Fit: Bloodborne + Gothic Mix**
- Purple-blue base (atmospheric, not too dark)
- Subtle desaturation (keeps gameplay readable)
- Slight vignette (draws focus)

**Optimized Colors:**
- Shadow Tint: (55, 45, 75) - Purple-blue, lighter than before
- Mid Tint: (50, 50, 70) - Neutral blue-gray
- Subtle alpha: 25-35 (was 40, causing FPS drop)

## Performance Optimization

**Current Issue:** Alpha blending every frame = slow

**Solutions:**
1. Lower alpha (25 instead of 40)
2. Skip frames (update every 3 frames)
3. Use BLEND_RGB_MULT for faster compositing
4. Pre-multiply alpha in texture

## Implementation

```python
# Optimized dark fantasy filter
tint_color = (55, 45, 75, 25)  # Lighter, less alpha
# Skip frame updates for color filter (it's static anyway)
```
