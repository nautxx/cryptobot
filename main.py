import argparse
from datetime import datetime
import pandas as pd # pip install pandas
import plotly.graph_objects as go   # pip install plotly
from dotenv import load_dotenv  # pip install python-dotenv
import os
import time
import logging
from user import User
from strategy import *

import ccxt # pip install ccxt
import cbpro    # pip install cbpro
import talib    # pip install TA-Lib
import base64
import json


# initialize APIs and objects
API_KEY = os.environ.get("CBPRO_API_KEY")
SECRET = os.environ.get("CBPRO_SECRET")
PASSPHRASE = os.environ.get("CBPRO_PASSPHRASE")

encoded = json.dumps(SECRET).encode()
b64_secret = base64.b64encode(encoded)

auth_client = cbpro.AuthenticatedClient(key=API_KEY, b64secret=b64_secret, passphrase=PASSPHRASE)
cbpro_client = cbpro.PublicClient()
ccxt_exchange = ccxt.coinbasepro()

# log for debugging
logging.basicConfig(filename="cryptobot.log", format='%(asctime)s %(message)s', filemode='w', level=logging.DEBUG)


def get_data(ticker):
    """Gets the data from OHLCV (Open, High, Low, Close, Volume) candles."""

    data = ccxt_exchange.fetch_ohlcv(ticker, timeframe=f"{user.delay}m", limit=100)
    ticker_df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'vol'])
    ticker_df['date'] = pd.to_datetime(ticker_df['date'], unit="ms")
    ticker_df['symbol'] = ticker

    ticker_df.to_csv("data_ticker.csv")

    return ticker_df

def get_current_data(ticker):
    """Gets the current ticker_data."""

    ticker_data = cbpro_client.get_product_ticker(product_id=ticker)
    return ticker_data


def trading_strategy(ticker_data):
    """The trading logic using any desired combination of functions in strategy.py"""

    # initialize strategy object.
    strat = Strategy()

    if strat.macd_indicator(ticker_data) != "WAIT":
        strat.overall_strategy = strat.rsi_indicator(ticker_data, user.oversold_threshold, user.overbought_threshold)
   
    # older_ticker_data = get_current_data(user.ticker)
    # print(older_ticker_data)
    # time.sleep(5 * 60)
    # current_ticker_data = get_current_data(user.ticker)
    # print(current_ticker_data)

    # strat.overall_strategy = strat.percent_indicator(older_ticker_data, current_ticker_data, 5)

    return strat.overall_strategy


def execute_trade(ticker, trade_strategy, investment, holding_qty):
    """Takes the recommended strategy of a BUY or a SELL and executes trade with Coinbase Pro."""

    order_success = False
    side = "buy" if (trade_strategy == "BUY") else "sell"

    try:
        current_ticker_info_response = cbpro_client.get_product_ticker(product_id=ticker)
    
    except:
        print(f"\n🤖: Boooops. Something went wrong. Unable to place order.")

    try:
        current_price = float(current_ticker_info_response['price'])
    
    except Exception as e:
        print(f"🤖: Error obtaining ticker data. {e}")

        order_size = round(investment / current_price, 5) if trade_strategy == "BUY" else holding_qty

        print(f"🤖: Placing order {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: "
            f"{ticker}, {side}, {current_price}, {order_size}, {int(time.time() * 1000)}"
        )

    try:
        order_response = auth_client.place_limit_order(product_id=ticker, side=side, price=current_price, size=order_size)

    except Exception as e:
        print(f"🤖: Error placing order. {e}")

    try:
        check = order_response["id"]
        logging.info(check)
        check_order = auth_client.get_order(order_id=check)

    except Exception as e:
        print(f"🤖: Unable to check order. {e}")

    if check_order['status'] == "done":
        print("🤖: Order has been placed successfully BOOPboopboop!")
        print(check_order)
        holding_qty = order_size if trade_strategy == "BUY" else holding_qty
        order_success = True

    else:
        print("🤖: Order was not matched.")

    return order_success


def cancel_order(order_id):
    cbpro_client.cancel_order(order_id=order_id)
    return


def plot_data(ticker):
    """Plots the ticker data."""

    # get the ticker data
    ticker_data = get_data(ticker)
    ticker_data['20 sma'] = ticker_data['close'].rolling(20).mean()

    # make the charts
    candlestick = go.Candlestick(
        x = ticker_data.index, 
        open = ticker_data['open'],
        high = ticker_data['high'],
        low = ticker_data['low'],
        close = ticker_data['close'],
        name = f"{ticker}",
    )

    line = go.Scatter(
        x = ticker_data.index, 
        y = ticker_data['20 sma'], 
        line = dict(color="blue", width=2),
        name = f"20 sma",
    )

    fig = go.Figure(data=[candlestick, line])
    fig.update_layout(title=f"{ticker} Candlestick Chart")
    fig.show()


def main():
    """Main bot script."""

    holding = False
    while True: # create infinite loop
        ticker_data = get_data(user.ticker)
        trade_strategy = trading_strategy(ticker_data)

        date_and_time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")    # get and use date_and_time_now at time of message
        print(f"{date_and_time_now} 🤖: Beep Bop Boop {trade_strategy}.")

        if (trade_strategy == "BUY" and not holding) or (trade_strategy == "SELL" and holding):
            print(f"🤖: Attempting to place {trade_strategy} order BOOOOOP...")
        
            trade_success = execute_trade(user.ticker, trade_strategy, user.investment, user.holding_qty)
            holding = not holding if trade_success else holding

        time.sleep(user.delay * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="🤖cryptobot by naut 2022",
        description="A python bot to buy and sell cryptocurrency using a basic buy and sell strategy.",
        epilog="Enjoy but please run at your own risk."
    )
    parser.add_argument("--version", "-v", action="version", version="%(prog)s v0.1.0")
    parser.add_argument("--ticker", "-t", help="cryptocurrency ticker symbol. default=BTC-USDC", default="BTC-USDC", type=str)
    parser.add_argument("--cancel", "-x", help="cancel orders.", action="store_true")
    parser.add_argument("--graph", "-plot", "-xy", help="plot a candlestick interactive chart.", action="store_true")
    parser.add_argument("--investment", "-usd", "-$", help="investment amount. default=10", default=10, type=int)
    parser.add_argument("--delay", "-d", help="delay in minutes. default=5", default=5, type=int)
    parser.add_argument("--oversold", "-os", help="rsi oversold threshold.", default=None, type=int)
    parser.add_argument("--overbought", "-ob", help="rsi overbought threshold.", default=None, type=int)
    args = parser.parse_args()


    # Initialize user settings
    user = User(
        ticker=args.ticker, 
        investment=args.investment, 
        rsi_oversold=args.oversold, 
        rsi_overbought=args.overbought, 
        delay=args.delay
    )

    if args.cancel:
        pass
    if args.graph:
        plot_data(args.ticker)
    else:
        main()