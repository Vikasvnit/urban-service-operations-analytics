import pandas as pd
import numpy as np
from pathlib import Path

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

INPUT_FILE = Path("data/processed/bookings_clean.csv")
OUTPUT_DIR = Path("reports")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("=" * 70)
print("CANCELLATION DRIVER ANALYSIS")
print("=" * 70)

print(f"\nTotal bookings analyzed: {len(df):,}")


# ------------------------------------------------------------
# BASIC VALIDATION
# ------------------------------------------------------------

required_columns = [
    "Booking_ID",
    "Service_Category",
    "City",
    "Time_Slot",
    "Response_Time_Min",
    "Distance_km",
    "Customer_Type",
    "Cancelled_Flag",
]

# Your cleaned dataset may contain City_x rather than City.
# Handle that automatically.
if "City" not in df.columns and "City_x" in df.columns:
    df["City"] = df["City_x"]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ------------------------------------------------------------
# 1. RESPONSE TIME ANALYSIS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("1. RESPONSE TIME VS CANCELLATION")
print("=" * 70)

response_bins = [-1, 5, 10, 15, 20, np.inf]
response_labels = [
    "0-5 min",
    "5-10 min",
    "10-15 min",
    "15-20 min",
    "20+ min"
]

df["Response_Time_Bucket"] = pd.cut(
    df["Response_Time_Min"],
    bins=response_bins,
    labels=response_labels
)

response_analysis = (
    df.groupby("Response_Time_Bucket", observed=False)
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean")
    )
    .reset_index()
)

response_analysis["Cancellation_Rate_%"] = (
    response_analysis["Cancelled"]
    / response_analysis["Bookings"]
    * 100
)

