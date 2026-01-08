from skyfield.api import load
import pygame

# These index constants are assignment order dependent. Change with caution
class SIndex:
    HIP = 0
    MAGNITUDE = 1
    RA_DEGREES = 2
    DEC_DEGREES = 3
    PARALLAX_MAS = 4
    RA_MAS_PER_YEAR = 5
    DEC_MAS_PER_YEAR = 6
    DISTANCE_PARSECS = 7
    ABS_MAG = 8
    COLOR_K_R = 9
    COLOR_K_G = 10
    COLOR_K_B = 11
    Dx = 12
    Dy = 13
    Dz = 14
    GLON = 15
    GLAT = 16
    RA_HOURS = 17
    EPOCH_YEAR = 18
    STAR_TYPE = 19
    X = 20
    Y = 21

class FIndex:
    VERYLARGE = 200
    LARGE = 150
    MEDIUM = 75
    SMALL = 50
    VERYSMALL = 25


class CIndex:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    GREEN2 = (0, 225, 0)
    GREEN3 = (0, 195, 0)
    RED = (255, 0, 0)
    CYAN = (0, 255, 255)
    LIGHTCYAN = (178, 235, 242)
    GREY = (128, 128, 128)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)
    NAVY = (0, 0, 128)

class StarColourIndex:
    O_Type = (140, 176, 255) # Blue
    B_Type = (170, 191, 255) # Blue-White
    A_Type = (202, 215, 255) # White
    F_Type = (248, 247, 255) # Yellow-White
    G_Type = (255, 233, 12) # Yellow
    K_Type = (255, 165, 12) # Orange
    M_Type = (255, 100, 12) # Red

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

# Constants for transformation, in degrees
RA_NGP = 192.859508
Dec_NGP = 27.128336
l_NCP = 122.932
screen_width = screen_height = 0
canvas_width = canvas_height = 0

def set_size_screen(width, height):
    global  screen_width, screen_height
    screen_width, screen_height = width, height

def set_size_canvas(size):
    global canvas_width, canvas_height
    canvas_width = canvas_height = size * 5

def get_size_screen():
    return screen_width, screen_height

def get_size_canvas():
    return canvas_width, canvas_height

def printsize():
    print("screen :" + str(screen_width)+ " " +str(screen_height))
    print("canvas :" +  str(canvas_width)+ " " +str(canvas_height) )


# Global variable initialization
pygame.init()
screen_info = pygame.display.Info()
# screen_width, screen_height = screen_info.current_w, screen_info.current_h - 60
set_size_screen(screen_info.current_w, screen_info.current_h - 60)
# canvas_width = canvas_height = max(screen_width, screen_height) *  2
set_size_canvas(max(screen_width, screen_height))
shift_x, shift_y, shift_z = 0, 0, 0
center_x = center_y = 0
prev_shift_x, prev_shift_y, prev_shift_z = 0, 0, 0
timescale = load.timescale()
BF = 2.512  # Brightness factor Created a bigger size difference between stars on the screen
BRM6 = 4  # Base radius for magnitude 6 stars, this will control if mag 6 is visible.


star_coordinates = {}  # Dictionary to store star coordinates
clicked_star_hip = None  # Variable to store the HIP ID of the clicked star
clicked_stars = []  # Global variable to store the list of clicked stars
star_coordinates_clicked = None

def set_star_coordinates_clicked(coord):
    global star_coordinates_clicked
    star_coordinates_clicked = coord

def get_star_coordinates_clicked():
    return star_coordinates_clicked

def set_clicked_star_hip(value):
    global clicked_star_hip
    clicked_star_hip = value

def get_clicked_star_hip():
    return clicked_star_hip

def set_star_coordinates(coordinates):
    global star_coordinates
    star_coordinates = coordinates

def get_star_coordinates():
    return star_coordinates

def set_clicked_stars(stars):
    global clicked_stars
    clicked_stars = stars

def get_clicked_stars():
    return clicked_stars


FPS = 20  # Frames per second
lat, long = 53.34, -5.26
when = '2000-01-01 00:00'

# Star Labels
SIRIUS_HIP = 32349
POLARIS_HIP = 11767
BETELGEUSE_HIP = 27989
APLHACENTAURI_HIP = 71683
GC_HIP = 99999
SOL_HIP = 99998


# File handling
column_names_for_csv = ["HIP", "MAGNITUDE", "RA_DEGREES", "DEC_DEGREES", "PARALLAX_MAS", "RA_MAS_PER_YEAR", "DEC_MAS_PER_YEAR",
                        "DISTANCE_PARSECS", "ABS_MAG", "COLOR_K_R", "COLOR_K_G", "COLOR_K_B", "Dx", "Dy", "Dz","GLON", "GLAT",
                        "RA_HOURS", "EPOCH_YEAR", "stereo_X", "stereo_Y"]
header_string = ",".join(column_names_for_csv)

