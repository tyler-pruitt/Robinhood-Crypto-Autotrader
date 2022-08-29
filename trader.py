import numpy as np
import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings

import robin_stocks.robinhood as rh
import robin_stocks.helper as helper
import robin_stocks.urls as urls

class Trader():
    def __init__(self, stocks):
        self.stocks = stocks
        
        self.start_time = time.time()
        self.previous_time = [time.time()] * len(self.stocks)
        
        # Set both buy and sell buffers to 0.1%
        self.sell_buffer = 0.001
        self.buy_buffer = 0.001

        # Loss threshold taken to be a positive value
        self.loss_threshold = abs(5.00)
        
        self.interval = "5minute"
        self.span = "day"
        
        self.profit = 0.0
        
        self.previous_trade = "NONE"
        self.trade = "NONE"
    
    def __repr__(self):
        return "Trader(crypto: " + str(self.stocks) + ", profit: " + self.display_profit() + ", runtime: " + self.display_time(self.get_runtime()) + ")"
    
    def display_time(self, seconds, granularity=5):
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
    
    def get_interval_sec(self):
        for i in range(1, len(self.interval)):
            try:
                digit = int(self.interval[:i])
            except ValueError:
                break
        
        time = self.interval[i-1:]
        
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
    
    def set_trade(self, trade):
        self.trade = trade
    
    def get_trade(self):
        return self.trade
    
    def set_previous_trade(self, trade):
        self.previous_trade = trade
    
    def get_previous_trade(self):
        return self.previous_trade
    
    def get_loss_threshold(self):
        return self.loss_threshold
    
    def set_loss_threshold(self, loss):
        if loss >= 0:
            self.loss_threshold = loss
        else:
            print("Loss must be set to a POSITIVE value: loss threshold not reset")
    
    def get_runtime(self):
        return time.time() - self.start_time

    def set_profit(self, profit):
        self.profit = profit
    
    def get_profit(self):
        return self.profit
    
    def display_profit(self, currency='$'):

        if self.profit >= 0:
            text = '+'
        else:
            text = '-'
        
        text += currency

        text += str(abs(self.profit))

        return text
    
    def set_interval(self, interval):
        self.interval = interval
    
    def set_span(self, span):
        self.span = span
    
    def get_interval(self):
        return self.interval
    
    def get_span(self):
        return self.span
    
    def set_sell_buffer(self, buffer):
        self.sell_buffer = buffer
    
    def get_sell_buffer(self):
        return self.sell_buffer
    
    def set_buy_buffer(self, buffer):
        self.buy_buffer = buffer
    
    def get_buy_buffer(self):
        return self.buy_buffer
    
    def get_stocks(self):
        return self.stocks
    
    def set_stocks(self, stocks):
        self.stocks = stocks
    
    def get_start_time(self):
        return self.start_time
    
    def set_start_time(self, time):
        self.start_time = time
    
    def get_previous_time(self, stock):
        return self.previous_time[self.stocks.index(stock)]
    
    def set_previous_time(self, stock, time):
        self.previous_time[self.stocks.index(stock)] = time
    
    def plot_model(self, stock, df, window, degree, coefficients, pause=1):
        # df is df_historical_prices
        stock_prices = []
        
        stock_data = df.to_numpy()
        
        for i in range(len(stock_data) - window, len(stock_data)):
            stock_prices.append(stock_data[i][0])
        
        times = list(range(len(stock_prices)))
        
        plt.figure(clear=True)
        plt.plot(times, stock_prices, 'k-')
        
        model_output = []
        
        for instance in times:
            model_output.append(np.polyval(coefficients, instance))
        
        plt.plot(times, model_output, 'b-')
        
        title = stock + " vs. Model: deg:" + str(degree) + ", window:" + str(window) + ", interval:" + self.interval + ", span:" + self.span
        
        plt.title(title)
        plt.ylabel("Price ($)")
        plt.xlabel("Time (" + self.interval + ")")
        plt.legend([stock, "model"], loc="upper left")
        plt.draw()
        plt.pause(pause)

    def get_historical_prices(self, stock, interval, span):
        span_interval = {'day': '5minute', 'week': '10minute', 'month': 'hour', '3month': 'hour', 'year': 'day', '5year': 'week'}
        #interval = span_interval[span]
        
        historical_data = rh.crypto.get_crypto_historicals(stock, interval=interval, span=span, bounds='24_7')

        df = pd.DataFrame(historical_data)

        dates_times = pd.to_datetime(df.loc[:, 'begins_at'])
        close_prices = df.loc[:, 'close_price'].astype('float')

        df_price = pd.concat([close_prices, dates_times], axis=1)
        df_price = df_price.rename(columns={'close_price': stock})
        df_price = df_price.set_index('begins_at')

        return df_price
    
    def poly_fit(self, market_data, window, degree):
        
        price_data = market_data.to_numpy()
        
        price = np.zeros(window, float)
        
        count = 0
        
        for i in range(len(price_data) - window, len(price_data)):
            price[count] = price_data[i][0]
            count += 1
        
        time = list(range(window))
        
        # If full is False or is not set to True, keep the line below
        #warnings.simplefilter('ignore', np.RankWarning)
        
        fit_data = np.polynomial.polynomial.polyfit(x=time, y=price, deg=degree, full=True)
        
        return fit_data

    def trade_option(self, stock):
        
        if time.time() - self.get_previous_time(stock) >= 0.25:
            
            df_historical_prices = self.get_historical_prices(stock, interval=self.interval, span=self.span)
            self.set_previous_time(stock, time.time())
        
        min_resid = float('inf')
        optimal_coeff, optimal_deg, optimal_window = [], 0, 0
        
        for window in range(10, len(df_historical_prices)):
            for degree in range(3, 11):
                coeff, fit_data = self.poly_fit(df_historical_prices, window, degree)
                
                if fit_data[2][0] < min_resid:
                    min_resid = fit_data[2][0]
                    optimal_coeff = list(coeff)
                    optimal_deg = fit_data[1]
                    optimal_window = window
        
        optimal_coeff.reverse()
        
        self.plot_model(stock, df_historical_prices, optimal_window, optimal_deg, optimal_coeff)
        
        #print(stock + " optimal polynomial fit:", optimal_coeff)
        
        # https://pandas.pydata.org/docs/reference/api/pandas.Timestamp.html#pandas.Timestamp
        #times = list(pd.to_datetime(df_historical_prices.loc[:, 'begins_at']))
        
        # Determine the trend of the prices
        derivative = np.polyder(np.poly1d(optimal_coeff))
        
        # derivative(optimal_window - 1) is the last index for the times given
        if derivative(optimal_window - 1) > 0:
            print(stock + " has a rising behaviour: buy")

            # If the prediction is that the price will increase, buy
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("BUY")
        elif derivative(optimal_window - 1) < 0:
            print(stock + " has a falling behaviour: sell")

            # If the prediction is that the price will decrease, sell
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("SELL")
        else:
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("HOLD")

        return self.get_trade()
