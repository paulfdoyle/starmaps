from astroquery.vizier import Vizier
import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u  # Import units from astropy

# Set up Vizier with a reasonable row limit, as the BSC is relatively small
Vizier.ROW_LIMIT = -1  # Download all rows in BSC
bsc_catalog_id = "V/50"  # Bright Star Catalog identifier in Vizier
gaia_catalog_id = "I/355/gaiadr3"  # Gaia DR3 catalog identifier

# Step 1: Query the Bright Star Catalog to get star identifiers and coordinates
try:
    bsc_result = Vizier.get_catalogs(bsc_catalog_id)
    bsc_data = bsc_result[0].to_pandas()  # Convert BSC catalog to a DataFrame

    # Print column names to verify
    print("BSC Column Names:", bsc_data.columns)

    # Convert RAJ2000 and DEJ2000 to numeric, coerce errors to NaN, and drop NaNs
    bsc_data['RAJ2000'] = pd.to_numeric(bsc_data['RAJ2000'], errors='coerce')
    bsc_data['DEJ2000'] = pd.to_numeric(bsc_data['DEJ2000'], errors='coerce')
    bsc_data = bsc_data.dropna(subset=['RAJ2000', 'DEJ2000'])

    # Convert RA and DEC values to lists and then to SkyCoord with units
    ra_values = bsc_data['RAJ2000'].tolist()  # Convert RA to a list
    dec_values = bsc_data['DEJ2000'].tolist()  # Convert DEC to a list

    # Create SkyCoord object with RA and DEC lists and units
    bsc_coords = SkyCoord(ra=ra_values, dec=dec_values, unit=(u.deg, u.deg), frame='icrs')

except Exception as e:
    print(f"An error occurred while retrieving BSC: {e}")

# Step 2: Cross-match Gaia with BSC using RA and DEC constraints
try:
    # Set a small search radius for cross-matching (e.g., 5 arcseconds)
    radius = 5 * u.arcsec  # Define radius with units

    # Query Gaia within positions of each BSC entry if bsc_coords is defined
    if 'bsc_coords' in locals():
        gaia_matches = Vizier.query_region(
            bsc_coords, radius=radius, catalog=gaia_catalog_id
        )

        # Convert Gaia result to DataFrame for easier processing and saving
        gaia_data = gaia_matches[0].to_pandas()

        # Save the result to CSV
        gaia_data.to_csv("gaia_bsc_crossmatch.csv", index=False)
        print("Gaia-BSC cross-matched catalog successfully downloaded and saved as 'gaia_bsc_crossmatch.csv'.")
    else:
        print("Error: bsc_coords not defined due to missing RAJ2000/DEJ2000 columns.")

except Exception as e:
    print(f"An error occurred while retrieving Gaia cross-matches: {e}")
