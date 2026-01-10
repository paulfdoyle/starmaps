import json

# File paths
first_json_path = '../datasets/star_database_colors.json'
second_json_path = '../datasets/bsc5p_spectral_extra.json'
output_json_path = '../datasets/updated_star_database_bsc5p.json'

# Mapping for "C" values to indices
c_value_to_index = {
    "O": 0,
    "B": 1,
    "A": 2,
    "F": 3,
    "G": 4,
    "K": 5,
    "M": 6
}

# Load the first JSON file
with open(first_json_path, 'r') as file:
    first_json = json.load(file)

# Load the second JSON file
with open(second_json_path, 'r') as file:
    second_json = json.load(file)

# Assuming "hr" in first.json matches "i" in second.json
for first_item in first_json:
    hr_value = first_item['hr']
    
    # Find the corresponding entry in the second JSON
    corresponding_item = next((item for item in second_json if item['i'] == hr_value), None)
    
    if corresponding_item and 'C' in corresponding_item and corresponding_item['C'] is not None:
        # Replace "C" with its corresponding index
        c_value = corresponding_item['C']
        first_item['C'] = c_value_to_index.get(c_value, "None")
    else:
        first_item['C'] = "None"  # Insert "None" where the "C" value is missing

# Save the updated first JSON as a new file
with open(output_json_path, 'w') as file:
    json.dump(first_json, file, indent=4)

print(f"Updated JSON saved as '{output_json_path}'")
