import os
import sys
import requests
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
import talib as ta
from datetime import datetime, timedelta
from dotenv import load_dotenv

# def fetch_latest_data(api_key, ticker):
#     # Fetch the last 3 days of data from Polygon.io
#     now = datetime.now()
#     before = now - timedelta(days=3)
#     now_str = now.strftime('%Y-%m-%d')
#     before_str = before.strftime('%Y-%m-%d')

#     url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/5/minute/{before_str}/{now_str}?apiKey={api_key}"
#     response = requests.get(url)
#     data = response.json()

#     print("Fetched data:", data)  # Add this line to see the fetched data

#     return data.get('results', [])

def fetch_latest_data(api_key, ticker, interval_type, time_interval):
    # Fetch the last 3 days of data from Polygon.io
    now = datetime.now()
    before = now - timedelta(days=14)
    now_str = now.strftime('%Y-%m-%d')
    before_str = before.strftime('%Y-%m-%d')

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{time_interval}/{interval_type}/{before_str}/{now_str}?apiKey={api_key}"
    response = requests.get(url)
    data = response.json()

    return data.get('results', [])

def main(api_key, ticker, input_model, input_scaler, interval_type, time_interval):
    # Load the trained model and scaler
    load_dotenv()
    model = tf.keras.models.load_model(input_model)
    scaler = joblib.load(input_scaler)

    # Fetch the latest data for the given ticker
    latest_data = fetch_latest_data(api_key, ticker, interval_type, time_interval)

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(latest_data)

    # Ensure the timestamp column is of datetime type
    df['timestamp'] = pd.to_datetime(df['t'], unit='ms')

    # Compute technical indicators
    df['EMA_50'] = ta.EMA(df['c'].values, timeperiod=50)
    df['EMA_200'] = ta.EMA(df['c'].values, timeperiod=200)
    df['RSI_14'] = ta.RSI(df['c'].values, timeperiod=14)
    df['RSI_50'] = ta.RSI(df['c'].values, timeperiod=50)

    # Fill NaN values using forward fill method and remove any remaining NaNs
    df.fillna(method='ffill', inplace=True)
    df.dropna(inplace=True)

    # Preprocess the data
    data = df[['o', 'h', 'l', 'c', 'EMA_50', 'EMA_200', 'RSI_14', 'RSI_50']].values
    data_scaled = scaler.transform(data)

    # Create input sequences for the LSTM model
    sequence_length = 60
    X = []

    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i - sequence_length:i])

    X = np.array(X)

    # Make predictions using the trained model
    y_pred = model.predict(X)
    idx = -1  # Get the last prediction

#  # Inverse transform the last price and predicted price to USD
#     temp_array = X[idx][-1].reshape(1, -1).copy()
#     temp_array[:, -1] = y_pred[idx]
#     actual_last_price_usd = scaler.inverse_transform(X[idx][-1].reshape(1, -1))[0, 3]
#     predicted_next_price_usd = scaler.inverse_transform(temp_array)[0, 3]

#     print(f"Actual last price (USD): {actual_last_price_usd:.2f}")
#     print(f"Predicted next price (USD): {predicted_next_price_usd:.2f}")
#     print(f"Price change: {price_change[idx][0]:.5f}")

#     action = 'BUY' if y_pred[idx] > data_scaled[-1, 0] else 'SELL'
#     print(f"{action} with a profit estimate of {profit_estimates[idx][0]:.2f}% and a probability of {probability_percentages[idx][0]:.2f}%")
  # Inverse transform the last price and predicted price to USD
    temp_array = X[idx][-1].reshape(1, -1).copy()
    temp_array[:, -1] = y_pred[idx]
    actual_last_price_usd = scaler.inverse_transform(X[idx][-1].reshape(1, -1))[0, 3]
    predicted_next_price_usd = scaler.inverse_transform(temp_array)[0, 3]

    price_change = predicted_next_price_usd - actual_last_price_usd

    print(f"Actual last price (USD): {actual_last_price_usd:.2f}")
    print(f"Predicted next price (USD): {predicted_next_price_usd:.2f}")
    print(f"Price change: {price_change:.5f}")

    action = 'BUY' if y_pred[idx] > data_scaled[-1, 0] else 'SELL'
    print(f"{action}")



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python script.py <input_model> <input_scaler>")
        sys.exit(1)

    load_dotenv()
    api_key = os.getenv('API_KEY')
    ticker = os.getenv('TICKER')
    interval_type = os.getenv('INTERVALTYPE')
    time_interval = os.getenv('TIMEINTERVAL')
    input_model = sys.argv[1]
    input_scaler = sys.argv[2]

    main(api_key, ticker, input_model, input_scaler, interval_type, time_interval)
