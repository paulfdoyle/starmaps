import pygame
import numpy as np
import sys
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 2000
FPS = 60
NUM_CIRCLES = 9000

# Set up the display with OpenGL
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("OpenGL Circle Batch Update Example")

# OpenGL initialization
glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Function to generate a unit circle
def generate_circle_vertices(num_segments=36):
    vertices = []
    angle_step = 2 * np.pi / num_segments
    for i in range(num_segments):
        angle = i * angle_step
        x = np.cos(angle)
        y = np.sin(angle)
        vertices.extend([x, y])
    vertices.extend([1.0, 0.0])  # Closing the circle
    return np.array(vertices, dtype=np.float32)

# Create a unit circle VBO
circle_vertices = generate_circle_vertices()
vbo_circle = vbo.VBO(circle_vertices)

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

# Main game loop
clock = pygame.time.Clock()
running = True
frame_count = 0
    
start_time = pygame.time.get_ticks()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Example: Update positions, sizes, and colors
    new_positions = np.array([(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(NUM_CIRCLES)])
    new_radii = np.random.randint(10, 11, NUM_CIRCLES)
    new_colors = np.random.randint(0, 200, (NUM_CIRCLES, 3))

    positions[:] = new_positions
    radii[:] = new_radii
    colors[:] = new_colors

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Draw the circles using VBO
    vbo_circle.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, vbo_circle)

    for i in range(NUM_CIRCLES):
        glPushMatrix()
        glTranslatef(positions[i][0], positions[i][1], 0)
        glScalef(radii[i], radii[i], 1)
        glColor4f(colors[i][0] / 255, colors[i][1] / 255, colors[i][2] / 255, 1.0)
        glDrawArrays(GL_TRIANGLE_FAN, 0, len(circle_vertices) // 2)
        glPopMatrix()

    vbo_circle.unbind()
    glDisableClientState(GL_VERTEX_ARRAY)

    # Swap the buffers
    pygame.display.flip()

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
