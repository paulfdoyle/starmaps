import pygame
import sys
import pygame.gfxdraw
import random
import math
from math import *

FPS = 20
BF = 2.512  # brightnes factor Created a bigger size difference between stars on the screen
BRM6 = 4  # Base radius for magnitude 6 stars, this will control if mag 6 is visible. 

# Define the RGB values for different types of stars
class StarColourIndex:
    O_Type = (140, 176, 255) # Blue
    B_Type = (170, 191, 255) # Blue-White
    A_Type = (202, 215, 255) # White
    F_Type = (248, 247, 255) # Yellow-White
    G_Type = (255, 233, 12) # Yellow
    K_Type = (255, 165, 12) # Orange
    M_Type = (255, 100, 12) # Red
class CIndex:
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    GREEN = (0,255,0)
    GREEN2 = (0,225,0)
    GREEN3 = (0,195,0)
    RED = (255,0,0)
    CYAN = (0,255,255)
    LIGHTCYAN = (178,235,242)

    GREY = (128,128,128)
    YELLOW = (255,255,0)
    BLUE = (0,0,255)
    ORANGE = (255, 165, 0)
    NAVY = (0, 0, 128)
# List of star types and their RGB values
star_list = [
    StarColourIndex.O_Type,
    StarColourIndex.B_Type,
    StarColourIndex.A_Type,
    StarColourIndex.F_Type,
    StarColourIndex.G_Type,
    StarColourIndex.K_Type,
    StarColourIndex.M_Type,
]
canvas_width, canvas_height = 3000, 3000  # Large off-screen canvas size
# Functions

def draw_star_surfaces(color):    
    RADIUS = 100
    NUMIMAGES = 1  # The number of images to create, the more images, the more variants in the images
    TR = 8         # The twinkle level, this is used to change the colour of each image very slightly 
    
    # Surface to draw on using a constant radius value
    star_surface = []
    
    # i starts at RADIUS and is reduced as the loop progresses. 
    for j in range (NUMIMAGES):
        star_surface.append(pygame.Surface((RADIUS*2, RADIUS*2), pygame.SRCALPHA))
        for i in range(RADIUS, 0, -1):
        #
            if i < RADIUS // 2:
                gradient_color = (255-(j*TR), 255-(j*TR), 255-(j*TR))
            elif i < RADIUS // 4:
                mix_ratio = (i - RADIUS // 4) / (RADIUS // 4)
                gradient_color = [int(255-(j*TR) + (color_component - 255) * mix_ratio) for color_component in color]
            else:
                mix_ratio = (i - RADIUS // 2) / (RADIUS // 2)
                gradient_color = [int(color_component * (1 - mix_ratio)-(j*TR)) for color_component in color]

            gradient_color = tuple(max(0, min(255, c)) for c in gradient_color) 			   # Keep in range of 0-255
            pygame.gfxdraw.filled_circle(star_surface[j], RADIUS, RADIUS, i, gradient_color)   # Draw the circle

    return star_surface


def initialize_pygame():
    pygame.init()

    screenInfo = pygame.display.Info()
    bestHeight = screenInfo.current_h-100
    pygame.display.set_caption("Holographic Star Test Main")
    screen = pygame.display.set_mode((bestHeight, bestHeight))

    clock = pygame.time.Clock()
    clock.tick(FPS)
    return screen, clock, bestHeight

def create_canvas():
    canvas = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    canvas.fill(CIndex.BLACK)
    return canvas

def drawScreenUpdate(screen,canvas,bestHeight):
    scaled_canvas = pygame.transform.smoothscale(canvas, (bestHeight, bestHeight))
    screen.blit(scaled_canvas, (0, 0))   
    pygame.display.flip()
    
def star_mag_size_scaling1(canvas,placeholder=None):

# Create a 2D array of canvas. Rows are different sizes, cols are different brightness
    """
    starcanvas [MAG0 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG1 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG2 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG3 Size][Brighness] [Brighness] [Brighness]

    """
    MAG_RANGE = 7  # 0 to 6

    rows, cols = MAG_RANGE,len(canvas)
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]        

    for x in range(rows):
        for y in range(cols):
            scaling_factor = BF ** (6 - x) if x < 6 else 1
            radius = int(BRM6 * math.sqrt(scaling_factor))
            canvas2D[x][y] = pygame.transform.smoothscale(canvas[y],(radius,radius))
               
    return canvas2D

def star_mag_size_scaling(canvas):
    """
    Create a 2D array where each row represents stars of different sizes
    based on their absolute magnitude. This version handles half-magnitude
    steps and limits the magnitude range from 0 to 10.
    
    Parameters:
    - canvas: A list of Pygame surface objects (images of stars) to be resized.
    
    Returns:
    - canvas2D: A 2D list where each element is a Pygame surface object
                representing a resized star image.
    """
    MAG_START = 0  # Starting magnitude
    MAG_END = 10   # Ending magnitude
    MAG_STEP = 0.5 # Step for magnitudes (half-magnitude steps)
    MAG_REF = 10   # Reference magnitude for the base radius
    RADIUS_REF = 4 # Radius for the reference magnitude
    
    # Calculate number of rows based on the range and step
    rows = int((MAG_END - MAG_START) / MAG_STEP + 1)  # Rows is the number of different star colours
    cols = len(canvas)      # This is the number of variants of each colour are in the list. 
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]
    
    mag = MAG_START
    for row in range(rows):
        for img_index in range(cols):
            # Calculate the scaling factor relative to the reference magnitude
            scaling_factor = 10 ** ((MAG_REF - mag) / 6)
            radius = max(1, int(RADIUS_REF * scaling_factor))
            
            # Resize the star image based on the calculated radius
            canvas2D[row][img_index] = pygame.transform.smoothscale(canvas[img_index], (radius, radius))
            print ("row = ",row," y = ",img_index," radius = ",radius)

        mag += MAG_STEP  # Move to the next magnitude step

    return canvas2D


def draw_sun(sun,index):
# draws the sun at the centre of the image
    screen=pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    screen.fill(CIndex.BLACK)

    offset = sun[index][1].get_width() / 2
    screen.blit(twinkle_star(sun[0]), (canvas_width/2-offset, canvas_height/2-offset), special_flags=pygame.BLEND_ADD)
 #   screen.blit(scale_labels['P1'], (canvas_width//5, 50))
    return screen

def twinkle_star(elements):
    if not elements:  # Check if the list is empty
        return None   # Or raise an exception, depending on how you want to handle this case
    return random.choice(elements)

def main():
    pygame.init()
    
    screen, clock, bestHeight= initialize_pygame()
    canvas = create_canvas()
    
    sun = star_mag_size_scaling(draw_star_surfaces(StarColourIndex.K_Type))


    # Get the 2D array of resized star images
    index=0
    # Main loop
    running = True
    while running:
        
        index+=0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Display the images
        x_offset = 100 + index
        y_offset = 50 + index
        y_spacing = 150
        
        for row in range(len(sun)):
            for col in range(len(sun[row])):
                if sun[row][col] is not None:
                    canvas.blit(sun[row][col], (x_offset + (row * 110), y_offset + row * y_spacing))

#                canvas.blit(draw_sun(sun,1),(0,0),special_flags=pygame.BLEND_ADD)
#        canvas.blit(draw_sun(sun),2,(0,0),special_flags=pygame.BLEND_ADD)


        drawScreenUpdate(screen,canvas,bestHeight)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
