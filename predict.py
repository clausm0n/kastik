import os
import tensorflow as tf
from tensorflow.keras import backend as K
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONHASHSEED'] = '0'
tf.get_logger().setLevel('ERROR')
from fetchLatestTick import getTick
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from preprocessData import preprocess_live_data
from fetchFlashHistory import getFlashHistory
import json
loaded_model = tf.keras.models.load_model('btc_usd_lstm_model.h5')


def infer():

    # Fetch the live data
    live_data = getTick()

    getFlashHistory()
    # Load your historical dataset (you can use the same CSV file you used for training)
    historical_data = pd.read_csv('data/flash_historical_data.csv', skiprows=1, names=['volume', 'vw', 'open', 'close', 'high', 'low', 'timestamp', 'n'])

    # Prepare live data (similar to how you preprocessed the historical data)
    preprocessed_live_data = preprocess_live_data(live_data, historical_data)

    # Reshape the preprocessed_live_data to match the input shape of the LSTM model
    live_input = preprocessed_live_data.reshape(1, preprocessed_live_data.shape[0], preprocessed_live_data.shape[1])

    # Make a prediction using the live data
    live_prediction = loaded_model.predict(live_input, verbose=0)
    #print(live_prediction)
    buy_threshold = 0.1
    sell_threshold = -0.1
    command = ""
    if live_prediction > buy_threshold:
        command = "BUY"
    elif live_prediction < sell_threshold:
        command = "SELL"
    else:
        command = "HOLD"
    dec = {
        "prediction": live_prediction[0][0].astype(float),
        "command": command
    }

    print(dec)
    return dec