# Robinhood-Crypto-Autotrader
An automated trader for crypto on Robinhood

## New to Robinhood?
Join Robinhood with my link and we'll both pick our own free stock 🤝 https://join.robinhood.com/tylerp5773

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
PLOTANALYTICS = False

# Plot graph of crypto price while running? (BOOLEAN), must be either True or False
PLOTCRYPTO = True

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
```

#### Interval options are
`['15second', '5minute', '10minute', 'hour', 'day', 'week']`

#### Span options are
`['hour', 'day', 'week', 'month', '3month', 'year', '5year']`

#### Bounds options are
`['Regular', 'trading', 'extended', '24_7']`

#### Cryptocurrency options can be found here: https://robinhood.com/lists/robinhood/97b746a5-bc2f-4c64-a828-1af0fc399bf9

### 3. modify the Trader class in "trader.py" to your personal trading strategy (optional)
### 4. run "main.py"
