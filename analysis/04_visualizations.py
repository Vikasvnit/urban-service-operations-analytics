import os
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

df = pd.read_csv("data/processed/bookings_clean.csv")

os.makedirs("reports/charts", exist_ok=True)

# ------------------------------------------------------------
# Prepare fields
# ------------------------------------------------------------

service_analysis = (
    df.groupby("Service_Category")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum")
    )
)

service_analysis["Cancellation_Rate"] = (
    service_analysis["Cancelled"]
    / service_analysis["Bookings"]
    * 100
)

city_analysis = (
    df.groupby("City")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum")
    )
)

city_analysis["Cancellation_Rate"] = (
    city_analysis["Cancelled"]
    / city_analysis["Bookings"]
    * 100
)

time_analysis = (
    df.groupby("Time_Slot")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response_Time=("Response_Time_Min", "mean")
    )
)

time_analysis["Cancellation_Rate"] = (
    time_analysis["Cancelled"]
    / time_analysis["Bookings"]
    * 100
)

# ------------------------------------------------------------
# Chart 1 - Cancellation by Service
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

service_analysis["Cancellation_Rate"].sort_values(
    ascending=True
).plot(kind="barh")

plt.title("Cancellation Rate by Service Category")
plt.xlabel("Cancellation Rate (%)")
plt.ylabel("Service Category")
plt.tight_layout()

plt.savefig(
    "reports/charts/cancellation_by_service.png",
    dpi=200
)

plt.close()

# ------------------------------------------------------------
# Chart 2 - Cancellation by City
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

city_analysis["Cancellation_Rate"].sort_values(
    ascending=True
).plot(kind="barh")

plt.title("Cancellation Rate by City")
plt.xlabel("Cancellation Rate (%)")
plt.ylabel("City")
plt.tight_layout()

plt.savefig(
    "reports/charts/cancellation_by_city.png",
    dpi=200
)

plt.close()

# ------------------------------------------------------------
# Chart 3 - Cancellation by Time Slot
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

time_analysis["Cancellation_Rate"].plot(
    kind="bar"
)

plt.title("Cancellation Rate by Time Slot")
plt.xlabel("Time Slot")
plt.ylabel("Cancellation Rate (%)")
plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "reports/charts/cancellation_by_time.png",
    dpi=200
)

plt.close()

# ------------------------------------------------------------
# Chart 4 - Response Time vs Cancellation
# ------------------------------------------------------------

response_analysis = (
    df.groupby(
        pd.cut(
            df["Response_Time_Min"],
            bins=[0, 5, 10, 15, 20, 30],
            labels=[
                "0-5 min",
                "5-10 min",
                "10-15 min",
                "15-20 min",
                "20+ min"
            ]
        ),
        observed=False
    )
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum")
    )
)

response_analysis["Cancellation_Rate"] = (
    response_analysis["Cancelled"]
    / response_analysis["Bookings"]
    * 100
)

plt.figure(figsize=(10, 6))

response_analysis["Cancellation_Rate"].plot(
    kind="line",
    marker="o"
)

plt.title("Response Time vs Cancellation Rate")
plt.xlabel("Response Time")
plt.ylabel("Cancellation Rate (%)")
plt.grid(True)

plt.tight_layout()

plt.savefig(
    "reports/charts/response_time_vs_cancellation.png",
    dpi=200
)

plt.close()

# ------------------------------------------------------------
# Chart 5 - Bookings by Service
# ------------------------------------------------------------

service_analysis["Bookings"].sort_values(
    ascending=True
).plot(
    kind="barh",
    figsize=(10, 6)
)

plt.title("Booking Volume by Service Category")
plt.xlabel("Number of Bookings")
plt.ylabel("Service Category")
plt.tight_layout()

plt.savefig(
    "reports/charts/bookings_by_service.png",
    dpi=200
)

plt.close()

print("=" * 60)
print("VISUALIZATION GENERATION COMPLETED")
print("=" * 60)

print("\nCharts created:")
print("1. cancellation_by_service.png")
print("2. cancellation_by_city.png")
print("3. cancellation_by_time.png")
print("4. response_time_vs_cancellation.png")
print("5. bookings_by_service.png")

print("\nSaved in: reports/charts/")