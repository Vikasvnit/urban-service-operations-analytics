import os
import pandas as pd
import numpy as np

# ============================================================
# CAPACITY PRESSURE ANALYSIS
# ============================================================

BOOKINGS_FILE = "data/processed/bookings_with_professionals.csv"
PROFESSIONAL_FILE = "data/processed/professional_master.csv"
OUTPUT_FILE = "reports/capacity_pressure_analysis.csv"

os.makedirs("reports", exist_ok=True)

# ------------------------------------------------------------
# LOAD FILES
# ------------------------------------------------------------

bookings = pd.read_csv(BOOKINGS_FILE)
professionals = pd.read_csv(PROFESSIONAL_FILE)

print("=" * 70)
print("CAPACITY PRESSURE ANALYSIS")
print("=" * 70)

print("\nBooking columns:")
print(list(bookings.columns))

print("\nProfessional columns:")
print(list(professionals.columns))

# ------------------------------------------------------------
# USE PROFESSIONAL MASTER AS THE SOURCE OF CITY + SERVICE
# ------------------------------------------------------------

# Keep only the professional information we need.
professional_info = professionals[
    [
        "Professional_ID",
        "City",
        "Primary_Service",
        "Available_Hours_Per_Week"
    ]
].copy()

# Remove any old location/service columns from bookings.
bookings = bookings.drop(
    columns=[
        "City",
        "City_x",
        "City_y",
        "Primary_Service",
        "Service_Category_x",
        "Service_Category_y"
    ],
    errors="ignore"
)

# ------------------------------------------------------------
# MERGE PROFESSIONAL INFORMATION
# ------------------------------------------------------------

df = bookings.merge(
    professional_info,
    on="Professional_ID",
    how="left"
)

# Verify merge
missing_city = df["City"].isna().sum()
missing_service = df["Primary_Service"].isna().sum()

print(f"\nBookings without professional city: {missing_city}")
print(f"Bookings without professional service: {missing_service}")

# ------------------------------------------------------------
# DATE
# ------------------------------------------------------------

df["Booking_Date"] = pd.to_datetime(
    df["Booking_Date"],
    errors="coerce"
)

# ------------------------------------------------------------
# COMPLETED BOOKINGS ONLY
# ------------------------------------------------------------

completed = df[
    df["Booking_Status"] == "Completed"
].copy()

completed["Service_Hours"] = (
    completed["Service_Duration_Min"] / 60
)

completed["Week"] = (
    completed["Booking_Date"]
    .dt.to_period("W")
    .astype(str)
)

# ------------------------------------------------------------
# WEEKLY PROFESSIONAL WORK
# ------------------------------------------------------------

weekly = (
    completed
    .groupby(
        [
            "Professional_ID",
            "Week"
        ],
        as_index=False
    )
    .agg(
        Completed_Bookings=("Booking_ID", "count"),
        Service_Hours=("Service_Hours", "sum")
    )
)

weekly = weekly.merge(
    professional_info,
    on="Professional_ID",
    how="left"
)

# ------------------------------------------------------------
# UTILIZATION
# ------------------------------------------------------------

weekly["Utilization_%"] = (
    weekly["Service_Hours"]
    / weekly["Available_Hours_Per_Week"]
    * 100
)

# ------------------------------------------------------------
# UTILIZATION CATEGORY
# ------------------------------------------------------------

def utilization_category(value):

    if value < 25:
        return "Underutilized"

    if value < 60:
        return "Healthy"

    if value < 80:
        return "High"

    if value < 100:
        return "Very High"

    return "Over Capacity"


weekly["Utilization_Category"] = (
    weekly["Utilization_%"]
    .apply(utilization_category)
)

# ------------------------------------------------------------
# PROFESSIONAL SUMMARY
# ------------------------------------------------------------

