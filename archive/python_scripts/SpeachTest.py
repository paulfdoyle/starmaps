import pygame
import sys
import speech_recognition as sr

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Menu with Voice Control")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Font
font = pygame.font.Font(None, 50)

# Function for actions
def start_game():
    print("Starting game...")

def options():
    print("Options selected...")

def quit_game():
    pygame.quit()
    sys.exit()

# Menu class with voice control
class Menu:
    def __init__(self, screen, items, font, font_color=WHITE, select_color=RED):
        self.screen = screen
        self.items = items
        self.font = font
        self.font_color = font_color
        self.select_color = select_color
        self.current_item = 0

    def draw(self):
        self.screen.fill(BLACK)
        for index, (text, _) in enumerate(self.items):
            label = self.font.render(text, True, self.font_color if index != self.current_item else self.select_color)
            width = label.get_width()
            height = label.get_height()
            pos_x = (WIDTH // 2) - (width // 2)
            pos_y = (HEIGHT // 2) - (height // 2) + (index * 60)
            self.screen.blit(label, (pos_x, pos_y))

    def recognize_voice_command(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        try:
            with mic as source:
                print("Listening for command...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print(f"Recognized command: {command}")
                return command
        except sr.UnknownValueError:
            print("Could not understand the command")
        except sr.RequestError:
            print("Could not request results from the service")
        
        return None

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_item = (self.current_item - 1) % len(self.items)
                    elif event.key == pygame.K_DOWN:
                        self.current_item = (self.current_item + 1) % len(self.items)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.items[self.current_item][1]()

            voice_command = self.recognize_voice_command()
            if voice_command:
                self.handle_voice_command(voice_command)

            self.draw()
            pygame.display.update()

    def handle_voice_command(self, command):
        # Map commands to menu actions
        if "start" in command:
            self.items[0][1]()
        elif "options" in command:
            self.items[1][1]()
        elif "quit" in command:
            self.items[2][1]()

# Menu items: (Text, Function)
menu_items = [("Start Game", start_game), 
              ("Options", options), 
              ("Quit", quit_game)]

menu = Menu(screen, menu_items, font)

# Run the menu
menu.run()

