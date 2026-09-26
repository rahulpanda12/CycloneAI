import pandas as pd
from collections import defaultdict

WEATHER_NEXT_FILE = "data/raw/weathernext/WeatherNext3_2025_Cyclones.csv"
IMD_FILE = "data/processed/imd_best_track_2024_2025.csv"

CHUNK_SIZE = 100_000


def main():
    print("Loading IMD 2025 timestamps...")

    imd = pd.read_csv(IMD_FILE, parse_dates=["timestamp_utc"])

    # WeatherNext file is for 2025, so only use 2025 IMD observations.
    imd = imd[imd["year"] == 2025].copy()

    imd_timestamps = set(imd["timestamp_utc"].dropna())

    print(f"IMD 2025 observations: {len(imd)}")
    print(f"Unique IMD 2025 timestamps: {len(imd_timestamps)}")

    print("\nScanning WeatherNext...")

    usecols = [
        "init_time",
        "track_id",
        "sample",
        "valid_time",
        "lat",
        "lon",
    ]

    overlapping_groups = set()
    overlapping_episodes = set()
    overlapping_times = set()

    # Store how many WeatherNext ensemble rows exist
    # for each track_id + init_time + valid_time group.
    group_counts = defaultdict(int)

    total_rows = 0
    overlapping_rows = 0

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

        # Keep only WeatherNext forecast rows whose valid_time
        # exactly matches an IMD observation timestamp.
        overlap = chunk[chunk["valid_time"].isin(imd_timestamps)].copy()

        if overlap.empty:
            continue

        overlapping_rows += len(overlap)

        # Forecast group = one WeatherNext forecast episode
        # at one valid_time.
        groups = overlap.groupby(
            ["track_id", "init_time", "valid_time"],
            sort=False,
        )

        for (track_id, init_time, valid_time), group in groups:
            group_key = (track_id, init_time, valid_time)

            overlapping_groups.add(group_key)

            episode_key = (track_id, init_time)
            overlapping_episodes.add(episode_key)

            overlapping_times.add(valid_time)

            group_counts[group_key] += len(group)

        print(
            f"Processed chunk {chunk_no}: "
            f"{total_rows:,} rows | "
            f"overlapping rows: {overlapping_rows:,}"
        )

    print("\n" + "=" * 60)
    print("WEATHERNEXT ↔ IMD EXACT-TIME OVERLAP")
    print("=" * 60)

    print(f"Total WeatherNext rows: {total_rows:,}")
    print(f"WeatherNext rows at an IMD timestamp: {overlapping_rows:,}")
    print(f"Unique overlapping valid_times: {len(overlapping_times):,}")
    print(f"Unique overlapping forecast groups: {len(overlapping_groups):,}")
    print(f"Unique overlapping forecast episodes: {len(overlapping_episodes):,}")

    # ---------------------------------------------------------
    # Ensemble completeness
    # ---------------------------------------------------------

    if group_counts:
        counts = pd.Series(list(group_counts.values()))

        print("\nEnsemble members in overlapping forecast groups:")
        print(f"  Minimum: {counts.min()}")
        print(f"  Median:  {counts.median()}")
        print(f"  Maximum: {counts.max()}")

        print("\nSample-count distribution:")
        print(counts.value_counts().sort_index().to_string())

    # ---------------------------------------------------------
    # IMD cyclone-level overlap
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("OVERLAP BY IMD CYCLONE")
    print("=" * 60)

    # Map IMD timestamp -> cyclone IDs.
    timestamp_to_cyclones = (
        imd.groupby("timestamp_utc")["cyclone_id"]
        .apply(set)
        .to_dict()
    )

    cyclone_episode_map = defaultdict(set)

    for track_id, init_time, valid_time in overlapping_groups:
        cyclone_ids = timestamp_to_cyclones.get(valid_time, set())

        for cyclone_id in cyclone_ids:
            cyclone_episode_map[cyclone_id].add(
                (track_id, init_time)
            )

    for cyclone_id in sorted(imd["cyclone_id"].unique()):
        episodes = cyclone_episode_map.get(cyclone_id, set())

        print(
            f"{cyclone_id}: "
            f"{len(episodes)} WeatherNext episode(s)"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()