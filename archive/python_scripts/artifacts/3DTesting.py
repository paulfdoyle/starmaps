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


# Setting Global Timescale object
global_timescale = load.timescale()

try:
    profile  # exists when kernprof is running the script
except NameError:
    def profile(func):
        return func  # Return the function unchanged if not profiling

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
    Dx = 11
    Dy = 12
    Dz = 13
    RA_HOURS = 14
    EPOCH_YEAR = 15
    X = 16
    Y = 17

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

def moveWorld (x,y,z,dist_parasec,moveDist):
    x_move,y_move,z_move = moveDist
    new_x = x+x_move
    new_y = y+y_move
    new_z = z+z_move


    ra_new, dec_new = cartesian_to_ra_dec(new_x,new_y,new_z)
    newDist = distance_3d(0,0,0,new_x,new_y,new_z)



    print("New Dist = ",newDist)   
    print(f"Cartesian coordinates with distance: x={x}, y={y}, z={z}")
    print ("ra=",ra_new,dec_new)
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


def calculate_apparent_magnitude(absolute_magnitude, distance_parsecs):     
    if distance_parsecs <= 0:
        raise ValueError("Distance must be greater than 0.")
    
    apparent_magnitude = absolute_magnitude + 5 * (math.log10(distance_parsecs) - 1)
    return apparent_magnitude

def load_custom_star_data(json_file_path):
    print ("loading data from file")
    required_columns = ['hip', 'mag', 'ra_decdeg', 'dec_decdeg', 'plx', 'pmra', 'pmdec', 'dist', 'absmag', 'kR', 'kG','kB','x','y','z']
    df = pd.read_json(json_file_path)
    df = df[required_columns]
    pd.set_option('display.max_columns', None)  # Adjust as per your DataFrame's column count
    pd.set_option('display.width', None)  # Use None for automatically adjusting to the screen
   
    # These column renames seem to be important for later. Why?
    df.columns = (
        'hip', 'magnitude', 'ra_degrees', 'dec_degrees',
        'parallax_mas', 'ra_mas_per_year', 'dec_mas_per_year',
        'distance_parsecs','absolutem', 'kR', 'kG','kB','3dx','3dy','3dz'
    )

    # Remove samples with missing data to elimiate checks later
    df = df.replace('', np.nan)

    #print(df.shape[1]," ",df.iloc[0, 0]," ",df.iloc[0, 1]," ",df.iloc[0, 2]," ",df.iloc[0, 3]," ",df.iloc[0, 4]," ",df.iloc[0, 7]," ",df.iloc[0, 5]," ",df.iloc[0, 6]," ",df.iloc[0, 7]," ",df.iloc[0, 8]," ",df.iloc[0, 9]," ",df.iloc[0, 10]," ",df.iloc[0, 11]," ",df.iloc[0, 12]," ",df.iloc[0, 13]," ",df.iloc[0, 14])

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


