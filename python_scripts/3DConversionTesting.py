import math
import csv
from astropy.coordinates import SkyCoord
from astropy import units as u

# Configuration: Pre-defined RA units for each known database
ra_in_hours_lookup = {
    "AT-HYG": True,  # RA is in hours for AT-HYG database
    # Add more databases as needed, e.g., "Other-DB": False
}

def ra_dec_to_cartesian(ra, dec, distance, system="celestial", ra_in_hours=True):
    """
    Convert RA/Dec to 3D Cartesian coordinates based on the specified system.
    Parameters:
        ra (float): Right Ascension in hours or degrees
        dec (float): Declination in degrees
        distance (float): Distance in parsecs
        system (str): Coordinate system ('celestial', 'galactic', 'galactocentric')
        ra_in_hours (bool): If True, RA is assumed to be in hours; if False, RA is assumed to be in degrees
    Returns:
        tuple: (x, y, z) Cartesian coordinates
    """
    # Convert RA from hours to degrees if necessary
    if ra_in_hours:
        ra *= 15  # Convert hours to degrees
    
    ra_rad = math.radians(ra)
    dec_rad = math.radians(dec)
    
    if system == "celestial":
        x = distance * math.cos(dec_rad) * math.cos(ra_rad)
        y = distance * math.cos(dec_rad) * math.sin(ra_rad)
        z = distance * math.sin(dec_rad)
        
    elif system in ["galactic", "galactocentric"]:
        coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, distance=distance * u.pc, frame='icrs')
        glon = coord.galactic.l.deg
        glat = coord.galactic.b.deg

        l_rad = math.radians(glon)
        b_rad = math.radians(glat)
        x = distance * math.cos(b_rad) * math.cos(l_rad)
        y = distance * math.cos(b_rad) * math.sin(l_rad)
        z = distance * math.sin(b_rad)
        
        if system == "galactocentric":
            x -= 8000  # Shift origin to galactic center
            
    else:
        raise ValueError("Invalid system specified. Use 'celestial', 'galactic', or 'galactocentric'.")
        
    return x, y, z

def cartesian_to_ra_dec(x, y, z, system="celestial"):
    """
    Convert 3D Cartesian coordinates to RA/Dec in degrees based on the specified system.
    Parameters:
        x, y, z (float): Cartesian coordinates
        system (str): Coordinate system ('celestial', 'galactic', 'galactocentric')
    Returns:
        tuple: (ra, dec) in degrees
    """
    if system == "celestial":
        distance = math.sqrt(x**2 + y**2 + z**2)
        dec = math.degrees(math.asin(z / distance))
        ra = math.degrees(math.atan2(y, x))
        if ra < 0:
            ra += 360

    elif system in ["galactic", "galactocentric"]:
        if system == "galactocentric":
            x += 8000  # Shift origin back to Sun's position

        distance = math.sqrt(x**2 + y**2 + z**2)
        glat = math.degrees(math.asin(z / distance))
        glon = math.degrees(math.atan2(y, x))
        if glon < 0:
            glon += 360

        coord = SkyCoord(l=glon * u.deg, b=glat * u.deg, distance=distance * u.pc, frame='galactic')
        ra = coord.icrs.ra.deg
        dec = coord.icrs.dec.deg
        
    else:
        raise ValueError("Invalid system specified. Use 'celestial', 'galactic', or 'galactocentric'.")
        
    return ra, dec

def round_trip_test(ra, dec, distance, ra_in_hours=True):
    """
    Test round-trip conversion from RA/Dec to 3D Cartesian and back for all systems.
    Parameters:
        ra (float): Right Ascension in hours or degrees
        dec (float): Declination in degrees
        distance (float): Distance in parsecs
        ra_in_hours (bool): If True, RA is assumed to be in hours; if False, RA is assumed to be in degrees
    """
    for system in ["celestial", "galactic", "galactocentric"]:
        print(f"\nTesting system: {system}")
        
        # Step 1: Convert RA/Dec to Cartesian
        x, y, z = ra_dec_to_cartesian(ra, dec, distance, system=system, ra_in_hours=ra_in_hours)
        print(f"3D Coordinates: x: {x}, y: {y}, z: {z}")
        
        # Step 2: Convert back to RA/Dec
        ra_back, dec_back = cartesian_to_ra_dec(x, y, z, system=system)
        print(f"Back-converted RA: {ra_back}, Dec: {dec_back}")
        
        # Compare to original values
        original_ra = ra * 15 if ra_in_hours else ra
        print(f"Original RA: {original_ra} degrees, Dec: {dec}")
        print(f"Difference in RA: {original_ra - ra_back}, Difference in Dec: {dec - dec_back}")

def process_csv_for_round_trip(csv_path, target_hip_id, database_name):
    """
    Process a CSV file to locate a specific HIP ID and run a round-trip test.
    Parameters:
        csv_path (str): Path to the CSV file
        target_hip_id (int): HIP ID to search for in the CSV file
        database_name (str): Name of the database being read
    """
    # Use lookup table to determine if RA is in hours for this database
    ra_in_hours = ra_in_hours_lookup.get(database_name, False)

    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            if row.get("hip") and int(row["hip"]) == target_hip_id:
                distance = float(row.get("dist"))
                ra = float(row.get("ra"))
                dec = float(row.get("dec"))
                
                print(f"CSV Data for HIP {target_hip_id} from {database_name}:")
                print(f"Distance: {distance} parsecs")
                print(f"RA (original): {ra} {'hours' if ra_in_hours else 'degrees'}, Dec: {dec} degrees")

                # Run round-trip transformation test with determined units
                round_trip_test(ra, dec, distance, ra_in_hours=ra_in_hours)
                return
        print(f"No star found in CSV with HIP ID {target_hip_id}")

# Specify the path to the CSV file, target HIP ID, and database name
csv_path = '../datasets/athyg_v32.csv'
target_hip_id = 27989
database_name = "AT-HYG"

# Call the function to process CSV and run the round-trip transformation
process_csv_for_round_trip(csv_path, target_hip_id, database_name)
