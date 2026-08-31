import os
import numpy as np
import pandas as pd

# -----------------------------
# 1. Project folders
# -----------------------------
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# Reproducibility
np.random.seed(42)

# -----------------------------
# 2. Basic configuration
# -----------------------------
N = 25000

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

time_slots = [
    "8-10 AM",
    "10-12 PM",
    "12-2 PM",
    "2-4 PM",
    "4-6 PM",
    "6-8 PM",
    "8-10 PM"
]

payment_methods = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Cash"
]

customer_types = [
    "New",
    "Returning"
]

booking_statuses = [
    "Completed",
    "Cancelled",
    "Rescheduled"
]

cancellation_reasons = [
    "Customer Changed Mind",
    "Professional Unavailable",
    "Long Response Time",
    "Price Too High",
    "Slot Not Available",
    "Distance Too Far"
]

# -----------------------------
# 3. Generate basic fields
# -----------------------------
booking_ids = [f"B{i:05d}" for i in range(1, N + 1)]
customer_ids = [f"C{np.random.randint(1000, 9999)}" for _ in range(N)]
professional_ids = [f"P{np.random.randint(100, 999)}" for _ in range(N)]

city = np.random.choice(
    cities,
    N,
    p=[0.15, 0.16, 0.20, 0.19, 0.17, 0.13]
)

service = np.random.choice(
    services,
    N,
    p=[0.22, 0.18, 0.16, 0.14, 0.15, 0.15]
)

time_slot = np.random.choice(
    time_slots,
    N,
    p=[0.10, 0.13, 0.14, 0.14, 0.17, 0.20, 0.12]
)

customer_type = np.random.choice(
    customer_types,
    N,
    p=[0.35, 0.65]
)

payment_method = np.random.choice(
    payment_methods,
    N,
    p=[0.55, 0.20, 0.15, 0.10]
)

booking_date = pd.date_range(
    start="2026-01-01",
    end="2026-06-30",
    periods=N
)

# -----------------------------
# 4. Service price
# -----------------------------
base_prices = {
    "Cleaning": 700,
    "Salon": 900,
    "AC Repair": 1200,
    "Plumbing": 650,
    "Electrician": 600,
    "Appliance Repair": 1000
}

service_price = np.array([
    base_prices[s] for s in service
]) + np.random.normal(0, 120, N)

service_price = np.maximum(service_price, 250).round(0)

# -----------------------------
# 5. Distance
# -----------------------------
distance = np.random.gamma(
    shape=2.2,
    scale=2.0,
    size=N
)

distance = np.clip(distance, 0.5, 15).round(2)

# -----------------------------
# 6. Response time
# -----------------------------
# Peak hours have slightly longer response times
peak_hour = np.isin(
    time_slot,
    ["4-6 PM", "6-8 PM", "8-10 PM"]
)

response_time = np.random.normal(7, 2.5, N)

response_time += np.where(peak_hour, 3.5, 0)
response_time += distance * 0.45

response_time = np.clip(response_time, 1, 30).round(1)

# -----------------------------
# 7. Service duration
# -----------------------------
duration_ranges = {
    "Cleaning": (60, 150),
    "Salon": (45, 120),
    "AC Repair": (60, 180),
    "Plumbing": (45, 150),
    "Electrician": (40, 120),
    "Appliance Repair": (60, 180)
}

service_duration = np.array([
    np.random.randint(
        duration_ranges[s][0],
        duration_ranges[s][1] + 1
    )
    for s in service
])

# -----------------------------
# 8. Cancellation probability
# -----------------------------
cancel_prob = np.full(N, 0.07)

# Longer response time -> higher cancellation
cancel_prob += np.where(response_time > 12, 0.08, 0)
cancel_prob += np.where(response_time > 18, 0.08, 0)

# Longer distance -> higher cancellation
cancel_prob += np.where(distance > 8, 0.05, 0)

# Peak demand -> higher cancellation
cancel_prob += np.where(peak_hour, 0.04, 0)

# Certain services have slightly higher cancellation
cancel_prob += np.where(
    service == "AC Repair",
    0.03,
    0
)

cancel_prob = np.clip(cancel_prob, 0.02, 0.35)

random_values = np.random.random(N)

is_cancelled = random_values < cancel_prob

# Rescheduled bookings among non-cancelled bookings
is_rescheduled = (
    (~is_cancelled) &
    (np.random.random(N) < 0.05)
)

booking_status = np.where(
    is_cancelled,
    "Cancelled",
    np.where(
        is_rescheduled,
        "Rescheduled",
        "Completed"
    )
)

# -----------------------------
# 9. Cancellation reason
# -----------------------------
cancellation_reason = []

for i in range(N):
    if booking_status[i] == "Cancelled":

        if response_time[i] > 15:
            reason = "Long Response Time"

        elif distance[i] > 8:
            reason = "Distance Too Far"

        elif peak_hour[i]:
            reason = "Slot Not Available"

        else:
            reason = np.random.choice(
                cancellation_reasons
            )

        cancellation_reason.append(reason)

    else:
        cancellation_reason.append("None")

# -----------------------------
# 10. Ratings
# -----------------------------
customer_rating = np.full(N, np.nan)

for i in range(N):
    if booking_status[i] == "Completed":

        rating = 4.6

        # Poor response time affects experience
        rating -= max(response_time[i] - 8, 0) * 0.03

        # Distance can slightly affect experience
        rating -= max(distance[i] - 8, 0) * 0.02

        rating += np.random.normal(0, 0.35)

        customer_rating[i] = np.clip(
            rating,
            1,
            5
        )

customer_rating = np.round(customer_rating, 1)

# -----------------------------
# 11. Professional rating
# -----------------------------
professional_rating = np.round(
    np.clip(
        np.random.normal(4.4, 0.4, N),
        1,
        5
    ),
    1
)

# -----------------------------
# 12. Create DataFrame
# -----------------------------
df = pd.DataFrame({
    "Booking_ID": booking_ids,
    "Customer_ID": customer_ids,
    "Professional_ID": professional_ids,
    "City": city,
    "Service_Category": service,
    "Booking_Date": booking_date,
    "Time_Slot": time_slot,
    "Service_Price": service_price.astype(int),
    "Distance_km": distance,
    "Response_Time_Min": response_time,
    "Service_Duration_Min": service_duration,
    "Booking_Status": booking_status,
    "Cancellation_Reason": cancellation_reason,
    "Customer_Rating": customer_rating,
    "Professional_Rating": professional_rating,
    "Customer_Type": customer_type,
    "Payment_Method": payment_method
})

# -----------------------------
# 13. Save dataset
# -----------------------------
output_file = "data/raw/bookings_raw.csv"

df.to_csv(
    output_file,
    index=False
)

# -----------------------------
# 14. Print summary
# -----------------------------
print("\n========================================")
print("URBAN SERVICE OPERATIONS DATASET")
print("========================================")
print(f"Total bookings: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_file}")

print("\nBooking Status:")
print(df["Booking_Status"].value_counts())

print("\nService Categories:")
print(df["Service_Category"].value_counts())

print("\nCities:")
print(df["City"].value_counts())

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset generation completed successfully!")