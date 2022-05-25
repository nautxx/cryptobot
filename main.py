import argparse
import pandas as pd # pip install pandas
import numpy as np  # pip install numpy

import ccxt # pip install ccxt
import talib    # pip install TA-Lib


def get_data(ticker):
    """Gets the data from OHLCV candles."""

    exchange = ccxt.coinbasepro()
    timeframe = 5 # in minutes
    limit = 100

    response = exchange.fetch_ohlcv(ticker, timeframe=f'{timeframe}m', limit=100)

    ticker_df = pd.DataFrame(response[:-1], columns=['timestamp', 'open', 'high', 'low', 'closing', 'vol'])
    ticker_df['date'] = pd.to_datetime(ticker_df['timestamp'], unit='ms')
    ticker_df['symbol'] = ticker

    return ticker_df


def trading_strategy(ticker_data):
    """Basic trading algorithm using Moving Average Convergence/Divergence and Relative Strength Index."""

    macd_conclusion = "WAIT"
    macd_and_rsi_conclusion = "WAIT"

    # Get MACD data
    macd, macdsignal, macdhist = talib.MACD(ticker_data['closing'], fastperiod=12, slowperiod=26, signalperiod=9)
    
    last_macdhist = macdhist.iloc[-1]
    prev_macdhist = macdhist.iloc[-2]

    if not np.isnan(prev_macdhist) and not np.isnan(last_macdhist):
        # A crossover is occuring if MACD history values change from positive to negative or vice versa.
        macd_crossover = (abs(last_macdhist + prev_macdhist)) != (abs(last_macdhist) + abs(prev_macdhist))

        if macd_crossover:
            macd_verdict = "BUY" if last_macdhist > 0 else "SELL"

    if macd_conclusion != "WAIT":
        # RSI = 100 – [100 / ( 1 + (Mean Upward Price Change / Mean Downward Price Change))]
        rsi = talib.RSI(ticker_data['closing'], timeperiod=14)

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
    # print(ticker_data)
    buy_sell_wait = trading_strategy(ticker_data)
    print(buy_sell_wait)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='CryptoBot',
        description='A simple python bot to buy and sell btc using a very simple buy and sell strategy.'
    )
    parser.add_argument("--version", "-v", action='version', version='%(prog)s v0.0.1')
    parser.add_argument("--ticker", "-t", help="Cryptocurrency ticker symbol.", default="BTC/USDT")
    args = parser.parse_args()


    main(args.ticker)