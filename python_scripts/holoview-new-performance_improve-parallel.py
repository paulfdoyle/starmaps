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
from pyquaternion import Quaternion
import pygame.gfxdraw
import warnings
from numba import jit
from numba import njit, prange
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore")

output_dir = "saved_images/"

global_timescale = load.timescale()




try:
    profile  # exists when kernprof is running the script
except NameError:
    def profile(func):
        return func  # Return the function unchanged if not profiling

canvas_width, canvas_height = 3000, 3000  # Large off-screen canvas size
screen_width, screen_height = 800,800     # default size
BF = 2.512  # brightness factor Created a bigger size difference between stars on the screen
BRM6 = 4  # Base radius for magnitude 6 stars, this will control if mag 6 is visible.
FPS = 30  # Frames per second
JSON_FILE = '../datasets/star_database_colors.json'  # Global variable to hold name of the file to read for star data
ScreenScaler = 0.8

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
    RAHRS = 17
    EPOC = 18
    STAR_TYPE = 19


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
    O_Type = (140, 176, 255)  # Blue
    B_Type = (170, 191, 255)  # Blue-White
    A_Type = (202, 215, 255)  # White
    F_Type = (248, 247, 255)  # Yellow-White
    G_Type = (255, 233, 12)  # Yellow
    K_Type = (255, 165, 12)  # Orange
    M_Type = (255, 100, 12)  # Red


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
    0: (1, 'P1'),
    1: (2, 'P2'),
    2: (10,'P10'),
    3: (50,'P50'),
    4: (75,'P75'),
    5: (125,'P125'),
    6: (250,'P250'),
    7: (500,'P500'),
    8: (1000,'P1000'),
    9: (1500,'P1500')

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
    return index_parsecs.get(index, "Index not found")


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


def get_index_from_magnitude_old(magnitude):
    """
    Get the index for a given magnitude value based on the StarApparentMagIndex class.
    The magnitude is mapped to the closest defined magnitude.

    Parameters:
    - magnitude (float): The magnitude value to be mapped.

    Returns:
    - int: The corresponding index.
    """
    closest_mag = min(mag_to_index.keys(), key=lambda k: abs(k - magnitude))
    return mag_to_index[closest_mag]

def distance_between_3d_points(point1, point2):
    """
    Calculate the Euclidean distance between two 3D points.
    
    Parameters:
    point1 (tuple): A tuple of three floats or integers representing the first point (x1, y1, z1).
    point2 (tuple): A tuple of three floats or integers representing the second point (x2, y2, z2).
    
    Returns:
    float: The Euclidean distance between the two points.
    """
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance


def distance_between_3d_points(rgb1, rgb2):
    """Calculate the Euclidean distance between two RGB colors."""
    return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5


def find_closest_star_index(rgb):
    """Find the index of the closest star color type to the given RGB values."""
    closest_star_index = None
    min_distance = float('inf')

    # Iterate over each star color to find the closest match
    for index, star_rgb in enumerate(star_list):
        distance = color_distance(rgb, star_rgb)
        if distance < min_distance:
            min_distance = distance
            closest_star_index = index

    # Return the index of the closest star type
    return closest_star_index


