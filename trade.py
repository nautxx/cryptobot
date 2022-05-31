import os
import time
from datetime import datetime
from dotenv import load_dotenv  # pip install python-dotenv

import cbpro    # pip install cbpro
import base64
import json

class Trade:

    # initialize APIs and objects
    API_KEY = os.environ.get("CBPROSAND_API_KEY")
    SECRET = os.environ.get("CBPROSAND_SECRET")
    PASSPHRASE = os.environ.get("CBPROSAND_PASSPHRASE")

    encoded = json.dumps(SECRET).encode()
    b64_secret = base64.b64encode(encoded)

    auth_client = cbpro.AuthenticatedClient(key=API_KEY, b64secret=b64_secret, passphrase=PASSPHRASE)
    cbpro_client = cbpro.PublicClient()

    def __init__(self, ticker, trade_strategy, investment,  holding_qty):
        self.order_success = False
        self.ticker = ticker
        self.side = "buy" if (trade_strategy == "BUY") else "sell"
        self.investment = investment
        self.holding_qty = holding_qty


    def paper_trade(self):
        try:
            current_ticker_info_response = self.cbpro_client.get_product_ticker(product_id=self.ticker)
        except:
            print(f"\n🤖: Boooops. Something went wrong. Unable to place order.")

        try:
            current_price = float(current_ticker_info_response['price'])
        except Exception as e:
            print(f"🤖: Error obtaining ticker data. {e}")

            order_size = round(self.investment / current_price, 5) if trade_strategy == "BUY" else holding_qty

            print(f"🤖: Placing order {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}: "
                f"{self.ticker}, {self.side}, {current_price}, {order_size}, {int(time.time() * 1000)}"
            )

        try:
            order_response = self.auth_client.place_limit_order(product_id=ticker, side=self.ide, price=current_price, size=order_size)
        except Exception as e:
            print(f"🤖: Error placing order. {e}")

        try:
            check = order_response["id"]
            # logging.info(check)
            check_order = self.auth_client.get_order(order_id=check)
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