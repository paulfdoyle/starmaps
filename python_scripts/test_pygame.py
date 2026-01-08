import pygame
import sys
from line_profiler import profile

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h - 60
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Star Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Function to create a star surface
def create_star_surface(color, radius):
    diameter = radius * 2
    star_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(star_surface, color, (radius, radius), radius)
    return star_surface

# Main function
@profile
def main():
    global screen, screen_width, screen_height
    running = True
    clock = pygame.time.Clock()

    # Star parameters
    star_radius = 10
    star_diameter = star_radius * 2
    stars_per_row = screen_width // star_diameter
    stars_per_column = screen_height // star_diameter
    total_stars = 9003

    # Precompute star positions
    star_positions = []
    for i in range(total_stars):
        row = i // stars_per_row
        col = i % stars_per_row
        x = col * star_diameter + star_radius
        y = row * star_diameter + star_radius
        if y + star_radius > screen_height:
            break
        star_positions.append((x, y))

    # Create star surface
    star_surface = create_star_surface(WHITE, star_radius)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                stars_per_row = screen_width // star_diameter
                stars_per_column = screen_height // star_diameter
                star_positions = []
                for i in range(total_stars):
                    row = i // stars_per_row
                    col = i % stars_per_row
                    x = col * star_diameter + star_radius
                    y = row * star_diameter + star_radius
                    if y + star_radius > screen_height:
                        break
                    star_positions.append((x, y))

        # Fill the screen with black
        screen.fill(BLACK)

        # Draw stars using blit
        for pos in star_positions:
            screen.blit(star_surface, (pos[0] - star_radius, pos[1] - star_radius))

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
