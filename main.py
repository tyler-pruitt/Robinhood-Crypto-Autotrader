import config
import trader

import robin_stocks.robinhood as rh
import datetime as dt
import time
import pandas as pd
import numpy as np

from robinhood_crypto_api import RobinhoodCrypto

# Make sure to take advantage of https://robin-stocks.readthedocs.io/en/latest/robinhood.html#getting-crypto-information

def login():
    days = int(input("Enter the number of days to run the automated trader (POSITIVE integer > 0): "))
    
    while days <= 0:
        days = int(input("Enter the number of days to run the automated trader (POSITIVE integer > 0): "))

    time_logged_in = 60 * 60 * 24 * days
    
    rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)

def logout():
    rh.authentication.logout()
    
    print("logout successful")

def get_cash():
    rh_cash = rh.account.build_user_profile()

    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    
    
    return(cash, equity)

def build_dataframes(df_trades, trade_dict, df_prices, price_dict):
    time_now = str(dt.datetime.now().time())[:8]
    
    df_trades.loc[time_now] = trade_dict
    df_prices.loc[time_now] = price_dict
    
    
    return(df_trades, df_prices)

def display_holdings(holdings):
    for crypto, amount in holdings.items():
        
        print('\t' + crypto + ' ' + str(amount) + " at $" + str(rh.get_crypto_quote(crypto)['mark_price']))

if __name__ == "__main__":
    login()
    
    export_orders = input("Export a CSV of completed crypto orders when finished? (True or False): ")
    
    while export_orders != "True" and export_orders != "False":
        export_orders = input("Export a CSV of completed crypto orders when finished? (True or False): ")
        
    if export_orders == "True":
        export_orders = True
    else:
        export_orders = False
    
    rhcrypto = RobinhoodCrypto(config.USERNAME, config.PASSWORD)
    
    stocks = config.CRYPTO
    
    print('cryptos:', stocks)
    
    cash, equity = get_cash()

    tr = trader.Trader(stocks)

    trade_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    price_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    
    df_trades = pd.DataFrame(columns=stocks)
    df_prices = pd.DataFrame(columns=stocks)
    
    inital_capital_is_init = False

    while tr.continue_trading():
        prices = rhcrypto.get_latest_price(stocks)
        
        holdings, bought_price = rhcrypto.get_holdings_and_bought_price(stocks)
        
        cash, equity = get_cash()
        
        if inital_capital_is_init == False:
            initial_capital = rhcrypto.get_crypto_holdings_capital(holdings) + cash
            
            inital_capital_is_init = True
        
        tr.set_profit(cash + rhcrypto.get_crypto_holdings_capital(holdings) - initial_capital)
        
        print("======================" + rhcrypto.get_mode() + "======================")
        print("runtime: " + tr.display_time(tr.get_runtime()))
        
        print("total equity: $" + str(equity))
        
        print('crypto holdings:')
        display_holdings(holdings)
        
        print("total crypto equity: $" + str(rhcrypto.get_crypto_holdings_capital(holdings)))
        print("cash: $" + str(cash))
        
        print("profit: " + tr.display_profit())

        for i, stock in enumerate(stocks):
            
            price = float(prices[i])
            
            print('\n{} = ${}'.format(stock, price))

            trade = tr.determine_trade(stock)
            
            print('trade:', trade, end='\n\n')
            
            if trade == "BUY":
                allowable_holdings = (cash / 10) / price
                
                if allowable_holdings > 0:
                    
                    rhcrypto.buy(stock, allowable_holdings, price)

                else:
                    print("Not enough allowable holdings")
                    
                    trade = "UNABLE TO BUY"
            elif trade == "SELL":
                if holdings[stock] > 0:

                    rhcrypto.sell(stock, holdings[stock], price)
                else:
                    print("Not enough holdings")

                    trade = "UNABLE TO SELL"
            
            price_dict[stock] = price
            
            trade_dict[stock] = trade

        df_trades, df_prices = build_dataframes(df_trades, trade_dict, df_prices, price_dict)
        
        print('\ndf_prices \n', df_prices, end='\n\n')
        print('df_trades \n', df_trades, end='\n\n')
        
        print("Waiting " + str(tr.get_interval_sec()) + ' seconds...', end='\n\n')
        time.sleep(tr.get_interval_sec())

    logout()
    
    if export_orders:
        rh.export.export_completed_crypto_orders('./', 'completed_crypto_orders')
