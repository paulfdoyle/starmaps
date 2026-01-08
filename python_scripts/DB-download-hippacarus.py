import argparse
from astroquery.vizier import Vizier
import pandas as pd

# Mapping of catalog options for easier selection by number
catalog_options = {
    "1": "I/239/hip_main",    # Hipparcos Catalog
    "2": "I/311/hip2",        # Hipparcos-2 Catalog
    "3": "I/239/tyc_main",    # Tycho Catalog
    "4": "I/259/tyc2",        # Tycho-2 Catalog
    "5": "V/50",              # Bright Star Catalog
    "6": "III/135",           # Henry Draper Catalog
    "7": "II/336"             # AAVSO Photometric All-Sky Survey (APASS)
}

def download_catalog(catalog_id):
    try:
        # Set Vizier parameters to retrieve the entire catalog
        Vizier.ROW_LIMIT = -1  # Download all available rows

        # Query the specified catalog
        result = Vizier.get_catalogs(catalog_id)

        # Convert the result to a DataFrame
        catalog_data = result[0].to_pandas()

        # Save the DataFrame to a CSV file with catalog name in the filename
        filename = f"{catalog_id.replace('/', '_')}_catalog.csv"
        catalog_data.to_csv(filename, index=False)
        print(f"Catalog '{catalog_id}' successfully downloaded and saved as '{filename}'.")

    except Exception as e:
        print("An error occurred:", e)

def main():
    # Setup argparse for help display if -h/--help is used
    parser = argparse.ArgumentParser(
        description="This program downloads selected star catalogs from the Vizier database.\n"
                    "The user can choose between Hipparcos, Tycho, Bright Star, HD, and APASS catalogs for download.\n\n"
                    "Usage:\n"
                    "  Run the program without arguments to be prompted for catalog selection.\n"
                    "  Use '-h' or '--help' to see this help message."
    )
    
    # This will display help and exit if -h/--help is given
    parser.parse_args()

    # If no -h option, proceed with user selection
    print("Select the catalog to download:")
    print("  1: Hipparcos Catalog (I/239/hip_main)")
    print("  2: Hipparcos-2 Catalog (I/311/hip2)")
    print("  3: Tycho Catalog (I/239/tyc_main)")
    print("  4: Tycho-2 Catalog (I/259/tyc2)")
    print("  5: Bright Star Catalog (V/50)")
    print("  6: Henry Draper Catalog (III/135)")
    print("  7: AAVSO Photometric All-Sky Survey (APASS) (II/336)")
    
    choice = input("Enter the number of the catalog to download: ")

    # Verify that the input is a valid choice
    if choice in catalog_options:
        catalog_id = catalog_options[choice]
        download_catalog(catalog_id)
    else:
        print("Invalid selection. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()
