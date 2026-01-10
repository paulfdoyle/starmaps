import json
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u

def safe_float_convert(value, default=np.nan):
    """Converts value to float, returns default if conversion fails."""
    try:
        return float(value)
    except ValueError:
        return default

# Galactic to Equatorial
def galactic_to_equatorial_numpy(l, b):
    l = safe_float_convert(l)
    b = safe_float_convert(b)
    if np.isnan(l) or np.isnan(b):
        return None  
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
    cos_DEC = np.cos(DEC)
    sin_l_minus_L = np.sin(l_rad - np.radians(L_NCP))
    cos_l_minus_L = np.cos(l_rad - np.radians(L_NCP))
    y = sin_l_minus_L * cos_b
    x = cos_b * sin_DEC_NGP * cos_l_minus_L - sin_b * cos_DEC_NGP
    RA = RA_NGP_rad + np.arctan2(y, x)  # in radians
    
    # Convert radians to degrees
    RA_deg = (np.degrees(RA) -180 ) % 360
    DEC_deg = np.degrees(DEC)
    
    return RA_deg, DEC_deg

# Galactic to Equatorial using Astropy
def galactic_to_equatorial_astropy(l, b):
    l = safe_float_convert(l)
    b = safe_float_convert(b)
    if np.isnan(l) or np.isnan(b):
        return None
    coord = SkyCoord(l=l*u.degree, b=b*u.degree, frame='galactic')
    equatorial = coord.icrs
    return equatorial.ra.degree, equatorial.dec.degree

# Function to convert RA and Dec to degrees
def ra_dec_to_degrees(rahrs, ramin, rasec, decsign, decdeg, decmin, decsec):
    try:
        ra_degrees = (safe_float_convert(rahrs) + safe_float_convert(ramin) / 60 + safe_float_convert(rasec) / 3600) * 15
        dec_degrees = safe_float_convert(decdeg) + safe_float_convert(decmin) / 60 + safe_float_convert(decsec) / 3600
        if decsign == "-":
            dec_degrees = -dec_degrees
        return ra_degrees, dec_degrees
    except TypeError:
        return None  # or (np.nan, np.nan)
    
# Load data from JSON file
with open('../../datasets/star_database_colors.json', 'r') as file:
    stars_data = json.load(file)

results = []
for star in stars_data:
    if any(not star.get(k) for k in ['GLON', 'GLAT', 'rahrs', 'ramin', 'rasec', 'dec-', 'decdeg', 'decmin', 'decsec']):
        continue

    ra_dec_numpy = galactic_to_equatorial_numpy(star['GLON'], star['GLAT'])
    ra_dec_astropy = galactic_to_equatorial_astropy(star['GLON'], star['GLAT'])
    ra_dec_direct = ra_dec_to_degrees(star['rahrs'], star['ramin'], star['rasec'], star['dec-'], star['decdeg'], star['decmin'], star['decsec'])

    if ra_dec_numpy and ra_dec_astropy and ra_dec_direct:
        ra_numpy, dec_numpy = ra_dec_numpy
        ra_astropy, dec_astropy = ra_dec_astropy
        ra_direct, dec_direct = ra_dec_direct

        # Calculate percentage differences
        ra_percent_diff_numpy_astropy = abs(ra_numpy - ra_astropy) / ((ra_numpy + ra_astropy) / 2) * 100
        dec_percent_diff_numpy_astropy = abs(dec_numpy - dec_astropy) / ((dec_numpy + dec_astropy) / 2) * 100
        ra_percent_diff_numpy_direct = abs(ra_numpy - ra_direct) / ((ra_numpy + ra_direct) / 2) * 100
        dec_percent_diff_numpy_direct = abs(dec_numpy - dec_direct) / ((dec_numpy + dec_direct) / 2) * 100

        results.append([star['hip'], ra_numpy, dec_numpy, ra_astropy, dec_astropy, ra_direct, dec_direct, ra_percent_diff_numpy_astropy, dec_percent_diff_numpy_astropy, ra_percent_diff_numpy_direct, dec_percent_diff_numpy_direct])

# Create DataFrame with the results
df = pd.DataFrame(results, columns=['HIP', 'RA_Numpy', 'DEC_Numpy', 'RA_Astropy', 'DEC_Astropy', 'RA_Direct', 'DEC_Direct', 'RA_Percent_Diff_Numpy_Astropy', 'DEC_Percent_Diff_Numpy_Astropy', 'RA_Percent_Diff_Numpy_Direct', 'DEC_Percent_Diff_Numpy_Direct'])

# Round the DataFrame to 4 decimal places for all numeric columns
df = df.round(4)

# Write to CSV
df.to_csv('../../datasets/proof_of_conversion_numpy.csv', index=False)