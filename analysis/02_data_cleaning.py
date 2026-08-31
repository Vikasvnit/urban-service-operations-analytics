import os
import pandas as pd

# ---------------------------------------
# 1. Load raw data
# ---------------------------------------
input_file = "data/raw/bookings_raw.csv"
output_file = "data/processed/bookings_clean.csv"

df = pd.read_csv(input_file)

print("=" * 60)
print("URBAN SERVICE OPERATIONS - DATA CLEANING")
print("=" * 60)

# ---------------------------------------
# 2. Initial information
# ---------------------------------------
print("\nInitial rows:", len(df))
print("Initial columns:", len(df.columns))

# ---------------------------------------
# 3. Remove exact duplicate records
# ---------------------------------------
duplicates = df.duplicated().sum()

print("\nDuplicate rows found:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates()

# ---------------------------------------
# 4. Convert date column
# ---------------------------------------
df["Booking_Date"] = pd.to_datetime(
    df["Booking_Date"],
    errors="coerce"
)

# ---------------------------------------
# 5. Standardize text columns
# ---------------------------------------
text_columns = [
    "City",
    "Service_Category",
    "Time_Slot",
    "Booking_Status",
    "Cancellation_Reason",
    "Customer_Type",
    "Payment_Method"
]

for column in text_columns:
    df[column] = df[column].astype(str).str.strip()

# ---------------------------------------
# 6. Handle missing cancellation reasons
# ---------------------------------------
df["Cancellation_Reason"] = df["Cancellation_Reason"].fillna("None")

# ---------------------------------------
# 7. Validate rating fields
# ---------------------------------------
df.loc[
    ~df["Customer_Rating"].between(1, 5),
    "Customer_Rating"
] = pd.NA

df.loc[
    ~df["Professional_Rating"].between(1, 5),
    "Professional_Rating"
] = pd.NA

# ---------------------------------------
# 8. Validate numeric fields
# ---------------------------------------
numeric_columns = [
    "Service_Price",
    "Distance_km",
    "Response_Time_Min",
    "Service_Duration_Min"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# ---------------------------------------
# 9. Remove impossible numeric values
# ---------------------------------------
df = df[df["Service_Price"] > 0]
df = df[df["Distance_km"] > 0]
df = df[df["Response_Time_Min"] > 0]
df = df[df["Service_Duration_Min"] > 0]

# ---------------------------------------
# 10. Create useful analytical fields
# ---------------------------------------

# Booking month
df["Booking_Month"] = df["Booking_Date"].dt.month

# Booking day
df["Booking_Day"] = df["Booking_Date"].dt.day_name()

# Weekend flag
df["Is_Weekend"] = df["Booking_Date"].dt.dayofweek >= 5

# Completed booking flag
df["Completed_Flag"] = (
    df["Booking_Status"] == "Completed"
).astype(int)

# Cancelled booking flag
df["Cancelled_Flag"] = (
    df["Booking_Status"] == "Cancelled"
).astype(int)

# ---------------------------------------
# 11. Save cleaned dataset
# ---------------------------------------
os.makedirs("data/processed", exist_ok=True)

df.to_csv(
    output_file,
    index=False
)

# ---------------------------------------
# 12. Cleaning summary
# ---------------------------------------
print("\nFinal rows:", len(df))
print("Final columns:", len(df.columns))

print("\nRemaining missing values:")
missing = df.isnull().sum()
print(missing[missing > 0])

print("\nFinal booking status:")
print(df["Booking_Status"].value_counts())

print("\nSaved cleaned dataset to:")
print(output_file)

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 60)