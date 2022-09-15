USERNAME = "Your_Robinhood_Username"
PASSWORD = "Your_Robinhood_Password"

# The number of days to run the autotrader (INTEGER), must be greater than zero (0)
TIMEINDAYS = 1

# Export the completed crypto orders into a CSV? (BOOLEAN), must be either True or False
EXPORTCSV = False

# Plot analytical graphs while running? (BOOLEAN), must be either True or False
PLOTGRAPH = True

# The mode to run the autotrader, available modes are 'LIVE', 'BACKTEST', and 'SAFE-LIVE'
MODE = 'SAFE-LIVE'

# Initial capital to start the backtesting with (optional: only for 'BACKTEST' mode)
CASH = 100.00

# File path to CSV of market data (optional: only for 'BACKTEST' mode)
PATHTODATA = ''

# The cryptocurrencies to have the autotrader place orders on
CRYPTO = ['BTC']