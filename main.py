import argparse
from datetime import datetime
import pandas as pd # pip install pandas
import numpy as np  # pip install numpy
from dotenv import load_dotenv  # pip install python-dotenv
import os

import ccxt
import talib    # pip install TA-Lib
import cbpro    # pip install cbpro
import base64
import json


# initialize API
API_KEY = os.environ.get("CBPRO_API_KEY")
SECRET = os.environ.get("CBPRO_SECRET")
PASSPHRASE = os.environ.get("CBPRO_PASSPHRASE")

encoded = json.dumps(SECRET).encode()
b64_secret = base64.b64encode(encoded)
auth_client = cbpro.AuthenticatedClient(key=API_KEY, b64secret=b64_secret, passphrase=PASSPHRASE)
c = cbpro.PublicClient()


def get_data(ticker):
    """Gets the data from OHLCV (Open, High, Low, Close, Volume) candles."""

    exchange = ccxt.coinbasepro()

    timeframe = 5 # in minutes
    limit = 100

    data = exchange.fetch_ohlcv(ticker, timeframe=f'{timeframe}m', limit=100)
    ticker_df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'vol'])
    ticker_df['date'] = pd.to_datetime(ticker_df['date'], unit='ms')
    ticker_df['symbol'] = ticker

    # c = cbpro.PublicClient()

    # ticker_df = pd.DataFrame(c.get_product_ticker_rates(product_id=ticker), columns=["date","open","high","low","close","vol"])
    # ticker_df['date'] = pd.to_datetime(ticker_df['date'], unit='s')
    # ticker_df['symbol'] = ticker

    return ticker_df


def trading_strategy(ticker_data):
    """Basic trading algorithm using Moving Average Convergence/Divergence and Relative Strength Index."""

    macd_conclusion = "WAIT"
    macd_and_rsi_conclusion = "WAIT"

    # Get MACD data
    macd, macdsignal, macdhist = talib.MACD(ticker_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    
    last_macdhist = macdhist.iloc[-1]
    prev_macdhist = macdhist.iloc[-2]

    if not np.isnan(prev_macdhist) and not np.isnan(last_macdhist):
        # A crossover is occuring if MACD history values change from positive to negative or vice versa.
        macd_crossover = (abs(last_macdhist + prev_macdhist)) != (abs(last_macdhist) + abs(prev_macdhist))

        if macd_crossover:
            macd_verdict = "BUY" if last_macdhist > 0 else "SELL"

    # If MACD determines a BUY or a SELL than check using RSI.
    if macd_conclusion != "WAIT":
        # RSI = 100 – [100 / ( 1 + (Mean Upward Price Change / Mean Downward Price Change))]
        rsi = talib.RSI(ticker_data['close'], timeperiod=14)

        # Use last 3 RSI values
        last_rsi_values = rsi.iloc[-3:]

        # RSI is considered overbought when above 70 and oversold when below 30.
        if (last_rsi_values.min() <= 30):
            macd_and_rsi_conclusion = "BUY"

        if (last_rsi_values.max() >= 70):
            macd_and_rsi_conclusion = "SELL"

    # print(macd, macdsignal, macdhist)
    # print("Last MACD:",last_macdhist)
    # print("Previous MACD:", prev_macdhist)
    # print("RSI:", rsi)
    # print("LAST3 RSI:", last_rsi_values)

    return macd_and_rsi_conclusion


def main(ticker):
    """Main bot script."""

    ticker_data = get_data(ticker)
    print(ticker_data)
    trade_strategy = trading_strategy(ticker_data)
    date_and_time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"{date_and_time_now} TRADING RECOMMENDATION: {trade_strategy}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='CryptoBot',
        description='A simple python bot to buy and sell btc using a very simple buy and sell strategy.'
    )
    parser.add_argument("--version", "-v", action='version', version='%(prog)s v0.0.1')
    parser.add_argument("--ticker", "-t", help="Cryptocurrency ticker symbol.", default="BTC-USDC")
    args = parser.parse_args()


    main(args.ticker)