import json
from astroquery.simbad import Simbad

def get_exoplanet_details(hip_id):
    # Create a custom Simbad query object
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('ids', 'plx', 'otypes')
    
    # Query the SIMBAD database for the given HIP ID
    result = custom_simbad.query_object(f"HIP {hip_id}")
    
    if result is None:
        return None
    
    # Check if the star has any exoplanet-related identifiers
    star_types = result['OTYPES'][0]
    if 'Exoplanet' in star_types:
        star_ids = result['IDS'][0]
        return star_ids
    else:
        return None

# Load the JSON data from the file
input_file_path = '../datasets/updated_star_database_bsc5p.json'

with open(input_file_path, 'r') as file:
    stars_data = json.load(file)

# Iterate over each star entry in the JSON data
for star in stars_data:
    hip_value = star.get('hip', "")
    
    # Check if hip_value is a valid number (float or int)
    if isinstance(hip_value, (int, float)):
        hip_id = int(hip_value)
        exoplanet_details = get_exoplanet_details(hip_id)
        
        if exoplanet_details:
            print(f"Exoplanets or related identifiers found for HIP {hip_id}: {exoplanet_details}")

