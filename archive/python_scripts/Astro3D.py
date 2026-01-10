import math
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np


def estimate_star_diameter(absmag, spect, ci):
    # This function estimates the diameter of a star based on its absolute magnitude, spectral type, and color index.
    if absmag is None or spect is None:
        return None

    luminosity_factor = 10 ** ((4.83 - absmag) / 2.5)
    color_factor = 1 + ci if ci else 1
    spectral_factor = 1.5 if "M" in spect else 1.0

    diameter = (luminosity_factor ** 0.5) * color_factor * spectral_factor
    return diameter

def ra_dec_to_cartesian(ra, dec, distance, system="celestial", ra_in_hours=True):
    """
    Convert RA/Dec to 3D Cartesian coordinates based on the specified system.
    Parameters:
        ra (float): Right Ascension in hours or degrees
        dec (float): Declination in degrees
        distance (float): Distance in parsecs
        system (str): Coordinate system ('celestial', 'galactic', 'galactocentric')
        ra_in_hours (bool): If True, RA is assumed to be in hours; if False, RA is assumed to be in degrees
    Returns:
        tuple: (x, y, z) Cartesian coordinates
    """
    if ra_in_hours:
        ra *= 15  # Convert hours to degrees
    
    ra_rad = math.radians(ra)
    dec_rad = math.radians(dec)
    
    if system == "celestial":
        x = distance * math.cos(dec_rad) * math.cos(ra_rad)
        y = distance * math.cos(dec_rad) * math.sin(ra_rad)
        z = distance * math.sin(dec_rad)
        
    elif system in ["galactic", "galactocentric"]:
        coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, distance=distance * u.pc, frame='icrs')
        glon = coord.galactic.l.deg
        glat = coord.galactic.b.deg
        print ('Galactic = ', glon, glat)

        l_rad = math.radians(glon)
        b_rad = math.radians(glat)
        x = distance * math.cos(b_rad) * math.cos(l_rad)
        y = distance * math.cos(b_rad) * math.sin(l_rad)
        z = distance * math.sin(b_rad)
        
        if system == "galactocentric":
            x -= 8000  # Shift origin to galactic center
            
    else:
        raise ValueError("Invalid system specified. Use 'celestial', 'galactic', or 'galactocentric'.")
        
    return x, y, z

def cartesian_to_ra_dec(x, y, z, system="celestial"):
    """
    Convert 3D Cartesian coordinates to RA/Dec in degrees based on the specified system.
    Parameters:
        x, y, z (float): Cartesian coordinates
        system (str): Coordinate system ('celestial', 'galactic', 'galactocentric')
    Returns:
        tuple: (ra, dec) in degrees
    """
    distance = math.sqrt(x**2 + y**2 + z**2)
    if distance == 0:
        print("Warning: Distance is zero, cannot convert to RA/Dec.")
        return None, None

    if system == "celestial":
        dec = math.degrees(math.asin(z / distance))
        ra = math.degrees(math.atan2(y, x))
        if ra < 0:
            ra += 360

    elif system in ["galactic", "galactocentric"]:
        if system == "galactocentric":
            x += 8000  # Shift for galactocentric origin

        distance = math.sqrt(x**2 + y**2 + z**2)
        if distance == 0:
            print("Warning: Distance is zero after galactocentric shift, cannot convert to RA/Dec.")
            return None, None

        glat = math.degrees(math.asin(z / distance))
        glon = math.degrees(math.atan2(y, x))
        if glon < 0:
            glon += 360

        coord = SkyCoord(l=glon * u.deg, b=glat * u.deg, distance=distance * u.pc, frame='galactic')
        ra = coord.icrs.ra.deg
        dec = coord.icrs.dec.deg
        
    else:
        raise ValueError("Invalid system specified. Use 'celestial', 'galactic', or 'galactocentric'.")
        
    return ra, dec

