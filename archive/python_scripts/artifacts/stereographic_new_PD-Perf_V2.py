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
FPS = 10  # Frames per second

# These index constants are assignment order dependent. Change with caution
class SIndex:
    MAGNITUDE = 0
    RA_DEGREES = 1
    DEC_DEGREES = 2
    PARALLAX_MAS = 3
    RA_MAS_PER_YEAR = 4
    DEC_MAS_PER_YEAR = 5
    DISTANCE_PARSECS = 6
    ABS_MAG = 7
    COLOR_K_R = 8
    COLOR_K_G = 9
    COLOR_K_B = 10
    RA_HOURS = 11
    EPOCH_YEAR = 12
    X = 13
    Y = 14

def load_custom_star_data(json_file_path):
    print ("loading data from file")
    required_columns = ['hip', 'mag', 'ra_decdeg', 'dec_decdeg', 'plx', 'pmra', 'pmdec', 'dist', 'absmag', 'kR', 'kG','kB']
    df = pd.read_json(json_file_path)
    df = df[required_columns]
    pd.set_option('display.max_columns', None)  # Adjust as per your DataFrame's column count
    pd.set_option('display.width', None)  # Use None for automatically adjusting to the screen
    # These column renames seem to be important for later. Why?
    df.columns = (
        'hip', 'magnitude', 'ra_degrees', 'dec_degrees',
        'parallax_mas', 'ra_mas_per_year', 'dec_mas_per_year',
        'distance_parsecs','absolutem', 'kR', 'kG','kB'
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

    # Why is this step necessary?
    df.set_index('hip', inplace=True)

    eph = load('de421.bsp')
    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
           '/skycultures/modern_st/constellationship.fab')
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)

    return df, eph, constellations

@profile
def collect_celestial_data(df, eph, constellations, lat, long, timescale, when = '2024-03-11 00:00'):
    observer_location = wgs84.latlon(lat, long)
    t = timescale.utc(datetime.strptime(when, '%Y-%m-%d %H:%M').replace(tzinfo=timezone("Europe/Dublin")))
    
    observer = observer_location.at(t)
    edges = [edge for _, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, _ in edges]
    edges_star2 = [star2 for _, star2 in edges]

    center_object = Star(ra=observer.radec()[0], dec=observer.radec()[1])
    center = eph['earth'].at(t).observe(center_object)
    projection = build_stereographic_projection(center)

    star_positions = eph['earth'].at(t).observe(Star.from_dataframe(df))
    df['x'], df['y'] = projection(star_positions)
    df['y'] = -df['y']

    return df, edges_star1, edges_star2

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

def precalculate_star_pairs(df_filtered, edges_star1, edges_star2, center_x, center_y, zoom_factor, x_offset, y_offset):
    precalculated_pairs = []
    for s1, s2 in zip(edges_star1, edges_star2):
        if s1 in df_filtered.index and s2 in df_filtered.index:
            star1 = df_filtered.loc[s1]
            star2 = df_filtered.loc[s2]

            # Preprocess the coordinates similarly to the draw_constellation_lines function
            x1, y1 = preprocess_coordinates(star1['x'], star1['y'], center_x, center_y, zoom_factor, x_offset, y_offset)
            x2, y2 = preprocess_coordinates(star2['x'], star2['y'], center_x, center_y, zoom_factor, x_offset, y_offset)

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

def buildImageDB(df):
    print ("Building Image DB")
#     print('[', end='', flush=True)
    print('[' + ' ' * 89 + ']', end='', flush=True)
    print('\b' * (89 + 1), end='', flush=True)
   
    df_filtered = df[df['magnitude'] <= 10]
    star_matrix = df_filtered.astype(float).to_numpy()
#     nstars = star_matrix.shape[0]
    canvas_set = [] # empty list
    index = 0
    for star in star_matrix:
        index+=1
#         mag = star[SIndex.MAGNITUDE]
#         absmag = star[SIndex.ABS_MAG]
        color = (int(star[8] * 255), int(star[9] * 255), int(star[10] * 255))
        canvas_set.append(star_mag_size_scaling(draw_star_surfaces(color)))
        if index % 100 == 0:
            print('.', end='', flush=True)           
#     print(']', flush=True)
    print("image DB Completed")
    return canvas_set

@profile
def draw_constellation_lines(canvas, precalculated_pairs):
    for (x1, y1), (x2, y2) in precalculated_pairs:
        pygame.draw.line(canvas, (255, 255, 255), (x1, y1), (x2, y2), 3)
    return canvas

@profile
def main():
    pygame.init()
    clock = pygame.time.Clock()
    clock.tick(FPS)
    # Get display information
    infoObject = pygame.display.Info()

    # Retrieve the screen width and height
#     screen_width = infoObject.current_w
#     screen_height = infoObject.current_h

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Star Chart: Dublin, Ireland")
    
#   canvas_width, canvas_height = 10000, 10000  # Large off-screen canvas size
    canvas = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
    canvas.fill ((0,0,0))  
    # Load data and collect celestial data
    df, eph, constellations = load_custom_star_data('../datasets/star_database_colors.json')

    # Initialize latitude and longitude for Dublin, Ireland
    lat, long = 53.34, -6.26
    when = '2024-03-11 00:00'
    timescale = global_timescale
    df, edges_star1, edges_star2 = collect_celestial_data(df, eph, constellations, lat, long, timescale, when)
    
    # Build the imageDB of stars
