from astroquery.simbad import Simbad
import astropy.units as u
from astropy.coordinates import Distance

def get_distance_from_simbad_hd(hd_id):
    # Customize Simbad query to include relevant fields (parallax, distance)
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('parallax', 'distance')

    # Query SIMBAD using the HD ID
    result_table = custom_simbad.query_object(f"HD {hd_id}")

    if result_table is None or len(result_table) == 0:
        print(f"No data found in SIMBAD for HD ID {hd_id}.")
        return None

    # Check for distance information
    if 'distance_result' in result_table.colnames and result_table['distance_result'][0] is not None:
        distance = result_table['distance_result'][0] * u.parsec
        print(f"Distance for HD {hd_id} from SIMBAD: {distance:.2f} parsecs")
        return distance
    elif 'PLX_VALUE' in result_table.colnames and result_table['PLX_VALUE'][0] is not None:
        parallax = result_table['PLX_VALUE'][0]
        # Calculate the distance from parallax
        distance = Distance(parallax=parallax * u.mas).parsec
        print(f"Calculated distance for HD {hd_id} from parallax: {distance:.2f} parsecs")
        return distance
    else:
        print(f"No distance or parallax data available for HD {hd_id}.")
        return None

def main():
    while True:
        try:
            hd_id = int(input("Enter HD ID (or 0 to exit): "))
            if hd_id == 0:
                print("Exiting the program.")
                break

            distance = get_distance_from_simbad_hd(hd_id)

            if distance is not None:
                print(f"The distance to the star with HD ID {hd_id} is approximately {distance:.2f} parsecs")
            else:
                print(f"Could not determine the distance for HD ID {hd_id}.")
        except ValueError:
            print("Invalid input. Please enter a valid HD ID or 0 to exit.")

if __name__ == "__main__":
    main()
