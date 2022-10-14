import config
import trader
import order

import robin_stocks.robinhood as rh
import datetime as dt
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

# Make sure to take advantage of robin_stocks.robinhood documentation: https://robin-stocks.readthedocs.io/en/latest/robinhood.html

def login():
    time_logged_in = 60 * 60 * 24 * config.TIMEINDAYS
    
    rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=False)
    
    print("login successful")

def logout():
    rh.authentication.logout()
    
    print("logout successful")

def get_cash():
    rh_cash = rh.account.build_user_profile()

    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    
    
    return(cash, equity)

def plot_portfolio(time, portfolio):
    plt.plot(time, portfolio, 'g-')
    plt.title("Portfolio (cash + crypto equity)")
    plt.xlabel("Runtime (in seconds)")
    plt.ylabel("Price ($)")
    plt.show()

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

def convert_time_to_sec(time):
    """
    RUNTIME IS TOO SLOW
    """
    
    assert type(time) == str
    
    digit = 1
    
    for i in range(1, len(time)):
        try:
            digit = int(time[:i])
        except ValueError:
            break
    
    time = time[i-1:]
    
    if time == 'second':
        sec = digit
    elif time == 'minute':
        sec = 60 * digit
    elif time == 'hour':
        sec = 3600 * digit
    elif time == 'day':
        sec = 86400 * digit
    elif time == 'week':
        sec = 604800 * digit
    else:
        raise ValueError
    
    return sec

def display_holdings(holdings):
    for crypto, amount in holdings.items():
        
        print('\t' + str(amount) + ' ' + crypto + " at $" + str(rh.get_crypto_quote(crypto)['mark_price']))

def update_output(iteration_num, tr, equity, holdings, cash, total_iteration_num=None):
    """
    Prints out the lastest information out to consol
    """
    
    if config.MODE != 'BACKTEST':
        print("======================ITERATION " + str(iteration_num) + "======================")
    else:
        print("======================ITERATION " + str(iteration_num) + '/' + str(total_iteration_num) + "======================")
    
    print("mode: " + config.MODE)
    print("runtime: " + tr.display_time(tr.get_runtime()))
    
    print("total equity: $" + str(equity))
    
    print('crypto holdings:')
    display_holdings(holdings)
    
    print("total crypto equity: $" + str(get_crypto_holdings_capital(holdings)))
    print("cash: $" + str(cash))
    print("total crypto equity and cash: $" + str(cash + get_crypto_holdings_capital(holdings)))
    
    print("profit: " + tr.display_profit() + " (" + tr.display_percent_change() + ")")

def download_backtest_data(stocks):
    
    crypto_historical_data = []
    
    for i in range(len(stocks)):
        
        crypto_historical_data += [rh.crypto.get_crypto_historicals(symbol=stocks[i], interval=config.INTERVAL, span=config.SPAN, bounds=config.BOUNDS)]
    
    print("downloading backtesting data finished")
    
    return crypto_historical_data

def check_config():
    assert type(config.TIMEINDAYS) == int and config.TIMEINDAYS >= 1

    assert type(config.USERNAME) == str and type(config.PASSWORD) == str
    
    assert len(config.USERNAME) > 0 and len(config.PASSWORD) > 0
    
    assert config.MODE in ['LIVE', 'BACKTEST', 'SAFELIVE']
    
    assert type(config.EXPORTCSV) == bool

    assert type(config.PLOTANALYTICS) == bool
    
    assert type(config.PLOTCRYPTO) == bool
    
    assert type(config.PLOTPORTFOLIO) == bool

    assert type(config.CRYPTO) == list and len(config.CRYPTO) > 0
    
    # Use rh.crypto.get_crypto_currency_pairs() for 'pairs' so that it is up-to-date
    
    crypto_pair_data = rh.crypto.get_crypto_currency_pairs()
    
    pairs = []
    
    for i in range(len(crypto_pair_data)):
        if crypto_pair_data[i]['tradability'] == 'tradable':
            pairs += [crypto_pair_data[i]['asset_currency']['code']]
            pairs += [crypto_pair_data[i]['symbol']]
    
    for i in range(len(config.CRYPTO)):
        assert config.CRYPTO[i] in pairs
    
    assert type(config.USECASH) == bool
    
    if config.USECASH:
        assert type(config.CASH) == float or type(config.CASH) == int
        
        assert config.CASH > 0
    
    if config.MODE == 'BACKTEST':
        intervals = ['15second', '5minute', '10minute', 'hour', 'day', 'week']
        spans = ['hour', 'day', 'week', 'month', '3month', 'year', '5year']
        bounds = ['Regular', 'trading', 'extended', '24_7']
        
        assert type(config.INTERVAL) == str
        
        assert config.INTERVAL in intervals
        
        assert type(config.SPAN) == str
        
        assert config.SPAN in spans
        
        assert type(config.BOUNDS) == str
        
        assert config.BOUNDS in bounds
        
        assert config.USECASH == True
    elif config.MODE == 'LIVE':
        
        assert config.USECASH == False
    
    print("configuration test: PASSED")

