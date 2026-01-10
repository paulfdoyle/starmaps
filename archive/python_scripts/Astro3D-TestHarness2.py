import Astro3D
import math

# Betelgeuse Data (from AT-HYG Database)
ra = 5.91952477         # Right Ascension in hours
dec = 7.40703634        # Declination in degrees
distance = 152.6718     # Distance in parsecs
absmag = -5.469         # Absolute Magnitude
spect = "M2IA"          # Spectral Type
ci = 1.5                # Color Index

# 1. Test Case: Estimate Star Diameter based on Absolute Magnitude, Spectral Type, and Color Index
print("Test Case 1: Estimate Star Diameter\n-------------------------------------")
diameter = Astro3D.estimate_star_diameter(absmag=absmag, spect=spect, ci=ci)
print("Expected Diameter: [Check against known value for M2IA class]")
print("Calculated Diameter (in Solar Diameters):", diameter)
print("-------------------------------------\n")

# 2. Test Case: Verify RA/Dec to Galactic Coordinates (GLON/GLAT) and back to RA/Dec
print("Test Case 2: Convert RA/Dec to Galactic Coordinates and Back\n-------------------------------------")

# Convert RA to degrees for comparison
ra_deg = ra * 15

# Convert RA/Dec to Galactic Coordinates (GLON/GLAT)
l, b = Astro3D.celestial_to_galactic(ra_deg, dec)
print(f"Galactic Coordinates: l={l:.2f} degrees, b={b:.2f} degrees")

# Convert back from Galactic Coordinates to RA/Dec
ra_back, dec_back = Astro3D.galactic_to_celestial(l, b)
print(f"Back-Converted Celestial Coordinates: RA={ra_back:.2f} degrees, Dec={dec_back:.2f} degrees")
print(f"Original RA: {ra_deg:.2f} degrees, Dec: {dec:.2f} degrees")

# Check differences
ra_diff = abs(ra_deg - ra_back)
dec_diff = abs(dec - dec_back)
if ra_diff > 0.001 or dec_diff > 0.001:
    print("Warning: Significant difference found in back-conversion.")
    print(f"RA Difference: {ra_diff}, Dec Difference: {dec_diff}")
else:
    print("Back-conversion is within acceptable error margin.")
print("-------------------------------------\n")

# 3. Test Case: Convert RA/Dec and GLON/GLAT to 3D Cartesian Coordinates
print("Test Case 3: 3D Cartesian Coordinate Transformation\n-------------------------------------")

# Convert RA/Dec to Cartesian coordinates in the celestial system
x_celestial, y_celestial, z_celestial = Astro3D.ra_dec_to_cartesian(ra, dec, distance, system="celestial", ra_in_hours=True)
print(f"Celestial 3D Coordinates: x={x_celestial:.2f}, y={y_celestial:.2f}, z={z_celestial:.2f}")

# Convert RA/Dec to GLON/GLAT, then convert to 3D Cartesian in galactic system
l, b = Astro3D.celestial_to_galactic(ra_deg, dec)
x_galactic, y_galactic, z_galactic = Astro3D.ra_dec_to_cartesian(l, b, distance, system="galactic")
print(f"Galactic 3D Coordinates: x={x_galactic:.2f}, y={y_galactic:.2f}, z={z_galactic:.2f}")
print("-------------------------------------\n")

# 4. Test Case: Direct Conversion Between Celestial and Galactic 3D Systems
print("Test Case 4: Verify Direct Conversion Between Celestial and Galactic 3D Coordinates\n-------------------------------------")

# Direct conversion from celestial to galactic
x_conv_gal, y_conv_gal, z_conv_gal = Astro3D.convert_coordinates(x_celestial, y_celestial, z_celestial, from_system="celestial", to_system="galactic", distance=distance)
print(f"Converted to Galactic Coordinates: x={x_conv_gal:.2f}, y={y_conv_gal:.2f}, z={z_conv_gal:.2f}")

# Convert back from galactic to celestial
x_back_cel, y_back_cel, z_back_cel = Astro3D.convert_coordinates(x_conv_gal, y_conv_gal, z_conv_gal, from_system="galactic", to_system="celestial", distance=distance)
print(f"Back-Converted to Celestial Coordinates: x={x_back_cel:.2f}, y={y_back_cel:.2f}, z={z_back_cel:.2f}")

# Check differences
diff_x = abs(x_celestial - x_back_cel)
diff_y = abs(y_celestial - y_back_cel)
diff_z = abs(z_celestial - z_back_cel)
if diff_x > 0.001 or diff_y > 0.001 or diff_z > 0.001:
    print("Warning: Significant difference found in direct conversion back and forth.")
    print(f"Differences - x: {diff_x:.2f}, y: {diff_y:.2f}, z: {diff_z:.2f}")
else:
    print("Direct conversion is within acceptable error margin.")
print("-------------------------------------")