print(
    response_analysis.to_string(
        index=False,
        formatters={
            "Cancellation_Rate_%": "{:.2f}".format,
            "Avg_Response_Time": "{:.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 2. DISTANCE ANALYSIS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("2. DISTANCE VS CANCELLATION")
print("=" * 70)

distance_bins = [-1, 3, 5, 10, 15, np.inf]
distance_labels = [
    "0-3 km",
    "3-5 km",
    "5-10 km",
    "10-15 km",
    "15+ km"
]

df["Distance_Bucket"] = pd.cut(
    df["Distance_km"],
    bins=distance_bins,
    labels=distance_labels
)

distance_analysis = (
    df.groupby("Distance_Bucket", observed=False)
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Distance=("Distance_km", "mean")
    )
    .reset_index()
)

distance_analysis["Cancellation_Rate_%"] = (
    distance_analysis["Cancelled"]
    / distance_analysis["Bookings"]
    * 100
)

print(
    distance_analysis.to_string(
        index=False,
        formatters={
            "Cancellation_Rate_%": "{:.2f}".format,
            "Avg_Distance": "{:.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 3. PEAK VS NON-PEAK
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("3. PEAK VS NON-PEAK")
print("=" * 70)

# Peak slots based on the project's generated dataset
peak_slots = [
    "6-8 PM",
    "8-10 PM"
]

df["Demand_Period"] = np.where(
    df["Time_Slot"].isin(peak_slots),
    "Peak",
    "Non-Peak"
)

period_analysis = (
    df.groupby("Demand_Period")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean")
    )
    .reset_index()
)

period_analysis["Cancellation_Rate_%"] = (
    period_analysis["Cancelled"]
    / period_analysis["Bookings"]
    * 100
)

print(
    period_analysis.to_string(
        index=False,
        formatters={
            "Cancellation_Rate_%": "{:.2f}".format,
            "Avg_Response_Time": "{:.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 4. SERVICE CATEGORY ANALYSIS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("4. SERVICE CATEGORY VS CANCELLATION")
print("=" * 70)

service_analysis = (
    df.groupby("Service_Category")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean"),
        Avg_Distance=("Distance_km", "mean")
    )
    .reset_index()
)

service_analysis["Cancellation_Rate_%"] = (
    service_analysis["Cancelled"]
    / service_analysis["Bookings"]
    * 100
)

service_analysis = service_analysis.sort_values(
    "Cancellation_Rate_%",
    ascending=False
)

print(
    service_analysis.to_string(
        index=False,
        formatters={
            "Cancellation_Rate_%": "{:.2f}".format,
            "Avg_Response_Time": "{:.2f}".format,
            "Avg_Distance": "{:.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 5. CITY ANALYSIS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("5. CITY VS CANCELLATION")
print("=" * 70)

city_analysis = (
    df.groupby("City")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean"),
        Avg_Distance=("Distance_km", "mean")
    )
    .reset_index()
)

city_analysis["Cancellation_Rate_%"] = (
    city_analysis["Cancelled"]
    / city_analysis["Bookings"]
    * 100
)

city_analysis = city_analysis.sort_values(
    "Cancellation_Rate_%",
    ascending=False
)

print(
    city_analysis.to_string(
        index=False,
        formatters={
            "Cancellation_Rate_%": "{:.2f}".format,
            "Avg_Response_Time": "{:.2f}".format,
            "Avg_Distance": "{:.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 6. CUSTOMER TYPE ANALYSIS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("6. CUSTOMER TYPE VS CANCELLATION")
print("=" * 70)

customer_type_analysis = (
    df.groupby("Customer_Type")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum")
    )
    .reset_index()
)

customer_type_analysis["Cancellation_Rate_%"] = (
    customer_type_analysis["Cancelled"]
    / customer_type_analysis["Bookings"]
    * 100
)

print(
    customer_type_analysis.to_string(
        index=False,
        formatters={
            "Cancellation_Rate_%": "{:.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 7. HIGH-RISK BOOKING SEGMENT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("7. HIGH-RISK BOOKING SEGMENT")
print("=" * 70)

df["High_Response_Risk"] = (
    df["Response_Time_Min"] > 15
)

df["High_Distance_Risk"] = (
    df["Distance_km"] > 10
)

df["Peak_Risk"] = (
    df["Demand_Period"] == "Peak"
)

df["High_Risk_Flag"] = (
    df["High_Response_Risk"]
    & df["Peak_Risk"]
)

risk_analysis = (
    df.groupby("High_Risk_Flag")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean"),
        Avg_Distance=("Distance_km", "mean")
    )
    .reset_index()
)

risk_analysis["Cancellation_Rate_%"] = (
    risk_analysis["Cancelled"]
    / risk_analysis["Bookings"]
    * 100
)

print(
    risk_analysis.to_string(
        index=False,
        formatters={
            "Cancellation_Rate_%": "{:.2f}".format,
            "Avg_Response_Time": "{:.2f}".format,
            "Avg_Distance": "{:.2f}".format
        }
    )
)


# ------------------------------------------------------------
# 8. SAVE OUTPUTS
# ------------------------------------------------------------

response_analysis.to_csv(
    OUTPUT_DIR / "response_time_cancellation.csv",
    index=False
)

distance_analysis.to_csv(
    OUTPUT_DIR / "distance_cancellation.csv",
    index=False
)

period_analysis.to_csv(
    OUTPUT_DIR / "peak_vs_nonpeak_cancellation.csv",
    index=False
)

service_analysis.to_csv(
    OUTPUT_DIR / "service_cancellation.csv",
    index=False
)

city_analysis.to_csv(
    OUTPUT_DIR / "city_cancellation.csv",
    index=False
)

customer_type_analysis.to_csv(
    OUTPUT_DIR / "customer_type_cancellation.csv",
    index=False
)

risk_analysis.to_csv(
    OUTPUT_DIR / "high_risk_segment.csv",
    index=False
)


# ------------------------------------------------------------
# KEY INSIGHTS
# ------------------------------------------------------------

highest_response_risk = response_analysis.loc[
    response_analysis["Cancellation_Rate_%"].idxmax()
]

highest_distance_risk = distance_analysis.loc[
    distance_analysis["Cancellation_Rate_%"].idxmax()
]

highest_service_risk = service_analysis.iloc[0]

highest_city_risk = city_analysis.iloc[0]

print("\n" + "=" * 70)
print("KEY CANCELLATION DRIVER INSIGHTS")
print("=" * 70)

print(
    f"1. Highest response-time risk: "
    f"{highest_response_risk['Response_Time_Bucket']} "
    f"({highest_response_risk['Cancellation_Rate_%']:.2f}% cancellation)"
)

print(
    f"2. Highest distance risk: "
    f"{highest_distance_risk['Distance_Bucket']} "
    f"({highest_distance_risk['Cancellation_Rate_%']:.2f}% cancellation)"
)

print(
    f"3. Highest service-category cancellation: "
    f"{highest_service_risk['Service_Category']} "
    f"({highest_service_risk['Cancellation_Rate_%']:.2f}%)"
)

print(
    f"4. Highest city cancellation: "
    f"{highest_city_risk['City']} "
    f"({highest_city_risk['Cancellation_Rate_%']:.2f}%)"
)

print("\nReports saved inside the 'reports' folder.")

print("\n" + "=" * 70)
print("CANCELLATION DRIVER ANALYSIS COMPLETED")
print("=" * 70)