import os
import re
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
import mysql.connector

# Load the .env variables
load_dotenv()
OPENAI_API_KEY = os.getenv("API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Dictionary to map full airport names to IATA codes
airport_name_to_code = {
    "Los Angeles International Airport": "LAX",
    "Dallas/Fort Worth International Airport": "DFW",
    "Cleveland Hopkins International Airport": "CLE",
    "San Francisco International Airport": "SFO",
    "Houston Love Field Airport": "DAL",
    "Miami International Airport": "MIA",
    "Salt Lake City International Airport": "SLC",
    "Logan International Airport": "BOS",
}

# Initialize Flask app
app = Flask(__name__, static_url_path="", static_folder="AirlinesLogo")

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
    flights_df = pd.read_sql("SELECT * FROM flights", db_connection)
    # print(flights_df)
    flights_df["departureDate"] = pd.to_datetime(flights_df["departureDate"])
except Exception as e:
    print(f"Error loading flight data: {e}")

# Load flights preferences data
try:
    db_connection = get_db_connection()
    preferences_df = pd.read_sql("SELECT * FROM preferences", db_connection)
    # print(preferences_df)
except Exception as e:
    print(f"Error loading preferences data: {e}")

# Load traveler references data
try:
    db_connection = get_db_connection()
    references_df = pd.read_sql("SELECT * FROM user_references", db_connection)
    # print(references_df)
except Exception as e:
    print(f"Error loading references data: {e}")

def extract_flight_info(query):
    """Extract the origin and destination airports from the user's query."""
    prompt = f"""
    Extract the origin and destination airports from the following query:
    "{query}"
    
    Please respond in this format:
    Origin: <origin_airport>
    Destination: <destination_airport>
    """

    # Generate the response
    response = llm.invoke(prompt)
    response_text = response.content.strip()

    # Use regex to extract origin and destination
    origin_match = re.search(r"Origin: (.+)", response_text)
    destination_match = re.search(r"Destination: (.+)", response_text)

    if origin_match and destination_match:
        origin_airport = origin_match.group(1).strip()
        destination_airport = destination_match.group(1).strip()

        # Map to IATA codes
        origin_code = airport_name_to_code.get(origin_airport)
        destination_code = airport_name_to_code.get(destination_airport)

        if origin_code and destination_code:
            return origin_code, destination_code
        return None, None
    return None, None

# Global variable to store the last query
LAST_QUERY = ""

@app.route("/search_flights", methods=["POST"])
def search_flights():
    """Will Search the Flights Based on the data how many are there"""
    global LAST_QUERY  # pylint: disable=global-statement

    # Get the query from the request
    data = request.get_json()
    LAST_QUERY = data.get("query", "")  # Store the query globally

    origin, destination = extract_flight_info(LAST_QUERY)

    # Check if origin and destination were successfully extracted
    if origin is None or destination is None:
        return (
            jsonify({"error": "Could not extract origin and destination airports."}),
            400,
        )

    # Search for flights using IATA codes
    matching_flights = flights_df[
        (flights_df["origin"].str.upper().str.strip() == origin)
        & (flights_df["destination"].str.upper().str.strip() == destination)
    ]

    # Display available dates and counts
    if not matching_flights.empty:
        available_dates = matching_flights["departureDate"].dt.date.value_counts()

        # Convert index to strings for JSON serialization and format the date
        available_dates = available_dates.rename_axis("date").reset_index(name="count")

        # Format the date to exclude the time part
        available_dates["date"] = available_dates["date"].apply(
            lambda x: x.strftime("%Y-%m-%d")
        )

        available_dates = available_dates.to_dict(orient="records")

        return jsonify({"available_dates": available_dates})

    return jsonify({"error": "No flights found."}), 404

# Updated airlines mapping with logos
airlines_mapping = {
    "AA": {
        "name": "American Airlines",
        "logo": f"https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/AA.png?_a=BAMADKTC0",
    },
    "DL": {
        "name": "Delta Airlines",
        "logo": "https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/DL.png?_a=BAMADKTC0",
    },
    "UA": {
        "name": "United Airlines",
        "logo": "https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/UA.png?_a=BAMADKTC0",
    },
    "WN": {
        "name": "Southwest Airlines",
        "logo": "https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/WN.png?_a=BAMADKTC0",
    },
    "B6": {
        "name": "JetBlue Airways",
        "logo": "https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/B6.png?_a=BAMADKTC0",
    },
    "AS": {
        "name": "Alaska Airlines",
        "logo": "https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/AS.png?_a=BAMADKTC0",
    },
    "F9": {
        "name": "Frontier Airlines",
        "logo": "https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/F9.png?_a=BAMADKTC0",
    },
    "NK": {
        "name": "Spirit Airlines",
        "logo": "https://res.cloudinary.com/dm0zqj0n2/image/upload/v1/Logos/Airlines/IATA/Square/NK.png?_a=BAMADKTC0",
    },
}

# Reverse the mapping to get airport codes from names
airport_code_to_name = {v: k for k, v in airport_name_to_code.items()}



@app.route("/get_flights_on_date", methods=["POST"])  
def get_flights_on_date():  
    """Display details of the flights on the selected date."""  
    global LAST_QUERY  # Use the global variable for the last query  
    data = request.get_json()  
    selected_date = data.get("date")
    traveller = data.get("traveller_id",1)  
    print(traveller)
    try:  
        selected_date = pd.to_datetime(selected_date).date()  
    except ValueError:  
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400  
    
    # Extract origin and destination from the last query  
    origin, destination = extract_flight_info(LAST_QUERY)  
    
    if origin is None or destination is None:  
        return (  
            jsonify({"error": f"No Flights Found between {origin} and {destination}"}),  
            400,  
        )  
    
    # # Fetch traveler preferences based on traveler_id  
    # traveler_id = 1  # Assuming you have a specific traveler ID to fetch preferences  
    # traveler_preferences = references_df[references_df["traveler_id"] == traveler_id]  
    traveler_id = traveller  
    traveler_preferences = references_df[references_df["traveler_id"] == traveler_id]  
    
    if traveler_preferences.empty:  
        return jsonify({"error": "Traveler preferences not found."}), 404  
    
    # Extract traveler's meal, seat, and loyalty preferences  
    traveler_meal_preference = traveler_preferences.iloc[0]["mealPreference"]  
    traveler_seat_preference = traveler_preferences.iloc[0]["seatPreference"]  
    traveler_loyalty_program = traveler_preferences.iloc[0]["loyaltyProgram"]  
    
    # Search for flights using IATA codes  
    matching_flights = flights_df[  
        (flights_df["origin"].str.upper().str.strip() == origin)  
        & (flights_df["destination"].str.upper().str.strip() == destination)  
    ]  
    
    # Convert departureDate and arrivalDate to datetime objects  
    matching_flights["departureDate"] = pd.to_datetime(  
        matching_flights["departureDate"]  
    )  
    matching_flights["arrivalDate"] = pd.to_datetime(matching_flights["arrivalDate"])  
    
    # Filter flights for the specified date  
    flights_on_date = matching_flights[  
        matching_flights["departureDate"].dt.date == selected_date  
    ]  
    
    if flights_on_date.empty:  
        return (  
            jsonify(  
            {  
                "message": (  
                    f"No flights available from {origin} to {destination} on {selected_date}."  
                )  
            }  
            ),  
            404,  
        )  
    
    # Merge flight data with preferences using flight_id  
    merged_data = pd.merge(  
        flights_on_date, preferences_df, left_on="id", right_on="flight_id", how="left"  
    )  
    
    results = []  
    for _, flight in merged_data.iterrows():  
        # Extract the airline code from the legId  
        airline_code = flight["legId"].split("/")[2][:2]  
    
        # Get airline information  
        airline_info = airlines_mapping.get(  
            airline_code, {"name": "Unknown Airline", "logo": ""}  
        )  
    
        # Check traveler's preferences  
        matched_meal = (  
            flight["mealPreference"]  
            if flight["mealPreference"] == traveler_meal_preference  
            else "No reference matched"  
        )  
        matched_seat = (  
            flight["seatPreference"]  
            if flight["seatPreference"] == traveler_seat_preference  
            else "No reference matched"  
        )  
        matched_loyalty = (  
            flight["loyaltyProgram"]  
            if flight["loyaltyProgram"] == traveler_loyalty_program  
            else "No reference matched"  
        )  
    
        # Prepare the departure and arrival times  
        departure_time = flight["departureDate"].strftime("%H:%M")  
        arrival_time = flight["arrivalDate"].strftime("%H:%M")  
    
        # Calculate duration  
        duration = flight["arrivalDate"] - flight["departureDate"]  
        duration_hours, duration_minutes = divmod(duration.seconds // 60, 60)  
    
        # Calculate preference score  
        preference_score = 0  
        if matched_meal == traveler_meal_preference:  
            preference_score += 1  
        if matched_seat == traveler_seat_preference:  
            preference_score += 1  
        if matched_loyalty == traveler_loyalty_program:  
            preference_score += 1  
    
        # Build the flight info dictionary  
        flight_info = {  
                "flight_id": flight["id"],  
                "leg_id": flight["legId"],  
                "airline": airline_info["name"],  
                "airline_logo": airline_info["logo"],  
                "flight_time_hours": flight["flightTimeHours"],  
                "total_time_hours": flight["totalTimeHours"],  
                "departure_date": flight["departureDate"].isoformat(),  
                "arrival_date": flight["arrivalDate"].isoformat(),  
                "stops": flight["stops"],  
                "origin": origin,  
                "destination": destination,  
                "departure_time": departure_time,  
                "arrival_time": arrival_time,  
                "duration": {  
                    "hours": int(duration_hours),  
                    "minutes": int(duration_minutes),  
                },  
                "matched_preferences": {  
                    "meal": matched_meal,  
                    "seat": matched_seat,  
                    "loyalty": matched_loyalty,  
                },  
                "preference_score": preference_score,  
            }  
        results.append(flight_info)  
    
    # Sort results by preference score in descending order  
    results.sort(key=lambda x: x["preference_score"], reverse=True)  
    
    # Move flights with all matched preferences to the top of the list  
    all_matched_flights = [flight for flight in results if flight["preference_score"] == 3]  
    other_flights = [flight for flight in results if flight["preference_score"] < 3]  
    results = all_matched_flights + other_flights  
    
    return jsonify({"available_flights": results})





if __name__ == "__main__":
    app.run(debug=True)

