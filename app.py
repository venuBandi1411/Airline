# import mysql.connector
# import json

# # Establish MySQL connection
# conn = mysql.connector.connect(
#     host="192.168.1.61",
#     user="enterpi",
#     password="Password",
#     database="airlines1",
#     port=3306
# )

# cursor = conn.cursor()

# # Function to create the required tables if they don't exist
# def create_tables():
#     # Create travel_preferences table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS travel_preferences (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             home_airport VARCHAR(10),
#             home_airport_label VARCHAR(255),
#             seat_preference VARCHAR(50),
#             redress_number VARCHAR(50),
#             redress_number_issuing_country VARCHAR(50),
#             known_traveler_number VARCHAR(50),
#             known_traveler_issuing_country VARCHAR(50),
#             results_view VARCHAR(50),
#             note_to_arranger TEXT
#         )
#     """)
    
#     # Create special_requests table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS special_requests (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             travel_pref_id INT,
#             label VARCHAR(255),
#             value VARCHAR(50),
#             FOREIGN KEY (travel_pref_id) REFERENCES travel_preferences(id)
#         )
#     """)
    
#     # Create loyalty_programs table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS loyalty_programs (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             travel_pref_id INT,
#             vendor_code VARCHAR(10),
#             label VARCHAR(255),
#             number VARCHAR(50),
#             img_url VARCHAR(255),
#             FOREIGN KEY (travel_pref_id) REFERENCES travel_preferences(id)
#         )
#     """)
    
#     # Create meal_options table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS meal_options (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             travel_pref_id INT,
#             label VARCHAR(255),
#             value VARCHAR(50),
#             FOREIGN KEY (travel_pref_id) REFERENCES travel_preferences(id)
#         )
#     """)
    
#     # Create flights table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS flights (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             leg_id VARCHAR(50),
#             origin VARCHAR(10),
#             destination VARCHAR(10),
#             departure_date DATETIME,
#             arrival_date DATETIME,
#             flight_time_hours INT,
#             flight_time_minutes INT,
#             total_time_hours INT,
#             total_time_minutes INT,
#             flight_stops INT,
#             days_in_between INT,
#             distance_value INT,
#             distance_units VARCHAR(10),
#             rate_amount DECIMAL(10,2),
#             rate_currency VARCHAR(10),
#             carrier_name VARCHAR(100),
#             carrier_id VARCHAR(10),
#             service_class VARCHAR(50)
#         )
#     """)

# # Function to insert travel preferences
# def insert_travel_preferences(data):
#     travel_data = data['data']['travelPreferences']['flight']
    
#     cursor.execute("""
#         INSERT INTO travel_preferences (home_airport, home_airport_label, seat_preference, redress_number, 
#                                          redress_number_issuing_country, known_traveler_number, 
#                                          known_traveler_issuing_country, results_view, note_to_arranger)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """, (
#         travel_data.get('homeAirport'),
#         travel_data.get('homeAirportLabel'),
#         travel_data.get('seatPreference'),
#         travel_data.get('redressNumber'),
#         travel_data.get('redressNumberIssuingCountry'),
#         travel_data.get('knownTravelerNumber'),
#         travel_data.get('knownTravelerIssuingCountry'),
#         travel_data.get('resultsView'),
#         travel_data.get('noteToArranger')
#     ))
    
#     travel_pref_id = cursor.lastrowid

#     # Insert Special Requests
#     for special_request in travel_data.get('specialRequest', []):
#         cursor.execute("""
#             INSERT INTO special_requests (travel_pref_id, label, value) 
#             VALUES (%s, %s, %s)
#         """, (travel_pref_id, special_request['label'], special_request['value']))
    
#     # Insert Loyalty Programs
#     for loyalty_program in travel_data.get('loyaltyProgram', []):
#         cursor.execute("""
#             INSERT INTO loyalty_programs (travel_pref_id, vendor_code, label, number, img_url) 
#             VALUES (%s, %s, %s, %s, %s)
#         """, (travel_pref_id, loyalty_program['vendorCode'], loyalty_program['label'], loyalty_program['number'], loyalty_program['imgUrl']))
    
#     # Insert Meal Options
#     for meal_option in travel_data.get('mealOptions', []):
#         cursor.execute("""
#             INSERT INTO meal_options (travel_pref_id, label, value) 
#             VALUES (%s, %s, %s)
#         """, (travel_pref_id, meal_option['label'], meal_option['value']))

