import os

import pandas as pd
import mysql.connector


# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="flight_assistant"
    )

# Load your flight data
try:
    db_connection = get_db_connection()
    print("db connection", db_connection)
    flights_df = pd.read_sql("SELECT * FROM flights1", db_connection)
    # print(flights_df)
    flights_df["departureDate"] = pd.to_datetime(flights_df["departureDate"])
except Exception as e:
    print(f"Error loading flight data: {e}")

# Load flights preferences data
try:
    db_connection = get_db_connection()
    preferences_df = pd.read_sql("SELECT * FROM preferences1", db_connection)
    # print(preferences_df)
except Exception as e:
    print(f"Error loading preferences data: {e}")

# Load traveler references data
try:
    db_connection = get_db_connection()
    references_df = pd.read_sql("SELECT * FROM flight_assistant.references1", db_connection)
    # print(references_df)
except Exception as e:
    print(f"Error loading references data: {e}")