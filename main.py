import argparse
from datetime import datetime
import pandas as pd # pip install pandas
from dotenv import load_dotenv  # pip install python-dotenv
import os
import time
import logging
from user import User
from strategy import *
from plots import *
from trade import Trade

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
    """Uses CCXT to get the data from OHLCV (Open, High, Low, Close, Volume) candles."""

    data = ccxt_exchange.fetch_ohlcv(ticker, timeframe=f"{user.delay}m", limit=150)
    ticker_df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'vol'])
    ticker_df['date'] = pd.to_datetime(ticker_df['date'], unit="ms")
    ticker_df['symbol'] = ticker

    ticker_df.to_csv("data_ticker.csv")

    return ticker_df


def get_current_data(ticker):
    """Uses coinbasepro to get the current ticker information."""

    ticker_data = cbpro_client.get_product_ticker(product_id=ticker)
    return ticker_data


def trading_strategy(ticker_data):
    """The trading logic using any desired combination of functions in strategy.py"""

    # initialize strategy object.
    strat = Strategy()

    if args.mean_reversion:
        strat.mean_reversion_strategy(ticker_data)
    if args.mean_reversion_simple:
        strat.simple_mean_reversion_strategy(ticker_data)
    if args.basic:
        strat.basic_strategy(ticker_data)

    # oldest_ticker_data = get_current_data(user.ticker)
    # print(old_ticker_data)
    # time.sleep(5 * 60)
    # newest_ticker_data = get_current_data(user.ticker)
    # print(newest_ticker_data)

    # strat.overall_strategy = strat.percent_indicator(oldest_ticker_data, newest_ticker_data)

    return strat.overall_strategy

#TODO move away execute_trade function from main.py
def execute_trade(ticker, trade_strategy, investment, holding_qty):
    """Takes the recommended strategy of BUY or SELL and executes trade with Coinbase Pro."""

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


def plot_bot():
    """Main plot script."""

    # initialize Plot class.
    plot = Plots()

    # get ticker data
    ticker_data = get_data(args.ticker)

    if args.candlestick:
        plot.candlestick_sma(ticker_data, args.sma_period)
    if args.line_sma:
        plot.line_sma(ticker_data)
    
    return


def trade_bot():
    """Main bot script."""

    holding = False
    while True: # create infinite loop
        ticker_data = get_data(user.ticker)
        trade_strategy = trading_strategy(ticker_data)

        date_and_time_now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")    # get and use date_and_time_now at time of message
        print(f"{date_and_time_now} 🤖: Beep Bop Boop {trade_strategy}.")

        if (trade_strategy == "BUY" and not holding) or (trade_strategy == "SELL" and holding):
            print(f"🤖: Attempting to place {trade_strategy} order BOOOOOP...")
            trade = Trade(user.ticker, trade_strategy, user.investment, user.holding_qty, args.paper)
            
            if args.paper:
                trade_success = trade.paper()
            else:
                trade_success = trade.execute()
            
            holding = not holding if trade_success else holding

        time.sleep(user.delay * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="🤖cryptobot by naut 2022",
        description="A python bot to buy and sell cryptocurrency using a few basic buy and sell strategies.",
        epilog="Enjoy but please run at your own risk."
    )
    subparser = parser.add_subparsers(dest='command')
    parser.add_argument("--version", "-v", action="version", version="%(prog)s v0.1.0")
    parser.add_argument("--ticker", "-t", help="cryptocurrency ticker symbol. default=BTC-USDC", default="BTC-USDC", type=str)
    parser.add_argument("--cancel", "-x", help="cancel orders.", action="store_true")
    parser.add_argument("--investment", "-inv", "-$", help="investment amount. default=10", default=10, type=int)
    parser.add_argument("--delay", "-d", help="delay in minutes. default=5", default=5, type=int)
    parser.add_argument("--paper", "-p", action="store_true")

    plot = subparser.add_parser('plot')
    plot.add_argument("--candlestick", "-candle", help="plot candlestick x sma interactive chart.", action="store_true")
    plot.add_argument("--line_sma", "-line", help="plot line x sma x signal interactive chart.", action="store_true")
    plot.add_argument("--sma_period", "-sma", help="simple moving average period.", default=26, type=int)

    strategy = subparser.add_parser('strat')
    strategy.add_argument("--basic", "-bsc", action="store_true")
    strategy.add_argument("--mean_reversion_simple", "-mrs", action="store_true")
    strategy.add_argument("--mean_reversion", "-mr", action="store_true")

    args = parser.parse_args()


    # Initialize user settings
    user = User(
        ticker=args.ticker, 
        investment=args.investment, 
        delay=args.delay
    )

    if args.cancel:
        pass
    if args.command == 'plot':
        plot_bot()
    if args.command == 'strat':
        trade_bot()