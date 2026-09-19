import pandas as pd

INPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"
OUTPUT_FILE = "data/processed/cyclone_summary.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

df = df.sort_values(
    ["cyclone_id", "timestamp_utc"]
)


# Category strength order
category_order = {
    "D": 1,
    "DD": 2,
    "CS": 3,
    "SCS": 4
}


# Create cyclone-level summary
summary = []

for cyclone_id, cyclone in df.groupby("cyclone_id"):

    cyclone = cyclone.sort_values("timestamp_utc")

    start = cyclone.iloc[0]
    end = cyclone.iloc[-1]

    duration_hours = (
        cyclone["timestamp_utc"].max()
        - cyclone["timestamp_utc"].min()
    ).total_seconds() / 3600

    max_msw = cyclone["msw_kt"].max()
    min_pressure = cyclone["ecp_hpa"].min()

    strongest_category = max(
        cyclone["category"].dropna(),
        key=lambda x: category_order.get(x, 0)
    )

    # Approximate total movement using consecutive observations
    total_distance = 0

    for i in range(1, len(cyclone)):

        previous = cyclone.iloc[i - 1]
        current = cyclone.iloc[i]

        lat_diff = current["latitude"] - previous["latitude"]
        lon_diff = current["longitude"] - previous["longitude"]

        # Approximate conversion to kilometres
        lat_km = lat_diff * 111
        lon_km = (
            lon_diff
            * 111
            * __import__("math").cos(
                __import__("math").radians(current["latitude"])
            )
        )

        distance = (lat_km ** 2 + lon_km ** 2) ** 0.5

        total_distance += distance

    summary.append({
        "cyclone_id": cyclone_id,
        "year": start["year"],
        "start_time": start["timestamp_utc"],
        "end_time": end["timestamp_utc"],
        "duration_hours": duration_hours,
        "duration_days": duration_hours / 24,
        "observations": len(cyclone),
        "start_latitude": start["latitude"],
        "start_longitude": start["longitude"],
        "end_latitude": end["latitude"],
        "end_longitude": end["longitude"],
        "start_category": start["category"],
        "strongest_category": strongest_category,
        "max_msw_kt": max_msw,
        "min_pressure_hpa": min_pressure,
        "approx_total_movement_km": total_distance
    })


summary_df = pd.DataFrame(summary)


# Display summary
print("\n===== CYCLONE-LEVEL SUMMARY =====")

print("\nShape:")
print(summary_df.shape)

print("\nSummary:")
print(summary_df.to_string(index=False))


# Basic statistics
print("\n===== SUMMARY STATISTICS =====")

print("\nDuration:")
print(summary_df["duration_days"].describe())

print("\nMaximum MSW:")
print(summary_df["max_msw_kt"].describe())

print("\nMinimum pressure:")
print(summary_df["min_pressure_hpa"].describe())

print("\nStrongest category:")
print(summary_df["strongest_category"].value_counts())


# Save
summary_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===== SAVED =====")
print("File:", OUTPUT_FILE)
print("Shape:", summary_df.shape)