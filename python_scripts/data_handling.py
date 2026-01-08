import pandas as pd
import numpy as np
from skyfield.api import load
from skyfield.data import stellarium
from celestial_mechanics import galactic_to_equatorial_proper, galactic_to_cartesian, find_closest_star_index
from utils import SIndex

def load_custom_star_data(json_file_path):
    """
    Load and preprocess star data from a JSON file.

    Args:
    - json_file_path (str): Path to the JSON file containing star data.

    Returns:
    - tuple: (star_data_array, ephemeris, constellations)
    """
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

        # Add StarType as the last column
        star_types = [find_closest_star_index((row[SIndex.COLOR_K_R] * 255, row[SIndex.COLOR_K_G] * 255, row[SIndex.COLOR_K_B] * 255)) for row in star_data_array]
        star_data_array = np.column_stack((star_data_array, star_types))
        # if star_types <0:
        #     print (star_types)
        eph = load('de421.bsp')
        url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern_st/constellationship.fab')
        with load.open(url) as f:
            constellations = stellarium.parse_constellations(f)
        
        print (star_data_array[SIndex.STAR_TYPE])
        return star_data_array, eph, constellations
    except Exception as e:
        print(f"An error occurred while loading or processing the star data: {e}")
        return None, None, None

def extract_orion_star_pairs(fab_file_path):
    """
    Extract star pairs for the Orion constellation from the constellationship.fab file.

    Args:
    - fab_file_path (str): Path to the constellationship.fab file.

    Returns:
    - list: List of star pairs (tuples) for the Orion constellation.
    """
    try:
        orion_pairs = []
        with open(fab_file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('Ori'):  # Orion constellation lines start with 'Ori'
                    parts = line.split()
                    star_ids = parts[2:]  # Skip the first two parts (abbreviation and number of pairs)
                    for i in range(0, len(star_ids) - 1, 2):
                        star1, star2 = star_ids[i], star_ids[i + 1]
                        orion_pairs.append((star1, star2))
        return orion_pairs
    except Exception as e:
        print(f"An error occurred while extracting Orion star pairs: {e}")
        return []

# Exported functions and variables
__all__ = ['load_custom_star_data', 'extract_orion_star_pairs']
