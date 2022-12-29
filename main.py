from alpaca_trade_api.rest import TimeFrame, REST
import config
import asyncio
import websockets

rest_api = REST(config.API_KEY, config.SECRET_KEY, "https://paper-api.alpaca.markets")


def get_current_price(crypto):
    price = (rest_api.get_crypto_bars(crypto, TimeFrame.Minute, exchanges="CBSE")).df["close"][-1]
    return price


def print_crypto_assets():
    for Asset in rest_api.list_assets():
        if Asset.status:
            if Asset.exchange == 'FTXU':
                print(Asset.symbol)


async def latest_quote():

    async with websockets.connect('wss://stream.data.alpaca.markets/v1beta2/crypto') as websocket:
        await websocket.send({"action": "auth",
                              "key": config.API_KEY,
                              "secret": config.SECRET_KEY})
        await websocket.send({"action": "subscribe",
                              "trades": ["BTC/USD"],
                              "quotes": ["LTC/USD", "ETH/USD"],
                              "bars": ["BCH/USD"]})


print_crypto_assets()
asyncio.run(latest_quote())