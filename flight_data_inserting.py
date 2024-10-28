import mysql.connector
import json

# Establish MySQL connection
conn = mysql.connector.connect(
    host="192.168.1.61",
    user="enterpi",
    password="Password",
    database="airlines1",
    port=3306
)

cursor = conn.cursor()





def insert_flights(data):
    insert_values = []  # List to hold the values for batch insertion
    
    for flight_leg in data['data']['flights']['flightLegs']:
        # Prepare common data for the flight leg
        leg_id = flight_leg['legId']
        origin = flight_leg['origin']
        destination = flight_leg['destination']
        departure_date = flight_leg['departureDate']
        arrival_date = flight_leg['arrivalDate']
        flight_time_hours = flight_leg['flightTime']['hours']
        flight_time_minutes = flight_leg['flightTime']['minutes']
        total_time_hours = flight_leg['totalTime']['hours']
        total_time_minutes = flight_leg['totalTime']['minutes']
        flight_stops = flight_leg['flightStops']
        days_in_between = flight_leg['daysInBetween']

        # Loop through each segment to gather segment-specific data
        for segment in flight_leg['segments']:
            carrier_name = segment['carrier']['name']
            carrier_id = segment['carrier']['id']
            service_class = segment.get('serviceClass', 'N/A')  # Handle missing 'serviceClass'
            
            # Get distance values
            distance_value = segment['distance']['value']
            distance_units = segment['distance']['units']

            # Debug: Print the values to ensure everything is in place
            print(f"Inserting flight_leg: {leg_id}, segment carrier: {carrier_name}")
            print(f"Values: ({leg_id}, {origin}, {destination}, {departure_date}, {arrival_date}, {flight_time_hours}, {flight_time_minutes}, {total_time_hours}, {total_time_minutes}, {flight_stops}, {days_in_between}, {distance_value}, {distance_units}, {carrier_name}, {carrier_id}, {service_class})")

            # Append to list for batch insertion
            insert_values.append((
                leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, flight_time_minutes,
                total_time_hours, total_time_minutes, flight_stops, days_in_between, distance_value, distance_units,
                carrier_name, carrier_id, service_class
            ))

    # Perform batch insertion if there are values to insert
    if insert_values:
        try:
            cursor.executemany("""  
                INSERT INTO flights (leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, 
                                     flight_time_minutes, total_time_hours, total_time_minutes, flight_stops, days_in_between, 
                                     distance_value, distance_units, carrier_name, carrier_id, service_class)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, insert_values)

            # Commit the transaction
            conn.commit()  # Make sure to commit the changes

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            print("Failed to insert flight legs")
            conn.rollback() 



with open('json/getFlights.json') as f:
    flights_data = json.load(f)
    insert_flights(flights_data)

conn.commit()
cursor.close()
conn.close()