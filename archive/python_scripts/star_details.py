import sys
from astroquery.simbad import Simbad

def fetch_star_details(hip_id):
    # Create a custom Simbad query object
    custom_simbad = Simbad()
    # Add the required fields
    custom_simbad.add_votable_fields('ids', 'flux(V)')
    
    # Query the SIMBAD database for the given HIP ID
    result = custom_simbad.query_object(f"HIP {hip_id}")
    
    if result is None:
        print(f"No results found for HIP ID {hip_id}")
        return
    
    # Extract the details
    main_id = result['MAIN_ID'][0] if not result['MAIN_ID'].mask[0] else "N/A"
    ids = result['IDS'][0] if not result['IDS'].mask[0] else "N/A"
    flux_v = result['FLUX_V'][0] if not result['FLUX_V'].mask[0] else "N/A"

    # Split the IDs to find HD and HR
    hd_id = "N/A"
    hr_id = "N/A"
    for id_str in ids.split('|'):
        if id_str.strip().startswith("HD"):
            hd_id = id_str.strip()
        if id_str.strip().startswith("HR"):
            hr_id = id_str.strip()

    print(f"Proper Name: {main_id}")
    print(f"HD ID: {hd_id}")
    print(f"HR ID: {hr_id}")
    print(f"Visual Magnitude (V): {flux_v}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <HIP ID>")
    else:
        hip_id = sys.argv[1]
        fetch_star_details(hip_id)
