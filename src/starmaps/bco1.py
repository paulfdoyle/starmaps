import pygame
import pandas as pd
import numpy as np
import random
from skyfield.api import load
import math
from math import *
from pathlib import Path
from pyquaternion import Quaternion
import pygame.gfxdraw
import warnings
from numba import jit
from numba import njit
from astroquery.simbad import Simbad
import ctypes
from ctypes import wintypes
import platform

warnings.filterwarnings("ignore")

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "processed"
ASSETS_DIR = REPO_ROOT / "assets" / "images"
OUTPUT_DIR = ASSETS_DIR / "generated"
DEFAULT_DATA_FILE = DATA_DIR / "updated_merged_star_exo_data.json"
LEGACY_DATA_FILE = REPO_ROOT / "datasets" / "star_database_colors.json"

observerPOS = (0,0,1)
output_dir = str(OUTPUT_DIR)
global_timescale = load.timescale()
pygame.font.init()
menu_font = pygame.font.SysFont('Consolas', 14, bold=True)  # Further reduced font size to fit buttons
# Slider parameters
slider_x = 50
slider_y = 800
slider_width = 400
slider_height = 5
circle_min_radius = 5
circle_max_radius = 15
# Circle's initial position and radius
circle_x = slider_x
circle_y = slider_y
circle_radius = circle_max_radius
TWINKLE_INTERVAL_MS = 200
BRIGHTNESS_MIN = -10
BRIGHTNESS_MAX = 10
BRIGHTNESS_SLIDER_X = slider_x
BRIGHTNESS_SLIDER_Y = slider_y + 40
BRIGHTNESS_SLIDER_WIDTH = slider_width
BRIGHTNESS_SLIDER_HEIGHT = 5
BRIGHTNESS_CIRCLE_RADIUS = 8

# Define arrow button parameters
arrow_button_width = 50
arrow_button_height = 50
# Time interval for auto-repeat (in milliseconds)
repeat_interval = 100  # How fast the auto-repeat occurs (lower is faster)

# Position for increase and decrease arrow buttons
decrease_button_pos = (100, 800)  # Example position for decrease button (left arrow)
increase_button_pos = (200, 800)  # Example position for increase button (right arrow)

MENU_OPTIONS = ["Stars with Exoplanets", "Super Giant Stars", "Stars like our Sun", "All Stars"]
MENU_LEFT_MARGIN = 100
MENU_TOP_MARGIN = 400
MENU_BUTTON_WIDTH = 250
MENU_BUTTON_HEIGHT = 50
MENU_SPACING = 20
SLIDER_HIT_PADDING = 20

try:
    profile  # exists when kernprof is running the script
except NameError:
    def profile(func):
        return func  # Return the function unchanged if not profiling

canvas_width, canvas_height = 1920, 1080  # Large off-screen canvas size
screen_width, screen_height = 1000,1000     # default size
BF = 2.512  # brightness factor Created a bigger size difference between stars on the screen
BRM6 = 4  # Base radius for magnitude 6 stars, this will control if mag 6 is visible.
FPS = 90  # Frames per second
JSON_FILE = str(LEGACY_DATA_FILE)  # Legacy data path; prefer DEFAULT_DATA_FILE
ScreenScaler = 0.9
MAG_OFFSET = 0

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
    STAR_TYPE = 17
    NUM_EXOs = 18
    NAME = 19
    DESCRIPTION = 20
    RAHRS = 21
    EPOC = 22


class CIndex:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    GREEN2 = (0, 225, 0)
    GREEN3 = (0, 195, 100)
    RED = (255, 0, 0)
    CYAN = (0, 255, 255)
    LIGHTCYAN = (178, 235, 242)
    GREY = (128, 128, 128)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)
    NAVY = (0, 0, 128)





class FIndex:
    VERYLARGE = 200
    LARGE = 150
    MEDIUM = 75
    SMALL = 50
    VERYSMALL = 25

class StarColourIndex:
    O_Type = {"rgb": (140, 176, 255), "description": "Blue O-Type Star"}
    B_Type = {"rgb": (170, 191, 255), "description": "Blue-White B-Type Star"}
    A_Type = {"rgb": (202, 215, 255), "description": "White A-Type Star"}
    F_Type = {"rgb": (248, 247, 255), "description": "Yellow-White F-Type Star"}
    G_Type = {"rgb": (255, 233, 12), "description": "Yellow G-Type Star"}
    K_Type = {"rgb": (255, 165, 12), "description": "Orange K-Type Star"}
    M_Type = {"rgb": (255, 100, 12), "description": "Red M-Type Star"}

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


class StarApparentMagIndex:
    MagPlus6point5 = 20  # +6.5
    MagPlus6 = 19  # +6
    MagPlus5point5 = 18  # +5.5
    MagPlus5 = 17  # +5
    MagPlus4point5 = 16  # +4.5
    MagPlus4 = 15  # +4
    MagPlus3point5 = 14  # +3.5
    MagPlus3 = 13  # +3
    MagPlus2point5 = 12  # +2.5
    MagPlus2 = 11  # +2
    MagPlus1point5 = 10  # +1.5
    MagPlus1 = 9  # +1
    MagPlus0point5 = 8  # +0.5
    MagPlus0 = 7  # 0
    MagMinus0point5 = 6  # -0.5
    MagMinus1 = 5  # -1
    MagMinus1point5 = 4  # -1.5
    MagMinus2 = 3  # -2
    MagMinus2point5 = 2  # -2.5
    MagMinus3 = 1  # -3
    MagMinus3point5 = 0  # -4


# Create a dictionary of magnitude values to indices
mag_to_index = {
    6.5: StarApparentMagIndex.MagPlus6point5,
    6: StarApparentMagIndex.MagPlus6,
    5.5: StarApparentMagIndex.MagPlus5point5,
    5: StarApparentMagIndex.MagPlus5,
    4.5: StarApparentMagIndex.MagPlus4point5,
    4: StarApparentMagIndex.MagPlus4,
    3.5: StarApparentMagIndex.MagPlus3point5,
    3: StarApparentMagIndex.MagPlus3,
    2.5: StarApparentMagIndex.MagPlus2point5,
    2: StarApparentMagIndex.MagPlus2,
    1.5: StarApparentMagIndex.MagPlus1point5,
    1: StarApparentMagIndex.MagPlus1,
    0.5: StarApparentMagIndex.MagPlus0point5,
    0: StarApparentMagIndex.MagPlus0,
    -0.5: StarApparentMagIndex.MagMinus0point5,
    -1: StarApparentMagIndex.MagMinus1,
    -1.5: StarApparentMagIndex.MagMinus1point5,
    -2: StarApparentMagIndex.MagMinus2,
    -2.5: StarApparentMagIndex.MagMinus2point5,
    -3: StarApparentMagIndex.MagMinus3,
    -4: StarApparentMagIndex.MagMinus3point5
}

# Create a dictionary with manually set values for each index from 0 to 20
index_parsecs = {
    0: 1,
    1: 2, 
    2: 10,
    3: 50,
    4: 75,
    5: 125,
    6: 250,
    7: 500,
    8: 1000,
    9: 1500

}
key_to_scale = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9
}

# Function to get the value using the index (key)
def get_pasec_from_index(index):
    return int(index_parsecs.get(index))

def clamp_mag_offset(value):
    return max(BRIGHTNESS_MIN, min(BRIGHTNESS_MAX, value))

def brightness_offset_to_x(offset):
    clamped = clamp_mag_offset(offset)
    ratio = (clamped - BRIGHTNESS_MIN) / (BRIGHTNESS_MAX - BRIGHTNESS_MIN)
    return BRIGHTNESS_SLIDER_X + ratio * BRIGHTNESS_SLIDER_WIDTH

def update_brightness_offset_from_mouse(mouse_x):
    clamped_x = max(BRIGHTNESS_SLIDER_X, min(mouse_x, BRIGHTNESS_SLIDER_X + BRIGHTNESS_SLIDER_WIDTH))
    ratio = (clamped_x - BRIGHTNESS_SLIDER_X) / BRIGHTNESS_SLIDER_WIDTH
    return int(round(BRIGHTNESS_MIN + ratio * (BRIGHTNESS_MAX - BRIGHTNESS_MIN)))


# Convert the dictionary to arrays for Numba compatibility
mags = np.array(list(mag_to_index.keys()))
indices = np.array(list(mag_to_index.values()))

@jit(nopython=True)
def get_index_from_magnitude(magnitude):
    """
    Get the index for a given magnitude value based on the StarApparentMagIndex class.
    The magnitude is mapped to the closest defined magnitude.

    Parameters:
    - magnitude (float): The magnitude value to be mapped.

    Returns:
    - int: The corresponding index.
    """
    # Calculate the absolute difference between the input magnitude and all known magnitudes
    abs_diff = np.abs(mags - magnitude)
    
    # Find the index of the minimum difference
    closest_index = np.argmin(abs_diff)
    
    # Return the corresponding index from the indices array
    return indices[closest_index]


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
        raise ValueError("zero_dimension must be 'x', 'y', or 'z'")

    # Generate the angles
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
    points = np.round(points, 3)

    return points


def color_distance(rgb1, rgb2):
    """Calculate the Euclidean distance between two RGB colors."""
    return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5

### Functions needed for the workflow: Galactic -> 3D -> 3D Mods -> Galactic -> RADEC

#
def galactic_to_cartesian(l, b, d):
    """
    Convert Galactic coordinates to Cartesian coordinates.
    l: Galactic longitude in degrees
    b: Galactic latitude in degrees
    d: Distance
    """
    # Convert angles from degrees to radians
    l_rad = np.radians(l)
    b_rad = np.radians(b)

    # Cartesian coordinates conversion
    x = d * math.cos(b_rad) * math.cos(l_rad)
    y = d * math.cos(b_rad) * math.sin(l_rad)
    z = d * math.sin(b_rad)

    return x, y, z


# Load the data into a DataFrame then convert it to NumpyArray
# We are reading in more data from the file than required since
# we may find a use for it later
def load_custom_star_data(json_file_path):
    try:
        print("Loading data from file")
        required_columns = [
            'hip', 'mag', 'ra_decdeg', 'dec_decdeg', 'plx', 'pmra', 'pmdec', 'dist', 'absmag',
            'kR', 'kG', 'kB', 'x', 'y', 'z', "GLON", "GLAT","C","sy_pnum","proper","info"
        ]
        df = pd.read_json(json_file_path)
        df = df[required_columns]
        # print("1-->",df.iloc[0])

        df.columns = (
            'hip', 'magnitude', 'ra_degrees', 'dec_degrees', 'parallax_mas', 'ra_mas_per_year',
            'dec_mas_per_year', 'distance_parsecs', 'absolutem', 'kR', 'kG', 'kB', '3dx', '3dy', '3dz', "GLON", "GLAT", "StarType","NumExo","name","Description"
        )
        # print("2-->",df.iloc[0])

        # Remove samples with missing data to elimiate checks later
        df = df.replace('', np.nan)

        # # Identify rows with missing 'ra_degrees', 'dec_degrees', or 'magnitude' before removing them
        # missing_values_df = df[df['ra_degrees'].isnull() | df['dec_degrees'].isnull() | df['magnitude'].isnull()]
        # missing_hr_ids = missing_values_df['hr']

        # # Save the missing HIP IDs to a text file
        # missing_hr_ids.to_csv('data/processed/missing_stars.txt', index=False, header=False)

        df.dropna(inplace=True)
        glon = df['GLON'].to_numpy()
        glat = df['GLAT'].to_numpy()
        ra_deg, dec_deg = galactic_to_equatorial_proper(glon, glat)
        df['ra_degrees'] = ra_deg
        df['dec_degrees'] = dec_deg

        l_rad = np.radians(glon)
        b_rad = np.radians(glat)
        dist = df['distance_parsecs'].to_numpy()
        df['3dx'] = dist * np.cos(b_rad) * np.cos(l_rad)
        df['3dy'] = dist * np.cos(b_rad) * np.sin(l_rad)
        df['3dz'] = dist * np.sin(b_rad)
        df = df.assign(ra_hours=df['ra_degrees'] / 15.0, epoch_year=2000)
        # print("3-->",df.iloc[0])

        star_data_array = df.to_numpy()  # Convert DataFrame to NumPy array

        return star_data_array

    except Exception as e:
        print(f"An error occurred while loading or processing the star data: {e}")
        return None


