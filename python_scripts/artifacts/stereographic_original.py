import pygame
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from skyfield.api import load, wgs84, utc, Star
from skyfield.data import stellarium
from pytz import timezone
from skyfield.projections import build_stereographic_projection
import math
import pygame.gfxdraw
import warnings
warnings.filterwarnings("ignore")

global_timescale = load.timescale()

try:
    profile  # exists when kernprof is running the script
except NameError:
    def profile(func):
        return func  # Return the function unchanged if not profiling

screen_width, screen_height = 1300, 1300
canvas_width, canvas_height = 5000, 5000  # Large off-screen canvas size
BF = 2.512  # brightnes factor Created a bigger size difference between stars on the screen
BRM6 = 4  # Base radius for magnitude 6 stars, this will control if mag 6 is visible. 
FPS = 20  # Frames per second

global shift_x, shift_y, shift_z
shift_x, shift_y, shift_z = 0, 0, 0  # Initialize shifts for X, Y, Z axes

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
    X = 19
    Y = 20

class FIndex:
    VERYLARGE = 200
    LARGE = 150
    MEDIUM = 75
    SMALL = 50
    VERYSMALL = 25

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

def load_custom_star_data(json_file_path):
    print("loading data from file")
    required_columns = ['hip', 'mag', 'ra_decdeg', 'dec_decdeg', 'plx', 'pmra', 'pmdec', 'dist', 'absmag', 'kR', 'kG', 'kB', 'x', 'y', 'z', "GLON", "GLAT"]
    df = pd.read_json(json_file_path)
    df = df[required_columns]

    df.columns = (
        'hip', 'magnitude', 'ra_degrees', 'dec_degrees',
        'parallax_mas', 'ra_mas_per_year', 'dec_mas_per_year',
        'distance_parsecs', 'absolutem', 'kR', 'kG', 'kB', '3dx', '3dy', '3dz', "GLON", "GLAT"
    )
    
    df = df.replace('', np.nan).dropna()
    df = df.assign(ra_hours=df['ra_degrees'] / 15.0, epoch_year=1991.25)

    # Convert GLON and GLAT to Cartesian coordinates and update the DataFrame
    for index, row in df.iterrows():
        x, y, z = galactic_to_cartesian(row['GLON'], row['GLAT'], row['distance_parsecs'])
        df.at[index, '3dx'] = x
        df.at[index, '3dy'] = y
        df.at[index, '3dz'] = z

    star_data_array = df.to_numpy()  # Convert DataFrame to NumPy array after update

    eph = load('de421.bsp')
    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern_st/constellationship.fab')
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)

    return star_data_array, eph, constellations

@profile
def collect_celestial_data(star_data_np, eph, constellations, lat, long, timescale, when='2024-01-01 00:00'):
    observer_location = wgs84.latlon(lat, long)
    t = timescale.utc(datetime.strptime(when, '%Y-%m-%d %H:%M').replace(tzinfo=timezone("Europe/Dublin")))

    observer = observer_location.at(t)
    edges = [edge for _, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, _ in edges]
    edges_star2 = [star2 for _, star2 in edges]

    center_object = Star(ra=observer.radec()[0], dec=observer.radec()[1])
    center = eph['earth'].at(t).observe(center_object)
    projection = build_stereographic_projection(center)

    # Map column names to indices for the NumPy array
    ra_hours_index = SIndex.RA_HOURS
    dec_degrees_index = SIndex.DEC_DEGREES
    
    # Extracting specific columns using their indices
    ra_hours = star_data_np[:, ra_hours_index]
    dec_degrees = star_data_np[:, dec_degrees_index]
    
    star_positions = eph['earth'].at(t).observe(Star(ra_hours=ra_hours, dec_degrees=dec_degrees))
    x, y = projection(star_positions)
    y = -y  # Adjust y-axis

    # Append the x, y projection results to the original star data array
    projected_positions = np.column_stack((x, y))
    star_data_np_with_xy = np.hstack((star_data_np, projected_positions))
    
    return star_data_np_with_xy, edges_star1, edges_star2

