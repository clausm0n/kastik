import sys
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tqdm.keras import TqdmCallback  # Import the TqdmCallback from tqdm


def main(input_file):
    # Read the historical data with indicators from the CSV file
    df = pd.read_csv(input_file)

    # Preprocessing
    # Fill NaN values using forward fill method and remove any remaining NaNs
    df.fillna(method='ffill', inplace=True)
    df.dropna(inplace=True)

    # Use OHLC and technical indicator data for prediction
    data = df[['o', 'h', 'l', 'c', 'EMA_50', 'EMA_200', 'RSI_14', 'RSI_50']].values

    # Scale the data to the range [0, 1]
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    # Create the input and output sequences for the LSTM model
    sequence_length = 60
    X = []
    y = []

    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i - sequence_length:i])
        y.append(data_scaled[i, 0])  # Predict the next 'Open' price

    X, y = np.array(X), np.array(y)

    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create the LSTM model
    # model = tf.keras.Sequential([
    #     tf.keras.layers.LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), use_bias=True, recurrent_dropout=0.2),
    #     tf.keras.layers.Dense(1)
    # ])
    # updated model
    model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), use_bias=True),
    tf.keras.layers.Dropout(0.2),  # Add a separate dropout layer
    tf.keras.layers.Dense(1)
    ])
    tf.debugging.check_numerics(X_train, "X_train contains NaN or Inf")
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(
        X_train,
        y_train,
        epochs=16,
        batch_size=32,
        validation_split=0.1,
        verbose=0,  # Set verbose to 0 to disable the default progress bar
        callbacks=[TqdmCallback(verbose=2)],  # Add the TqdmCallback to display the progress bar
    )

    # Evaluate the model on test data
    test_loss = model.evaluate(X_test, y_test)
    print(f'Test loss: {test_loss}')

    # Save the trained model
    model.save('trained_lstm_model.h5')

    # Save the scaler
    joblib.dump(scaler, 'data_scaler.pkl')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
