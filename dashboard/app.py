import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# URBAN SERVICE OPERATIONS DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Urban Service Operations",
    page_icon="🏠",
    layout="wide"
)

# ============================================================
# LOAD DATA
# ============================================================

BOOKINGS_FILE = "data/processed/bookings_clean.csv"
CAPACITY_FILE = "reports/capacity_pressure_analysis.csv"

df = pd.read_csv(BOOKINGS_FILE)
capacity_df = pd.read_csv(CAPACITY_FILE)

df["Booking_Date"] = pd.to_datetime(df["Booking_Date"])

# ============================================================
# TIME SLOT ORDER
# ============================================================

time_order = [
    "8-10 AM",
    "10-12 PM",
    "12-2 PM",
    "2-4 PM",
    "4-6 PM",
    "6-8 PM",
    "8-10 PM"
]

# ============================================================
# HEADER
# ============================================================

st.title("Urban Service Operations Dashboard")

st.markdown(
    """
    **Operations analytics dashboard for a home-service marketplace**

    Monitor booking demand, cancellation risk, response performance,
    customer experience and capacity pressure.
    """
)

st.divider()

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

# City
city_options = sorted(df["City"].dropna().unique())

selected_cities = st.sidebar.multiselect(
    "City",
    city_options,
    default=city_options
)

# Service
service_options = sorted(
    df["Service_Category"].dropna().unique()
)

selected_services = st.sidebar.multiselect(
    "Service Category",
    service_options,
    default=service_options
)

# Booking status
status_options = sorted(
    df["Booking_Status"].dropna().unique()
)

selected_statuses = st.sidebar.multiselect(
    "Booking Status",
    status_options,
    default=status_options
)

# Time slot
selected_time_slots = st.sidebar.multiselect(
    "Time Slot",
    time_order,
    default=time_order
)

# ============================================================
# FILTER BOOKING DATA
# ============================================================

filtered_df = df[
    df["City"].isin(selected_cities)
    & df["Service_Category"].isin(selected_services)
    & df["Booking_Status"].isin(selected_statuses)
    & df["Time_Slot"].isin(selected_time_slots)
].copy()

# Filter capacity data
filtered_capacity = capacity_df[
    capacity_df["City"].isin(selected_cities)
    & capacity_df["Primary_Service"].isin(selected_services)
].copy()

# ============================================================
# KPI CALCULATIONS
# ============================================================

total_bookings = len(filtered_df)

completed_bookings = (
    filtered_df["Booking_Status"] == "Completed"
).sum()

cancelled_bookings = (
    filtered_df["Booking_Status"] == "Cancelled"
).sum()

rescheduled_bookings = (
    filtered_df["Booking_Status"] == "Rescheduled"
).sum()

completion_rate = (
    completed_bookings / total_bookings * 100
    if total_bookings > 0
    else 0
)

cancellation_rate = (
    cancelled_bookings / total_bookings * 100
    if total_bookings > 0
    else 0
)

completed_revenue = filtered_df.loc[
    filtered_df["Booking_Status"] == "Completed",
    "Service_Price"
].sum()

average_order_value = filtered_df.loc[
    filtered_df["Booking_Status"] == "Completed",
    "Service_Price"
].mean()

average_response_time = filtered_df[
    "Response_Time_Min"
].mean()

average_rating = filtered_df[
    "Customer_Rating"
].mean()

# ============================================================
# EXECUTIVE KPI SECTION
# ============================================================

st.subheader("Executive Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Bookings",
    f"{total_bookings:,}"
)

c2.metric(
    "Completion Rate",
    f"{completion_rate:.2f}%"
)

c3.metric(
    "Cancellation Rate",
    f"{cancellation_rate:.2f}%"
)

c4.metric(
    "Completed Revenue",
    f"₹{completed_revenue:,.0f}"
)

c5, c6, c7, c8 = st.columns(4)

c5.metric(
    "Completed Bookings",
    f"{completed_bookings:,}"
)

c6.metric(
    "Avg Response Time",
    f"{average_response_time:.2f} min"
)

