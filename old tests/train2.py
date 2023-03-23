import sys
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tqdm.keras import TqdmCallback

def generate_targets(y, steps, sequence_length):
    targets = []
    for i in range(sequence_length, len(y) - max(steps)):
        target = [y[i + step] for step in steps]
        targets.append(target)
    return np.array(targets)

def main(input_file):
    df = pd.read_csv(input_file)
    df.fillna(method='ffill', inplace=True)
    df.dropna(inplace=True)
    data = df[['o', 'h', 'l', 'c', 'EMA_50', 'EMA_200', 'RSI_14', 'RSI_50']].values
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    sequence_length = 60
    X = []

    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i - sequence_length:i])

    X = np.array(X)

    # Define the future time steps
    future_steps = [1, 3, 6]  # Corresponding to 5, 15, and 30-minute windows for 5-minute intervals
    y = generate_targets(data_scaled[:, 0], future_steps, sequence_length)

    # Adjust the length of X to match the length of y
    X = X[:len(y)]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # model = tf.keras.Sequential([
    #     tf.keras.layers.LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2]), use_bias=True),
    #     tf.keras.layers.Dropout(0.2),
    #     tf.keras.layers.Dense(len(future_steps))
    # ])

    model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2]), use_bias=True),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(len(future_steps))
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(
        X_train,
        y_train,
        epochs=16,
        batch_size=32,
        validation_split=0.1,
        verbose=0,
        callbacks=[TqdmCallback(verbose=2)],
    )

    test_loss = model.evaluate(X_test, y_test)
    print(f'Test loss: {test_loss}')

    model.save('trained_lstm_model.h5')
    joblib.dump(scaler, 'data_scaler.pkl')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
