# Create your own personal trading strategy to trade with
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd

import robin_stocks.robinhood as rh
import robin_stocks.helper as helper
import robin_stocks.urls as urls

class Trader():
    def __init__(self, stocks):
        self.stocks = stocks

        self.sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}
        self.run_time = 0
        
        # On Robinhood market orders are adjusted to limit orders collared up to 1% for buys, and 5% for sells.
        # https://robinhood.com/us/en/support/articles/why-is-the-price-displayed-on-the-crypto-detail-pages-different-from-the-final-buy-and-sell-price-on-the-order-page/
        self.sellBuffer = 0.05
        self.buyBuffer = 0.01

        self.price_sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}

    def get_historical_prices(self, rhcrypto, stock, span):
        span_interval = {'day': '5minute', 'week': '10minute', 'month': 'hour', '3month': 'hour', 'year': 'day', '5year': 'week'}
        interval = span_interval[span]

        '''Due to users receiving a 404 Error, the historical data section has been updated'''
        # symbols = helper.inputs_to_set(stock)
        # url = urls.historicals()
        # payload = { 'symbols' : ','.join(symbols),
        #             'interval' : interval,
        #             'span' : span,
        #             'bounds' : 'regular'}
        #
        # data = helper.request_get(url,'results',payload)
        #
        # historical_data = []
        # for item in data:
        #     for subitem in item['historicals']:
        #         historical_data.append(subitem)
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
    
    def polynomial_fit(self, stock, df_prices, window):
        # STILL NEED TO IMPLEMENT
        y = df_prices.rolling(window=window, min_periods=window)
        x = list(range(0, window))

    def trade_option(self, rhcrypto, stock, price):
        # gets new sma_hour every 5min
        if self.run_time % (5) == 0:
            df_historical_prices = self.get_historical_prices(rhcrypto, stock, span='day')
            self.sma_hour[stock] = self.get_sma(stock, df_historical_prices[-12:], window=12)

        self.price_sma_hour[stock] = self.get_price_sma(price, self.sma_hour[stock])
        p_sma = self.price_sma_hour[stock]
        
        if self.price_sma_hour[stock] < 1.0 - self.buyBuffer:
            i1 = "BUY"
        elif self.price_sma_hour[stock] > 1.0 + self.sellBuffer:
            i1 = "SELL"
        else:
            i1 = "NONE"
        
        if i1 == "BUY":
            trade = "BUY"
        elif i1 == "SELL":
            trade = "SELL"
        else:
            trade = "HOLD"

        return(trade)
