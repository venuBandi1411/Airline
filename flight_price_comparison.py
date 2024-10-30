from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load dummy flight data from CSV
flights_data = pd.read_csv('flight_price_comparison/flights.csv')

@app.route('/flights/search', methods=['GET'])
def search_flights():
    # Get query parameters from the request
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')

    # Validate input parameters
    if not origin or not destination or not date:
        return jsonify({'message': 'Please provide origin, destination, and date.'}), 400

    # Filter flights based on query parameters
    filtered_flights = flights_data[
        (flights_data['origin'].str.lower() == origin.lower()) &
        (flights_data['destination'].str.lower() == destination.lower()) &
        (flights_data['date'] == date)
    ]

    # Check if any flights were found
    if filtered_flights.empty:
        return jsonify({'message': 'No flights found for the given parameters.'}), 404

    # Sort flights by price (ascending)
    filtered_flights = filtered_flights.sort_values(by='price')

    # Convert filtered data to JSON format
    result = filtered_flights.to_dict(orient='records')

    # Return the result without similarity messages
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5002)