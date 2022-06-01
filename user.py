class User:
    
    def __init__(self, ticker, investment, delay):
        self.ticker = ticker
        self.investment = investment
        self.delay = delay
        self.order_id = None