#     star_matrix = df_filtered.astype(float).to_numpy()
#     nstars = star_matrix.shape[0]
#     canvas_set = [] # empty list
#     index = 0
#     for star in star_matrix:
#             index+=1
#             mag = star[SIndex.MAGNITUDE]
#             absmag = star[SIndex.ABS_MAG]
#             color = (int(star[SIndex.COLOR_K_R] * 255), int(star[SIndex.COLOR_K_G] * 255), int(star[SIndex.COLOR_K_B] * 255))
#             canvas_set.append(star_mag_size_scaling(draw_star_surfaces(color)))
#
    canvas_set = buildImageDB(df)
    
    draw_constellations = False
    zoom_factor = 1.0
    current_time = datetime.strptime("2024-03-11 00:00", '%Y-%m-%d %H:%M')
    time_delta = timedelta(minutes=1)
    rotate=False
    x_offset = 0
    y_offset = 0
    # Main loop
    print ("running simulation")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    draw_constellations = not draw_constellations
                    print(f"draw_constellations toggled to: {draw_constellations}")
                elif event.key == pygame.K_n:
                    print(f"move north: {rotate}")
                elif event.key == pygame.K_r:
                    if rotate == True:
                        rotate = False
                    else:
                        rotate=True
                    print(f"Rotate On: {rotate}")
                elif event.key in [pygame.K_PLUS, pygame.K_EQUALS]:
                    zoom_factor *= 1.1
                    print(f"Zoom factor increased to: {zoom_factor}")
                elif event.key == pygame.K_MINUS:
                    zoom_factor /= 1.1
                    print(f"Zoom factor decreased to: {zoom_factor}")
                elif event.key == pygame.K_LEFT:
                    current_time -= time_delta
                    print(f"Current time set back to: {current_time.strftime('%Y-%m-%d %H:%M')}")
                    df, edges_star1, edges_star2 = collect_celestial_data(df, eph, constellations, lat, long, timescale, current_time.strftime('%Y-%m-%d %H:%M'))
                elif event.key == pygame.K_RIGHT:
                    current_time += time_delta
                # elif event.key ==pygame.K_UP:
                #     lat += 10 if lat <= 80 else 0
                # elif event.key ==pygame.K_DOWN:
                #     lat -= 10 if lat >= -80 else 0
                # elif event.key == pygame.K_z:
                #     long -= 10
                #     long = long + 360 if long < -180 else long  # Wrap around globally
                # elif event.key == pygame.K_x:
                #     long += 10
                #     long = long - 360 if long > 180 else long  # Wrap around globally
                elif event.key == pygame.K_w:
                    y_offset += 100  # Move up
                elif event.key == pygame.K_s:
                    y_offset -= 100  # Move down
                elif event.key == pygame.K_a:
                    x_offset += 100  # Move left
                elif event.key == pygame.K_d:
                    x_offset -= 100  # Move right
                    print(f"Current time advanced to: {current_time.strftime('%Y-%m-%d %H:%M')}")
                    df, edges_star1, edges_star2 = collect_celestial_data(df, eph, constellations, lat, long, timescale, current_time.strftime('%Y-%m-%d %H:%M'))

        if rotate == True:
            current_time += time_delta
               
        df, edges_star1, edges_star2 = collect_celestial_data(df, eph, constellations, lat, long, timescale, current_time.strftime('%Y-%m-%d %H:%M'))
        canvas.fill((0, 0, 0))
        df_filtered = df[df['magnitude'] <= 10]
        column_names = df_filtered.columns.tolist()
        header_string = ','.join(column_names)
        star_matrix = df_filtered.astype(float).to_numpy()
#       nstars = star_matrix.shape[0]
        index=0
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        for star in star_matrix:
    # Translate so the center of the canvas is the origin
            translated_x = (star[SIndex.X] + 1) * center_x - center_x
            translated_y = (star[SIndex.Y] + 1) * center_y - center_y
    # Apply zoom
            zoomed_x = translated_x * zoom_factor
            zoomed_y = translated_y * zoom_factor
    # Translate back
            x = zoomed_x + center_x + x_offset
            y = zoomed_y + center_y + y_offset
#             mag = star[SIndex.MAGNITUDE]
#             absmag = star[SIndex.ABS_MAG]  
#             distance = star[SIndex.DISTANCE_PARSECS]  
            
            # Using this code we can move in space and have the apparent magnitude recalculated
            calc_mag = calculate_apparent_magnitude(star[SIndex.ABS_MAG],star[SIndex.DISTANCE_PARSECS])
#             color = (int(star[SIndex.COLOR_K_R] * 255), int(star[SIndex.COLOR_K_G] * 255), int(star[SIndex.COLOR_K_B] * 255))
            if (round(calc_mag) > 6):  # To stop MAG index being rounded up to 7
                mag = 6
            else:
                mag = round(calc_mag)
            offset = canvas_set[index][mag][0].get_width()/2  
            canvas.blit(twinkle_star(canvas_set[index][mag]), (x-offset,y-offset),special_flags=pygame.BLEND_ADD)       
            index+=1

    # Draw constellations directly on the scaled canvas
        precalculated_pairs = precalculate_star_pairs(df_filtered, edges_star1, edges_star2, center_x, center_y, zoom_factor, x_offset, y_offset)
        if draw_constellations:
            canvas = draw_constellation_lines(canvas, precalculated_pairs)

        scaled_canvas = pygame.transform.smoothscale(canvas, (screen_width, screen_height))
        screen.blit(scaled_canvas, (0, 0))
        pygame.display.flip()
        #np.savetxt('../datasets/star_matrix_Original.csv', star_matrix, delimiter=',', fmt='%s', header=header_string, comments='')
# Initialize Pygame and settings

if __name__ == "__main__":
    main()
    
pygame.quit()
