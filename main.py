import config
import trader
import grapher

import robin_stocks.robinhood as rh
import datetime as dt
import time
import pandas as pd
import numpy as np

from robinhood_crypto_api import RobinhoodCrypto

def login(days):
    time_logged_in = 60 * 60 * 24 * days
    rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)

def logout():
    rh.authentication.logout()

def open_market():
    """
    market = False
    time_now = dt.datetime.now().time()

    market_open = dt.time(9,30,0) # 9:30AM
    market_close = dt.time(15,59,0) # 3:59PM

    if time_now > market_open and time_now < market_close:
        market = True
    else:
        print('### market is closed')
        pass

    return(market)
    """
    return True

def get_cash():
    rh_cash = rh.account.build_user_profile()

    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    
    
    return(cash, equity)

def get_holdings_and_bought_price(rhcrypto, stocks):
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
    # un-comment when ready to trade on the live market
    
    print('sell is currently commented')
    
    # sell_order = rh.orders.order_sell_limit(symbol=stock,
    #                                         quantity=holdings,
    #                                         limitPrice=sell_price,
    #                                         timeInForce='gfd')
    """
    sell_order_info = rhcrypto.trade(
        pair=stock,
        price=round(price, 2),
        quantity="holdings",
        side="buy",
        time_in_force="gtc",
        type="limit"
    )
    """

    print('### Trying to SELL {} amount of {} at ${}'.format(holdings, stock, price))
    
    #return sell_order_info

def buy(rhcrypto, stock, allowable_holdings, price):
    # buy_price = round((price + 0.10), 2)
    # un-comment when ready to trade on the live market
    
    print('buy is currently commented')
    
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

    print('### Trying to BUY {} of {} at ${}'.format(allowable_holdings, stock, price))

    #return buy_order_info

def build_dataframes(df_trades, trade_dict, df_prices, price_dict):
    time_now = str(dt.datetime.now().time())[:8]
    
    df_trades.loc[time_now] = trade_dict
    df_prices.loc[time_now] = price_dict
    
    
    return(df_trades, df_prices)

def display_time(seconds, granularity=5):
    result = []
    
    intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    
    
    return ', '.join(result[:granularity])

if __name__ == "__main__":
    login(days=1)
    rhcrypto = RobinhoodCrypto(config.USERNAME, config.PASSWORD)
    
    stocks = config.CRYPTO
    
    print('cryptos:', stocks)
    
    cash, equity = get_cash()

    ts = trader.Trader(stocks)

    trade_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    price_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    
    df_trades = pd.DataFrame(columns=stocks)
    df_prices = pd.DataFrame(columns=stocks)

    while open_market():
        prices = rhcrypto.get_latest_price(stocks)
        
        holdings, bought_price = get_holdings_and_bought_price(rhcrypto, stocks)
        
        print("==========================================")
        print("runtime: " + display_time(ts.get_runtime()))
        print('crypto holdings:', holdings)

        for i, stock in enumerate(stocks):
            
            price = float(prices[i])
            
            print('{} = ${}'.format(stock, price))

            trade = ts.trade_option(rhcrypto, stock, price)
            
            print('trade:', trade, end='\n\n')
            
            if trade == "BUY":
                allowable_holdings = (cash / 10) / price
                
                if allowable_holdings > 0:
                    buy(stock, allowable_holdings, price)
                else:
                    print("Not enough allowable holdings")
                    trade = "UNABLE TO BUY"
            elif trade == "SELL":
                if holdings[stock] > 0:
                    sell(stock, holdings[stock], price)
                else:
                    print("Not enough holdings")
                    trade = "UNABLE TO SELL"
            
            price_dict[stock] = price
            
            trade_dict[stock] = trade

        df_trades, df_prices = build_dataframes(df_trades, trade_dict, df_prices, price_dict)
        
        grapher.active_graph(grapher.normalize(df_prices), df_trades)

        time.sleep(30)

    logout()
