import os
import pandas as pd
import numpy as np

# ============================================================
# URBAN SERVICE OPERATIONS - OPERATIONS ANALYSIS
# ============================================================

INPUT_FILE = "data/processed/bookings_clean.csv"

os.makedirs("reports", exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# Convert date
df["Booking_Date"] = pd.to_datetime(df["Booking_Date"])

print("=" * 70)
print("URBAN SERVICE OPERATIONS - OPERATIONS ANALYSIS")
print("=" * 70)

# ============================================================
# 1. OVERALL KPIs
# ============================================================

total_bookings = len(df)

completed = (df["Booking_Status"] == "Completed").sum()
cancelled = (df["Booking_Status"] == "Cancelled").sum()
rescheduled = (df["Booking_Status"] == "Rescheduled").sum()

completion_rate = completed / total_bookings * 100
cancellation_rate = cancelled / total_bookings * 100
reschedule_rate = rescheduled / total_bookings * 100

average_rating = df["Customer_Rating"].mean()
average_response = df["Response_Time_Min"].mean()
average_distance = df["Distance_km"].mean()

completed_revenue = df.loc[
    df["Booking_Status"] == "Completed",
    "Service_Price"
].sum()

average_completed_order_value = df.loc[
    df["Booking_Status"] == "Completed",
    "Service_Price"
].mean()

print("\n1. OVERALL KPIs")
print("-" * 40)
print(f"Total Bookings           : {total_bookings:,}")
print(f"Completed Bookings       : {completed:,}")
print(f"Cancelled Bookings      : {cancelled:,}")
print(f"Rescheduled Bookings    : {rescheduled:,}")
print(f"Completion Rate         : {completion_rate:.2f}%")
print(f"Cancellation Rate       : {cancellation_rate:.2f}%")
print(f"Reschedule Rate         : {reschedule_rate:.2f}%")
print(f"Average Customer Rating : {average_rating:.2f}")
print(f"Average Response Time   : {average_response:.2f} min")
print(f"Average Distance        : {average_distance:.2f} km")
print(f"Completed Revenue       : ₹{completed_revenue:,.0f}")
print(f"Average Order Value     : ₹{average_completed_order_value:,.2f}")


# ============================================================
# 2. SERVICE CATEGORY ANALYSIS
# ============================================================

service_analysis = (
    df.groupby("Service_Category")
    .agg(
        Bookings=("Booking_ID", "count"),
        Completed=("Completed_Flag", "sum"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Price=("Service_Price", "mean"),
        Avg_Response_Time=("Response_Time_Min", "mean"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
)

service_analysis["Completion_Rate_%"] = (
    service_analysis["Completed"]
    / service_analysis["Bookings"]
    * 100
)

service_analysis["Cancellation_Rate_%"] = (
    service_analysis["Cancelled"]
    / service_analysis["Bookings"]
    * 100
)

service_analysis["Revenue"] = (
    df[df["Booking_Status"] == "Completed"]
    .groupby("Service_Category")["Service_Price"]
    .sum()
    .reindex(service_analysis["Service_Category"])
    .fillna(0)
    .values
)

service_analysis = service_analysis.sort_values(
    "Cancellation_Rate_%",
    ascending=False
)

print("\n2. SERVICE CATEGORY ANALYSIS")
print("-" * 40)
print(
    service_analysis[
        [
            "Service_Category",
            "Bookings",
            "Cancellation_Rate_%",
            "Completion_Rate_%",
            "Avg_Response_Time",
            "Avg_Rating",
            "Revenue"
        ]
    ].to_string(index=False)
)

service_analysis.to_csv(
    "reports/service_analysis.csv",
    index=False
)


# ============================================================
# 3. CITY ANALYSIS
# ============================================================

city_analysis = (
    df.groupby("City")
    .agg(
        Bookings=("Booking_ID", "count"),
        Completed=("Completed_Flag", "sum"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean"),
        Avg_Distance=("Distance_km", "mean"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
)

city_analysis["Cancellation_Rate_%"] = (
    city_analysis["Cancelled"]
    / city_analysis["Bookings"]
    * 100
)

city_analysis["Completion_Rate_%"] = (
    city_analysis["Completed"]
    / city_analysis["Bookings"]
    * 100
)

city_analysis = city_analysis.sort_values(
    "Cancellation_Rate_%",
    ascending=False
)

print("\n3. CITY ANALYSIS")
print("-" * 40)
print(
    city_analysis[
        [
            "City",
            "Bookings",
            "Cancellation_Rate_%",
            "Completion_Rate_%",
            "Avg_Response_Time",
            "Avg_Distance",
            "Avg_Rating"
        ]
    ].to_string(index=False)
)

city_analysis.to_csv(
    "reports/city_analysis.csv",
    index=False
)


# ============================================================
# 4. TIME SLOT ANALYSIS
# ============================================================

time_analysis = (
    df.groupby("Time_Slot")
    .agg(
        Bookings=("Booking_ID", "count"),
        Completed=("Completed_Flag", "sum"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
)

time_analysis["Cancellation_Rate_%"] = (
    time_analysis["Cancelled"]
    / time_analysis["Bookings"]
    * 100
)

time_analysis["Completion_Rate_%"] = (
    time_analysis["Completed"]
    / time_analysis["Bookings"]
    * 100
)

print("\n4. TIME SLOT ANALYSIS")
print("-" * 40)
print(
    time_analysis[
        [
            "Time_Slot",
            "Bookings",
            "Cancellation_Rate_%",
            "Completion_Rate_%",
            "Avg_Response_Time",
            "Avg_Rating"
        ]
    ].to_string(index=False)
)

time_analysis.to_csv(
    "reports/time_slot_analysis.csv",
    index=False
)


# ============================================================
# 5. RESPONSE TIME VS CANCELLATION
# ============================================================

df["Response_Time_Bucket"] = pd.cut(
    df["Response_Time_Min"],
    bins=[0, 5, 10, 15, 20, 30],
    labels=[
        "0-5 min",
        "5-10 min",
        "10-15 min",
        "15-20 min",
        "20+ min"
    ],
    include_lowest=True
)

response_analysis = (
    df.groupby("Response_Time_Bucket", observed=False)
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum")
    )
    .reset_index()
)

response_analysis["Cancellation_Rate_%"] = (
    response_analysis["Cancelled"]
    / response_analysis["Bookings"]
    * 100
)

print("\n5. RESPONSE TIME VS CANCELLATION")
print("-" * 40)
print(
    response_analysis.to_string(index=False)
)

response_analysis.to_csv(
    "reports/response_time_analysis.csv",
    index=False
)


# ============================================================
# 6. CUSTOMER TYPE ANALYSIS
# ============================================================

customer_analysis = (
    df.groupby("Customer_Type")
    .agg(
        Bookings=("Booking_ID", "count"),
        Completed=("Completed_Flag", "sum"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Order_Value=("Service_Price", "mean"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
)

customer_analysis["Cancellation_Rate_%"] = (
    customer_analysis["Cancelled"]
    / customer_analysis["Bookings"]
    * 100
)

customer_analysis["Completion_Rate_%"] = (
    customer_analysis["Completed"]
    / customer_analysis["Bookings"]
    * 100
)

print("\n6. CUSTOMER TYPE ANALYSIS")
print("-" * 40)
print(customer_analysis.to_string(index=False))

customer_analysis.to_csv(
    "reports/customer_type_analysis.csv",
    index=False
)


# ============================================================
# 7. CANCELLATION REASONS
# ============================================================

cancellation_reasons = (
    df[df["Booking_Status"] == "Cancelled"]
    ["Cancellation_Reason"]
    .value_counts()
    .reset_index()
)

cancellation_reasons.columns = [
    "Cancellation_Reason",
    "Cancelled_Bookings"
]

cancellation_reasons["Percentage_%"] = (
    cancellation_reasons["Cancelled_Bookings"]
    / cancellation_reasons["Cancelled_Bookings"].sum()
    * 100
)

print("\n7. CANCELLATION REASONS")
print("-" * 40)
print(cancellation_reasons.to_string(index=False))

cancellation_reasons.to_csv(
    "reports/cancellation_reasons.csv",
    index=False
)


# ============================================================
# 8. PEAK VS NON-PEAK ANALYSIS
# ============================================================

peak_slots = [
    "4-6 PM",
    "6-8 PM",
    "8-10 PM"
]

df["Demand_Period"] = np.where(
    df["Time_Slot"].isin(peak_slots),
    "Peak",
    "Non-Peak"
)

peak_analysis = (
    df.groupby("Demand_Period")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
)

peak_analysis["Cancellation_Rate_%"] = (
    peak_analysis["Cancelled"]
    / peak_analysis["Bookings"]
    * 100
)

print("\n8. PEAK VS NON-PEAK")
print("-" * 40)
print(peak_analysis.to_string(index=False))

peak_analysis.to_csv(
    "reports/peak_analysis.csv",
    index=False
)


# ============================================================
# 9. AUTOMATIC KEY INSIGHTS
# ============================================================

highest_cancel_service = service_analysis.iloc[0]["Service_Category"]
highest_cancel_service_rate = service_analysis.iloc[0]["Cancellation_Rate_%"]

highest_cancel_city = city_analysis.iloc[0]["City"]
highest_cancel_city_rate = city_analysis.iloc[0]["Cancellation_Rate_%"]

highest_cancel_slot = time_analysis.sort_values(
    "Cancellation_Rate_%",
    ascending=False
).iloc[0]

slow_response_bucket = response_analysis.iloc[-1]

print("\n" + "=" * 70)
print("KEY OPERATIONAL INSIGHTS")
print("=" * 70)

print(
    f"\n1. Highest cancellation service: "
    f"{highest_cancel_service} "
    f"({highest_cancel_service_rate:.2f}%)"
)

print(
    f"2. Highest cancellation city: "
    f"{highest_cancel_city} "
    f"({highest_cancel_city_rate:.2f}%)"
)

print(
    f"3. Highest cancellation time slot: "
    f"{highest_cancel_slot['Time_Slot']} "
    f"({highest_cancel_slot['Cancellation_Rate_%']:.2f}%)"
)

print(
    f"4. Response-time bucket with highest cancellation: "
    f"{slow_response_bucket['Response_Time_Bucket']} "
    f"({slow_response_bucket['Cancellation_Rate_%']:.2f}%)"
)

# ============================================================
# 10. SAVE SUMMARY REPORT
# ============================================================

with open(
    "reports/operations_insights.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write("URBAN SERVICE OPERATIONS - INSIGHTS\n")
    file.write("=" * 50 + "\n\n")

    file.write(
        f"Total bookings: {total_bookings:,}\n"
    )

    file.write(
        f"Completion rate: {completion_rate:.2f}%\n"
    )

    file.write(
        f"Cancellation rate: {cancellation_rate:.2f}%\n"
    )

    file.write(
        f"Average response time: {average_response:.2f} minutes\n"
    )

    file.write(
        f"Average customer rating: {average_rating:.2f}\n"
    )

    file.write(
        f"Completed revenue: ₹{completed_revenue:,.0f}\n\n"
    )

    file.write(
        f"Highest cancellation service: "
        f"{highest_cancel_service} "
        f"({highest_cancel_service_rate:.2f}%)\n"
    )

    file.write(
        f"Highest cancellation city: "
        f"{highest_cancel_city} "
        f"({highest_cancel_city_rate:.2f}%)\n"
    )

    file.write(
        f"Highest cancellation time slot: "
        f"{highest_cancel_slot['Time_Slot']} "
        f"({highest_cancel_slot['Cancellation_Rate_%']:.2f}%)\n"
    )

print("\nAnalysis completed successfully!")
print("Reports saved inside the 'reports' folder.")