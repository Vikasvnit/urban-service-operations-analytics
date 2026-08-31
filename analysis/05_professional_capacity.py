import os
import numpy as np
import pandas as pd

# ============================================================
# URBAN SERVICE OPERATIONS
# PROFESSIONAL MASTER + CAPACITY MODEL
# ============================================================

np.random.seed(42)

BOOKINGS_FILE = "data/processed/bookings_clean.csv"
PROFESSIONAL_FILE = "data/processed/professional_master.csv"
UPDATED_BOOKINGS_FILE = "data/processed/bookings_with_professionals.csv"
CAPACITY_FILE = "reports/professional_capacity.csv"

os.makedirs("data/processed", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# ============================================================
# 1. LOAD CLEAN BOOKINGS
# ============================================================

df = pd.read_csv(BOOKINGS_FILE)

df["Booking_Date"] = pd.to_datetime(df["Booking_Date"])

print("=" * 70)
print("PROFESSIONAL CAPACITY MODEL")
print("=" * 70)

# ============================================================
# 2. CREATE PROFESSIONAL MASTER DATA
# ============================================================

cities = [
    "Nagpur",
    "Pune",
    "Mumbai",
    "Bengaluru",
    "Delhi",
    "Hyderabad"
]

services = [
    "Cleaning",
    "Salon",
    "AC Repair",
    "Plumbing",
    "Electrician",
    "Appliance Repair"
]

professionals = []

professional_number = 1

# Four professionals for every city-service combination
# This gives us a realistic supply network.
for city in cities:
    for service in services:

        for _ in range(4):

            professional_id = f"P{professional_number:04d}"

            experience_years = np.random.randint(1, 11)

            # Standard weekly working hours
            available_hours = np.random.choice(
                [36, 40, 44, 48],
                p=[0.15, 0.55, 0.20, 0.10]
            )

            base_rating = np.clip(
                np.random.normal(4.4, 0.25),
                3.5,
                5.0
            )

            professionals.append({
                "Professional_ID": professional_id,
                "City": city,
                "Primary_Service": service,
                "Experience_Years": experience_years,
                "Available_Hours_Per_Week": available_hours,
                "Professional_Base_Rating": round(base_rating, 1)
            })

            professional_number += 1

professional_df = pd.DataFrame(professionals)

professional_df.to_csv(
    PROFESSIONAL_FILE,
    index=False
)

print("\nProfessional master created.")
print(f"Total professionals: {len(professional_df)}")

# ============================================================
# 3. CREATE LOOKUP BY CITY + SERVICE
# ============================================================

professional_lookup = {}

for _, row in professional_df.iterrows():

    key = (
        row["City"],
        row["Primary_Service"]
    )

    professional_lookup.setdefault(key, []).append(
        row["Professional_ID"]
    )

# ============================================================
# 4. ASSIGN PROFESSIONALS TO BOOKINGS
# ============================================================

assigned_professionals = []

for _, booking in df.iterrows():

    key = (
        booking["City"],
        booking["Service_Category"]
    )

    available_professionals = professional_lookup[key]

    # Assign randomly among professionals
    professional_id = np.random.choice(
        available_professionals
    )

    assigned_professionals.append(
        professional_id
    )

df["Professional_ID"] = assigned_professionals

# ============================================================
# 5. MERGE PROFESSIONAL INFORMATION
# ============================================================

df = df.drop(
    columns=[
        "Customer_ID"
    ],
    errors="ignore"
)

df = df.merge(
    professional_df,
    on="Professional_ID",
    how="left"
)

# ============================================================
# 6. CALCULATE WEEK
# ============================================================

df["Week"] = (
    df["Booking_Date"]
    .dt.to_period("W")
    .astype(str)
)

# ============================================================
# 7. SERVICE HOURS
# ============================================================

df["Service_Hours"] = (
    df["Service_Duration_Min"] / 60
)

# Only completed/rescheduled services consume
# actual professional service time.
df["Actual_Service_Hours"] = np.where(
    df["Booking_Status"].isin(
        ["Completed", "Rescheduled"]
    ),
    df["Service_Hours"],
    0
)

# ============================================================
# 8. WEEKLY PROFESSIONAL UTILIZATION
# ============================================================

weekly_capacity = (
    professional_df[
        [
            "Professional_ID",
            "Available_Hours_Per_Week"
        ]
    ]
)

# Actual hours worked by professional per week
weekly_work = (
    df.groupby(
        [
            "Professional_ID",
            "Week"
        ],
        as_index=False
    )
    .agg(
        Service_Hours=("Actual_Service_Hours", "sum"),
        Bookings=("Booking_ID", "count")
    )
)

weekly_work = weekly_work.merge(
    weekly_capacity,
    on="Professional_ID",
    how="left"
)

weekly_work["Utilization_%"] = (
    weekly_work["Service_Hours"]
    / weekly_work["Available_Hours_Per_Week"]
    * 100
)

weekly_work["Utilization_%"] = (
    weekly_work["Utilization_%"].clip(upper=100)
)

# ============================================================
# 9. PROFESSIONAL-LEVEL SUMMARY
# ============================================================

professional_summary = (
    weekly_work
    .groupby("Professional_ID", as_index=False)
    .agg(
        Weeks_Active=("Week", "count"),
        Total_Service_Hours=("Service_Hours", "sum"),
        Total_Bookings=("Bookings", "sum"),
        Avg_Weekly_Utilization=("Utilization_%", "mean"),
        Peak_Weekly_Utilization=("Utilization_%", "max")
    )
)

professional_summary = professional_summary.merge(
    professional_df,
    on="Professional_ID",
    how="left"
)

# ============================================================
# 10. UTILIZATION CATEGORY
# ============================================================

def utilization_category(value):

    if value < 25:
        return "Underutilized"

    elif value < 60:
        return "Healthy"

    elif value < 80:
        return "High"

    else:
        return "Overloaded"


professional_summary[
    "Utilization_Category"
] = professional_summary[
    "Avg_Weekly_Utilization"
].apply(utilization_category)

# ============================================================
# 11. CITY + SERVICE CAPACITY ANALYSIS
# ============================================================

city_service_capacity = (
    professional_summary
    .groupby(
        [
            "City",
            "Primary_Service"
        ],
        as_index=False
    )
    .agg(
        Professionals=(
            "Professional_ID",
            "count"
        ),
        Avg_Utilization=(
            "Avg_Weekly_Utilization",
            "mean"
        ),
        Peak_Utilization=(
            "Peak_Weekly_Utilization",
            "max"
        ),
        Total_Service_Hours=(
            "Total_Service_Hours",
            "sum"
        )
    )
)

# ============================================================
# 12. SAVE OUTPUTS
# ============================================================

df.to_csv(
    UPDATED_BOOKINGS_FILE,
    index=False
)

professional_summary.to_csv(
    CAPACITY_FILE,
    index=False
)

print("\nFiles created:")
print(
    f"1. {PROFESSIONAL_FILE}"
)

print(
    f"2. {UPDATED_BOOKINGS_FILE}"
)

print(
    f"3. {CAPACITY_FILE}"
)

# ============================================================
# 13. DISPLAY KEY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("PROFESSIONAL UTILIZATION SUMMARY")
print("=" * 70)

print(
    professional_summary[
        [
            "Utilization_Category"
        ]
    ]
    .value_counts()
)

print("\nAverage professional utilization:")
print(
    f"{professional_summary['Avg_Weekly_Utilization'].mean():.2f}%"
)

print("\nHighest average-utilization professionals:")

print(
    professional_summary[
        [
            "Professional_ID",
            "City",
            "Primary_Service",
            "Avg_Weekly_Utilization",
            "Peak_Weekly_Utilization",
            "Utilization_Category"
        ]
    ]
    .sort_values(
        "Avg_Weekly_Utilization",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)

print("\nCity + Service Capacity Analysis:")

print(
    city_service_capacity
    .sort_values(
        "Avg_Utilization",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("PROFESSIONAL CAPACITY MODEL COMPLETED")
print("=" * 70)