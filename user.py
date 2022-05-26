class User:
    
    def __init__(self, ticker, investment, rsi_oversold, rsi_overbought, delay):
        self.ticker = ticker
        self.investment = investment
        self.oversold_threshold = rsi_oversold
        self.overbought_threshold = rsi_overbought
        self.delay = delay
        self.holding_qty = 0
        self.order_id = None