@jit(nopython=True)
def galactic_to_equatorial_proper(l, b):
    # Constants
    RA_NGP = 192.859508  # RA of the North Galactic Pole
    DEC_NGP = 27.128336  # DEC of the North Galactic Pole
    L_NCP = 122.931919  # Galactic Longitude of the North Celestial Pole

    # Convert angles from degrees to radians
    l_rad = np.radians(l)
    b_rad = np.radians(b)
    RA_NGP_rad = np.radians(RA_NGP)
    DEC_NGP_rad = np.radians(DEC_NGP)

    # Calculate the declination in radians
    sin_b = np.sin(b_rad)
    cos_b = np.cos(b_rad)
    sin_DEC_NGP = np.sin(DEC_NGP_rad)
    cos_DEC_NGP = np.cos(DEC_NGP_rad)
    sin_DEC = sin_b * sin_DEC_NGP + cos_b * cos_DEC_NGP * np.cos(l_rad - np.radians(L_NCP))
    DEC = np.arcsin(sin_DEC)  # in radians

    # Calculate the right ascension in radians
    sin_l_minus_L = np.sin(l_rad - np.radians(L_NCP))
    cos_l_minus_L = np.cos(l_rad - np.radians(L_NCP))
    y = sin_l_minus_L * cos_b
    x = cos_b * sin_DEC_NGP * cos_l_minus_L - sin_b * cos_DEC_NGP
    RA = RA_NGP_rad + np.arctan2(y, x)  # in radians

    # Convert radians to degrees
    RA_deg = (np.degrees(RA) - 180) % 360
    DEC_deg = np.degrees(DEC)

    return RA_deg, DEC_deg


@jit(nopython=True)
def convert_to_cartesian_numpy(ra_hours, ra_minutes, ra_seconds, dec_degrees, dec_minutes, dec_seconds, distance):
    ra = (ra_hours + ra_minutes / 60 + ra_seconds / 3600) * (np.pi / 12)  # Convert RA to radians
    dec = (dec_degrees + dec_minutes / 60 + dec_seconds / 3600) * (np.pi / 180)  # Convert DEC to radians
    x = distance * np.cos(dec) * np.cos(ra)
    y = distance * np.cos(dec) * np.sin(ra)
    z = distance * np.sin(dec)
    return x, y, z

@jit(nopython=True)
def ra_dec_distance_to_cartesian(ra_deg, dec_deg, distance_parsecs):
    """
    Convert RA, DEC, and distance in parsecs to Cartesian coordinates.

    Parameters:
    - ra_deg: Right Ascension in decimal degrees
    - dec_deg: Declination in decimal degrees
    - distance_parsecs: Distance in parsecs

    Returns:
    - A tuple of (x, y, z) representing the Cartesian coordinates.
    """
    # Convert RA and DEC from degrees to radians
    #  print ("about to check ",ra_deg)
    ra_rad = math.radians(ra_deg)
    dec_rad = math.radians(dec_deg)

    # Calculate Cartesian coordinates with distance
    x = distance_parsecs * math.cos(dec_rad) * math.cos(ra_rad)
    y = distance_parsecs * math.cos(dec_rad) * math.sin(ra_rad)
    z = distance_parsecs * math.sin(dec_rad)

    return (x, y, z)

@jit(nopython=True)
def convert_ra_dec(ra_deg, dec_deg, distance):
    print("RA DEG", ra_deg)
    print("DEC_D", dec_deg)

    # Convert RA to hours
    ra_hours = ra_deg / 15.0
    ra_h = int(ra_hours)
    ra_m = int((ra_hours - ra_h) * 60)
    ra_s = ((ra_hours - ra_h) * 60 - ra_m) * 60

    # DEC conversion remains the same
    dec_d = int(dec_deg)
    dec_m = int(abs(dec_deg - dec_d) * 60)
    dec_s = (abs(dec_deg - dec_d) * 60 - dec_m) * 60

    x_numpy, y_numpy, z_numpy = convert_to_cartesian_numpy(ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, distance)

    # Format RA and DEC into strings
    # ra_str = f"{ra_h:02d}h{ra_m:02d}m{ra_s:05.2f}s"
    # dec_str = f"{dec_d:+03d}°{dec_m:02d}'{dec_s:05.2f}\""

    return x_numpy, y_numpy, z_numpy

@jit(nopython=True)
def moveWorld(x, y, z, dist_parasec, moveDist):
    x_move, y_move, z_move = moveDist
    new_x = x + x_move
    new_y = y + y_move
    new_z = z + z_move

    ra_new, dec_new = cartesian_to_ra_dec(new_x, new_y, new_z)
    newDist = distance_3d(0, 0, 0, new_x, new_y, new_z)

    # print("New Dist = ",newDist)
    # print(f"Cartesian coordinates with distance: x={x}, y={y}, z={z}")
    # print ("ra=",ra_new,dec_new)
    return ra_new, dec_new, newDist

@jit(nopython=True)
def cartesian_to_ra_dec(x, y, z):
    """
    Convert Cartesian coordinates to RA and DEC in decimal degrees.

    Parameters:
    - x, y, z: Cartesian coordinates

    Returns:
    - A tuple (ra_deg, dec_deg) representing the Right Ascension and
      Declination in decimal degrees.
    """
    # Calculate RA in radians
    ra_rad = math.atan2(y, x)
    # Ensure RA is in the range [0, 2π]
    ra_rad = ra_rad if ra_rad >= 0 else ra_rad + 2 * math.pi

    # Calculate DEC in radians
    distance = math.sqrt(x ** 2 + y ** 2 + z ** 2)  # Calculate the distance to normalize z
    dec_rad = math.asin(z / distance)

    # Convert RA and DEC from radians to degrees
    ra_deg = math.degrees(ra_rad)
    dec_deg = math.degrees(dec_rad)

    return (ra_deg, dec_deg)


@jit(nopython=True)
def calculate_apparent_magnitude(absolute_magnitude, distance_parsecs,star3dpos,observerPOS):
    """
    Calculate the apparent magnitude of a celestial object given its absolute magnitude
    and distance in parsecs.

    Args:
        absolute_magnitude (float): The absolute magnitude of the celestial object.
        distance_parsecs (float): The distance to the celestial object in parsecs.

    Returns:
        float: The apparent magnitude of the celestial object.
    """
 
    distance_parsecs = calculate_distance(observerPOS,star3dpos)
    if distance_parsecs <= 0:
        distance_parsecs = 1e-3

    apparent_magnitude = absolute_magnitude + 5 * (math.log10(distance_parsecs) - 1) - MAG_OFFSET
    return apparent_magnitude
  
 #   return absolute_magnitude


# Take in a standard canvas (which can have 1-N stars with slightly different brightness and then build a series of versions
# one for each magnitude ranging from Mag 0 to Mag 6

def star_mag_size_scaling(canvas,screen_width):
    """
    Create a 2D array where each row represents stars of different sizes
    based on their absolute magnitude, adjusted for screen resolution.
    This version handles half-magnitude steps and limits the magnitude range from 0 to 10.

    Parameters:
    - canvas: A list of Pygame surface objects (images of stars) to be resized.
    - screen_width: The width of the screen (resolution) to adjust the star sizes accordingly.

    Returns:
    - canvas2D: A 2D list where each element is a Pygame surface object
                representing a resized star image.
    """
    MAG_START = 0  # Starting magnitude
    MAG_END = 10  # Ending magnitude
    MAG_STEP = 0.5  # Step for magnitudes (half-magnitude steps)
    MAG_REF = 10  # Reference magnitude for the base radius
    BASE_SCREEN_WIDTH = 1400  # Reference screen width for RADIUS_REF = 1
    RADIUS_REF = 1  # Radius for the reference magnitude

    # Calculate the scaling factor based on the screen width
    resolution_scaling_factor = max(1, round(screen_width / BASE_SCREEN_WIDTH))

    print (resolution_scaling_factor,screen_width, BASE_SCREEN_WIDTH)
    
    # Calculate number of rows based on the range and step
    rows = int((MAG_END - MAG_START) / MAG_STEP + 1)  # Rows is the number of different star colours
    cols = len(canvas)  # This is the number of variants of each colour are in the list.
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]

    mag = MAG_START
    for row in range(rows):
        for img_index in range(cols):
            # Calculate the scaling factor relative to the reference magnitude
            magnitude_scaling_factor = 10 ** ((MAG_REF - mag) / 6)
            radius = max(1, int(RADIUS_REF * magnitude_scaling_factor * resolution_scaling_factor))

            # Resize the star image based on the calculated radius
            canvas2D[row][img_index] = pygame.transform.smoothscale(canvas[img_index], (radius, radius))
            # print ("row = ",row," mag index = ",img_index," radius = ",radius)

        mag += MAG_STEP  # Move to the next magnitude step

    return canvas2D

# This function take the colour for a star as a parameter in the form of a tuple (255, 255, 255)
# It draws the star on a single Pygame surface 100pixels wide and returns a pointer to the star surface.
# The star can be scaled by another function to match different magnitudes
#
# The function dras a series of filled circles starting from the largest to the smallest
# The outer part of the star contains the colour of the star, while the centre is white
# There are 3 distinct areas drawn, the outer section, the middle and the inner section
# The middle and outer sections modify the circle colour to be more faint the larger the radius

