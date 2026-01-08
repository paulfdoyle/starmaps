import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy import units as u
import time
import pandas as pd  # Import pandas for tabular data representation



### Astropy Full cycle for the workflow as discussed:

### Galactic -> Cartesian -> Galactic -> RADEC

def astropy_full_cycle(l, b, d):
    # Convert from Galactic to Cartesian Coordinates
    galactic_coord = SkyCoord(l=l * u.deg, b=b * u.deg, frame='galactic', distance=d * u.pc)
    cartesian_coord = galactic_coord.cartesian

    # Recover Galactic Coordinates from Cartesian Coordinates
    cartesian_galactic = SkyCoord(cartesian_coord, frame='galactic', representation_type='cartesian')
    recovered_galactic_from_cartesian = cartesian_galactic.represent_as('spherical')

    # Directly Convert Galactic to Equatorial Coordinates
    equatorial_direct_from_galactic = galactic_coord.transform_to('icrs')

    return equatorial_direct_from_galactic.ra.deg, equatorial_direct_from_galactic.dec.deg

### Numpy Full cycle for the workflow as discussed:

### Galactic -> Cartesian -> Galactic -> RADEC
def galactic_to_cartesian(l, b, d):
    l_rad = np.radians(l)
    b_rad = np.radians(b)
    x = d * np.cos(b_rad) * np.cos(l_rad)
    y = d * np.cos(b_rad) * np.sin(l_rad)
    z = d * np.sin(b_rad)
    return x, y, z

def cartesian_to_galactic(x, y, z):
    d = np.sqrt(x**2 + y**2 + z**2)
    b_rad = np.arcsin(z / d)
    l_rad = np.arctan2(y, x)
    b = np.degrees(b_rad)
    l = np.degrees(l_rad) % 360
    return l, b, d

def galactic_to_equatorial(l, b):
    RA_NGP = 192.859508
    DEC_NGP = 27.128336
    L_NCP = 122.931919
    l_rad = np.radians(l)
    b_rad = np.radians(b)
    RA_NGP_rad = np.radians(RA_NGP)
    DEC_NGP_rad = np.radians(DEC_NGP)
    sin_b = np.sin(b_rad)
    cos_b = np.cos(b_rad)
    sin_DEC_NGP = np.sin(DEC_NGP_rad)
    cos_DEC_NGP = np.cos(DEC_NGP_rad)
    sin_DEC = sin_b * sin_DEC_NGP + cos_b * cos_DEC_NGP * np.cos(l_rad - np.radians(L_NCP))
    DEC = np.arcsin(sin_DEC)
    cos_DEC = np.cos(DEC)
    sin_l_minus_L = np.sin(l_rad - np.radians(L_NCP))
    cos_l_minus_L = np.cos(l_rad - np.radians(L_NCP))
    y = sin_l_minus_L * cos_b
    x = cos_b * sin_DEC_NGP * cos_l_minus_L - sin_b * cos_DEC_NGP
    RA = RA_NGP_rad + np.arctan2(y, x)
    RA_deg = (np.degrees(RA) - 180) % 360
    DEC_deg = np.degrees(DEC)
    return RA_deg, DEC_deg

def numpy_full_cycle(l, b, d):
    x, y, z = galactic_to_cartesian(l, b, d)
    l, b, d = cartesian_to_galactic(x, y, z)
    RA, DEC = galactic_to_equatorial(l, b)
    return RA, DEC

### Time calculation
def time_conversion(func, l, b, d):
    # Measure the time it takes to perform the conversion
    start_time = time.time()
    func(l, b, d)
    return time.time() - start_time

# Define the range of star counts
ranges = np.arange(1, 1100001, 100000)  # For 1 million stars
numpy_times = []
astropy_times = []


### Compare execution time between astropy and numpy full cycles
for num_stars in ranges:
    l, b, d = np.random.uniform(0, 360, num_stars), np.random.uniform(-90, 90, num_stars), np.random.uniform(0.1, 10000, num_stars)
    numpy_time = time_conversion(numpy_full_cycle, l, b, d)
    astropy_time = time_conversion(astropy_full_cycle, l, b, d)  # astropy_full_cycle as defined earlier
    numpy_times.append(numpy_time)
    astropy_times.append(astropy_time)

# Create a DataFrame for results
results_table = pd.DataFrame({
    "Number of Stars": ranges,
    "Numpy Execution Time (s)": numpy_times,
    "Astropy Execution Time (s)": astropy_times
})
print(results_table)

# Plot the results
plt.figure(figsize=(12, 8))
plt.plot(ranges, numpy_times, marker='o', linestyle='-', color='r', label='Numpy Cycle')
plt.plot(ranges, astropy_times, marker='o', linestyle='-', color='b', label='Astropy Cycle')
plt.title('Performance Comparison of Galactic-Equatorial Conversions')
plt.xlabel('Number of Stars')
plt.ylabel('Execution Time (s)')
plt.legend()
plt.grid(True)
plt.show()