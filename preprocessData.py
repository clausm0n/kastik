import pandas as pd
import numpy as np
import os
from ta import add_all_ta_features
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
# Load the API key from the .env file
from dotenv import load_dotenv
import warnings

def replace_nan_with_zero(df):
    return df.fillna(value=0)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    def preprocess_data():
        load_dotenv()
        api_key = os.getenv('API_KEY')
        ticker = os.getenv('TICKER')
        timeunit = os.getenv('TIMEUNIT')
        timespan = os.getenv('TIMESPAN')
        timeinterval = int(os.getenv('TIMEINTERVAL'))
        intervaltype = os.getenv('INTERVALTYPE')
        timeamount = int(os.getenv('TIMEAMOUNT'))
        # Set the interval based on the time interval and interval type
        multiplier = timeinterval

        # Update the timespan value based on the interval type
        timespan = intervaltype
        # Load your dataset
        filename = 'data/{ticker}_{multiplier}_{timespan}_historical_data.csv'.format(
        ticker=ticker,
        multiplier=multiplier,
        timespan=timespan
    )
        data = pd.read_csv(filename, skiprows=1, names=['volume', 'vw', 'open', 'close', 'high', 'low', 'timestamp', 'n'])

        # Convert timestamp to datetime and set it as index
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)

        # Calculate TA indicators
        data = add_all_ta_features(data, open="open", high="high", low="low", close="close", volume="volume")

        # Remove unnecessary columns
        data.drop(columns=['vw', 'n'], inplace=True)

        # convert rows containing NaN values
        data = replace_nan_with_zero(data)
        #data.dropna(inplace=True)
        print(data)
        # Select relevant features and labels
        features = data.drop(columns=['open', 'high', 'low', 'close', 'volume']).values
        labels = data['close'].shift(-1).dropna().values

        # Normalize the data
        scaler = MinMaxScaler()
        features = scaler.fit_transform(features)

        # Create input sequences and corresponding target values
        seq_length = 60  # Sequence length for the LSTM model
        X, y = [], []

        for i in range(len(features) - seq_length):
            X.append(features[i:i + seq_length])
            # y.append(np.sign(labels[i + seq_length - 1] - labels[i + seq_length - 2]))
            # Add a small constant value, e.g., 1e-8, to the sign function to prevent zero values
            y.append(np.sign(labels[i + seq_length - 1] - labels[i + seq_length - 2] + 1e-8))

        X = np.array(X)
        y = np.array(y)

        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        return X_train, X_test, y_train, y_test

# # Load the model for live trading
# loaded_model = tf.keras.models.load_model('btc_usd_lstm_model.h5')




# buy_threshold = 0.5
# sell_threshold = -0.5

# if live_prediction > buy_threshold:
#     print("BUY")
# elif live_prediction < sell_threshold:
#     print("SELL")
# else:
#     print("HOLD")

    # # Prepare live data (similar to how you preprocessed the historical data)
    def preprocess_live_data(live_data, historical_data):
        last_price, last_timestamp = live_data

        # Convert the live data to a DataFrame
        live_df = pd.DataFrame({"timestamp": [last_timestamp], "open": [last_price], "high": [last_price], "low": [last_price], "close": [last_price], "volume": [0]})

        # Append the live data to the historical data
        combined_data = historical_data.append(live_df, ignore_index=True)

        # Convert timestamp to datetime and set it as index
        combined_data['timestamp'] = pd.to_datetime(combined_data['timestamp'], unit='ms')
        combined_data.set_index('timestamp', inplace=True)

        # Calculate TA indicators
        combined_data = add_all_ta_features(combined_data, open="open", high="high", low="low", close="close", volume="volume")

        # Remove unnecessary columns
        combined_data.drop(columns=['vw', 'n'], inplace=True)

        # Replace NaN values with zeros
        combined_data = replace_nan_with_zero(combined_data)

        # Select relevant features
        features = combined_data.drop(columns=['open', 'high', 'low', 'close', 'volume']).values

        # Normalize the data
        scaler = MinMaxScaler()
        features = scaler.fit_transform(features)

        # Use the last 60 samples for live prediction
        live_input = features[-60:]

        return live_input