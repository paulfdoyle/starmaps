import json
from astroquery.simbad import Simbad

# Assuming the fetch_star_details function is provided as follows:
def fetch_star_details(hip_id: int):
    # Create a custom Simbad query object
    custom_simbad = Simbad()
    # Add the required fields
    custom_simbad.add_votable_fields('ids', 'flux(V)')

    # Query the SIMBAD database for the given HIP ID
    result = custom_simbad.query_object(f"HIP {hip_id}")

    if result is None:
        print(f"No results found for HIP ID {hip_id}")
        return None

    # Extract the details
    main_id = result['MAIN_ID'][0] if not result['MAIN_ID'].mask[0] else "N/A"
    return main_id

# Load the JSON data from the file
input_file_path = '../datasets/updated_star_database_bsc5p.json'
output_file_path = '../datasets/updated_star_database_bsc5p_output.json'

with open(input_file_path, 'r') as file:
    stars_data = json.load(file)

# Track the stars where the "proper" field was not updated
not_updated = []

# Iterate over each star entry in the JSON data
for star in stars_data:
    if star['proper'] == "":
        hip_value = star.get('hip', "")
        
        # Check if hip_value is a valid number (float or int) and convert it to an integer
        if isinstance(hip_value, (int, float)):
            hip_id = int(hip_value)
            proper_name = fetch_star_details(hip_id)
            
            if proper_name and proper_name != "N/A":
                star['proper'] = proper_name
                print (hip_value,",",proper_name)
            else:
                not_updated.append(star)
        else:
            not_updated.append(star)
    else:
        not_updated.append(star)

# Output the updated JSON data to a new file
with open(output_file_path, 'w') as file:
    json.dump(stars_data, file, indent=4)

# Print the stars where the "proper" field was not updated
print("Stars where the 'proper' field was not updated:")
for star in not_updated:
    print(f"HIP ID: {star['hip']}, Proper Name: {star['proper']}")
