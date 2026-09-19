import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

# Load data
df = pd.read_csv(INPUT_FILE)

df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

df = df.sort_values(
    ["cyclone_id", "timestamp_utc"]
).reset_index(drop=True)

# 1. Category transitions

transitions = []

for cyclone_id, cyclone in df.groupby("cyclone_id"):

    cyclone = cyclone.sort_values("timestamp_utc")

    categories = cyclone["category"].tolist()

    for i in range(1, len(categories)):

        previous_category = categories[i - 1]
        current_category = categories[i]

        if previous_category != current_category:

            transitions.append({
                "cyclone_id": cyclone_id,
                "from_category": previous_category,
                "to_category": current_category
            })


transition_df = pd.DataFrame(transitions)


print("\n===== CATEGORY TRANSITIONS =====")

if transition_df.empty:

    print("No category transitions found.")

else:

    print("\nIndividual transitions:")
    print(transition_df.to_string(index=False))

    print("\nTransition counts:")

    transition_counts = (
        transition_df
        .groupby(["from_category", "to_category"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    print(transition_counts.to_string(index=False))

# 2. Category distribution by cyclone

print("\n===== CATEGORY RANGE BY CYCLONE =====")

category_order = {
    "D": 1,
    "DD": 2,
    "CS": 3,
    "SCS": 4
}

cyclone_summary = []

for cyclone_id, cyclone in df.groupby("cyclone_id"):

    categories = cyclone["category"].dropna().unique()

    categories_sorted = sorted(
        categories,
        key=lambda x: category_order.get(x, 999)
    )

    cyclone_summary.append({
        "cyclone_id": cyclone_id,
        "categories_observed": " → ".join(categories_sorted)
    })

cyclone_summary_df = pd.DataFrame(cyclone_summary)

print(cyclone_summary_df.to_string(index=False))

# 3. Category lifecycle visualization

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
            (cyclone["timestamp_utc"] - start_time)
            .dt.total_seconds()
            / duration
        ) * 100

    lifecycle_data.append(cyclone)


df_lifecycle = pd.concat(
    lifecycle_data,
    ignore_index=True
)


# Convert category to numeric level for plotting

df_lifecycle["category_level"] = (
    df_lifecycle["category"].map(category_order)
)


plt.figure(figsize=(12, 7))

for cyclone_id, cyclone in df_lifecycle.groupby("cyclone_id"):

    plt.plot(
        cyclone["lifecycle_percent"],
        cyclone["category_level"],
        linewidth=1,
        alpha=0.5
    )


plt.yticks(
    [1, 2, 3, 4],
    ["D", "DD", "CS", "SCS"]
)

plt.xlabel("Cyclone Lifecycle (%)")
plt.ylabel("Cyclone Category")

plt.title(
    "Cyclone Category Across Lifecycle — IMD 2024–2025"
)

plt.grid(True)
plt.tight_layout()

plt.savefig(
    "reports/imd_category_lifecycle.png",
    dpi=200
)

plt.show()

# 4. Final output

print("\n===== CATEGORY TRANSITION ANALYSIS COMPLETE =====")

print("\nSaved:")
print("reports/imd_category_lifecycle.png")