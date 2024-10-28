import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import mysql.connector
from mysql.connector import Error
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("API_KEY")

# Initialize OpenAI model
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)


# Connect to the MySQL database
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def fetch_travelers(connection):
    """Fetch traveler data from the database."""
    query = "SELECT * FROM Travelers"  # Replace with your actual table name
    return pd.read_sql(query, connection)


def fetch_flights(connection):
    """Fetch flight data from the database."""
    query = "SELECT * FROM Flights"  # Replace with your actual table name
    return pd.read_sql(query, connection)


# Create database connection
connection = create_connection()

# Load flight and traveler data from the database
travelers_df = fetch_travelers(connection)
flights_df = fetch_flights(connection)


def get_user_preferences(traveler_id):
    """Get user preferences based on traveler ID."""
    traveler_data = travelers_df[travelers_df["id"] == traveler_id].iloc[0]
    preferences = {
        "id": traveler_data["id"],
        "home_airport": traveler_data["homeAirport"],
        "seat_preference": traveler_data["seatPreference"],
        "redressNumber": traveler_data["redressNumber"],
        "meal_preference": traveler_data["mealPreference"],
        "loyalty_program": traveler_data["loyaltyProgram"],
        "travel_companions": traveler_data["travelCompanions"],
        "accessibilityNeeds": traveler_data["accessibilityNeeds"],
    }
    return preferences


def filter_flights(preferences, from_airport, to_airport):
    """Filter flights based on user preferences and input airports."""
    matching_flights = flights_df[
        (flights_df["origin"] == from_airport)
        & (flights_df["destination"] == to_airport)
    ]

    # Check if seatPreference is available in the DataFrame and filter accordingly
    if "seatPreference" in flights_df.columns:
        matching_flights = matching_flights[
            (matching_flights.get("seatPreference") == preferences["seat_preference"])
            | (
                matching_flights.get("seatPreference").isnull()
                & pd.isnull(preferences["seat_preference"])
            )
        ]

    return matching_flights


def find_non_matching_flights(preferences, from_airport, to_airport):
    """Find non-matching flights based on user preferences."""
    non_matching_flights = flights_df[
        ~(
            (flights_df["origin"] == from_airport)
            & (flights_df["destination"] == to_airport)
            & (flights_df.get("seatPreference") == preferences["seat_preference"])
        )
    ]
    return non_matching_flights


# Streamlit UI
st.title("Flight Preference Filter")

# Default traveler ID
traveler_id = 1
preferences = get_user_preferences(traveler_id)

# User input for "from" and "to" airports
from_airport = st.text_input("Enter From Airport", "LAX")
to_airport = st.text_input("Enter To Airport", "DFW")

if st.button("Find Flights"):
    matching_flights = filter_flights(preferences, from_airport, to_airport)
    non_matching_flights = find_non_matching_flights(
        preferences, from_airport, to_airport
    )

    # Display user preferences
    st.subheader("User Preferences")
    st.write(f"ID: {preferences['id']}")
    st.write(f"Home Airport: {preferences['home_airport']}")
    st.write(f"Seat Preference: {preferences['seat_preference']}")
    st.write(f"Meal Preference: {preferences['meal_preference']}")
    st.write(f"Loyalty Program: {preferences['loyalty_program']}")
    st.write(f"Travel Companions: {preferences['travel_companions']}")

    # Display matching flights
    st.subheader("Matching Flights")
    if not matching_flights.empty:
        for _, flight in matching_flights.iterrows():
            # st.write(
            #     f"Flight Number: {flight['id']} | "
            #     f"From: {flight['origin']} To: {flight['destination']} | "
            #     f"Departure: {flight['departureDate']} | "
            #     f"Arrival: {flight['arrivalDate']} | "
            #     f"Duration: {flight['totalTimeHours']}h {flight['totalTimeMinutes']}m"
            #     f"Airline name:{flight['airline_name']}"
            #     f"image:{flight['image_url']}"
            # )
            st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; border: 2px solid #007BFF; border-radius: 10px; padding: 10px; margin-bottom: 15px; background-color: #F7F9FC;">
                <div style="flex-grow: 0.5;">
                    <h5 style="color: #007BFF;">✈️ Flight Number: {flight['id']}</h5>
                    <p><strong>From:</strong> {flight['origin']} <strong>To:</strong> {flight['destination']}</p>
                    <p><strong>Departure:</strong> {flight['departureDate']} <strong>Arrival:</strong> {flight['arrivalDate']}</p>
                    <p><strong>Duration:</strong> {flight['totalTimeHours']}h {flight['totalTimeMinutes']}m</p>
                    <p><strong>Airline Name:</strong> {flight['airline_name']}</p>
                </div>
                <img src="{flight['image_url']}" style="max-width: 100px; margin-left: 10px;" alt="{flight['airline_name']} Logo"/>
            </div>
            """,
            unsafe_allow_html=True
            )
        
    else:
        st.write("No matching flights found.")

    # Display non-matching flights
    st.subheader("Non-Matching Flights")
    if not non_matching_flights.empty:
        for _, flight in non_matching_flights.iterrows():
            # st.write(
            #     f"Flight Number: {flight['id']} | "
            #     f"From: {flight['origin']} To: {flight['destination']} | "
            #     f"Departure: {flight['departureDate']} | "
            #     f"Arrival: {flight['arrivalDate']} | "
            #     f"Duration: {flight['totalTimeHours']}h {flight['totalTimeMinutes']}m"
            # )
            st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; border: 2px solid #007BFF; border-radius: 10px; padding: 10px; margin-bottom: 15px; background-color: #F7F9FC;">
                <div style="flex-grow: 1;">
                    <h5 style="color: #007BFF;">✈️ Flight Number: {flight['id']}</h5>
                    <p><strong>From:</strong> {flight['origin']} <strong>To:</strong> {flight['destination']}</p>
                    <p><strong>Departure:</strong> {flight['departureDate']} <strong>Arrival:</strong> {flight['arrivalDate']}</p>
                    <p><strong>Duration:</strong> {flight['totalTimeHours']}h {flight['totalTimeMinutes']}m</p>
                    <p><strong>Airline Name:</strong> {flight['airline_name']}</p>
                </div>
                <img src="{flight['image_url']}" style="max-width: 100px; margin-left: 10px;" alt="{flight['airline_name']} Logo"/>
            </div>
            """,
            unsafe_allow_html=True
            )
    else:
        st.write("No non-matching flights found.")