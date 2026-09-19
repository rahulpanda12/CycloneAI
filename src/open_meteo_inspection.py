import csv


file_path = "data/raw/environmental/open_meteo_raw.csv"


print("=" * 60)
print("OPEN-METEO RAW FILE INSPECTION")
print("=" * 60)

with open(file_path, "r", encoding="utf-8") as file:

    reader = csv.reader(file)

    for i, row in enumerate(reader):

        print(f"Line {i + 1}:")
        print(row)

        if i >= 14:
            break