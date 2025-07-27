import os
import logging
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

dotenv_path = r"D:\internship\binance_trading_bot\.env"
load_dotenv(dotenv_path)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = Client(api_key, api_secret)

try:
    account = client.get_account()
    print("✅ Successfully connected to Binance API!")
except Exception as e:
    print("❌ API error:", e)
    
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    format = '%(asctime)s - %(levelname)s - %(message)s',
    level = logging.INFO

)

# Helper to validate CLI input
def get_valid_input(prompt, options):
    while True:
        val = input(prompt).upper()
        if val in options:
            return val
        print(f"Invalid input. Choose from: {options}")


class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret)
        if testnet:
            self.client.API_URL = 'https://testnet.binancefuture.com/fapi'

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity
            }

            if order_type == 'LIMIT':
                params['price'] = price
                params['timeInForce'] = 'GTC'

            elif order_type == 'STOP_MARKET':
                params['stopPrice'] = stop_price
                params['timeInForce'] = 'GTC'

            elif order_type == 'STOP':
                params['stopPrice'] = stop_price
                params['price'] = price
                params['timeInForce'] = 'GTC'

            logging.info(f"Placing order: {params}")
            print("Sending order...")
            order = self.client.futures_create_order(**params)

            logging.info(f"Order response: {order}")
            print("Order placed successfully!")
            self.log_to_csv(order)
            return order

        except BinanceAPIException as e:
            print("Binance API error:", e.message)
            logging.error(f"Binance API Exception: {e.message}")
        except Exception as e:
            print("Error placing order:", str(e))
            logging.error(f"Error placing order: {str(e)}")

    def log_to_csv(self, order):
        with open("orders.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now(),
                order.get('symbol'),
                order.get('side'),
                order.get('type'),
                order.get('origQty'),
                order.get('price', 'Market'),
                order.get('status')
            ])
def main():
    # Load keys from environment
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')

    if not api_key or not api_secret:
        print("API key/secret not found in environment variables.")
        return

    bot = BasicBot(api_key, api_secret)

    print("Welcome to Binance Futures Testnet Trading Bot!")
    print("Supported order types: MARKET, LIMIT")
    print("Supported sides: BUY, SELL")

    # Get user input
    symbol = input("Enter trading symbol (e.g. BTCUSDT): ").upper()
    side = input("Enter side (BUY or SELL): ").upper()
    order_type = input("Enter order type (MARKET or LIMIT): ").upper()
    quantity = input("Enter quantity: ")
    price = None

    if order_type == 'LIMIT':
        price = input("Enter price for limit order: ")

    # Validate inputs basic
    if side not in ['BUY', 'SELL']:
        print("Invalid side input.")
        return
    if order_type not in ['MARKET', 'LIMIT']:
        print("Invalid order type input.")
        return

    try:
        quantity = float(quantity)
        if price:
            price = float(price)
    except ValueError:
        print("Quantity and price must be numbers.")
        return

    bot.place_order(symbol, side, order_type, quantity, price)

if __name__ == '__main__':
    main()
 
