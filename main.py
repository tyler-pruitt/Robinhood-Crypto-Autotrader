import config
import backtest
import trader
import order

import robin_stocks.robinhood as rh
import datetime as dt
import time
import pandas as pd
import numpy as np

from robinhood_crypto_api import RobinhoodCrypto

# Make sure to take advantage of https://robin-stocks.readthedocs.io/en/latest/robinhood.html#getting-crypto-information

def login():
    time_logged_in = 60 * 60 * 24 * config.TIMEINDAYS
    
    rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)
    
    print("robin_stonks.robinhood login successful")

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
        
        print('\t' + str(amount) + ' ' + crypto + " at $" + str(rh.get_crypto_quote(crypto)['mark_price']))

if __name__ == "__main__":
    assert type(config.TIMEINDAYS) == int and config.TIMEINDAYS >= 1

    assert type(config.USERNAME) == str and type(config.PASSWORD) == str
    assert len(config.USERNAME) > 0 and len(config.PASSWORD) > 0
    
    login()
    
    mode = config.MODE
    available_modes = ['LIVE', 'BACKTEST', 'SAFE-LIVE']
    assert mode in available_modes
    
    if mode == 'LIVE':
        is_live = True
    else:
        is_live = False
    
    assert type(config.EXPORTCSV) == bool

    assert type(config.PLOTGRAPH) == bool

    assert type(config.CRYPTO) == list and len(config.CRYPTO) > 0
    
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
    
    outgoing_order_queue, filled_orders = [], []

    while tr.continue_trading():
        
        if len(outgoing_order_queue) > 0:
            while len(outgoing_order_queue) > 0:
                if rhcrypto.is_order_filled(outgoing_order_queue[0]['id']):
                    filled_orders.append(outgoing_order_queue[0])
                    outgoing_order_queue.pop(0)
                else:
                    break
        
        prices = rhcrypto.get_latest_price(stocks)
        
        holdings, bought_price = rhcrypto.get_holdings_and_bought_price(stocks)
        
        cash, equity = get_cash()
        
        if inital_capital_is_init == False:
            initial_capital = rhcrypto.get_crypto_holdings_capital(holdings) + cash
            
            inital_capital_is_init = True
            
            assert initial_capital > 0
        
        tr.set_profit(cash + rhcrypto.get_crypto_holdings_capital(holdings) - initial_capital)
        percent_change = tr.get_profit() * 100 / initial_capital
        
        print("======================" + mode + "======================")
        print("runtime: " + tr.display_time(tr.get_runtime()))
        
        print("total equity: $" + str(equity))
        
        print('crypto holdings:')
        display_holdings(holdings)
        
        print("total crypto equity: $" + str(rhcrypto.get_crypto_holdings_capital(holdings)))
        print("cash: $" + str(cash))
        
        print("profit: " + tr.display_profit() + " (" + tr.display_profit()[0] + str(round(abs(percent_change), 2)) + "%)")

        for i, stock in enumerate(stocks):
            
            price = float(prices[i])
            
            print('\n{} = ${}'.format(stock, price))

            trade = tr.determine_trade(stock)
            
            print('trade:', trade, end='\n\n')
            
            if trade == "BUY":
                price = round(float(rhcrypto.get_latest_price([stock])[0]), 2)
                
                if cash > 0:
                    
                    # https://robin-stocks.readthedocs.io/en/latest/robinhood.html#placing-and-cancelling-orders
                    
                    dollars_to_sell = cash / 10.0
                    
                    print('Attempting to BUY ${} of {} at price ${}'.format(dollars_to_sell, stock, price))
                    
                    if is_live:
                        print("LIVE: Buy order is going through")

                        if len(outgoing_order_queue) == 0:
                            print("No orders still in queue: new order will execute")

                            # Limit order by price
                            #order_info = rh.orders.order_buy_crypto_limit_by_price(symbol=stock, amountInDollars=dollars_to_sell, limitPrice=price, timeInForce='gtc', jsonify=True)
                            
                            # Market order
                            order_info = rh.orders.order_buy_crypto_by_price(symbol=stock, amountInDollars=dollars_to_sell, timeInForce='gtc', jsonify=True)
                            
                            outgoing_order_queue.append(order_info)
                            
                            print("Order info:", order_info)
                        else:
                            print("Orders are still in queue: order is canceled")
                        
                    else:
                        print(mode + ": Buy order is not going through")

                else:
                    print("Not enough cash")
                    
                    trade = "UNABLE TO BUY"
            elif trade == "SELL":
                if holdings[stock] > 0:
                    
                    # https://robin-stocks.readthedocs.io/en/latest/robinhood.html#placing-and-cancelling-orders
                    
                    price = round(float(rhcrypto.get_latest_price([stock])[0]), 2)
                    
                    holdings_to_sell = holdings[stock] / 10.0
                    
                    print('Attempting to SELL {} of {} at price ${} for ${}'.format(holdings_to_sell, stock, price, round(holdings_to_sell * price, 2)))

                    if is_live:
                        print("LIVE: Sell order is going through")

                        if len(outgoing_order_queue) == 0:
                            print("No orders still in queue: new order will execute")

                            # Limit order by price for a set quantity
                            #order_info = rh.orders.order_sell_crypto_limit(symbol=stock, quantity=holdings_to_sell, limitPrice=price, timeInForce='gtc', jsonify=True)
                            
                            # Market order
                            order_info = rh.orders.order_sell_crypto_by_quantity(symbol=stock, quantity=holdings_to_sell, timeInForce='gtc', jsonify=True)
                            
                            outgoing_order_queue.append(order_info)
                            
                            print("Order info:", order_info)
                        else:
                            print("Orders are still in queue: order is canceled")
                        
                    else:
                        print(mode + ": Sell order is not going through")
                    
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
    
    if config.EXPORTCSV:
        rh.export.export_completed_crypto_orders('./', 'completed_crypto_orders')
