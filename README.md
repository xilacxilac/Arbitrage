# Arbitrage
 
**Arbitrage** is a Python project which attempts to create profit through
discrepancies between three (crypto)currencies. This is known as triangular
arbitrage. Currently, it supports arbitrage between USD, BTC, and ETH.

****

### How to Use:
1. Copy and paste your API and secret key in config.py
2. Adjust ARB_DIFF_REQ, wait_time, and val to your preferences in config.py
3. Go to main.py and run

### How It Works:

1. Gets the ask price of USD to BTC, USD to ETH, and BTC to ETH
2. Mathematically determine if discrepancies exist
3. If they do, attempt arbitrage. If not, then wait a certain amount of time and repeat

### APIs and Libraries:

- Alpaca API
  - Acts as a broker 
  - Used to get financial data (ask prices)
  - Used to create orders
- asyncio (Asynchronous I/O)
  - Used to improve efficiency 
    - ie: when waiting for a response for the ask price of BTC, it runs code to also get the price of ETH