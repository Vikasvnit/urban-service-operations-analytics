import sqlite3
import os

DATABASE_FILE = "urban_operations.db"
SQL_FILE = "sql/analysis_queries.sql"
OUTPUT_FILE = "reports/sql_results.txt"

os.makedirs("reports", exist_ok=True)

# Connect to database
connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

# Read SQL file
with open(SQL_FILE, "r", encoding="utf-8") as file:
    sql_content = file.read()

# Split into individual queries
queries = [
    query.strip()
    for query in sql_content.split(";")
    if query.strip()
]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as output:

    for number, query in enumerate(
        queries,
        start=1
    ):

        try:

            cursor.execute(query)

            results = cursor.fetchall()

            columns = [
                description[0]
                for description in cursor.description
            ]

            output.write(
                f"\n{'=' * 70}\n"
            )

            output.write(
                f"QUERY {number}\n"
            )

            output.write(
                f"{'=' * 70}\n"
            )

            output.write(
                "\t".join(columns) + "\n"
            )

            for row in results:

                output.write(
                    "\t".join(
                        str(value)
                        for value in row
                    ) + "\n"
                )

        except Exception as error:

            output.write(
                f"\nQUERY {number} ERROR:\n"
            )

            output.write(
                str(error) + "\n"
            )

connection.close()

print("=" * 60)
print("SQL ANALYSIS COMPLETED")
print("=" * 60)

print("\nResults saved to:")
print(OUTPUT_FILE)