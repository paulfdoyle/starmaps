import csv
import json

def parse_csv_to_json(csv_file_path, output_file_path):
    """
    Parses a CSV file and outputs a JSON file indexed by the HD value.
    Only includes the first record found for each planet.
    Modifies the hip_name field to contain only the number.

    Parameters:
        csv_file_path (str): Path to the input CSV file.
        output_file_path (str): Path to the output JSON file.
    """
    data = {}
    seen_planets = set()  # To track planets that have already been added

    try:
        # Open the CSV file
        with open(csv_file_path, 'r') as csvfile:
            # Skip the commented lines at the beginning
            while True:
                line = csvfile.readline()
                if not line.startswith('#'):
                    break

            # Go back one line (to include the header) and parse the CSV
            csvfile.seek(csvfile.tell() - len(line))
            reader = csv.DictReader(csvfile)
            
            # Iterate through each row in the CSV
            for row in reader:
                planet_name = row['pl_name']
                
                # Skip if this planet has already been processed
                if planet_name in seen_planets:
                    continue
                
                # Mark this planet as processed
                seen_planets.add(planet_name)
                
                hd_name = row['hd_name']
                if hd_name not in data:
                    data[hd_name] = []

                # Modify the hip_name to only include the number
                hip_name = row['hip_name'].replace('HIP', '').strip()
                
                # Add the row data to the list of entries under this HD name
                data[hd_name].append({
                    'pl_name': row['pl_name'],
                    'hostname': row['hostname'],
                    'pl_letter': row['pl_letter'],
                    'hip_name': hip_name,
                    'default_flag': row['default_flag'],
                    'sy_snum': row['sy_snum'],
                    'sy_pnum': row['sy_pnum'],
                    'sy_mnum': row['sy_mnum'],
                    'disc_year': row['disc_year'],
                    'pl_controv_flag': row['pl_controv_flag'],
                    'pl_orbper': row['pl_orbper'],
                    'pl_orbsmax': row['pl_orbsmax'],
                    'pl_rade': row['pl_rade'],
                    'pl_radj': row['pl_radj'],
                    'pl_masse': row['pl_masse'],
                    'pl_massj': row['pl_massj'],
                    'pl_bmasse': row['pl_bmasse'],
                    'pl_bmassj': row['pl_bmassj'],
                    'pl_bmassprov': row['pl_bmassprov'],
                    'pl_orbeccen': row['pl_orbeccen'],
                    'pl_insol': row['pl_insol'],
                    'pl_eqt': row['pl_eqt'],
                    'st_spectype': row['st_spectype'],
                    'st_teff': row['st_teff'],
                    'st_rad': row['st_rad'],
                    'st_mass': row['st_mass'],
                    'st_logg': row['st_logg'],
                    'glat': row['glat'],
                    'glon': row['glon'],
                    'sy_dist': row['sy_dist'],
                    'sy_vmag': row['sy_vmag'],
                    'sy_gaiamag': row['sy_gaiamag']
                })

        # Write the parsed data to a JSON file
        with open(output_file_path, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)

        print(f"Data successfully parsed and saved to {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    csv_file = '../datasets/exoplanets.csv'    # Path to your input CSV file
    output_file = '../datasets/exoplanets_by_hd.json'  # Path to your output JSON file
    
    parse_csv_to_json(csv_file, output_file)
