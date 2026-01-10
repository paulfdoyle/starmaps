import json

# Mapping of spectral types to index numbers
spectral_type_indices = {
    'O': 0,
    'B': 1,
    'A': 2,
    'F': 3,
    'G': 4,
    'K': 5,
    'M': 6,
}

def get_spectral_type_index(sptype):
    """Get the index for the spectral type."""
    if sptype:
        # Extract the first character from the spectral type string
        spectral_type_letter = sptype[0].upper()
        return spectral_type_indices.get(spectral_type_letter, -1)  # Return -1 if not found
    return -1  # Return -1 if sptype is None or empty

def process_json_file(input_file, output_file):
    # Read the JSON data from the input file
    with open(input_file, 'r') as file:
        data = json.load(file)
    
    # Check if data is a list
    if isinstance(data, list):
        # Iterate over each item in the list
        for entry in data:
            # Assuming 'proper' key might contain the spectral type (or replace with correct key)
            spectral_type = entry.get('proper', '')
            
            # Calculate the index number based on the spectral type
            entry['C'] = get_spectral_type_index(spectral_type)
    else:
        # Handle case if the data is a single dictionary
        spectral_type = data.get('proper', '')
        data['C'] = get_spectral_type_index(spectral_type)
    
    # Write the modified data to the output file
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

# File paths
input_file = '../datasets/star_database_colors.json'  # Input JSON file path
output_file = '../datasets/star_database_updates.json'  # Output JSON file path

process_json_file(input_file, output_file)
