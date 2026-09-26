import pandas as pd
import numpy as np

WEATHER_NEXT_FILE = "data/raw/weathernext/WeatherNext3_2025_Cyclones.csv"
IMD_FILE = "data/processed/imd_best_track_2024_2025.csv"

CHUNK_SIZE = 100_000


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def main():

    print("Loading IMD 2025 data...")

    imd = pd.read_csv(
        IMD_FILE,
        parse_dates=["timestamp_utc"]
    )

    imd = imd[imd["year"] == 2025].copy()

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

    print(f"IMD observations: {len(imd_lookup)}")
    print(f"Unique IMD timestamps: {len(imd_timestamps)}")

    # ---------------------------------------------------------
    # Aggregate WeatherNext ensemble members
    # ---------------------------------------------------------

    usecols = [
        "init_time",
        "track_id",
        "sample",
        "valid_time",
        "lat",
        "lon",
    ]

    aggregates = {}

    total_rows = 0

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

        chunk = chunk[
            chunk["valid_time"].isin(imd_timestamps)
        ].copy()

        if chunk.empty:
            continue

        chunk = chunk.dropna(
            subset=["lat", "lon"]
        )

        grouped = chunk.groupby(
            [
                "track_id",
                "init_time",
                "valid_time",
            ],
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
            f"{total_rows:,} rows"
        )

    # ---------------------------------------------------------
    # Build WeatherNext ensemble mean positions
    # ---------------------------------------------------------

    records = []

    for (
        track_id,
        init_time,
        valid_time
    ), values in aggregates.items():

        lat_sum, lon_sum, sample_count = values

        records.append(
            {
                "track_id": track_id,
                "init_time": init_time,
                "valid_time": valid_time,
                "wn_mean_lat": lat_sum / sample_count,
                "wn_mean_lon": lon_sum / sample_count,
                "sample_count": int(sample_count),
            }
        )

    wn = pd.DataFrame(records)

    print(
        f"\nWeatherNext forecast groups: "
        f"{len(wn):,}"
    )

    # ---------------------------------------------------------
    # Match by SAME valid_time
    # ---------------------------------------------------------

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

    merged["lead_time_hours"] = (
        merged["valid_time"] - merged["init_time"]
    ).dt.total_seconds() / 3600

    # ---------------------------------------------------------
    # Episode-level diagnostic
    # ---------------------------------------------------------

    episode_summary = (
        merged
        .groupby(
            [
                "cyclone_id",
                "track_id",
                "init_time",
            ]
        )
        .agg(
            overlap_points=("valid_time", "count"),
            min_distance_km=("distance_km", "min"),
            median_distance_km=("distance_km", "median"),
            mean_distance_km=("distance_km", "mean"),
            max_distance_km=("distance_km", "max"),
            within_100km=(
                "distance_km",
                lambda x: (x <= 100).sum()
            ),
            within_250km=(
                "distance_km",
                lambda x: (x <= 250).sum()
            ),
            within_500km=(
                "distance_km",
                lambda x: (x <= 500).sum()
            ),
            min_lead_hours=("lead_time_hours", "min"),
            max_lead_hours=("lead_time_hours", "max"),
        )
        .reset_index()
    )

    # Require at least one close point only for DISPLAY.
    # This does NOT establish the final matching rule.
    close_candidates = episode_summary[
        episode_summary["within_500km"] > 0
    ].copy()

    close_candidates = close_candidates.sort_values(
        [
            "cyclone_id",
            "median_distance_km",
            "min_distance_km",
        ]
    )

    # ---------------------------------------------------------
    # Print candidate episodes
    # ---------------------------------------------------------

    print("\n" + "=" * 90)
    print("EPISODE-LEVEL CANDIDATES WITH AT LEAST ONE POINT <= 500 KM")
    print("=" * 90)

    if close_candidates.empty:

        print("No candidates found.")

    else:

        for cyclone_id in sorted(
            close_candidates["cyclone_id"].unique()
        ):

            print(f"\n{cyclone_id}")

            candidates = close_candidates[
                close_candidates["cyclone_id"] == cyclone_id
            ]

            for _, row in candidates.head(15).iterrows():

                print(
                    f"  {row['track_id']} | "
                    f"init={row['init_time']} | "
                    f"points={row['overlap_points']} | "
                    f"min={row['min_distance_km']:.1f} km | "
                    f"median={row['median_distance_km']:.1f} km | "
                    f"mean={row['mean_distance_km']:.1f} km | "
                    f"<=100={int(row['within_100km'])} | "
                    f"<=250={int(row['within_250km'])} | "
                    f"<=500={int(row['within_500km'])} | "
                    f"lead={row['min_lead_hours']:.0f}-"
                    f"{row['max_lead_hours']:.0f}h"
                )

    # ---------------------------------------------------------
    # Best episode per cyclone by median distance
    # ---------------------------------------------------------

    print("\n" + "=" * 90)
    print("BEST CANDIDATE EPISODE PER IMD CYCLONE")
    print("=" * 90)

    for cyclone_id in sorted(
        episode_summary["cyclone_id"].unique()
    ):

        candidates = episode_summary[
            episode_summary["cyclone_id"] == cyclone_id
        ].sort_values(
            [
                "median_distance_km",
                "min_distance_km",
            ]
        )

        best = candidates.iloc[0]

        print(
            f"{cyclone_id}: "
            f"{best['track_id']} | "
            f"init={best['init_time']} | "
            f"points={best['overlap_points']} | "
            f"min={best['min_distance_km']:.1f} km | "
            f"median={best['median_distance_km']:.1f} km | "
            f"mean={best['mean_distance_km']:.1f} km | "
            f"<=100={int(best['within_100km'])} | "
            f"<=250={int(best['within_250km'])} | "
            f"<=500={int(best['within_500km'])}"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()