if __name__ == "__main__":
    
    check_config()
    
    login()
    
    try:
        
        if config.MODE == 'LIVE':
            is_live = True
        else:
            is_live = False
        
        stocks = config.CRYPTO
        
        print('cryptos:', stocks, end='\n\n')
        
        if config.MODE == 'BACKTEST':
            crypto_historicals = download_backtest_data(stocks)
            
            # Set initial_backtest_index to 33 (33 = macd_slow_period + macd_signal_period) for tr.determine_trade_macd_rsi()
            # Set initial_backtest_index to 19 (19 = period + 1) for tr.determine_trade_boll()
            
            #initial_backtest_index = 33
            initial_backtest_index = 19
            
            backtest_index = initial_backtest_index
            
            total_iteration_num = convert_time_to_sec(config.SPAN) // convert_time_to_sec(config.INTERVAL) - initial_backtest_index
        
        cash, equity = get_cash()
    
        trade_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
        price_dict = {stocks[i]: 0 for i in range(0, len(stocks))}
        
        df_trades = pd.DataFrame(columns=stocks)
        df_prices = pd.DataFrame(columns=stocks)
        
        # Initialization of holdings and bought price (necessary to be here due to different modes and cash initializations)
        holdings, bought_price = get_holdings_and_bought_price(stocks)
        
        # Initialization of initial_capital and cash (if necessary)
        # This initialization needs to be here due to different modes and cash initializations
        if config.USECASH == False or is_live:
            
            initial_capital = get_crypto_holdings_capital(holdings) + cash
        else:
            initial_capital = config.CASH
            
            # Initialize cash to config.CASH
            cash = config.CASH
        
        assert initial_capital > 0
        
        tr = trader.Trader(stocks, initial_capital)
        
        if is_live:
            outgoing_order_queue, filled_orders = [], []
        
        if config.PLOTPORTFOLIO:
            time_data, portfolio_data = [], []
        
        iteration_num = 1
        
        if config.MODE != 'BACKTEST':
            average_iteration_runtime = 0
        
        cash_divisor, holdings_divisor = 5, 5
        
        if cash_divisor < len(stocks):
            cash_divisor = len(stocks)
        
        if holdings_divisor < len(stocks):
            holdings_divisor = len(stocks)
        
        while tr.continue_trading():
            iteration_runtime_start = time.time()
            
            if config.MODE == 'BACKTEST':
                if backtest_index == len(crypto_historicals[0]):
                    print("backtesting finished")
                    
                    break
                elif backtest_index > len(crypto_historicals[0]):
                    print("not enough backtesting data to perform calculations")
                    
                    break
            
            if is_live:
                while len(outgoing_order_queue) > 0:
                    if outgoing_order_queue[0].is_filled():
    
                        filled_orders.append(outgoing_order_queue[0])
    
                        outgoing_order_queue.pop(0)
                    else:
                        break
            
            if config.MODE != 'BACKTEST':
                prices = get_latest_price(stocks)
            else:
                prices = []
                
                for i in range(len(stocks)):
                    prices += [crypto_historicals[i][backtest_index]['close_price']]
            
            if config.USECASH == False or is_live:
                # Update holdings and bought_price
                holdings, bought_price = get_holdings_and_bought_price(stocks)
                
                # Update cash and equity
                cash, equity = get_cash()
            else:
                # Update only equity
                _, equity = get_cash()
            
            tr.set_profit(cash + get_crypto_holdings_capital(holdings) - initial_capital)
            
            if config.MODE == 'BACKTEST':
                update_output(iteration_num, tr, equity, holdings, cash, total_iteration_num)
            else:
                update_output(iteration_num, tr, equity, holdings, cash)
            
            if config.PLOTPORTFOLIO:
                time_data += [tr.get_runtime()]
                portfolio_data += [cash + get_crypto_holdings_capital(holdings)]
                
                plot_portfolio(time_data, portfolio_data)
            
            for i, stock in enumerate(stocks):
                
                price = float(prices[i])
                
                print('\n{} = ${}'.format(stock, price))
                
                if config.MODE != 'BACKTEST':
                    #trade = tr.determine_trade_macd_rsi(stock)
                    
                    trade = tr.determine_trade_boll(stock)
                else:
                    #trade = tr.determine_trade_macd_rsi(stock, crypto_historicals[i][:backtest_index+1])
                    
                    trade = tr.determine_trade_boll(stock, crypto_historicals[i][:backtest_index+1])
                
                print('trade:', trade, end='\n\n')
                
                if trade == "BUY":
                    if config.MODE != 'BACKTEST':
                        price = round(float(get_latest_price([stock])[0]), 2)
                    
                    if cash > 0:
                        
                        # https://robin-stocks.readthedocs.io/en/latest/robinhood.html#placing-and-cancelling-orders
                        
                        dollars_to_sell = cash / cash_divisor
                        
                        print('Attempting to BUY ${} of {} at price ${}'.format(dollars_to_sell, stock, price))
                        
                        if is_live:
                            print("LIVE: Buy order is going through")
    
                            if len(outgoing_order_queue) == 0:
                                print("No orders still in queue: new order will execute")
    
                                # Limit order by price
                                #order_info = rh.orders.order_buy_crypto_limit_by_price(symbol=stock, amountInDollars=dollars_to_sell, limitPrice=price, timeInForce='gtc', jsonify=True)
                                
                                # Market order
                                order_info = rh.orders.order_buy_crypto_by_price(symbol=stock, amountInDollars=dollars_to_sell, timeInForce='gtc', jsonify=True)
                                
                                outgoing_order_queue.append(order.Order(order_info))
                                
                                print("Order info:", order_info)
                                
                                tr.buy_times[i][dt.datetime.now()] = 'live_buy'
                            else:
                                print("Orders are still in queue: order is canceled")
                                
                                trade = "UNABLE TO BUY (ORDERS STILL IN QUEUE)"
                                
                                tr.buy_times[i][dt.datetime.now()] = 'unable_to_buy'
                            
                        else:
                            print(config.MODE + ": live buy order is not going through")
                            
                            # Simulate buying the crypto by subtracting from cash, adding to holdings, and adjusting average bought price
                            
                            cash -= dollars_to_sell
                            
                            holdings_to_add = dollars_to_sell / price
                            
                            bought_price[stock] = ((bought_price[stock] * holdings[stock]) + (holdings_to_add * price)) / (holdings[stock] + holdings_to_add)
                            
                            holdings[stock] += holdings_to_add
                            
                            trade = "SIMULATION BUY"
                            
                            if config.MODE == 'SAFELIVE':
                                tr.buy_times[i][dt.datetime.now()] = 'simulated_buy'
                            else:
                                tr.buy_times[i][tr.convert_timestamp_to_datetime(crypto_historicals[i][backtest_index]['begins_at'])] = 'simulated_buy'
    
                    else:
                        print("Not enough cash")
                        
                        trade = "UNABLE TO BUY (NOT ENOUGH CASH)"
                        
                        if config.MODE != 'BACTEST':
                            tr.buy_times[i][dt.datetime.now()] = 'unable_to_buy'
                        else:
                            tr.buy_times[i][tr.convert_timestamp_to_datetime(crypto_historicals[i][backtest_index]['begins_at'])] = 'unable_to_buy'
                elif trade == "SELL":
                    if holdings[stock] > 0:
                        
                        # https://robin-stocks.readthedocs.io/en/latest/robinhood.html#placing-and-cancelling-orders
                        
                        if config.MODE != 'BACKTEST':
                            price = round(float(get_latest_price([stock])[0]), 2)
                        
                        holdings_to_sell = holdings[stock] / holdings_divisor
                        
                        print('Attempting to SELL {} of {} at price ${} for ${}'.format(holdings_to_sell, stock, price, round(holdings_to_sell * price, 2)))
    
                        if is_live:
                            print("LIVE: Sell order is going through")
    
                            if len(outgoing_order_queue) == 0:
                                print("No orders still in queue: new order will execute")
    
                                # Limit order by price for a set quantity
                                #order_info = rh.orders.order_sell_crypto_limit(symbol=stock, quantity=holdings_to_sell, limitPrice=price, timeInForce='gtc', jsonify=True)
                                
                                # Market order
                                order_info = rh.orders.order_sell_crypto_by_quantity(symbol=stock, quantity=holdings_to_sell, timeInForce='gtc', jsonify=True)
                                
                                outgoing_order_queue.append(order.Order(order_info))
                                
                                print("Order info:", order_info)
                                
                                tr.sell_times[i][dt.datetime.now()] = 'live_sell'
                            else:
                                print("Orders are still in queue: order is canceled")
                                
                                trade = "UNABLE TO SELL (ORDERS STILL IN QUEUE)"
                                
                                if config.MODE == 'SAFELIVE':
                                    tr.sell_times[i][dt.datetime.now()] = 'unable_to_sell'
                                else:
                                    tr.sell_times[i][tr.convert_timestamp_to_datetime(crypto_historicals[i][backtest_index]['begins_at'])] = 'unable_to_sell'
                            
                        else:
                            print(config.MODE + ": live sell order is not going through")
                            
                            # Simulate selling the crypto by adding to cash and subtracting from holdings
                            cash += holdings_to_sell * price
                            
                            holdings[stock] -= holdings_to_sell
                            
                            # Average bought price is unaffected when selling
                            if holdings[stock] == 0:
                                bought_price[stock] = 0
                            
                            trade = "SIMULATION SELL"
                            
                            if config.MODE == 'SAFELIVE':
                                tr.sell_times[i][dt.datetime.now()] = 'simulated_sell'
                            else:
                                tr.sell_times[i][tr.convert_timestamp_to_datetime(crypto_historicals[i][backtest_index]['begins_at'])] = 'simulated_sell'
                        
                    else:
                        print("Not enough holdings")
    
                        trade = "UNABLE TO SELL (NOT ENOUGH HOLDINGS)"
                        
                        if config.MODE != 'BACKTEST':
                            tr.sell_times[i][dt.datetime.now()] = 'unable_to_sell'
                        else:
                            tr.sell_times[i][tr.convert_timestamp_to_datetime(crypto_historicals[i][backtest_index]['begins_at'])] = 'unable_to_sell'
                
                price_dict[stock] = price
                
                trade_dict[stock] = trade
    
            df_trades, df_prices = build_dataframes(df_trades, trade_dict, df_prices, price_dict)
            
            print('\ndf_prices \n', df_prices, end='\n\n')
            print('df_trades \n', df_trades, end='\n\n')
            
            if config.MODE != 'BACKTEST':
                iteration_runtime_end = time.time()
                
                if average_iteration_runtime == 0:
                    
                    average_iteration_runtime = iteration_runtime_end - iteration_runtime_start
                else:
                    # Update average_iteration_runtime
                    average_iteration_runtime *= iteration_num
                    
                    average_iteration_runtime += (iteration_runtime_end - iteration_runtime_start)
                
                    average_iteration_runtime /= (iteration_num + 1)
                
                wait_time = convert_time_to_sec(tr.get_interval()) - average_iteration_runtime
                
                if wait_time < 0:
                    wait_time = 0
                
                print("Waiting " + str(round(wait_time, 2)) + ' seconds...')
                
                time.sleep(wait_time)
            else:
                backtest_index += 1
            
            iteration_num += 1
        
        logout()
        
        if config.EXPORTCSV:
            rh.export.export_completed_crypto_orders('./', 'completed_crypto_orders')
    
    except KeyboardInterrupt:
        print("User ended execution of program.")
        
        logout()
        
        if config.EXPORTCSV:
            rh.export.export_completed_crypto_orders('./', 'completed_crypto_orders')
    
    except Exception:
        print("An error occured: stopping process")
        
        logout()
        
        if config.EXPORTCSV:
            rh.export.export_completed_crypto_orders('./', 'completed_crypto_orders')
        
        print("Error message:", sys.exc_info())
