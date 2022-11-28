USERNAME = "Your_Robinhood_Username"
PASSWORD = "Your_Robinhood_Password"

# The number of days to run the autotrader (INTEGER), must be greater than zero (0)
TIMEINDAYS = 1

# Export the completed crypto orders into a CSV? (BOOLEAN), must be either True or False
# Note: If set to True, should the user terminate the program via KeyboardInterrupt while trading, then the csv will still be exported
EXPORTCSV = False

# Plot analytical graphs while running? (BOOLEAN), must be either True or False
PLOTANALYTICS = False

# Plot graph of crypto price while running? (BOOLEAN), must be either True or False
PLOTCRYPTO = False

# Plot graph of portfolio while running? (BOOLEAN), must be either True of False
PLOTPORTFOLIO = False

# The mode to run the autotrader, available modes are 'LIVE', 'BACKTEST', and 'SAFELIVE'
MODE = 'SAFELIVE'

#------------------FOR 'BACKTEST' MODE ONLY---------------------------------
# 'INTERVAL', 'SPAN', and 'BOUNDS' used for retreiving historical crypto data for backtesting

INTERVAL = '15second'

SPAN = 'hour'

BOUNDS = '24_7'

#---------------------------------------------------------------------------

# Initial capital to start the backtesting with (optional: only for 'BACKTEST' and possibly 'SAFELIVE' modes)
CASH = 1000.00

# Is "CASH" above to be used in the 'SAFELIVE' mode? (BOOLEAN), must be either True or False
USECASH = True

# The cryptocurrencies to have the autotrader place orders on
CRYPTO = ['BTC','ETH']
