import config
import trader
import order

import robin_stocks.robinhood as rh
import datetime as dt
import time
import pandas as pd
import numpy as np

# Make sure to take advantage of robin_stocks.robinhood documentation: https://robin-stocks.readthedocs.io/en/latest/robinhood.html

def login():
    time_logged_in = 60 * 60 * 24 * config.TIMEINDAYS
    
    rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)
    
    print("login successful")

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

def get_crypto_holdings_capital(holdings):
    capital = 0
        
    for crypto_name, crypto_amount in holdings.items():
        capital += crypto_amount * float(get_latest_price([crypto_name])[0])
        
    return capital

def is_order_filled(order_id):
    order_update = rh.orders.get_crypto_order_info(order_id)
    
    if order_update['state'] == 'filled':
        return True
    else:
        return False

def get_latest_price(stocks):
    """
    Returns: list of prices
    """
    
    prices = []
    
    for i in range(len(stocks)):
        prices.append(rh.crypto.get_crypto_quote(stocks[i])['mark_price'])
    
    return prices

def build_holdings():
    """
    Returns {
        'stock1': {
            'price': '76.24',
            'quantity': '2.00',
            'average_buy_price': '79.26',
            },
        'stock2': {
            'price': '76.24',
            'quantity': '2.00',
            'average_buy_price': '79.26',
            }}
    """
    
    holdings_data = rh.crypto.get_crypto_positions()
    
    build_holdings_data = dict()
    
    for i in range(len(holdings_data)):
        nested_data = dict()
        
        nested_data['price'] = get_latest_price([holdings_data[i]["currency"]["code"]])
        nested_data['quantity'] = holdings_data[i]["quantity"]
        
        try:
            nested_data['average_buy_price'] = str(float(holdings_data[i]["cost_bases"][0]["direct_cost_basis"]) / float(nested_data["quantity"]))
        except ZeroDivisionError:
            nested_data['average_buy_price'] = '-'
        
        build_holdings_data[holdings_data[i]["currency"]["code"]] = nested_data
    
    return build_holdings_data

def get_holdings_and_bought_price(stocks):
    holdings = {stocks[i]: 0 for i in range(0, len(stocks))}
    bought_price = {stocks[i]: 0 for i in range(0, len(stocks))}
    
    rh_holdings = build_holdings()

    for stock in stocks:
        try:
            holdings[stock] = float(rh_holdings[stock]['quantity'])
            bought_price[stock] = float(rh_holdings[stock]['average_buy_price'])
        except:
            holdings[stock] = 0
            bought_price[stock] = 0

    return holdings, bought_price

def display_holdings(holdings):
    for crypto, amount in holdings.items():
        
        print('\t' + str(amount) + ' ' + crypto + " at $" + str(rh.get_crypto_quote(crypto)['mark_price']))

def update_output(mode, tr, equity, holdings, cash, percent_change):
    """
    Prints out the lastest information out to consol
    """
    
    print("======================" + mode + "======================")
    print("runtime: " + tr.display_time(tr.get_runtime()))
    
    print("total equity: $" + str(equity))
    
    print('crypto holdings:')
    display_holdings(holdings)
    
    print("total crypto equity: $" + str(get_crypto_holdings_capital(holdings)))
    print("cash: $" + str(cash))
    print("total crypto equity and cash: $" + str(cash + get_crypto_holdings_capital(holdings)))
    
    print("profit: " + tr.display_profit() + " (" + tr.display_profit()[0] + str(round(abs(percent_change), 2)) + "%)")

def check_config():
    assert type(config.TIMEINDAYS) == int and config.TIMEINDAYS >= 1

    assert type(config.USERNAME) == str and type(config.PASSWORD) == str
    
    assert len(config.USERNAME) > 0 and len(config.PASSWORD) > 0
    
    assert config.MODE in ['LIVE', 'BACKTEST', 'SAFELIVE']
    
    assert type(config.EXPORTCSV) == bool

    assert type(config.PLOTGRAPH) == bool

    assert type(config.CRYPTO) == list and len(config.CRYPTO) > 0
    
    pairs = ['BTC','ETH','ETC','BCH','BSV','LTC','DOGE','SHIB','SOL','MATIC','COMP','LINK','UNI','XLM','AVAX','ADA','USDC']
    
    for i in range(len(config.CRYPTO)):
        assert config.CRYPTO[i] in pairs
    
    assert type(config.CASHFORSAFELIVE) == bool
    
    if config.CASHFORSAFELIVE:
        assert type(config.CASH) == float or type(config.CASH) == int
        
        assert config.CASH > 0
    
    assert type(config.DATAPATH) == str

