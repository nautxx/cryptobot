import argparse
import ccxt # pip install ccxt
import pandas as pd # pip install pandas
import numpy as np  # pip install numpy


def get_data(ticker):
    """Gets the data from OHLCV candles."""

    exchange = ccxt.coinbasepro()
    timeframe = 5 # in minutes
    limit = 100

    response = exchange.fetch_ohlcv(ticker, timeframe=f'{timeframe}m', limit=100)

    if response is not None:
        ticker_df = pd.DataFrame(response[:-1], columns=['timestamp', 'open', 'high', 'low', 'closing', 'vol'])
        ticker_df['date'] = pd.to_datetime(ticker_df['timestamp'], unit='ms')
        ticker_df['symbol'] = ticker

    return ticker_df


def main(ticker):
    """Main bot script."""

    ticker_data = get_data(ticker)

    print(ticker_data)
    return ticker_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='CryptoBot',
        description='A simple python bot to buy and sell btc using a very simple buy and sell strategy.'
    )
    parser.add_argument("--version", "-v", action='version', version='%(prog)s v0.0.1')
    parser.add_argument("--ticker", "-t", help="Cryptocurrency ticker symbol.", default="BTC/USDT")
    args = parser.parse_args()


    main(args.ticker)