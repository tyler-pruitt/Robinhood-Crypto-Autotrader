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