if __name__ == "__main__":
    
    check_config()
    
    login()
    
    mode = config.MODE
    
    if mode == 'LIVE':
        is_live = True
    else:
        is_live = False
    
    stocks = config.CRYPTO
    
    print('cryptos:', stocks)
    
    cash, equity = get_cash()

    tr = trader.Trader(stocks)

    trade_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    price_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
    
    df_trades = pd.DataFrame(columns=stocks)
    df_prices = pd.DataFrame(columns=stocks)
    
    # Initialization of holdings and bought price (necessary to be here due to different modes and cash initializations)
    holdings, bought_price = get_holdings_and_bought_price(stocks)
    
    # Initialization of initial_capital and cash (if necessary)
    # This initialization needs to be here due to different modes and cash initializations
    if config.CASHFORSAFELIVE == False or is_live:
        
        initial_capital = get_crypto_holdings_capital(holdings) + cash
    else:
        initial_capital = config.CASH
        
        # Initialize cash to config.CASH
        cash = config.CASH
    
    assert initial_capital > 0
    
    
    outgoing_order_queue, filled_orders = [], []

    while tr.continue_trading():
        try:
            if len(outgoing_order_queue) > 0:
                while len(outgoing_order_queue) > 0:
                    if is_order_filled(outgoing_order_queue[0]['id']):
                        
                        filled_orders.append(outgoing_order_queue[0])
                        
                        outgoing_order_queue.pop(0)
                    else:
                        break
            
            prices = get_latest_price(stocks)
            
            if config.CASHFORSAFELIVE == False or is_live:
                
                holdings, bought_price = get_holdings_and_bought_price(stocks)
            
            if config.CASHFORSAFELIVE == False or is_live:
                cash, equity = get_cash()
            else:
                # Update only equity
                _, equity = get_cash()
            
            tr.set_profit(cash + get_crypto_holdings_capital(holdings) - initial_capital)
            
            percent_change = tr.get_profit() * 100 / initial_capital
            
            update_output(mode, tr, equity, holdings, cash, percent_change)
    
            for i, stock in enumerate(stocks):
                
                price = float(prices[i])
                
                print('\n{} = ${}'.format(stock, price))
    
                trade = tr.determine_trade(stock)
                
                print('trade:', trade, end='\n\n')
                
                if trade == "BUY":
                    price = round(float(get_latest_price([stock])[0]), 2)
                    
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
                                
                                trade = "UNABLE TO BUY (ORDERS STILL IN QUEUE)"
                            
                        else:
                            print(mode + ": live buy order is not going through")
                            
                            # Simulate buying the crypto by subtracting from cash, adding to holdings, and adjusting average bought price
                            
                            cash -= dollars_to_sell
                            
                            holdings_to_add = dollars_to_sell / price
                            
                            bought_price[stock] = ((bought_price[stock] * holdings[stock]) + (holdings_to_add * price)) / (holdings[stock] + holdings_to_add)
                            
                            holdings[stock] += holdings_to_add
                            
                            trade = "SIMULATION BUY"
    
                    else:
                        print("Not enough cash")
                        
                        trade = "UNABLE TO BUY (NOT ENOUGH CASH)"
                elif trade == "SELL":
                    if holdings[stock] > 0:
                        
                        # https://robin-stocks.readthedocs.io/en/latest/robinhood.html#placing-and-cancelling-orders
                        
                        price = round(float(get_latest_price([stock])[0]), 2)
                        
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
                                
                                trade = "UNABLE TO SELL (ORDERS STILL IN QUEUE)"
                            
                        else:
                            print(mode + ": live sell order is not going through")
                            
                            # Simulate selling the crypto by adding to cash and subtracting from holdings
                            cash += holdings_to_sell * price
                            
                            holdings[stock] -= holdings_to_sell
                            
                            # Average bought price is unaffected when selling
                            if holdings[stock] == 0:
                                bought_price[stock] = 0
                            
                            trade = "SIMULATION SELL"
                        
                    else:
                        print("Not enough holdings")
    
                        trade = "UNABLE TO SELL (NOT ENOUGH HOLDINGS)"
                
                price_dict[stock] = price
                
                trade_dict[stock] = trade
    
            df_trades, df_prices = build_dataframes(df_trades, trade_dict, df_prices, price_dict)
            
            print('\ndf_prices \n', df_prices, end='\n\n')
            print('df_trades \n', df_trades, end='\n\n')
            
            print("Waiting " + str(tr.get_interval_sec()) + ' seconds...', end='\n\n')
            time.sleep(tr.get_interval_sec())
        
        except KeyboardInterrupt:
            break
        
        except Exception:
            print("An error occured: stopping process")
            
            break

    logout()
    
    if config.EXPORTCSV:
        rh.export.export_completed_crypto_orders('./', 'completed_crypto_orders')
