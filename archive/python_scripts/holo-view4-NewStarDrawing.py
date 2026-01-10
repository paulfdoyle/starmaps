import pygame
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta
from skyfield.api import load, wgs84, utc, Star
from skyfield.data import stellarium
from pytz import timezone
from skyfield.projections import build_stereographic_projection
import math
from math import *

import pygame.gfxdraw
import warnings
warnings.filterwarnings("ignore")

output_dir = "saved_images/"

global_timescale = load.timescale()

try:
    profile  # exists when kernprof is running the script
except NameError:
    def profile(func):
        return func  # Return the function unchanged if not profiling

#screen_width, screen_height = 1500, 1500
canvas_width, canvas_height = 3000, 3000  # Large off-screen canvas size
BF = 2.512  # brightnes factor Created a bigger size difference between stars on the screen
BRM6 = 4  # Base radius for magnitude 6 stars, this will control if mag 6 is visible. 
FPS = 20  # Frames per second

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

class FIndex:
    VERYLARGE = 200
    LARGE = 150
    MEDIUM = 75
    SMALL = 50
    VERYSMALL = 25

class PIndex:
    P1 = 0
    P5 = 1
    P10 = 2
    P50 = 3
    P100 = 4
    P200 = 5
    P400 = 6
    P800 = 7
    P1600 = 8

# Define the RGB values for different types of stars
class StarColourIndex:
    O_Type = (155, 176, 255) # Blue
    B_Type = (170, 191, 255) # Blue-White
    A_Type = (202, 215, 255) # White
    F_Type = (248, 247, 255) # Yellow-White
    G_Type = (255, 244, 234) # Yellow
    K_Type = (255, 210, 161) # Orange
    M_Type = (255, 204, 111) # Red


def color_distance(rgb1, rgb2):
    """Calculate the Euclidean distance between two RGB colors."""
    return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5

def find_closest_star_color(rgb):
    """Find the closest star color type to the given RGB values."""
    # Define the RGB values for different types of stars directly in the function
    star_colors = {
        'O-Type (Blue)': (155, 176, 255),
        'B-Type (Blue-White)': (170, 191, 255),
        'A-Type (White)': (202, 215, 255),
        'F-Type (Yellow-White)': (248, 247, 255),
        'G-Type (Yellow)': (255, 244, 234),
        'K-Type (Orange)': (255, 210, 161),
        'M-Type (Red)': (255, 204, 111)
    }

    # Initialize variables to store the closest star type and its minimum distance
    closest_star_type = None
    min_distance = float('inf')

    # Iterate over each star color to find the closest match
    for star_type, star_rgb in star_colors.items():
        distance = color_distance(rgb, star_rgb)
        if distance < min_distance:
            min_distance = distance
            closest_star_type = star_type

    # Return the name of the closest star type and its RGB values
    return star_colors[closest_star_type]


def pregenerate_Framepoints(radius):
    radius = radius * 0.8
    frame_points = []

    current_radius = radius 
    for angle in range(0, 360, 1):
        rad = math.radians(angle)
        x = current_radius * math.sin(rad)
        y = current_radius * math.cos(rad)
        z = 0
        x,y,z = generalRotation (x , y, z, 45,0,0)
        frame_points.append([x, y, z])


    return np.array(frame_points)


