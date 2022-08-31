import numpy as np
import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import warnings
#import pandas_ta as ta

from indicators import MA, EMA, RSI, MACD

import robin_stocks.robinhood as rh
import robin_stocks.helper as helper
import robin_stocks.urls as urls

class Trader():
    def __init__(self, stocks):
        self.stocks = stocks
        
        self.start_time = time.time()
        self.previous_time = [time.time()] * len(self.stocks)

        # Loss threshold taken to be a positive value
        self.loss_threshold = abs(5.00)
        
        # RSI overbought and oversold thresholds
        self.oversold = 30
        self.overbought = 70
        
        self.interval = "15second"
        self.span = "hour"
        
        self.profit = 0.0
        
        self.trade = ''
        self.previous_trade = ''
    
    def get_overbought_threshold(self):
        return self.overbought
    
    def get_oversold_threshold(self):
        return self.oversold
    
    def set_overbought_threshold(self, threshold):
        self.overbought = threshold
    
    def set_oversold_threshold(self, threshold):
        self.oversold = threshold
    
    def __repr__(self):
        return "Trader(crypto: " + str(self.stocks) + ", profit: " + self.display_profit() + ", runtime: " + self.display_time(self.get_runtime()) + ")"
    
    def continue_trading(self, override=False):
        # Assumes there is no condition for which the user will want the trading bot to stop trading
        if override:
            return True
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

        text += str(abs(round(self.profit, 2)))

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
    
    def get_previous_time(self, stock):
        return self.previous_time[self.stocks.index(stock)]
    
    def set_previous_time(self, stock, time):
        self.previous_time[self.stocks.index(stock)] = time
    
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

    def determine_trade(self, stock):
        
        if time.time() - self.get_previous_time(stock) >= 0.25:
            
            df_historical_prices = self.get_historical_prices(stock, interval=self.interval, span=self.span)
            self.set_previous_time(stock, time.time())
        
        # https://pandas.pydata.org/docs/reference/api/pandas.Timestamp.html#pandas.Timestamp
        times = self.convert_dataframe_to_list(self.get_historical_times(stock, self.interval, self.span))
        prices = self.convert_dataframe_to_list(df_historical_prices, True)
        
        rsi_data = RSI(times, prices, 14)
        
        print("RSI:", rsi_data[-1][1])
        
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
        
        print("MACD", macd[-1][1])
        print("signal:", signal[-1][1])
        print("difference:", macd_signal_difference[-1][1])
        
        if macd_signal_difference[-1][1] > 0:
            macd_signal_indicator = "SELL"
        elif macd_signal_difference[-1][1] < 0:
            macd_signal_indicator = "BUY"
        else:
            macd_signal_indicator = "HOLD"
        
        self.plot_indicator(stock, prices, times, macd, signal, macd_signal_difference, rsi_data)
        
        if rsi_indicator == "BUY" and macd_signal_indicator == "BUY":

            # If the prediction is that the price will increase, buy
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("BUY")
        elif rsi_indicator == "SELL" and macd_signal_indicator == "SELL":

            # If the prediction is that the price will decrease, sell
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("SELL")
        else:
            self.set_previous_trade(self.get_trade())
            
            self.set_trade("HOLD")

        return self.get_trade()
    
    def plot_stock(self, stock, prices, price_times, pause=1):
        
        for i in range(len(price_times)):
            price_times[i] = self.convert_timestamp_to_datetime(price_times[i])
        
        plt.figure(clear=True)
        plt.plot_date(price_times, prices, 'g-')
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
    
    def plot_indicator(self, stock, prices, price_times, macd, signal, macd_signal_difference, rsi, pause=1):
        self.plot_stock(stock, prices, price_times)
        self.plot_macd_signal(stock, macd, signal)
        self.plot_macd_signal_difference(stock, macd_signal_difference)
        self.plot_rsi(stock, rsi)
    
    def convert_timestamp_to_datetime(self, timestamp):
        string = str(timestamp)[:-6]
        
        year = int(string[:4])
        month = int(string[5:7])
        day = int(string[8:10])
        
        hour = int(string[11:13])
        minute = int(string[14:16])
        second = int(string[17:19])
        
        return dt.datetime(year, month, day, hour, minute, second)
