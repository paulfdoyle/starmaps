import pandas as pd
import json

def convert_color_and_save(input_file, output_file):
    # Load the data
    df = pd.read_json(input_file)

    # Ensure all missing or empty 'K' values are replaced with a representation of white
    df['K'].replace('', "{'r': 1, 'g': 1, 'b': 1}", inplace=True)
    df['K'].fillna("{'r': 1, 'g': 1, 'b': 1}", inplace=True)

    # Function to parse the color string into RGB components
    def parse_color(color_str):
        try:
            # Convert string representation of dictionary to actual dictionary
            color_dict = json.loads(color_str.replace("'", "\""))
            return pd.Series([color_dict.get('r', 1), color_dict.get('g', 1), color_dict.get('b', 1)])
        except json.JSONDecodeError:
            # Default to white in case of any error
            return pd.Series([1, 1, 1])

    # Apply the function and create new columns
    df[['kR', 'kG', 'kB']] = df['K'].apply(parse_color)
    df.drop('K', axis=1, inplace=True)

    # Save the modified DataFrame to a new JSON file
    df.to_json(output_file, orient='records', indent=4)

# Specify the input and output file paths
input_file_path = '../datasets/star_database.json'
output_file_path = '../datasets/star_database_colors.json'

# Call the function with the specified file paths
convert_color_and_save(input_file_path, output_file_path)

print("Conversion complete. The output file is saved as:", output_file_path)
