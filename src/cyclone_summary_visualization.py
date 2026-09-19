import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/processed/cyclone_summary.csv"

df = pd.read_csv(INPUT_FILE)

# 1. Cyclone duration vs maximum wind speed

plt.figure(figsize=(10, 7))

for year in sorted(df["year"].unique()):

    year_df = df[df["year"] == year]

    plt.scatter(
        year_df["duration_days"],
        year_df["max_msw_kt"],
        label=str(year),
        alpha=0.7
    )

plt.xlabel("Cyclone Duration (days)")
plt.ylabel("Maximum Sustained Wind (kt)")
plt.title("Cyclone Duration vs Maximum Intensity — IMD 2024–2025")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    "reports/cyclone_duration_vs_intensity.png",
    dpi=200
)

plt.show()

# 2. Maximum intensity of each cyclone

plot_df = df.sort_values("max_msw_kt")

plt.figure(figsize=(12, 8))

plt.barh(
    plot_df["cyclone_id"],
    plot_df["max_msw_kt"]
)

plt.xlabel("Maximum Sustained Wind (kt)")
plt.ylabel("Cyclone")
plt.title("Maximum Intensity by Cyclone — IMD 2024–2025")
plt.grid(axis="x")
plt.tight_layout()

plt.savefig(
    "reports/cyclone_max_intensity.png",
    dpi=200
)

plt.show()


print("\n===== CYCLONE SUMMARY VISUALIZATION COMPLETE =====")

print("Saved:")
print("reports/cyclone_duration_vs_intensity.png")
print("reports/cyclone_max_intensity.png")