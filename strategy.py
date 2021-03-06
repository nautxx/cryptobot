import numpy as np  # pip install numpy
import talib    # pip install TA-Lib
import time


class Strategy:
    """Contains the strategy algorithms."""

    def __init__(self):
        self.macd_strategy = "WAIT"
        self.rsi_strategy = "WAIT"
        self.perc_strategy = "WAIT"
        self.overall_strategy = "WAIT"


    def macd_indicator(self, ticker_data):
        """Calculates MACD and returns BUY, SELL, or WAIT."""
        
        fast_period = 12
        slow_period = 26
        signal_period = 9

        # MACD = 12Day Exponential Moving Average − 26Day EMA
        macd, macdsignal, macdhist = talib.MACD(ticker_data['close'],
                                                fastperiod=fast_period, 
                                                slowperiod=slow_period, 
                                                signalperiod=signal_period)
        
        last_macdhist = macdhist.iloc[-1]
        prev_macdhist = macdhist.iloc[-2]

        # Save MACD to file
        macdhist.to_csv("data_macd.csv")

        if not np.isnan(prev_macdhist) and not np.isnan(last_macdhist):
            # A crossover is occuring if MACD history values change from positive to negative or vice versa.
            macd_crossover = (abs(last_macdhist + prev_macdhist)) != (abs(last_macdhist) + abs(prev_macdhist))

            if macd_crossover:
                self.macd_strategy = "BUY" if last_macdhist > 0 else "SELL"
        
        return self.macd_strategy


    def rsi_indicator(self, ticker_data):
        """Calculates RSI and returns BUY, SELL, or WAIT."""
        
        oversold_threshold = 30
        overbought_threshold = 70

        # RSI = 100 – [100 / (1 + (Mean Upward Price Change / Mean Downward Price Change))]
        rsi = talib.RSI(ticker_data['close'], timeperiod=14)

        # Save RSI to file
        rsi.to_csv("data_rsi.csv")

        # Use last 3 RSI values
        last_rsi_values = rsi.iloc[-3:]

        # RSI is considered overbought when above 70 and oversold when below 30.
        if last_rsi_values.min() <= oversold_threshold:
            self.rsi_strategy = "BUY"

        if last_rsi_values.max() >= overbought_threshold:
            self.rsi_strategy = "SELL"

        return self.rsi_strategy

    
    def mean_reversion_strategy(self, ticker_data):
        """If MACD line crosses signal line from below and RSI value is in 
        oversold region, this is the signal to buy. If MACD line crosses signal 
        line from above and RSI value is in overbought region, this is the 
        signal to sell."""

        if self.macd_indicator(ticker_data) != "WAIT":
            self.overall_strategy = self.rsi_indicator(ticker_data)

        return self.overall_strategy

    
    def simple_mean_reversion_strategy(self, ticker_data):
        """If MACD line crosses signal line from below, this is the signal to buy.
        If MACD line crosses signal line from above, this is the signal to sell."""

        self.overall_strategy = self.macd_indicator(ticker_data)

        return self.overall_strategy


    def percent_indicator(self, ticker_begin, ticker_end, percent_threshold=5):
        """Calculates percent increase/decrease and returns BUY, SELL, or WAIT."""
        
        percent = ((float(ticker_end['price']) - float(ticker_begin['price'])) * 100 / float(ticker_begin['price']))
        
        if percent >= float(percent_threshold / 100):
            self.per_strategy = "SELL"
        
        if percent <= float(percent_threshold / -100):
            self.perc_strategy = "BUY"

        return self.perc_strategy

    
    def basic_strategy(self, ticker_begin, ticker_end, threshold):
        self.overall_strategy = self.percent_indicator(ticker_begin, ticker_end, threshold)

        return self.overall_strategy


    def arbitrage(self):
        pass