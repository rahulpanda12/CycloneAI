import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
df = df.sort_values(["cyclone_id", "timestamp_utc"])

# 1. MSW over time for all cyclones

plt.figure(figsize=(12, 7))

for cyclone_id, cyclone in df.groupby("cyclone_id"):
    plt.plot(
        cyclone["timestamp_utc"],
        cyclone["msw_kt"],
        linewidth=1,
        alpha=0.6
    )

plt.title("Cyclone Intensity Over Time — IMD 2024–2025")
plt.xlabel("Time")
plt.ylabel("Maximum Sustained Wind (kt)")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "reports/imd_intensity_over_time.png",
    dpi=200
)

plt.show()

# 2. Central pressure over time

plt.figure(figsize=(12, 7))

for cyclone_id, cyclone in df.groupby("cyclone_id"):
    plt.plot(
        cyclone["timestamp_utc"],
        cyclone["ecp_hpa"],
        linewidth=1,
        alpha=0.6
    )

plt.title("Central Pressure Over Time — IMD 2024–2025")
plt.xlabel("Time")
plt.ylabel("Central Pressure (hPa)")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "reports/imd_pressure_over_time.png",
    dpi=200
)

plt.show()


print("\n===== INTENSITY VISUALIZATION COMPLETE =====")
print("Saved:")
print("reports/imd_intensity_over_time.png")
print("reports/imd_pressure_over_time.png")