import pygame
import sys

# Initialize Pygame
pygame.init()

# Define RGB values for O and B type stars
star_colors = {
    'O-type': (140, 176, 255),
    'B-type': (170, 191, 255),
    'A-type': (240, 240, 255),
    'F-type': (248, 247, 220),
    'G-type': (255, 233, 180),
    'K-type': (255, 165, 130),
    'M_Type': (255, 100, 100) # Yellow
}

star_colors_old = {
    'O-Type (Blue)': (60, 120, 255),
    'B-Type (Blue-White)': (100, 120, 255),
    'A-Type (White)': (230, 230, 255),
    'F-Type (Yellow-White)': (248, 247, 180),
    'G-Type (Yellow)': (255, 233, 120),
    'K-Type (Orange)': (255, 165, 100),
    'M-Type (Red)': (255, 100, 12)  
}
# Set up the display
display_width = 800
display_height = 1500
screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Star Type Colors')

# Main function
def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with black
        screen.fill((0, 0, 0))

        # Display each star color as a rectangle
        for i, (star_type, rgb) in enumerate(star_colors.items()):
            pygame.draw.rect(screen, rgb, (50, i * 150 + 50, 700, 100))
            font = pygame.font.SysFont(None, 36)
            label = font.render(star_type, True, (255, 255, 255))
            screen.blit(label, (50, i * 150 + 50))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
