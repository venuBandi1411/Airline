import pandas as pd  
from datetime import datetime, timedelta  
  
# Load the original data  
df = pd.read_csv('flight_data.csv')  
  
# Get the current date  
today = datetime.today()  
  
# Define the number of days to generate duplicate data for  
num_days = 30  
  
# Create a list to store the duplicate data  
duplicate_data = []  
  
# Loop through each row in the original data  
for index, row in df.iterrows():  
  departure_date = datetime.strptime(row['departureDate'], '%Y-%m-%d %H:%M:%S')  
  arrival_date = datetime.strptime(row['arrivalDate'], '%Y-%m-%d %H:%M:%S')  
  
  for day in range(num_days):  
    new_departure_date = departure_date + timedelta(days=day)  
    new_arrival_date = arrival_date + timedelta(days=day)  
  
    new_row = row.copy()  
    new_row['departureDate'] = new_departure_date.strftime('%Y-%m-%d %H:%M:%S')  
    new_row['arrivalDate'] = new_arrival_date.strftime('%Y-%m-%d %H:%M:%S')  
  
    duplicate_data.append(new_row)

  
# Convert the duplicate data list to a Pandas DataFrame  
duplicate_df = pd.DataFrame(duplicate_data)  
  
# Save the duplicate data to a new CSV file  
duplicate_df.to_csv('duplicate_flight_data.csv', index=False)
