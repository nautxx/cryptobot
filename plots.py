import plotly.graph_objects as go   # pip install plotly

class Plots:
    def __init__(self):
        pass

    
    def candlestick_sma(self, ticker_data, sma):
        """Plots the ticker data."""

        # get the ticker data
        ticker = ticker_data['symbol'][1]
        ticker_data[f'sma-{sma}'] = ticker_data['close'].rolling(sma).mean() # simple moving average

        # make the charts
        candlestick = go.Candlestick(
            x = ticker_data.index, 
            open = ticker_data['open'],
            high = ticker_data['high'],
            low = ticker_data['low'],
            close = ticker_data['close'],
            name = ticker,
        )

        line = go.Scatter(
            x = ticker_data.index, 
            y = ticker_data[f'sma-{sma}'], 
            line = dict(color="purple", width=2),
            name = f"sma-{sma}",
        )

        fig = go.Figure(data=[candlestick, line])
        fig.update_layout(title=f"{ticker} Candlestick Chart")
        fig.show()