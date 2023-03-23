import sys
import pandas as pd
import talib

def add_technical_indicators(df):
    # Calculate the EMA with a 50-period and 200-period window
    df['EMA_50'] = talib.EMA(df['c'].values, timeperiod=50)
    df['EMA_200'] = talib.EMA(df['c'].values, timeperiod=200)

    # Calculate the Bollinger Bands with a 20-period and 100-period window
    df['upper_BB_20'], df['middle_BB_20'], df['lower_BB_20'] = talib.BBANDS(df['c'].values, timeperiod=20)
    df['upper_BB_100'], df['middle_BB_100'], df['lower_BB_100'] = talib.BBANDS(df['c'].values, timeperiod=100)

    # Calculate the RSI with a 14-period and 50-period window
    df['RSI_14'] = talib.RSI(df['c'].values, timeperiod=14)
    df['RSI_50'] = talib.RSI(df['c'].values, timeperiod=50)

    # Calculate the MACD with 12 and 26 period windows
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['c'].values, fastperiod=12, slowperiod=26, signalperiod=9)

    return df

def main(input_file):
    # Read the historical data from the CSV file
    df = pd.read_csv(input_file)

    # Ensure the 't' (timestamp) column is of datetime type
    df['t'] = pd.to_datetime(df['t'], unit='ms')

    # Apply the technical indicators
    df = add_technical_indicators(df)

    # Save the updated DataFrame to a new CSV file
    output_file = input_file.replace('.csv', '_with_indicators.csv')
    df.to_csv(output_file, index=False)
    print(f"Data with indicators saved to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)