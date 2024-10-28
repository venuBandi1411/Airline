"""This file will get the airline details based on user preferences."""

import os
import re
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI

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

# Load your flight data
try:
    flights_df = pd.read_csv("flight2.csv")
    print(flights_df)
    flights_df["departureDate"] = pd.to_datetime(flights_df["departureDate"])
    print(flights_df["departureDate"])
except FileNotFoundError:
    print("Error: The file 'flights2.csv' was not found.")
except pd.errors.EmptyDataError:
    print("Error: The file 'flights2.csv' is empty.")

# Load flights preferences data
try:
    preferences_df = pd.read_csv("preferences1.csv")
except FileNotFoundError:
    print("Error: The file 'preferences1.csv' was not found.")
except pd.errors.EmptyDataError:
    print("Error: The file 'preferences1.csv' is empty.")

# Load traveler references data
try:
    references_df = pd.read_csv("references2.csv")
except FileNotFoundError:
    print("Error: The file 'references.csv' was not found.")
except pd.errors.EmptyDataError:
    print("Error: The file 'references.csv' is empty.")


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


# airlines_mapping = {
#     "AA": {
#         "name": "American Airlines",
#         "logo": "/THUMB-aa_aa__ahz_4cp_grd_pos-(1).svg",
#     },
#     "DL": {
#         "name": "Delta Airlines",
#         "logo": "/delta.svg",
#     },
#     "UA": {
#         "name": "United Airlines",
#         "logo": "/United_Airlines-Logo.wine.svg",
#     },
#     "WN": {
#         "name": "Southwest Airlines",
#         "logo": "/sw.svg",
#     },
#     "B6": {
#         "name": "JetBlue Airways",
#         "logo": "/JB.svg",
#     },
#     "AS": {
#         "name": "Alaska Airlines",
#         "logo": "/ALaska.svg",
#     },
#     "F9": {
#         "name": "Frontier Airlines",
#         "logo": "/Front.svg",
#     },
#     "NK": {
#         "name": "Spirit Airlines",
#         "logo": "/spirit.svg",
#     },
# }

# # Reverse the mapping to get airport codes from names
# airport_code_to_name = {v: k for k, v in airport_name_to_code.items()}


# @app.route("/get_flights_on_date", methods=["POST"])
# def get_flights_on_date():
#     """Display details of the flights on the selected date."""
#     global LAST_QUERY  # Use the global variable for the last query
#     data = request.get_json()
#     selected_date = data.get("date")

#     try:
#         selected_date = pd.to_datetime(selected_date).date()
#     except ValueError:
#         return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

#     # Extract origin and destination from the last query
#     origin, destination = extract_flight_info(LAST_QUERY)

#     if origin is None or destination is None:
#         return (
#             jsonify({"error": f"No Flights Found between {origin} and {destination}"}),
#             400,
#         )

#     # Fetch traveler preferences based on traveler_id
#     traveler_id = 1  # Assuming you have a specific traveler ID to fetch preferences
#     traveler_preferences = references_df[references_df["traveler_id"] == traveler_id]

#     if traveler_preferences.empty:
#         return jsonify({"error": "Traveler preferences not found."}), 404

#     # Extract traveler's meal, seat, and loyalty preferences
#     traveler_meal_preference = traveler_preferences.iloc[0]["mealPreference"]
#     traveler_seat_preference = traveler_preferences.iloc[0]["seatPreference"]
#     traveler_loyalty_program = traveler_preferences.iloc[0]["loyaltyProgram"]

#     # Search for flights using IATA codes
#     matching_flights = flights_df[
#         (flights_df["origin"].str.upper().str.strip() == origin)
#         & (flights_df["destination"].str.upper().str.strip() == destination)
#     ]

#     # Convert departureDate and arrivalDate to datetime objects
#     matching_flights["departureDate"] = pd.to_datetime(
#         matching_flights["departureDate"]
#     )
#     matching_flights["arrivalDate"] = pd.to_datetime(matching_flights["arrivalDate"])

#     # Filter flights for the specified date
#     flights_on_date = matching_flights[
#         matching_flights["departureDate"].dt.date == selected_date
#     ]

#     if flights_on_date.empty:
#         return (
#             jsonify(
#                 {
#                     "message": (
#                         f"No flights available from {origin} to {destination} on {selected_date}."
#                     )
#                 }
#             ),
#             404,
#         )

#     # Merge flight data with preferences using flight_id
#     merged_data = pd.merge(
#         flights_on_date, preferences_df, left_on="id", right_on="flight_id", how="left"
#     )

#     results = []
#     for _, flight in merged_data.iterrows():
#         # Extract the airline code from the legId
#         airline_code = flight["legId"].split("/")[2][:2]

#         # Get airline information
#         airline_info = airlines_mapping.get(
#             airline_code, {"name": "Unknown Airline", "logo": ""}
#         )

