import pandas as pd

FILE = "data/raw/weathernext/WeatherNext3_2025_Cyclones.csv"
CHUNK_SIZE = 100_000


def main():
    print("=" * 70)
    print("WEATHERNEXT EPISODE CHECK")
    print("=" * 70)

    frames = []

    print("\nReading required columns...")

    for chunk in pd.read_csv(
        FILE,
        usecols=[
            "init_time",
            "track_id",
            "sample",
            "valid_time",
            "lead_time_hours",
            "lat",
            "lon"
        ],
        chunksize=CHUNK_SIZE
    ):
        frames.append(chunk)

    df = pd.concat(frames, ignore_index=True)

    df["init_time"] = pd.to_datetime(
        df["init_time"],
        errors="coerce"
    )

    df["valid_time"] = pd.to_datetime(
        df["valid_time"],
        errors="coerce"
    )

    print(f"\nRows loaded: {len(df):,}")

    # --------------------------------------------------------------
    # One row per track_id + init_time
    # --------------------------------------------------------------
    episodes = (
        df.groupby(["track_id", "init_time"])
        .agg(
            valid_min=("valid_time", "min"),
            valid_max=("valid_time", "max"),
            min_lat=("lat", "min"),
            max_lat=("lat", "max"),
            min_lon=("lon", "min"),
            max_lon=("lon", "max"),
            samples=("sample", "nunique"),
            rows=("sample", "size")
        )
        .reset_index()
        .sort_values(["track_id", "init_time"])
    )

    print("\n" + "=" * 70)
    print("FORECAST EPISODES")
    print("=" * 70)

    print(f"\nUnique track_id + init_time episodes: {len(episodes):,}")

    # --------------------------------------------------------------
    # Show track IDs with multiple widely separated init periods
    # --------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TRACK IDs WITH MULTIPLE INIT PERIODS")
    print("=" * 70)

    track_groups = (
        episodes.groupby("track_id")
        .agg(
            episode_count=("init_time", "size"),
            first_init=("init_time", "min"),
            last_init=("init_time", "max")
        )
        .sort_values("episode_count", ascending=False)
    )

    print(track_groups.head(30).to_string())

    # --------------------------------------------------------------
    # Calculate gaps between consecutive init times
    # --------------------------------------------------------------
    episodes["previous_init"] = (
        episodes.groupby("track_id")["init_time"].shift(1)
    )

    episodes["init_gap_hours"] = (
        episodes["init_time"] - episodes["previous_init"]
    ).dt.total_seconds() / 3600

    print("\n" + "=" * 70)
    print("LARGE INIT-TIME GAPS")
    print("=" * 70)

    large_gaps = episodes[
        episodes["init_gap_hours"] > 72
    ].copy()

    print(
        f"\nNumber of init-time gaps > 72 hours: "
        f"{len(large_gaps):,}"
    )

    if len(large_gaps) > 0:
        print(
            large_gaps[
                [
                    "track_id",
                    "previous_init",
                    "init_time",
                    "init_gap_hours"
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------------------
    # Detailed look at suspicious long-period track IDs
    # --------------------------------------------------------------
    suspicious_ids = [
        "IO012025",
        "IO022025",
        "IO902025",
        "IO942025",
        "IO972025",
        "IO072025",
        "IO102025",
        "IO112025"
    ]

    print("\n" + "=" * 70)
    print("DETAILED SUSPICIOUS TRACK IDs")
    print("=" * 70)

    for track_id in suspicious_ids:
        subset = episodes[
            episodes["track_id"] == track_id
        ].copy()

        if subset.empty:
            continue

        print(f"\n--- {track_id} ---")

        print(
            subset[
                [
                    "track_id",
                    "init_time",
                    "valid_min",
                    "valid_max",
                    "samples",
                    "rows",
                    "init_gap_hours"
                ]
            ].to_string(index=False)
        )

    print("\nEpisode check complete.")


if __name__ == "__main__":
    main()