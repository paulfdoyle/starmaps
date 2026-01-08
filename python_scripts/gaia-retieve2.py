from astroquery.gaia import Gaia
import pandas as pd
import numpy as np

# Convert 100 light-years to parsecs
light_years_to_parsecs = 100 / 3.26156  # Approx. 30.67 parsecs

# Define ADQL query with JOIN to get luminosity and radius from astrophysical_parameters
query = f"""
SELECT TOP 2000 
    gs.source_id, 
    gs.ra, 
    gs.dec, 
    gs.parallax, 
    gs.pmra, 
    gs.pmdec, 
    gs.phot_g_mean_mag, 
    ap.teff_val, 
    ap.lum_val, 
    ap.radius_val, 
    gs.bp_rp
FROM gaiadr3.gaia_source AS gs
JOIN gaiadr3.astrophysical_parameters AS ap
ON gs.source_id = ap.source_id
WHERE gs.parallax >= {1 / light_years_to_parsecs}
"""

# Run the query and retrieve data
job = Gaia.launch_job(query)
results = job.get_results().to_pandas()

# Calculate Absolute Magnitude (M) and add it to the DataFrame
# Check for zero or negative parallax to avoid math errors
results['absolute_magnitude'] = np.where(
    results['parallax'] > 0,
    results['phot_g_mean_mag'] + 5 * (np.log10(1000 / results['parallax']) - 1),
    np.nan  # Assign NaN for stars with invalid parallax
)

# Save the data as CSV file
results.to_csv('gaia_100ly_stars_with_luminosity_radius.csv', index=False)
print("Data saved as gaia_100ly_stars_with_luminosity_radius.csv")

# Optional: Convert CSV to JSON
json_data = results.to_json(orient="records")
with open('gaia_100ly_stars_with_luminosity_radius.json', 'w') as f:
    f.write(json_data)
print("Data saved as gaia_100ly_stars_with_luminosity_radius.json")
