from alpaca_trade_api.rest import REST
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import config
import asyncio

price = {
    'ETH/USD': 0,
    'BTC/USD': 0,
    'ETH/BTC': 0
}

rest_api = REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets')
crypto_client = CryptoHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)


async def main():
    while True:
        try:
            task1 = loop.create_task(get_current_price('ETH/USD'))
            task2 = loop.create_task(get_current_price('BTC/USD'))
            task3 = loop.create_task(get_current_price('ETH/BTC'))

            await asyncio.wait([task1, task2, task3])
            await test_arb()
            await asyncio.sleep(config.wait_time)

        except TimeoutError:
            print('main() error: TimeoutError')


async def get_current_price(crypto):
    try:
        crypto_latest_request_params = CryptoLatestQuoteRequest(symbol_or_symbols=crypto)
        crypto_latest_quote = crypto_client.get_crypto_latest_quote(crypto_latest_request_params)
        price[crypto] = crypto_latest_quote[crypto].ask_price
        print('{0}: {1}'.format(crypto, price[crypto]))

        return True
    except Exception as e:
        price[crypto] = 0

        print('get_current_price() error: {0}'.format(e))
        return False


def print_crypto_assets():
    for Asset in rest_api.list_assets():
        if Asset.status:
            if Asset.exchange == 'FTXU':
                print(Asset.symbol)


def order(symbol, qty, side):
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.GTC
        )

        market_order = trading_client.submit_order(market_order_data)
        return market_order.id

    except Exception as e:
        print('order() error: {0}'.format(e))
        return 0


def get_quantity_id(id_):
    try:
        qty = trading_client.get_order_by_id(id_)
        return qty

    except Exception as e:
        print('order() error: {0}'.format(e))
        return 0


async def test_arb():
    ETH = price['ETH/USD']
    BTC = price['BTC/USD']
    ETHBTC = price['ETH/BTC']
    ARB_DIV = ETH / BTC

    x = 10000
    BTC_START = x / BTC
    ETH_START = x / ETH

    # USD -> BTC -> ETH -> USD (BTC is cheaper)
    if ETHBTC > ARB_DIV * (1 + config.ARB_DIFF_REQ):
        id_1 = order('BTC/USD', BTC_START, OrderSide.BUY)
        if id_1 != 0:
            BTC_CONVERT = get_quantity_id(id_1) / ETHBTC
            id_2 = order('ETH/BTC', BTC_CONVERT, OrderSide.BUY)
            if id_2 != 0:
                BTC_FINAL = get_quantity_id(id_2)
                id_3 = order('ETH/USD', BTC_FINAL, OrderSide.SELL)
                if id_3 != 0:
                    print('Success: BTC')
                else:
                    print('Order failed: ETH -  > USD (BTC)')
                    print('Manual Sell Back required')
                    print('ID: {0}'.format(id_3))
                    exit()
            else:
                print('Order failed: BTC -> ETH (BTC)')
                if order('BTC/USD', BTC_CONVERT, OrderSide.SELL) == 0:
                    print('Sell Back failed: BTC -> USD (BTC)')
                    exit()
        else:
            print('Order failed: USD -> BTC (BTC)')

    # USD -> ETH -> BTC -> USD (ETH is cheaper)
    elif ETHBTC < ARB_DIV * (1 - config.ARB_DIFF_REQ):
        ETH_ACT = order('ETH/USD', ETH_START, OrderSide.BUY)
        if ETH_ACT > 0:
            ETH_BTC = ETH_ACT * ETHBTC
            if order('ETH/BTC', ETH_ACT, OrderSide.SELL) > 0:
                if order('BTC/USD', ETH_BTC, OrderSide.SELL) > 0:
                    print('Success: ETH')
                else:
                    print('Order failed: BTC -> USD (ETH)')
                    print('Manual Sell Back required')
                    exit()
            else:
                print('Order failed: ETH -> BTC (ETH)')
                if order('ETH/USD', ETH_ACT, OrderSide.SELL) == 0:
                    print('Sell Back failed: ETH -> USD (ETH)')
                    exit()
        else:
            print('Order failed: USD -> ETH (ETH)')

    else:
        print('No arbitrage conditions found')


def get_quantity(crypto):
    try:
        positions = trading_client.get_all_positions()
        return positions[0].qty
    except Exception as e:
        print('get_quantity() error: {1}'.format(e))
        return -1


def get_account():
    account = trading_client.get_account()
    for property_name, value in account:
        print(f"\"{property_name}\": {value}")


def get_positions():
    positions = trading_client.get_all_positions()

    for position in positions:
        for property_name, value in position:
            print(f"\"{property_name}\": {value}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