def draw_star_surfaces(color):
    RADIUS = 100
    NUMIMAGES = 6 # The number of images to create, the more images, the more variants in the images
    TR = 5  # The twinkle level, this is used to change the colour of each image very slightly

    # Surface to draw on using a constant radius value
    star_surface = []

    # i starts at RADIUS and is reduced as the loop progresses.
    for j in range(NUMIMAGES):
        star_surface.append(pygame.Surface((RADIUS * 2, RADIUS * 2), pygame.SRCALPHA))
        for i in range(RADIUS, 0, -1):
            if i < RADIUS // 4:
                gradient_color = (255 - (j * TR), 255 - (j * TR), 255 - (j * TR))
            elif i < RADIUS // 2:
                mix_ratio = (i - RADIUS // 4) / (RADIUS // 4)
                gradient_color = [int(255 - (j * TR) + (color_component - 255) * mix_ratio) for color_component in color]
            else:
                mix_ratio = (i - RADIUS // 2) / (RADIUS // 2)
                gradient_color = [int(color_component * (1 - mix_ratio) - (j * TR)) for color_component in color]

            gradient_color = tuple(max(0, min(255, c)) for c in gradient_color)  # Keep in range of 0-255
            pygame.gfxdraw.filled_circle(star_surface[j], RADIUS, RADIUS, i, gradient_color)  # Draw the circle

    return star_surface  # the star_surface is a 2D array of surfaces  []

# This builds an array of surfaces
def buildStarImageDB(screen_width):
    canvas_set = []  # Empty list to store surfaces
    for star in star_list:
        star_rgb= star["rgb"]
        canvas_set.append(star_mag_size_scaling(draw_star_surfaces(star_rgb), screen_width))  
    return canvas_set



# Rotate object using quaternion
def rotate_object(quaternion, axis, degrees):
    angle = np.radians(degrees)
    if axis == 'x':
        delta_rotation = Quaternion(axis=[1, 0, 0], angle=angle)
    elif axis == 'y':
        delta_rotation = Quaternion(axis=[0, 1, 0], angle=angle)
    elif axis == 'z':
        delta_rotation = Quaternion(axis=[0, 0, 1], angle=angle)
    return quaternion * delta_rotation  # Quaternion multiplication is non-commutative


def perspective_projection(x, y, z, f):
    if z == 0:
        z = 1
    x_prime = (f * x) / z
    y_prime = (f * y) / z
    return (x_prime, y_prime)

FONT_CACHE = {}

# create a surface with text on it
def writeText(text, color, fontsize):
    font = FONT_CACHE.get(fontsize)
    if font is None:
        font = pygame.font.Font(None, fontsize)
        FONT_CACHE[fontsize] = font
    return font.render(text, True, color)

    # Functions
def initialize_pygame():
    pygame.init()

    # Detect the operating system
    current_os = platform.system()

    if current_os == "Windows":
        # Import ctypes for Windows API calls
        user32 = ctypes.windll.user32
        monitors = []

        # RECT structure
        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long),
            ]

        # MONITORINFOEX structure
        class MONITORINFOEX(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_long),
                ("rcMonitor", RECT),
                ("rcWork", RECT),
                ("dwFlags", ctypes.c_long),
                ("szDevice", ctypes.c_wchar * 32),
            ]

        # Monitor enumeration callback function
        def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            mi = MONITORINFOEX()
            mi.cbSize = ctypes.sizeof(MONITORINFOEX)
            user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))
        
            monitor_width = mi.rcMonitor.right - mi.rcMonitor.left
            monitor_height = mi.rcMonitor.bottom - mi.rcMonitor.top

            monitors.append((monitor_width, monitor_height))
            return True

        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_double
        )

        # Enumerate monitors
        user32.EnumDisplayMonitors(0, 0, MonitorEnumProc(monitor_enum_proc), 0)

        # Calculate total width and maximum height
        total_width = sum([m[0] for m in monitors])
        total_height = max([m[1] for m in monitors])

        print(f"Detected total width: {total_width}, total height: {total_height} across {len(monitors)} monitors.")

    elif current_os == "Darwin":  # macOS
        # macOS-specific imports
        from AppKit import NSScreen

        # Get the total resolution across all screens on macOS
        total_width = 0
        total_height = 0

        # Get all connected screens
        screens = NSScreen.screens()
        for screen in screens:
            total_width += int(screen.frame().size.width)
            total_height = max(total_height, int(screen.frame().size.height))  # Take the maximum height

        print(f"Detected total width: {total_width}, total height: {total_height} across {len(screens)} screens.")

    else:
        # Default fallback for Linux or other platforms
        total_width = 1920  # Example width
        total_height = 1080  # Example height

    # Set up the Pygame window to cover all screens
    screen = pygame.display.set_mode((total_width, total_height), pygame.NOFRAME,pygame.SRCALPHA)
    pygame.display.set_caption(f"Pygame Across Multiple Monitors on {current_os}")



    screen_info = pygame.display.Info()

    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.RESIZABLE,pygame.SRCALPHA)
    screen = pygame.display.set_mode((total_width, total_height), pygame.NOFRAME,pygame.SRCALPHA)
    pygame.display.set_caption(f"Holographic Star Chart Main {current_os}")
    clock = pygame.time.Clock()
    clock.tick(FPS)
    return screen, clock, total_height   

def create_canvas():
    canvas = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    canvas.fill(CIndex.BLACK)
    return canvas

@profile
def drawScreenUpdate(screen, canvas, bestHeight):
    original_width, original_height = canvas.get_size()
    screen_width, screen_height = screen.get_size()
    width_scale = screen_width / original_width
    
    height_scale = screen_height / original_height
    
    # Use the smaller scaling factor to maintain aspect ratio
    scale_factor = min(width_scale, height_scale)
    # Calculate the new dimensions
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)    
 #   scaled_canvas = pygame.transform.scale(canvas, (new_width, new_height))

 #   print ("new width/height = ",new_width,new_height)
    #    Calculate position to center the scaled canvas on the screen
    x_position = (screen_width - new_width) // 2
    y_position = (screen_height - new_height) // 2
#    screen.fill((0, 0, 0))

 #   screen.blit(scaled_canvas, (x_position, y_position))
 #   screen.blit(canvas, (x_position, y_position))


    return x_position, y_position, scale_factor

def initialise_control_varaiables():
    control_vars = {
        'draw_frame': True,
        'draw_sun': True,
        'draw_labels': True,
        'draw_scale': True,
        'test_color': True,
        'optimise': True,
        'MagType':    "APP",
        'ViewScale':  1,   # this is in parsecs
        'MaxParsecIndex' : 0, # Initialise to begin
        'MagOffset':   0,
        'brightness_changed': False,
        'Position':   (0,0,20),
        'sphere': 20,
        'filter_mode': len(MENU_OPTIONS) - 1,
        'scale': 0 # The scale needs to be worked out based on the radius of the frame circle. 

    }
    return control_vars



@jit(nopython=True)
def rotate_points_numba(points, q):
    """
    Rotate a batch of points using a quaternion with Numba.

    Parameters:
    - points: An array of shape (N, 3) where N is the number of points.
    - q: A NumPy array representing the quaternion for rotation.

    Returns:
    - Rotated points as an array of shape (N, 3).
    """
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
    rotated_points = np.zeros_like(points)
    for i in range(points.shape[0]):
        point = points[i]
        p = np.array([0, point[0], point[1], point[2]])
        q_p = np.zeros(4)

        q_p[0] = q[0] * p[0] - q[1] * p[1] - q[2] * p[2] - q[3] * p[3]
        q_p[1] = q[0] * p[1] + q[1] * p[0] + q[2] * p[3] - q[3] * p[2]
        q_p[2] = q[0] * p[2] - q[1] * p[3] + q[2] * p[0] + q[3] * p[1]
        q_p[3] = q[0] * p[3] + q[1] * p[2] - q[2] * p[1] + q[3] * p[0]

        rotated_p = np.zeros(4)
        rotated_p[0] = q_p[0] * q_conj[0] - q_p[1] * q_conj[1] - q_p[2] * q_conj[2] - q_p[3] * q_conj[3]
        rotated_p[1] = q_p[0] * q_conj[1] + q_p[1] * q_conj[0] + q_p[2] * q_conj[3] - q_p[3] * q_conj[2]
        rotated_p[2] = q_p[0] * q_conj[2] - q_p[1] * q_conj[3] + q_p[2] * q_conj[0] + q_p[3] * q_conj[1]
        rotated_p[3] = q_p[0] * q_conj[3] + q_p[1] * q_conj[2] - q_p[2] * q_conj[1] + q_p[3] * q_conj[0]

        rotated_points[i] = rotated_p[1:]  # Ignore the w component

    return rotated_points


@jit(nopython=True)
def calculate_distance(point1, point2):
    """
    Calculate the Euclidean distance between two points in 3D space.
    
    Parameters:
    point1 (tuple): A tuple of three coordinates (x1, y1, z1)
    point2 (tuple): A tuple of three coordinates (x2, y2, z2)
    
    Returns:
    float: The distance between the two points
    """
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance


@jit(nopython=True)
def check_distance(distance, sphere):
    return distance > sphere or distance <= 1

@jit(nopython=True)
def is_point_behind_viewpoint(point, viewpoint=(0, 0, 0), view_direction=(0, 0, 1)):
    """
    Determine if a 3D point is behind the viewpoint and not visible.
    
    Parameters:
    point (tuple): A tuple of three coordinates (x, y, z) representing the point in 3D space.
    viewpoint (tuple): A tuple of three coordinates (x, y, z) representing the viewpoint.
                       Default is the origin (0, 0, 0).
    view_direction (tuple): A tuple of three coordinates (x, y, z) representing the direction
                            the viewpoint is facing. Default is along the positive Z-axis (0, 0, 1).
    
    Returns:
    bool: True if the point is behind the viewpoint, False otherwise.
    """
    px, py, pz = point
    vx, vy, vz = viewpoint
    dx, dy, dz = view_direction
    
    # Calculate the vector from the viewpoint to the point
    vector_to_point = (px - vx, py - vy, pz - vz)
    
    # Calculate the dot product of the view direction and the vector to the point
    dot_product = vector_to_point[0] * dx + vector_to_point[1] * dy + vector_to_point[2] * dz
    
    # If the dot product is negative, the point is behind the viewpoint
    return dot_product < 0
@njit
def should_draw_star(stardistance, currentradius,mag):
    if currentradius < 100:
        return True
    if stardistance < currentradius/10 and mag >14:
        return False
    return True


def create_circle_surfaces(color, max_radius):
    surfaces = []
    for radius in range(2, max_radius*2):
        diameter = 2 * radius
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (radius, radius), radius)
        scaled_size = max(1, radius // 2)
        newsurface = pygame.transform.smoothscale(surface, (scaled_size, scaled_size))
        surfaces.append(newsurface)
    return surfaces

@profile
def update_star_positions(sprites, new_positions,scale):
    global observerPOS
    for sprite, new_position in zip(sprites, new_positions):
        sprite.set_position_3d(new_position,scale,observerPOS)

def update_sprites_positions(sprites, new_positions):
    for sprite, new_pos in zip(sprites, new_positions):
        sprite.set_position_3d(new_pos)


@jit(nopython=True)
def set_2d_position(pos_3d,scale,canvas_offset):
    pos_2d = (pos_3d[0] * scale + canvas_offset[0],
    pos_3d[1] * scale + canvas_offset[1])
    return pos_2d


@jit(nopython=True)
def set_frame_based_on_distance1(pos_3d, reference_point_3d,maxdistance,mindistance,num_frames):    
    x1, y1, z1 = pos_3d[0], pos_3d[1], pos_3d[2]
    x2, y2, z2 = reference_point_3d[0],reference_point_3d[1], reference_point_3d[2]
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) *100
    frame_index = int((maxdistance - distance) / (maxdistance - mindistance) * (num_frames - 1))
    if frame_index < 0:
        frame_index = 0
    if frame_index > num_frames -1:
        frame_index = num_frames -1  

    return frame_index

