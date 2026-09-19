import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

df = pd.read_csv(INPUT_FILE)

# LOAD DATA

df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

df = df.sort_values(
    ["cyclone_id", "timestamp_utc"]
)

# PLOT ALL CYCLONE TRACKS

plt.figure(figsize=(10, 8))

for cyclone_id, cyclone in df.groupby("cyclone_id"):

    plt.plot(
        cyclone["longitude"],
        cyclone["latitude"],
        marker="o",
        markersize=2,
        linewidth=1,
        alpha=0.7
    )

plt.title("Cyclone Tracks — IMD 2024–2025")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "reports/imd_cyclone_tracks.png",
    dpi=200
)

plt.show()

# 2024 vs 2025

for year in [2024, 2025]:

    plt.figure(figsize=(10, 8))

    year_df = df[df["year"] == year]

    for cyclone_id, cyclone in year_df.groupby("cyclone_id"):

        plt.plot(
            cyclone["longitude"],
            cyclone["latitude"],
            marker="o",
            markersize=2,
            linewidth=1,
            alpha=0.7
        )

    plt.title(f"Cyclone Tracks — IMD {year}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        f"reports/imd_cyclone_tracks_{year}.png",
        dpi=200
    )

    plt.show()

print("\n===== TRACK VISUALIZATION COMPLETE =====")
print("Saved:")
print("reports/imd_cyclone_tracks.png")
print("reports/imd_cyclone_tracks_2024.png")
print("reports/imd_cyclone_tracks_2025.png")