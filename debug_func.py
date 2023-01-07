from alpaca_trade_api.rest import REST
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.trading.client import TradingClient
import config

# Rest API and other clients
rest_api = REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets')
crypto_client = CryptoHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)


# Prints all available cryptocurrency assets (ie. BTC/USD)
def print_crypto_assets():
    for Asset in rest_api.list_assets():
        if Asset.status:
            if Asset.exchange == 'FTXU':
                print(Asset.symbol)


# Get the quantity of an order by id
def get_quantity_id(id_):
    try:
        get_order = trading_client.get_order_by_id(id_)
        return float(get_order.qty)

    except Exception as e:
        print('get_quantity_id() error: {0}'.format(e))
        return 0


# Get the quantity of a specific cryptocurrency
def get_quantity(crypto):
    try:
        positions = trading_client.get_all_positions()
        return positions[0].qty
    except Exception as e:
        print('get_quantity() error: {1}'.format(e))
        return -1


# Get information from account and print it
def get_account():
    account = trading_client.get_account()
    for property_name, value in account:
        print(f"\"{property_name}\": {value}")


# Get all positions from an account and print it
def get_positions():
    positions = trading_client.get_all_positions()
    for position in positions:
        for property_name, value in position:
            print(f"\"{property_name}\": {value}")