import pandas as pd
import re
import numpy as np


FILE_2024 = "data/raw/imd/imd_2024_raw.csv"
FILE_2025 = "data/raw/imd/imd_2025_raw.csv"


TIME_PATTERN = r"\b(0000|0300|0600|0900|1200|1500|1800|2100)\b"
DATE_PATTERN = r"\b(\d{2})[.\-](\d{2})[.\-](\d{2,4})\b"
TABLE_PATTERN = r"\bTable\s+(\d+)"
CATEGORY_PATTERN = r"\b(D|DD|CS|SCS|VSCS|ESCS|SuCS)\b"


def extract_date(row):
    match = re.search(DATE_PATTERN, row)

    if match is None:
        return None

    day, month, year = match.groups()

    if len(year) == 2:
        year = "20" + year

    return f"{day}-{month}-{year}"


def extract_time(row):
    match = re.search(TIME_PATTERN, row)

    if match is None:
        return None

    return match.group(1)


def extract_numeric_values(row):
    """
    Extract numeric values while preserving '-' as NaN.
    """

    remaining = re.sub(DATE_PATTERN, " ", row)
    remaining = re.sub(TIME_PATTERN, " ", remaining)

    category_match = re.search(CATEGORY_PATTERN, remaining)

    if category_match:
        remaining = re.sub(CATEGORY_PATTERN, " ", remaining)

    tokens = remaining.split()

    values = []

    for token in tokens:

        if token == "-":
            values.append(np.nan)

        else:
            try:
                values.append(float(token))
            except ValueError:
                pass

    return values


def is_valid_observation(row):
    """
    Check whether a row actually looks like a best-track observation.

    We require:
    latitude, longitude, CI, ECP, pressure-drop/MSW values,
    and a cyclone category.
    """

    time = extract_time(row)

    if time is None:
        return False

    category_match = re.search(CATEGORY_PATTERN, row)

    if category_match is None:
        return False

    values = extract_numeric_values(row)

    if len(values) < 6:
        return False

    latitude = values[0]
    longitude = values[1]
    ecp = values[3]

    # Geographic sanity checks
    if not (0 <= latitude <= 40):
        return False

    if not (40 <= longitude <= 110):
        return False

    # Central pressure should be realistic
    if pd.isna(ecp) or not (850 <= ecp <= 1050):
        return False

    return True


def parse_observation(row, current_date, year, cyclone_id, previous_time=None):
    """
    Parse one valid observation.

    2024:
        Lat Lon CI ECP MSW ΔP Category

    2025:
        Lat Lon CI ECP ΔP MSW Category

    Date handling:
    - Use an explicit date when present.
    - If the time moves backward (e.g. 1800 -> 0000),
      advance the date by one day.
    """

    time = extract_time(row)

    if time is None:
        return None, current_date, previous_time

    # 1. Handle explicit date in the current row

    date_in_row = extract_date(row)

    if date_in_row is not None:
        current_date = date_in_row

    # 2. If no explicit date, detect midnight rollover

    if date_in_row is None and current_date is not None:
        if previous_time is not None:
            current_minutes = int(time[:2]) * 60 + int(time[2:])
            previous_minutes = int(previous_time[:2]) * 60 + int(previous_time[2:])

            # Example:
            # 1800 -> 0000
            # 2100 -> 0000
            if current_minutes < previous_minutes:
                current_timestamp = pd.to_datetime(
                    current_date,
                    dayfirst=True,
                    errors="coerce"
                )

                if not pd.isna(current_timestamp):
                    current_timestamp += pd.Timedelta(days=1)
                    current_date = current_timestamp.strftime("%d-%m-%Y")

    if current_date is None:
        return None, current_date, previous_time

    # 3. Extract category
    category_match = re.search(CATEGORY_PATTERN, row)

    if category_match is None:
        return None, current_date, previous_time

    category = category_match.group(1)

    # 4. Extract numeric values
    values = extract_numeric_values(row)

    if len(values) < 6:
        return None, current_date, previous_time

    latitude = values[0]
    longitude = values[1]
    ci_no = values[2]
    ecp_hpa = values[3]

    value_1 = values[4]
    value_2 = values[5]

    if year == 2024:
        msw_kt = value_1
        pressure_drop_hpa = value_2
    else:
        pressure_drop_hpa = value_1
        msw_kt = value_2


    # 5. Construct timestamp

    timestamp = pd.to_datetime(
        f"{current_date} {time[:2]}:{time[2:]}",
        dayfirst=True,
        errors="coerce"
    )

    if pd.isna(timestamp):
        return None, current_date, previous_time

    # 6. Create observation
    observation = {
        "cyclone_id": cyclone_id,
        "year": year,
        "timestamp_utc": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "ci_no": ci_no,
        "ecp_hpa": ecp_hpa,
        "pressure_drop_hpa": pressure_drop_hpa,
        "msw_kt": msw_kt,
        "category": category
    }

    return observation, current_date, time


