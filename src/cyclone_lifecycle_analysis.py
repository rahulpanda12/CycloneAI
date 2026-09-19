import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

df = df.sort_values(["cyclone_id", "timestamp_utc"])

# Calculate lifecycle percentage for each cyclone
lifecycle_data = []

for cyclone_id, cyclone in df.groupby("cyclone_id"):

    cyclone = cyclone.sort_values("timestamp_utc").copy()

    start_time = cyclone["timestamp_utc"].min()
    end_time = cyclone["timestamp_utc"].max()

    duration = (end_time - start_time).total_seconds()

    if duration == 0:
        cyclone["lifecycle_percent"] = 0
    else:
        cyclone["lifecycle_percent"] = (
            (cyclone["timestamp_utc"] - start_time).dt.total_seconds()
            / duration
        ) * 100

    lifecycle_data.append(cyclone)

df_lifecycle = pd.concat(lifecycle_data, ignore_index=True)


# 1. MSW vs Cyclone Lifecycle

plt.figure(figsize=(12, 7))

for cyclone_id, cyclone in df_lifecycle.groupby("cyclone_id"):
    plt.plot(
        cyclone["lifecycle_percent"],
        cyclone["msw_kt"],
        linewidth=1,
        alpha=0.5
    )

plt.xlabel("Cyclone Lifecycle (%)")
plt.ylabel("Maximum Sustained Wind (kt)")
plt.title("Cyclone Intensity Across Lifecycle — IMD 2024–2025")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "reports/imd_msw_lifecycle.png",
    dpi=200
)

plt.show()

# 2. Central Pressure vs Cyclone Lifecycle

plt.figure(figsize=(12, 7))

for cyclone_id, cyclone in df_lifecycle.groupby("cyclone_id"):
    plt.plot(
        cyclone["lifecycle_percent"],
        cyclone["ecp_hpa"],
        linewidth=1,
        alpha=0.5
    )

plt.xlabel("Cyclone Lifecycle (%)")
plt.ylabel("Central Pressure (hPa)")
plt.title("Central Pressure Across Cyclone Lifecycle — IMD 2024–2025")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "reports/imd_pressure_lifecycle.png",
    dpi=200
)

plt.show()


print("\n===== CYCLONE LIFECYCLE ANALYSIS COMPLETE =====")
print("Saved:")
print("reports/imd_msw_lifecycle.png")
print("reports/imd_pressure_lifecycle.png")