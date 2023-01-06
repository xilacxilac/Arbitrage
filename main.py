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
        return True
    except Exception as e:
        price[crypto] = 0
        print('get_current_price() error: {0}'.format(e))
        return False


def order(symbol, qty, side):
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.GTC
        )

        market_order = trading_client.submit_order(market_order_data)
        return True

    except Exception as e:
        print('order() error: {0}'.format(e))
        return False


def get_position(crypto):
    try:
        position = trading_client.get_open_position(crypto)
        return float(position.qty)

    except Exception as e:
        print('get_position() error: {0}'.format(e))
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
        if order('BTC/USD', BTC_START, OrderSide.BUY):
            BTC_NEW = get_position('BTCUSD')
            BTC_ETH = (BTC_NEW / ETHBTC) / 1.05
            if order('ETH/BTC', BTC_ETH, OrderSide.BUY):
                BTC_FINAL = get_position('ETHUSD')
                if order('ETH/USD', BTC_FINAL, OrderSide.SELL):
                    BTC_LEFT = get_position('BTCUSD')
                    if order('BTC/USD', BTC_LEFT, OrderSide.SELL):
                        print('Success: BTC')
                    else:
                        print('Sell Back failed: Leftover BTC -> USD (BTC)')
                        exit()
                else:
                    print('Order failed: ETH -> USD (BTC)')
                    print('Manual Sell Back required')
                    exit()
            else:
                print('Order failed: BTC -> ETH (BTC)')
                if not order('BTC/USD', BTC_NEW, OrderSide.SELL):
                    print('Sell Back failed: BTC -> USD (BTC)')
                    exit()
        else:
            print('Order failed: USD -> BTC (BTC)')
            exit()

    # USD -> ETH -> BTC -> USD (ETH is cheaper)
    elif ETHBTC < ARB_DIV * (1 - config.ARB_DIFF_REQ):
        if order('ETH/USD', ETH_START, OrderSide.BUY):
            ETH_NEW = get_position('ETHUSD')
            ETH_BTC = ETH_NEW * ETHBTC
            if order('ETH/BTC', ETH_BTC, OrderSide.SELL):
                ETH_FINAL = get_position('BTCUSD')
                if order('BTC/USD', ETH_FINAL, OrderSide.SELL):
                    ETH_LEFT = get_position('ETHUSD')
                    if order('ETH/USD', ETH_LEFT, OrderSide.SELL):
                        print('Success: ETH')
                    else:
                        print('Sell Back failed: Leftover ETH -> USD (ETH)')
                        exit()
                else:
                    print('Order failed: ETH -> USD (ETH)')
                    print('Manual Sell Back required')
                    exit()
            else:
                print('Order failed: ETH -> BTC (ETH)')
                if not order('BTC/USD', ETH_NEW, OrderSide.SELL):
                    print('Sell Back failed: ETH -> USD (ETH)')
                    exit()
        else:
            print('Order failed: USD -> ETH (ETH)')
            exit()

    else:
        print('No arbitrage conditions found')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
