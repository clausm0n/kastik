import tensorflow as tf


def create_model(X_train, y_train, X_test, y_test):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(128, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation='tanh')
    ])

    model.compile(optimizer='adam', loss='mse')

    history = model.fit(X_train, y_train, epochs=50, batch_size=64, validation_data=(X_test, y_test))
    print(history.history.keys())

    # Evaluate the model
    test_loss = model.evaluate(X_test, y_test)
    print('Test loss:', test_loss)

    # Make predictions
    predictions = model.predict(X_test)
    print('Predictions:', predictions)

    # Save the model
    model.save('btc_usd_lstm_model.h5')