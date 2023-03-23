#!/bin/bash

# Fetch data
echo "Fetching data..."
python fetchDatabyTicker.py

# Get the output file name from fetchDatabyTicker.py
source .env
ticker=$(echo $TICKER | tr -d '[:space:]')
multiplier=$(echo $TIMEINTERVAL | tr -d '[:space:]')
timespan=$(echo $INTERVALTYPE | tr -d '[:space:]')
output_file="data/${ticker}_${multiplier}_${timespan}_historical_data.csv"

# Apply technical indicators
echo "Applying technical indicators..."
python applyTA.py ${output_file}

output_file_with_indicators=${output_file%.csv}_with_indicators.csv

# Train the model
echo "Training the model..."
python train2.py ${output_file_with_indicators}

input_model='trained_lstm_model.h5'
input_scaler='data_scaler.pkl'

# Inference
echo "Running inference..."
python infer2.py ${input_model} ${input_scaler}

echo "Done!"
