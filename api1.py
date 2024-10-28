import os
import re
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from data_file import flights_df, references_df, preferences_df
from flask_cors import CORS, cross_origin
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
CORS(app)


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
@cross_origin()
def get_flights_on_date():
    """Display details of the flights on the selected date."""
    global LAST_QUERY  # pylint: disable=W0602

    data = request.get_json()
    selected_date = data.get("date")
    traveler_id = data.get(
        "traveller_id"
    )  # Assuming you have a specific traveler ID to fetch preferences

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

    # Fetch traveler preferences based on traveler_id
    print(traveler_id)
    traveler_preferences = references_df[references_df["traveler_id"] == traveler_id]
    print(traveler_preferences)
    if traveler_preferences.empty:
        return jsonify({"error": "Traveler preferences not found."}), 404

    # Extract traveler's preferences
    traveler_meal_preference = traveler_preferences.iloc[0]["mealPreference"]
    traveler_seat_preference = traveler_preferences.iloc[0]["seatPreference"]
    traveler_loyalty_program = traveler_preferences.iloc[0]["loyaltyProgram"]
    traveler_class_of_service = traveler_preferences.iloc[0]["classOfService"]
    traveler_in_flight_amenities = traveler_preferences.iloc[0]["inFlightAmenities"]
    traveler_special_requests = traveler_preferences.iloc[0]["specialRequests"]
    traveler_company_policy = traveler_preferences.iloc[0]["companyPolicy"]
    print("Newly Added :", traveler_in_flight_amenities, traveler_special_requests)
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
        matched_class_of_service = (
            flight["classOfService"]
            if flight["classOfService"] == traveler_class_of_service
            else "No reference matched"
        )
        matched_in_flight_amenities = (
            flight["inFlightAmenities"]
            if flight["inFlightAmenities"] == traveler_in_flight_amenities
            else "No reference matched"
        )
        matched_special_requests = (
            flight["specialRequests"]
            if flight["specialRequests"] == traveler_special_requests
            else "No reference matched"
        )
        matched_company_policy = (
            flight["companyPolicy"]
            if flight["companyPolicy"] == traveler_company_policy
            else "No reference matched"
        )

        # Determine flight stops
        flight_stops = "Non-Stop" if flight["stops"] == "0" else flight["stops"]

        # Map origin and destination codes to names
        origin_name = airport_code_to_name.get(flight["origin"], "Unknown Airport")
        destination_name = airport_code_to_name.get(
            flight["destination"], "Unknown Airport"
        )

        # Calculate the time difference between arrival and departure
        departure_datetime = pd.to_datetime(flight["departureDate"])
        arrival_datetime = pd.to_datetime(flight["arrivalDate"])
        flight_duration = arrival_datetime - departure_datetime

        # Get duration in hours and minutes
        duration_hours, duration_minutes = divmod(
            flight_duration.total_seconds() // 60, 60
        )

        # Extract just the time portion for departure and arrival
        departure_time = departure_datetime.strftime("%H:%M")
        arrival_time = arrival_datetime.strftime("%H:%M")

        # Determine matched preferences and calculate preference score
        preference_score = 0
        matched_preferences = {}

        # Check and score preferences
        if matched_meal != "No reference matched":
            matched_preferences["meal"] = matched_meal
            preference_score += 1

        if matched_seat != "No reference matched":
            matched_preferences["seat"] = matched_seat
            preference_score += 1

        if matched_loyalty != "No reference matched":
            matched_preferences["loyalty"] = matched_loyalty
            preference_score += 1

        if matched_class_of_service != "No reference matched":
            matched_preferences["class_of_service"] = matched_class_of_service
            preference_score += 1

        if matched_in_flight_amenities != "No reference matched":
            matched_preferences["in_flight_amenities"] = matched_in_flight_amenities
            preference_score += 1

        if matched_special_requests != "No reference matched":
            matched_preferences["special_requests"] = matched_special_requests
            preference_score += 1

        if matched_company_policy != "No reference matched":
            matched_preferences["company_policy"] = matched_company_policy
            preference_score += 1

        # Build the response for matched preferences
        if len(matched_preferences) == 0:
            matched_preferences = {"message": "No preference is matched"}
        else:
            matched_preferences = {
                "message": "Matched preferences",
                **matched_preferences,  # Include matched preference values
            }

        # Construct the AI message
        ai_result_msg = (
            f"You have a {flight_stops} flight from {origin_name} ({flight['origin']}) "
            f"to {destination_name} ({flight['destination']}) on {flight['departureDate'].strftime('%B %d, %Y')} at {departure_time}. "  # pylint: disable=C0301
            f"The flight is {matched_meal} and you have a {matched_seat}. "
            f"Your loyalty program is {matched_loyalty}. "
            f"Class of service is {matched_class_of_service}. "
            f"In-flight amenities include {matched_in_flight_amenities}. "
            f"Special requests: {matched_special_requests}. "
            f"Company policy: {matched_company_policy}. "
            f"The flight duration is approximately {duration_hours} hours, arriving at {arrival_time}."  # pylint: disable=C0301
        )

        # Invoke the AI model with the constructed message
        summarize_result = f"Summarize this make shorter message but nothing should be missed: {ai_result_msg}"  # pylint: disable=C0301

        res = llm.invoke(summarize_result)

        # Capture the AI's response
        ai_msg = res.content
        print(ai_msg)
        flight_info = {
            "ai_msg": ai_msg,
            "flight_id": flight["id"],
            "leg_id": flight["legId"],
            "airline": {"name": airline_info["name"], "image": airline_info["logo"]},
            "flight_time_hours": duration_hours,
            "flight_time_minutes": duration_minutes,  # Include minutes as well
            "departure_date": flight["departureDate"].isoformat(),
            "arrival_date": flight["arrivalDate"].isoformat(),
            "departure_time": departure_time,  # Departure time in HH:MM format
            "arrival_time": arrival_time,  # Arrival time in HH:MM format
            "stops": flight_stops,
            "origin": {"code": flight["origin"], "name": origin_name},
            "destination": {"code": flight["destination"], "name": destination_name},
            "matched_preferences": matched_preferences,  # Include matched preferences here
            "preference_score": preference_score,  # Include preference score
        }
        results.append(flight_info)

    # Sort the results based on preference score in descending order
    sorted_results = sorted(results, key=lambda x: x["preference_score"], reverse=True)

    return jsonify({"available_flights": sorted_results})



if __name__ == "__main__":
    app.run(debug=True)

