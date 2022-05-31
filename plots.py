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

    
    def line_sma(self, ticker_data):

        period_1 = 26
        period_2 = 12
        period_3 = 9

        # get the ticker data
        ticker = ticker_data['symbol'][1]   # grab ticker name
        ticker_data['sma-26'] = ticker_data['close'].rolling(period_1).mean() # simple moving average
        # ticker_data['sma-12'] = ticker_data['close'].rolling(period_2).mean() # simple moving average
        ticker_data['signal'] = ticker_data['close'].rolling(period_3).mean() # simple moving average

        line_closing = go.Scatter(
            x = ticker_data.index, 
            y = ticker_data['close'], 
            line = dict(color="red", width=1),
            name = "closing price",
        )
        line_sma_1 = go.Scatter(
            x = ticker_data.index, 
            y = ticker_data['sma-26'], 
            line = dict(color="green", width=2),
            name = "sma-26",
        )
        # line_sma_2 = go.Scatter(
        #     x = ticker_data.index, 
        #     y = ticker_data['sma-12'], 
        #     line = dict(color="blue", width=1),
        #     name = "sma-12",
        # )
        line_signal = go.Scatter(
            x = ticker_data.index, 
            y = ticker_data['signal'], 
            line = dict(color="blue", width=2),
            name = "signal",
        )

        fig = go.Figure(data=[line_closing, line_sma_1, line_signal])
        fig.update_layout(title=f"{ticker} Price x Simple Moving Averages")
        fig.show()