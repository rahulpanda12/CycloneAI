import pandas as pd
import numpy as np

INPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

df = df.sort_values(
    ["cyclone_id", "timestamp_utc"]
).reset_index(drop=True)

# Previous position
df["prev_latitude"] = (
    df.groupby("cyclone_id")["latitude"].shift(1)
)

df["prev_longitude"] = (
    df.groupby("cyclone_id")["longitude"].shift(1)
)

# Position changes
df["delta_latitude"] = (
    df["latitude"] - df["prev_latitude"]
)

df["delta_longitude"] = (
    df["longitude"] - df["prev_longitude"]
)

# Time difference
df["time_diff_hours"] = (
    df.groupby("cyclone_id")["timestamp_utc"]
    .diff()
    .dt.total_seconds() / 3600
)

print("\n===== TRACK ANALYSIS =====")

print("\nShape:")
print(df.shape)

print("\nTime difference:")
print(df["time_diff_hours"].value_counts().sort_index())

print("\nMovement statistics:")
print(
    df[
        ["delta_latitude", "delta_longitude"]
    ].describe()
)

print("\nSample:")
print(
    df[
        [
            "cyclone_id",
            "timestamp_utc",
            "latitude",
            "longitude",
            "delta_latitude",
            "delta_longitude",
            "time_diff_hours"
        ]
    ].head(15).to_string(index=False)
)