### FIXED ISSUE WHERE THE STEREOGRAPHIC X AND Y COORDINATES FROM THIS FUNCTION WAS NOT SAME AS THE EXISTING ONE###
### THE CURRENT_TIME AND WHEN VARIABLES WERE DISPLAYING A DIFFERENT TIME###
### THIS SCRIPT DIDNT FOLLOW THE UPDATED METHOD TO CALL AND INITIATE THE TIMESCALE OBJECT###
def collect_celestial_data(df, eph, constellations, lat, long, timescale, when = '2024-03-11 00:00'):
    observer_location = wgs84.latlon(lat, long)
    t = timescale.utc(datetime.strptime(when, '%Y-%m-%d %H:%M').replace(tzinfo=timezone("Europe/Dublin")))
    observer = observer_location.at(t)
    # lat, long = 53.34, -6.26


    # #lat, long = 90.0, 135.0
    # dt = datetime.strptime(when, '%Y-%m-%d %H:%M')
    # timezone_str = "Europe/Dublin"
    # local_tz = timezone(timezone_str)
    # dt = local_tz.localize(dt)
    # utc_dt = dt.astimezone(utc)
    # t = load.timescale().from_datetime(utc_dt)
    # observer = wgs84.latlon(lat, long).at(t)

    edges = [edge for _, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, _ in edges]
    edges_star2 = [star2 for _, star2 in edges]

    center_object = Star(ra=observer.radec()[0], dec=observer.radec()[1])
    print ("Center OBJECT ",center_object)
    center = eph['earth'].at(t).observe(center_object)
    projection = build_stereographic_projection(center)



    star_matrix = df.astype(float).to_numpy()
    print("matrics 1",star_matrix[0])
    stars_array = np.array([Star(ra_hours=row[1]/15.0, dec_degrees=row[2]) for row in star_matrix], dtype=object)
  
    i=0
    for myloop in stars_array:
        apparent_position = eph['earth'].at(t).observe(stars_array[0])
 #       ra, dec, dist = apparent_position.radec()    
 #       apparent_position1 = eph['earth'].at(t).observe(stars_array[myloop])
        myx, myy = projection(apparent_position)
  #      myx1, myy1 = projection(apparent_position1)

        i+=1
        if i < 3:
            print ("myloop = ", myloop)
            print ("My Values = ",myx, myy)
            print (stars_array[0])
    # Need documentation on what format the dataframe needs to have to for this API call
  
    star_positions = eph['earth'].at(t).observe(Star.from_dataframe(df))


# Iterate over the array of Star objects
 #   for star in stars_array:
    # Compute the observed position of each star from Earth at time t
 #       observed_position = eph['earth'].at(t).observe(star)
 #       observed_positions.append(observed_position)
 #   observed_positions_array = np.array(observed_positions)

    test = Star.from_dataframe(df)
    print(df.iloc[0,[1,2]])
    print ("Star positions ",test)


    df['x'], df['y'] = projection(star_positions)
    #df['x'] = -df['x']
    df['y'] = -df['y']   
    print("New X = ",df.iloc[0,[16,17]])
 

    # for column in df.columns:
    #     print(column)

    return df, edges_star1, edges_star2