# # Function to insert flights
# def insert_flights(data):
#     for flight_leg in data['data']['flights']['flightLegs']:
#         # Prepare the data values for insertion
#         leg_id = flight_leg['legId']
#         origin = flight_leg['origin']
#         destination = flight_leg['destination']
#         departure_date = flight_leg['departureDate']
#         arrival_date = flight_leg['arrivalDate']
#         flight_time_hours = flight_leg['flightTime']['hours']
#         flight_time_minutes = flight_leg['flightTime']['minutes']
#         total_time_hours = flight_leg['totalTime']['hours']
#         total_time_minutes = flight_leg['totalTime']['minutes']
#         flight_stops = flight_leg['flightStops']
#         days_in_between = flight_leg['daysInBetween']
#         distance_value = flight_leg['distance']['value']
#         distance_units = flight_leg['distance']['units']
#         rate_amount = flight_leg['rate']['primary']['amount']
#         rate_currency = flight_leg['rate']['primary']['currency']
#         carrier_name = flight_leg['segments'][0]['carrier']['name']
#         carrier_id = flight_leg['segments'][0]['carrier']['id']
#         service_class = flight_leg['segments'][0].get('serviceClass', 'N/A')  # Handle missing 'serviceClass'

#         # Debug: Print the values to ensure everything is in place
#         print(f"Inserting flight_leg: {leg_id}")
#         print(f"Values: ({leg_id}, {origin}, {destination}, {departure_date}, {arrival_date}, {flight_time_hours}, {flight_time_minutes}, {total_time_hours}, {total_time_minutes}, {flight_stops}, {days_in_between}, {distance_value}, {distance_units}, {rate_amount}, {rate_currency}, {carrier_name}, {carrier_id}, {service_class})")
        
#         try:
#             cursor.execute("""
#                 INSERT INTO flights (leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, 
#                                      flight_time_minutes, total_time_hours, total_time_minutes, flight_stops, days_in_between, 
#                                      distance_value, distance_units, rate_amount, rate_currency, carrier_name, carrier_id, service_class)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """, (
#                 leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, flight_time_minutes,
#                 total_time_hours, total_time_minutes, flight_stops, days_in_between, distance_value, distance_units,
#                 rate_amount, rate_currency, carrier_name, carrier_id, service_class
#             ))

#         except mysql.connector.Error as err:
#             print(f"Error: {err}")
#             print(f"Failed to insert flight leg with id: {leg_id}")


# # Create tables if not exists
# create_tables()

# # Read and insert data from JSON files
# with open('json/getTravelPreferences.json') as f:
#     travel_data = json.load(f)
#     insert_travel_preferences(travel_data)

# with open('json/getFlights.json') as f:
#     flights_data = json.load(f)
#     insert_flights(flights_data)

# # Commit and close the connection
# conn.commit()
# cursor.close()
# conn.close()






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