def distance_3d(x1, y1, z1, x2, y2, z2):
    """
    Calculate the Euclidean distance between two points in 3D space.

    Parameters:
    - x1, y1, z1: Coordinates of the first point.
    - x2, y2, z2: Coordinates of the second point.

    Returns:
    - The Euclidean distance between the two points.
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

# Function to convert RA and DEC to 3D Cartesian coordinates using NumPy
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

def precalculate_star_pairs(star_data_np, edges_star1, edges_star2, center_x, center_y, zoom_factor, x_offset, y_offset):
    precalculated_pairs = []
    for s1, s2 in zip(edges_star1, edges_star2):
        # Find indices in star_data_np where HIP matches s1 or s2
        indices1 = np.where(star_data_np[:, SIndex.HIP] == s1)[0]
        indices2 = np.where(star_data_np[:, SIndex.HIP] == s2)[0]

        # Check if both stars are found in the dataset
        if indices1.size > 0 and indices2.size > 0:
            index1 = indices1[0]
            index2 = indices2[0]

            # Extract X, Y coordinates for both stars
            x1, y1 = star_data_np[index1, SIndex.X], star_data_np[index1, SIndex.Y]
            x2, y2 = star_data_np[index2, SIndex.X], star_data_np[index2, SIndex.Y]

            # Adjust coordinates based on the provided parameters
            x1, y1 = preprocess_coordinates(x1, y1, center_x, center_y, zoom_factor, x_offset, y_offset)
            x2, y2 = preprocess_coordinates(x2, y2, center_x, center_y, zoom_factor, x_offset, y_offset)

            # Add the adjusted coordinates to the list of precalculated pairs
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
# It draws the star on a single Pygame surface 100pixels wide and returns a pointer to the star surface.
# The star can be scaled by another function to match different magnitudes
#
# The function dras a series of filled circles starting from the largest to the smallest
# The outer part of the star contains the colour of the star, while the centre is white
# There are 3 distinct areas drawn, the outer section, the middle and the inner section
# The middle and outer sections modify the circle colour to be more faint the larger the radius

def draw_star_surfaces(color):    
    RADIUS = 100
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

def buildImageDB(star_data_np):
    print("Building Image DB")
    # Setup a progress indicator
    total_stars = len(star_data_np)
    
    # Adjust the progress bar length by one to accommodate the closing bracket
    print('[' + ' ' * 88 + ']', end='', flush=True)
    progress_marker = total_stars // 89  # Adjust the progress bar update frequency
    
    canvas_set = []  # Empty list to store surfaces
    
    for index, star in enumerate(star_data_np):
        # Extract color values using the provided SIndex class indices
        color = (int(star[SIndex.COLOR_K_R] * 255), int(star[SIndex.COLOR_K_G] * 255), int(star[SIndex.COLOR_K_B] * 255))
        
        # Append the generated surface to the canvas set
        canvas_set.append(star_mag_size_scaling(draw_star_surfaces(color)))
        
        # Move the cursor back before the closing bracket to update the progress bar correctly
        if (index + 1) % progress_marker == 0 or index == total_stars - 1:
            print('\r[' + '.' * ((index + 1) // progress_marker) + ' ' * (88 - ((index + 1) // progress_marker)) + ']', end='', flush=True)
    
    print("\nImage DB Completed")
    return canvas_set

def update_star_positions(star_data_np):
    global shift_x, shift_y, shift_z  # Use the global movement variables

    new_positions_3d = []
    for star in star_data_np:
        updated_star = list(star)

        x, y, z, distance_parsecs = star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz], star[SIndex.DISTANCE_PARSECS]
        
        # Use updated global movement variables here
        new_ra, new_dec, new_distance = moveWorld(x, y, z, distance_parsecs, (shift_x, shift_y, shift_z))
        
        new_x, new_y, new_z = ra_dec_distance_to_cartesian(new_ra, new_dec, new_distance)
        ## Have to move from new 3D positions
        
        updated_star[SIndex.RA_DEGREES] = new_ra
        updated_star[SIndex.DEC_DEGREES] = new_dec
        updated_star[SIndex.Dx] = new_x
        updated_star[SIndex.Dy] = new_y
        updated_star[SIndex.Dz] = new_z
        updated_star[SIndex.DISTANCE_PARSECS] = new_distance
        updated_star[SIndex.RA_HOURS] = new_ra / 15
        
        new_positions_3d.append(updated_star)

    return np.array(new_positions_3d)

def update_celestial_projection(new_star_positions_np, eph, constellations, observer_lat, observer_lon, timescale, when ='2024-01-01 00:00'):
    observer_location = wgs84.latlon(observer_lat, observer_lon)
    t = timescale.utc(datetime.strptime(when, '%Y-%m-%d %H:%M').replace(tzinfo=timezone("Europe/Dublin")))

    edges = [edge for _, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, _ in edges]
    edges_star2 = [star2 for _, star2 in edges]

    ra_hours_index = SIndex.RA_HOURS
    dec_degrees_index = SIndex.DEC_DEGREES

    ra_hours = new_star_positions_np[:, ra_hours_index]
    dec_degrees = new_star_positions_np[:, dec_degrees_index]

    # Observer at the given time
    observer = observer_location.at(t)
    
    # Star positions for projection
    star_positions = eph['earth'].at(t).observe(Star(ra_hours=ra_hours, dec_degrees=dec_degrees))
    projection = build_stereographic_projection(observer)
    
    # Projection
    x, y = projection(star_positions)
    x = -x  # Inverting y to match the graphical y-axis direction

    updated_star_positions_np = new_star_positions_np.copy()  # Make a copy to avoid altering the original array
    updated_star_positions_np[:, SIndex.X] = x  # Update X coordinates
    updated_star_positions_np[:, SIndex.Y] = y  # Update Y coordinates
    return updated_star_positions_np, edges_star1, edges_star2

@profile
def draw_constellation_lines(canvas, precalculated_pairs, active_star_data):
    for (x1, y1), (x2, y2) in precalculated_pairs:
        # Perform a visibility check for both stars forming the constellation line
        star1_visible = 0 <= x1 < canvas_width and 0 <= y1 < canvas_height
        star2_visible = 0 <= x2 < canvas_width and 0 <= y2 < canvas_height

        # Draw the line only if both stars are visible on the canvas
        if star1_visible and star2_visible:
            pygame.draw.line(canvas, (255, 255, 255), (x1, y1), (x2, y2), 3)
    return canvas

def draw_menu(screen):
    menu_font = pygame.font.Font(None, 36)  # Adjust size as needed
    menu_items = [
        "Y/I: Move Y axis", "X/V: Move X axis", "Z/C: Move Z axis",
        "C: Toggle constellations", "R: Rotate", "+/-: Zoom",
        "Arrow Keys: Time travel", "WASD: Pan", "U: Toggle positions",
        "M: Show/Hide this menu"
    ]
    for index, item in enumerate(menu_items):
        text_surface = menu_font.render(item, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10 + index * 30))  # Adjust positioning as needed

def writeText (text,color,fontsize):
    font = pygame.font.Font(None, fontsize)
    return font.render(text, True, color)

@profile
def main():
    pygame.init()
    clock = pygame.time.Clock()
    clock.tick(FPS)
    # Get display information
    infoObject = pygame.display.Info()

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Star Chart: Dublin, Ireland")
    global shift_x, shift_y, shift_z
    show_menu = False  # Start with the menu hidden

    canvas = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    canvas.fill((0, 0, 0))
    # Initialize latitude and longitude for Dublin, Ireland
    lat, long = 53.34, -6.26
    observer_lat, observer_lon = 53.34, -6.26
    when = '2024-01-01 00:00'
    timescale = global_timescale
    star_data_array, eph, constellations = load_custom_star_data('../datasets/star_database_colors.json')
    star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, when)
    # Define column names
    column_names_for_csv = ["HIP", "MAGNITUDE", "RA_DEGREES", "DEC_DEGREES", "PARALLAX_MAS", "RA_MAS_PER_YEAR", "DEC_MAS_PER_YEAR",
                    "DISTANCE_PARSECS", "ABS_MAG", "COLOR_K_R", "COLOR_K_G", "COLOR_K_B", "Dx", "Dy", "Dz","GLON", "GLAT",
                    "RA_HOURS", "EPOCH_YEAR", "stereo_X", "stereo_Y"]
    header_string = ",".join(column_names_for_csv)

    #np.savetxt("../datasets/star_data_np.csv", star_data_np, delimiter=',', header=header_string, comments='', fmt='%s')

    new_star_positions_np = update_star_positions(star_data_np)
    updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, observer_lat, observer_lon, timescale, when)
    #np.savetxt("../datasets/star_data_np_galactic.csv", star_data_np, delimiter=',', header=header_string, comments='', fmt='%s')
    np.savetxt("../datasets/updated_star_positions_galactic.csv", updated_star_positions_np, delimiter=',', header=header_string, comments='', fmt='%s')
    
    canvas_set = buildImageDB(star_data_np)
    print(f"Before shift: RA={updated_star_positions_np[418, SIndex.RA_HOURS]*15}, DEC={updated_star_positions_np[418, SIndex.DEC_DEGREES]}, stereo_X = {updated_star_positions_np[418, SIndex.X]}, stereo_y = {updated_star_positions_np[418,SIndex.Y]}, distance = {updated_star_positions_np[418, SIndex.DISTANCE_PARSECS]}")

    draw_constellations = False
    zoom_factor = 1.0
    current_time = datetime.strptime("2024-01-01 00:00", '%Y-%m-%d %H:%M')
    time_delta = timedelta(minutes=1)
    rotate = False
    x_offset = 0
    y_offset = 0
    use_updated_positions = False  # Flag to toggle between original and updated positions
    # Initialize these flags and variables before the main loop
    track_axes_changes = False  # Flag to toggle tracking on or off
    prev_shift_x, prev_shift_y, prev_shift_z = 0, 0, 0  # To remember previous shift values for comparison
    SIRIUS_HIP = 32349
    POLARIS_HIP = 11767
    BETELGEUSE_HIP = 27989
    APLHACENTAURI_HIP = 71683  
    X_SGR_HIP = 87072
    REF_HIP = 99999
    sirius_label = writeText("Sirius", CIndex.WHITE,FIndex.MEDIUM)
    polaris_label = writeText("Polaris", CIndex.WHITE,FIndex.MEDIUM)
    orion_label = writeText("Betelgeuse", CIndex.WHITE, FIndex.MEDIUM) 
    alphaCentA = writeText("ALpha Centauri", CIndex.WHITE, FIndex.MEDIUM)
    xsgr_label = writeText("X-SGR", CIndex.WHITE, FIndex.MEDIUM)
    ref_label = writeText("Reference", CIndex.WHITE, FIndex.MEDIUM)
    # Main loop
    print("running simulation")
    running = True
    while running:
    # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    draw_constellations = not draw_constellations
                elif event.key == pygame.K_r:
                    rotate = not rotate
                elif event.key == pygame.K_LEFT:
                    current_time -= time_delta
                elif event.key == pygame.K_RIGHT:
                    current_time += time_delta
                elif event.key == pygame.K_u:
                    use_updated_positions = not use_updated_positions
                    track_axes_changes = not track_axes_changes
                    if track_axes_changes:
                        print("Start tracking axes changes.")
                    else:
                        print("Stop tracking axes changes.")
                elif event.key == pygame.K_m:
                    show_menu = not show_menu
    # Continuous actions for moving and zooming
        keys = pygame.key.get_pressed()  # This needs to be inside the while loop
        if keys[pygame.K_w]:
            y_offset += 100
        elif keys[pygame.K_s]:
            y_offset -= 100
        if keys[pygame.K_a]:
            x_offset += 100
        elif keys[pygame.K_d]:
            x_offset -= 100
        if keys[pygame.K_y]:
            shift_y -= 1
        elif keys[pygame.K_i]:
            shift_y += 1
        if keys[pygame.K_x]:
            shift_x -= 1
        elif keys[pygame.K_b]:
            shift_x += 1
        if keys[pygame.K_z]:
            shift_z += 1
        elif keys[pygame.K_v]:
            shift_z -= 1
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            zoom_factor *= 1.1
        elif keys[pygame.K_MINUS]:
            zoom_factor /= 1.1

        if track_axes_changes and (shift_x != prev_shift_x or shift_y != prev_shift_y or shift_z != prev_shift_z):
            print(f"Axes changed to X: {shift_x}, Y: {shift_y}, Z: {shift_z}")
            if use_updated_positions:
                new_star_positions_np = update_star_positions(star_data_np)
                updated_star_positions_np, edges_star1, edges_star2 = update_celestial_projection(new_star_positions_np, eph, constellations, observer_lat, observer_lon, timescale, current_time.strftime('%Y-%m-%d %H:%M'))
                print(f"After shift: RA={updated_star_positions_np[418, SIndex.RA_HOURS]*15}, DEC={updated_star_positions_np[418, SIndex.DEC_DEGREES]}, stereo_X = {updated_star_positions_np[0, SIndex.X]}, stereo_y = {updated_star_positions_np[418,SIndex.Y]}, distance = {updated_star_positions_np[418, SIndex.DISTANCE_PARSECS]}")
                print(f"Distance of X-SGR = {updated_star_positions_np[6522 ,SIndex.DISTANCE_PARSECS]}")
            prev_shift_x, prev_shift_y, prev_shift_z = shift_x, shift_y, shift_z

        if rotate:
            current_time += time_delta

        if not use_updated_positions:
            star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, current_time.strftime('%Y-%m-%d %H:%M'))

        active_star_data = updated_star_positions_np if use_updated_positions else star_data_np
        canvas.fill((0, 0, 0))
        index = 0
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        #Inside the main loop, when iterating over stars to draw them
        for star in active_star_data:
            hip_id = star[SIndex.HIP]  # Get HIP ID of the current star
            x, y = (star[-2], star[-1]) if use_updated_positions else (star[SIndex.X], star[SIndex.Y])
            x, y = preprocess_coordinates(x, y, center_x, center_y, zoom_factor, x_offset, y_offset)
            
            newmag = calculate_apparent_magnitude(star[SIndex.ABS_MAG], star[SIndex.DISTANCE_PARSECS])

            if 0 <= x < canvas_width and 0 <= y < canvas_height:
                #mag = round(star[SIndex.MAGNITUDE]) if round(star[SIndex.MAGNITUDE]) <= 6 else 6
                mag = round(newmag) if round(newmag) <= 6 else 6
#               color = (int(star[SIndex.COLOR_K_R] * 255), int(star[SIndex.COLOR_K_G] * 255), int(star[SIndex.COLOR_K_B] * 255))
                offset = canvas_set[index][mag][0].get_width() / 2
                canvas.blit(twinkle_star(canvas_set[index][mag]), (x - offset, y - offset), special_flags=pygame.BLEND_ADD)
                
                # Check for specific stars and draw their labels if their HIP ID matches
                if hip_id == SIRIUS_HIP:
                    canvas.blit(sirius_label, (x - offset, y - offset - 20))  # Adjust position as needed
                elif hip_id == POLARIS_HIP:
                    canvas.blit(polaris_label, (x - offset, y - offset - 20))
                elif hip_id == BETELGEUSE_HIP:
                    canvas.blit(orion_label, (x - offset, y - offset - 20))
                elif hip_id == APLHACENTAURI_HIP:
                    canvas.blit(alphaCentA, (x - offset, y - offset - 20))
                # elif hip_id == X_SGR_HIP:
                #     canvas.blit(xsgr_label, (x - offset, y - offset - 20))
                # elif hip_id == REF_HIP:
                #     canvas.blit(ref_label, (x - offset, y - offset - 20))
            index += 1
        # Recalculate constellation lines if needed
        if draw_constellations:
            precalculated_pairs = precalculate_star_pairs(active_star_data, edges_star1, edges_star2, center_x, center_y, zoom_factor, x_offset, y_offset)
            canvas = draw_constellation_lines(canvas, precalculated_pairs, active_star_data)

        scaled_canvas = pygame.transform.smoothscale(canvas, (screen_width, screen_height))
        screen.blit(scaled_canvas, (0, 0))

        if show_menu:
            draw_menu(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()
