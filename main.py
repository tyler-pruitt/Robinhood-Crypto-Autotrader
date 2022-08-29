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

def continue_trading(tr=''):
    # Assumes there is no condition for which the user will want the trading bot to stop trading
    if tr == '':
        return True
    else:
        if tr.get_profit() >= -1 * tr.get_loss_threshold():
            return True
        else:
            print("Loss exceeded $" + str(tr.get_loss_threshold()) + ": terminating automated trading")
            
            #logout()

            return False

def get_cash():
    rh_cash = rh.account.build_user_profile()

    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    
    
    return(cash, equity)

def get_holdings_and_bought_price(rhcrypto, stocks):
    # rh.get_crypto_positions()
    
    holdings = {stocks[i]: 0 for i in range(0, len(stocks))}
    bought_price = {stocks[i]: 0 for i in range(0, len(stocks))}
    
    rh_holdings = rhcrypto.build_holdings()

    for stock in stocks:
        try:
            holdings[stock] = float(rh_holdings[stock]['quantity'])
            bought_price[stock] = float(rh_holdings[stock]['average_buy_price'])
        except:
            holdings[stock] = 0
            bought_price[stock] = 0

    return(holdings, bought_price)

def sell(rhcrypto, stock, holdings, price):
    # sell_price = round(price - 0.10, 2)
    
    # un-comment below when ready to trade on the live market
    
    print('SELL IS CURRENTLY COMMENTED')
    
    # sell_order = rh.orders.order_sell_limit(symbol=stock,
    #                                         quantity=holdings,
    #                                         limitPrice=sell_price,
    #                                         timeInForce='gfd')
    """
    sell_order_info = rhcrypto.trade(
        pair=stock,
        price=round(price, 2),
        quantity=holdings,
        side="buy",
        time_in_force="gtc",
        type="limit"
    )
    """

    print('### Trying to SELL {} amount of {} at ${} totaling +${}'.format(holdings, stock, price, round(holdings * price, 2)))
    
    #return sell_order_info

def buy(rhcrypto, stock, allowable_holdings, price):
    # buy_price = round((price + 0.10), 2)
    
    # un-comment below when ready to trade on the live market
    
    print('BUY IS CURRENTLY COMMENTED')
    
    # buy_order = rh.orders.order_buy_limit(symbol=stock,
    #                                       quantity=allowable_holdings,
    #                                       limitPrice=buy_price,
    #                                       timeInForce='gfd')
    """
    buy_order_info = rhcrypto.trade(
        pair=stock,
        price=round(price, 2),
        quantity=allowable_holdings,
        side="sell",
        time_in_force="gtc",
        type="limit"
    )
    """

    print('### Trying to BUY {} of {} at ${} totaling -${}'.format(allowable_holdings, stock, price, round(allowable_holdings * price, 2)))

    #return buy_order_info

def build_dataframes(df_trades, trade_dict, df_prices, price_dict):
    time_now = str(dt.datetime.now().time())[:8]
    
    df_trades.loc[time_now] = trade_dict
    df_prices.loc[time_now] = price_dict
    
    
    return(df_trades, df_prices)

def display_holdings(holdings):
    for crypto, amount in holdings.items():
        
        print('\t' + crypto + ' ' + str(amount) + " at $" + str(rh.get_crypto_quote(crypto)['mark_price']))

def get_crypto_holdings_capital(rhcrypto, holdings):
    capital = 0
    
    for crypto_name, crypto_amount in holdings.items():
        capital += crypto_amount * float(rhcrypto.get_latest_price([crypto_name])[0])
        
    return capital

if __name__ == "__main__":
    login()
    
    export_orders = input("Export a CSV of completed crypto orders when finished? (True or False): ")
    
    while export_orders != "True" and export_orders != "False":
        export_orders = input("Export a CSV of completed crypto orders when finished? (True or False): ")
        
    if export_orders == "True":
        export_orders = True
    else:
        export_orders = False
    
    mode = input("Select trader setting ('LIVE', 'BACKTEST', or 'SAFE-LIVE'): ")
    
    while mode != 'LIVE' and mode != 'BACKTEST' and mode != 'SAFE-LIVE':
        mode = input("Select trader setting ('LIVE', 'BACKTEST', or 'SAFE-LIVE'): ")
    
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

    while continue_trading(tr):
        prices = rhcrypto.get_latest_price(stocks)
        
        holdings, bought_price = get_holdings_and_bought_price(rhcrypto, stocks)
        
        cash, equity = get_cash()
        
        if inital_capital_is_init == False:
            initial_capital = get_crypto_holdings_capital(rhcrypto, holdings) + cash
            
            inital_capital_is_init = True
        
        tr.set_profit(cash + get_crypto_holdings_capital(rhcrypto, holdings) - initial_capital)
        
        print("======================" + mode + "======================")
        print("runtime: " + tr.display_time(tr.get_runtime()))
        
        print("total equity: $" + str(equity))
        
        print('crypto holdings:')
        display_holdings(holdings)
        
        print("total crypto equity: $" + str(get_crypto_holdings_capital(rhcrypto, holdings)))
        print("cash: $" + str(cash))
        
        print("profit: " + tr.display_profit())

        for i, stock in enumerate(stocks):
            
            price = float(prices[i])
            
            print('\n{} = ${}'.format(stock, price))

            trade = tr.trade_option(stock)
            
            print('trade:', trade, end='\n\n')
            
            if trade == "BUY":
                allowable_holdings = (cash / 10) / price
                
                if allowable_holdings > 0:
                    
                    buy(rhcrypto, stock, allowable_holdings, price)

                else:
                    print("Not enough allowable holdings")
                    
                    trade = "UNABLE TO BUY"
            elif trade == "SELL":
                if holdings[stock] > 0:

                    sell(rhcrypto, stock, holdings[stock], price)
                else:
                    print("Not enough holdings")

                    trade = "UNABLE TO SELL"
            
            price_dict[stock] = price
            
            trade_dict[stock] = trade

        df_trades, df_prices = build_dataframes(df_trades, trade_dict, df_prices, price_dict)
        
        print('\ndf_prices \n', df_prices, end='\n\n')
        print('df_trades \n', df_trades, end='\n\n')
        
        print("Waiting " + str(tr.get_interval_sec()) + ' seconds...')
        time.sleep(tr.get_interval_sec())

    logout()
    
    if export_orders:
        rh.export.export_completed_crypto_orders('./', 'completed_crypto_orders')
