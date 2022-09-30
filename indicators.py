#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 14:39:58 2022

@author: tylerpruitt
"""

def MA(times, prices, period):
    """
    Moving Average
    """
    
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
    Weighted Moving Average
    """
    
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
    Moving Average Convergence Divergence
    """
    
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