# Function to create the required tables if they don't exist
def create_tables():
    # Create travel_preferences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_preferences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            home_airport VARCHAR(10),
            home_airport_label VARCHAR(255),
            seat_preference VARCHAR(50),
            redress_number VARCHAR(50),
            redress_number_issuing_country VARCHAR(50),
            known_traveler_number VARCHAR(50),
            known_traveler_issuing_country VARCHAR(50),
            results_view VARCHAR(50),
            note_to_arranger TEXT
        )
    """)
    
    # Create special_requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS special_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            travel_pref_id INT,
            label VARCHAR(255),
            value VARCHAR(50),
            FOREIGN KEY (travel_pref_id) REFERENCES travel_preferences(id)
        )
    """)
    
    # Create loyalty_programs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loyalty_programs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            travel_pref_id INT,
            vendor_code VARCHAR(10),
            label VARCHAR(255),
            number VARCHAR(50),
            img_url VARCHAR(255),
            FOREIGN KEY (travel_pref_id) REFERENCES travel_preferences(id)
        )
    """)
    
    # Create meal_options table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_options (
            id INT AUTO_INCREMENT PRIMARY KEY,
            travel_pref_id INT,
            label VARCHAR(255),
            value VARCHAR(50),
            FOREIGN KEY (travel_pref_id) REFERENCES travel_preferences(id)
        )
    """)
    
    # Create flights table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INT AUTO_INCREMENT PRIMARY KEY,
            leg_id VARCHAR(50),
            origin VARCHAR(10),
            destination VARCHAR(10),
            departure_date DATETIME,
            arrival_date DATETIME,
            flight_time_hours INT,
            flight_time_minutes INT,
            total_time_hours INT,
            total_time_minutes INT,
            flight_stops INT,
            days_in_between INT,
            distance_value INT,
            distance_units VARCHAR(10),
            rate_amount DECIMAL(10,2),
            rate_currency VARCHAR(10),
            carrier_name VARCHAR(100),
            carrier_id VARCHAR(10),
            service_class VARCHAR(50)
        )
    """)

    # Create DisplayConfiguration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DisplayConfiguration (
        id INT AUTO_INCREMENT PRIMARY KEY,
        isAdminRoleEnabled BOOLEAN,
        isMod2FlowEnabled BOOLEAN,
        isFlightSearchServiceEnabled BOOLEAN,
        areRecommendationsEnabled BOOLEAN,
        isPhoenixHotelSearchEnabled BOOLEAN,
        isPhoenixCarRentalSearchEnabled BOOLEAN,
        maxNumberOfGuestsPerRoom INT,
        isTripAdvisorReviewsEnabled BOOLEAN,
        mapProvider VARCHAR(50),
        isPerDiemDisplayEnabled BOOLEAN,
        isStarRatingsFilterEnabled BOOLEAN,
        isHoldTripAllowed BOOLEAN,
        isSoldOutFilterAvailable BOOLEAN,
        isPreBookCostAllocationEnabled BOOLEAN,
        isShowTravelerAcknowledgement BOOLEAN,
        isExcludeBasicFareBlock BOOLEAN,
        isSouthwestDirectConnectionEnabled BOOLEAN,
        isExpiringCreditCardForHotelAllowed BOOLEAN,
        isCreditCardSavingEnabled BOOLEAN,
        isAppleLockSettingsEnabled BOOLEAN,
        appleDsmMessage TEXT,
        enableNearByAirport BOOLEAN,
        bookAndChangeAdvanceTime INT,
        selfDelegation BOOLEAN,
        userDelegation BOOLEAN,
        hideUnusedTickets BOOLEAN,
        defaultCarSize VARCHAR(10),
        isMod2DoubleWriteEnabled BOOLEAN,
        geosureReportEnabled BOOLEAN,
        geosureReportVariant VARCHAR(50),
        flightSearchTimeRangeBefore INT,
        flightSearchTimeRangeAfter INT,
        hotelSearchRadiusDefault INT,
        hotelSearchRadiusMax INT,
        privacyPolicyUrl VARCHAR(255),
        privacyPolicyLabel VARCHAR(255),
        mobileSupportEmail VARCHAR(255),
        desktopSupportEmail VARCHAR(255),
        technicalSupportEnabled BOOLEAN,
        technicalSupportText TEXT
    )
    """)

    # Create ExploreDisplayConfiguration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ExploreDisplayConfiguration (
            id INT AUTO_INCREMENT PRIMARY KEY,
            display_config_id INT,
            isFlightsSearchEnabled BOOLEAN,
            isHotelsSearchEnabled BOOLEAN,
            isTrainsSearchEnabled BOOLEAN,
            isCarRentalsSearchEnabled BOOLEAN,
            searchDefaultsAirEnabled BOOLEAN,
            searchDefaultsHotelEnabled BOOLEAN,
            searchDefaultsCarEnabled BOOLEAN,
            FOREIGN KEY (display_config_id) REFERENCES DisplayConfiguration(id)
        )
    """)

    # Create FlightHotelCarDisplayConfiguration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FlightHotelCarDisplayConfiguration (
            id INT AUTO_INCREMENT PRIMARY KEY,
            display_config_id INT,
            defaultSort VARCHAR(50),
            areNearbyAirportsIncluded BOOLEAN,
            isMorningAfternoonEveningEnabled BOOLEAN,
            isAnytimeEnabled BOOLEAN,
            isDefaultAnyTime BOOLEAN,
            isFirstClassEnabled BOOLEAN,
            isBusinessClassEnabled BOOLEAN,
            isPremiumEconomyClassEnabled BOOLEAN,
            isEconomyClassEnabled BOOLEAN,
            defaultAirTravelType VARCHAR(50),
            isOutOfPolicyFlightsSelectable BOOLEAN,
            defaultFareType VARCHAR(50),
            areRefundableEnabled BOOLEAN,
            areUnrestrictedEnabled BOOLEAN,
            carDeliveryAndCollectionSupported BOOLEAN,
            requireCarPaymentForm BOOLEAN,
            isStarRatingEnabled BOOLEAN,
            FOREIGN KEY (display_config_id) REFERENCES DisplayConfiguration(id)
        )
    """)

    # Create SupportExternalLinksResource table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SupportExternalLinksResource (
            id INT AUTO_INCREMENT PRIMARY KEY,
            display_config_id INT,
            isExternalLinksEnabled BOOLEAN,
            link_url VARCHAR(255),
            link_label VARCHAR(255),
            resource_label VARCHAR(255),
            resource_url VARCHAR(255),
            FOREIGN KEY (display_config_id) REFERENCES DisplayConfiguration(id)
        )
    """)


# Function to insert travel preferences
def insert_travel_preferences(data):
    travel_data = data['data']['travelPreferences']['flight']
    
    cursor.execute("""
        INSERT INTO travel_preferences (home_airport, home_airport_label, seat_preference, redress_number, 
                                         redress_number_issuing_country, known_traveler_number, 
                                         known_traveler_issuing_country, results_view, note_to_arranger)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        travel_data.get('homeAirport'),
        travel_data.get('homeAirportLabel'),
        travel_data.get('seatPreference'),
        travel_data.get('redressNumber'),
        travel_data.get('redressNumberIssuingCountry'),
        travel_data.get('knownTravelerNumber'),
        travel_data.get('knownTravelerIssuingCountry'),
        travel_data.get('resultsView'),
        travel_data.get('noteToArranger')
    ))
    
    travel_pref_id = cursor.lastrowid

    # Insert Special Requests
    for special_request in travel_data.get('specialRequest', []):
        cursor.execute("""
            INSERT INTO special_requests (travel_pref_id, label, value) 
            VALUES (%s, %s, %s)
        """, (travel_pref_id, special_request['label'], special_request['value']))
    
    # Insert Loyalty Programs
    for loyalty_program in travel_data.get('loyaltyProgram', []):
        cursor.execute("""
            INSERT INTO loyalty_programs (travel_pref_id, vendor_code, label, number, img_url) 
            VALUES (%s, %s, %s, %s, %s)
        """, (travel_pref_id, loyalty_program['vendorCode'], loyalty_program['label'], loyalty_program['number'], loyalty_program['imgUrl']))
    
    # Insert Meal Options
    for meal_option in travel_data.get('mealOptions', []):
        cursor.execute("""
            INSERT INTO meal_options (travel_pref_id, label, value) 
            VALUES (%s, %s, %s)
        """, (travel_pref_id, meal_option['label'], meal_option['value']))