c7.metric(
    "Avg Customer Rating",
    f"{average_rating:.2f}"
)

c8.metric(
    "Average Order Value",
    f"₹{average_order_value:,.0f}"
)

st.divider()

# ============================================================
# SERVICE PERFORMANCE
# ============================================================

st.subheader("Service Performance")

service_data = (
    filtered_df
    .groupby("Service_Category")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum")
    )
    .reset_index()
)

service_data["Cancellation_Rate"] = (
    service_data["Cancelled"]
    / service_data["Bookings"]
    * 100
)

col1, col2 = st.columns(2)

with col1:

    booking_chart = service_data.sort_values(
        "Bookings",
        ascending=True
    )

    fig = px.bar(
        booking_chart,
        x="Bookings",
        y="Service_Category",
        orientation="h",
        title="Booking Volume by Service"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    cancellation_chart = service_data.sort_values(
        "Cancellation_Rate",
        ascending=True
    )

    fig = px.bar(
        cancellation_chart,
        x="Cancellation_Rate",
        y="Service_Category",
        orientation="h",
        title="Cancellation Rate by Service",
        labels={
            "Cancellation_Rate":
            "Cancellation Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ============================================================
# CITY PERFORMANCE
# ============================================================

st.subheader("City Performance")

city_data = (
    filtered_df
    .groupby("City")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response=("Response_Time_Min", "mean"),
        Avg_Rating=("Customer_Rating", "mean")
    )
    .reset_index()
)

city_data["Cancellation_Rate"] = (
    city_data["Cancelled"]
    / city_data["Bookings"]
    * 100
)

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        city_data.sort_values(
            "Cancellation_Rate",
            ascending=True
        ),
        x="Cancellation_Rate",
        y="City",
        orientation="h",
        title="Cancellation Rate by City",
        labels={
            "Cancellation_Rate":
            "Cancellation Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.bar(
        city_data.sort_values(
            "Avg_Response",
            ascending=True
        ),
        x="Avg_Response",
        y="City",
        orientation="h",
        title="Average Response Time by City",
        labels={
            "Avg_Response":
            "Response Time (minutes)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ============================================================
# TIME-SLOT PERFORMANCE
# ============================================================

st.subheader("Demand & Time-Slot Performance")

time_data = (
    filtered_df
    .groupby("Time_Slot")
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum"),
        Avg_Response=("Response_Time_Min", "mean")
    )
    .reset_index()
)

time_data["Cancellation_Rate"] = (
    time_data["Cancelled"]
    / time_data["Bookings"]
    * 100
)

time_data["Sort_Order"] = (
    time_data["Time_Slot"].map(
        {slot: i for i, slot in enumerate(time_order)}
    )
)

time_data = time_data.sort_values(
    "Sort_Order"
)

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        time_data,
        x="Time_Slot",
        y="Bookings",
        title="Booking Demand by Time Slot"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.line(
        time_data,
        x="Time_Slot",
        y="Cancellation_Rate",
        markers=True,
        title="Cancellation Rate by Time Slot",
        labels={
            "Cancellation_Rate":
            "Cancellation Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ============================================================
# RESPONSE TIME ANALYSIS
# ============================================================

st.subheader("Response Time & Cancellation Risk")

response_df = filtered_df.copy()

response_df["Response_Time_Bucket"] = pd.cut(
    response_df["Response_Time_Min"],
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

response_data = (
    response_df
    .groupby(
        "Response_Time_Bucket",
        observed=False
    )
    .agg(
        Bookings=("Booking_ID", "count"),
        Cancelled=("Cancelled_Flag", "sum")
    )
    .reset_index()
)

response_data["Cancellation_Rate"] = (
    response_data["Cancelled"]
    / response_data["Bookings"]
    * 100
)

fig = px.line(
    response_data,
    x="Response_Time_Bucket",
    y="Cancellation_Rate",
    markers=True,
    title="Response Time vs Cancellation Rate",
    labels={
        "Response_Time_Bucket":
        "Response Time",
        "Cancellation_Rate":
        "Cancellation Rate (%)"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ============================================================
# CANCELLATION REASONS
# ============================================================

st.subheader("Cancellation Reasons")

reason_data = (
    filtered_df[
        filtered_df["Booking_Status"] == "Cancelled"
    ]
    .groupby("Cancellation_Reason")
    .size()
    .reset_index(
        name="Cancellations"
    )
    .sort_values(
        "Cancellations",
        ascending=True
    )
)

fig = px.bar(
    reason_data,
    x="Cancellations",
    y="Cancellation_Reason",
    orientation="h",
    title="Why Customers Cancel"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ============================================================
# CAPACITY PRESSURE
# ============================================================

st.divider()

st.subheader("Capacity Pressure")

st.markdown(
    """
    Capacity pressure combines professional utilization with
    peak-period cancellation and response-time indicators.
    """
)

if len(filtered_capacity) > 0:

    display_capacity = filtered_capacity[
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
    ].copy()

    display_capacity = display_capacity.sort_values(
        "Capacity_Pressure_Score",
        ascending=False
    )

    st.dataframe(
        display_capacity,
        use_container_width=True,
        hide_index=True
    )

    # Pressure distribution
    pressure_counts = (
        display_capacity[
            "Pressure_Level"
        ]
        .value_counts()
        .reset_index()
    )

    pressure_counts.columns = [
        "Pressure_Level",
        "Count"
    ]

    fig = px.bar(
        pressure_counts,
        x="Pressure_Level",
        y="Count",
        title="Capacity Pressure Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info(
        "No capacity data available for the selected filters."
    )

# ============================================================
# MANAGEMENT INSIGHTS
# ============================================================

st.divider()

st.subheader("Management Insights")

# Highest-risk service
if len(service_data) > 0:

    highest_service = service_data.loc[
        service_data["Cancellation_Rate"].idxmax()
    ]

    st.write(
        f"**Highest-risk service:** "
        f"{highest_service['Service_Category']} "
        f"has a cancellation rate of "
        f"{highest_service['Cancellation_Rate']:.2f}%."
    )

# Highest-risk city
if len(city_data) > 0:

    highest_city = city_data.loc[
        city_data["Cancellation_Rate"].idxmax()
    ]

    st.write(
        f"**Highest-risk city:** "
        f"{highest_city['City']} "
        f"has a cancellation rate of "
        f"{highest_city['Cancellation_Rate']:.2f}%."
    )

# Highest-risk slot
if len(time_data) > 0:

    highest_slot = time_data.loc[
        time_data["Cancellation_Rate"].idxmax()
    ]

    st.write(
        f"**Highest-risk time slot:** "
        f"{highest_slot['Time_Slot']} "
        f"has a cancellation rate of "
        f"{highest_slot['Cancellation_Rate']:.2f}%."
    )

# Highest response-time risk
if len(response_data) > 0:

    highest_response = response_data.loc[
        response_data["Cancellation_Rate"].idxmax()
    ]

    st.write(
        f"**Response-time risk:** "
        f"{highest_response['Response_Time_Bucket']} "
        f"bookings show a "
        f"{highest_response['Cancellation_Rate']:.2f}% "
        f"cancellation rate."
    )

# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("Recommended Actions")

st.markdown(
    """
**1. Reduce professional response time**  
Introduce faster assignment/escalation for bookings that remain
unaccepted beyond a defined threshold.

**2. Increase evening capacity**  
Redistribute or add professionals during the 4–10 PM demand window.

**3. Improve slot availability**  
Use demand forecasts to allocate professionals to high-pressure
city-service combinations before peak periods.

**4. Prioritize high-risk categories**  
Focus operational improvement efforts on service categories with
persistently high cancellation rates.

**5. Monitor capacity pressure continuously**  
Use utilization and cancellation indicators together to identify
areas requiring supply rebalancing.
"""
)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Urban Service Operations Analytics & Optimization System | "
    "Synthetic dataset created for portfolio demonstration"
)