@jit(nopython=True)
def projection3D_to_2D (x, y, z,scale,canvas_center):
    d = 500  # Example projection distance
    if z != -d:  # To avoid division by zero when z == -d
        projected_x = (x * d) / (z + d) * scale * ScreenScaler + canvas_center[0]
        projected_y = (y * d) / (z + d) * scale * ScreenScaler + canvas_center[1]
    else:
        projected_x = x * scale * ScreenScaler + canvas_center[0]
        projected_y = y * scale * ScreenScaler + canvas_center[1]
    return (projected_x, projected_y)


class StarSprite(pygame.sprite.Sprite):
    def __init__(self, surface_array, start_pos, visibility, glon, glat, scale, canvas_center,
                 parsecs, abs_mag, star_type_index, exo_planet_num, hr, hip, hd, visibility_radius,name,description, star_type_name):
        super().__init__()
        self.surface_array = surface_array  # Reference to external 2D list or array [magnitude][variant]
        self.variant = 0
        self.num_variants = len(self.surface_array[0])
        self.pos_3d = np.array(start_pos)
        self.visible = visibility
        self.glon = glon
        self.glat = glat
        self.scale = scale
        self.canvas_center = canvas_center
        self.image = self.surface_array[8][self.variant]  # use a default mag index
        self.rect = None
        self.Parsecs = parsecs  # This is a distance from a specific position, can be SOL, or a relative position
        self.ABS_Mag = abs_mag
        self.StarType = star_type_index
        self.StarTypeName = star_type_name
        self.ExoPlanetNum = exo_planet_num
        self.HR = hr
        self.HIP = hip
        self.HD = hd
        self.NAME = name
        self.Description = description
        self.observerPOS = (0,0,1)
        self.last_observer_pos = None
        self.last_twinkle_ms = 0
        self.update_2d_position()

        self.info = (
            self.NAME
            + "\nReference: "
            + str(self.HIP)
            + "\nStar Type: "
            + self.StarTypeName
            + "\nExoplanets: "
            + str(self.ExoPlanetNum)
            + "\nDistance to Sun: "
            + f"{self.Parsecs:.2f} pc"
        )
        self.infoVisible = False
        self.info_surface = None
        self.info_surface_scaled = None
        self.info_scale_factor = None

        self.visibility_radius = visibility_radius
        #self.create_info_surface()
        
    def setInfoVisible(self, visible):
        """
        Set the visibility of the star's information.
        
        Args:
            visible (bool): True to make the info visible, False to hide it.
        """
        self.infoVisible = visible

    def create_info_surface(self):
        if self.info_surface is not None:
            return
        # Create a font for rendering text
        font = pygame.font.Font(None, FIndex.VERYSMALL)  # Adjust the font size as needed

        # Render the text to a surface, splitting lines
        lines = self.info.split('\n')
        max_width = 0
        total_height = 0
        text_surfaces = []
        
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))  # White text
            text_surfaces.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
            total_height += text_surface.get_height()

        # Calculate padding and border thickness
        padding = 10  # Space around the text
        border_thickness = 5  # Thickness of the white border

        # Create a surface to hold the entire text block, including padding and border
        surface_width = max_width + 2 * padding
        surface_height = total_height + 2 * padding
        info_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        # Fill the surface with a barely transparent background
        info_surface.fill((0, 0, 0, 128))  # RGBA (0, 0, 0, 128) -> Semi-transparent black

        # Draw a thick white border with rounded corners
        pygame.draw.rect(info_surface, (255, 255, 255), (0, 0, surface_width, surface_height), border_thickness, border_radius=10)

        # Blit the individual text surfaces onto the main surface
        y_offset = padding
        for text_surface in text_surfaces:
            info_surface.blit(text_surface, (padding, y_offset))
            y_offset += text_surface.get_height()

        # Store the created surface and return it along with its 2D position
        self.info_surface = info_surface
        self.info_pos = self.pos_2d  # Adjust position as needed



    def create_info_surface_old(self):
        # Create a font for rendering text
        font = pygame.font.Font(None, FIndex.SMALL)  # Adjust the font size as needed

        # Render the text to a surface, splitting lines
        lines = self.info.split('\n')
        max_width = 0
        total_height = 0
        text_surfaces = []
        
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))  # White text
            text_surfaces.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
            total_height += text_surface.get_height()

        # Create a surface to hold the entire text block
        info_surface = pygame.Surface((max_width, total_height))
        info_surface.fill((0, 0, 0, 128))  # Semi-transparent black background

        # Blit the individual text surfaces onto the main surface
        y_offset = 0
        for text_surface in text_surfaces:
            info_surface.blit(text_surface, (0, y_offset))
            y_offset += text_surface.get_height()

        # Return the info surface and the 2D position where it should be drawn
        self.info_surface = info_surface
    

    def is_visible(self):
        return self.Parsecs <= self.visibility_radius

    def set_visibility_radius(self, new_radius):
        self.visibility_radius = new_radius   

    def set_position_3d(self, new_pos, scale, observerPos, magindex=None):
        self.scale = scale
        self.pos_3d = new_pos
        self.observerPOS = observerPos
        if magindex is not None:
            self.magindex = magindex
            self.last_observer_pos = observerPos
        self.update_2d_position(recompute_mag=magindex is None)

    def update_2d_position(self, recompute_mag=True):
        now_ms = pygame.time.get_ticks()
        if now_ms - self.last_twinkle_ms >= TWINKLE_INTERVAL_MS:
            self.variant = self.select_random_variant()
            self.last_twinkle_ms = now_ms

        self.pos_2d = set_2d_position(self.pos_3d, self.scale, self.canvas_center)

        if recompute_mag and self.last_observer_pos != self.observerPOS:
            self.magindex = get_index_from_magnitude(
                calculate_apparent_magnitude(self.ABS_Mag, self.Parsecs, self.pos_3d, self.observerPOS)
            )
            self.last_observer_pos = self.observerPOS

        new_image = self.surface_array[self.magindex][self.variant]
        if self.rect is None:
            self.image = new_image
            self.rect = self.image.get_rect(center=self.pos_2d)
        elif new_image is not self.image:
            self.image = new_image
            if self.rect.size != self.image.get_size():
                self.rect = self.image.get_rect(center=self.pos_2d)
            else:
                self.rect.center = self.pos_2d
        else:
            self.rect.center = self.pos_2d



    def update_2d_position_old(self):
        self.variant = self.select_random_variant()
        print (self.variant)
        x, y, z = self.pos_3d
        self.pos_2d = self.project_3d_to_2d(x, y, z)        
        if self.visible:
            self.image = self.surface_array[self.magnitude][self.variant]
            self.rect = self.image.get_rect(center=self.pos_2d)
        else:
            self.image = None
            self.rect = None


    def select_random_variant(self):
        # Select a random variant based on the number of variants available for the current magnitude
        variant_count = self.num_variants
        return random.randint(0, variant_count - 1)

    def project_3d_to_2d(self, x, y, z):

        return (projection3D_to_2D (x, y, z,self.scale,self.canvas_center))
        # d = 500  # Example projection distance
        # if z != -d:  # To avoid division by zero when z == -d
        #     projected_x = (x * d) / (z + d) * self.scale * ScreenScaler + self.canvas_center[0]
        #     projected_y = (y * d) / (z + d) * self.scale * ScreenScaler + self.canvas_center[1]
        # else:
        #     projected_x = x * self.scale * ScreenScaler + self.canvas_center[0]
        #     projected_y = y * self.scale * ScreenScaler + self.canvas_center[1]
        # return (projected_x, projected_y)
    



    # def project_3d_to_2d(self, x, y, z):
    #     projected_x = x * self.scale * ScreenScaler + self.canvas_center[0]
    #     projected_y = y * self.scale * ScreenScaler + self.canvas_center[1]


    def set_visibility(self, visibility):
        self.visible = visibility
        self.update_2d_position()

 
    def set_distance (self, newdist_parsecs):
        self.Parsecs = newdist_parsecs
        self.magnitude = get_index_from_magnitude(calculate_apparent_magnitude(self.ABS_Mag, self.Parsecs,self.pos_3d,self.observerPOS))

    def set_magnitude(self):
        self.magnitude = get_index_from_magnitude(calculate_apparent_magnitude(self.ABS_Mag, self.Parsecs,self.pos_3d,self.observerPOS))
        self.update_2d_position()

    def set_variant(self, variant):
        self.variant = variant
        self.update_2d_position()

    def set_glon(self, glon):
        self.glon = glon

    def set_glat(self, glat):
        self.glat = glat

    def update(self):
        self.update_2d_position()

    def update_rect_position(self):
        if self.image is not None and self.rect is not None:
            self.rect.center = self.pos_2d
    def print_values(self):
        print("3D Position: ", self.pos_3d)
        print("Scale: ", self.scale)
        print("Canvas Center: ", self.canvas_center)
        print("2D Position: ", self.pos_2d)
        print("Rect: ", self.rect)
        print("Parsecs: ", self.Parsecs)
        print("Absolute Magnitude: ", self.ABS_Mag)
        print("Star Type: ", self.StarType)
        print("HIP: ", self.HIP)
        print("Magnitude Index: ", self.magindex)


class FrameSprite(pygame.sprite.Sprite):
    def __init__(self, surfaces, pos_3d, scale, canvas_offset,reference_point_3d):
        super().__init__()
        self.surfaces = surfaces
        self.num_frames = len(self.surfaces)
        self.current_frame = self.num_frames -1
        self.pos_3d = pos_3d
        self.scale = scale
        self.canvas_offset = canvas_offset
        self.reference_point_3d = reference_point_3d
        self.projection_distance = 3
        self.update_2d_position()
        self.visible = True
        self.image = self.surfaces[self.current_frame]
        self.rect = self.image.get_rect(center=self.pos_2d)
        self.maxdistance = self.calculate_max_distance()*100
        self.mindistance = self.calculate_min_distance()*100

        self.num_frames = len(self.surfaces)
    def set_position_3d(self, pos_3d):
        self.pos_3d = pos_3d
        self.update_2d_position()
        self.update_frame_based_on_distance()
        self.update_rect_position()  # Ensure rect position is updated

    def set_frame(self, frame_index):
        if 0 <= frame_index < len(self.surfaces):
            self.current_frame = frame_index
            self.image = self.surfaces[self.current_frame]
 #           self.update_rect_position()  # Ensure rect position is updated
        else:
            raise IndexError("Frame index out of range", frame_index)

    def set_reference_point_3d(self, ref_point_3d):
        self.reference_point_3d = ref_point_3d
        self.update_frame_based_on_distance()


    def calculate_max_distance(self):
        # Calculate the Euclidean distance between two 3D points
        x1, y1, z1 = self.reference_point_3d
        x2, y2, z2 = (0,0,-1)
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)  
    
    def calculate_min_distance(self):
        # Calculate the Euclidean distance between two 3D points
        x1, y1, z1 = self.reference_point_3d
        x2, y2, z2 = (0,0,1)
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)  
    
    def update_frame_based_on_distance(self):
        self.set_frame (set_frame_based_on_distance1(self.pos_3d, self.reference_point_3d,self.maxdistance,self.mindistance,self.num_frames))    

    def update_2d_position(self):
        self.pos_2d = (set_2d_position (self.pos_3d, self.scale,self.canvas_offset))

    def update_rect_position(self):
        if self.image is not None and self.rect is not None:
            self.rect.center = self.pos_2d

    def set_canvas_offset(self, canvas_offset):
        self.canvas_offset = canvas_offset
        self.update_2d_position()
        self.update_rect_position()

    def set_visibility(self, visible):
        self.visible = visible
