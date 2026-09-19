import sys
sys.path.insert(0, "src")

import pandas as pd
from imd_reconstruction import process_file, FILE_2024, FILE_2025


# LOAD RECONSTRUCTED DATA

df_2024 = process_file(FILE_2024, 2024)
df_2025 = process_file(FILE_2025, 2025)

df = pd.concat([df_2024, df_2025], ignore_index=True)

df = df.sort_values(
    ["cyclone_id", "timestamp_utc"]
).reset_index(drop=True)


print("\n===== IMD DATA QUALITY AUDIT =====")

print("\nShape:")
print(df.shape)


# 1. MISSING VALUES

print("\n===== MISSING VALUES =====")
print(df.isna().sum())



# 2. DUPLICATES

print("\n===== DUPLICATES =====")

duplicate_rows = df.duplicated().sum()

duplicate_keys = df.duplicated(
    subset=["cyclone_id", "timestamp_utc"]
).sum()

print("Duplicate complete rows:", duplicate_rows)
print("Duplicate cyclone/timestamp:", duplicate_keys)



# 3. LATITUDE / LONGITUDE CHECK

print("\n===== GEOGRAPHIC CHECK =====")

invalid_lat = df[
    ~df["latitude"].between(0, 40)
]

invalid_lon = df[
    ~df["longitude"].between(40, 110)
]

print("Invalid latitude rows:", len(invalid_lat))
print("Invalid longitude rows:", len(invalid_lon))



# 4. PRESSURE CHECK

print("\n===== PRESSURE CHECK =====")

invalid_pressure = df[
    ~df["ecp_hpa"].between(850, 1050)
]

print("Invalid central pressure rows:", len(invalid_pressure))



# 5. WIND SPEED CHECK

print("\n===== WIND SPEED CHECK =====")

invalid_wind = df[
    ~df["msw_kt"].between(0, 200)
]

print("Invalid MSW rows:", len(invalid_wind))



# 6. CATEGORY CHECK

print("\n===== CATEGORY CHECK =====")

valid_categories = {
    "D",
    "DD",
    "CS",
    "SCS",
    "VSCS",
    "ESCS",
    "SuCS"
}

invalid_categories = df[
    ~df["category"].isin(valid_categories)
]

print("Invalid category rows:", len(invalid_categories))

print("\nCategory distribution:")
print(df["category"].value_counts())


# 7. CYCLONE COUNTS

print("\n===== CYCLONE COUNTS =====")

cyclone_counts = (
    df.groupby("cyclone_id")
      .size()
      .sort_index()
)

print(cyclone_counts)

print("\nNumber of cyclones:", df["cyclone_id"].nunique())


# 8. DATE RANGES

print("\n===== DATE RANGES =====")

date_ranges = (
    df.groupby("cyclone_id")["timestamp_utc"]
      .agg(["min", "max", "count"])
)

print(date_ranges)


# 9. TIME GAPS

print("\n===== TIME GAP CHECK =====")

df["time_gap_hours"] = (
    df.groupby("cyclone_id")["timestamp_utc"]
      .diff()
      .dt.total_seconds()
      / 3600
)

print("\nTime-gap distribution:")
print(df["time_gap_hours"].describe())

large_gaps = df[
    df["time_gap_hours"] > 24
]

print(
    "\nGaps greater than 24 hours:",
    len(large_gaps)
)

if len(large_gaps) > 0:
    print(
        large_gaps[
            [
                "cyclone_id",
                "timestamp_utc",
                "time_gap_hours"
            ]
        ].to_string(index=False)
    )


# 10. FINAL SUMMARY
print("\n===== FINAL SUMMARY =====")

print("Total observations:", len(df))
print("Total cyclones:", df["cyclone_id"].nunique())
print("Duplicate keys:", duplicate_keys)
print("Missing CI:", df["ci_no"].isna().sum())
print("Invalid latitude:", len(invalid_lat))
print("Invalid longitude:", len(invalid_lon))
print("Invalid pressure:", len(invalid_pressure))
print("Invalid wind:", len(invalid_wind))
print("Invalid category:", len(invalid_categories))