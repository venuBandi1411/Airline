# Re-importing pandas since the environment reset
import pandas as pd

# Data provided
data = {
    'id': [1, 2, 3, 4, 5, 31],
    'legId': ['15/LAX-DFW/NK3710', '15/LAX-DFW/DL3711', '15/LAX-DFW/WN3712', '15/LAX-DFW/AS3713', '15/LAX-DFW/UA3714', '15/LAX-DFW/UA3715'],
    'flightTimeHours': [3, 3, 3, 3, 3, 3],
    'flightTimeMinutes': [8, 8, 10, 5, 15, 15],
    'totalTimeHours': [3, 3, 3, 3, 3, 3],
    'totalTimeMinutes': [8, 8, 10, 5, 15, 15],
    'daysInBetween': [1, 1, 1, 1, 1, 1],
    'flightStops': [0, 0, 0, 0, 0, 0],
    'stops': [0, 1, 0, 0, 0, 2],
    'origin': ['LAX', 'LAX', 'LAX', 'LAX', 'LAX', 'LAX'],
    'destination': ['DFW', 'DFW', 'DFW', 'DFW', 'DFW', 'DFW'],
    'departureDate': ['2024-10-16 11:52:00', '2024-10-16 12:00:00', '2024-10-16 14:00:00', '2024-10-17 18:00:00', '2024-10-18 20:00:00', '2024-10-18 21:00:00'],
    'arrivalDate': ['2024-10-16 14:52:00', '2024-10-16 16:00:00', '2024-10-16 17:10:00', '2024-10-17 21:05:00', '2024-10-18 23:15:00', '2024-10-19 03:15:00'],
    'distanceValue': [1231, 1231, 1231, 1231, 1231, 1231],
    'distanceUnits': ['MI', 'MI', 'MI', 'MI', 'MI', 'MI'],
    'isSelectable': [1, 1, 1, 1, 1, 1],
    'hasTechnicalStop': [0, 0, 0, 0, 0, 0],
    'travel_preference_id': [None, None, None, None, None, None],
    'match_preferences': [True, True, True, True, True, True],
    'mealPreference': ['Vegetarian', 'Non-Vegetarian', 'Vegan', 'Vegetarian', 'Non-Vegetarian', 'Vegan'],
    'loyaltyProgram': ['None', 'Gold', 'Silver', 'None', 'Gold', 'Silver'],
    'seatPreference': ['Window', 'Aisle', 'Exit Row', 'Window', 'Aisle', 'Exit Row'],
    'travelDates': ['2024-10-16', '2024-10-17', '2024-10-18', '2024-10-19', '2024-10-20', '2024-10-18']
}

# Create DataFrame
df = pd.DataFrame(data)

# Saving the DataFrame to a CSV file
csv_file_path = "flight_data.csv"
df.to_csv(csv_file_path, index=False)
