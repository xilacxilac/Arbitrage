from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import config

trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)

account = trading_client.get_account()
for property_name, value in account:
    print(f"\"{property_name}\": {value}")

    market_order_data = MarketOrderRequest(
        symbol="BTC/USD",
        qty=1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )
    market_order = trading_client.submit_order(market_order_data)

    market_order = trading_client.submit_order(market_order_data)
    for property_name, value in market_order:
        print(f"\"{property_name}\": {value}")

    positions = trading_client.get_all_positions()
    for position in positions:
        for property_name, value in position:
            print(f"\"{property_name}\": {value}")