def find_closest_star_color(rgb):
    """Find the closest star color type to the given RGB values. Function only used for testing"""
    # Define the RGB values for different types of stars directly in the function
    star_colors = {
        'O-Type (Blue)': StarColourIndex.O_Type,
        'B-Type (Blue-White)': StarColourIndex.B_Type,
        'A-Type (White)': StarColourIndex.A_Type,
        'F-Type (Yellow-White)': StarColourIndex.F_Type,
        'G-Type (Yellow)': StarColourIndex.G_Type,
        'K-Type (Orange)': StarColourIndex.K_Type,
        'M-Type (Red)': StarColourIndex.M_Type
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
    return closest_star_type, star_colors[closest_star_type]


def pregenerate_frame_points(radius, num_circles=2, num_spokes=4):
    radius = radius * ScreenScaler
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

    current_radius = radius - 10
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        x = current_radius * math.sin(rad)
        y = current_radius * math.cos(rad)
        z = 0
        circle_points.append([x, y, z])
        circle_points.append([z, y, x])
        circle_points.append([x, z, y]) 

    spoke_points = []
    index = 0
    arrowhead_angle_rad = math.radians(20)
    arrowhead_lenght    = 100
    for angle in range(0, 360, 360 // num_spokes):
        rad = math.radians(angle)
        x = radius * math.sin(rad)
        y = radius * math.cos(rad)
        z = 0
        if index == 1:
            Arrowangle = math.atan2(y, x )
            x1 = x - arrowhead_lenght * math.cos(Arrowangle + arrowhead_angle_rad)
            y1 = y - arrowhead_lenght * math.sin(Arrowangle + arrowhead_angle_rad)
            x2 = x - arrowhead_lenght * math.cos(Arrowangle - arrowhead_angle_rad)
            y2 = y - arrowhead_lenght * math.sin(Arrowangle - arrowhead_angle_rad)
        index+=1
        spoke_points.append([x, y, z])

    spoke_points.append([x1,y1,0])
    spoke_points.append([x2,y2,0])

    frame_points = []
    current_radius = radius
    for angle in range(0, 360, 1):
        rad = math.radians(angle)
        x = current_radius * math.sin(rad)
        y = current_radius * math.cos(rad)
        z = 0
        frame_points.append([x, y, z])

    current_radius = radius - 10

    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        x = current_radius * math.sin(rad)
        y = current_radius * math.cos(rad)
        z = 0
        frame_points.append([x, y, z])

    return np.array(circle_points), np.array(spoke_points), np.array(frame_points)

def draw_frame(frame_points):
    screen = pygame.Surface((canvas_width, canvas_height))
    for point in frame_points:
        projected_x = int(point[0] + canvas_width // 2)
        projected_y = int(point[1] + canvas_height // 2)
        pygame.draw.circle(screen, CIndex.CYAN, (projected_x, projected_y), 10)
    return screen


def interpolate_color(distance, min_dist, max_dist):
    intensity = 255 - int((distance - min_dist) * (255 - 100) / (max_dist - min_dist))  # 255 is bright, 100 is faint
    return (intensity, 255, 255)  # Brighter cyan color

# Function to interpolate size based on distance
def interpolate_size(distance, min_dist, max_dist):
    return 2 + (distance - min_dist) * (10 - 1) / (max_dist - min_dist)

def color_distance(rgb1, rgb2):
    """Calculate the Euclidean distance between two RGB colors."""
    return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5

def draw_points(circle_points, spoke_points, frame_points,star_labels):
    """Draw the frame around the stars"""
    screen = pygame.Surface((canvas_width, canvas_height))

# Assuming circle_points, canvas_width, canvas_height, color_distance, and pygame are defined elsewhere

# Arrays to store projected values
    projected_points = []
    distances = []

    # Variables to track min and max distances
    min_distance = float('inf')
    max_distance = float('-inf')

    # Loop to calculate projected points and distances
    for point in circle_points:
        projected_x = int(point[0] + canvas_width // 2)
        projected_y = int(point[1] + canvas_height // 2)
        projected_z = int(point[2] + canvas_height // 2)
        distance1 = distance_between_3d_points((projected_x, projected_y, projected_z), (0, 0, 0))
        distance = color_distance((projected_x, projected_y, projected_z), (-1000,-900, -5000))
        print(distance1, distance)
        
        # Store projected points
        projected_points.append((projected_x, projected_y))
        distances.append(distance)
    
        # Update min and max distances
        if distance < min_distance:
            min_distance = distance
        if distance > max_distance:
            max_distance = distance



## New loop to draw circles using stored projected points
#    for projected_x, projected_y in projected_points:
#        size = 3
#        pygame.draw.circle(screen, CIndex.LIGHTCYAN, (projected_x, projected_y), size)
    # New loop to draw circles using stored projected points and distances
    for (projected_x, projected_y), distance in zip(projected_points, distances):
        size = int(interpolate_size(distance, min_distance, max_distance))
        color = interpolate_color(distance, min_distance, max_distance)
        pygame.draw.circle(screen, color, (projected_x, projected_y), size)

    center_projected = np.array([canvas_width / 2, canvas_height / 2, 0])
    index = 0
    label_width=star_labels['galactic_centre'].get_width()//2
    for point in spoke_points:
        start_proj = (int(point[0] + canvas_width / 2), int(point[1] + canvas_height / 2))
        size = 3
        # print (start_proj, center_projected[:2])
        if index == 1:
            arrowend = start_proj
            pygame.draw.line(screen, CIndex.RED, start_proj, center_projected[:2], 10)
        elif index == 4:
            pygame.draw.line(screen, CIndex.RED, arrowend, start_proj, 10)

        elif index == 5:
            pygame.draw.line(screen, CIndex.RED, arrowend, start_proj, 10)
        else:
            pygame.draw.line(screen, CIndex.CYAN, start_proj, center_projected[:2], size)
        index += 1
    screen.blit(star_labels['galactic_centre'], (arrowend[0]-label_width, arrowend[1]+40))

    return screen



def draw_points1(circle_points, spoke_points, frame_points,star_labels):
    """Draw the frame around the stars"""

    screen = pygame.Surface((canvas_width, canvas_height))
    for point in circle_points:
        projected_x = int(point[0] + canvas_width // 2)
        projected_y = int(point[1] + canvas_height // 2)
        projected_z = int(point[2] + canvas_height // 2)
        size = 3
        pygame.draw.circle(screen, CIndex.LIGHTCYAN, (projected_x, projected_y), size)

    center_projected = np.array([canvas_width / 2, canvas_height / 2, 0])
    index = 0
    label_width=star_labels['galactic_centre'].get_width()//2
    for point in spoke_points:
        start_proj = (int(point[0] + canvas_width / 2), int(point[1] + canvas_height / 2))
        size = 3
        # print (start_proj, center_projected[:2])
        if index == 1:
            arrowend = start_proj
            pygame.draw.line(screen, CIndex.RED, start_proj, center_projected[:2], 10)
        elif index == 4:
            pygame.draw.line(screen, CIndex.RED, arrowend, start_proj, 10)

        elif index == 5:
            pygame.draw.line(screen, CIndex.RED, arrowend, start_proj, 10)
        else:
            pygame.draw.line(screen, CIndex.CYAN, start_proj, center_projected[:2], size)
        index += 1
    screen.blit(star_labels['galactic_centre'], (arrowend[0]-label_width, arrowend[1]+40))

    return screen


def draw_sun(sun, star_labels, scale_labels):
    # draws the sun at the centre of the image
    screen = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    screen.fill(CIndex.BLACK)

    offset = sun[10][1].get_width() / 2
    screen.blit(twinkle_star(sun[10]), (canvas_width / 2 - offset, canvas_height / 2 - offset),
                special_flags=pygame.BLEND_ADD)
    screen.blit(star_labels['sol'],
                (canvas_width // 2 - star_labels['sol'].get_width() // 2, canvas_height / 2 + star_labels['sol'].get_height() // 2))
    # screen.blit(scale_labels['P1'], (canvas_width//5, 50))
    return screen


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
            'kR', 'kG', 'kB', 'x', 'y', 'z', "GLON", "GLAT"
        ]
        df = pd.read_json(json_file_path)
        df = df[required_columns]
        # print("1-->",df.iloc[0])

        df.columns = (
            'hip', 'magnitude', 'ra_degrees', 'dec_degrees', 'parallax_mas', 'ra_mas_per_year',
            'dec_mas_per_year', 'distance_parsecs', 'absolutem', 'kR', 'kG', 'kB', '3dx', '3dy', '3dz', "GLON", "GLAT"
        )
        # print("2-->",df.iloc[0])

        # Remove samples with missing data to elimiate checks later
        df = df.replace('', np.nan)

        # # Identify rows with missing 'ra_degrees', 'dec_degrees', or 'magnitude' before removing them
        # missing_values_df = df[df['ra_degrees'].isnull() | df['dec_degrees'].isnull() | df['magnitude'].isnull()]
        # missing_hr_ids = missing_values_df['hr']

        # # Save the missing HIP IDs to a text file
        # missing_hr_ids.to_csv('../datasets/missing_stars.txt', index=False, header=False)

        df.dropna(inplace=True)
        df = df.assign(ra_hours=df['ra_degrees'] / 15.0, epoch_year=2000)
        for index, row in df.iterrows():
            ra_deg, dec_deg = galactic_to_equatorial_proper(row['GLON'], row['GLAT'])
            df.at[index, 'ra_degrees'] = ra_deg
            df.at[index, 'dec_degrees'] = dec_deg
            # The line below causes the projection to change unexpectedly when axis shifts are enabled
            x, y, z = galactic_to_cartesian(row['GLON'], row['GLAT'], row['distance_parsecs'])
            df.at[index, '3dx'] = x
            df.at[index, '3dy'] = y
            df.at[index, '3dz'] = z
        # print("3-->",df.iloc[0])

        star_data_array = df.to_numpy()  # Convert DataFrame to NumPy array
        array_copy = star_data_array.copy()

        new_rows = []
        for row in array_copy:
            startypeIndex = find_closest_star_index(
                (row[SIndex.COLOR_K_R] * 255, row[SIndex.COLOR_K_G] * 255, row[SIndex.COLOR_K_B] * 255))
            new_row = np.append(row, startypeIndex)
            new_rows.append(new_row)
        new_array = np.array(new_rows)

        # Print the dimensions of the updated array
        print(new_array.shape)

        # new_array = np.star_data_array([np.append(row, find_closest_star_index((row[SIndex.COLOR_K_R] *255, row[SIndex.COLOR_K_G]*255, row[SIndex.COLOR_K_B]*255))) for row in array])
        print(star_data_array.shape)

        return new_array

    except Exception as e:
        print(f"An error occurred while loading or processing the star data: {e}")
        return None, None, None


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


# Given a list of slightly various elements in a list, return a random item
# if the stars are of different brightness we can simulate them twinkling
def twinkle_star(elements):
    if not elements:  # Check if the list is empty
        return None  # Or raise an exception, depending on how you want to handle this case
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


@jit(nopython=True)
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
    if distance_parsecs < 0:
        raise ValueError("Distance must be greater than 0.")

    apparent_magnitude = absolute_magnitude + 5 * (math.log10(distance_parsecs) - 1)
    return apparent_magnitude


# Take in a standard canvas (which can have 1-N stars with slightly different brightness and then build a series of versions
# one for each magnitude ranging from Mag 0 to Mag 6

# Canvas is a list of surfaces
def star_mag_size_scaling1(canvas, placeholder=None):
    # Create a 2D array of canvas. Rows are different sizes, cols are different brightness
    """
    starcanvas [MAG0 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG1 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG2 Size][Brighness] [Brighness] [Brighness]
    starcanvas [MAG3 Size][Brighness] [Brighness] [Brighness]

    """
    MAG_RANGE = 7  # 0 to 6

    rows, cols = MAG_RANGE, len(canvas)
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]

    for x in range(rows):
        for y in range(cols):
            scaling_factor = BF ** (6 - x) if x < 6 else 1
            radius = int(BRM6 * math.sqrt(scaling_factor))
            canvas2D[x][y] = pygame.transform.smoothscale(canvas[y], (radius, radius))

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
    MAG_END = 10  # Ending magnitude
    MAG_STEP = 0.5  # Step for magnitudes (half-magnitude steps)
    MAG_REF = 10  # Reference magnitude for the base radius
    RADIUS_REF = 4  # Radius for the reference magnitude

    # Calculate number of rows based on the range and step
    rows = int((MAG_END - MAG_START) / MAG_STEP + 1)  # Rows is the number of different star colours
    cols = len(canvas)  # This is the number of variants of each colour are in the list.
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]

    mag = MAG_START
    for row in range(rows):
        for img_index in range(cols):
            # Calculate the scaling factor relative to the reference magnitude
            scaling_factor = 10 ** ((MAG_REF - mag) / 6)
            radius = max(1, int(RADIUS_REF * scaling_factor))

            # Resize the star image based on the calculated radius
            canvas2D[row][img_index] = pygame.transform.smoothscale(canvas[img_index], (radius, radius))
            # print ("row = ",row," mag index = ",img_index," radius = ",radius)

        mag += MAG_STEP  # Move to the next magnitude step

    return canvas2D


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
# It draws the star on a single Pygame surface 100pixels wide and returns a pointer to the star surface.
# The star can be scaled by another function to match different magnitudes
#
# The function dras a series of filled circles starting from the largest to the smallest
# The outer part of the star contains the colour of the star, while the centre is white
# There are 3 distinct areas drawn, the outer section, the middle and the inner section
# The middle and outer sections modify the circle colour to be more faint the larger the radius

def draw_star_surfaces(color):
    RADIUS = 100
    NUMIMAGES = 2  # The number of images to create, the more images, the more variants in the images
    TR = 7  # The twinkle level, this is used to change the colour of each image very slightly

    # Surface to draw on using a constant radius value
    star_surface = []

    # i starts at RADIUS and is reduced as the loop progresses.
    for j in range(NUMIMAGES):
        star_surface.append(pygame.Surface((RADIUS * 2, RADIUS * 2), pygame.SRCALPHA))
        for i in range(RADIUS, 0, -1):
            #
            if i < RADIUS // 2:
                gradient_color = (255 - (j * TR), 255 - (j * TR), 255 - (j * TR))
            elif i < RADIUS // 2:
                mix_ratio = (i - RADIUS // 4) / (RADIUS // 4)
                gradient_color = [int(255 - (j * TR) + (color_component - 255) * mix_ratio) for color_component in color]
            else:
                mix_ratio = (i - RADIUS // 2) / (RADIUS // 2)
                gradient_color = [int(color_component * (1 - mix_ratio) - (j * TR)) for color_component in color]

            gradient_color = tuple(max(0, min(255, c)) for c in gradient_color)  # Keep in range of 0-255
            pygame.gfxdraw.filled_circle(star_surface[j], RADIUS, RADIUS, i, gradient_color)  # Draw the circle

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
    for star_rgb in star_list:
        canvas_set.append(star_mag_size_scaling(draw_star_surfaces(star_rgb)))

    print("Created new star DB")
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

def translationMatrix(x, y, z, tx, ty, tz):
    x_rotated = (1 * x) + (0 * y) + (0 * z) + (1 * tx)
    y_rotated = (0 * x) + (1 * y) + (0 * z) + (1 * ty)
    z_rotated = (0 * x) + (0 * y) + (1 * z) + (1 * tz)

    return (x_rotated, y_rotated, z_rotated)


def rotateXaxis4D(x, y, z, theta):
    x_rotated = (1 * x) + (0 * y) + (0 * z) + (0 * 1)
    y_rotated = (0 * x) + (cos(theta) * y) - (sin(theta) * z) + (0 * 1)
    z_rotated = (0 * x) + (sin(theta) * y) + (cos(theta) * z) + (0 * 1)
    t_rotated = (0 * x) + (0 * y) + (0 * z) + (1 * 1)

    return (x_rotated, y_rotated, z_rotated)


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


# General rotation matrix, Rz(Alpha) x Ry(Beta) x Rx(Gamma)
# The x,y,z are the coordinates to rotate
# The angles are rotated around the axis list Rz(alpha) rotates around z axis by degrees Alpha
def generalRotation(x, y, z, alpha, beta, gamma):
    x_rotated = (cos(alpha) * cos(beta) * x) + (((cos(alpha) * sin(beta) * sin(gamma)) - (sin(alpha) * cos(gamma))) * y) + (
                ((cos(alpha) * sin(beta) * cos(gamma)) + (sin(alpha) * sin(gamma))) * z)
    y_rotated = (sin(alpha) * cos(beta) * x) + (((sin(alpha) * sin(beta) * sin(gamma)) + (cos(alpha) * cos(gamma))) * y) + (
                ((sin(alpha) * sin(beta) * cos(gamma)) - (cos(alpha) * sin(gamma))) * z)
    z_rotated = (-sin(beta) * x) + (cos(beta) * sin(gamma) * y) + (cos(beta) * cos(gamma) * z)

    return (x_rotated, y_rotated, z_rotated)


# Loop through all the values in the starMap
# extract the coordinates and rotate them using a general rotation matrix
# return  the updated startMap dictionary which has the updated coordinates
def rotatePoints(starMap, theta_x, theta_y, theta_z):
    for row in starMap:
        x = row[0]  # Extracting the third column value from each row
        y = row[1]  # Extracting the third column value from each row
        z = row[2]  # Extracting the third column value from each row
        x, y, z = generalRotation(x, y, z, theta_x, theta_y, theta_z)

    for name, values in starMap.items():
        x, y, z = generalRotation(values[0], values[1], values[2], theta_x, theta_y, theta_z)
        starMap[name] = (x, y, z, values[3], values[4], values[5])

    return (starMap)


def perspective_projection(x, y, z, f):
    if z == 0:
        z = 1
    x_prime = (f * x) / z
    y_prime = (f * y) / z
    return (x_prime, y_prime)


# create a surface with text on it
def writeText(text, color, fontsize):
    font = pygame.font.Font(None, fontsize)
    return font.render(text, True, color)

    # Functions
def initialize_pygame():
    pygame.init()
    screen_info = pygame.display.Info()


    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.RESIZABLE)
    pygame.display.set_caption("Holographic Star Chart Main")
    clock = pygame.time.Clock()
    clock.tick(FPS)
    return screen, clock, screen_info.current_h   


# Functions
def initialize_pygame1():
    pygame.init()

    screenInfo = pygame.display.Info()
    bestHeight = screenInfo.current_h - 100
    pygame.display.set_caption("Holographic Star Chart Main")
    screen = pygame.display.set_mode((bestHeight, bestHeight))

    clock = pygame.time.Clock()
    clock.tick(FPS)
    return screen, clock, bestHeight


def create_canvas():
    canvas = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    canvas.fill(CIndex.BLACK)
    return canvas


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
    scaled_canvas = pygame.transform.smoothscale(canvas, (new_width, new_height))
    #    Calculate position to center the scaled canvas on the screen
    x_position = (screen_width - new_width) // 2
    y_position = (screen_height - new_height) // 2
    screen.fill((0, 0, 0))

    screen.blit(scaled_canvas, (x_position, y_position))

 #   scaled_canvas = pygame.transform.smoothscale(canvas, (bestHeight, bestHeight))
  #  width_scale = screen_width / canvas_width
   # Calculate position to center the scaled canvas on the screen
  #  x_position = (screen_width - new_width) // 2
  #  y_position = (screen_height - new_height) // 2

 #   scaled_canvas = pygame.transform.smoothscale(canvas, (min(screen_width, screen_height), max(screen_width, screen_height)))

 #   screen.blit(scaled_canvas, (0, 0))
    pygame.display.flip()

def blit_labels(canvas, star, nx, ny, scale, star_labels,control_vars):
    hip_to_label = {
        32349: 'sirius',
        102098: 'deneb',
        71683: 'alphaCentA',
        37279: 'procyon',
        8102: 'tauceti52',
        16537: 'eridani',
        104214: 'cyg61',
        108870: 'epsilonIndi',
        11767: 'polaris',
    }
    if star[SIndex.DISTANCE_PARSECS] > control_vars['sphere']:
        return
    if star[SIndex.HIP] in hip_to_label:
        label_name = hip_to_label[star[SIndex.HIP]]
        label_surface = star_labels[label_name]
        canvas.blit(label_surface, (
            nx * scale * ScreenScaler+ (canvas_width / 2) - label_surface.get_width() // 2,
            ny * scale * ScreenScaler+ (canvas_height / 2) + label_surface.get_height() // 2
        ))


def initialize_labels():
    star_labels = {
        'sirius': writeText("Sirius", CIndex.WHITE, FIndex.MEDIUM),
        'epsilonIndi': writeText("Epsilon Indi", CIndex.WHITE, FIndex.MEDIUM),
        'deneb': writeText("Deneb", CIndex.WHITE, FIndex.MEDIUM),
        'polaris': writeText("Polaris", CIndex.WHITE, FIndex.MEDIUM),
        'betelgeuse': writeText("Betelgeuse", CIndex.WHITE, FIndex.MEDIUM),
        'alphaCentA': writeText("Alpha Centauri A", CIndex.WHITE, FIndex.MEDIUM),
        'alphaCentB': writeText("Alpha Centauri B", CIndex.WHITE, FIndex.MEDIUM),
        'eridani': writeText("8 varepsilon Eridani", CIndex.WHITE, FIndex.MEDIUM),
        'procyon': writeText("Procyon", CIndex.WHITE, FIndex.MEDIUM),
        'tauceti52': writeText("52 Tau Ceti", CIndex.WHITE, FIndex.MEDIUM),
        'galactic_centre': writeText("Towards Galactic Core", CIndex.WHITE, FIndex.MEDIUM),
        'cyg61': writeText("61 Cyg", CIndex.WHITE, FIndex.MEDIUM),
        'sol': writeText("Sol", CIndex.WHITE, FIndex.MEDIUM),
    }

    scale_labels = {
        'P1': writeText("1 Parsec Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P2': writeText("2 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P10': writeText("10 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P50': writeText("50 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P75': writeText("75 Parsec Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P125': writeText("125 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P250': writeText("250 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P200': writeText("200 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P250': writeText("250 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P500': writeText("500 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P1000': writeText("1000 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
        'P1500': writeText("1500 Parsecs Radius", CIndex.WHITE, FIndex.MEDIUM),
    }
    return star_labels, scale_labels


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
        'Position':   (0,0,1),
        'sphere': 20,
        'scale': 0 # The scale needs to be worked out based on the radius of the frame circle. 

    }
    return control_vars


def initialise_menu_list():
    menu_items = [
        "Y/I: Move Y axis", "X/B: Move X axis", "Z/V: Move Z axis",
        "C: Toggle constellations", "R: Rotate", "+/-: Zoom",
        "Arrow Keys right/left: Move time forward/backward", "WASD: Pan", "U: Toggle positions to enable axis shifting",
        "M: Show/Hide this menu", "F: Reset Panning and Zooms", "G: Reset Axis rotations"
    ]

    return menu_items


def test_star_color():
    color = (int(0.304 * 255), int(0.452 * 255), int(1 * 255))
    print("Theta OrionisC is O-Type Test = ", find_closest_star_index(color))

    color = (int(0.355 * 255), int(0.449 * 255), int(1 * 255))
    print("Regulus      is B-Type Test = ", find_closest_star_index(color))

    color = (int(0.349 * 255), int(0.493 * 255), int(1 * 255))
    print("Vega is A-Type Test = ", find_closest_star_index(color))

    color = (int(0.939 * 255), int(0.907 * 255), int(1 * 255))
    print("Procyon A is F-Type Test = ", find_closest_star_index(color))

    color = (int(1 * 255), int(0.881 * 255), int(0.848 * 255))
    print("Tau Ceti is G-Type Test = ", find_closest_star_index(color))

    color = (int(1 * 255), int(0.715 * 255), int(0.502 * 255))
    print("Epsilon Eridni is K-Type Test = ", find_closest_star_index(color))

    color = (int(1 * 255), int(0.359 * 255), int(0.074 * 255))
    print("Betelguese is M-Type Test = ", find_closest_star_index(color))

    color = (int(0.304 * 255), int(0.452 * 255), int(1 * 255))
    print("Theta OrionisC is O-Type Test = ", find_closest_star_color(color), " color = ", color)

    color = (int(0.355 * 255), int(0.449 * 255), int(1 * 255))
    print("Regulus      is B-Type Test = ", find_closest_star_color(color), " color = ", color)

    color = (int(0.349 * 255), int(0.493 * 255), int(1 * 255))
    print("Vega is A-Type Test = ", find_closest_star_color(color), " color = ", color)

    color = (int(0.939 * 255), int(0.907 * 255), int(1 * 255))
    print("Procyon A is F-Type Test = ", find_closest_star_color(color), " color = ", color)

    color = (int(1 * 255), int(0.881 * 255), int(0.848 * 255))
    print("Tau Ceti is G-Type Test = ", find_closest_star_color(color), " color = ", color)

    color = (int(1 * 255), int(0.715 * 255), int(0.502 * 255))
    print("Epsilon Eridni is K-Type Test = ", find_closest_star_color(color), " color = ", color)

    color = (int(1 * 255), int(0.359 * 255), int(0.074 * 255))
    print("Betelguese is M-Type Test = ", find_closest_star_color(color), " color = ", color)

@njit(parallel=True)
def rotate_points_numba1(points, q):
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

    for i in prange(points.shape[0]):
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

def getMag(star,x,y,z,control_vars):

    MAGTYPE = control_vars['MagType']
    MagOffset = control_vars['MagOffset']
    control_vars['Position']

    if MAGTYPE == "APP":                
        magindex = get_index_from_magnitude(calculate_apparent_magnitude(star[SIndex.ABS_MAG], star[SIndex.DISTANCE_PARSECS]))
    elif MAGTYPE == "REL":
        distance = calculate_distance((x,y,z),control_vars['Position'])
        magindex = get_index_from_magnitude(calculate_apparent_magnitude(star[SIndex.ABS_MAG], distance))
        print ("distance from me",distance, "Distance from earth = ",star[SIndex.DISTANCE_PARSECS])
    else:
        magindex = get_index_from_magnitude(star[SIndex.ABS_MAG])
        magindex += MagOffset
        if magindex > 20:
            magindex = 20
    return magindex

@jit(nopython=True)
def compute_star_data(star, control_vars, q_np, sun, scale, canvas_width, canvas_height):

    rotated_points = rotate_points_numba(np.array([[star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz]]]), q_np)
    nx, ny, nz = rotated_points[0]

    magindex = getMag(star, control_vars['MagType'], control_vars['MagOffset'],control_vars['Position'])
    starimagewidth = sun[magindex][0].get_width() / 2

    return (star, nx, ny, magindex, starimagewidth)

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
    else:
        return True


    # This function returns a probability that the star should be drawn
    # Sigmoid function to scale the probability
    return 1 / (1 + math.exp((distance - max_distance / 2) / (max_distance / 10)))

def processStar (star_data_np,canvas,canvas_set,control_vars,q_np,scale,star_labels,sun):

    index = 0
    counter = 0
    for star in star_data_np:
        stardistance = star[SIndex.DISTANCE_PARSECS]
        if check_distance(stardistance, control_vars['sphere']):
            pass
        else:
            rotated_points = rotate_points_numba(np.array([[star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz]]]), q_np)
            nx, ny, nz = rotated_points[0]

            if control_vars['draw_labels']:
                blit_labels(canvas, star, nx, ny, scale, star_labels,control_vars)
 #           magindex = getMag(star,,nx,ny,nz,control_vars['MagType'],control_vars['MagOffset'])
            magindex = getMag(star, nx,ny,nz,control_vars)
            starimagewidth = sun[magindex][0].get_width() / 2

            if control_vars['optimise']:
                if should_draw_star(stardistance, control_vars['sphere'],magindex):
                    counter+=1
                    canvas.blit(twinkle_star(canvas_set[int(star[SIndex.STAR_TYPE])][magindex]),
                            (nx * scale* ScreenScaler + (canvas_width/ 2 - starimagewidth),
                            ny * scale * ScreenScaler+ (canvas_height / 2) - starimagewidth), special_flags=pygame.BLEND_ADD)  
     
            else:
                counter+=1
                canvas.blit(twinkle_star(canvas_set[int(star[SIndex.STAR_TYPE])][magindex]),
                    (nx * scale * ScreenScaler+ (canvas_width/ 2 - starimagewidth),
                    ny * scale * ScreenScaler + (canvas_height/ 2) - starimagewidth), special_flags=pygame.BLEND_ADD)

        if index < 8995:
            index += 1
    #print ("stars drawn = ",counter)

@profile
def main():
    # Initialise variables used to control the user experience

    control_vars = initialise_control_varaiables()
    control_vars['scale'] = (canvas_width//2) / control_vars['ViewScale']
    control_vars['MaxParsecIndex'] = len(index_parsecs)
    parsecs,parsec_label = get_pasec_from_index(control_vars['ViewScale'])   

    print (control_vars['scale'])

    current_orientation = Quaternion()

    # Initialise Pygame and the Screen for primary display, setting Height and Width to the Height of the canvas
    # bestHeight is set as the width and height of the display screen
    screen, clock, bestHeight = initialize_pygame()

    # Now create a canvas to draw on which will be scaled down for use on the screen
    # This is the main area for all driving
    canvas = create_canvas()

    # Load the data from a file
    #
    star_data_np = load_custom_star_data('../datasets/star_database_colors.json')
    # print (star_data_np.shape)

    # Calculate the points, for spkes and overall frame for viewing/drawing later
    circle_points, spoke_points, frame_points = pregenerate_frame_points(canvas_width // 2)
    frame = draw_frame(frame_points)
    # Create a blit set of images for the Sun
    sun = star_mag_size_scaling(draw_star_surfaces(StarColourIndex.G_Type))


    # Initialising the labes for use in the progam
    star_labels, scale_labels = initialize_labels()

    canvas_set = buildStarImageDB()

    scale = 100
 
    frame_count = 0
    start_time = pygame.time.get_ticks()

    # Main loop
    print("running simulation")
    running = True
#    pygame.key.set_repeat(200, 25)
    prev_mouse_pos = None

    # Find the galactic center star in the dataset
    galactic_center_star = None
    for star in star_data_np:
        if star[SIndex.HIP] == 99999:
            galactic_center_star = star
            break

    if galactic_center_star is None:
        print("Galactic center star with HIP 99999 not found in the dataset.")
        pygame.quit()
        return
    pygame.key.set_repeat(200, 25)

    FPS_text = f"Actual FPS: 0"

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()

                # default starting view 10 Parsec around SOL
                if event.key == pygame.K_m:
                    if control_vars['MagType'] == "REL":
                        control_vars['MagType'] = "APP"
                    else:
                        control_vars['MagType'] = "REL"

                if event.key == pygame.K_MINUS:
                    scaling_factor = 1.03
                    # Apply the scaling factor to the parsecs variable
                    parsecs = parsecs * scaling_factor
                    # Cap the maximum value of parsecs
                    max_parsecs = 1500
                    if parsecs > max_parsecs:
                        parsecs = max_parsecs
                    control_vars['Position'] = (0,0,parsecs)  


                if event.key == pygame.K_EQUALS:
                    scaling_factor = 1/ 1.03
                    parsecs = parsecs * scaling_factor
                    if parsecs <= 0:
                        parsecs = 1
                    control_vars['Position'] = (0,0,parsecs)  



                if event.key in key_to_scale:       
                    control_vars['ViewScale'] = key_to_scale[event.key]
                    parsecs,parsec_label = get_pasec_from_index(control_vars['ViewScale']) 
                    control_vars['Position'] = (0,0,parsecs)  

                if event.key == pygame.K_o:
                    control_vars['optimise'] = not control_vars['optimise']
                    print(f"Frame {'On' if control_vars['optimise'] else 'Off'}")

                if event.key == pygame.K_f:
                    control_vars['draw_frame'] = not control_vars['draw_frame']
                    print(f"Frame {'On' if control_vars['draw_frame'] else 'Off'}")
 
                if event.key == pygame.K_s:
                    control_vars['draw_sun'] = not control_vars['draw_sun']
                    print(f"Sun {'On' if control_vars['draw_sun'] else 'Off'}")
                if event.key == pygame.K_l:
                    control_vars['draw_labels'] = not control_vars['draw_labels']
                    print(f"Labels {'On' if control_vars['draw_labels'] else 'Off'}")

                if event.key == pygame.K_x:
                    current_orientation = rotate_object(current_orientation, 'x', 1)
                if event.key == pygame.K_b:
                    current_orientation = rotate_object(current_orientation, 'x', -1)
                if event.key == pygame.K_y:
                    current_orientation = rotate_object(current_orientation, 'y', 1)
                if event.key == pygame.K_i:
                    current_orientation = rotate_object(current_orientation, 'y', -1)
                if event.key == pygame.K_z:
                    current_orientation = rotate_object(current_orientation, 'z', 1)
                if event.key == pygame.K_v:
                    current_orientation = rotate_object(current_orientation, 'z', -1)
                if event.key == pygame.K_SPACE:
                    current_orientation = Quaternion()  # Reset rotation
                if event.key == pygame.K_r:
                    control_vars['MagOffset'] += 1
                if event.key == pygame.K_t:
                    control_vars['MagOffset'] -= 1
                if event.key == pygame.K_2:
                    scale += 1
                    print("Zoom + Scale ",scale)

                if event.type == pygame.QUIT:
                    done = True

        canvas.fill((0, 0, 0))
        canvas.blit(writeText(FPS_text, CIndex.WHITE, FIndex.MEDIUM), (100,200))           

        # Rotate and update frame points regardless of the draw_frame flag
        q_np = np.array([current_orientation.w, current_orientation.x, current_orientation.y, current_orientation.z])
        updated_circle = rotate_points_numba(circle_points, q_np)
        updated_spokes = rotate_points_numba(spoke_points, q_np)

        # Draw the Frame if the var is set to True
        if control_vars['draw_frame']:
            canvas.blit(draw_points(updated_circle, updated_spokes, frame_points,star_labels), (1, 1), special_flags=pygame.BLEND_ADD)
            canvas.blit(frame,(1,1), special_flags=pygame.BLEND_ADD)
        if control_vars['draw_sun']:
            offset = sun[10][1].get_width() / 2
            canvas.blit(twinkle_star(sun[10]), (canvas_width / 2 - offset, canvas_height / 2 - offset),special_flags=pygame.BLEND_ADD)
            #canvas.blit(draw_sun(sun, star_labels, scale_labels), (0, 0), special_flags=pygame.BLEND_ADD)
            if control_vars['draw_labels']:
                canvas.blit(star_labels['sol'], (canvas_width / 2 - star_labels['sol'].get_width() // 2, canvas_height / 2 + star_labels['sol'].get_height() // 2))
 
        parsec_text = f"Distance in Parsecs: {parsecs:.2f}"
        canvas.blit(writeText(parsec_text, CIndex.WHITE, FIndex.MEDIUM), (100,100))

      #  if control_vars['scale'] < (canvas_width//2) / parsecs:
      #      control_vars['scale'] += 1
      #  elif control_vars['scale'] > (canvas_width//2) / parsecs:
      #      control_vars['scale'] -= 1
       # else:
       #     control_vars['scale'] = (canvas_width//2) / parsecs

        control_vars['scale'] = (canvas_width//2) / parsecs
        control_vars['sphere'] = parsecs
        # Rotate the galactic center star
        processStar(star_data_np,canvas,canvas_set,control_vars,q_np,control_vars['scale'],star_labels,sun)

        drawScreenUpdate(screen, canvas, bestHeight)
        frame_count += 1
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        if elapsed_time > 1000:  # 1000 ms = 1 second
            actual_fps = frame_count / (elapsed_time / 1000.0)
            FPS_text = f"Actual FPS: {actual_fps:.2f}"
            #print(f"Actual FPS: {actual_fps:.2f}")
            frame_count = 0
            start_time = current_time
if __name__ == "__main__":
    main()

pygame.quit()