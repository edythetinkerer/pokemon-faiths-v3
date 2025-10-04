#!/usr/bin/env python3
"""Test if arrow keys are detected properly"""

import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()

print("Press arrow keys (ESC to quit)")
print("Testing key detection...")
print()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                print("UP arrow detected")
            elif event.key == pygame.K_DOWN:
                print("DOWN arrow detected")
            elif event.key == pygame.K_LEFT:
                print("LEFT arrow detected")
            elif event.key == pygame.K_RIGHT:
                print("RIGHT arrow detected")

    # Also check pressed state
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        print("  (UP is pressed)")
    if keys[pygame.K_DOWN]:
        print("  (DOWN is pressed)")
    if keys[pygame.K_LEFT]:
        print("  (LEFT is pressed)")
    if keys[pygame.K_RIGHT]:
        print("  (RIGHT is pressed)")

    clock.tick(10)  # 10 FPS for easier reading

pygame.quit()
