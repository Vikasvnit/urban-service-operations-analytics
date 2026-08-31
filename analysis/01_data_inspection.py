import pandas as pd

# Load the raw dataset
file_path = "data/raw/bookings_raw.csv"
df = pd.read_csv(file_path)

print("=" * 60)
print("URBAN SERVICE OPERATIONS - DATA INSPECTION")
print("=" * 60)

# 1. Dataset size
print("\n1. DATASET SHAPE")
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")

# 2. Column names
print("\n2. COLUMNS")
for column in df.columns:
    print("-", column)

# 3. Data types
print("\n3. DATA TYPES")
print(df.dtypes)

# 4. Missing values
print("\n4. MISSING VALUES")
missing = df.isnull().sum()
print(missing[missing > 0])

# 5. Duplicate rows
print("\n5. DUPLICATE ROWS")
print(df.duplicated().sum())

# 6. Booking status
print("\n6. BOOKING STATUS")
print(df["Booking_Status"].value_counts())

# 7. Service categories
print("\n7. SERVICE CATEGORIES")
print(df["Service_Category"].value_counts())

# 8. Cities
print("\n8. CITIES")
print(df["City"].value_counts())

# 9. Numerical summary
print("\n9. NUMERICAL SUMMARY")
print(df.describe())

print("\n" + "=" * 60)
print("DATA INSPECTION COMPLETED")
print("=" * 60)