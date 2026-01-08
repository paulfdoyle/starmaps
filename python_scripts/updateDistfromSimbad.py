import json
from astroquery.simbad import Simbad
import astropy.units as u
from astropy.coordinates import Distance

def get_distance_from_simbad_hd(hd_id):
    # Customize Simbad query to include relevant fields (parallax, distance)
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('parallax', 'distance')

    # Query SIMBAD using the HD ID
    result_table = custom_simbad.query_object(f"HD {int(hd_id)}")

    if result_table is None or len(result_table) == 0:
        print(f"No data found in SIMBAD for HD ID {hd_id}.")
        return None

    # Check for distance information
    if 'distance_result' in result_table.colnames and result_table['distance_result'][0] is not None:
        distance = result_table['distance_result'][0] * u.parsec
        return distance
    elif 'PLX_VALUE' in result_table.colnames and result_table['PLX_VALUE'][0] is not None:
        parallax = result_table['PLX_VALUE'][0]
        # Calculate the distance from parallax
        distance = Distance(parallax=parallax * u.mas).parsec
        return distance
    else:
        print(f"No distance or parallax data available for HD {hd_id}.")
        return None

def update_json_with_distances(input_json_file, output_json_file):
    with open(input_json_file, 'r') as file:
        data = json.load(file)

    for item in data:
        hd_id = item.get("hd")
        if hd_id:
            print(f"Processing HD {hd_id}...")
            old_distance = item.get("dist", None)
            if old_distance is not None:
                try:
                    old_distance = float(old_distance)
                except ValueError:
                    print(f"Invalid old distance for HD {hd_id}: {old_distance}. Skipping this entry.")
                    continue
            
            distance = get_distance_from_simbad_hd(hd_id)
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
        else:
            print("HD ID not found in item.")

    with open(output_json_file, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Updated data written to {output_json_file}")

if __name__ == "__main__":
    # Replace 'data.json' with your input JSON file path
    # Replace 'updated_data.json' with your desired output JSON file path
    update_json_with_distances('../datasets/updated_merged_star_exo_data.json', '../datasets/updated_merged_star_exo_data_dist.json')
