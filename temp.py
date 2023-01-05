from alpaca_trade_api.stream import Stream
import config

stream = Stream(config.API_KEY, config.SECRET_KEY, raw_data=True)


async def quote(q):
    print(q)


async def trade(t):
    print(t)


def subscribe_to_quotes(crypto):
    stream.subscribe_crypto_quotes(quote, crypto)
    stream.subscribe_crypto_trades(trade, crypto)

    @stream.on_bar(crypto)
    async def _(bar):
        print('bar', bar)

    stream.run()
