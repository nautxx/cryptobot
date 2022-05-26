class User:
    
    def __init__(self, ticker, investment):
        self.ticker = ticker
        self.investment = investment
        self.holding_qty = 0
        self.order_id = None