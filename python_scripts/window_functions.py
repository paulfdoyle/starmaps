# window_functions.py

import pygame

class PygameWindow:
    def __init__(self, title, width, height, color, draw_func):
        self.title = title
        self.width = width
        self.height = height
        self.color = color
        self.draw_func = draw_func

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill(self.color)
            self.draw_func(screen)
            pygame.display.flip()

        pygame.quit()

def draw_window1(screen):
    pygame.draw.circle(screen, (0, 0, 255), (200, 150), 50)  # Blue circle

def draw_window2(screen):
    pygame.draw.rect(screen, (255, 255, 0), (150, 100, 100, 100))  # Yellow square

def create_and_run_window(title, width, height, color, draw_func):
    window = PygameWindow(title, width, height, color, draw_func)
    window.run()