#         # Check traveler's preferences
#         matched_meal = (
#             flight["mealPreference"]
#             if flight["mealPreference"] == traveler_meal_preference
#             else "No reference matched"
#         )
#         matched_seat = (
#             flight["seatPreference"]
#             if flight["seatPreference"] == traveler_seat_preference
#             else "No reference matched"
#         )
#         matched_loyalty = (
#             flight["loyaltyProgram"]
#             if flight["loyaltyProgram"] == traveler_loyalty_program
#             else "No reference matched"
#         )

#         # Determine flight stops
#         flight_stops = "Non-Stop" if flight["stops"] == "0" else flight["stops"]

#         # Map origin and destination codes to names
#         origin_name = airport_code_to_name.get(flight["origin"], "Unknown Airport")
#         destination_name = airport_code_to_name.get(
#             flight["destination"], "Unknown Airport"
#         )

#         # Calculate the time difference between arrival and departure
#         departure_datetime = pd.to_datetime(flight["departureDate"])
#         arrival_datetime = pd.to_datetime(flight["arrivalDate"])
#         flight_duration = arrival_datetime - departure_datetime

#         # Get duration in hours and minutes
#         duration_hours, duration_minutes = divmod(
#             flight_duration.total_seconds() // 60, 60
#         )

#         # Extract just the time portion for departure and arrival
#         departure_time = departure_datetime.strftime("%H:%M")
#         arrival_time = arrival_datetime.strftime("%H:%M")

#         # Determine matched preferences
#         matched_preferences = {}
#         if matched_meal != "No reference matched":
#             matched_preferences["meal"] = matched_meal
#         if matched_seat != "No reference matched":
#             matched_preferences["seat"] = matched_seat
#         if matched_loyalty != "No reference matched":
#             matched_preferences["loyalty"] = matched_loyalty

#         # Build the response for matched preferences
#         if len(matched_preferences) == 0:
#             matched_preferences = {"message": "No preference is matched"}
#         else:
#             matched_preferences = {
#                 "message": "Matched preferences: "
#                 + ", ".join(matched_preferences.keys()),
#                 **matched_preferences,  # Include matched preference values
#             }

#         flight_info = {
#             "flight_id": flight["id"],
#             "leg_id": flight["legId"],
#             "airline": {"name": airline_info["name"], "image": airline_info["logo"]},
#             "flight_time_hours": duration_hours,
#             "flight_time_minutes": duration_minutes,  # Include minutes as well
#             "departure_date": flight["departureDate"].isoformat(),
#             "arrival_date": flight["arrivalDate"].isoformat(),
#             "departure_time": departure_time,  # Departure time in HH:MM format
#             "arrival_time": arrival_time,  # Arrival time in HH:MM format
#             "stops": flight_stops,
#             "origin": {"code": flight["origin"], "name": origin_name},
#             "destination": {"code": flight["destination"], "name": destination_name},
#             "matched_preferences": matched_preferences,  # Include matched preferences here
#         }
#         results.append(flight_info)

#     return jsonify({"available_flights": results})


# Updated airlines mapping with logos  
airlines_mapping = {  
   "AA": {  
      "name": "American Airlines",  
      "logo": "/THUMB-aa_aa__ahz_4cp_grd_pos-(1).svg",  
   },  
   "DL": {  
      "name": "Delta Airlines",  
      "logo": "/delta.svg",  
   },  
   "UA": {  
      "name": "United Airlines",  
      "logo": "/United_Airlines-Logo.wine.svg",  
   },  
   "WN": {  
      "name": "Southwest Airlines",  
      "logo": "/sw.svg",  
   },  
   "B6": {  
      "name": "JetBlue Airways",  
      "logo": "/JB.svg",  
   },  
   "AS": {  
      "name": "Alaska Airlines",  
      "logo": "/ALaska.svg",  
   },  
   "F9": {  
      "name": "Frontier Airlines",  
      "logo": "/Front.svg",  
   },  
   "NK": {  
      "name": "Spirit Airlines",  
      "logo": "/spirit.svg",  
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
   traveler_id = 1  # Assuming you have a specific traveler ID to fetch preferences  
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
  
      # Determine matched preferences  
      matched_preferences = {}  
      if matched_meal != "No reference matched":  
        matched_preferences["meal"] = matched_meal  
      if matched_seat != "No reference matched":  
        matched_preferences["seat"] = matched_seat  
      if matched_loyalty != "No reference matched":  
        matched_preferences["loyalty"] = matched_loyalty  
  
      # Build the response for matched preferences  
      if len(matched_preferences) == 0:  
        matched_preferences = {"message": "No preference is matched"}  
      else:  
        matched_preferences = {  
           "message": "Matched preferences: "  
           + ", ".join(matched_preferences.keys()),  
           **matched_preferences,  # Include matched preference values  
        }  
  
      flight_info = {  
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
      }  
      results.append(flight_info)  
  
   return jsonify({"available_flights": results}) 


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6768, debug=True)
