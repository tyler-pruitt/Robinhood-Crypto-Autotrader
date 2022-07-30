import config
import grapher

import numpy as np
import pandas as pd
import time
#import warnings

import robin_stocks.robinhood as rh
import robin_stocks.helper as helper
import robin_stocks.urls as urls

class Trader():
    def __init__(self, stocks):
        self.stocks = stocks

        self.sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}
        
        self.start_time = time.time()
        self.previous_time = time.time()
        
        # On Robinhood market orders are adjusted to limit orders collared up to 1% for buys, and 5% for sells.
        # https://robinhood.com/us/en/support/articles/why-is-the-price-displayed-on-the-crypto-detail-pages-different-from-the-final-buy-and-sell-price-on-the-order-page/
        #self.sellBuffer = 0.05
        #self.buyBuffer = 0.01
        
        # Set both buy and sell buffers to 0.1%
        self.sellBuffer = 0.001
        self.buyBuffer = 0.001
        
        self.interval = "15second"
        self.span = "hour"

        self.price_sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}

    def get_historical_prices(self, rhcrypto, stock, interval, span):
        span_interval = {'day': '5minute', 'week': '10minute', 'month': 'hour', '3month': 'hour', 'year': 'day', '5year': 'week'}
        #interval = span_interval[span]
        
        historical_data = rh.crypto.get_crypto_historicals(stock, interval=interval, span=span, bounds='24_7')

        df = pd.DataFrame(historical_data)

        dates_times = pd.to_datetime(df.loc[:, 'begins_at'])
        close_prices = df.loc[:, 'close_price'].astype('float')

        df_price = pd.concat([close_prices, dates_times], axis=1)
        df_price = df_price.rename(columns={'close_price': stock})
        df_price = df_price.set_index('begins_at')

        return(df_price)

    def get_sma(self, stock, df_prices, window=12):
        sma = df_prices.rolling(window=window, min_periods=window).mean()
        sma = round(float(sma[stock].iloc[-1]), 8)
        return(sma)

    def get_price_sma(self, price, sma):
        price_sma = round(price/sma, 8)
        return(price_sma)
    
    def poly_fit(self, prices, window, degree):
        
        y_data = prices.to_numpy()
        
        y = np.zeros(window, float)
        
        count = 0
        
        for i in range(len(y_data) - window, len(y_data)):
            y[count] = y_data[i][0]
            count += 1
        
        x = list(range(window))
        
        # if full is False or is left unchanged keep the line below
        #warnings.simplefilter('ignore', np.RankWarning)
        
        fit_data = np.polynomial.polynomial.polyfit(x, y, degree, full=True)
        
        return fit_data

    def trade_option(self, rhcrypto, stock, price):
        
        if time.time() - self.previous_time >= 0.15:
            df_historical_prices = self.get_historical_prices(rhcrypto, stock, interval=self.interval, span=self.span)
            self.previous_time = time.time()
            
            # gets new sma_hour every 15 seconds
            self.sma_hour[stock] = self.get_sma(stock, df_historical_prices[-12:], window=12)

        self.price_sma_hour[stock] = self.get_price_sma(price, self.sma_hour[stock])
        p_sma = self.price_sma_hour[stock]
        
        if self.price_sma_hour[stock] < 1.0 - self.buyBuffer:
            i1 = "BUY"
        elif self.price_sma_hour[stock] > 1.0 + self.sellBuffer:
            i1 = "SELL"
        else:
            i1 = "NONE"
        
        min_resid = float('inf')
        optimal_coeff, optimal_deg, optimal_window = [], 0, 0
        
        for window in range(10, len(df_historical_prices)):
            for degree in range(1, 11):
                coeff, fit_data = self.poly_fit(df_historical_prices, window, degree)
                
                if fit_data[2][0] < min_resid:
                    min_resid = fit_data[2][0]
                    optimal_coeff = list(coeff)
                    optimal_deg = fit_data[1]
                    optimal_window = window
        
        optimal_coeff.reverse()
        
        grapher.plot_crypto_model(stock, df_historical_prices, optimal_window, optimal_deg, optimal_coeff, self.interval, self.span)
        
        print(stock + " optimal polynomial fit:", optimal_coeff)
        
        # Buy low and sell high
        derivative = np.polyder(np.poly1d(optimal_coeff))
        
        if derivative(optimal_window - 1) > 0:
            print(stock + " has a rising behaviour: sell")
            i2 = "SELL"
        elif derivative(optimal_window - 1) < 0:
            print(stock + " has a falling behaviour: buy")
            i2 = "BUY"
        else:
            i2 = "NONE"
        
        # Determine the trade (i1: simple moving average with normalization, i2: polynomial fit)
        if i2 == "BUY":
            trade = "BUY"
        elif i2 == "SELL":
            trade = "SELL"
        else:
            trade = "HOLD"

        return(trade)
    
    def get_runtime(self):
        return time.time() - self.start_time
