import json
import numpy as np
#  https://science.nasa.gov/exoplanet-catalog/hd-190360-c/  
# Load the JSON data from the file
file_path = '../datasets/updated_merged_star_exo_data.json'

with open(file_path, 'r') as file:
    data = json.load(file)

# Constants for calculations
T_sun = 5778  # Sun's effective temperature in K

# Function to calculate habitable zone
def calculate_habitable_zone(st_teff, st_rad):
    luminosity = (st_rad ** 2) * (st_teff / T_sun) ** 4
    hz_inner = np.sqrt(luminosity / 1.1)
    hz_outer = np.sqrt(luminosity / 0.53)
    return hz_inner, hz_outer

# Process each star and its planets
for star in data:
    # Only process stars that have exoplanets
    if 'exo_planets' in star and len(star['exo_planets']) > 0:
        for planet in star['exo_planets']:
            st_teff = planet.get("st_teff", None)
            st_rad = planet.get("st_rad", None)
            hip_value = star.get("hip", "N/A")  # Get HIP value, default to "N/A" if not available
            planet_name = planet.get("pl_name", "Unknown")  # Get planet name, default to "Unknown" if not available
            
            # Convert st_teff and st_rad to float, if possible
            try:
                st_teff = float(st_teff)
                st_rad = float(st_rad)
            except (TypeError, ValueError):
                print(f"HIP {hip_value}: Invalid data for habitable zone calculation.")
                continue
            
            # Check if the values are valid and not None
            if st_teff > 0 and st_rad > 0:
                hz_inner, hz_outer = calculate_habitable_zone(st_teff, st_rad)
                
                pl_orbsmax_str = planet.get("pl_orbsmax", "")
                pl_orbper = planet.get("pl_orbper", "N/A")  # Get rotational period, default to "N/A"
                try:
                    pl_orbsmax = float(pl_orbsmax_str)
                except ValueError:
                    print(f"HIP {hip_value}: Planet {planet_name} has invalid or missing semi-major axis data.")
                    continue

                # Determine the position of the planet relative to the habitable zone
                if hz_inner <= pl_orbsmax <= hz_outer:
                    position = "inside HZ"
                elif pl_orbsmax < hz_inner:
                    position = "too close"
                else:
                    position = "too far away"

                print(f"HIP {hip_value}, Planet: {planet_name}, Habitable Zone Range: {hz_inner:.2f} AU - {hz_outer:.2f} AU, "
                      f"Distance of the planet: {pl_orbsmax:.2f} AU, Rotational Period: {pl_orbper} days, "
                      f"Position: {position}")
            else:
                print(f"HIP {hip_value}: Insufficient data for habitable zone calculation.")
        print()  # Blank line for readability