# Function to insert flights
def insert_flights(data):
    for flight_leg in data['data']['flights']['flightLegs']:
        # Prepare the data values for insertion
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
        distance_value = flight_leg['distance']['value']
        distance_units = flight_leg['distance']['units']
        rate_amount = flight_leg['rate']['primary']['amount']
        rate_currency = flight_leg['rate']['primary']['currency']
        carrier_name = flight_leg['segments'][0]['carrier']['name']
        carrier_id = flight_leg['segments'][0]['carrier']['id']
        service_class = flight_leg['segments'][0].get('serviceClass', 'N/A')  # Handle missing 'serviceClass'

        # Debug: Print the values to ensure everything is in place
        print(f"Inserting flight_leg: {leg_id}")
        print(f"Values: ({leg_id}, {origin}, {destination}, {departure_date}, {arrival_date}, {flight_time_hours}, {flight_time_minutes}, {total_time_hours}, {total_time_minutes}, {flight_stops}, {days_in_between}, {distance_value}, {distance_units}, {rate_amount}, {rate_currency}, {carrier_name}, {carrier_id}, {service_class})")
        
        try:
            cursor.execute("""
                INSERT INTO flights (leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, 
                                     flight_time_minutes, total_time_hours, total_time_minutes, flight_stops, days_in_between, 
                                     distance_value, distance_units, rate_amount, rate_currency, carrier_name, carrier_id, service_class)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, flight_time_minutes,
                total_time_hours, total_time_minutes, flight_stops, days_in_between, distance_value, distance_units,
                rate_amount, rate_currency, carrier_name, carrier_id, service_class
            ))

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            print(f"Failed to insert flight leg with id: {leg_id}")

# Function to insert DisplayConfiguration data
def insert_display_configuration(cursor, data):
    cursor.execute("""
        INSERT INTO DisplayConfiguration (
            isAdminRoleEnabled, isMod2FlowEnabled, isFlightSearchServiceEnabled,
            areRecommendationsEnabled, isPhoenixHotelSearchEnabled,
            isPhoenixCarRentalSearchEnabled, maxNumberOfGuestsPerRoom,
            isTripAdvisorReviewsEnabled, mapProvider, isPerDiemDisplayEnabled,
            isStarRatingsFilterEnabled, isHoldTripAllowed, isSoldOutFilterAvailable,
            isPreBookCostAllocationEnabled, isShowTravelerAcknowledgement,
            isExcludeBasicFareBlock, isSouthwestDirectConnectionEnabled,
            isExpiringCreditCardForHotelAllowed, isCreditCardSavingEnabled,
            isAppleLockSettingsEnabled, appleDsmMessage, enableNearByAirport,
            bookAndChangeAdvanceTime, selfDelegation, userDelegation,
            hideUnusedTickets, defaultCarSize, isMod2DoubleWriteEnabled,
            geosureReportEnabled, geosureReportVariant,
            flightSearchTimeRangeBefore, flightSearchTimeRangeAfter,
            hotelSearchRadiusDefault, hotelSearchRadiusMax,
            privacyPolicyUrl, privacyPolicyLabel,
            mobileSupportEmail, desktopSupportEmail,
            technicalSupportEnabled, technicalSupportText
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
            data.get('isAdminRoleEnabled', False),
            data.get('isMod2FlowEnabled', False),
            data.get('isFlightSearchServiceEnabled', False),
            data.get('areRecommendationsEnabled', False),
            data.get('isPhoenixHotelSearchEnabled', False),
            data.get('isPhoenixCarRentalSearchEnabled', False),
            data.get('maxNumberOfGuestsPerRoom', 1),
            data.get('isTripAdvisorReviewsEnabled', False),
            data.get('mapProvider', ''),
            data.get('isPerDiemDisplayEnabled', False),
            data.get('isStarRatingsFilterEnabled', False),
            data.get('isHoldTripAllowed', False),
            data.get('isSoldOutFilterAvailable', False),
            data.get('isPreBookCostAllocationEnabled', False),
            data.get('isShowTravelerAcknowledgement', False),
            data.get('isExcludeBasicFareBlock', False),
            data.get('isSouthwestDirectConnectionEnabled', False),
            data.get('isExpiringCreditCardForHotelAllowed', False),
            data.get('isCreditCardSavingEnabled', False),
            data.get('isAppleLockSettingsEnabled', False),
            data.get('appleDsmMessage', ''),
            data.get('enableNearByAirport', False),
            data.get('bookAndChangeAdvanceTime', 0),
            data.get('selfDelegation', False),
            data.get('userDelegation', False),
            data.get('hideUnusedTickets', False),
            data.get('defaultCarSize', ''),
            data.get('isMod2DoubleWriteEnabled', False),
            data.get('geosureReport', {}).get('enabled', False),
            data.get('geosureReport', {}).get('variant', ''),
            data.get('flightSearchTimeRange', {}).get('before', 0),
            data.get('flightSearchTimeRange', {}).get('after', 0),
            data.get('hotelSearchRadius', {}).get('default', 0),
            data.get('hotelSearchRadius', {}).get('max', 0),
            data.get('privacyPolicy', {}).get('url', ''),
            data.get('privacyPolicy', {}).get('label', ''),
            data.get('support', {}).get('mobile', {}).get('email', {}).get('emailAddress', ''),
            data.get('support', {}).get('desktop', {}).get('email', ''),
            data.get('support', {}).get('technicalSupport', {}).get('isEnabled', False),
            data.get('support', {}).get('technicalSupport', {}).get('text', '')
        ))

    display_config_id = cursor.lastrowid

    # Insert External Links
    for link in data.get('externalLinks', {}).get('links', []):
        cursor.execute("""
            INSERT INTO support_external_links (display_config_id, isExternalLinksEnabled, link_url, link_label) 
            VALUES (%s, %s, %s, %s)
        """, (
            display_config_id,
            data['externalLinks'].get('isExternalLinksEnabled', False),
            link.get('url', ''),
            link.get('label', '')
        ))

    # Insert Company Resources
    for resource in data.get('companyResourceConfiguration', {}).get('resourceTexts', []):
        cursor.execute("""
            INSERT INTO company_resources (display_config_id, label, url) 
            VALUES (%s, %s, %s)
        """, (
            display_config_id,
            resource.get('label', ''),
            resource.get('url', '')
        ))


