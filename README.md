# Robinhood-Crypto-Autotrader
An automated trader for crypto on Robinhood

## To run the code:
### 1. place all files in the same folder 
### 2. place your Robinhood USERNAME, PASSWORD, and CRYPTO to trade in "config.py"

#### You should fill in your information in the file "config.py" like so

```python
USERNAME = "Your_Robinhood_Username"
PASSWORD = "Your_Robinhood_Password"

# The number of days to run the autotrader (INTEGER), must be greater than zero (0)
TIMEINDAYS = 1

# Export the completed crypto orders into a CSV? (BOOLEAN), must be either True or False
# Note: If set to True, should the user terminate the program via KeyboardInterrupt while trading, then the csv will still be exported
EXPORTCSV = False

# Plot analytical graphs while running? (BOOLEAN), must be either True or False
PLOTGRAPH = False

# The mode to run the autotrader, available modes are 'LIVE', 'BACKTEST', and 'SAFELIVE'
MODE = 'SAFELIVE'

# Initial capital to start the backtesting with (optional: only for 'BACKTEST' and possibly 'SAFELIVE' modes)
CASH = 1000.00

# Is "CASH" above to be used in the 'SAFELIVE' mode? (BOOLEAN), must be either True or False
CASHFORSAFELIVE = True

# File path to CSV of market data (optional: only for 'BACKTEST' mode)
DATAPATH = ''

# The cryptocurrencies to have the autotrader place orders on
CRYPTO = ['BTC','ETH']
```

#### Cryptocurrency options are 
- `BTC` for Bitcoin
- `ETH` for Ethereum
- `ETC` for Ethereum Classic
- `BCH` for Bitcoin Cash
- `BSV` for Bitcoin SV
- `LTC` for Litecoin
- `DOGE` for Dogecoin
- `SHIB` for Shiba Inu
- `SOL` for Solana
- `MATIC` for Polygon
- `COMP` for Compound
- `LINK` for Chainlink
- `UNI` for Uniswap
- `XLM` for Stellar Lumens
- `AVAX` for Avalanche
- `ADA` for Cardano
- `USDC` for USD Coin

### 3. modify the Trader class in "trader.py" to your personal trading strategy (optional)
### 4. run "main.py"
