from astroquery.gaia import Gaia
import pandas as pd
import numpy as np

# Convert 100 light-years to parsecs
light_years_to_parsecs = 100 / 3.26156  # Approx. 30.67 parsecs

# Define ADQL query to get fields from gaiadr3.gaia_source for stars within 100 light-years
query = f"""
SELECT TOP 2000 
    source_id, 
    ra, 
    dec, 
    parallax, 
    pmra, 
    pmdec, 
    phot_g_mean_mag, 
    bp_rp
FROM gaiadr3.gaia_source
WHERE parallax >= {1 / light_years_to_parsecs}
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
results.to_csv('gaia_100ly_stars.csv', index=False)
print("Data saved as gaia_100ly_stars.csv")

# Optional: Convert CSV to JSON
json_data = results.to_json(orient="records")
with open('gaia_100ly_stars.json', 'w') as f:
    f.write(json_data)
print("Data saved as gaia_100ly_stars.json")
