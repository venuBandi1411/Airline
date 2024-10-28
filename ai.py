import openai
import mysql.connector
import os

# Set up OpenAI API key
openai.api_key = os.getenv("API_KEY")

# Database connection
connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)

def fetch_data_from_table(table_name):
    try:
        cursor = connection.cursor()
        # Dynamically construct the SQL query
        sql_query = f"SELECT * FROM {table_name}"
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        return results
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_user_table_data():
    # Ask the user which table they want to fetch data from
    table_name = input("print the Airlines table data")

    # Fetch and print the requested table's data
    data = fetch_data_from_table(f'ai.{table_name}')
    
    if data:
        print(f"Data from {table_name} table:")
        for row in data:
            print(row)
    else:
        print(f"No data found or error fetching data from {table_name}.")

# Run the function to get user input and fetch data
get_user_table_data()
