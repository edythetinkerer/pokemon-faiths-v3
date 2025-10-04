#!/usr/bin/env python3
"""Test movement speed in all directions"""

import pygame
import sys

# Mock constants
PLAYER_SPEED = 1.4

def test_movement_calculation(dt=1.0):
    """Test what the actual movement values are"""
    speed = PLAYER_SPEED * dt * 60
    print(f"Base speed calculation: {PLAYER_SPEED} * {dt} * 60 = {speed}")
    print()

    test_cases = [
        ("UP", 0, -1),
        ("DOWN", 0, 1),
        ("LEFT", -1, 0),
        ("RIGHT", 1, 0),
        ("UP-LEFT", -1, -1),
        ("UP-RIGHT", 1, -1),
    ]

    for direction, move_x, move_y in test_cases:
        # Normalize diagonal
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        actual_x = move_x * speed
        actual_y = move_y * speed

        # Calculate magnitude
        magnitude = (actual_x**2 + actual_y**2)**0.5

        print(f"{direction:12} -> move_x={move_x:7.4f}, move_y={move_y:7.4f}")
        print(f"{'':12}    actual_x={actual_x:7.4f}, actual_y={actual_y:7.4f}, magnitude={magnitude:.4f}")
        print()

if __name__ == "__main__":
    print("=== Movement Speed Test ===\n")
    test_movement_calculation(dt=0.016667)  # ~60 FPS
