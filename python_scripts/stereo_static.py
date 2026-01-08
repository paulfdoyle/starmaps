import pandas as pd
import numpy as np
from skyfield.api import load
from skyfield.data import stellarium
import math
from skyfield.api import Star, wgs84
from skyfield.projections import build_stereographic_projection
from datetime import datetime, timedelta
from pytz import timezone
import pygame
from pygame import gfxdraw
import random


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

class CIndex:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    CYAN = (0, 255, 255)
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
    O_Type = (140, 176, 255)  # Blue
    B_Type = (170, 191, 255)  # Blue-White
    A_Type = (202, 215, 255)  # White
    F_Type = (248, 247, 255)  # Yellow-White
    G_Type = (255, 233, 12)   # Yellow
    K_Type = (255, 165, 12)   # Orange
    M_Type = (255, 100, 12)   # Red

star_list = [
    StarColourIndex.O_Type,
    StarColourIndex.B_Type,
    StarColourIndex.A_Type,
    StarColourIndex.F_Type,
    StarColourIndex.G_Type,
    StarColourIndex.K_Type,
    StarColourIndex.M_Type,
]

# Star Labels
SIRIUS_HIP = 32349
POLARIS_HIP = 11767
BETELGEUSE_HIP = 27989
APLHACENTAURI_HIP = 71683
GC_HIP = 99999
SOL_HIP = 99998

def writeText(text, color, fontsize):
    font = pygame.font.Font(None, fontsize)
    return font.render(text, True, color)

def set_size_screen(width, height):
    global screen_width, screen_height
    screen_width, screen_height = width, height

def set_size_canvas(size):
    global canvas_width, canvas_height
    canvas_width = canvas_height = size

def get_size_screen():
    return screen_width, screen_height

def get_size_canvas():
    return canvas_width, canvas_height

timescale = load.timescale()
BF = 2.512  # Brightness factor Created a bigger size difference between stars on the screen
BRM6 = 4  # Base radius for magnitude 6 stars, this will control if mag 6 is visible.
screen_width, screen_height = 1300, 1300
canvas_width, canvas_height = 6500, 6500
lat, long = 53.34, -5.26
when = '2000-01-01 00:00'

def galactic_to_cartesian(l, b, d):
    l_rad = np.radians(l)
    b_rad = np.radians(b)
    x = d * math.cos(b_rad) * math.cos(l_rad)
    y = d * math.cos(b_rad) * math.sin(l_rad)
    z = d * math.sin(b_rad)
    return x, y, z

def galactic_to_equatorial_proper(l, b):
    RA_NGP = 192.859508
    DEC_NGP = 27.128336
    L_NCP = 122.931919
    l_rad = np.radians(l)
    b_rad = np.radians(b)
    RA_NGP_rad = np.radians(RA_NGP)
    DEC_NGP_rad = np.radians(DEC_NGP)
    sin_b = np.sin(b_rad)
    cos_b = np.cos(b_rad)
    sin_DEC_NGP = np.sin(DEC_NGP_rad)
    cos_DEC_NGP = np.cos(DEC_NGP_rad)
    sin_DEC = sin_b * sin_DEC_NGP + cos_b * cos_DEC_NGP * np.cos(l_rad - np.radians(L_NCP))
    DEC = np.arcsin(sin_DEC)
    sin_l_minus_L = np.sin(l_rad - np.radians(L_NCP))
    cos_l_minus_L = np.cos(l_rad - np.radians(L_NCP))
    y = sin_l_minus_L * cos_b
    x = cos_b * sin_DEC_NGP * cos_l_minus_L - sin_b * cos_DEC_NGP
    RA = RA_NGP_rad + np.arctan2(y, x)
    RA_deg = (np.degrees(RA) - 180) % 360
    DEC_deg = np.degrees(DEC)
    return RA_deg, DEC_deg

def color_distance(rgb1, rgb2):
    return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5

def find_closest_star_index(rgb):
    star_list = [
        (140, 176, 255),
        (170, 191, 255),
        (202, 215, 255),
        (248, 247, 255),
        (255, 233, 12),
        (255, 165, 12),
        (255, 100, 12),
    ]
    
    closest_star_index = None
    min_distance = float('inf')
    for index, star_rgb in enumerate(star_list):
        distance = color_distance(rgb, star_rgb)
        if distance < min_distance:
            min_distance = distance
            closest_star_index = index
    return closest_star_index

def star_mag_size_scaling(canvas):
    MAG_RANGE = 7
    rows, cols = MAG_RANGE, len(canvas)
    canvas2D = [[None for _ in range(cols)] for _ in range(rows)]        
    for x in range(rows):
        for y in range(cols):
            scaling_factor = BF ** (6 - x) if x < 6 else 1
            radius = int(BRM6 * math.sqrt(scaling_factor))
            canvas2D[x][y] = pygame.transform.smoothscale(canvas[y], (radius, radius))
    return canvas2D  

