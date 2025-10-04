"""
Color Filter Demo for Pokemon Faiths
Demonstrates all available color filter presets

Controls:
- Arrow Keys: Navigate through filters
- Enter: Apply selected filter
- T: Start transition to next filter
- ESC: Quit demo
"""

import pygame
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.color_filters import ColorFilter
from src.core.asset_manager import get_asset_manager
from src.constants import TILE_SIZE

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

def main():
    """Run the color filter demo"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pokemon Faiths - Color Filter Demo")
    clock = pygame.time.Clock()
    
    # Create a test surface with sample content
    test_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Load some sample assets for the demo
    asset_manager = get_asset_manager()
    try:
        # Try to load some game assets
        floor_tile = asset_manager.load_image('assets/images/grass_tile1.png', (TILE_SIZE, TILE_SIZE))
        sprite = asset_manager.load_image('assets/sprites/rotations/south.png', (48, 48))
    except:
        # Fallback to placeholder shapes if assets not found
        floor_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        floor_tile.fill((50, 150, 50))
        sprite = pygame.Surface((48, 48))
        sprite.fill((200, 100, 100))
    
    # Initialize color filter
    color_filter = ColorFilter((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Get list of all presets
    presets = ColorFilter.list_presets()
    current_index = 0
    
    # UI settings
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    
    running = True
    transition_mode = False
    
    print("\n" + "="*60)
    print("COLOR FILTER DEMO")
    print("="*60)
    print("\nControls:")
    print("  Arrow Keys: Navigate filters")
    print("  Enter: Apply selected filter")
    print("  T: Transition to next filter")
    print("  ESC: Quit")
    print("\n" + "="*60 + "\n")
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    current_index = (current_index - 1) % len(presets)
                    print(f"Selected filter: {presets[current_index]}")
                elif event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % len(presets)
                    print(f"Selected filter: {presets[current_index]}")
                elif event.key == pygame.K_RETURN:
                    color_filter.set_filter(presets[current_index])
                    print(f"Applied filter: {presets[current_index]}")
                elif event.key == pygame.K_t:
                    next_index = (current_index + 1) % len(presets)
                    color_filter.transition_to(presets[next_index], 2.0)
                    print(f"Transitioning: {presets[current_index]} -> {presets[next_index]}")
                    current_index = next_index
        
        # Update
        color_filter.update(dt)
        
        # Draw test scene
        test_surface.fill((30, 30, 40))  # Dark background
        
        # Draw a grid of tiles
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            for x in range(0, SCREEN_WIDTH, TILE_SIZE):
                test_surface.blit(floor_tile, (x, y))
        
        # Draw some sprites at different positions
        positions = [
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            (3 * SCREEN_WIDTH // 4, 2 * SCREEN_HEIGHT // 3)
        ]
        for pos in positions:
            test_surface.blit(sprite, pos)
        
        # Draw some shapes for color testing
        pygame.draw.rect(test_surface, (255, 100, 100), (50, 50, 100, 100))
        pygame.draw.rect(test_surface, (100, 255, 100), (170, 50, 100, 100))
        pygame.draw.rect(test_surface, (100, 100, 255), (290, 50, 100, 100))
        pygame.draw.circle(test_surface, (255, 255, 100), (250, 500), 50)
        
        # Apply color filter
        color_filter.apply(test_surface)
        
        # Blit to screen
        screen.blit(test_surface, (0, 0))
        
        # Draw UI overlay
        draw_ui(screen, font_large, font_medium, font_small, presets, current_index, color_filter)
        
        pygame.display.flip()
    
    pygame.quit()
    print("\nDemo ended.")

def draw_ui(screen, font_large, font_medium, font_small, presets, current_index, color_filter):
    """Draw the UI overlay"""
    # Semi-transparent background for text
    ui_bg = pygame.Surface((SCREEN_WIDTH, 200))
    ui_bg.fill((0, 0, 0))
    ui_bg.set_alpha(180)
    screen.blit(ui_bg, (0, SCREEN_HEIGHT - 200))
    
    # Title
    title = font_large.render("Color Filter Demo", True, (255, 255, 255))
    screen.blit(title, (20, SCREEN_HEIGHT - 190))
    
    # Current filter name
    filter_name = presets[current_index]
    filter_text = font_medium.render(f"Current: {filter_name}", True, (100, 255, 100))
    screen.blit(filter_text, (20, SCREEN_HEIGHT - 130))
    
    # Get filter info
    filter_info = ColorFilter.get_preset_info(filter_name)
    if filter_info:
        info_text = font_small.render(
            f"RGB: {filter_info['color']}  Alpha: {filter_info['alpha']}", 
            True, (200, 200, 200)
        )
        screen.blit(info_text, (20, SCREEN_HEIGHT - 95))
    
    # Transition status
    if color_filter.is_transitioning():
        trans_text = font_small.render("TRANSITIONING...", True, (255, 200, 100))
        screen.blit(trans_text, (20, SCREEN_HEIGHT - 65))
    
    # Controls
    controls_text = font_small.render(
        "◄► Navigate | ENTER Apply | T Transition | ESC Quit", 
        True, (150, 150, 150)
    )
    screen.blit(controls_text, (20, SCREEN_HEIGHT - 35))
    
    # Filter list preview (show nearby filters)
    list_y = 20
    for i in range(max(0, current_index - 2), min(len(presets), current_index + 3)):
        name = presets[i]
        if i == current_index:
            color = (255, 255, 100)
            prefix = "► "
        else:
            color = (180, 180, 180)
            prefix = "  "
        
        text = font_small.render(f"{prefix}{name}", True, color)
        screen.blit(text, (SCREEN_WIDTH - 250, list_y))
        list_y += 30

if __name__ == '__main__':
    main()
