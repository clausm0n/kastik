import sys
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

def main(input_file):
    # Read the historical data from the CSV file
    df = pd.read_csv(input_file)

    # Initialize the Dash app
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Historical Data Visualization"),
        dcc.Dropdown(
            id="indicator_dropdown",
            options=[
                {"label": "EMA (50)", "value": "EMA_50"},
                {"label": "EMA (200)", "value": "EMA_200"},
                {"label": "Bollinger Bands (20)", "value": "BB_20"},
                {"label": "Bollinger Bands (100)", "value": "BB_100"},
                {"label": "RSI (14)", "value": "RSI_14"},
                {"label": "RSI (50)", "value": "RSI_50"},
            ],
            multi=True,
            placeholder="Select Indicators",
        ),
        dcc.Graph(id="candlestick_chart"),
    ])

    @app.callback(
        Output("candlestick_chart", "figure"),
        [Input("indicator_dropdown", "value")],
    )
    def update_candlestick_chart(indicators):
        traces = []

        # Add the main candlestick chart
        traces.append(go.Candlestick(
            x=df["t"],
            open=df["o"],
            high=df["h"],
            low=df["l"],
            close=df["c"],
            name="Candlesticks",
        ))

        # Add the selected indicators
        if indicators:
            for indicator in indicators:
                if "BB" in indicator:
                    if "20" in indicator:
                        traces.append(go.Scatter(x=df["t"], y=df["upper_BB_20"], mode="lines", name="Upper BB (20)"))
                        traces.append(go.Scatter(x=df["t"], y=df["middle_BB_20"], mode="lines", name="Middle BB (20)"))
                        traces.append(go.Scatter(x=df["t"], y=df["lower_BB_20"], mode="lines", name="Lower BB (20)"))
                    elif "100" in indicator:
                        traces.append(go.Scatter(x=df["t"], y=df["upper_BB_100"], mode="lines", name="Upper BB (100)"))
                        traces.append(go.Scatter(x=df["t"], y=df["middle_BB_100"], mode="lines", name="Middle BB (100)"))
                        traces.append(go.Scatter(x=df["t"], y=df["lower_BB_100"], mode="lines", name="Lower BB (100)"))
                else:
                    traces.append(go.Scatter(x=df["t"], y=df[indicator], mode="lines", name=indicator))

        return {"data": traces}

    app.run_server(debug=True, host='127.0.0.1')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dash_viz.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
