# Robinhood-Crypto-Autotrader
An automated trader for crypto on Robinhood

To run the code:
1. place all files in the same folder 
2. place your Robinhood USERNAME, PASSWORD, and cryptocurrencies to watch in "config.py"
3. modify "trade_strat.py" to your personal trading strategy
4. un-comment the "sell()" and "buy()" functions in the "trader.py" file when you are ready to trade on the live market

-- UPDATE: 6/25/21 --
Due to users receiving a 404 Error from trade_strat.py in the get_historical_prices() function. Some lines have been updated to the newer version of robin_stocks
updated files:
     - trader.py
     - trade_strat.py

-- UPDATE: 07/04/2022 --
Trading ideas:
- Linear regression, least squares, R^2
- Polynomial and exponential regression
- Machine learning

-- UPDATE: 07/29/2022 --
- Implemented polynomial regression
- Fixed Trader class runtime implementation
