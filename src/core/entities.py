"""
Shared Game Entities for Pokemon Faiths
Contains Player, Camera, and other reusable game objects
"""

import pygame
from constants import (
    PLAYER_SPEED, PLAYER_SIZE, PLAYER_COLLISION_WIDTH, 
    PLAYER_COLLISION_HEIGHT, PLAYER_VISUAL_SIZE
)
from .asset_manager import get_asset_manager
from .logger import get_logger

logger = get_logger('Entities')

class Player:
    """Player character with movement, animation, and collision"""

    def __init__(self, x, y):
        self.animations = self._load_sprites()
        self.direction = 'south'
        self.state = 'idle'  # 'idle' or 'walk'
        self.animation_frame = 0
        self.image = self.animations[self.direction]['idle'][0]
        self.sprinting = False  # Sprint toggle state

        # Create collision box shorter so head can overlap furniture
        self.rect = pygame.Rect(x - PLAYER_COLLISION_WIDTH//2, y - 2,
                               PLAYER_COLLISION_WIDTH, PLAYER_COLLISION_HEIGHT)

        # Store the visual position for drawing
        self.visual_rect = pygame.Rect(x - PLAYER_VISUAL_SIZE//2, y - PLAYER_VISUAL_SIZE//2,
                                      PLAYER_VISUAL_SIZE, PLAYER_VISUAL_SIZE)

    def _load_sprites(self):
        """Loads all player sprites using the centralized AssetManager."""
        animations = {}
        asset_manager = get_asset_manager()
        directions = ['south', 'north', 'east', 'west']

        for direction in directions:
            animations[direction] = {'idle': [], 'walk': []}
            
            # Load idle sprite using AssetManager
            idle_path = f'assets/sprites/rotations/{direction}.png'
            sprite = asset_manager.load_image(idle_path, (PLAYER_SIZE, PLAYER_SIZE))
            animations[direction]['idle'].append(sprite)

            # Load walking animation frames
            for i in range(6):
                walk_path = f'assets/sprites/animations/walk/{direction}/frame_{i:03d}.png'
                sprite = asset_manager.load_image(walk_path, (PLAYER_SIZE, PLAYER_SIZE))
                animations[direction]['walk'].append(sprite)

        logger.debug("Player sprites loaded successfully")
        return animations

    def update(self, keys, collision_rects, dt=1.0):
        """
        BRAND NEW MOVEMENT SYSTEM - Simple and clean
        Updated player position with frame-independent movement
        """
        # Store old position for collision rollback
        old_x = self.rect.x
        old_y = self.rect.y

        # Calculate actual movement speed (pixels per frame)
        # Apply sprint multiplier if sprinting
        sprint_multiplier = 2.0 if self.sprinting else 1.0
        movement_speed = PLAYER_SPEED * dt * 60 * sprint_multiplier

        # Initialize movement
        dx = 0.0
        dy = 0.0
        moved = False

        # 4-DIRECTIONAL MOVEMENT ONLY (no diagonals)
        up_pressed = keys[pygame.K_w] or keys[pygame.K_UP]
        down_pressed = keys[pygame.K_s] or keys[pygame.K_DOWN]
        left_pressed = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right_pressed = keys[pygame.K_d] or keys[pygame.K_RIGHT]

        # Priority order: UP > DOWN > LEFT > RIGHT
        # Only one direction at a time
        if up_pressed:
            dy = -movement_speed
            self.direction = 'north'
            moved = True
        elif down_pressed:
            dy = movement_speed
            self.direction = 'south'
            moved = True
        elif left_pressed:
            dx = -movement_speed
            self.direction = 'west'
            moved = True
        elif right_pressed:
            dx = movement_speed
            self.direction = 'east'
            moved = True

        # Apply movement
        self.rect.x += int(dx)
        self.rect.y += int(dy)

        # Collision detection and rollback
        for collision_rect in collision_rects:
            if self.rect.colliderect(collision_rect):
                # Collision detected - revert to old position
                self.rect.x = old_x
                self.rect.y = old_y
                break

        # Update animation state
        self.state = 'walk' if moved else 'idle'
        
        # Update animation frame
        if self.state == 'walk':
            self.animation_frame += 0.15 * dt * 60  # Frame-independent animation
            if self.animation_frame >= len(self.animations[self.direction]['walk']):
                self.animation_frame = 0
        else:
            self.animation_frame = 0

        # Update sprite
        frame_index = int(self.animation_frame)
        self.image = self.animations[self.direction][self.state][frame_index]
        
        # Update visual rect to follow collision rect
        self.visual_rect.centerx = self.rect.centerx
        self.visual_rect.centery = self.rect.centery + 8  # Offset for better visual alignment

    def draw(self, surface, camera):
        """Draw player sprite with camera offset"""
        surface.blit(self.image, self.visual_rect.topleft - camera.offset)

    def toggle_sprint(self):
        """Toggle sprint state"""
        self.sprinting = not self.sprinting
        logger.info(f"Sprint: {'ON' if self.sprinting else 'OFF'}")


class Camera:
    """Camera system for following player and managing viewport"""
    
    def __init__(self, target, game_width=480, game_height=270):
        self.target = target
        self.offset = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, game_width, game_height)
        self.smoothing = False  # Can be enabled for smooth following
        self.smoothing_speed = 5.0

    def update(self, dt=1.0):
        """Update camera to follow the target"""
        if not self.target:
            return
            
        target_pos = pygame.math.Vector2(self.target.rect.center)
        
        if self.smoothing:
            # Smooth camera movement
            camera_pos = pygame.math.Vector2(self.rect.center)
            direction = target_pos - camera_pos
            camera_pos += direction * self.smoothing_speed * dt
            self.rect.center = camera_pos
        else:
            # Instant camera movement
            self.rect.center = target_pos

        # Update offset for rendering
        self.offset = pygame.math.Vector2(self.rect.topleft)

    def set_smoothing(self, enabled, speed=5.0):
        """Enable or disable camera smoothing"""
        self.smoothing = enabled
        self.smoothing_speed = speed

    def get_world_pos(self, screen_pos):
        """Convert screen position to world position"""
        return pygame.math.Vector2(screen_pos) + self.offset

    def get_screen_pos(self, world_pos):
        """Convert world position to screen position"""
        return pygame.math.Vector2(world_pos) - self.offset


class GameObject:
    """Base class for all game objects with position and sprite"""
    
    def __init__(self, x, y, sprite=None):
        self.rect = pygame.Rect(x, y, 0, 0)
        self.sprite = sprite
        if sprite:
            self.rect.size = sprite.get_size()
        self.visible = True
        self.active = True

    def update(self, dt=1.0):
        """Override in subclasses for custom update logic"""
        pass

    def draw(self, surface, camera):
        """Draw the object with camera offset"""
        if self.visible and self.sprite:
            surface.blit(self.sprite, self.rect.topleft - camera.offset)

    def set_position(self, x, y):
        """Set object position"""
        self.rect.x = x
        self.rect.y = y

    def get_center(self):
        """Get center position as tuple"""
        return self.rect.center

    def collides_with(self, other):
        """Check collision with another GameObject or rect"""
        if hasattr(other, 'rect'):
            return self.rect.colliderect(other.rect)
        else:
            return self.rect.colliderect(other)
