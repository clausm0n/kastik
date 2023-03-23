import os
import requests

# Load the API key from the .env file
from dotenv import load_dotenv



def getTick():
    load_dotenv()
    api_key = os.getenv('API_KEY')
    pair_a = os.getenv('PAIRA')
    pair_b = os.getenv('PAIRB')

    # Define the API endpoint URL template for v2
    url_template = "https://api.polygon.io/v1/last/crypto/{symbol}?apiKey={api_key}"

    # Define the symbol to fetch the latest tick for
    symbol = pair_a + "/" + pair_b
    symbolh = os.getenv('TICKER')

    # Replace the URL template placeholders with the actual values
    url = url_template.format(symbol=symbol, api_key=api_key)

    # Make the API request and retrieve the JSON response
    response = requests.get(url)
    data = response.json()

    # Extract the relevant fields from the response
    last_price = data['last']['price']
    last_timestamp = data['last']['timestamp']

    # # Fetch historical data using Polygon API
    # # Adjust the time range and interval as needed
    # historical_url = f"https://api.polygon.io/v2/aggs/ticker/{symbolh}/range/1/day/2023-01-01/2023-03-01?apiKey={api_key}"
    # historical_response = requests.get(historical_url)
    # historical_data = historical_response.json()

    return last_price, last_timestamp