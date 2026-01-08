import os
import pandas as pd
import json
import sys
import multiprocessing
import traceback

def process_file(file_path, dataset_name):
    try:
        # Read only the first 10 lines using the 'python' engine
        df = pd.read_csv(file_path, nrows=10, engine='python')
        columns_info = [
            {"name": column, "data_type": str(df[column].dtype)} for column in df.columns
        ]
        return {"filename": os.path.basename(file_path), "columns": columns_info}
    except Exception as e:
        print(f"Error processing {dataset_name}: {e}")
        traceback.print_exc()
        return None

def generate_template(directory, common_names):
    template = {}
    files = [f for f in os.listdir(directory) if f.endswith(".csv")]
    total_files = len(files)

    for idx, filename in enumerate(files, start=1):
        file_path = os.path.join(directory, filename)
        dataset_name = common_names.get(filename, filename)

        print(f"Processing file {idx} of {total_files}: {filename} ({dataset_name})")

        # Set up a multiprocessing timeout
        with multiprocessing.Pool(1) as pool:
            result = pool.apply_async(process_file, args=(file_path, dataset_name))
            try:
                file_info = result.get(timeout=30)  # Timeout set to 30 seconds
                if file_info:
                    template[dataset_name] = file_info
            except multiprocessing.TimeoutError:
                print(f"Skipping {filename} due to timeout.")

    return template

# Command-line entry point
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    common_names = {
        "III_135_catalog.csv": "III/135 Bright Star Catalog",
        "II_336_catalog.csv": "II/336 2MASS All-Sky Catalog",
        "I_239_hip_main_catalog.csv": "I/239 HIP Main Catalog",
        "I_239_tyc_main_catalog.csv": "I/239 TYC Main Catalog",
        "I_259_tyc2_catalog.csv": "I/259 TYC2 Catalog",
        "I_311_hip2_catalog.csv": "I/311 HIP2 Catalog",
        "V_50_catalog.csv": "V/50 Catalog",
        "athyg_v32.csv": "ATHYG v32 Stellar Database"
    }

    # Generate the template
    template = generate_template(directory, common_names)

    # Write the template to a JSON file
    with open("Stellar Database Templates.json", "w") as f:
        json.dump(template, f, indent=4)

    print("Template saved to 'Stellar Database Templates.json'")