# Function to get the star description by index
def get_star_description_by_index(index):
    if 0 <= index < len(star_list):
        return star_list[index]["description"]
    else:
        return "Invalid index"
    

@jit(nopython=True)
def calculate_line_points(start_point, end_point, num_points=10):
    """
    Calculate a series of points from start_point to end_point.
    
    Args:
    start_point (tuple): The starting point (x, y, z).
    end_point (tuple): The ending point (x, y, z).
    num_points (int): The number of points to calculate.
    
    Returns:
    np.ndarray: A NumPy array of shape (num_points, 3) representing the points.
    """
    # Create arrays for x, y, and z coordinates from start to end
    x_coords = np.linspace(start_point[0], end_point[0], num_points)
    y_coords = np.linspace(start_point[1], end_point[1], num_points)
    z_coords = np.linspace(start_point[2], end_point[2], num_points)
    
    # Stack the coordinates to form a (num_points, 3) array
    points = np.column_stack((x_coords, y_coords, z_coords))
    
    return points

def batch_create_frame_sprites(surfaces, positions,scale,canvas_centre,reference_point):
    sprites = pygame.sprite.Group()
    for pos in positions:
        sprite = FrameSprite(surfaces, pos,scale,canvas_centre,reference_point)
        sprites.add(sprite)
    return sprites

def generate_star_sprites(control_vars, canvas, canvas_set, star_data_np):
    canvas_center = (canvas.get_width() // 2, canvas.get_height() // 2)
    scale = control_vars['scale'] * ScreenScaler
    sprites = pygame.sprite.Group()
    star_points = []
    sprite_index_map = {}
    max_star_type = len(canvas_set) - 1

    for star in star_data_np:
        hip_id = int(star[SIndex.HIP])  # Convert HIP ID to integer
        star_type_raw = int(star[SIndex.STAR_TYPE])
        if star_type_raw < 0 or star_type_raw > max_star_type:
            star_type_raw = 0
        sprite = StarSprite(
            canvas_set[star_type_raw],
            (star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz]),
            True,
            star[SIndex.GLON],
            star[SIndex.GLAT],
            scale,
            canvas_center,
            star[SIndex.DISTANCE_PARSECS],
            star[SIndex.ABS_MAG],
            star_type_raw,
            star[SIndex.NUM_EXOs],
            0,
            star[SIndex.HIP],
            0,
            control_vars['sphere'],
            star[SIndex.NAME],
            star[SIndex.DESCRIPTION],
            get_star_description_by_index(star_type_raw)
        )
        sprites.add(sprite)
        star_point = np.array([star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz]])
        star_points.append(star_point)

        # Map HIP ID to the sprite
        sprite_index_map[hip_id] = sprite

    star_points = np.array(star_points)
    return star_points, sprites, sprite_index_map

def generate_star_sprites_old(control_vars, canvas, canvas_set, star_data_np):
    canvas_center = (canvas.get_width() // 2, canvas.get_height() // 2)
    scale = control_vars['scale'] * ScreenScaler
    sprites = pygame.sprite.Group()
    print("Building star sprites..")
    star_points = []

    for star in star_data_np:
        sprite = StarSprite(
            canvas_set[int(star[SIndex.STAR_TYPE])],
            (star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz]),
            True,
            star[SIndex.GLON],
            star[SIndex.GLAT],
            scale,
            canvas_center,
            star[SIndex.DISTANCE_PARSECS],
            star[SIndex.ABS_MAG],
            star[SIndex.STAR_TYPE],
            star[SIndex.NUM_EXOs],
            0,
            star[SIndex.HIP],
            0, 
            control_vars['sphere'],
            star[SIndex.NAME],
            star[SIndex.DESCRIPTION],
            get_star_description_by_index(int(star[SIndex.STAR_TYPE]))
            
        )
        sprites.add(sprite)
        star_point = np.array([star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz]])
        star_points.append(star_point)

    star_points = np.array(star_points)
    return star_points, sprites


@profile
@jit(nopython=True)
def is_visible(position, visibility_radius):
    return np.linalg.norm(position) <= visibility_radius

@profile
def update_visibility(sprites, visibility_radius, custom_sprites, option, filter_masks=None, dist_sq=None, sprite_list=None):
    custom_sprites.empty()

    if filter_masks is None or dist_sq is None or sprite_list is None:
        for sprite in sprites:
            if option == 0:
                if sprite.ExoPlanetNum > 0:  # exoplanet filter
                    if is_visible(sprite.pos_3d, visibility_radius):
                        custom_sprites.add(sprite)
            elif option == 1:
                if sprite.StarType == 6:  # Large Reg Giants filter
                    if is_visible(sprite.pos_3d, visibility_radius):
                        custom_sprites.add(sprite)
            elif option == 2:
                if sprite.StarType == 4:  # Earth Type Stars filter
                    if is_visible(sprite.pos_3d, visibility_radius):
                        custom_sprites.add(sprite)
            else:
                if is_visible(sprite.pos_3d, visibility_radius):
                    custom_sprites.add(sprite)
        return custom_sprites, None

    radius_sq = visibility_radius * visibility_radius
    if option == 0:
        base_mask = filter_masks["exo"]
    elif option == 1:
        base_mask = filter_masks["giant"]
    elif option == 2:
        base_mask = filter_masks["sun"]
    else:
        base_mask = None

    if base_mask is None:
        visible_mask = dist_sq <= radius_sq
    else:
        visible_mask = base_mask & (dist_sq <= radius_sq)

    visible_indices = np.nonzero(visible_mask)[0]
    for idx in visible_indices:
        custom_sprites.add(sprite_list[idx])

    return custom_sprites, visible_indices

def compute_magindices_for_indices(visible_indices, xy_sq, z_vals, abs_mags, observer_pos, all_star_points):
    if visible_indices is None or visible_indices.size == 0:
        return np.array([], dtype=int)

    if observer_pos[0] == 0 and observer_pos[1] == 0:
        dz = z_vals[visible_indices] - observer_pos[2]
        dist = np.sqrt(xy_sq[visible_indices] + dz * dz)
    else:
        points = all_star_points[visible_indices]
        dx = points[:, 0] - observer_pos[0]
        dy = points[:, 1] - observer_pos[1]
        dz = points[:, 2] - observer_pos[2]
        dist = np.sqrt(dx * dx + dy * dy + dz * dz)

    dist = np.maximum(dist, 1e-3)
    apparent = abs_mags[visible_indices] + 5 * (np.log10(dist) - 1) - MAG_OFFSET
    abs_diff = np.abs(mags[:, None] - apparent[None, :])
    closest = np.argmin(abs_diff, axis=0)
    return indices[closest]

# @profile
# def update_visibility(sprites, visibility_radius, custom_sprites):
#     SUN = 99998.0

#     custom_sprites.empty()  # Clear the existing group instead of creating a new one

#     for sprite in sprites:
#         sprite.set_visibility_radius(visibility_radius)
#         if sprite.is_visible():
#             custom_sprites.add(sprite)
#         if sprite.HIP == SUN:
#             sprite.set_distance(1)

#     return custom_sprites

def update_visibility_old(sprites, visibility_radius):

    custom_sprites = CustomSpriteGroup()
    SUN = 99998.0
#    visible_sprites = pygame.sprite.Group()
    for sprite in sprites:
        sprite.set_visibility_radius(visibility_radius)
        if sprite.is_visible():
            custom_sprites.add(sprite)
        if sprite.HIP == SUN:
            sprite.set_distance(1)
            #print ("Found the Sun, ",sprite.HIP, sprite.scale, sprite.magindex, visibility_radius)

    return custom_sprites

class CustomSpriteGroup(pygame.sprite.Group):
    def draw(self, surface):
        sprites = self.sprites()
        for spr in sprites:
            surface.blit(spr.image, spr.rect, special_flags=pygame.BLEND_ADD)
            if spr.infoVisible:
                radius = max(spr.rect.width, spr.rect.height) // 2 + 4
                pygame.draw.circle(surface, CIndex.CYAN, spr.rect.center, radius, width=1)


    def drawInfo(self, surface, parsecs):
        sprites = self.sprites()
        for spr in sprites:
            # Check if the sprite has a reference distance set
            if not hasattr(spr, 'ref_distance'):
                # Set the reference distance to the current parsecs value the first time the label is drawn
                spr.ref_distance = parsecs
            
            # Calculate the scale factor based on the reference distance
            scale_factor = spr.ref_distance / parsecs

            # Limit the scale factor to a maximum of 1 (to prevent scaling larger than the original size)
            scale_factor = min(scale_factor, 1.0)

            # Skip drawing the label if the scale factor is less than 0.5 (meaning the size would be halved or more)
            if scale_factor < 0.25:
                continue

            # Create the info surface (assuming this generates the original size)
            spr.create_info_surface()

            scale_key = round(scale_factor, 3)
            if spr.info_surface_scaled is None or spr.info_scale_factor != scale_key:
                spr.info_surface_scaled = pygame.transform.scale(
                    spr.info_surface,
                    (
                        int(spr.info_surface.get_width() * scale_factor),
                        int(spr.info_surface.get_height() * scale_factor)
                    )
                )
                spr.info_scale_factor = scale_key
            scaled_info_surface = spr.info_surface_scaled

            # Calculate the position where the scaled surface should be blitted
            # Offset it to the right and slightly below the star, without covering it
            offset_x = spr.rect.right + 10  # Move it 10 pixels to the right of the star
            offset_y = spr.rect.bottom + 10  # Move it 10 pixels below the star

            # Blit the scaled surface
            surface.blit(scaled_info_surface, (offset_x, offset_y))


    def drawInfo_old(self,surface,parsecs):
        sprites = self.sprites()
        for spr in sprites:
            spr.Parsecs
            spr.create_info_surface()
            offset_rect = spr.rect.move(30, 10)
            surface.blit(spr.info_surface, offset_rect) #, special_flags=pygame.BLEND_ADD)

    def clearInfo(self):
        sprites = self.sprites()
        for spr in sprites:
            spr.setInfoVisible(False)


def update_visibility_old(sprites, visibility_radius):

    custom_sprites = CustomSpriteGroup()
    SUN = 99998.0
#    visible_sprites = pygame.sprite.Group()
    for sprite in sprites:
        sprite.set_visibility_radius(visibility_radius)
        if sprite.is_visible():
            custom_sprites.add(sprite)
        if sprite.HIP == SUN:
            sprite.set_distance(1)
            #print ("Found the Sun, ",sprite.HIP, sprite.scale, sprite.magindex, visibility_radius)

    return custom_sprites