def main():
    timescale = global_timescale
    lat, long = 53.34, -6.26
    # Load data and collect celestial data
    df, eph, constellations = load_custom_star_data('../datasets/star_database_colors.json')
    print(df.shape[1]," ",df.iloc[0, 0]," ",df.iloc[0, 1]," ",df.iloc[0, 2]," ",df.iloc[0, 3]," ",df.iloc[0, 4]," ",df.iloc[0, 7]," ",df.iloc[0, 5]," ",df.iloc[0, 6]," ",df.iloc[0, 7]," ",df.iloc[0, 8]," ",df.iloc[0, 9]," ",df.iloc[0, 10]," ",df.iloc[0, 11]," ",df.iloc[0, 12]," ",df.iloc[0, 13]," ",df.iloc[0, 14]," ",df.iloc[0, 15])
    df, edges_star1, edges_star2 = collect_celestial_data(df, eph, constellations, lat, long, timescale)
    print(df.shape[1]," ",df.iloc[0, 0]," ",df.iloc[0, 1]," ",df.iloc[0, 2]," ",df.iloc[0, 3]," ",df.iloc[0, 4]," ",df.iloc[0, 7]," ",df.iloc[0, 5]," ",df.iloc[0, 6]," ",df.iloc[0, 7]," ",df.iloc[0, 8]," ",df.iloc[0, 9]," ",df.iloc[0, 10]," ",df.iloc[0, 11]," ",df.iloc[0, 12]," ",df.iloc[0, 13]," ",df.iloc[0, 14]," ",df.iloc[0, 15]," ",df.iloc[0, 16]," ",df.iloc[0, 17])
    current_time = datetime.strptime("2024-03-11 00:00", '%Y-%m-%d %H:%M')

    df, edges_star1, edges_star2 = collect_celestial_data(df, eph, constellations, lat, long, timescale, current_time.strftime('%Y-%m-%d %H:%M'))
    print(df.shape[1]," ",df.iloc[0, 0]," ",df.iloc[0, 1]," ",df.iloc[0, 2]," ",df.iloc[0, 3]," ",df.iloc[0, 4]," ",df.iloc[0, 7]," ",df.iloc[0, 5]," ",df.iloc[0, 6]," ",df.iloc[0, 7]," ",df.iloc[0, 8]," ",df.iloc[0, 9]," ",df.iloc[0, 10]," ",df.iloc[0, 11]," ",df.iloc[0, 12]," ",df.iloc[0, 13]," ",df.iloc[0, 14]," ",df.iloc[0, 15]," ",df.iloc[0, 16]," ",df.iloc[0, 17])
    df, edges_star1, edges_star2 = collect_celestial_data(df, eph, constellations, lat, long, timescale, current_time.strftime('%Y-%m-%d %H:%M'))
    print(df.shape[1]," ",df.iloc[0, 0]," ",df.iloc[0, 1]," ",df.iloc[0, 2]," ",df.iloc[0, 3]," ",df.iloc[0, 4]," ",df.iloc[0, 7]," ",df.iloc[0, 5]," ",df.iloc[0, 6]," ",df.iloc[0, 7]," ",df.iloc[0, 8]," ",df.iloc[0, 9]," ",df.iloc[0, 10]," ",df.iloc[0, 11]," ",df.iloc[0, 12]," ",df.iloc[0, 13]," ",df.iloc[0, 14]," ",df.iloc[0, 15]," ",df.iloc[0, 16]," ",df.iloc[0, 17])
    df_filtered = df[df['magnitude'] <= 10]
    column_names = df_filtered.columns.tolist()
    header_string = ','.join(column_names)
    star_matrix = df_filtered.astype(float).to_numpy()
#    nstars = star_matrix.shape[0]
    index=0

    for star in star_matrix:
        print (star[SIndex.X],star[SIndex.Y],  )
        print(f"X= {star[SIndex.X]} Y= {star[SIndex.Y]} x= {star[SIndex.Dx]} y= {star[SIndex.Dy]} z= {star[SIndex.Dz]}")
        print("convert ",convert_ra_dec(star[SIndex.RA_DEGREES],star[SIndex.DEC_DEGREES],star[SIndex.DISTANCE_PARSECS]))
        x, y, z = ra_dec_distance_to_cartesian(star[SIndex.RA_DEGREES],star[SIndex.DEC_DEGREES],star[SIndex.DISTANCE_PARSECS])
        print(f"Cartesian coordinates with distance: x={x}, y={y}, z={z}")
        print ("Back to decimal",cartesian_to_ra_dec(x, y, z))
        mag = star[SIndex.MAGNITUDE]
        absmag = star[SIndex.ABS_MAG]  
        distance = star[SIndex.DISTANCE_PARSECS]  
        print (star[SIndex.DISTANCE_PARSECS])
        print (distance_3d(0,0,0,star[SIndex.Dx],star[SIndex.Dy],star[SIndex.Dz]))

        print("Moveworkd",moveWorld (star[SIndex.Dx],star[SIndex.Dy],star[SIndex.Dz],star[SIndex.DISTANCE_PARSECS],(1,1,1)))

        #np.savetxt('../datasets/star_matrix_3D.csv', star_matrix, delimiter=',', fmt='%s', header=header_string, comments='')
        exit()
            
            # Using this code we can move in space and have the apparent magnitude recalculated
    calc_mag = calculate_apparent_magnitude(star[SIndex.ABS_MAG],star[SIndex.DISTANCE_PARSECS])
#             color = (int(star[SIndex.COLOR_K_R] * 255), int(star[SIndex.COLOR_K_G] * 255), int(star[SIndex.COLOR_K_B] * 255))

if __name__ == "__main__":
    main()
 