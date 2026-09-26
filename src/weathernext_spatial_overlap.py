import pandas as pd
import numpy as np

WEATHER_NEXT_FILE = "data/raw/weathernext/WeatherNext3_2025_Cyclones.csv"
IMD_FILE = "data/processed/imd_best_track_2024_2025.csv"

CHUNK_SIZE = 100_000


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two latitude/longitude points.
    """
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def main():

    print("Loading IMD 2025 data...")

    imd = pd.read_csv(
        IMD_FILE,
        parse_dates=["timestamp_utc"]
    )

    imd = imd[imd["year"] == 2025].copy()

    # Keep one IMD row per cyclone + timestamp.
    imd_lookup = imd[
        [
            "cyclone_id",
            "timestamp_utc",
            "latitude",
            "longitude",
        ]
    ].copy()

    imd_timestamps = set(
        imd_lookup["timestamp_utc"].dropna()
    )

    print(f"IMD 2025 observations: {len(imd_lookup)}")
    print(f"Unique IMD timestamps: {len(imd_timestamps)}")

    # ---------------------------------------------------------
    # Read WeatherNext and aggregate ensemble members
    # ---------------------------------------------------------

    usecols = [
        "init_time",
        "track_id",
        "sample",
        "valid_time",
        "lat",
        "lon",
    ]

    # Key:
    # (track_id, init_time, valid_time)
    #
    # Value:
    # [sum_lat, sum_lon, valid_member_count]
    aggregates = {}

    total_rows = 0
    overlapping_rows = 0

    print("\nScanning WeatherNext...")

    for chunk_no, chunk in enumerate(
        pd.read_csv(
            WEATHER_NEXT_FILE,
            usecols=usecols,
            parse_dates=["init_time", "valid_time"],
            chunksize=CHUNK_SIZE,
        ),
        start=1,
    ):

        total_rows += len(chunk)

        # Only retain rows whose valid_time exists in IMD.
        chunk = chunk[
            chunk["valid_time"].isin(imd_timestamps)
        ].copy()

        if chunk.empty:
            continue

        overlapping_rows += len(chunk)

        # Only valid geographical positions contribute
        # to ensemble mean.
        chunk = chunk.dropna(
            subset=["lat", "lon"]
        )

        grouped = chunk.groupby(
            ["track_id", "init_time", "valid_time"],
            sort=False
        ).agg(
            lat_sum=("lat", "sum"),
            lon_sum=("lon", "sum"),
            sample_count=("sample", "count"),
        )

        for key, row in grouped.iterrows():

            if key not in aggregates:
                aggregates[key] = [
                    row["lat_sum"],
                    row["lon_sum"],
                    row["sample_count"],
                ]
            else:
                aggregates[key][0] += row["lat_sum"]
                aggregates[key][1] += row["lon_sum"]
                aggregates[key][2] += row["sample_count"]

        print(
            f"Processed chunk {chunk_no}: "
            f"{total_rows:,} rows | "
            f"overlapping rows: {overlapping_rows:,}"
        )

    print("\nBuilding ensemble-mean forecast positions...")

    records = []

    for (
        track_id,
        init_time,
        valid_time
    ), values in aggregates.items():

        lat_sum, lon_sum, sample_count = values

        if sample_count == 0:
            continue

        mean_lat = lat_sum / sample_count
        mean_lon = lon_sum / sample_count

        records.append(
            {
                "track_id": track_id,
                "init_time": init_time,
                "valid_time": valid_time,
                "wn_mean_lat": mean_lat,
                "wn_mean_lon": mean_lon,
                "sample_count": int(sample_count),
            }
        )

    wn = pd.DataFrame(records)

    print(f"Unique WeatherNext forecast groups: {len(wn):,}")

    # ---------------------------------------------------------
    # Match every WeatherNext forecast group against IMD
    # at the SAME valid_time.
    # ---------------------------------------------------------

    print("\nCalculating spatial distances...")

    merged = wn.merge(
        imd_lookup,
        left_on="valid_time",
        right_on="timestamp_utc",
        how="inner",
    )

    merged["distance_km"] = haversine_km(
        merged["wn_mean_lat"].to_numpy(),
        merged["wn_mean_lon"].to_numpy(),
        merged["latitude"].to_numpy(),
        merged["longitude"].to_numpy(),
    )

    # ---------------------------------------------------------
    # Sort nearest candidates first
    # ---------------------------------------------------------

    merged = merged.sort_values(
        [
            "cyclone_id",
            "valid_time",
            "distance_km",
        ]
    )

    print("\n" + "=" * 70)
    print("CLOSEST WEATHERNEXT CANDIDATES")
    print("=" * 70)

    # Show the 5 closest candidates for every IMD cyclone.
    for cyclone_id in sorted(
        merged["cyclone_id"].unique()
    ):

        candidates = merged[
            merged["cyclone_id"] == cyclone_id
        ].head(5)

        print(f"\n{cyclone_id}")

        for _, row in candidates.iterrows():

            print(
                f"  {row['valid_time']} | "
                f"{row['track_id']} | "
                f"init={row['init_time']} | "
                f"lead={row['valid_time'] - row['init_time']} | "
                f"distance={row['distance_km']:.2f} km | "
                f"members={row['sample_count']}"
            )

    # ---------------------------------------------------------
    # Best distance per IMD cyclone
    # ---------------------------------------------------------

    best = (
        merged
        .groupby("cyclone_id")["distance_km"]
        .min()
        .sort_values()
    )

    print("\n" + "=" * 70)
    print("BEST DISTANCE FOUND FOR EACH IMD CYCLONE")
    print("=" * 70)

    for cyclone_id, distance in best.items():

        print(
            f"{cyclone_id}: "
            f"{distance:.2f} km"
        )

    print("\n" + "=" * 70)
    print("DISTANCE DISTRIBUTION OF ALL CANDIDATES")
    print("=" * 70)

    print(
        merged["distance_km"].describe(
            percentiles=[
                0.01,
                0.05,
                0.10,
                0.25,
                0.50,
                0.75,
                0.90,
                0.95,
                0.99,
            ]
        )
    )

    print("\nDone.")


if __name__ == "__main__":
    main()