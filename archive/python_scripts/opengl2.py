import pygame
import numpy as np
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
NUM_CIRCLES = 9000

# Set up the display with hardware acceleration and double buffering
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Pygame Optimization Example")

# Function to create a surface with a circle
def create_circle_surface(radius, color):
    surface = pygame.Surface((2*radius, 2*radius), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (radius, radius), radius)
    return surface

# Example numpy array containing positions, colors, and sizes (radius)
data_array = np.array([
    [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)),
     (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
     random.randint(10, 50)] for _ in range(NUM_CIRCLES)
], dtype=object)

# Extract positions, colors, and radii for easier manipulation
positions = np.array([item[0] for item in data_array])
colors = np.array([item[1] for item in data_array])
radii = np.array([item[2] for item in data_array])

# Pre-render circle surfaces
circle_surfaces = [create_circle_surface(radii[i], colors[i]) for i in range(NUM_CIRCLES)]

# Main game loop
clock = pygame.time.Clock()
running = True
frame_count = 0
start_time = pygame.time.get_ticks()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Example: Update positions
    positions = np.array([(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(NUM_CIRCLES)])
    
    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the circles
    for i in range(NUM_CIRCLES):
        pos = positions[i]
        radius = radii[i]
        surface = circle_surfaces[i]
        screen.blit(surface, (pos[0] - radius, pos[1] - radius))

    # Swap the buffers
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
   # Cap the frame rate
    clock.tick(FPS)
    frame_count += 1
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time
    if elapsed_time > 1000:  # 1000 ms = 1 second
        actual_fps = frame_count / (elapsed_time / 1000.0)
        print(f"Actual FPS: {actual_fps:.2f}")
        frame_count = 0
        start_time = current_time
pygame.quit()
sys.exit()
