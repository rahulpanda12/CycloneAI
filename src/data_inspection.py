import pandas as pd
import numpy as np


# 1. FILE PATHS

file_2024 = "data/raw/imd/imd_2024_raw.csv"
file_2025 = "data/raw/imd/imd_2025_raw.csv"

# 2. LOAD IMD FILES

df_2024 = pd.read_csv(file_2024)
df_2025 = pd.read_csv(file_2025)

# 3. BASIC INFORMATION

print("=" * 60)
print("IMD 2024")
print("=" * 60)

print("Shape:", df_2024.shape)
print("Columns:", df_2024.columns.tolist())

print("\nFirst 20 rows:")
print(df_2024.head(20).to_string())

print("\nData types:")
print(df_2024.dtypes)

print("\nMissing values:")
print(df_2024.isnull().sum())


print("\n\n")


print("=" * 60)
print("IMD 2025")
print("=" * 60)

print("Shape:", df_2025.shape)
print("Columns:", df_2025.columns.tolist())

print("\nFirst 20 rows:")
print(df_2025.head(20).to_string())

print("\nData types:")
print(df_2025.dtypes)

print("\nMissing values:")
print(df_2025.isnull().sum())

# 4. NUMPY CHECK

print("\n\n")
print("=" * 60)
print("NUMPY CHECK")
print("=" * 60)

print("2024 values:", df_2024.to_numpy().shape)
print("2025 values:", df_2025.to_numpy().shape)