def find_star_by_position(sprites, x, y ):
    found = False  # use this to only return the first hit on a star
    custom_sprites = CustomSpriteGroup()
    for star in sprites:
        if star.infoVisible:
            custom_sprites.add(star)
        variance = abs(star.pos_2d[0]-star.rect[0])/2
        if variance < 5:
            variance = 5
        if not found:
            if abs(star.pos_2d[0] - x) <= variance and abs(star.pos_2d[1] - y) <= variance:
                found = True
                if star.infoVisible:
                    star.setInfoVisible(False)
                    custom_sprites.remove(star)
                    print ("removed ", star.NAME)

                else:
                    star.setInfoVisible(True)
                    custom_sprites.add(star)


    return custom_sprites

               
    #         if star.ExoPlanetNum > 0:
    #             return star.NAME + "\nReference: " + str(star.HIP) + "\nStar Type: "+ star.StarTypeName + "\nExoplanets: " + str(star.ExoPlanetNum)
    #         return star.NAME + "\n Reference: " + str(star.HIP) + "\nStar Type: "+ star.StarTypeName +    "\nExoplanets: 0\n"


def generate_frame_sprites(control_vars,canvas):
    
    canvas_center = (canvas.get_width() // 2, canvas.get_height() // 2)
    scale = control_vars['scale']*ScreenScaler

    frame_surfaces = create_circle_surfaces(CIndex.CYAN, 6 ) 
    frame_surfaces1 = create_circle_surfaces(CIndex.RED, 6)
    
    frame_surfaces2 = create_circle_surfaces(CIndex.GREEN3, 4) 


    points_circle_frame1 = generate_3d_circle_points(1, 1, 'z')
 #   points_circle_frame2 = generate_3d_circle_points(0.99, 4, 'z')
    green_circle_sprites_group1  = batch_create_frame_sprites(frame_surfaces2, points_circle_frame1, scale,canvas_center,(0,0,20))
 #   green_circle_sprites_group2  = batch_create_frame_sprites(frame_surfaces2, points_circle_frame2, scale,canvas_center,(0,0,20))


    points_3dz = generate_3d_circle_points(1, 2, 'z')
    points_3dx = generate_3d_circle_points(1, 2, 'x')
    points_3dz1 = generate_3d_circle_points(0.5, 2, 'z')
    points_3dy = generate_3d_circle_points(1, 2, 'y')
    line_x = calculate_line_points((0.01,0,0),(1,0,0),100)
    line_x1 = calculate_line_points((-1,0,0),(0,0,0),100)
    line_y = calculate_line_points((0,-1,0),(0,1,0),100)

    all_frame_points1 = np.concatenate((points_3dz,points_3dx,points_3dz1, points_3dy, line_x1, line_y ) )

    red_line_sprites_group  = batch_create_frame_sprites(frame_surfaces1, line_x, scale,canvas_center,(0,0,20))

 
  
  
    all_frame_sprites_group = batch_create_frame_sprites(frame_surfaces,all_frame_points1, scale,canvas_center,(0,0,20) )
    all_frame_sprites_group.add(red_line_sprites_group.sprites())
    all_frame_sprites_group.add(green_circle_sprites_group1.sprites())
 #   all_frame_sprites_group.add(green_circle_sprites_group2.sprites())
    all_frame_points = np.concatenate((all_frame_points1,line_x) )

    return all_frame_points, all_frame_sprites_group

def showFPS(FPS_text,frame_count,start_time):
    frame_count += 1
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time
    if elapsed_time > 1000:  # 1000 ms = 1 second
        actual_fps = frame_count / (elapsed_time / 1000.0)
        FPS_text = f"Actual FPS: {actual_fps:.2f}"
        frame_count = 0
        start_time = current_time
    return FPS_text, frame_count, start_time


# Handle the keyboard events
def handle_events(control_vars, key_to_scale, parsecs, current_orientation,rotate,x_offset,y_offset,canvas_scale,parsecs_changed,decrease_button_rect,increase_button_rect,mouse_held,last_repeat_time,quit_button_rect,menu_rects):
    global observerPOS, circle_x, circle_radius
    scaling_factor = 1.05
    max_parsecs = 1500

    scaled_mouse_x,scaled_mouse_y = None, None
    clearInfo = False

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
            return False, parsecs, current_orientation, rotate, scaled_mouse_x, scaled_mouse_y, clearInfo, parsecs_changed, mouse_held, last_repeat_time
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            #control_vars, parsecs = menu.handle_mouse_click((scaled_mouse_x,scaled_mouse_y),control_vars, parsecs)

            if event.button in (4, 5):
                if event.button == 4:
                    control_vars['MagOffset'] = clamp_mag_offset(control_vars['MagOffset'] + 1)
                else:
                    control_vars['MagOffset'] = clamp_mag_offset(control_vars['MagOffset'] - 1)
                control_vars['brightness_changed'] = True
                continue

            if quit_button_rect and quit_button_rect.collidepoint(mouse_x, mouse_y):
                pygame.quit()
                return False, parsecs, current_orientation, rotate, scaled_mouse_x, scaled_mouse_y, clearInfo, parsecs_changed, mouse_held, last_repeat_time

            if event.button == 1:
                click_consumed = False
                change = handle_arrow_click(event, decrease_button_rect, increase_button_rect)
                if change != 0:
                    if change < 0:
                        parsecs *= scaling_factor  # Decrease button clicked
                    elif change > 0:
                        parsecs *= 1 / scaling_factor  # Increase button clicked
                    parsecs_changed = True

                    if parsecs > max_parsecs:
                        parsecs = max_parsecs
                    if parsecs <= 0:
                        parsecs = 1

                    control_vars['Position'] = (0, 0, parsecs)
                    observerPOS = (0, 0, parsecs)
                    click_consumed = True

                for index, rect in enumerate(menu_rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if control_vars['filter_mode'] != index:
                            control_vars['filter_mode'] = index
                            parsecs_changed = True
                        click_consumed = True
                        break

                is_on_slider = (
                    slider_x <= mouse_x <= slider_x + slider_width
                    and slider_y - SLIDER_HIT_PADDING <= mouse_y <= slider_y + SLIDER_HIT_PADDING
                )
                if is_on_slider and not decrease_button_rect.collidepoint(mouse_x, mouse_y) and not increase_button_rect.collidepoint(mouse_x, mouse_y):
                    circle_x, circle_radius, position_value = update_circle_position_and_size(mouse_x)
                    if control_vars['ViewScale'] != position_value:
                        parsecs_changed = True
                        control_vars['ViewScale'] = position_value
                        parsecs = get_pasec_from_index(control_vars['ViewScale'])
                        control_vars['Position'] = (0, 0, parsecs)
                        observerPOS = (0, 0, parsecs)
                    click_consumed = True

                is_on_brightness = (
                    BRIGHTNESS_SLIDER_X <= mouse_x <= BRIGHTNESS_SLIDER_X + BRIGHTNESS_SLIDER_WIDTH
                    and BRIGHTNESS_SLIDER_Y - SLIDER_HIT_PADDING <= mouse_y <= BRIGHTNESS_SLIDER_Y + SLIDER_HIT_PADDING
                )
                if is_on_brightness:
                    control_vars['MagOffset'] = clamp_mag_offset(update_brightness_offset_from_mouse(mouse_x))
                    control_vars['brightness_changed'] = True
                    click_consumed = True

                if not click_consumed:
                    scaled_mouse_x = (mouse_x - x_offset) / canvas_scale
                    scaled_mouse_y = (mouse_y - y_offset) / canvas_scale

        if event.type == pygame.MOUSEMOTION and mouse_held:
            mouse_x, mouse_y = event.pos
            is_on_slider = (
                slider_x <= mouse_x <= slider_x + slider_width
                and slider_y - SLIDER_HIT_PADDING <= mouse_y <= slider_y + SLIDER_HIT_PADDING
            )
            if is_on_slider and not decrease_button_rect.collidepoint(mouse_x, mouse_y) and not increase_button_rect.collidepoint(mouse_x, mouse_y):
                circle_x, circle_radius, position_value = update_circle_position_and_size(mouse_x)
                if control_vars['ViewScale'] != position_value:
                    parsecs_changed = True
                    control_vars['ViewScale'] = position_value
                    parsecs = get_pasec_from_index(control_vars['ViewScale'])
                    control_vars['Position'] = (0, 0, parsecs)
                    observerPOS = (0, 0, parsecs)

            is_on_brightness = (
                BRIGHTNESS_SLIDER_X <= mouse_x <= BRIGHTNESS_SLIDER_X + BRIGHTNESS_SLIDER_WIDTH
                and BRIGHTNESS_SLIDER_Y - SLIDER_HIT_PADDING <= mouse_y <= BRIGHTNESS_SLIDER_Y + SLIDER_HIT_PADDING
            )
            if is_on_brightness:
                control_vars['MagOffset'] = clamp_mag_offset(update_brightness_offset_from_mouse(mouse_x))
                control_vars['brightness_changed'] = True

        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                control_vars['MagOffset'] = clamp_mag_offset(control_vars['MagOffset'] + 1)
            elif event.y < 0:
                control_vars['MagOffset'] = clamp_mag_offset(control_vars['MagOffset'] - 1)
            control_vars['brightness_changed'] = True


           # Handle mouse down and mouse up events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button down
            mouse_held = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left mouse button up
            mouse_held = False
            print ("Setting False")

 
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                pygame.quit()
                return False, parsecs, current_orientation, rotate, scaled_mouse_x, scaled_mouse_y, clearInfo, parsecs_changed, mouse_held, last_repeat_time

            if event.key == pygame.K_m:
                control_vars['MagType'] = "APP" if control_vars['MagType'] == "REL" else "REL"

            if event.key == pygame.K_MINUS:
                parsecs_changed = True
                parsecs *= scaling_factor
                if parsecs > max_parsecs:
                    parsecs = max_parsecs
                control_vars['Position'] = (0, 0, parsecs)
                observerPOS = (0, 0, parsecs)

            if event.key == pygame.K_EQUALS:
                parsecs_changed = True
                parsecs *= 1 / scaling_factor
                if parsecs <= 0:
                    parsecs = 1
                control_vars['Position'] = (0, 0, parsecs)
                observerPOS = (0, 0, parsecs)

            if event.key in key_to_scale:

                parsecs_changed = True
                control_vars['ViewScale'] = key_to_scale[event.key]
                parsecs = get_pasec_from_index(control_vars['ViewScale'])
                control_vars['Position'] = (0, 0, parsecs)
                observerPOS = (0, 0, parsecs)
                view_index = max(0, min(9, control_vars['ViewScale']))
                slider_progress = 1 - (view_index / 9)
                circle_x = slider_x + slider_progress * slider_width
                circle_radius = circle_max_radius - (circle_max_radius - circle_min_radius) * slider_progress


            if event.key == pygame.K_o:
                control_vars['optimise'] = not control_vars['optimise']
                print(f"Frame {'On' if control_vars['optimise'] else 'Off'}")

            if event.key == pygame.K_e:
                observerPOS = (0, 0, 500)
            if event.key == pygame.K_w:
                observerPOS = (0, 0, 10)

            if event.key == pygame.K_f:
                control_vars['draw_frame'] = not control_vars['draw_frame']

            if event.key == pygame.K_s:
                control_vars['draw_sun'] = not control_vars['draw_sun']
                print(f"Sun {'On' if control_vars['draw_sun'] else 'Off'}")

            if event.key == pygame.K_l:
                control_vars['draw_labels'] = not control_vars['draw_labels']
                print(f"Labels {'On' if control_vars['draw_labels'] else 'Off'}")

            if event.key == pygame.K_c:
                clearInfo = True

            if event.key == pygame.K_x:
                rotate = True
                current_orientation = rotate_object(current_orientation, 'x', 1)
            if event.key == pygame.K_b:
                rotate = True
                current_orientation = rotate_object(current_orientation, 'x', -1)
            if event.key == pygame.K_y:
                rotate = True
                current_orientation = rotate_object(current_orientation, 'y', 1)
            if event.key == pygame.K_i:
                rotate = True
                current_orientation = rotate_object(current_orientation, 'y', -1)
            if event.key == pygame.K_z:
                rotate = True
                current_orientation = rotate_object(current_orientation, 'z', 1)
            if event.key == pygame.K_v:
                rotate = True
                current_orientation = rotate_object(current_orientation, 'z', -1)
            if event.key == pygame.K_SPACE:
                rotate = True
                current_orientation = Quaternion()  # Reset rotation

            if event.key == pygame.K_r:
                control_vars['MagOffset'] = clamp_mag_offset(control_vars['MagOffset'] + 1)
                control_vars['brightness_changed'] = True
            if event.key == pygame.K_t:
                control_vars['MagOffset'] = clamp_mag_offset(control_vars['MagOffset'] - 1)
                control_vars['brightness_changed'] = True


   # Handle auto-repeat while mouse is held down
    if mouse_held:
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
        change, last_repeat_time = handle_arrow_hold(mouse_pos, decrease_button_rect, increase_button_rect, last_repeat_time)

        if change != 0:
            print(f"Change: {change}")  # Output 1 for increase, -1 for decrease

            if change < 0:
                parsecs *= scaling_factor  # Decrease button held
            elif change > 0:
                parsecs *= 1 / scaling_factor  # Increase button held
                        
            parsecs_changed = True  # Indicate that parsecs has changed
            
            if parsecs > max_parsecs:
                parsecs = max_parsecs
            if parsecs <= 0:
                parsecs = 1

            control_vars['Position'] = (0, 0, parsecs)
            observerPOS = (0, 0, parsecs)
    return True, parsecs, current_orientation, rotate,scaled_mouse_x, scaled_mouse_y,clearInfo, parsecs_changed, mouse_held, last_repeat_time

def count_stars(sprite_group):
    return len(sprite_group)



def wrap_text(text, font, max_width):
    """Splits the text into lines that fit within the specified width."""
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_surface = font.render(word, True, (0, 0, 0))
        word_width, word_height = word_surface.get_size()
        
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width + font.size(' ')[0]  # Add a space width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width + font.size(' ')[0]
    
    lines.append(' '.join(current_line))
    return lines

def render_text(surface, text, font, color, rect, max_width):
    """Renders the text on the surface with wrapping."""
    y = rect.top
    line_spacing = -2  # Adjust as needed

    lines = wrap_text(text, font, max_width)
    
    for line in lines:
        line_surface = font.render(line, True, color)
        line_width, line_height = line_surface.get_size()
        surface.blit(line_surface, (rect.left, y))
        y += line_height + line_spacing

# Draw a rounded rectangle border (with rounded corners) and hover effect
def draw_rounded_border_button(screen, text, rect, border_color, is_hovered, is_selected=False):
    """
    Draws a button with a green border and rounded edges, without filling the background.
    
    Parameters:
    - screen: Pygame screen to draw the button.
    - text: The text label of the button.
    - rect: The position and size of the button (pygame.Rect).
    - border_color: The color of the border (RGBA).
    - is_hovered: Boolean indicating whether the mouse is hovering over the button.
    - is_selected: Boolean indicating whether the button is selected.
    """
    # If hovered or selected, make the border color brighter and update text color
    if is_selected:
        button_border_color = CIndex.GREEN2
        text_color = CIndex.LIGHTCYAN
    elif is_hovered:
        button_border_color = (border_color[0], border_color[1], border_color[2], 255)  # Fully opaque border on hover
        text_color = CIndex.CYAN # Change text color to cyan when hovered
    else:
        button_border_color = border_color
        text_color = CIndex.WHITE  # Default text color is white

    # Draw the rounded rectangle border (directly on the screen)
    pygame.draw.rect(screen, button_border_color, rect, width=3, border_radius=15)
    
    # Render the text with hover effect
    text_surface = menu_font.render(text, True, text_color)
    
    # Make sure there is no unwanted background by setting the colorkey
    text_surface.set_colorkey((0, 0, 0))  # Ensuring transparency for black (or any specific color)

    # Center the text inside the button rectangle
    text_rect = text_surface.get_rect(center=rect.center)

    # Blit the text directly onto the screen
    screen.blit(text_surface, text_rect)

def build_menu_rects():
    return [
        pygame.Rect(
            MENU_LEFT_MARGIN,
            MENU_TOP_MARGIN + (MENU_BUTTON_HEIGHT + MENU_SPACING) * index,
            MENU_BUTTON_WIDTH,
            MENU_BUTTON_HEIGHT,
        )
        for index in range(len(MENU_OPTIONS))
    ]

def draw_futuristic_menu(screen, selected_index, menu_rects):
    """
    Draws a futuristic-looking menu on the right side of the screen with options.
    """
    hovered_index = -1
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for index, option in enumerate(MENU_OPTIONS):
        rect = menu_rects[index]
        is_hovered = rect.collidepoint(mouse_x, mouse_y)
        is_selected = index == selected_index
        draw_rounded_border_button(screen, option, rect, CIndex.GREEN3, is_hovered, is_selected)
        if is_hovered:
            hovered_index = index

    return hovered_index


def draw_exit_button(screen, rect):
    is_hovered = rect.collidepoint(pygame.mouse.get_pos())
    draw_rounded_border_button(screen, "Exit (Esc)", rect, CIndex.RED, is_hovered)

def draw_arrow_button(screen, rect, direction, is_hovered):
    """
    Draws an arrow button with a green border and transparent background.
    
    Parameters:
    - screen: Pygame screen to draw the button.
    - rect: The position and size of the button (pygame.Rect).
    - direction: "left" for decrease arrow or "right" for increase arrow.
    - is_hovered: Boolean indicating whether the mouse is hovering over the button.
    """
    border_color = CIndex.GREEN if not is_hovered else CIndex.GREEN3  # Green color
    arrow_color = (255, 255, 255)  # White color for the arrow

    # Draw the rounded rectangle border
    pygame.draw.rect(screen, border_color, rect, width=3, border_radius=15)

    # Draw the arrow
    if direction == "left":
        pygame.draw.polygon(screen, arrow_color, [
            (rect.centerx + 10, rect.centery - 10),
            (rect.centerx - 10, rect.centery),
            (rect.centerx + 10, rect.centery + 10)
        ])
    elif direction == "right":
        pygame.draw.polygon(screen, arrow_color, [
            (rect.centerx - 10, rect.centery - 10),
            (rect.centerx + 10, rect.centery),
            (rect.centerx - 10, rect.centery + 10)
        ])
def handle_arrow_hold(mouse_pos, decrease_button_rect, increase_button_rect, last_repeat_time):
    """
    Handles auto-repeat when mouse is held down on the arrow buttons.
       """
    global repeat_interval # How fast the auto-repeat occurs (lower is faster)

    current_time = pygame.time.get_ticks()
    if current_time - last_repeat_time >= repeat_interval:
        if decrease_button_rect.collidepoint(mouse_pos):
            return -1, current_time  # Decrease button held down
        elif increase_button_rect.collidepoint(mouse_pos):
            return 1, current_time  # Increase button held down
    return 0, last_repeat_time  # No change or not enough time has passed


def handle_arrow_click(event, decrease_button_rect, increase_button_rect):
    """
    Handles mouse clicks on the arrow buttons and returns 1 for increase and -1 for decrease.
    """
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button click
        mouse_pos = pygame.mouse.get_pos()
        if decrease_button_rect.collidepoint(mouse_pos):
            return -1  # Decrease button clicked
        elif increase_button_rect.collidepoint(mouse_pos):
            return 1  # Increase button clicked
    return 0  # No change if no button clicked



def update_circle_position_and_size(mouse_x):
    """
    Updates the circle's position and decreases its size as it moves to the right.
    Additionally, returns a value from 9 (large circle) to 0 (small circle) based on the circle's position along the slider.
    """
    # Keep the circle within the bounds of the slider
    new_circle_x = max(slider_x, min(mouse_x, slider_x + slider_width))
    
    # Calculate the size reduction based on the position
    slider_progress = (new_circle_x - slider_x) / slider_width
    new_circle_radius = circle_max_radius - (circle_max_radius - circle_min_radius) * slider_progress

    # Calculate the position value from 9 to 0
    position_value = int((1 - slider_progress) * 9)  # Inverse the progress to map it from 9 to 0

    return new_circle_x, new_circle_radius, position_value


# Function to handle the slider and moving circle
def handle_slider(screen, circle_x, circle_radius):
    """
    Handles drawing the slider and moving the circle based on mouse hover interaction.
    """
    # Draw the slider line
    pygame.draw.line(screen, CIndex.GREEN3, (slider_x, slider_y), (slider_x + slider_width, slider_y), slider_height)

    # Draw the moving circle
    pygame.draw.circle(screen, CIndex.GREEN3, (circle_x, circle_y), circle_radius)

def draw_brightness_slider(screen, mag_offset):
    knob_x = brightness_offset_to_x(mag_offset)
    pygame.draw.line(
        screen,
        CIndex.GREEN3,
        (BRIGHTNESS_SLIDER_X, BRIGHTNESS_SLIDER_Y),
        (BRIGHTNESS_SLIDER_X + BRIGHTNESS_SLIDER_WIDTH, BRIGHTNESS_SLIDER_Y),
        BRIGHTNESS_SLIDER_HEIGHT,
    )
    pygame.draw.circle(
        screen,
        CIndex.GREEN3,
        (int(knob_x), BRIGHTNESS_SLIDER_Y),
        BRIGHTNESS_CIRCLE_RADIUS,
    )


@profile
def main():
     # Initialise Pygame and the Screen for primary display, setting Height and Width to the Height of the canvas
    # bestHeight is set as the width and height of the display screen
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    screen, clock, bestHeight = initialize_pygame()
    canvas_width = bestHeight
    # This is the main surface for all drawing
    #canvas = create_canvas()
    canvas = screen
    global circle_x, circle_radius  # Declare them as global
    global observerPOS
    global MAG_OFFSET

    # Define the rectangles for the buttons
    decrease_button_rect = pygame.Rect(decrease_button_pos, (arrow_button_width, arrow_button_height))
    increase_button_rect = pygame.Rect(increase_button_pos, (arrow_button_width, arrow_button_height))
    quit_button_rect = pygame.Rect(20, 20, 140, 40)
    menu_rects = build_menu_rects()

    mouse_held = False  # Track if the mouse button is being held
    last_repeat_time = pygame.time.get_ticks()  # Track the last time the auto-repeat occurred


    # Initialise variables used to control the user experience
    control_vars = initialise_control_varaiables()
    control_vars['scale'] = (canvas_width//2) / control_vars['ViewScale']
    control_vars['MaxParsecIndex'] = len(index_parsecs)
    parsecs = get_pasec_from_index(control_vars['ViewScale'])     

    current_orientation = Quaternion()
    q_np = np.array([current_orientation.w, current_orientation.x, current_orientation.y, current_orientation.z])
    rotated = True
    parsecs_changed = True





    canvas_center = (canvas.get_width() // 2, canvas.get_height() // 2)
    scale = control_vars['scale'] * ScreenScaler

    # Load the data from the JSOPN file 
    canvas_set = buildStarImageDB(canvas.get_width())

    # Load the data from a file
    #   star_data_np = load_custom_star_data(str(LEGACY_DATA_FILE))

    star_data_np = load_custom_star_data(str(DEFAULT_DATA_FILE))
    if star_data_np is None:
        print("Star data failed to load; exiting.")
        pygame.quit()
        return

    # Now create all of the sprites for the wire-frame and the points for rotation
    all_frame_points, all_frame_sprites_group = generate_frame_sprites(control_vars,canvas)
   
    # Now create all of the sprites for the stars 
    #all_star_points, all_stars_sprites_group = generate_star_sprites(control_vars,canvas, canvas_set,star_data_np)

    all_star_points, all_stars_sprites_group, sprite_index_mapnew = generate_star_sprites(control_vars, canvas, canvas_set, star_data_np)
    sprite_list = list(all_stars_sprites_group)
    dist_sq = np.einsum('ij,ij->i', all_star_points, all_star_points)
    xy_sq = np.einsum('ij,ij->i', all_star_points[:, :2], all_star_points[:, :2])
    z_vals = all_star_points[:, 2]
    abs_mags = np.fromiter((sprite.ABS_Mag for sprite in sprite_list), dtype=float, count=len(sprite_list))
    exo_mask = np.fromiter((sprite.ExoPlanetNum > 0 for sprite in sprite_list), dtype=bool, count=len(sprite_list))
    giant_mask = np.fromiter((sprite.StarType == 6 for sprite in sprite_list), dtype=bool, count=len(sprite_list))
    sun_mask = np.fromiter((sprite.StarType == 4 for sprite in sprite_list), dtype=bool, count=len(sprite_list))
    filter_masks = {"exo": exo_mask, "giant": giant_mask, "sun": sun_mask}
    
    hip_id = 102098.0  # Example HIP ID
    hip_id_int = int(hip_id)  # Convert to integer before lookup 
    if hip_id_int in sprite_index_mapnew:
        star_sprite = sprite_index_mapnew[hip_id_int]
        print (star_sprite.NAME)
        star_sprite.setInfoVisible(True)

    # Main loop, required variables for testing
    print("Starting simulation")
    frame_count = 0

    start_time = pygame.time.get_ticks()
    running = True
    pygame.key.set_repeat(200, 25)
    FPS_text = f"Actual FPS: 0"
    static_text_surfaces = {
        "exoplanets": writeText("View Stars with ExoPlanets", CIndex.WHITE, FIndex.VERYSMALL),
        "earth_like": writeText("View Earth Like Stars", CIndex.WHITE, FIndex.VERYSMALL),
    }
    parsec_text = f"Distance in Parsecs: {parsecs:.2f}"
    parsec_surface = writeText(parsec_text, CIndex.WHITE, FIndex.VERYSMALL)
    last_parsec_text = parsec_text
    fps_surface = writeText(FPS_text, CIndex.WHITE, FIndex.VERYSMALL)
    last_fps_text = FPS_text
    brightness_text = f"Brightness Offset (R/T/Scroll/Drag): {control_vars['MagOffset']:+d}"
    brightness_surface = writeText(brightness_text, CIndex.WHITE, FIndex.VERYSMALL)
    last_brightness_text = brightness_text

    x_offset,y_offset,canvas_scale = (0,0,1)
    response= ""
    font = pygame.font.SysFont(None, 24)
    clearInfo = False
   
    custom_visible_star_sprites = CustomSpriteGroup()
    infoSpriteGroup = CustomSpriteGroup()
    visible_indices = np.array([], dtype=int)
    visible_magindices = np.array([], dtype=int)
    last_observer_pos = observerPOS
    last_mag_offset = control_vars['MagOffset']
    # Initialize circle_x and circle_radius to match the current view scale
    view_index = max(0, min(9, control_vars['ViewScale']))
    slider_progress = 1 - (view_index / 9)
    circle_x = slider_x + slider_progress * slider_width
    circle_radius = circle_max_radius - (circle_max_radius - circle_min_radius) * slider_progress

    while running:
        clock.tick(FPS)

        # check for key input
        running, parsecs, current_orientation,rotated,mouse_x,mouse_y,clearInfo, parsecs_changed, mouse_held,last_repeat_time = handle_events(control_vars, key_to_scale, parsecs, current_orientation,rotated,x_offset,y_offset,canvas_scale,parsecs_changed, decrease_button_rect, increase_button_rect,mouse_held,last_repeat_time, quit_button_rect, menu_rects)
        MAG_OFFSET = control_vars['MagOffset']
        if running:
            canvas.fill((0, 0, 0))

 

            # Rotate and update frame points regardless of the draw_frame flag
            if rotated:
                q_np = np.array([current_orientation.w, current_orientation.x, current_orientation.y, current_orientation.z])
        
            # Required in case the canvas resizes
            #
            control_vars['scale'] = (canvas_width//2) / parsecs
            control_vars['sphere'] = parsecs
            # Rotate the galactic center star

            if control_vars['draw_frame']:
                update_sprites_positions(all_frame_sprites_group, rotate_points_numba(all_frame_points,q_np))
                all_frame_sprites_group.draw(canvas)


            # rotated_points = rotate_points_numba(all_star_points,q_np)
            # update_star_positions(all_stars_sprites_group,rotated_points ,control_vars['scale'])
            # custom_visible_star_sprites = update_visibility(all_stars_sprites_group,control_vars['sphere']*ScreenScaler)

            selected_filter = control_vars['filter_mode']
            draw_futuristic_menu(canvas, selected_filter, menu_rects)
            draw_exit_button(canvas, quit_button_rect)
            handle_slider(canvas, circle_x, circle_radius)
            draw_brightness_slider(canvas, control_vars['MagOffset'])

            mouse_pos = pygame.mouse.get_pos()
            draw_arrow_button(canvas, decrease_button_rect, "left", decrease_button_rect.collidepoint(mouse_pos))
            draw_arrow_button(canvas, increase_button_rect, "right", increase_button_rect.collidepoint(mouse_pos))

            # Step 2: Determine which stars are visible and create a visible sprite group
            if parsecs_changed:
                custom_visible_star_sprites, visible_indices = update_visibility(
                    all_stars_sprites_group,
                    control_vars['sphere'] * ScreenScaler,
                    custom_visible_star_sprites,
                    selected_filter,
                    filter_masks,
                    dist_sq,
                    sprite_list,
                )
                visible_magindices = compute_magindices_for_indices(
                    visible_indices,
                    xy_sq,
                    z_vals,
                    abs_mags,
                    observerPOS,
                    all_star_points,
                )
                last_observer_pos = observerPOS
                parsecs_changed = False
                rotated = True
            elif observerPOS != last_observer_pos:
                visible_magindices = compute_magindices_for_indices(
                    visible_indices,
                    xy_sq,
                    z_vals,
                    abs_mags,
                    observerPOS,
                    all_star_points,
                )
                last_observer_pos = observerPOS
            if control_vars['brightness_changed'] or control_vars['MagOffset'] != last_mag_offset:
                visible_magindices = compute_magindices_for_indices(
                    visible_indices,
                    xy_sq,
                    z_vals,
                    abs_mags,
                    observerPOS,
                    all_star_points,
                )
                last_mag_offset = control_vars['MagOffset']
                control_vars['brightness_changed'] = False
                rotated = True

            # Step 2: Update only the visible stars using the map
            if rotated :
                if visible_indices.size:
                    if visible_magindices.size != visible_indices.size:
                        visible_magindices = compute_magindices_for_indices(
                            visible_indices,
                            xy_sq,
                            z_vals,
                            abs_mags,
                            observerPOS,
                            all_star_points,
                        )
                        last_observer_pos = observerPOS
                    rotated_points = rotate_points_numba(all_star_points[visible_indices], q_np)
                    for idx, new_position, magindex in zip(visible_indices, rotated_points, visible_magindices):
                        sprite_list[idx].set_position_3d(new_position, control_vars['scale'], observerPOS, magindex)
                rotated = False



            # Step 3: Update only the visible stars
            # for star in custom_visible_star_sprites:
            #     # Assuming that `rotated_points` is a list or array with the same order as `all_stars_sprites_group`
            #     index = all_stars_sprites_group.sprites().index(star)  # Find the index of the star in the original group
            #     new_position = rotated_points[index]  # Get the corresponding rotated position
                
            #     # Update the star's position with the new rotated and scaled position
            #     star.set_position_3d(new_position,control_vars['scale'],observerPOS)



            custom_visible_star_sprites.draw(canvas)

            if clearInfo:
                custom_visible_star_sprites.clearInfo()
                clearInfo = False
            if mouse_x is not None and mouse_y is not None:
                infoSpriteGroup = find_star_by_position(custom_visible_star_sprites, mouse_x, mouse_y)
            
            infoSpriteGroup.drawInfo(canvas,parsecs)

            FPS_text, frame_count,start_time = showFPS(FPS_text,frame_count,start_time)
            parsec_text = f"Distance in Parsecs: {parsecs:.2f}"
            if parsec_text != last_parsec_text:
                parsec_surface = writeText(parsec_text, CIndex.WHITE, FIndex.VERYSMALL)
                last_parsec_text = parsec_text
            if FPS_text != last_fps_text:
                fps_surface = writeText(FPS_text, CIndex.WHITE, FIndex.VERYSMALL)
                last_fps_text = FPS_text
            brightness_text = f"Brightness Offset (R/T/Scroll/Drag): {control_vars['MagOffset']:+d}"
            if brightness_text != last_brightness_text:
                brightness_surface = writeText(brightness_text, CIndex.WHITE, FIndex.VERYSMALL)
                last_brightness_text = brightness_text

            canvas.blit(parsec_surface, (100,100))
            canvas.blit(fps_surface, (100,120))
            canvas.blit(static_text_surfaces["exoplanets"], (100,140))
            canvas.blit(static_text_surfaces["earth_like"], (100,160))
            canvas.blit(brightness_surface, (100,180))
             
 #           x_offset, y_offset, canvas_scale = drawScreenUpdate(screen, canvas, bestHeight)
 #           text_rect = pygame.Rect(10, 10, 700, 500)  # Define the area for text
 #           render_text(screen, response, font, CIndex.WHITE, text_rect, text_rect.width)

            pygame.display.flip()

        else:
            print("Ending simulation")
    pygame.quit()

if __name__ == "__main__":
    main()