def pregenerate_points(radius, num_circles, num_spokes):
    radius = radius * 0.8
    circle_points = []

    for n in range(num_circles, 0, -1):
        current_radius = radius * (n / num_circles)
        for angle in range(0, 360, 1):
            rad = math.radians(angle)
            x = current_radius * math.sin(rad)
            y = current_radius * math.cos(rad)
            z = 0
            circle_points.append([x, y, z])
            if n == num_circles:
                circle_points.append([z, y, x])
            if n == num_circles:
                circle_points.append([x, z, y])

    current_radius = radius-10 
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        x = current_radius * math.sin(rad)
        y = current_radius * math.cos(rad)
        z = 0
        circle_points.append([x, y, z])
        circle_points.append([z, y, x])
        circle_points.append([x, z, y])


    spoke_points = []
    for angle in range(0, 360, 360 // num_spokes):
        rad = math.radians(angle)
        x = radius * math.sin(rad)
        y = radius * math.cos(rad)
        z = 0
        spoke_points.append([x, y, z])


    frame_points = []
    current_radius = radius 
    for angle in range(0, 360, 1):
        rad = math.radians(angle)
        x = current_radius * math.sin(rad)
        y = current_radius * math.cos(rad)
        z = 0
        frame_points.append([x, y, z])
    
    current_radius = radius-10 

    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        x = current_radius * math.sin(rad)
        y = current_radius * math.cos(rad)
        z = 0
        frame_points.append([x, y, z])

    return np.array(circle_points), np.array(spoke_points), np.array(frame_points)

def draw_points(circle_points, spoke_points, frame_points):

    screen=pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    for point in circle_points:
        projected_x = int(point[0] + canvas_width // 2)
        projected_y = int(point[1] + canvas_height // 2)
        pygame.draw.circle(screen, CIndex.LIGHTCYAN, (projected_x, projected_y), 3)

    center_projected = np.array([canvas_width / 2, canvas_height / 2, 0])
    for point in spoke_points:
        start_proj = (int(point[0] + canvas_width / 2), int(point[1] + canvas_height / 2))
        pygame.draw.line(screen, CIndex.CYAN, start_proj, center_projected[:2],3)

    index=0
    for point in frame_points:
        index +=1
        projected_x = int(point[0] + canvas_width // 2)
        projected_y = int(point[1] + canvas_height // 2)
        pygame.draw.circle(screen, CIndex.CYAN, (projected_x, projected_y), 10)
    
    return screen

def galactic_to_cartesian(l_deg, b_deg, r):
    """
    Convert Galactic coordinates to Cartesian coordinates.
    
    Parameters:
    - l_deg: Galactic longitude in degrees.
    - b_deg: Galactic latitude in degrees.
    - r: Distance from the Sun.
    
    Returns:
    - A tuple of (x, y, z) representing the Cartesian coordinates.

    Z is the distance vector pointing towards galactic centre
    """


    # Convert degrees to radians
    l_rad = math.radians(l_deg)
    b_rad = math.radians(b_deg)
    
    # Calculate Cartesian coordinates
    x = r * math.cos(b_rad) * math.sin(l_rad)
    y = r * math.cos(b_rad) * math.cos(l_rad)
    z = r * math.sin(b_rad)

    return x,y,z
    
# Load the data into a DataFrame then convert it to NumpyArray
# We are reading in more data from the file than required since
# we may find a use for it later
def load_custom_star_data(json_file_path):
    print("loading data from file")
    required_columns = ['hip', 'mag', 'ra_decdeg', 'dec_decdeg', 'plx', 'pmra', 'pmdec', 'dist', 'absmag', 'kR', 'kG', 'kB', 'x', 'y', 'z','GLON','GLAT']
    df = pd.read_json(json_file_path)
    df = df[required_columns]

    df.columns = (
        'hip', 'magnitude', 'ra_degrees', 'dec_degrees',
        'parallax_mas', 'ra_mas_per_year', 'dec_mas_per_year',
        'distance_parsecs', 'absolutem', 'kR', 'kG', 'kB', '3dx', '3dy', '3dz', 'GLON','GLAT'
    )

    # Remove samples with missing data to elimiate checks later
    df = df.replace('', np.nan)

    # # Identify rows with missing 'ra_degrees', 'dec_degrees', or 'magnitude' before removing them
    # missing_values_df = df[df['ra_degrees'].isnull() | df['dec_degrees'].isnull() | df['magnitude'].isnull()]
    # missing_hr_ids = missing_values_df['hr']

    # # Save the missing HIP IDs to a text file
    # missing_hr_ids.to_csv('../datasets/missing_stars.txt', index=False, header=False)

    df.dropna(inplace=True)
    df = df.assign(ra_hours=df['ra_degrees'] / 15.0, epoch_year=1991.25)

    star_data_array = df.to_numpy()  # Convert DataFrame to NumPy array

    return star_data_array

def convert_to_cartesian_numpy(ra_hours, ra_minutes, ra_seconds, dec_degrees, dec_minutes, dec_seconds, distance):
    ra = (ra_hours + ra_minutes / 60 + ra_seconds / 3600) * (np.pi / 12)  # Convert RA to radians
    dec = (dec_degrees + dec_minutes / 60 + dec_seconds / 3600) * (np.pi / 180)  # Convert DEC to radians
    x = distance * np.cos(dec) * np.cos(ra)
    y = distance * np.cos(dec) * np.sin(ra)
    z = distance * np.sin(dec)
    return x, y, z

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

def convert_ra_dec(ra_deg, dec_deg,distance):
    print ("RA DEG", ra_deg)
    print ("DEC_D", dec_deg)

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
    #ra_str = f"{ra_h:02d}h{ra_m:02d}m{ra_s:05.2f}s"
    #dec_str = f"{dec_d:+03d}°{dec_m:02d}'{dec_s:05.2f}\""

    return x_numpy, y_numpy, z_numpy


def moveWorld (x,y,z,dist_parasec,moveDist):
    x_move,y_move,z_move = moveDist
    new_x = x+x_move
    new_y = y+y_move
    new_z = z+z_move


    ra_new, dec_new = cartesian_to_ra_dec(new_x,new_y,new_z)
    newDist = distance_3d(0,0,0,new_x,new_y,new_z)

    # print("New Dist = ",newDist)   
    # print(f"Cartesian coordinates with distance: x={x}, y={y}, z={z}")
    # print ("ra=",ra_new,dec_new)
    return ra_new,dec_new,newDist

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
    distance = math.sqrt(x**2 + y**2 + z**2)  # Calculate the distance to normalize z
    dec_rad = math.asin(z / distance)
    
    # Convert RA and DEC from radians to degrees
    ra_deg = math.degrees(ra_rad)
    dec_deg = math.degrees(dec_rad)
    
    return (ra_deg, dec_deg)

# Given a list of slightly various elements in a list, return a random item
# if the stars are of different brightness we can simulate them twinkling
def twinkle_star(elements):
    if not elements:  # Check if the list is empty
        return None   # Or raise an exception, depending on how you want to handle this case
    return random.choice(elements)

# For all stars we will have 3 reference points, apparent Mag, absolute Mag, distance.
# To calculate the apparent mag from a different location other than earth, we need to
# know the absolute Mag, which we can calculate from the apparent mag from earth where there
# is a know distance, OR we can take this data from our data set, if not available, we can
# reliably use these functions to calculate it. 
def calculate_absolute_magnitude(apparent_magnitude, distance_parsecs):
    """
    Calculate the absolute magnitude of a celestial object given its apparent magnitude
    and distance in parsecs.

    Args:
        apparent_magnitude (float): The apparent magnitude of the celestial object.
        distance_parsecs (float): The distance to the celestial object in parsecs.

    Returns:
        float: The absolute magnitude of the celestial object.
    """
    if distance_parsecs <= 0:
        raise ValueError("Distance must be greater than 0.")
    
    absolute_magnitude = apparent_magnitude - 5 * (math.log10(distance_parsecs) - 1)
    return absolute_magnitude

def calculate_apparent_magnitude(absolute_magnitude, distance_parsecs):
    """
    Calculate the apparent magnitude of a celestial object given its absolute magnitude
    and distance in parsecs.

    Args:
        absolute_magnitude (float): The absolute magnitude of the celestial object.
        distance_parsecs (float): The distance to the celestial object in parsecs.

    Returns:
        float: The apparent magnitude of the celestial object.
    """
    if distance_parsecs <= 0:
        raise ValueError("Distance must be greater than 0.")
    
    apparent_magnitude = absolute_magnitude + 5 * (math.log10(distance_parsecs) - 1)
    return apparent_magnitude


# Take in a standard canvas (which can have 1-N stars with slightly different brightness and then build a series of versions
# one for each magnitude ranging from Mag 0 to Mag 6

# Canvas is a list of surfaces
# Abs Mag can range from -10 to +15  (+15 is the smallest and faintest stars, -10 are the largest ones)
# We use a scale from 0 (representing -10) to +25 (representing +15)
def star_absmag_size_scaling(canvas):

# Create a 2D array of canvas. Rows are different sizes, cols are different brightness
    """
    starcanvas [MAG0 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG1 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG2 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG3 Size][Brighness] [Brighness] [Brighness]

    """

    MAG_RANGE = 26  # Absolute magnitude range from 0 to 25
    MAG_REF = 26  # Reference magnitude for the base radius
    RADIUS_REF = 4  # Radius for the reference magnitude
    rows, cols = MAG_RANGE, len(canvas)
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]
    
    for mag in range(rows):
        for img_index in range(cols):
            # Calculate the scaling factor relative to the reference magnitude
            scaling_factor = 10 ** ((MAG_REF - mag) / 6)
            radius = max(1, int(RADIUS_REF * scaling_factor))
            
            # Resize the star image based on the calculated radius
    #        canvas2D[mag][img_index] = pygame.transform.smoothscale(canvas[img_index], (radius, radius))
            print ("mag = ",mag," y = ",img_index," radius = ",radius)

    return canvas2D


def star_absmag_size_scaling1(canvas):
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


# Take in a standard canvas (which can have 1-N stars with slightly different brightness and then build a series of versions
# one for each magnitude ranging from Mag 0 to Mag 6

# Canvas is a list of surfaces
def star_mag_size_scaling(canvas,placeholder=None):

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

def precalculate_star_pairs(star_data_np, hip_to_index_map, edges_star1, edges_star2, center_x, center_y, zoom_factor, x_offset, y_offset):
    precalculated_pairs = []
    for s1, s2 in zip(edges_star1, edges_star2):
        if s1 in hip_to_index_map and s2 in hip_to_index_map:
            index1 = hip_to_index_map[s1]
            index2 = hip_to_index_map[s2]

            x1, y1 = star_data_np[index1, -2], star_data_np[index1, -1]
            x2, y2 = star_data_np[index2, -2], star_data_np[index2, -1]

            # Then, simply pass them to preprocess_coordinates without trying to index them again:
            x1, y1 = preprocess_coordinates(x1, y1, center_x, center_y, zoom_factor, x_offset, y_offset)
            x2, y2 = preprocess_coordinates(x2, y2, center_x, center_y, zoom_factor, x_offset, y_offset)

            precalculated_pairs.append(((x1, y1), (x2, y2)))
    return precalculated_pairs

def preprocess_coordinates(x, y, center_x, center_y, zoom_factor, x_offset, y_offset):
    # Apply translation and zoom to the star coordinates
    translated_x = (x + 1) * center_x - center_x
    translated_y = (y + 1) * center_y - center_y
    # Apply zoom
    zoomed_x = translated_x * zoom_factor
    zoomed_y = translated_y * zoom_factor
    # Translate back with offset
    final_x = zoomed_x + center_x + x_offset
    final_y = zoomed_y + center_y + y_offset
    return final_x, final_y  

# This function take the colour for a star as a parameter in the form of a tuple (255, 255, 255)
# It draws the star on a single Pygame surface 200pixels wide and returns a pointer to the star surface.
# The star can be scaled by another function to match different magnitudes
#
# The function draws a series of filled circles starting from the largest to the smallest
# The outer part of the star contains the colour of the star, while the centre is white
# There are 3 distinct areas drawn, the outer section, the middle and the inner section
# The middle and outer sections modify the circle colour to be more faint the larger the radius

def draw_star_surfaces(color):    
    RADIUS = 200
    NUMIMAGES = 4  # The number of images to create, the more images, the more variants in the images
    TR = 10         # The twinkle level, this is used to change the colour of each image very slightly 
    
    # Surface to draw on using a constant radius value
    star_surface = []
    
    # i starts at RADIUS and is reduced as the loop progresses. 
    for j in range (NUMIMAGES):
        star_surface.append(pygame.Surface((RADIUS*2, RADIUS*2), pygame.SRCALPHA))
        for i in range(RADIUS, 0, -1):
        #
            if i < RADIUS // 4:
                gradient_color = (255-(j*TR), 255-(j*TR), 255-(j*TR))
            elif i < RADIUS // 2:
                mix_ratio = (i - RADIUS // 4) / (RADIUS // 4)
                gradient_color = [int(255-(j*TR) + (color_component - 255) * mix_ratio) for color_component in color]
            else:
                mix_ratio = (i - RADIUS // 2) / (RADIUS // 2)
                gradient_color = [int(color_component * (1 - mix_ratio)-(j*TR)) for color_component in color]

            gradient_color = tuple(max(0, min(255, c)) for c in gradient_color) 			   # Keep in range of 0-255
            pygame.gfxdraw.filled_circle(star_surface[j], RADIUS, RADIUS, i, gradient_color)   # Draw the circle

    return star_surface


def getDimensions(output_dir):

    # Initialize variables to track the maximum indices
    max_layer = -1
    max_row = -1
    max_col = -1

    # List all files in the directory and iterate through them
    for filename in os.listdir(output_dir):
        if filename.startswith("image_") and filename.endswith(".png"):
            # Extract indices from the filename
            parts = filename.split('_')
            layer_idx, row_idx, col_idx = int(parts[1]), int(parts[2]), int(parts[3].split('.')[0])
            
            # Update max indices if current indices are larger
            max_layer = max(max_layer, layer_idx)
            max_row = max(max_row, row_idx)
            max_col = max(max_col, col_idx)

    # The dimensions of the 3D array (adding 1 since indices are zero-based)
    dimensions = (max_layer + 1, max_row + 1, max_col + 1)

    print("Dimensions of the 3D array:", dimensions)
    return dimensions

def buildStarImageDB():
    canvas_set = []  # Empty list to store surfaces
    for attr in dir(StarColourIndex):   
        if not attr.startswith("__"):
            color = getattr(StarColourIndex, attr)
            canvas_set.append(star_absmag_size_scaling1(draw_star_surfaces(color)))
        print ("looping fo colour", attr)
    return canvas_set


def buildImageDB(star_data_np):
    canvas_set = []  # Empty list to store surfaces
    if os.path.exists(output_dir):
        num_layers, num_rows, num_cols = getDimensions(output_dir)
        print ("loading Images")
        for layer_idx in range(num_layers):
            layer = []  # Create a new layer for the loaded images
            for row_idx in range(num_rows):
                row = []  # Create a new row for the loaded images
                for col_idx in range(num_cols):
                    filename = f"{output_dir}image_{layer_idx}_{row_idx}_{col_idx}.png"
                    img = pygame.image.load(filename)  # Load the image from the file
                    row.append(img)  # Add it to the current row
                layer.append(row)  # Add the completed row to the current layer
            canvas_set.append(layer)  # Add the completed layer to the loaded_images array
    else:
        print(f"Directory {output_dir} does not exist. Did not load any images.")
        print("Building Image DB")
        # Setup a progress indicator
        total_stars = len(star_data_np)
        
        # Adjust the progress bar length by one to accommodate the closing bracket
        print('[' + ' ' * 88 + ']', end='', flush=True)
        progress_marker = total_stars // 89  # Adjust the progress bar update frequency
        
        
        for index, star in enumerate(star_data_np):
            # Extract color values using the provided SIndex class indices
            color = (int(star[SIndex.COLOR_K_R] * 255), int(star[SIndex.COLOR_K_G] * 255), int(star[SIndex.COLOR_K_B] * 255))
            
            # Append the generated surface to the canvas set
            canvas_set.append(star_mag_size_scaling(draw_star_surfaces(color)))
            
            # Move the cursor back before the closing bracket to update the progress bar correctly
            if (index + 1) % progress_marker == 0 or index == total_stars - 1:
                print('\r[' + '.' * ((index + 1) // progress_marker) + ' ' * (88 - ((index + 1) // progress_marker)) + ']', end='', flush=True)
        
        print("\nImage DB Completed")

    # Check if the directory exists, and if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print ("Saving Images if they don't exist")

    for layer_idx, layer in enumerate(canvas_set):
        for row_idx, row in enumerate(layer):
            for col_idx, img in enumerate(row):
                filename = f"{output_dir}image_{layer_idx}_{row_idx}_{col_idx}.png"  # Construct filename

                            # Check if the file already exists
                if not os.path.exists(filename):
                    pygame.image.save(img, filename)  # Save the surface to a file only if it doesn't already exist
    return canvas_set

def update_star_positions(star_data_np):
    new_positions_3d = []
    for star in star_data_np:
        # Extract all necessary original values, not just positions and distance
        updated_star = list(star)  # Convert tuple to list if necessary, to allow modifications

        # Extract current star position and distance for calculation
        x, y, z, distance_parsecs = star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz], star[SIndex.DISTANCE_PARSECS]
        
        # Calculate new RA, DEC, and distance
 #       new_ra, new_dec, new_distance = moveWorld(x, y, z, distance_parsecs, (1, 1, 1))
        
        # Convert back to Cartesian coordinates for new position
        new_x, new_y, new_z = ra_dec_distance_to_cartesian(new_ra, new_dec, new_distance)
        
        # Update the corresponding values in 'updated_star'
        updated_star[SIndex.Dx] = new_x
        updated_star[SIndex.Dy] = new_y
        updated_star[SIndex.Dz] = new_z
        updated_star[SIndex.DISTANCE_PARSECS] = new_distance
        updated_star[SIndex.RA_HOURS] = new_ra / 15  # Update RA in hours directly
        
        # Append the updated star data to the new list
        new_positions_3d.append(updated_star)

    # Convert the list to a NumPy array, preserving all original columns
    new_star_positions_np = np.array(new_positions_3d)
    return new_star_positions_np

def update_celestial_projection(new_star_positions_np, eph, constellations, observer_lat, observer_lon, timescale, when ='2024-03-11 00:00'):
    observer_location = wgs84.latlon(observer_lat, observer_lon)
    t = timescale.utc(datetime.strptime(when, '%Y-%m-%d %H:%M').replace(tzinfo=timezone("Europe/Dublin")))

    edges = [edge for _, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, _ in edges]
    edges_star2 = [star2 for _, star2 in edges]


    ra_hours = new_star_positions_np[:, SIndex.RA_HOURS]
    dec_degrees = new_star_positions_np[:, SIndex.DEC_DEGREES]

    # Observer at the given time
    observer = observer_location.at(t)
    
    # Star positions for projection
    star_positions = eph['earth'].at(t).observe(Star(ra_hours=ra_hours, dec_degrees=dec_degrees))
    projection = build_stereographic_projection(observer)
    
    # Projection
    x, y = projection(star_positions)
    y = -y  # Inverting y to match the graphical y-axis direction

    updated_star_positions_np = new_star_positions_np.copy()  # Make a copy to avoid altering the original array
    updated_star_positions_np[:, SIndex.X] = x  # Update X coordinates
    updated_star_positions_np[:, SIndex.Y] = y  # Update Y coordinates

    return updated_star_positions_np, edges_star1, edges_star2

@profile
def draw_constellation_lines(canvas, precalculated_pairs):
    for (x1, y1), (x2, y2) in precalculated_pairs:
        pygame.draw.line(canvas, (255, 255, 255), (x1, y1), (x2, y2), 3)
    return canvas
def translationMatrix (x , y, z, tx,ty,tz):
    x_rotated = (1 * x) + (0 * y)          + (0 * z) + (1 * tx)
    y_rotated = (0 * x) + (1 * y)          + (0 * z) + (1 * ty)
    z_rotated = (0 * x) + (0 * y)          + (1 * z) + (1 * tz)
    
    return (x_rotated, y_rotated, z_rotated)

def rotateXaxis4D (x , y, z, theta):
    x_rotated = (1 * x) + (0 * y)          + (0 * z)            + (0 * 1)
    y_rotated = (0 * x) + (cos(theta) * y) - (sin(theta) * z)   + (0 * 1)
    z_rotated = (0 * x) + (sin(theta) * y) + (cos(theta) * z)   + (0 * 1)
    t_rotated = (0 * x) + (0 * y)          + (0 * z)            + (1 * 1)

    return (x_rotated, y_rotated, z_rotated)

# General rotation matrix, Rz(Alpha) x Ry(Beta) x Rx(Gamma)
# The x,y,z are the coordinates to rotate
# The angles are rotated around the axis list Rz(alpha) rotates around z axis by degrees Alpha
def generalRotation (x , y, z, alpha,beta,gamma):


    x_rotated = (cos(alpha) * cos(beta) * x) + (((cos(alpha)*sin(beta)*sin(gamma)) - (sin(alpha)*cos(gamma))) * y)      + (((cos(alpha)*sin(beta)*cos(gamma)) + (sin(alpha)*sin(gamma))) * z)
    y_rotated = (sin(alpha) * cos(beta) * x) + (((sin(alpha)*sin(beta)*sin(gamma)) + (cos(alpha)*cos(gamma))) * y)      + (((sin(alpha)*sin(beta)*cos(gamma)) - (cos(alpha)*sin(gamma))) * z)
    z_rotated = (-sin(beta) * x) + (cos(beta) * sin(gamma) * y) + (cos(beta) * cos(gamma) * z)
    
  
    return (x_rotated, y_rotated, z_rotated)

# Loop through all the values in the starMap
# extract the coordinates and rotate them using a general rotation matrix
# return  the updated startMap dictionary which has the updated coordinates
def rotatePoints(starMap,theta_x,theta_y,theta_z):

#     for star in starMap:
#         (x,y,z) = generalRotation (starMap[star][0] , starMap[star][1], starMap[star][2], theta_z,theta_y,theta_x)
#         starMap[star][5] = 1
#         print ("star ", starMap[star][5] )
#         print ("before ", starMap[star][0], "rotated", x )
#         starMap[star][1] = y
#         starMap[star][2] = z

    for row in starMap:
        x = row[0]  # Extracting the third column value from each row
        y = row[1]  # Extracting the third column value from each row
        z = row[2]  # Extracting the third column value from each row
        x,y,z = generalRotation (x,y,z,theta_x,theta_y,theta_z)


    for name, values in starMap.items() :
        x,y,z = generalRotation (values[0] , values[1], values[2], theta_x,theta_y,theta_z)
        starMap[name] = (x,y,z,values[3],values[4],values[5])

    return (starMap)

def normaliseABSMagLog(data):

    column_index = 7
    column_data = data[:, column_index]

    # Logarithmic transformation of the selected column
    # Adding a small constant to handle zero values (assuming there are any)
    constant = np.min(column_data[column_data > 0]) * 0.01
    log_transformed_data = np.log(column_data + constant)

    # Normalization to [0, 6] range
    min_val = log_transformed_data.min()
    max_val = log_transformed_data.max()
    normalized_data = 6 * (log_transformed_data - min_val) / (max_val - min_val)

    # Replace the original column data with the normalized data
    data[:, column_index] = normalized_data

    # Checking the median of the normalized column
    median_val = np.median(normalized_data)
    print("Median of normalized column after log transformation:", median_val)

    # Optional: Plotting to visualize the effect of transformation
    plt.figure(figsize=(12, 6))

    # Original Column Data Histogram
    plt.subplot(1, 2, 1)
    plt.hist(column_data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title('Original Column Data Distribution')

    # Normalized Column Data Histogram
    plt.subplot(1, 2, 2)
    plt.hist(normalized_data, bins=30, color='lightgreen', edgecolor='black', alpha=0.7)
    plt.title('Normalized Column Data After Log Transformation')

    plt.tight_layout()
    plt.show()




def normaliseABSMag(star_data_np):

    # Select the column you're interested in
    column_index = SIndex.ABS_MAG
    column_data = star_data_np[:, column_index]

    # Normalize the selected column to be in the range [0, 6]
    min_val = column_data.min()
    max_val = column_data.max()

    # Linear transformation to scale [min_val, max_val] to [0, 6]
    normalized_column = 6 * (column_data - min_val) / (max_val - min_val)

    # Replace original column data with normalized data if desired
    star_data_np[:, column_index] = normalized_column

    # Showing the first few rows to verify normalization
    return (star_data_np)


def drawHist(data,column_index):
    column_data = data[:, column_index]
    mean = np.mean(column_data)
    median = np.median(column_data)
    std_dev = np.std(column_data)
    variance = np.var(column_data)
    minimum = np.min(column_data)
    maximum = np.max(column_data)
    range_of_data = maximum - minimum
    percentile_25 = np.percentile(column_data, 25)
    percentile_75 = np.percentile(column_data, 75)

    # Printing the statistics
    print(f"Descriptive Statistics for Column {column_index}:")
    print(f"Mean: {mean:.2f}")
    print(f"Median: {median:.2f}")
    print(f"Standard Deviation: {std_dev:.2f}")
    print(f"Variance: {variance:.2f}")
    print(f"Minimum: {minimum:.2f}")
    print(f"Maximum: {maximum:.2f}")
    print(f"Range: {range_of_data:.2f}")
    print(f"25th Percentile: {percentile_25:.2f}")
    print(f"75th Percentile: {percentile_75:.2f}")
    # Plotting the distribution of the selected column
    plt.hist(column_data, bins=30, alpha=0.7, color='blue', edgecolor='black')
    plt.title('Distribution of Column {}'.format(column_index))
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()
    input("Press Enter to continue...")

# create a surface with text on it
def writeText (text,color,fontsize):
    font = pygame.font.Font(None, fontsize)
    return font.render(text, True, color)

@profile
def main():

    pygame.init()
    clock = pygame.time.Clock()
    clock.tick(FPS)
    # Get display information and let the game run in full screen using actual screen 
    # width and height
    infoObject = pygame.display.Info()
    bestWidth = infoObject.current_w
    bestHeight = infoObject.current_h-100
    #screen = pygame.display.set_mode((bestHeight, bestHeight), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((bestHeight, bestHeight))
    pygame.display.set_caption("Holographic Star Chart")

   

    # Now create a canvas to draw on which will be scaled down for use on the screen
    # This is the main area for all driving
    canvas = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    canvas.fill((0, 0, 0))


    # Load the data from a file
    # 
    star_data_np = load_custom_star_data('../datasets/star_database_colors.json')
    print (star_data_np.shape)

    # Circle properties
    circle_radius = canvas_width//2
    num_circles = 4
    num_spokes = 8
    circle_points, spoke_points, frame_points = pregenerate_points(circle_radius, num_circles, num_spokes)
    canvas.blit(draw_points(circle_points, spoke_points,frame_points),(0,0),special_flags=pygame.BLEND_ADD)


    for i in range(star_data_np.shape[0]):
     #   print ("Test", i, star_data_np[i,SIndex.RA_DEGREES], star_data_np[i,SIndex.DEC_DEGREES], star_data_np[i,SIndex.DISTANCE_PARSECS])
        val1, val2, val3 = ra_dec_distance_to_cartesian(star_data_np[i,SIndex.RA_DEGREES],star_data_np[i,SIndex.DEC_DEGREES],star_data_np[i,SIndex.DISTANCE_PARSECS])
        gx,gy,gz =  galactic_to_cartesian              (star_data_np[i,SIndex.GLON],      star_data_np[i,SIndex.GLAT],       star_data_np[i,SIndex.DISTANCE_PARSECS])  
        
        # Update the specific columns for the row 'i'
        star_data_np[i, SIndex.Dx] = gx  # Updating column 0
        star_data_np[i, SIndex.Dy] = gy  # Updating column 1
        star_data_np[i, SIndex.Dz] = gz  # Updating column 2

    
    sun = star_mag_size_scaling(draw_star_surfaces((255,255,0)))
    grey = star_mag_size_scaling(draw_star_surfaces((50,50,50)))

 #   font = pygame.font.Font(None, 100)
#    suntext = "Sol!"
 #   suntext = "Sol!"
    
    sphere = 10  # measurement in parsecs for sphere of observation
 #   message = f"Parsec, {sphere}!"
    
    
    sol_label = writeText("Sol", CIndex.WHITE,FIndex.MEDIUM)
    sirius_label = writeText("Sirius", CIndex.WHITE,FIndex.MEDIUM)
    alphaCentA = writeText("Alpha Centauri", CIndex.WHITE,FIndex.MEDIUM)
    alphaCentB = writeText("Alpha Centauri B", CIndex.WHITE,FIndex.MEDIUM)
    eridani_label = writeText("18 varepsilon Eridani", CIndex.WHITE,FIndex.MEDIUM)
    procyon_label = writeText("Procyon", CIndex.WHITE,FIndex.MEDIUM)
    TauCeti52_label = writeText("52 Tau Ceti", CIndex.WHITE,FIndex.MEDIUM)

    scale_label = []
    scale_label.append (writeText(f"Parsec = 1", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 5", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 10", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 50", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 100", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 200", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 400", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 800", CIndex.WHITE,FIndex.MEDIUM))
    scale_label.append (writeText(f"Parsec = 1600", CIndex.WHITE,FIndex.MEDIUM))

    offset = sun[0][1].get_width() / 2
    canvas.blit(twinkle_star(sun[2]), (canvas_width/2-offset, canvas_height/2-offset), special_flags=pygame.BLEND_ADD)
    canvas_set1 = buildStarImageDB()

    canvas_set = buildImageDB(star_data_np)
    star_data_np=normaliseABSMag(star_data_np)


    zoom_factor = 1.0
    rotate = False
    x_offset = 0
    y_offset = 0

    scale = 100
    newscale = 5
    angle_x = 0
    angle_y = 0
    angle_z = 0
    angle_x_rate = 0
    angle_y_rate = 0
    angle_z_rate = 0
    viewMag = 6


    max = 0

    tx = 0
    ty = 0
    tz = 0

    # Main loop
    print("running simulation")
    running = True
    pygame.key.set_repeat(200, 25)
    prev_mouse_pos = None

    while running:
        for event in pygame.event.get():
        

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  
                    pygame.quit()

                # default starting view 1 Parsec around SOL
                if event.key == pygame.K_7:
                    print("parsecs Increase")
                    sphere = sphere + (sphere * 0.1)
                    max = 0
                    print ("newscale = ",newscale)

                if event.key == pygame.K_8:
                    print("parsecs Increase")
                    sphere = sphere - (sphere * 0.1)
                    max = 0
                    print ("newscale = ",newscale)


                if event.key == pygame.K_UP:
                    angle_x_rate = angle_x_rate -0.01
                    print("rotate +X")
                if event.key == pygame.K_DOWN:
                    print("rotate -X")
                    angle_x_rate = angle_x_rate +0.01
  
                if event.key == pygame.K_LEFT:
                    angle_y_rate = angle_y_rate -0.01
                    print("rotate +Y")
                if event.key == pygame.K_RIGHT:
                    print("rotate -Y")
                    angle_y_rate = angle_y_rate +0.01
                    
                if event.key == pygame.K_SPACE:
                    angle_x_rate = 0
                    angle_y_rate = 0
                    angle_z_rate = 0

                if event.key == pygame.K_a:
                    print("rotate +Z")
                    angle_z_rate = angle_z_rate +0.01
                if event.key == pygame.K_z:
                    print("rotate -Z")
                    angle_z_rate = angle_z_rate -0.01

                if event.key == pygame.K_0:
                    print("parsecs Increase")
                    sphere = sphere + (sphere * 0.1)
                    max = 0
                    print ("newscale = ",newscale)

                if event.key == pygame.K_MINUS:
                    print("parsecs Decrease")
                    sphere = sphere - (sphere * 0.1)
                    max = 0
                    print ("newscale = ",newscale)


                if event.key == pygame.K_r:
                    print("mag plus")
                    viewMag = viewMag+1
                if event.key == pygame.K_t:
                    print("mag minus")
                    viewMag = viewMag-1

                if event.key == pygame.K_2:
                    print("Zoom +")
                    scale = scale +1
                if event.key == pygame.K_1:
                    print("Zoom -")
                    scale = scale -1
                    
                if event.key == pygame.K_3:
                    ty = ty +10
                if event.key == pygame.K_4:
                    ty = ty -10                    
                    
                if event.key == pygame.K_5:
                    tz = tz +10
                if event.key == pygame.K_6:
                    tz = tz -10
                    
                    
              
                    
                if event.type == pygame.QUIT:
                    done = True  
        
        angle_x = angle_x + angle_x_rate
        angle_y = angle_y + angle_y_rate
        angle_z = angle_z + angle_z_rate
        
   #     print (angle_x, angle_y, angle_z)
   #     angle_x_rate = 0
   #     angle_y_rate = 0
   #     angle_z_rate = 0
                    
   #     angle_y_rate = angle_y_rate +0.01
        canvas.fill((0, 0, 0))
        
        index = 0
        center_x = bestHeight / 2
        center_y = bestHeight / 2

        offset = sun[0][1].get_width() / 2
        canvas.blit(twinkle_star(sun[0]), (canvas_width/2-offset, canvas_height/2-offset), special_flags=pygame.BLEND_ADD)
        canvas.blit(sol_label, (canvas_width//2 - sol_label.get_width()//2, canvas_height/2 + sol_label.get_height()//2))
        canvas.blit(scale_label[1], (canvas_width//5, 50))

        updated_circle = np.copy(circle_points)
        for row in updated_circle:
            nx,ny,nz = generalRotation(row[0],row[1],row[2],angle_x,angle_y,angle_z)
            row[0] = nx
            row[1] = ny
            row[2] = nz

        updated_spokes = np.copy(spoke_points)
        for row in updated_spokes:
            nx,ny,nz = generalRotation(row[0],row[1],row[2],angle_x,angle_y,angle_z)
            row[0] = nx
            row[1] = ny
            row[2] = nz

        canvas.blit(draw_points(updated_circle, updated_spokes,frame_points),(1,1),special_flags=pygame.BLEND_ADD)

        # Draw the line towards the centre of the galaxy
        nx,ny,nz = generalRotation(0,0,2000,angle_x,angle_y,angle_z)
        pygame.draw.line(canvas, CIndex.RED, (canvas_width/2, canvas_height/2),(nx+canvas_width/2,ny+canvas_height/2),5)

        for star in star_data_np:
        
            nx,ny,nz = generalRotation(star[SIndex.Dx],star[SIndex.Dy],star[SIndex.Dz],angle_x,angle_y,angle_z)
            if star[SIndex.HIP] == 32349:
                canvas.blit(sirius_label, (nx*scale+(canvas_width/2) - sirius_label.get_width()//2, ny*scale+(canvas_height/2) + sirius_label.get_height()//2))
            if star[SIndex.HIP] == 71683:
                canvas.blit(alphaCentA, (nx*scale+(canvas_width/2) - alphaCentA.get_width()//2, ny*scale+(canvas_height/2) + alphaCentA.get_height()//2))
            if star[SIndex.HIP] == 16537:
                canvas.blit(eridani_label, (nx*scale+(canvas_width/2) - eridani_label.get_width()//2, ny*scale+(canvas_height/2) + eridani_label.get_height()//2))

            mag = round(star[SIndex.ABS_MAG]) 
            mag-=4
        
            if nz > 0:
                mag+=1

            if mag > 6:
                mag = 6
            if mag < 0:
                mag = 0

            offset = canvas_set[index][mag][0].get_width() / 2
 #           print (sphere,star[SIndex.DISTANCE_PARSECS])
            if star[SIndex.DISTANCE_PARSECS] > sphere:
                pass 
                #canvas.blit(twinkle_star(canvas_set[6][6]), (nz*scale+(canvas_width/2), ny*scale+(canvas_height/2)), special_flags=pygame.BLEND_ADD)
#             canvas.blit(twinkle_star(grey[4]), (nz*scale+(canvas_width/2), ny*scale+(canvas_height/2)), special_flags=pygame.BLEND_ADD)
            else:
                if nz > max:
                    max = nz
                    newscale = (canvas_width/3)/nx
                canvas.blit(twinkle_star(canvas_set[index][mag]), (nx*scale+(canvas_width/2), ny*scale+(canvas_height/2)), special_flags=pygame.BLEND_ADD)
            index += 1

         #display_screen.blit(canvas, (0,0))
        
        scaled_canvas = pygame.transform.smoothscale(canvas, (bestHeight, bestHeight))
        screen.blit(scaled_canvas, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()