def galactic_to_celestial(l, b):
    """
    Converts galactic coordinates (l, b) in degrees to celestial coordinates (RA, Dec) in degrees.
    :param l: Galactic longitude in degrees
    :param b: Galactic latitude in degrees
    :return: RA and Dec in degrees
    """
    # Convert l and b from degrees to radians
    l_rad = np.radians(l)
    b_rad = np.radians(b)

    # Define the inverse rotation matrix for galactic to celestial
    inverse_rotation_matrix = np.array([
        [-0.054876, +0.494109, -0.867666],
        [-0.873437, -0.444830, -0.198076],
        [-0.483835, +0.746982, +0.455984]
    ])

    # Convert l and b to a 3D Cartesian vector
    x = np.cos(l_rad) * np.cos(b_rad)
    y = np.sin(l_rad) * np.cos(b_rad)
    z = np.sin(b_rad)
    galactic_vector = np.array([x, y, z])

    # Apply the inverse rotation matrix
    celestial_vector = inverse_rotation_matrix @ galactic_vector

    # Calculate RA and Dec from the resulting Cartesian coordinates
    dec_rad = np.arcsin(celestial_vector[2])  # Declination in radians
    ra_rad = np.arctan2(celestial_vector[1], celestial_vector[0])  # Right Ascension in radians

    # Convert from radians to degrees and adjust RA to the range [0, 360)
    ra_deg = np.degrees(ra_rad) % 360
    dec_deg = np.degrees(dec_rad)

    return ra_deg, dec_deg


def celestial_to_galactic(ra_deg, dec_deg):
    """
    Converts celestial coordinates (RA, Dec) in degrees to galactic coordinates (l, b) in degrees.
    :param ra_deg: Right Ascension in degrees
    :param dec_deg: Declination in degrees
    :return: Galactic longitude (l) and latitude (b) in degrees
    """

    # Convert RA and Dec to radians
    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)

    # Define the rotation matrix for transformation
    rotation_matrix = np.array([
        [-0.054876, -0.873437, -0.483835],
        [+0.494109, -0.444830, +0.746982],
        [-0.867666, -0.198076, +0.455984]
    ])

    # Convert RA and Dec to a 3D Cartesian vector
    x = np.cos(ra_rad) * np.cos(dec_rad)
    y = np.sin(ra_rad) * np.cos(dec_rad)
    z = np.sin(dec_rad)
    celestial_vector = np.array([x, y, z])

    # Apply the rotation matrix
    galactic_vector = rotation_matrix @ celestial_vector

    # Calculate galactic latitude (b) and longitude (l)
    b_rad = np.arcsin(galactic_vector[2])  # Galactic latitude in radians
    l_rad = np.arctan2(galactic_vector[1], galactic_vector[0])  # Galactic longitude in radians

    # Convert from radians to degrees and adjust longitude to the range [0, 360)
    l_deg = np.degrees(l_rad) % 360
    b_deg = np.degrees(b_rad)

    return l_deg, b_deg


def convert_coordinates(x, y, z, from_system="celestial", to_system="galactic", distance=None):
    """
    Convert 3D coordinates directly between celestial, galactic, and galactocentric systems.
    Parameters:
        x, y, z (float): 3D Cartesian coordinates
        from_system (str): Source coordinate system
        to_system (str): Target coordinate system
        distance (float): Original distance in parsecs (used to avoid recalculating during conversion)
    Returns:
        tuple: Converted (x, y, z) coordinates in the target system
    """
    # Exit if conversion is within the same system
    if from_system == to_system:
        print("No conversion needed; both systems are the same.")
        return x, y, z

    # Step 1: Convert from Cartesian to RA/Dec
    ra, dec = cartesian_to_ra_dec(x, y, z, system=from_system)
    if ra is None or dec is None:
        print(f"Conversion failed from {from_system} to {to_system}")
        return None, None, None

    # Step 3: Convert to Cartesian coordinates in the target system using the original distance
    x_new, y_new, z_new = ra_dec_to_cartesian(ra, dec, distance, system=to_system, ra_in_hours=False)

    return x_new, y_new, z_new
