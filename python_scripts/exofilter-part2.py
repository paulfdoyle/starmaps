import csv
import json

def parse_and_merge_json(csv_file_path, exo_output_file_path, star_json_file_path, merged_output_file_path):
    """
    Parses a CSV file to JSON and merges it with a second JSON file based on HD values.
    Outputs the merged JSON data to a new file, sorting exoplanets alphabetically by `pl_letter`.
    Also adds a `sy_pnum` field to the merged JSON, set to `0` if there are no exoplanets.

    Parameters:
        csv_file_path (str): Path to the input CSV file.
        exo_output_file_path (str): Path to the intermediate exoplanet JSON file.
        star_json_file_path (str): Path to the input star JSON file.
        merged_output_file_path (str): Path to the output merged JSON file.
    """
    exoplanet_data = {}
    seen_planets = set()

    try:
        # Step 1: Parse the CSV and create exoplanet data indexed by HD value
        with open(csv_file_path, 'r') as csvfile:
            while True:
                line = csvfile.readline()
                if not line.startswith('#'):
                    break

            csvfile.seek(csvfile.tell() - len(line))
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                planet_name = row['pl_name']
                if planet_name in seen_planets:
                    continue
                seen_planets.add(planet_name)
                
                # Remove "HD" from hd_name and convert to an integer
                hd_name = row['hd_name'].replace('HD', '').strip()
                hip_name = row['hip_name'].replace('HIP', '').strip()

                # Ensure HD name is treated as an integer
                try:
                    hd_int = int(hd_name)
                except ValueError:
                    continue

                if hd_int not in exoplanet_data:
                    exoplanet_data[hd_int] = []

                exoplanet_data[hd_int].append({
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
                    'st_refname': row['st_refname'],
                    'st_spectype': row['st_spectype'],
                    'st_teff': row['st_teff'],
                    'st_rad': row['st_rad'],
                    'st_mass': row['st_mass'],
                    'st_logg': row['st_logg'],
                    'sy_refname': row['sy_refname'],
                    'glat': row['glat'],
                    'glon': row['glon'],
                    'sy_dist': row['sy_dist'],
                    'sy_vmag': row['sy_vmag'],
                    'sy_gaiamag': row['sy_gaiamag']
                })

        # Step 2: Save the intermediate exoplanet data
        with open(exo_output_file_path, 'w') as exo_json_file:
            json.dump(exoplanet_data, exo_json_file, indent=4)
        print(f"Exoplanet data successfully parsed and saved to {exo_output_file_path}")

        # Step 3: Merge with the second JSON file
        with open(star_json_file_path, 'r') as star_json_file:
            star_data = json.load(star_json_file)

        star_hd_values = []

        for star in star_data:
            hd_value = star.get('hd')
            if isinstance(hd_value, (int, float)) and hd_value:
                hd_value_int = int(hd_value)
                star_hd_values.append(hd_value_int)
                print(f"Comparing star HD {hd_value_int} with exoplanet HD values...")

                for exo_hd in exoplanet_data.keys():
                    print(f"  Exoplanet HD: {exo_hd} vs Star HD: {hd_value_int}")

                if hd_value_int in exoplanet_data:
                    # Sort exoplanets by `pl_letter`
                    sorted_exoplanets = sorted(exoplanet_data[hd_value_int], key=lambda x: x['pl_letter'])
                    # Add `sy_pnum` field and place it before `exo_planets`
                    star['sy_pnum'] = sorted_exoplanets[0]['sy_pnum'] if sorted_exoplanets else 0
                    star['exo_planets'] = sorted_exoplanets
                    print(f"Exoplanet found for HD {hd_value_int}")
                else:
                    print(f"No exoplanet found for HD {hd_value_int}")
                    star['sy_pnum'] = 0
                    star['exo_planets'] = []
            else:
                star['sy_pnum'] = 0
                star['exo_planets'] = []

        # Print out all HD values for exoplanet data
        print("\nAll HD values in exoplanet data:")
        for exo_hd in exoplanet_data.keys():
            print(exo_hd)

        # Print out all HD values in star data
        print("\nAll HD values in star data:")
        for hd_value in star_hd_values:
            print(hd_value)

        # Step 4: Save the merged data to a new JSON file
        with open(merged_output_file_path, 'w') as merged_json_file:
            json.dump(star_data, merged_json_file, indent=4)
        print(f"Merged data successfully saved to {merged_output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
if __name__ == "__main__":
    csv_file = '../datasets/exoplanets.csv'                   # Path to your input CSV file
    exo_output_file = '../datasets/exoplanets_by_hd.json'     # Path to your intermediate exoplanet JSON file
    star_json_file = '../datasets/updated_star_database_bsc5p_names.json'  # Path to your input star JSON file
    merged_output_file = '../datasets/merged_star_exo_data.json'  # Path to your output merged JSON file
    
    parse_and_merge_json(csv_file, exo_output_file, star_json_file, merged_output_file)

