import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/raw/weathernext/WeatherNext3_2025_Cyclones.csv")
OUTPUT_FILE = Path("data/processed/weathernext_cleaned.csv")

print("Loading WeatherNext...")
df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Original shape: {df.shape}")

# Convert timestamps
df["init_time"] = pd.to_datetime(df["init_time"], errors="coerce")
df["valid_time"] = pd.to_datetime(df["valid_time"], errors="coerce")

# Remove only rows that are demonstrably invalid.
# All previous audits found zero such rows.
invalid_mask = (
    df["init_time"].isna()
    | df["valid_time"].isna()
    | df["lat"].isna()
    | df["lon"].isna()
    | (df["lat"] < -90)
    | (df["lat"] > 90)
    | (df["lon"] < -180)
    | (df["lon"] > 180)
    | (df["lead_time_hours"] < 0)
)

removed = invalid_mask.sum()

if removed > 0:
    df = df.loc[~invalid_mask].copy()

# Remove exact duplicate rows only.
duplicates = df.duplicated().sum()

if duplicates > 0:
    df = df.drop_duplicates().copy()

# Sort for reproducibility.
df = df.sort_values(
    ["init_time", "track_id", "sample", "valid_time"]
).reset_index(drop=True)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

print("\n========================================")
print("WEATHERNEXT CLEANING RESULT")
print("========================================")

original_rows = len(pd.read_csv(INPUT_FILE, low_memory=False))

print(f"Original rows : {original_rows}")
print(f"Rows removed  : {removed + duplicates}")
print(f"Final shape   : {df.shape}")
print(f"Output file   : {OUTPUT_FILE}")

print("\n========================================")
print("CLEANING RULES")
print("========================================")
print("Invalid rows removed :", removed)
print("Exact duplicates removed:", duplicates)
print("Missing values imputed: 0")
print("Incomplete ensembles removed: 0")
print("Outliers removed: 0")
print("========================================")