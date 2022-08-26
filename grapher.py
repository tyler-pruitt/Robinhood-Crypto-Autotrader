import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np


def plot_crypto_model(stock, df, window, degree, coefficients, interval, span, pause=1):
    # df is df_historical_prices
    stock_prices = []
    
    stock_data = df.to_numpy()
    
    for i in range(len(stock_data) - window, len(stock_data)):
        stock_prices.append(stock_data[i][0])
    
    times = list(range(len(stock_prices)))
    
    #plt.clf()
    #plt.figure()
    
    plt.plot(times, stock_prices, 'k-')
    
    model_output = []
    
    for time in times:
        model_output.append(np.polyval(coefficients, time))
    
    plt.plot(times, model_output, 'b-')
    
    title = stock + " vs. Model: deg" + str(degree) + ", window" + str(window) + ", interval" + interval + ", span" + span
    
    plt.title(title)
    plt.ylabel("Price ($)")
    plt.xlabel("Time (" + interval + ")")
    plt.legend([stock, "model"], loc="upper left")
    plt.draw()
    plt.pause(pause)
