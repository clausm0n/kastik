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

def fetch_latest_data(api_key, ticker, interval_type, time_interval):
    now = datetime.now()
    before = now - timedelta(days=14)
    now_str = now.strftime('%Y-%m-%d')
    before_str = before.strftime('%Y-%m-%d')

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{time_interval}/{interval_type}/{before_str}/{now_str}?apiKey={api_key}"
    response = requests.get(url)
    data = response.json()

    return data.get('results', [])

def generate_targets(y, steps):
    targets = []
    for i in range(len(y) - max(steps)):
        target = [y[i + step] for step in steps]
        targets.append(target)
    return np.array(targets)

def main(api_key, ticker, input_model, input_scaler, interval_type, time_interval):
    load_dotenv()
    model = tf.keras.models.load_model(input_model)
    scaler = joblib.load(input_scaler)
    latest_data = fetch_latest_data(api_key, ticker, interval_type, time_interval)
    df = pd.DataFrame(latest_data)
    df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
    df['EMA_50'] = ta.EMA(df['c'].values, timeperiod=50)
    df['EMA_200'] = ta.EMA(df['c'].values, timeperiod=200)
    df['RSI_14'] = ta.RSI(df['c'].values, timeperiod=14)
    df['RSI_50'] = ta.RSI(df['c'].values, timeperiod=50)
    df.fillna(method='ffill', inplace=True)
    df.dropna(inplace=True)
    data = df[['o', 'h', 'l', 'c', 'EMA_50', 'EMA_200', 'RSI_14', 'RSI_50']].values
    data_scaled = scaler.transform(data)
    sequence_length = 60
    X = []

    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i - sequence_length:i])

    X = np.array(X)

    # Define the future time steps
    future_steps = [1, 3, 6]  # Corresponding to 5, 15, and 30-minute windows for 5-minute intervals
    y_pred = model.predict(X)

    # Get the last prediction
    idx = -1

    # Inverse transform the last price and predicted prices to USD
    temp_array = X[idx][-1].reshape(1, -1).copy()
    actual_last_price_usd = scaler.inverse_transform(X[idx][-1].reshape(1, -1))[0, 3]

    for i, step in enumerate(future_steps):
        temp_array[:, -1] = y_pred[idx, i]
        predicted_price_usd = scaler.inverse_transform(temp_array)[0, 3]
        price_change = predicted_price_usd - actual_last_price_usd
        action = 'BUY' if price_change > 0 else 'SELL'
        print(f"Predicted price in {step * 5} minutes (USD): {predicted_price_usd:.2f}")
        print(f"Price change: {price_change:.5f}")
        print(f"{action}")
        print("\n")

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
