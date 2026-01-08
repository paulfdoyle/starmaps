import pygame
import random
import numpy as np

def create_circle_surfaces(color, max_radius):
    surfaces = []
    for radius in range(1, max_radius + 1):
        diameter = 2 * radius
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (radius, radius), radius)
        surfaces.append(surface)
    return surfaces

class FrameSprite(pygame.sprite.Sprite):
    def __init__(self, surfaces, pos):
        super().__init__()
        self.surfaces = surfaces
        self.current_frame = 0
        self.image = self.surfaces[self.current_frame]
        self.rect = self.image.get_rect(center=pos)

    def set_position(self, pos):
        self.rect.center = pos

    def set_frame(self, frame_index):
        if 0 <= frame_index < len(self.surfaces):
            self.current_frame = frame_index
            self.image = self.surfaces[self.current_frame]
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            raise IndexError("Frame index out of range")

    def random_frame(self):
        new_frame = random.randint(0, len(self.surfaces) - 1)
        self.set_frame(new_frame)

def batch_create_sprites(surfaces, positions):
    sprites = pygame.sprite.Group()
    for pos in positions:
        sprite = FrameSprite(surfaces, pos)
        sprites.add(sprite)
    return sprites

def randomize_sprites_frames(sprites):
    for sprite in sprites:
        sprite.random_frame()

def display_fps(screen, clock, font):
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, True, pygame.Color('white'))
    screen.blit(fps_text, (10, 10))

def generate_3d_circle_points(radius, angle_degrees, zero_dimension='z'):
    """
    Generates 3D points around the origin (0, 0, 0) on a circle.
    The number of points is determined by the angular separation and the specified zero dimension.

    Parameters:
    radius (float): The radius of the circle.
    angle_degrees (float): The angular separation in degrees between points.
    zero_dimension (str): The dimension to be zero ('x', 'y', or 'z').

    Returns:
    list of tuples: A list of 3D points (x, y, z) rounded to 3 decimal places.
    """
    if zero_dimension not in {'x', 'y', 'z'}:
        raise ValueError("zero_dimension must be 'x', 'y', or 'z'}")

    # Generate the angles
    num_points = int(360 / angle_degrees)
    angles = np.radians(np.arange(0, 360, angle_degrees))

    # Compute the coordinates
    cos_angles = np.cos(angles)
    sin_angles = np.sin(angles)

    if zero_dimension == 'z':
        x = radius * cos_angles
        y = radius * sin_angles
        z = np.zeros_like(x)
    elif zero_dimension == 'y':
        x = radius * cos_angles
        y = np.zeros_like(x)
        z = radius * sin_angles
    elif zero_dimension == 'x':
        x = np.zeros_like(cos_angles)
        y = radius * cos_angles
        z = radius * sin_angles

    # Combine and round the points
    points = np.column_stack((x, y, z))
    return points.round(3)

# Example usage
pygame.init()
screen = pygame.display.set_mode((1000, 1000))
screen_center = (screen.get_width() // 2, screen.get_height() // 2)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# Create surfaces with circles of radius 1 to 8 in CYAN
cyan = (0, 255, 255)
surfaces = create_circle_surfaces(cyan, 8)

# Generate 3D circle points and project them onto 2D screen coordinates
radius = 300
angle_degrees = 1
zero_dimension = 'z'
points_3d = generate_3d_circle_points(radius, angle_degrees, zero_dimension)
positions = [(int(x) + screen_center[0], int(y) + screen_center[1]) for x, y, z in points_3d]
# Batch create sprites
sprites = batch_create_sprites(surfaces, positions)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                for sprite in sprites:
                    sprite.set_frame(0)
            elif event.key == pygame.K_2:
                for sprite in sprites:
                    sprite.set_frame(1)
            elif event.key == pygame.K_3:
                for sprite in sprites:
                    sprite.set_frame(2)
            elif event.key == pygame.K_4:
                for sprite in sprites:
                    sprite.set_frame(3)
            elif event.key == pygame.K_5:
                for sprite in sprites:
                    sprite.set_frame(4)
            elif event.key == pygame.K_6:
                for sprite in sprites:
                    sprite.set_frame(5)
            elif event.key == pygame.K_7:
                for sprite in sprites:
                    sprite.set_frame(6)
            elif event.key == pygame.K_8:
                for sprite in sprites:
                    sprite.set_frame(7)
            elif event.key == pygame.K_r:
                randomize_sprites_frames(sprites)

    screen.fill((0, 0, 0))
    sprites.draw(screen)
    display_fps(screen, clock, font)
    pygame.display.flip()
    clock.tick(60)  # Cap the frame rate to 60 FPS

pygame.quit()