professional_summary = (
    weekly
    .groupby(
        [
            "Professional_ID",
            "City",
            "Primary_Service"
        ],
        as_index=False
    )
    .agg(
        Avg_Utilization=(
            "Utilization_%",
            "mean"
        ),
        Peak_Utilization=(
            "Utilization_%",
            "max"
        ),
        Total_Completed_Bookings=(
            "Completed_Bookings",
            "sum"
        ),
        Total_Service_Hours=(
            "Service_Hours",
            "sum"
        )
    )
)

# ------------------------------------------------------------
# PEAK DEMAND
# ------------------------------------------------------------

peak_slots = [
    "4-6 PM",
    "6-8 PM",
    "8-10 PM"
]

peak = df[
    df["Time_Slot"].isin(peak_slots)
].copy()

peak_demand = (
    peak
    .groupby(
        [
            "City",
            "Service_Category"
        ],
        as_index=False
    )
    .agg(
        Peak_Bookings=("Booking_ID", "count"),
        Peak_Cancelled=(
            "Cancelled_Flag",
            "sum"
        ),
        Peak_Avg_Response=(
            "Response_Time_Min",
            "mean"
        )
    )
)

peak_demand["Peak_Cancellation_Rate_%"] = (
    peak_demand["Peak_Cancelled"]
    / peak_demand["Peak_Bookings"]
    * 100
)

peak_demand = peak_demand.rename(
    columns={
        "Service_Category": "Primary_Service"
    }
)

# ------------------------------------------------------------
# CITY + SERVICE CAPACITY
# ------------------------------------------------------------

capacity = (
    professional_summary
    .groupby(
        [
            "City",
            "Primary_Service"
        ],
        as_index=False
    )
    .agg(
        Professionals=("Professional_ID", "count"),
        Avg_Utilization=("Avg_Utilization", "mean"),
        Peak_Utilization=("Peak_Utilization", "max"),
        Total_Completed_Bookings=(
            "Total_Completed_Bookings",
            "sum"
        ),
        Total_Service_Hours=(
            "Total_Service_Hours",
            "sum"
        )
    )
)

# ------------------------------------------------------------
# COMBINE
# ------------------------------------------------------------

final = capacity.merge(
    peak_demand,
    on=[
        "City",
        "Primary_Service"
    ],
    how="left"
)

# ------------------------------------------------------------
# PRESSURE SCORE
# ------------------------------------------------------------

final["Capacity_Pressure_Score"] = (
    (
        final["Avg_Utilization"]
        / final["Avg_Utilization"].max()
    ) * 50
    +
    (
        final["Peak_Cancellation_Rate_%"]
        / final["Peak_Cancellation_Rate_%"].max()
    ) * 50
)

# ------------------------------------------------------------
# PRESSURE LEVEL
# ------------------------------------------------------------

def pressure_level(score):

    if score >= 75:
        return "Critical"

    if score >= 55:
        return "High"

    if score >= 35:
        return "Moderate"

    return "Low"


final["Pressure_Level"] = (
    final["Capacity_Pressure_Score"]
    .apply(pressure_level)
)

# ------------------------------------------------------------
# SORT + SAVE
# ------------------------------------------------------------

final = final.sort_values(
    "Capacity_Pressure_Score",
    ascending=False
)

final.to_csv(
    OUTPUT_FILE,
    index=False
)

# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------

print("\nTop capacity-pressure combinations:\n")

print(
    final[
        [
            "City",
            "Primary_Service",
            "Professionals",
            "Avg_Utilization",
            "Peak_Utilization",
            "Peak_Cancellation_Rate_%",
            "Peak_Avg_Response",
            "Capacity_Pressure_Score",
            "Pressure_Level"
        ]
    ]
    .head(15)
    .to_string(index=False)
)

print("\n\nPressure distribution:")

print(
    final["Pressure_Level"]
    .value_counts()
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)
print("CAPACITY PRESSURE ANALYSIS COMPLETED")
print("=" * 70)