from astroquery.vizier import Vizier
from astroquery.gaia import Gaia

def match_hr_or_hd_to_gaia(identifier, catalog="HD"):
    Vizier.ROW_LIMIT = 1  # Limit the number of results to 1

    # Choose the correct catalog based on the identifier type
    catalog_name = "III/135A"  # Example for HD catalog
    if catalog == "HR":
        catalog_name = "IV/24/hr"  # Example for HR catalog

    # Query VizieR for the star using its HR or HD ID
    result = Vizier.query_constraints(catalog=catalog_name, **{catalog: identifier})

    if len(result) == 0:
        print(f"No data found in VizieR for {catalog} ID {identifier}.")
        return None

    # Extract relevant data, e.g., Gaia DR2 ID or parallax, then query Gaia
    if 'Plx' in result[0].colnames:
        parallax = result[0]['Plx'][0]
        print(f"Found parallax in VizieR: {parallax} mas")
    else:
        print(f"No parallax information available in VizieR for {catalog} ID {identifier}.")
        return None

    query = f"""
    SELECT *
    FROM gaiadr2.gaia_source
    WHERE parallax = {parallax}
    """

    job = Gaia.launch_job(query)
    gaia_result = job.get_results()

    if len(gaia_result) == 0:
        print(f"No Gaia data found for {catalog} ID {identifier}.")
        return None

    return gaia_result

# Example usage:
hr_id = 8425  # Replace with the HR ID of the star you want to look up
gaia_data = match_hr_or_hd_to_gaia(hr_id, catalog="HR")

if gaia_data is not None:
    print(gaia_data)
