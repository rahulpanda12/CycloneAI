import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

df = pd.read_csv(INPUT_FILE)
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])


# BASIC INFORMATION

print("\n===== IMD EDA =====")

print("\nDataset shape:")
print(df.shape)

print("\nYears:")
print(df["year"].value_counts().sort_index())

print("\nCyclones per year:")
print(df.groupby("year")["cyclone_id"].nunique())

print("\nCategory distribution:")
print(df["category"].value_counts())


# CYCLONE DURATION

duration = (
    df.groupby("cyclone_id")["timestamp_utc"]
    .agg(["min", "max"])
)

duration["duration_hours"] = (
    duration["max"] - duration["min"]
).dt.total_seconds() / 3600

duration["duration_days"] = (
    duration["duration_hours"] / 24
)

print("\nCyclone duration:")
print(duration.sort_values("duration_hours").to_string())


# INTENSITY

print("\nMSW statistics:")
print(df["msw_kt"].describe())

print("\nCentral pressure statistics:")
print(df["ecp_hpa"].describe())

print("\nAverage MSW by category:")
print(
    df.groupby("category")["msw_kt"]
    .mean()
    .sort_values()
)


# VISUALIZATION 1
# CATEGORY DISTRIBUTION

plt.figure(figsize=(8, 5))

df["category"].value_counts().sort_index().plot(
    kind="bar"
)

plt.title("Cyclone Observations by Category")
plt.xlabel("Cyclone Category")
plt.ylabel("Number of Observations")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    "reports/imd_category_distribution.png",
    dpi=150
)

plt.show()


# VISUALIZATION 2
# MSW DISTRIBUTION
plt.figure(figsize=(8, 5))

df["msw_kt"].plot(
    kind="hist",
    bins=15
)

plt.title("Maximum Sustained Wind Distribution")
plt.xlabel("MSW (knots)")
plt.ylabel("Number of Observations")
plt.tight_layout()

plt.savefig(
    "reports/imd_msw_distribution.png",
    dpi=150
)

plt.show()

# VISUALIZATION 3
# CENTRAL PRESSURE

plt.figure(figsize=(8, 5))

df["ecp_hpa"].plot(
    kind="hist",
    bins=15
)

plt.title("Central Pressure Distribution")
plt.xlabel("Central Pressure (hPa)")
plt.ylabel("Number of Observations")
plt.tight_layout()

plt.savefig(
    "reports/imd_pressure_distribution.png",
    dpi=150
)

plt.show()

print("\n===== EDA COMPLETE =====")
print("Charts saved in reports/")