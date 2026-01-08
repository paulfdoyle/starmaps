from astropy.coordinates import SkyCoord    
from astropy import units as u

# Define the galactic coordinates
l = 199.79 * u.deg  # Galactic longitude
b = -8.96 * u.deg   # Galactic latitude
distance = 152.6718 * u.pc  # Distance in parsecs

print (f"Original galactic coordinates of Betelgeuse: GLON: {l}, GLAT: {b}")

# Create a SkyCoord object in the Galactic frame
galactic_coord = SkyCoord(l=l, b=b, frame='galactic', distance=distance)

# Convert to Cartesian coordinates using the cartesian attribute
cartesian_coord = galactic_coord.cartesian

# Print Cartesian coordinates
print(f"Astropy Cartesian coordinates: x = {cartesian_coord.x}, y = {cartesian_coord.y}, z = {cartesian_coord.z}")

# Create a SkyCoord object from Cartesian coordinates in Galactic frame
cartesian_galactic = SkyCoord(cartesian_coord, frame='galactic', representation_type='cartesian')

# Convert the Cartesian coordinates to Equatorial coordinates (ICRS frame)
equatorial_coord_from_cartesian = cartesian_galactic.transform_to('icrs')

# Print the Equatorial coordinates
print(f"Astropy Equatorial coordinates from Cartesian: RA = {equatorial_coord_from_cartesian.ra.degree} degrees, DEC = {equatorial_coord_from_cartesian.dec.degree} degrees")

# Recover Original Galactic Coordinates from Cartesian
recovered_galactic_from_cartesian = cartesian_galactic.represent_as('spherical')
print(f"Recovered Galactic from Cartesian: l = {recovered_galactic_from_cartesian.lon.deg} deg, b = {recovered_galactic_from_cartesian.lat.deg} deg")

# Recover Original Galactic Coordinates from Equatorial (via Cartesian)
recovered_galactic_from_equatorial_via_cartesian = equatorial_coord_from_cartesian.transform_to('galactic')
print(f"Recovered Galactic from Equatorial via Cartesian: l = {recovered_galactic_from_equatorial_via_cartesian.l.deg} deg, b = {recovered_galactic_from_equatorial_via_cartesian.b.deg} deg")

# Direct conversion from Galactic to Equatorial
equatorial_direct_from_galactic = galactic_coord.transform_to('icrs') 

print(f"Direct conversion from galactic to RADEC-> RA = {equatorial_direct_from_galactic.ra.deg} degrees, DEC = {equatorial_direct_from_galactic.dec.deg} degrees")

# Recover Original Galactic Coordinates from Directly Converted Equatorial
recovered_galactic_from_direct_equatorial = equatorial_direct_from_galactic.transform_to('galactic')
print(f"Recovered Galactic from Direct Equatorial: l = {recovered_galactic_from_direct_equatorial.l.deg} deg, b = {recovered_galactic_from_direct_equatorial.b.deg} deg")

# Function to convert RA/DEC to degrees from h, min, sec
def ra_dec_to_degrees(rahrs, ramin, rasec, decsign, decdeg, decmin, decsec):
    # Convert Right Ascension to decimal degrees
    ra_degrees = (rahrs + ramin / 60 + rasec / 3600) * 15

    # Convert Declination to decimal degrees
    dec_degrees = decdeg + decmin / 60 + decsec / 3600
    if decsign == "-":
        dec_degrees = -dec_degrees

    return ra_degrees, dec_degrees
    
# Input values for RA/DEC conversion

##Betelgeuse
rahrs = 5.0
ramin = 55.0
rasec = 10.3
decsign = "+"
decdeg = 7.0
decmin = 24.0
decsec = 25.0


# # Calculate RA and DEC in degrees
# ra_degrees, dec_degrees = ra_dec_to_degrees(rahrs, ramin, rasec, decsign, decdeg, decmin, decsec)
# print(f"Directly calculated RA = {ra_degrees} degrees, DEC = {dec_degrees} degrees")

# # Verify the converted Equatorial coordinates against directly calculated values
# print("Verification of Equatorial coordinates:")
# print(f"Transformed RA = {equatorial_coord_from_cartesian.ra.degree:.6f} degrees, Expected RA = {ra_degrees:.6f} degrees")
# print(f"Transformed DEC = {equatorial_coord_from_cartesian.dec.degree:.6f} degrees, Expected DEC = {dec_degrees:.6f} degrees")


### Proving discrepancy in cartesian coordiantes when converted from galactic frame and equatorial frame

# Define Betelgeuse in Equatorial coordinates

# betelgeuse_icrs = SkyCoord(ra=88.7929383*u.degree, dec=7.4070642*u.degree, distance=152.6718*u.pc, frame='icrs')

# # Convert to Galactic coordinates
# betelgeuse_galactic = betelgeuse_icrs.galactic

# # Calculate Cartesian coordinates in the ICRS frame
# x_icrs, y_icrs, z_icrs = betelgeuse_icrs.cartesian.xyz

# # Calculate Cartesian coordinates in the Galactic frame
# x_gal, y_gal, z_gal = betelgeuse_galactic.cartesian.xyz

# print(f"ICRS Cartesian coordinates: x={x_icrs}, y={y_icrs}, z={z_icrs}")
# print(f"Galactic Cartesian coordinates: x={x_gal}, y={y_gal}, z={z_gal}")

