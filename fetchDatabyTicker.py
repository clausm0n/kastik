import argparse
import requests
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv



# Load the API key, ticker, and other settings from the .env file
load_dotenv()
api_key = os.getenv('API_KEY')
ticker = os.getenv('TICKER')
timeunit = os.getenv('TIMEUNIT')
timespan = os.getenv('TIMESPAN')
timeinterval = int(os.getenv('TIMEINTERVAL'))
intervaltype = os.getenv('INTERVALTYPE')
timeamount = int(os.getenv('TIMEAMOUNT'))

today = datetime.date.today()

# Calculate the start date based on the time unit and time amount
if timeunit.lower() == 'years':
    window = today - relativedelta(years=timeamount)
elif timeunit.lower() == 'months':
    window = today - relativedelta(months=timeamount)
elif timeunit.lower() == 'days':
    window = today - relativedelta(days=timeamount)
else:
    raise ValueError("Invalid TIMEUNIT value. Please use 'years', 'months', or 'days'.")

# Define the API endpoint URL template
url_template = "https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}?apiKey={api_key}"

# Set the interval based on the time interval and interval type
multiplier = timeinterval

# Update the timespan value based on the interval type
timespan = intervaltype

# Function to fetch data for a specific date range
def fetch_data(from_date, to_date):
    print(timespan, multiplier, from_date, to_date)
    url = url_template.format(ticker=ticker, multiplier=multiplier, timespan=timespan,
                              from_date=from_date, to_date=to_date, api_key=api_key)
    response = requests.get(url)
    data = response.json()
    return data.get('results', [])
# Fetch data in smaller chunks (e.g., one month at a time)
all_data = []
start_date = window
total_chunks = (today - window).days // 30
current_chunk = 1

while start_date < today:
    end_date = start_date + relativedelta(days=30)
    if end_date > today:
        end_date = today
    print(f"Fetching data for {ticker} from {start_date} to {end_date} ({current_chunk}/{total_chunks})")
    chunk_data = fetch_data(start_date, end_date)
    all_data.extend(chunk_data)
    start_date = end_date
    current_chunk += 1

# Convert the data to a pandas DataFrame and save it to a CSV file
df = pd.DataFrame(all_data)
output_file = f"data/{ticker}_{multiplier}_{timespan}_historical_data.csv"
df.to_csv(output_file, index=False)
print(f"Data for {ticker} saved to {output_file}")
