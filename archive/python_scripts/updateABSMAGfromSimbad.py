import json
from astroquery.simbad import Simbad
import astropy.units as u
from astropy.coordinates import Distance
import numpy as np

def get_simbad_data_for_hd(hd_id):
    # Customize Simbad query to include relevant fields (parallax, distance, and absolute magnitude)
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('parallax', 'distance', 'flux(V)')  # flux(V) corresponds to the V-band magnitude
    
    # Query SIMBAD using the HD ID
    result_table = custom_simbad.query_object(f"HD {int(hd_id)}")

    if result_table is None or len(result_table) == 0:
        print(f"No data found in SIMBAD for HD ID {hd_id}.")
        return None, None

    # Calculate distance information
    if 'distance_result' in result_table.colnames and result_table['distance_result'][0] is not None:
        distance = result_table['distance_result'][0]  # Distance is already in parsecs
    elif 'PLX_VALUE' in result_table.colnames and result_table['PLX_VALUE'][0] is not None:
        parallax = result_table['PLX_VALUE'][0]
        distance = Distance(parallax=parallax * u.mas).parsec
    else:
        distance = None
        print(f"No distance or parallax data available for HD {hd_id}.")

    # Get absolute magnitude (based on V-band apparent magnitude and distance)
    if distance is not None and 'FLUX_V' in result_table.colnames and result_table['FLUX_V'][0] is not None:
        apparent_magnitude = result_table['FLUX_V'][0]
        absolute_magnitude = apparent_magnitude - 5 * np.log10(distance) + 5
    else:
        absolute_magnitude = None
        print(f"No apparent magnitude data available for HD {hd_id}, unable to calculate absolute magnitude.")
    
    return distance, absolute_magnitude

def update_json_with_simbad_data(input_json_file, output_json_file):
    with open(input_json_file, 'r') as file:
        data = json.load(file)

    for item in data:
        hd_id = item.get("hd")
        if hd_id:
            print(f"Processing HD {hd_id}...")
            old_distance = item.get("dist", None)
            old_absmag = item.get("absmag", None)

            if old_distance is not None:
                try:
                    old_distance = float(old_distance)
                except ValueError:
                    print(f"Invalid old distance for HD {hd_id}: {old_distance}. Skipping this entry.")
                    continue
            
            distance, absmag = get_simbad_data_for_hd(hd_id)
            
            if distance is not None:
                item["dist"] = distance
                if old_distance is not None:
                    difference = abs(distance - old_distance)
                    percentage_difference = (difference / old_distance) * 100
                    if percentage_difference >= 10:
                        print(f"Significant change detected for HD {hd_id}:")
                        print(f"  Old distance: {old_distance:.2f} parsecs")
                        print(f"  New distance: {distance:.2f} parsecs")
                        print(f"  Difference: {percentage_difference:.2f}%")
                print(f"Updated distance for HD {hd_id}: {distance:.2f} parsecs")
            else:
                print(f"Could not update distance for HD {hd_id}.")
            
            if absmag is not None:
                item["absmag"] = absmag
                if old_absmag is not None:
                    try:
                        old_absmag = float(old_absmag)
                        mag_difference = abs(absmag - old_absmag)
                        if mag_difference >= 0.1:  # Example threshold for significant change
                            print(f"Significant change detected in absolute magnitude for HD {hd_id}:")
                            print(f"  Old absolute magnitude: {old_absmag:.2f}")
                            print(f"  New absolute magnitude: {absmag:.2f}")
                            print(f"  Difference: {mag_difference:.2f}")
                    except ValueError:
                        print(f"Invalid old absolute magnitude for HD {hd_id}. Skipping comparison.")
                print(f"Updated absolute magnitude for HD {hd_id}: {absmag:.2f}")
            else:
                print(f"Could not update absolute magnitude for HD {hd_id}.")
        else:
            print("HD ID not found in item.")

    with open(output_json_file, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Updated data written to {output_json_file}")

if __name__ == "__main__":
    # Replace 'data.json' with your input JSON file path
    # Replace 'updated_data.json' with your desired output JSON file path
    update_json_with_simbad_data('../datasets/updated_merged_star_exo_data_dist.json', '../datasets/updated_merged_star_exo_data_dist_absmag.json')
