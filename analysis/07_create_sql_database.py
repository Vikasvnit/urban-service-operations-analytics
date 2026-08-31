import sqlite3
import pandas as pd

# ============================================================
# CREATE URBAN OPERATIONS SQL DATABASE
# ============================================================

bookings_file = "data/processed/bookings_with_professionals.csv"
professionals_file = "data/processed/professional_master.csv"
database_file = "urban_operations.db"

print("=" * 60)
print("CREATING URBAN OPERATIONS DATABASE")
print("=" * 60)

# Load datasets
bookings = pd.read_csv(bookings_file)
professionals = pd.read_csv(professionals_file)

# Create / replace SQLite database
connection = sqlite3.connect(database_file)

# Create bookings table
bookings.to_sql(
    "bookings",
    connection,
    if_exists="replace",
    index=False
)

# Create professionals table
professionals.to_sql(
    "professionals",
    connection,
    if_exists="replace",
    index=False
)

# Verify row counts
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM bookings")
booking_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM professionals")
professional_count = cursor.fetchone()[0]

connection.close()

print("\nDatabase created successfully!")
print(f"Database: {database_file}")
print(f"Bookings table: {booking_count:,} rows")
print(f"Professionals table: {professional_count:,} rows")

print("\nTables created:")
print("1. bookings")
print("2. professionals")

print("\n" + "=" * 60)
print("SQL DATABASE CREATION COMPLETED")
print("=" * 60)