def calculate_apparent_magnitude(absolute_magnitude, distance_parsecs, hip_id):
    if distance_parsecs <= 0:
        return None
    apparent_magnitude = absolute_magnitude + 5 * (math.log10(distance_parsecs) - 1)
    return apparent_magnitude

def preprocess_coordinates(x, y, center_x, center_y, zoom_factor, x_offset, y_offset):
    translated_x = (x + 1) * center_x - center_x
    translated_y = (y + 1) * center_y - center_y
    zoomed_x = (translated_x + x_offset) * zoom_factor
    zoomed_y = (translated_y + y_offset) * zoom_factor
    final_x = center_x + zoomed_x
    final_y = center_y + zoomed_y
    return final_x, final_y

def twinkle_star(elements):
    if not elements:
        return None
    return random.choice(elements)

def load_custom_star_data(json_file_path):
    try:
        print("Loading data from file")
        required_columns = [
            'hip', 'mag', 'ra_decdeg', 'dec_decdeg', 'plx', 'pmra', 'pmdec', 'dist', 'absmag',
            'kR', 'kG', 'kB', 'x', 'y', 'z', "GLON", "GLAT"
        ]
        df = pd.read_json(json_file_path)
        df = df[required_columns]
        df.columns = (
            'hip', 'magnitude', 'ra_degrees', 'dec_degrees', 'parallax_mas', 'ra_mas_per_year',
            'dec_mas_per_year', 'distance_parsecs', 'absolutem', 'kR', 'kG', 'kB', '3dx', '3dy', '3dz', "GLON", "GLAT"
        )
        df = df.replace('', np.nan).dropna()
        df = df.assign(ra_hours=df['ra_degrees'] / 15.0, epoch_year=2000)

        for index, row in df.iterrows():
            ra_deg, dec_deg = galactic_to_equatorial_proper(row['GLON'], row['GLAT'])
            df.at[index, 'ra_degrees'] = ra_deg
            df.at[index, 'dec_degrees'] = dec_deg
            x, y, z = galactic_to_cartesian(row['GLON'], row['GLAT'], row['distance_parsecs'])
            df.at[index, '3dx'] = x
            df.at[index, '3dy'] = y
            df.at[index, '3dz'] = z

        star_data_array = df.to_numpy()
        star_types = [find_closest_star_index((row[SIndex.COLOR_K_R] * 255, row[SIndex.COLOR_K_G] * 255, row[SIndex.COLOR_K_B] * 255)) for row in star_data_array]
        star_data_array = np.column_stack((star_data_array, star_types))

        eph = load('de421.bsp')
        url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern_st/constellationship.fab')
        with load.open(url) as f:
            constellations = stellarium.parse_constellations(f)
        
        return star_data_array, eph, constellations
    except Exception as e:
        print(f"An error occurred while loading or processing the star data: {e}")
        return None, None, None

def collect_celestial_data(star_data_np, eph, constellations, lat, long, timescale, when):
    observer_location = wgs84.latlon(lat, long)
    t = timescale.utc(datetime.strptime(when, '%Y-%m-%d %H:%M').replace(tzinfo=timezone("Europe/Dublin")))
    observer = observer_location.at(t)
    if constellations is not None:
        edges = [edge for _, edges in constellations for edge in edges]
        edges_star1 = [star1 for star1, _ in edges]
        edges_star2 = [star2 for _, star2 in edges]
    else:
        edges = []
        edges_star1 = []
        edges_star2 = []
        print("Warning: 'constellations' is None")
    center_object = Star(ra=observer.radec()[0], dec=observer.radec()[1])
    center = eph['earth'].at(t).observe(center_object)
    projection = build_stereographic_projection(center)
    ra_hours = star_data_np[:, SIndex.RA_HOURS]
    dec_degrees = star_data_np[:, SIndex.DEC_DEGREES]
    star_positions = eph['earth'].at(t).observe(Star(ra_hours=ra_hours, dec_degrees=dec_degrees))
    x, y = projection(star_positions)
    y = -y
    x = np.around(x, 10)
    y = np.around(y, 10)
    projected_positions = np.column_stack((x, y))
    star_data_np_with_xy = np.hstack((star_data_np, projected_positions))
    return star_data_np_with_xy, edges_star1, edges_star2

def draw_star_surfaces(color):
    RADIUS = 100
    NUMIMAGES = 4
    TR = 10
    star_surface = []
    radius_half = RADIUS // 2
    radius_quarter = RADIUS // 4
    mix_ratios1 = [(i - radius_quarter) / radius_quarter for i in range(radius_quarter, radius_half)]
    mix_ratios2 = [(i - radius_half) / radius_half for i in range(radius_half, RADIUS)]
    for j in range(NUMIMAGES):
        star_surface.append(pygame.Surface((RADIUS*2, RADIUS*2), pygame.SRCALPHA))
        for i in range(RADIUS, 0, -1):
            if i < radius_quarter:
                gradient_color = (255-(j*TR), 255-(j*TR), 255-(j*TR))
            elif i < radius_half:
                mix_ratio = mix_ratios1[i - radius_quarter]
                gradient_color = [int(255-(j*TR) + (color_component - 255) * mix_ratio) for color_component in color]
            else:
                mix_index = max(0, min(len(mix_ratios2) - 1, i - radius_half))
                mix_ratio = mix_ratios2[mix_index]
                gradient_color = [int(color_component * (1 - mix_ratio)-(j*TR)) for color_component in color]
            gradient_color = tuple(max(0, min(255, c)) for c in gradient_color)
            pygame.gfxdraw.filled_circle(star_surface[j], RADIUS, RADIUS, i, gradient_color)
    return star_surface

