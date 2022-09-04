USERNAME = "Your_Robinhood_Username"
PASSWORD = "Your_Robinhood_Password"

# The number of days to run the autotrader (INTEGER), must be greater than zero (0)
TIMEINDAYS = 1

# Export the completed crypto orders into a CSV? (BOOLEAN), must be either True or False
EXPORTCSV = False

# The mode to run the autotrader, available modes are 'LIVE', 'BACKTEST', and 'SAFE-LIVE'
MODE = 'SAFE-LIVE'

# The cryptocurrencies to have the autotrader place orders on
"""
Available options:
- 'BTC' for Bitcoin
- 'ETH' for Ethereum
- 'ETC' for Ethereum Classic
- 'BCH' for Bitcoin Cash
- 'BSV' for Bitcoin SV
- 'LTC' for Litecoin
- 'DOGE' for Dogecoin
- 'SHIB' for Shiba Inu
- 'SOL' for Solana
- 'MATIC' for Polygon
- 'COMP' for Compound
- 'LINK' for Chainlink
- 'UNI' for Uniswap
- 'XLM' for Stellar Lumens
- 'AVAX' for Avalanche
- 'ADA' for Cardano
"""
CRYPTO = ['BTC']