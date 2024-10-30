from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Flight model
class Flight(db.Model):
    __tablename__ = 'price_tracker'
    
    id = db.Column(db.Integer, primary_key=True)
    airline = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2))
    departure_time = db.Column(db.DateTime)
    arrival_time = db.Column(db.DateTime)
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    date = db.Column(db.Date)
    source = db.Column(db.String(100))

@app.route('/flights/search', methods=['GET'])
def search_flights():
    # Get query parameters from the request
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')

    # Validate input parameters
    if not origin or not destination or not date:
        return jsonify({'message': 'Please provide origin, destination, and date.'}), 400

    # Query the database for flights matching the criteria
    filtered_flights = Flight.query.filter(
        Flight.origin.ilike(origin),
        Flight.destination.ilike(destination),
        Flight.date == date
    ).order_by(Flight.price).all()

    # Check if any flights were found
    if not filtered_flights:
        return jsonify({'message': 'No flights found for the given parameters.'}), 404

    # Convert filtered data to JSON format
    result = [
        {
            'airline': flight.airline,
            'price': str(flight.price),  # Convert Decimal to string for JSON serialization
            'departure_time': flight.departure_time.isoformat(),
            'arrival_time': flight.arrival_time.isoformat(),
            'origin': flight.origin,
            'destination': flight.destination,
            'date': flight.date.isoformat(),
            'source': flight.source,
        }
        for flight in filtered_flights
    ]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5003)