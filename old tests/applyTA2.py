import sys
import pandas as pd
import numpy as np
import talib
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def add_technical_indicators(df):
    # Existing indicators
    # ...

    # Additional indicators
    df['ADX'] = talib.ADX(df['h'].values, df['l'].values, df['c'].values, timeperiod=14)
    df['CCI'] = talib.CCI(df['h'].values, df['l'].values, df['c'].values, timeperiod=20)
    df['MFI'] = talib.MFI(df['h'].values, df['l'].values, df['c'].values, df['v'].values, timeperiod=14)

    return df

def create_target_variable(df, shift_periods):
    df['future_c'] = df['c'].shift(-shift_periods)
    df.dropna(inplace=True)
    return df

def create_lag_features(df, lag_periods):
    for i in range(1, lag_periods + 1):
        df[f'c_lag_{i}'] = df['c'].shift(i)
    df.dropna(inplace=True)
    return df

def scale_features(df):
    scaler = MinMaxScaler()
    columns_to_scale = [col for col in df.columns if col != 't']
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    return df

def split_data(df, test_size=0.2, validation_size=0.1):
    df_train, df_test = train_test_split(df, test_size=test_size, shuffle=False)
    df_train, df_val = train_test_split(df_train, test_size=validation_size / (1 - test_size), shuffle=False)
    return df_train, df_val, df_test

def main(input_file):
    # Read the historical data from the CSV file
    df = pd.read_csv(input_file)

    # Ensure the 't' (timestamp) column is of datetime type
    df['t'] = pd.to_datetime(df['t'], unit='ms')

    # Apply the technical indicators
    df = add_technical_indicators(df)

    # Create the target variable
    shift_periods = 1
    df = create_target_variable(df, shift_periods)

    # Create lag features
    lag_periods = 3
    df = create_lag_features(df, lag_periods)

    # Scale the features
    df = scale_features(df)

    # Split the data into training, validation, and testing sets
    df_train, df_val, df_test = split_data(df)

    # Save the updated DataFrames to new CSV files
    df_train.to_csv('train_data.csv', index=False)
    df_val.to_csv('validation_data.csv', index=False)
    df_test.to_csv('test_data.csv', index=False)
    print("Train, validation, and test data saved.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)