import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np

def normalize(df):
    # df.shape = (rows, columns)
    if len(df.shape) == 1 or df.shape[1] == 1:
        dfNORMALIZED = df/df.iloc[0]
    else:
        dfNORMALIZED = pd.DataFrame()
        trading_days = df.index
        for stock in df.columns.values.tolist():
            dfNORMALIZED[stock] = pd.Series(df[stock]/df[stock].iloc[0], index=trading_days)

    return(dfNORMALIZED)

def active_graph(df, df_trades, pause=1):
    plt.clf()
    plt.ion()
    plt.title('active_graph')
    plt.xlabel('Time')
    plt.xticks([])
    plt.ylabel('Normalized Price')

    for stock in df_trades.columns.values.tolist():
        if df_trades[stock].iloc[-1] == 'UNABLE TO BUY' or df_trades[stock].iloc[-1] == 'BUY':
            plt.plot(df[stock], alpha=1.0)
        elif df_trades[stock].iloc[-1] == 'UNABLE TO SELL' or df_trades[stock].iloc[-1] == 'SELL':
            plt.plot(df[stock], alpha=0.2)

        for day, order in df_trades.iterrows():
            if order[stock] == 'BUY':
                plt.axvline(day, color='g', alpha=0.25)
            elif order[stock] == 'SELL':
                plt.axvline(day, color='r', alpha=0.25)

    print('df_prices \n', df, end='\n\n')
    print('df_trades \n', df_trades, end='\n\n')

    plt.legend(df.columns.values.tolist(), loc='upper left')
    plt.draw()
    plt.savefig(str(dt.date.today()))
    plt.pause(pause)

def plot_crypto_model(stock, df, window, degree, coefficients, interval, span, pause=1):
    # df is df_historical_prices
    stock_prices = []
    
    stock_data = df.to_numpy()
    
    for i in range(len(stock_data) - window, len(stock_data)):
        stock_prices.append(stock_data[i][0])
    
    times = list(range(len(stock_prices)))
    
    plt.clf()
    plt.figure()
    
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
