import pandas as pd
import re


# FILE PATHS

file_2024 = "data/raw/imd/imd_2024_raw.csv"
file_2025 = "data/raw/imd/imd_2025_raw.csv"

# FUNCTION TO SEARCH FOR BEST-TRACK ROWS

def inspect_file(file_path, year):

    df = pd.read_csv(file_path)

    # Convert the single column to strings
    text = df.iloc[:, 0].fillna("").astype(str)

    print("\n" + "=" * 70)
    print(f"SEARCHING IMD {year}")
    print("=" * 70)

    # Look for lines containing observation times
    time_pattern = re.compile(
        r"\b(0000|0300|0600|0900|1200|1500|1800|2100)\b"
    )

    matches = []

    for index, value in text.items():

        if time_pattern.search(value):
            matches.append((index, value))

    print(f"\nNumber of rows containing observation times: {len(matches)}")

    print("\nFirst 30 possible observation rows:")

    for index, value in matches[:30]:

        print(f"{index}: {value}")

# RUN
inspect_file(file_2024, 2024)
inspect_file(file_2025, 2025)