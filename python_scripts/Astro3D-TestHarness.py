import Astro3D
import math

# Betelgeuse Data (from AT-HYG Database)
ra = 5.91952477         # Right Ascension in hours
dec = 7.40703634        # Declination in degrees
distance = 152.6718     # Distance in parsecs
absmag = -5.469         # Absolute Magnitude
spect = "M2IA"          # Spectral Type
ci = 1.5                # Color Index

# Estimate Star Diameter
diameter = Astro3D.estimate_star_diameter(absmag=absmag, spect=spect, ci=ci)
print("Estimated Diameter (in Solar Diameters):", diameter)

# Convert and print 3D Coordinates for all systems
systems = ["celestial", "galactic", "galactocentric"]
for system in systems:
    print(f"\nTesting {system.capitalize()} Coordinate System:")

    # Convert RA/Dec to Cartesian coordinates for the specified system
    x, y, z = Astro3D.ra_dec_to_cartesian(ra=ra, dec=dec, distance=distance, system=system, ra_in_hours=True)
    print(f"3D Coordinates ({system.capitalize()}): x={x}, y={y}, z={z}")

    # Convert back to RA/Dec from Cartesian coordinates
    ra_back, dec_back = Astro3D.cartesian_to_ra_dec(x, y, z, system=system)
    ra_deg = ra * 15  # Convert RA from hours to degrees for comparison
    print(f"Back-Converted RA/Dec ({system.capitalize()}): RA={ra_back} degrees, Dec={dec_back} degrees")
    print(f"Original RA: {ra_deg} degrees, Dec: {dec} degrees")
    
    # Check and print differences
    ra_diff = abs(ra_deg - ra_back) if ra_back is not None else None
    dec_diff = abs(dec - dec_back) if dec_back is not None else None

    if ra_diff is not None and dec_diff is not None:
        if ra_diff > 0.001 or dec_diff > 0.001:
            print(f"Warning: Significant difference found in {system} back-conversion.")
            print(f"RA Difference: {ra_diff}, Dec Difference: {dec_diff}")
        else:
            print(f"{system.capitalize()} conversion is within acceptable error margin.")
    else:
        print(f"Error in {system.capitalize()} back-conversion; values are None.")


# Testing direct conversion between systems
for from_system in systems:
    # Get the original 3D coordinates in `from_system`
    x_orig, y_orig, z_orig = Astro3D.ra_dec_to_cartesian(ra=ra, dec=dec, distance=distance, system=from_system, ra_in_hours=True)
    
    for to_system in systems:
        if from_system != to_system:
            # Convert from one 3D system to another directly
            x_conv, y_conv, z_conv = Astro3D.convert_coordinates(x_orig, y_orig, z_orig, from_system=from_system, to_system=to_system, distance=distance)
            
            print(f"\nConversion from {from_system.capitalize()} to {to_system.capitalize()}:")
            print(f"Original Coordinates ({from_system.capitalize()}): x={x_orig}, y={y_orig}, z={z_orig}")
            print(f"Converted Coordinates ({to_system.capitalize()}): x={x_conv}, y={y_conv}, z={z_conv}")

            # Convert back to the original system for comparison
            x_back, y_back, z_back = Astro3D.convert_coordinates(x_conv, y_conv, z_conv, from_system=to_system, to_system=from_system, distance=distance)
            print(f"Back-Converted Coordinates ({from_system.capitalize()}): x={x_back}, y={y_back}, z={z_back}")
            
            # Check for significant differences
            diff_x = abs(x_orig - x_back)
            diff_y = abs(y_orig - y_back)
            diff_z = abs(z_orig - z_back)
            if diff_x > 0.001 or diff_y > 0.001 or diff_z > 0.001:
                print(f"Warning: Significant difference found in direct conversion from {from_system} to {to_system}.")
                print(f"Differences - x: {diff_x}, y: {diff_y}, z: {diff_z}")
            else:
                print(f"Direct conversion from {from_system} to {to_system} is within acceptable error margin.")