def process_file(file_path, year):
    """
    Process one flattened IMD CSV.

    Each Table X section becomes one cyclone_id.
    """

    df = pd.read_csv(file_path)

    text = df.iloc[:, 0].fillna("").astype(str)

    observations = []

    current_table = None
    current_date = None

    # Store rows belonging to each table first.
    table_rows = {}
    table_order = []

    for row in text:

        row = row.strip()

        if not row:
            continue

        table_match = re.search(r"\bTable\s*(\d+)\s*[:.]", row, re.IGNORECASE)

        if table_match:

            table_number = int(table_match.group(1))

            current_table = f"{year}_T{table_number:02d}"

            current_date = None

            if current_table not in table_rows:
                table_rows[current_table] = []
                table_order.append(current_table)

            continue

        if current_table is not None:
            table_rows[current_table].append(row)

    # Process each table separately.
    for cyclone_id in table_order:

        rows = table_rows[cyclone_id]

        # Find the first explicit date inside this table.
        #
        # This is important because the first observations may
        # appear before the date is printed.
        initial_date = None

        for row in rows:

            date_found = extract_date(row)

            if date_found is not None:
                initial_date = date_found
                break

        current_date = initial_date

        # Keep track of the previous observation time so that
        # midnight rollover can be detected:
        # 1800 -> 0000 means next day.
        previous_time = None

        rows = table_rows[cyclone_id]

        # Find the first explicit date inside this table.
        #
        # This is important because the first observations may
        # appear before the date is printed.
        initial_date = None

        for row in rows:

            date_found = extract_date(row)

            if date_found is not None:
                initial_date = date_found
                break

        current_date = initial_date

        # Keep track of the previous observation time so that
        # midnight rollover can be detected:
        # 1800 -> 0000 means next day.
        previous_time = None

        for row in rows:

            if not is_valid_observation(row):
                continue

            observation, current_date, previous_time = parse_observation(
                row,
                current_date,
                year,
                cyclone_id,
                previous_time
            )

            if observation is not None:
                observations.append(observation)
    return pd.DataFrame(observations)


# PROCESS 2024

df_2024 = process_file(FILE_2024, 2024)

print("\n===== 2024 =====")
print("Shape:", df_2024.shape)

print("\nObservations per cyclone:")
print(df_2024.groupby("cyclone_id").size())

print("\nFirst 10 observations:")
print(df_2024.head(10).to_string(index=False))



# PROCESS 2025

df_2025 = process_file(FILE_2025, 2025)

print("\n===== 2025 =====")
print("Shape:", df_2025.shape)

print("\nObservations per cyclone:")
print(df_2025.groupby("cyclone_id").size())

print("\nFirst 10 observations:")
print(df_2025.head(10).to_string(index=False))



# COMBINE

df = pd.concat(
    [df_2024, df_2025],
    ignore_index=True
)

df = df.sort_values(
    ["cyclone_id", "timestamp_utc"]
).reset_index(drop=True)


print("\n===== COMBINED DATA =====")

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isna().sum())

print("\nCategory counts:")
print(df["category"].value_counts())

print("\nCyclone counts:")
print(df["cyclone_id"].nunique())



# VALIDATION

print("\n===== CYCLONE DATE RANGES =====")

summary = (
    df.groupby("cyclone_id")
    .agg(
        observations=("timestamp_utc", "count"),
        start=("timestamp_utc", "min"),
        end=("timestamp_utc", "max")
    )
)

print(summary.to_string())


print("\n===== DUPLICATE CYCLONE + TIMESTAMP CHECK =====")

duplicates = df.duplicated(
    subset=["cyclone_id", "timestamp_utc"]
).sum()

print("Duplicate cyclone/timestamp rows:", duplicates)


print("\n===== TIMESTAMP ORDER CHECK =====")

bad_order = 0

for cyclone_id, group in df.groupby("cyclone_id"):

    timestamps = group["timestamp_utc"]

    if not timestamps.is_monotonic_increasing:
        bad_order += 1
        print("Not sorted:", cyclone_id)

print("Cyclones with timestamp ordering problems:", bad_order)


# SAVE PROCESSED DATA

OUTPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

df_combined = pd.concat(
    [df_2024, df_2025],
    ignore_index=True
)

df_combined = df_combined.sort_values(
    ["cyclone_id", "timestamp_utc"]
).reset_index(drop=True)

df_combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===== SAVED PROCESSED DATA =====")
print("File:", OUTPUT_FILE)
print("Shape:", df_combined.shape)


# SAVE PROCESSED DATA

OUTPUT_FILE = "data/processed/imd_best_track_2024_2025.csv"

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===== SAVED PROCESSED DATA =====")
print("File:", OUTPUT_FILE)
print("Shape:", df.shape)