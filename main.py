import argparse
from datetime import datetime
import pandas as pd # pip install pandas
import numpy as np  # pip install numpy
import plotly.graph_objects as go   # pip install plotly
from dotenv import load_dotenv  # pip install python-dotenv
import os
import time
from user import User

import ccxt # pip install ccxt
import talib    # pip install TA-Lib
import cbpro    # pip install cbpro
import base64
import json


DELAY = 5   # in minutes

# initialize APIs and objects
API_KEY = os.environ.get("CBPRO_API_KEY")
SECRET = os.environ.get("CBPRO_SECRET")
PASSPHRASE = os.environ.get("CBPRO_PASSPHRASE")

encoded = json.dumps(SECRET).encode()
b64_secret = base64.b64encode(encoded)

auth_client = cbpro.AuthenticatedClient(key=API_KEY, b64secret=b64_secret, passphrase=PASSPHRASE)
c = cbpro.PublicClient()
exchange = ccxt.coinbasepro()


def get_data(ticker):
    """Gets the data from OHLCV (Open, High, Low, Close, Volume) candles."""

    data = exchange.fetch_ohlcv(ticker, timeframe=f"{DELAY}m", limit=100)
    ticker_df = pd.DataFrame(data, columns=["date", "open", "high", "low", "close", "vol"])
    ticker_df["date"] = pd.to_datetime(ticker_df["date"], unit="ms")
    ticker_df["symbol"] = ticker
    ticker_df.to_csv("data_ticker.csv")

    return ticker_df


def trading_strategy(ticker_data):
    """Basic trading algorithm using Moving Average Convergence/Divergence and Relative Strength Index."""

    macd_conclusion = "WAIT"
    macd_and_rsi_conclusion = "WAIT"

    # Get MACD data
    macd, macdsignal, macdhist = talib.MACD(ticker_data["close"], fastperiod=12, slowperiod=26, signalperiod=9)
    
    last_macdhist = macdhist.iloc[-1]
    prev_macdhist = macdhist.iloc[-2]

    macdhist.to_csv("data_macd.csv")

    if not np.isnan(prev_macdhist) and not np.isnan(last_macdhist):
        # A crossover is occuring if MACD history values change from positive to negative or vice versa.
        macd_crossover = (abs(last_macdhist + prev_macdhist)) != (abs(last_macdhist) + abs(prev_macdhist))

        if macd_crossover:
            macd_verdict = "BUY" if last_macdhist > 0 else "SELL"

    # If MACD determines a BUY or a SELL than check using RSI.
    if macd_conclusion != "WAIT":
        # RSI = 100 – [100 / ( 1 + (Mean Upward Price Change / Mean Downward Price Change))]
        rsi = talib.RSI(ticker_data["close"], timeperiod=14)

        rsi.to_csv("data_rsi.csv")

        # Use last 3 RSI values
        last_rsi_values = rsi.iloc[-3:]

        # RSI is considered overbought when above 70 and oversold when below 30.
        if (last_rsi_values.min() <= 30):
            macd_and_rsi_conclusion = "BUY"

        if (last_rsi_values.max() >= 70):
            macd_and_rsi_conclusion = "SELL"

    return macd_and_rsi_conclusion


def execute_trade(ticker, trade_strategy, investment, holding_qty):
    """Takes the recommended strategy of a BUY or a SELL and executes trade with Coinbase Pro."""

    order_success = False
    side = "buy" if (trade_strategy == "BUY") else "sell"

    try:
        current_ticker_info_response = c.get_product_ticker(product_id=ticker)

        current_price = float(current_ticker_info_response["price"])

        order_size = round(investment / current_price, 5) if trade_strategy == "BUY" else holding_qty

        print(f"Placing order {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: "
                f"{ticker}, {side}, {current_price}, {order_size}, {int(time.time() * 1000)} ")

        order_response = auth_client.place_limit_order(product_id=ticker, side=side, price=current_price, size=order_size)

        try:
            check = order_response["id"]
            check_order = auth_client.get_order(order_id=check)

        except Exception as e:
            print(f"Unable to check order. It might be rejected. {e}")

        if check_order["status"] == "done":
            print("Order has been placed successfully!")
            print(check_order)
            holding_qty = order_size if trade_strategy == "BUY" else holding_qty
            order_success = True

        else:
            print("Order was not matched.")

    except:
        print(f"\nOops. Something went wrong. Unable to place order.")

    return order_success


def cancel_order(order_id):
    c.cancel_order(order_id=order_id)
    return


def plot_data(ticker):
    """Plots the ticker data."""

    # get the ticker data
    ticker_data = get_data(ticker)
    ticker_data["20 sma"] = ticker_data["close"].rolling(20).mean()

    # make the charts
    candlestick = go.Candlestick(
        x = ticker_data.index, 
        open = ticker_data["open"],
        high = ticker_data["high"],
        low = ticker_data["low"],
        close = ticker_data["close"],
    )

    scatter = go.Scatter(
        x = ticker_data.index, 
        y = ticker_data["20 sma"], 
        line = dict(color="mediumaquamarine", width=1)
    )

    fig = go.Figure(data=[candlestick, scatter])

    fig.show()


def main():
    """Main bot script."""

    date_and_time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    holding = False
    while 1: # create infinite loop
        ticker_data = get_data(user.ticker)

        trade_strategy = trading_strategy(ticker_data)
        print(f"{date_and_time_now} Trade Strategy: {trade_strategy}")

        if (trade_strategy == "BUY" and not holding) or (trade_strategy == "SELL" and holding):
            print(f"Placing {trade_strategy} order...")
        
            trade_success = execute_trade(user.ticker, trade_strategy, user.investment, user.holding_qty)
            holding = not holding if trade_success else holding

        time.sleep(DELAY * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="Cryptobot",
        description="A simple python bot to buy and sell btc using a very simple buy and sell strategy."
    )
    parser.add_argument("--version", "-v", action="version", version="%(prog)s v0.1.0")
    parser.add_argument("--ticker", "-t", help="Cryptocurrency ticker symbol.", default="BTC-USDC")
    parser.add_argument("--cancel", "-x", help="Cancel orders.", default=False)
    parser.add_argument("--graph", "-plot", "-xy", help="Plot candlestick interactive chart.", default=False)
    parser.add_argument("--investment", "-usd", "-$", help="Investment amount.", default=10)
    args = parser.parse_args()

    user = User(args.ticker, args.investment)

    if args.cancel:
        pass
    if args.graph:
        plot_data(user.ticker)
    else:
        main()