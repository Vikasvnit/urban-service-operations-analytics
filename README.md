# Urban Service Operations Analytics

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Streamlit-red?logo=streamlit)](https://urban-service-operations-analytics.streamlit.app)

An operations analytics and capacity optimization dashboard for a home-service marketplace.

## 📊 Project Overview

This project analyzes booking operations across multiple cities and service categories to identify:

- Booking demand and service trends
- Cancellation patterns and drivers
- Professional capacity pressure
- Customer experience and ratings
- Response-time performance
- High-risk customer and booking segments
- Peak booking periods
- Service and city-level operational performance

The project combines **Python, SQL, Pandas, data analysis, and Streamlit** to transform raw booking data into actionable operational insights.

## 🎯 Business Objective

The objective is to help a home-service marketplace understand its operational performance and identify areas where capacity, response time, cancellations, and customer experience can be improved.

The dashboard provides an interactive view of key operational KPIs and allows users to filter results by:

- City
- Service Category
- Booking Status
- Time Slot

## 🏙️ Cities Covered

- Bengaluru
- Delhi
- Hyderabad
- Mumbai
- Nagpur
- Pune

## 🛠️ Service Categories

- AC Repair
- Appliance Repair
- Cleaning
- Electrician
- Plumbing
- Salon

## 📈 Key KPIs

The dashboard tracks important operational metrics including:

- Total Bookings
- Completed Bookings
- Completion Rate
- Cancellation Rate
- Completed Revenue
- Average Response Time
- Average Customer Rating
- Average Order Value

## 🔍 Analysis Performed

The project includes analysis of:

### Booking & Service Performance
Analysis of booking volume and performance across different services and cities.

### Cancellation Analysis
Identification of cancellation patterns by:

- Service
- City
- Time
- Customer type
- Cancellation reason
- Response time
- Booking characteristics

### Capacity Analysis
Analysis of professional availability and capacity pressure to identify periods and services where operational capacity may be constrained.

### Response Time Analysis
Evaluation of response times and their relationship with booking outcomes and cancellations.

### Customer Analysis
Analysis of customer types and their booking and cancellation behavior.

### Peak Demand Analysis
Identification of peak booking periods and time slots to support better workforce and capacity planning.

## 📊 Dashboard

The project includes an interactive **Streamlit dashboard** for exploring operational performance.

Users can dynamically filter the analysis by city, service category, booking status, and time slot.

The dashboard provides an executive overview followed by detailed service and operational performance analysis.

## 🧰 Tech Stack

- **Python**
- **Pandas**
- **NumPy**
- **Matplotlib**
- **Streamlit**
- **SQL**
- **SQLite**
- **CSV**
- **Git & GitHub**

## 📁 Project Structure

```text
urban-service-operations-analytics/
│
├── analysis/
│   ├── 05_professional_capacity.py
│   ├── 06_capacity_pressure.py
│   ├── 07_cancellation_drivers.py
│   ├── 07_create_sql_database.py
│   └── 08_run_sql_analysis.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   │   └── bookings_raw.csv
│   │
│   └── processed/
│       ├── bookings_clean.csv
│       ├── bookings_with_professionals.csv
│       └── professional_master.csv
│
├── reports/
│   ├── charts/
│   ├── cancellation_reasons.csv
│   ├── capacity_pressure_analysis.csv
│   ├── city_analysis.csv
│   ├── city_cancellation.csv
│   ├── customer_type_analysis.csv
│   ├── customer_type_cancellation.csv
│   ├── distance_cancellation.csv
│   ├── high_risk_segment.csv
│   ├── operations_insights.txt
│   ├── peak_analysis.csv
│   ├── peak_vs_nonpeak_cancellation.csv
│   ├── professional_capacity.csv
│   ├── response_time_analysis.csv
│   ├── response_time_cancellation.csv
│   ├── service_analysis.csv
│   ├── service_cancellation.csv
│   ├── sql_results.txt
│   └── time_slot_analysis.csv
│
├── sql/
│   └── analysis_queries.sql
│
├── generate_data.py
├── requirements.txt
└── urban_operations.db