# Function to insert travel preferences
def insert_travel_preferences(data):
    travel_data = data['data']['travelPreferences']['flight']
    
    cursor.execute("""
        INSERT INTO travel_preferences (home_airport, home_airport_label, seat_preference, redress_number, 
                                         redress_number_issuing_country, known_traveler_number, 
                                         known_traveler_issuing_country, results_view, note_to_arranger)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        travel_data.get('homeAirport'),
        travel_data.get('homeAirportLabel'),
        travel_data.get('seatPreference'),
        travel_data.get('redressNumber'),
        travel_data.get('redressNumberIssuingCountry'),
        travel_data.get('knownTravelerNumber'),
        travel_data.get('knownTravelerIssuingCountry'),
        travel_data.get('resultsView'),
        travel_data.get('noteToArranger')
    ))
    
    travel_pref_id = cursor.lastrowid

    # Insert Special Requests
    for special_request in travel_data.get('specialRequest', []):
        cursor.execute("""
            INSERT INTO special_requests (travel_pref_id, label, value) 
            VALUES (%s, %s, %s)
        """, (travel_pref_id, special_request['label'], special_request['value']))
    
    # Insert Loyalty Programs
    for loyalty_program in travel_data.get('loyaltyProgram', []):
        cursor.execute("""
            INSERT INTO loyalty_programs (travel_pref_id, vendor_code, label, number, img_url) 
            VALUES (%s, %s, %s, %s, %s)
        """, (travel_pref_id, loyalty_program['vendorCode'], loyalty_program['label'], loyalty_program['number'], loyalty_program['imgUrl']))
    
    # Insert Meal Options
    for meal_option in travel_data.get('mealOptions', []):
        cursor.execute("""
            INSERT INTO meal_options (travel_pref_id, label, value) 
            VALUES (%s, %s, %s)
        """, (travel_pref_id, meal_option['label'], meal_option['value']))

# Function to insert flights
def insert_flights(data):
    insert_values = []  # List to hold the values for batch insertion
    
    for flight_leg in data['data']['flights']['flightLegs']:
        # Prepare the data values for insertion
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
        distance_value = flight_leg['distance']['value']
        distance_units = flight_leg['distance']['units']
        rate_amount = flight_leg['rate']['primary']['amount']
        rate_currency = flight_leg['rate']['primary']['currency']
        carrier_name = flight_leg['segments'][0]['carrier']['name']
        carrier_id = flight_leg['segments'][0]['carrier']['id']
        service_class = flight_leg['segments'][0].get('serviceClass', 'N/A')  # Handle missing 'serviceClass'

        # Debug: Print the values to ensure everything is in place
        print(f"Inserting flight_leg: {leg_id}")
        print(f"Values: ({leg_id}, {origin}, {destination}, {departure_date}, {arrival_date}, {flight_time_hours}, {flight_time_minutes}, {total_time_hours}, {total_time_minutes}, {flight_stops}, {days_in_between}, {distance_value}, {distance_units}, {rate_amount}, {rate_currency}, {carrier_name}, {carrier_id}, {service_class})")
        
        # Append the values to the list for batch insertion
        insert_values.append((
            leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, flight_time_minutes,
            total_time_hours, total_time_minutes, flight_stops, days_in_between, distance_value, distance_units,
            rate_amount, rate_currency, carrier_name, carrier_id, service_class
        ))

    # Perform batch insertion if there are values to insert
    if insert_values:
        try:
            cursor.executemany("""  -- Use executemany for batch insertion
                INSERT INTO flights (leg_id, origin, destination, departure_date, arrival_date, flight_time_hours, 
                                     flight_time_minutes, total_time_hours, total_time_minutes, flight_stops, days_in_between, 
                                     distance_value, distance_units, rate_amount, rate_currency, carrier_name, carrier_id, service_class)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, insert_values)

            # Commit the transaction
            conn.commit()  # Make sure to commit the changes

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            print(f"Failed to insert flight legs")
            conn.rollback()  # Rollback the transaction on error




# Create tables if not exists
create_tables()

# Read and insert data from JSON files
with open('json/getDisplayConfiguration.json') as f:
    display_data = json.load(f)
    print(display_data)
    insert_display_configuration(display_data)

with open('json/getTravelPreferences.json') as f:
    travel_data = json.load(f)
    insert_travel_preferences(travel_data)

with open('json/getFlights.json') as f:
    flights_data = json.load(f)
    insert_flights(flights_data)

# Commit and close the connection
conn.commit()
cursor.close()
conn.close()
