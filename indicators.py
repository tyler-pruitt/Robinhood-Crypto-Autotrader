#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def MA(times, prices, period):
    """
    Moving Average (MA)
    """
    
    assert len(times) == len(prices)
    
    ma = []
    
    for i in range(len(prices) - period + 1):
        total = 0
        
        for j in range(i, i+period):
            
            total += prices[j]
        
        total /= period
        
        ma.append([times[i + period - 1], total])
    
    return ma

def EMA(times, prices, period):
    """
    Exponential Moving Average (EMA)
    """
    
    assert len(times) == len(prices)
    
    ema = []
    
    # First calculate the moving average for the first length
    ma = 0
    
    for i in range(period):
        ma += prices[i]
    
    ma /= period
    
    
    ema.append([times[period-1], ma])
    
    multiplier = 2 / (period + 1)
    
    # Calculate the EMA for the rest of the lengths
    for i in range(period, len(prices)):
        ema.append([times[i], (prices[i] * multiplier + (ema[-1][1] * (1 - multiplier)))])
    
    return ema

def RSI(times, prices, period):
    """
    Relative Strength Index (RSI)
    """
    
    assert len(times) == len(prices)
    assert len(times) >= period + 2
    assert len(prices) >= period + 2
    
    RSI = []
    
    for i in range(1, len(prices) - period):
        count_gain, count_loss = 0, 0
        
        for j in range(i, i + period):
            if prices[j] - prices[j-1] > 0:
                count_gain += 1
            elif prices[j] - prices[j-1] < 0:
                count_loss += 1
        
        avgU = count_gain / period
        avgD = count_loss / period
        
        try:
            RSI.append([times[j+1], 100 - 100 / (1 + (avgU / avgD))])
        except ZeroDivisionError:
            RSI.append([times[j+1], 100])
    
    return RSI

def MACD(times, prices, fast_period, slow_period, signal_period):
    """
    Moving Average Convergence Divergence (MACD)
    """
    
    assert len(times) == len(prices)
    assert len(times) >= slow_period + signal_period - 1
    assert len(prices) >= slow_period + signal_period - 1
    
    macd = []
    signal = []
    
    fast = EMA(times, prices, fast_period)
    
    slow = EMA(times, prices, slow_period)
    
    for i in range(len(slow)):
        for j in range(len(fast)):
            if slow[i][0] == fast[j][0]:
                macd.append([slow[i][0], fast[j][1] - slow[i][1]])
    
    macd_times, macd_values = [], []
    
    for i in range(len(macd)):
        macd_times.append(macd[i][0])
        macd_values.append(macd[i][1])
    
    signal = EMA(macd_times, macd_values, signal_period)
    
    return macd, signal

def BOLL(times, prices, period=20, std_width=2):
    """
    Bollinger bands (BOLL)
    
    Returns:
        [{'time': 'time1',
          'moving_average': 0.397,
          'upper_band': 0.348,
          'lower_band': 0.299},
         {'time': 'time2',
          'moving_average': 0.972,
          'upper_band': 1.000
          'lower_band': 0.944}
         ]
    """
    
    assert len(times) == len(prices)
    assert len(times) >= period
    assert len(prices) >= period
    
    moving_average = MA(times, prices, period)
    
    boll = []
    
    for i in range(len(moving_average)):
        std = np.std(prices[i:i+period])
        
        boll += [{'time': moving_average[i][0], 'moving_average': moving_average[i][1], 'upper_band': moving_average[i][1] + (std * std_width), 'lower_band': moving_average[i][1] - (std * std_width)}]
    
    return boll
