#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 10:18:19 2021

@author: valeriomellini
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import yfinance as yf
import requests

def extract_fcf(cash_flow, n):
    if n >= 0:
        return [cash_flow[n]['freeCashFlow']] + (extract_fcf(cash_flow, n-1))
    else:
        return [] 

def linear_regression_model(Y):
    #X = np.array([i for i in range (0,len(Y))]).reshape(-1,1)
    X = np.array([i for i in range (-len(Y), 0)]).reshape(-1,1)
    Y = np.array(Y)
    lm = LinearRegression()
    lm.fit(X, Y)
    return (lm.intercept_, lm.coef_)

def linear_regression_prediction(model, acc, n):
    if n > 0:
        return [model[0] + model[1][0] * acc] + linear_regression_prediction(model, acc+1, n-1)
    else:
        return []

def dcf_calc(pred, wacc, n, multiplier = 1):
    if n>1:
        return (pred[n-1] / pow(1 + wacc, n)) * multiplier + dcf_calc(pred, wacc, n-1, multiplier=1)
    if n == 1:
        return pred[n-1] / pow(1 + wacc, n)
    if n <=0:
        return 0

def getFreeCashFlow(company, secretkey):
    cash_flow = requests.get(f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{company}?apikey={secretkey}').json()
    #freeCashFlow
    len_cash_flow = len(cash_flow)
    fcf_extracted = None
    if len_cash_flow >= 5:
        fcf_extracted = extract_fcf(cash_flow, 4)
    else:
        fcf_extracted = extract_fcf(cash_flow, len_cash_flow-1)
    return fcf_extracted
        