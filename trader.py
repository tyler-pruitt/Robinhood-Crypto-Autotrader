import numpy as np
import pandas as pd
import datetime as dt
import time as t
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import warnings
import pandas_ta as ta

import config
from indicators import MA, EMA, RSI, MACD

import robin_stocks.robinhood as rh
import robin_stocks.helper as helper
import robin_stocks.urls as urls

class Trader():
    def __init__(self, stocks, initial_capital):
        self.stocks = stocks
        
        self.initial_capital = initial_capital
        
        self.start_time = t.time()

        # Loss threshold (in dollars) taken to be a positive value
        self.loss_threshold = 50.00
        
        # RSI overbought and oversold thresholds
        self.oversold = 30
        self.overbought = 70
        
        self.interval = "15second"
        self.span = "hour"
        
        self.profit = 0.0
        self.percent_change = 0.0
        
        self.trade = ''
        self.previous_trade = ''
        
        # self.buy_times = [{datetime: 'status'}]
        # status possibilities arew ['live_buy', 'simulated_buy', 'unable_to_buy', 'live_sell', 'simulated_sell', unable_to_sell']
        self.buy_times = [dict()] * len(stocks)
        self.sell_times = [dict()] * len(stocks)
        
        assert self.loss_threshold >= 0
        
        assert self.oversold >= 0 and self.oversold <= 100
        
        assert self.overbought >= 0 and self.overbought <= 100
        
        assert self.profit == 0.0
    
    def get_percent_change(self):
        return self.percent_change
    
    def get_overbought_threshold(self):
        return self.overbought
    
    def get_oversold_threshold(self):
        return self.oversold
    
    def set_overbought_threshold(self, threshold):
        self.overbought = threshold
    
    def set_oversold_threshold(self, threshold):
        self.oversold = threshold
    
    def __repr__(self):
        return "Trader(profit: " + self.display_profit() + " (" + self.display_percent_change() + "), runtime: " + self.display_time(self.get_runtime()) + ")"
    
    def continue_trading(self, override=None):
        if override != None:
            assert type(override) == bool
            
            return override
        else:
            if self.get_profit() >= -1 * self.get_loss_threshold():
                return True
            else:
                print("Loss exceeded $" + str(self.get_loss_threshold()) + ": terminating automated trading")
    
                return False
    
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
        return t.time() - self.start_time

    def set_profit(self, profit):
        """
        Sets Trader.profit and Trader.percent_change accordingly
        """
        self.profit = profit
        
        self.percent_change = (profit * 100) / self.initial_capital
    
    def get_profit(self):
        return self.profit
    
    def display_profit(self, currency='$'):

        if self.profit >= 0:
            text = '+'
        else:
            text = '-'
        
        text += currency

        text += str(abs(round(self.profit, 2)))

        return text
    
    def display_percent_change(self):

        if self.percent_change >= 0:
            text = '+'
        else:
            text = '-'

        text += str(abs(round(self.percent_change, 2)))
        text += '%'

        return text
    
    def set_interval(self, interval):
        self.interval = interval
    
    def set_span(self, span):
        self.span = span
    
    def get_interval(self):
        return self.interval
    
    def get_span(self):
        return self.span
    
    def get_stocks(self):
        return self.stocks
    
    def set_stocks(self, stocks):
        self.stocks = stocks
    
    def get_start_time(self):
        return self.start_time
    
    def set_start_time(self, time):
        self.start_time = time
    
    def get_historical_data(self, stock, interval, span):
        historical_data = rh.crypto.get_crypto_historicals(stock, interval=interval, span=span, bounds='24_7')
        
        # df contains all the data (eg. time, open, close, high, low, volume, session, interpolated, symbol)
        df = pd.DataFrame(historical_data)
        
        return df
    
    def get_historical_times(self, stock, interval, span):
        # df contains all the data (eg. time, open, close, high, low)
        df = self.get_historical_data(stock, interval, span)
        
        dates_times = pd.to_datetime(df.loc[:, 'begins_at'])
        
        return dates_times

    def get_historical_prices(self, stock, interval, span):
        # df contains all the data (eg. time, open, close, high, low)
        df = self.get_historical_data(stock, interval, span)

        dates_times = pd.to_datetime(df.loc[:, 'begins_at'])
        close_prices = df.loc[:, 'close_price'].astype('float')

        df_price = pd.concat([close_prices, dates_times], axis=1)
        df_price = df_price.rename(columns={'close_price': stock})
        df_price = df_price.set_index('begins_at')

        return df_price
    
    def convert_dataframe_to_list(self, df, is_nested=False):
        df = df.to_numpy()
        
        data = []
        
        for i in range(len(df)):
            if is_nested:
                data.append(df[i][0])
            else:
                data.append(df[i])
        
        return data

    def determine_trade(self, stock, stock_historicals=None):
        
        if config.MODE == 'BACKTEST':
            assert stock_historicals != None
            
            # Set times and prices given stock_historicals
            # For this algorithm, need times and prices to be of length >= (macd_slow_period + macd_signal_period - 1) = 34
            times, prices = [], []
            
            for k in range(len(stock_historicals)):
                times += [stock_historicals[k]['begins_at']]
                
                prices += [float(stock_historicals[k]['close_price'])]
        else:
            df_historical_prices = self.get_historical_prices(stock, interval=self.interval, span=self.span)
            
            # For this algorithm, need times and prices to be of length >= (macd_slow_period + macd_signal_period - 1) = 34
            
            # https://pandas.pydata.org/docs/reference/api/pandas.Timestamp.html#pandas.Timestamp
            times = self.convert_dataframe_to_list(self.get_historical_times(stock, self.interval, self.span))
            prices = self.convert_dataframe_to_list(df_historical_prices, True)
        
        rsi_data = RSI(times, prices, 14)
        
        if rsi_data[-1][1] > self.get_overbought_threshold():
            rsi_indicator = "SELL"
        elif rsi_data[-1][1] < self.get_oversold_threshold():
            rsi_indicator = "BUY"
        else:
            rsi_indicator = "HOLD"
        
        macd, signal = MACD(times, prices, 12, 26, 9)
        macd_signal_difference = []
        
        for i in range(len(macd)):
            for j in range(len(signal)):
                if macd[i][0] == signal[j][0]:
                    macd_signal_difference.append([signal[j][0], macd[i][1] - signal[j][1]])
        
        if macd_signal_difference[-1][1] > 0:
            macd_signal_indicator = "SELL"
        elif macd_signal_difference[-1][1] < 0:
            macd_signal_indicator = "BUY"
        else:
            macd_signal_indicator = "HOLD"
        
        if config.PLOTANALYTICS:
            self.plot_analytics(stock, macd, signal, macd_signal_difference, rsi_data)
        
        if config.PLOTCRYPTO:
            self.plot_crypto(stock, prices, times)
        
        if rsi_indicator == "BUY" and macd_signal_indicator == "BUY":
            
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("BUY")
        elif rsi_indicator == "SELL" and macd_signal_indicator == "SELL":
            
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("SELL")
        else:
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("HOLD")

        return self.get_trade()
    
    def plot_crypto(self, stock, prices, price_times, pause=1):
        # RGBA: [red, green, blue, alpha]
        """
        status_to_color = {
            'live_buy': dark_red,
            'simulated_buy': light_red,
            'unable_to_buy': yellow,
            'live_sell': dark_green,
            'simulated_sell': light_green,
            'unable_to_sell': blue
        }
        """
        status_to_color = {'live_buy': [1, 0, 0, 1], 'simulated_buy': [1, 0, 0, 0.5], 'unable_to_buy': [1, 1, 0, 1], 'live_sell': [0, 1, 0, 1], 'simulated_sell': [0, 1, 0, 0.5], 'unable_to_sell': [0, 0, 1, 1]}
        
        buy_x, buy_y, buy_color = [], [], []
        sell_x, sell_y, sell_color = [], [], []
        
        for i in range(len(price_times)):
            price_times[i] = self.convert_timestamp_to_datetime(price_times[i])
        
        for time, status in self.buy_times[self.stocks.index(stock)].items():
            
            min_abs_distance, min_index = dt.timedelta(days=9999), 0
            
            for i in range(len(price_times)):
                if abs(price_times[i] - time) < min_abs_distance:
                    min_abs_distance = abs(price_times[i] - time)
                    min_index = i
            
            buy_x += [price_times[min_index]]
            buy_y += [prices[min_index]]
            buy_color += [status_to_color[status]]
        
        for time, status in self.sell_times[self.stocks.index(stock)].items():
            min_abs_distance, min_index = dt.timedelta(days=9999), 0
            
            for i in range(len(price_times)):
                if abs(price_times[i] - time) < min_abs_distance:
                    min_abs_distance = abs(price_times[i] - time)
                    min_index = i
            
            sell_x += [price_times[min_index]]
            sell_y += [prices[min_index]]
            sell_color += [status_to_color[status]]
        
        plt.figure(clear=True)
        plt.plot_date(price_times, prices, 'g-')
        
        # https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers
        plt.scatter(x=buy_x, y=buy_y, c=buy_color)
        plt.scatter(x=sell_x, y=sell_y, c=sell_color)
        
        plt.title(stock)
        plt.ylabel("Price ($)")
        plt.xlabel("Time")
        plt.show()
        plt.pause(pause)
    
    def plot_macd_signal(self, stock, macd, signal, pause=1):
        
        macd_data, macd_times = [], []
    
        for i in range(len(macd)):
            macd_data.append(macd[i][1])
            macd_times.append(self.convert_timestamp_to_datetime(macd[i][0]))
        
        signal_data, signal_times = [], []
        
        for i in range(len(signal)):
            signal_data.append(signal[i][1])
            signal_times.append(self.convert_timestamp_to_datetime(signal[i][0]))
        
        plt.figure(clear=True)
        plt.plot_date(macd_times, macd_data, 'b-')
        plt.plot_date(signal_times, signal_data, 'r-')
        plt.title(stock)
        plt.ylabel("MACD vs. Signal")
        plt.legend(["MACD", "Signal"], loc='upper left')
        plt.xlabel("Time")
        plt.show()
        plt.pause(pause)
    
    def plot_macd_signal_difference(self, stock, macd_signal_difference, pause=1):
        
        macd_signal_data, macd_signal_times = [], []
        
        for i in range(len(macd_signal_difference)):
            macd_signal_times.append(self.convert_timestamp_to_datetime(macd_signal_difference[i][0]))
            macd_signal_data.append(macd_signal_difference[i][1])
        
        zeroLine = []
        for i in range(len(macd_signal_times)):
            zeroLine.append(0)
        
        plt.figure(clear=True)
        plt.plot_date(macd_signal_times, macd_signal_data, 'r-')
        plt.plot_date(macd_signal_times, zeroLine, 'k--')
        plt.title(stock)
        plt.ylabel("MACD - Signal")
        plt.xlabel("Time")
        plt.show()
        plt.pause(pause)
    
    def plot_rsi(self, stock, rsi, pause=1):
        rsi_data, rsi_times = [], []
        
        for i in range(len(rsi)):
            rsi_times.append(self.convert_timestamp_to_datetime(rsi[i][0]))
            rsi_data.append(rsi[i][1])
        
        overbought_line, oversold_line = [], []
        
        for i in range(len(rsi_times)):
            overbought_line.append(self.get_overbought_threshold())
            oversold_line.append(self.get_oversold_threshold())
        
        plt.figure(clear=True)
        plt.plot_date(rsi_times, rsi_data, 'r-')
        plt.plot_date(rsi_times, overbought_line, 'k--')
        plt.plot_date(rsi_times, oversold_line, 'k--')
        plt.title(stock)
        plt.ylabel("RSI")
        plt.xlabel("Time")
        plt.show()
        plt.pause(pause)
    
    def plot_analytics(self, stock, macd, signal, macd_signal_difference, rsi):
        self.plot_macd_signal(stock, macd, signal)
        self.plot_macd_signal_difference(stock, macd_signal_difference)
        self.plot_rsi(stock, rsi)
    
    def convert_timestamp_to_datetime(self, timestamp):
        if type(timestamp) != str:
            timestamp = str(timestamp)[:-6]
        
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        
        hour = int(timestamp[11:13])
        minute = int(timestamp[14:16])
        second = int(timestamp[17:19])
        
        return dt.datetime(year, month, day, hour, minute, second)
