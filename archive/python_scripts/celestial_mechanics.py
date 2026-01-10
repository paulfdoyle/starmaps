import math
import numpy as np
from skyfield.api import Star, wgs84
from skyfield.projections import build_stereographic_projection
from datetime import datetime
from pytz import timezone
from utils import SIndex


def color_distance(rgb1, rgb2):
    """
    Calculate the Euclidean distance between two RGB colors.
    """
    return sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5

def find_closest_star_index(rgb):
    """
    Find the index of the closest star color type to the given RGB values.
    """
    star_list = [
        (140, 176, 255), # O_Type
        (170, 191, 255), # B_Type
        (202, 215, 255), # A_Type
        (248, 247, 255), # F_Type
        (255, 233, 12),  # G_Type
        (255, 165, 12),  # K_Type
        (255, 100, 12),  # M_Type
    ]
    
    closest_star_index = None
    min_distance = float('inf')

    # Iterate over each star color to find the closest match
    for index, star_rgb in enumerate(star_list):
        distance = color_distance(rgb, star_rgb)
        if distance < min_distance:
            min_distance = distance
            closest_star_index = index

    return closest_star_index

def find_closest_star_color(rgb):
    """
    Find the closest star color type to the given RGB values. Function only used for testing.
    """
    star_colors = {
        'O-Type (Blue)': (140, 176, 255),
        'B-Type (Blue-White)': (170, 191, 255),
        'A-Type (White)': (202, 215, 255),
        'F-Type (Yellow-White)': (248, 247, 255),
        'G-Type (Yellow)': (255, 233, 12),
        'K-Type (Orange)': (255, 165, 12),
        'M-Type (Red)': (255, 100, 12)
    }

    closest_star_type = None
    min_distance = float('inf')

    for star_type, star_rgb in star_colors.items():
        distance = color_distance(rgb, star_rgb)
        if distance < min_distance:
            min_distance = distance
            closest_star_type = star_type

    return closest_star_type, star_colors[closest_star_type]

def collect_celestial_data(star_data_np, eph, constellations, lat, long, timescale, when):
    """
    Collect data for celestial observations.

    Args:
    - star_data_np (np.ndarray): NumPy array of star data.
    - eph (Ephemeris): Skyfield ephemeris data.
    - constellations (list): List of constellations.
    - lat, long (float): Latitude and longitude for observation.
    - timescale (Timescale): Skyfield timescale object.
    - when (str): Date and time for observations.

    Returns:
    - tuple: (star_data_np_with_xy, edges_star1, edges_star2)
    """
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
    y = -y  # Adjust y-axis

    x = np.around(x, 10)
    y = np.around(y, 10)

    projected_positions = np.column_stack((x, y))
    star_data_np_with_xy = np.hstack((star_data_np, projected_positions))

    return star_data_np_with_xy, edges_star1, edges_star2

def update_celestial_projection(new_star_positions_np, eph, constellations, observer_lat, observer_lon, timescale, when):
    observer_location = wgs84.latlon(observer_lat, observer_lon)
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

    ra_hours = new_star_positions_np[:, SIndex.RA_HOURS]
    dec_degrees = new_star_positions_np[:, SIndex.DEC_DEGREES]
    
    # Star positions for projection
    star_positions = eph['earth'].at(t).observe(Star(ra_hours=ra_hours, dec_degrees=dec_degrees))
    projection = build_stereographic_projection(observer)
    
    # Projection
    x, y = projection(star_positions)
    y = -y  # Inverting y to match the graphical y-axis direction

    x = np.around(x, 10)
    y = np.around(y, 10)

    updated_star_positions_np = new_star_positions_np.copy()  # Make a copy to avoid altering the original array
    updated_star_positions_np[:, SIndex.X] = x  # Update X coordinates
    updated_star_positions_np[:, SIndex.Y] = y  # Update Y coordinates
    return updated_star_positions_np, edges_star1, edges_star2

def update_star_positions(star_data_np, shift_x, shift_y, shift_z):
    """
    Update star positions based on global movement variables.

    Args:
    - star_data_np (np.ndarray): Numpy array of star data.
    - shift_x, shift_y, shift_z (float): Shifts in the X, Y, and Z axes.

    Returns:
    - np.ndarray: Updated star positions.
    """
    if shift_x == 0 and shift_y == 0 and shift_z == 0:
        # Return a direct copy if no shifts are applied
        return np.copy(star_data_np)
    else:
        new_positions_3d = []
        for star in star_data_np:
            updated_star = list(star)
            x, y, z, distance_parsecs = star[SIndex.Dx], star[SIndex.Dy], star[SIndex.Dz], star[SIndex.DISTANCE_PARSECS]
            glon, glat = star[SIndex.GLON], star[SIndex.GLAT]
            new_ra, new_dec, new_distance = move_world(x, y, z, distance_parsecs, (shift_x, shift_y, shift_z))
            new_x, new_y, new_z = galactic_to_cartesian(glon, glat, new_distance)
            updated_star[SIndex.RA_DEGREES] = new_ra
            updated_star[SIndex.DEC_DEGREES] = new_dec
            updated_star[SIndex.Dx] = new_x
            updated_star[SIndex.Dy] = new_y
            updated_star[SIndex.Dz] = new_z
            updated_star[SIndex.DISTANCE_PARSECS] = new_distance
            updated_star[SIndex.RA_HOURS] = new_ra / 15
            new_positions_3d.append(updated_star)
    return np.array(new_positions_3d)

