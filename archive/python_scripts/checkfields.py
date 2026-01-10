from astroquery.vizier import Vizier

# Specify the Gaia Data Release catalog identifier in Vizier
catalog_id = "I/355/gaiadr3"  # Gaia DR3 catalog identifier

# Set Vizier's row limit to 0 to only retrieve metadata (no data rows)
Vizier.ROW_LIMIT = 0

# Query the catalog to get metadata
try:
    catalog_metadata = Vizier.get_catalogs(catalog_id)
    catalog = catalog_metadata[0]  # Access the first (and usually only) table

    # Display available columns and descriptions
    print("Available fields in the Gaia DR3 catalog:")
    for column in catalog.columns:
        print(f"{column}: {catalog[column].description}")

except Exception as e:
    print(f"An error occurred: {e}")
