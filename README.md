# Robinhood-Crypto-Autotrader
An automated trader for crypto on Robinhood

## Donate to this project and help support open-sourced financial software (anything helps!)

### I am happy to accept the following crypto currencies as gifts, it is much appreciated!
- Bitcoin (BTC) wallet address: `bc1qvljdr72k3tz6w8k6hpnhv3722fmsgftkeeakx8`
- Ethereum (ETH) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- US Dollar Coin (USDC) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Cardano (ADA) wallet address: `addr1q8g90gwc2u82fnv6m0pw7crervtslar746rxx06apfcf44cg6h5us0avc20ee2azzun58lgylyl54sjr6y9efwq86krst57w35`
- Solana (SOL) wallet address: `EzQveUMk45NmuftUSGLqRH8DUBmxzCpS3HuEchFc5t1X`
- Dogecoin (DOGE) wallet address: `DQCzww2Sz9UhtAaMZbHHGofng1ioRgTkEu`
- Polygon (MATIC) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Shiba Inu (SHIB) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Avalanche (AVAX) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Ethereum Classic (ETC) wallet address: `0x42D1125fB02D0eaAA3b0D57330EC46AaF5F95F15`
- Uniswap (UNI) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Litecoin (LTC) wallet address: `ltc1qvwzqm4jxqt0gjf7fwzxpnvtlssxtc9lutrnxsh`
- Chainlink (LINK) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Bitcoin Cash (BCH) wallet address: `bitcoincash:qr4h4edxt5muv2ns3kls0d4ca8lezu8x9v9d4r227h`
- Compound (COMP) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Aave (AAVE) wallet address: `0xDd5E232561177e5E48432F6BA4fD12173Bbe869A`
- Tezos (XTZ) wallet address: `tz1Wexc9bv6BxCBgyXwaqmJq1RNYxXBr9aff`
- Stellar Lumens (XLM): `GB2ES2N326MZK4EGJBKN3ZARCQ5RTFQSAWIJAAKFVIIIJSCC35TXIMLB`, memo (needs to be included): `1592369023`

<!--
- Bitcoin SV (BSV): `Currently unable to send and receive on Robinhood`
-->

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
