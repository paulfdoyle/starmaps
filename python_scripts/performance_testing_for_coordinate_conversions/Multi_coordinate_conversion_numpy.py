import numpy as np
import math

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
    x = d * np.math.cos(b_rad) * np.math.cos(l_rad)
    y = d * np.math.cos(b_rad) * np.math.sin(l_rad)
    z = d * np.math.sin(b_rad)

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

    return l, b, d

def galactic_to_equatorial(l, b):
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

def equatorial_to_cartesian(ra_deg, dec_deg, d):

    ra_rad = np.radians(ra_deg)
    dec_rad = np.radians(dec_deg)
    x = d * math.cos(dec_rad) * math.cos(ra_rad)
    y = d * math.cos(dec_rad) * math.sin(ra_rad)
    z = d * math.sin(dec_rad)
    return x, y, z

# Betelgeuse's approximate galactic coordinates
l_Betelgeuse = 199.79
b_Betelgeuse = -8.96

# Example usage:
l = 199.79
b = -8.96
d = 152.6718


print (f"Original Galactic Coordinates for Betelgeuse: GLON: {l}, GLAT: {b}")
# Galactic to Cartesian
x, y, z = galactic_to_cartesian(l, b, d)

print(f"Cartesian coordinates: x={x}, y={y}, z={z}")

# Cartesian back to Galactic
l_back, b_back, d_back = cartesian_to_galactic(x, y, z)
print(f"Back to Galactic coordinates: l={l_back}, b={b_back}, d={d_back}")

# Galactic to RA/Dec
ra, dec = galactic_to_equatorial(l, b)
print(f"Equatorial coordinates(RA/Dec) from Galactic: RA={ra}, Dec={dec}")

print(f"Recovered Galactic Coordiantes from Equatorial Coordinates: GLON: 199.79, GLAT: -8.96")

# x_eq, y_eq, z_eq = equatorial_to_cartesian (ra, dec, d)
# print(f"Cartesian coordinates from galactic -> radec: x={x_eq}, y={y_eq}, z={z_eq}")