def move_world(x, y, z, dist_parsecs, move_dist):
    """
    Move a point in 3D space.

    Args:
    - x, y, z (float): Initial coordinates.
    - dist_parsecs (float): Initial distance in parsecs.
    - move_dist (tuple): Tuple of (x, y, z) distances to move in each axis.

    Returns:
    - tuple: New RA, new DEC, and new distance in parsecs.
    """
    x_move, y_move, z_move = move_dist
    new_x = x + x_move
    new_y = y + y_move
    new_z = z + z_move

    glon_new, glat_new = cartesian_to_galactic (new_x,new_y,new_z)
    ra_new, dec_new = galactic_to_equatorial_proper(glon_new, glat_new)
    new_dist = distance_3d(0, 0, 0, new_x, new_y, new_z)

    return ra_new, dec_new, new_dist

def distance_3d(x1, y1, z1, x2, y2, z2):
    """
    Calculate the Euclidean distance between two points in 3D space.

    Args:
    - x1, y1, z1, x2, y2, z2 (float): Coordinates of the two points.

    Returns:
    - float: The Euclidean distance between the two points.
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def calculate_absolute_magnitude(apparent_magnitude, distance_parsecs):
    """
    Calculate the absolute magnitude of a celestial object given its apparent magnitude
    and distance in parsecs.

    Args:
    - apparent_magnitude (float): The apparent magnitude of the celestial object.
    - distance_parsecs (float): The distance to the celestial object in parsecs.

    Returns:
    - float: The absolute magnitude of the celestial object.
    """
    if distance_parsecs <= 0:
        raise ValueError("Distance must be greater than 0.")
    absolute_magnitude = apparent_magnitude - 5 * (math.log10(distance_parsecs) - 1)
    return absolute_magnitude

def calculate_apparent_magnitude(absolute_magnitude, distance_parsecs, hip_id):
    """
    Calculate the apparent magnitude of a celestial object given its absolute magnitude
    and distance in parsecs. Include the HIP ID in error messages for better traceability.

    Args:
    - absolute_magnitude (float): The absolute magnitude of the celestial object.
    - distance_parsecs (float): The distance to the celestial object in parsecs.
    - hip_id (int): The HIP ID of the celestial object, used for identification.

    Returns:
    - float: The apparent magnitude of the celestial object, or None if the distance is <= 0.
    """
    if distance_parsecs <= 0:
        #print(f"Distance must be greater than 0. Skipping star with HIP ID: {hip_id}")
        return None
    apparent_magnitude = absolute_magnitude + 5 * (math.log10(distance_parsecs) - 1)
    return apparent_magnitude


def interpolate_shifts(start_value, end_value, steps):
    interpolated_values = [(start_value + (end_value - start_value) * step / steps) for step in range(steps)]
    interpolated_values.append(end_value)  # Ensure the last value is exactly the end value
    return interpolated_values

def return_to_home(control_vars):
    # Calculate the shifts needed to return to (0, 0, 0)
    shift_x_delta = -control_vars['shift_x']
    shift_y_delta = -control_vars['shift_y']
    shift_z_delta = -control_vars['shift_z']

    # Number of steps for the animation
    steps = 20  # Adjust this value for smoother or faster animation

    # Generate the steps for each axis
    control_vars['shift_x_steps'] = interpolate_shifts(control_vars['shift_x'], 0, steps)
    control_vars['shift_y_steps'] = interpolate_shifts(control_vars['shift_y'], 0, steps)
    control_vars['shift_z_steps'] = interpolate_shifts(control_vars['shift_z'], 0, steps)

    control_vars['current_step'] = 0
    control_vars['animating'] = True  # Start the animation

    print(f"Returning to home (0, 0, 0) from ({control_vars['shift_x']}, {control_vars['shift_y']}, {control_vars['shift_z']})")


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

def cartesian_to_galactic(x, y, z):
    """
    Convert Cartesian coordinates to Galactic coordinates.
    """
    # Distance calculation
    d = np.sqrt(x**2 + y**2 + z**2)

    # Galactic coordinates conversion
    b_rad = np.arcsin(z / d)
    l_rad = np.arctan2(y, x)

    # Convert radians to degrees
    b = np.degrees(b_rad)
    l = np.degrees(l_rad) % 360  # Ensure l is in the range [0, 360)

    return l, b

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
    RA_deg = (np.degrees(RA) -180 ) % 360
    DEC_deg = np.degrees(DEC)
    
    return RA_deg, DEC_deg