def buildStarImageDB():
    canvas_set = []
    for star_rgb in star_list:
        canvas_set.append(star_mag_size_scaling(draw_star_surfaces(star_rgb)))
    print("Created new star DB")
    return canvas_set

def initialize_pygame():
    pygame.init()
    set_size_screen(1300, 1300)
    set_size_canvas(6500)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Star Chart: Dublin, Ireland")
    return screen, pygame.time.Clock()

def create_canvas():
    canvas = pygame.Surface((canvas_width, canvas_height))
    canvas.fill(CIndex.BLACK)
    return canvas

def load_data():
    star_data_array, eph, constellations = load_custom_star_data('../datasets/star_database_colors.json')
    star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, when)
    return star_data_array, star_data_np, eph, constellations, edges_star1, edges_star2

def initialize_labels():
    return {
        'sirius': writeText("Sirius", CIndex.WHITE, FIndex.MEDIUM),
        'polaris': writeText("Polaris", CIndex.WHITE, FIndex.MEDIUM),
        'orion': writeText("Betelgeuse", CIndex.WHITE, FIndex.MEDIUM),
        'alphaCentA': writeText("Alpha Centauri", CIndex.WHITE, FIndex.MEDIUM),
        'Galactic_Centre': writeText("GC", CIndex.WHITE, FIndex.MEDIUM),
        'Sun': writeText("Sun", CIndex.WHITE, FIndex.MEDIUM),
    }

star_coordinates = {}

def draw_labels(canvas, active_star_data, control_vars, canvas_set, labels):
    global center_x, center_y
    global star_coordinates
    star_coordinates.clear()
    center_x = canvas_width / 2
    center_y = canvas_height / 2
    for star in active_star_data:
        hip_id = star[SIndex.HIP]
        x, y = star[-2], star[-1]
        x, y = preprocess_coordinates(x, y, center_x, center_y, control_vars['zoom_factor'], control_vars['x_offset'], control_vars['y_offset'])
        star_coordinates[(x, y)] = hip_id
        newmag = calculate_apparent_magnitude(star[SIndex.ABS_MAG], star[SIndex.DISTANCE_PARSECS], hip_id)
        if newmag is not None and 0 <= x < canvas_width and 0 <= y < canvas_height:
            mag = round(newmag) if round(newmag) <= 6 else 6
            mag = min(max(mag, 0), 6)
            star_type_index = int(star[SIndex.STAR_TYPE])
            offset = canvas_set[star_type_index][mag][0].get_width() / 2
            canvas.blit(twinkle_star(canvas_set[star_type_index][mag]), (x - offset, y - offset), special_flags=pygame.BLEND_ADD)
            if hip_id == SIRIUS_HIP:
                canvas.blit(labels['sirius'], (x - offset, y - offset - 20))
            elif hip_id == POLARIS_HIP:
                canvas.blit(labels['polaris'], (x - offset, y - offset - 20))
            elif hip_id == BETELGEUSE_HIP:
                canvas.blit(labels['orion'], (x - offset, y - offset - 20))
            elif hip_id == APLHACENTAURI_HIP:
                canvas.blit(labels['alphaCentA'], (x - offset, y - offset - 20))
            elif hip_id == GC_HIP:
                canvas.blit(labels['Galactic_Centre'], (x - offset, y - offset - 20))
            elif hip_id == SOL_HIP:
                canvas.blit(labels['Sun'], (x - offset, y - offset - 20))

def main():
    global star_data_array, star_data_np, eph, constellations, edges_star1, edges_star2
    FPS = 20
    screen, clock = initialize_pygame()
    canvas = create_canvas()
    star_data_array, star_data_np, eph, constellations, edges_star1, edges_star2 = load_data()
    labels = initialize_labels()
    canvas_set = buildStarImageDB()
    control_vars = {
        'zoom_factor': 1.0,
        'x_offset': 0,
        'y_offset': 0,
    }
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        star_data_np, edges_star1, edges_star2 = collect_celestial_data(star_data_array, eph, constellations, lat, long, timescale, when)
        canvas.fill(CIndex.BLACK)
        draw_labels(canvas, star_data_np, control_vars, canvas_set, labels)
        scaled_canvas = pygame.transform.smoothscale(canvas, (screen_width, screen_height))
        screen.blit(scaled_canvas, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    main()

pygame.quit()
