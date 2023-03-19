import sys
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

external_stylesheets = [
    {
        "href": "https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
        "rel": "stylesheet",
        "integrity": "sha384-pzjw8f+ua7Kw1TIq0v8FqFjcJ6pajs/rfdfs3SO+kD4Ck5BdPtF+to8xMp9MvcJ5",
        "crossorigin": "anonymous",
    }
]

def main(input_file):
    # Read the historical data from the CSV file
    df = pd.read_csv(input_file)

    # Initialize the Dash app
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        html.Div([
            html.H1("Historical Data Visualization"),
            html.P("Select technical indicators to display on the candlestick chart."),
        ], className="jumbotron text-center"),
        html.Div([
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
        ], className="container mb-4"),
        html.Div([
            dcc.Graph(id="candlestick_chart"),
        ], className="container"),
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
            increasing_line_color="#17BECF",
            decreasing_line_color="#7F7F7F",
        ))

        # Add the selected indicators
        if indicators:
            for indicator in indicators:
                if "BB" in indicator:
                    if "20" in indicator:
                        traces.append(go.Scatter(x=df["t"], y=df["upper_BB_20"], mode="lines", name="Upper BB (20)", line=dict(color="#FF5733")))
                        traces.append(go.Scatter(x=df["t"], y=df["middle_BB_20"], mode="lines", name="Middle BB (20)", line=dict(color="#FFC300")))
                        traces.append(go.Scatter(x=df["t"], y=df["lower_BB_20"], mode="lines", name="Lower BB (20)", line=dict(color="#FF5733")))
                    elif "100" in indicator:
                        traces.append(go.Scatter(x=df["t"], y=df["upper_BB_100"], mode="lines", name="Upper BB (100)", line=dict(color="#DAF7A6")))
                        traces.append(go.Scatter(x=df["t"], y=df["middle_BB_100"], mode="lines", name="Middle BB (100)", line=dict(color="#C39BD3")))
                        traces.append(go.Scatter(x=df["t"], y=df["lower_BB_100"], mode="lines", name="Lower BB (100)", line=dict(color="#DAF7A6")))
                else:
                    traces.append(go.Scatter(x=df["t"], y=df[indicator], mode="lines", name=indicator, line=dict(color="#BB8FCE")))

        return {
            "data": traces,
            "layout": go.Layout(
                xaxis={"title": "Date"},
                yaxis={"title": "Price"},
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)",
                font={"color": "#2C3E50"},
            ),
        }

    app.run_server(debug=True, host='127.0.0.1')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dash_visualization.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)

