#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 10:19:51 2021

@author: codingandfun.com
"""

import pandas_datareader.data as web
import datetime
import requests

class Wacc:   
    
    def __init__(self, secretkey, start=None, end=None):
        self.secretkey=secretkey
        if start == None:
            tmp = datetime.datetime.today() - datetime.timedelta(days=365)
            self.start = tmp.strftime('%Y-%m-%d')
        else:
            self.start=start
        if end == None:
            tmp = datetime.datetime.today()
            self.end=tmp.strftime('%Y-%m-%d')
        else: 
            self.end = end
    
    def interest_coveraga_and_RF(self, company):
      IS= requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?apikey={self.secretkey}').json()
      EBIT= IS[0]['ebitda'] - IS[0]['depreciationAndAmortization'] 
      interest_expense = IS[0]['interestExpense']
      interest_coverage_ratio = EBIT / interest_expense
      Treasury = web.DataReader(['TB1YR'], 'fred', self.start, self.end)
      RF = float(Treasury.iloc[-1])
      RF = RF/100
      return [RF,interest_coverage_ratio]
      

    #Cost of debt
    def cost_of_debt(self, company, RF,interest_coverage_ratio):
      if interest_coverage_ratio > 8.5:
        #Rating is AAA
        credit_spread = 0.0063
      if (interest_coverage_ratio > 6.5) & (interest_coverage_ratio <= 8.5):
        #Rating is AA
        credit_spread = 0.0078
      if (interest_coverage_ratio > 5.5) & (interest_coverage_ratio <=  6.5):
        #Rating is A+
        credit_spread = 0.0098
      if (interest_coverage_ratio > 4.25) & (interest_coverage_ratio <=  5.49):
        #Rating is A
        credit_spread = 0.0108
      if (interest_coverage_ratio > 3) & (interest_coverage_ratio <=  4.25):
        #Rating is A-
        credit_spread = 0.0122
      if (interest_coverage_ratio > 2.5) & (interest_coverage_ratio <=  3):
        #Rating is BBB
        credit_spread = 0.0156
      if (interest_coverage_ratio > 2.25) & (interest_coverage_ratio <=  2.5):
        #Rating is BB+
        credit_spread = 0.02
      if (interest_coverage_ratio > 2) & (interest_coverage_ratio <=  2.25):
        #Rating is BB
        credit_spread = 0.0240
      if (interest_coverage_ratio > 1.75) & (interest_coverage_ratio <=  2):
        #Rating is B+
        credit_spread = 0.0351
      if (interest_coverage_ratio > 1.5) & (interest_coverage_ratio <=  1.75):
        #Rating is B
        credit_spread = 0.0421
      if (interest_coverage_ratio > 1.25) & (interest_coverage_ratio <=  1.5):
        #Rating is B-
        credit_spread = 0.0515
      if (interest_coverage_ratio > 0.8) & (interest_coverage_ratio <=  1.25):
        #Rating is CCC
        credit_spread = 0.0820
      if (interest_coverage_ratio > 0.65) & (interest_coverage_ratio <=  0.8):
        #Rating is CC
        credit_spread = 0.0864
      if (interest_coverage_ratio > 0.2) & (interest_coverage_ratio <=  0.65):
        #Rating is C
        credit_spread = 0.1134
      if interest_coverage_ratio <=  0.2:
        #Rating is D
        credit_spread = 0.1512
      cost_of_debt = RF + credit_spread
      return cost_of_debt


    def costofequity(self, company):
      Treasury = web.DataReader(['TB1YR'], 'fred', self.start, self.end)
      RF = float(Treasury.iloc[-1])
      RF = RF/100
      beta = requests.get(f'https://financialmodelingprep.com/api/v3/company/profile/{company}?apikey={self.secretkey}')
      beta = beta.json()
      beta = float(beta['profile']['beta'])
      SP500 = web.DataReader(['sp500'], 'fred', self.start, self.end)
      #Drop all Not a number values using drop method.
      SP500.dropna(inplace = True)
      SP500yearlyreturn = (SP500['sp500'].iloc[-1]/ SP500['sp500'].iloc[-252])-1   
      #CAPM Formula   
      cost_of_equity = RF+(beta*(SP500yearlyreturn - RF))
      return cost_of_equity

    #effective tax rate and capital structure
    def calc_wacc(self, company):
      FR = requests.get(f'https://financialmodelingprep.com/api/v3/ratios/{company}?apikey={self.secretkey}').json()
      ETR = FR[0]['effectiveTaxRate'] 
      
      BS = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?&apikey={self.secretkey}').json()
      Debt_to = BS[0]['totalDebt'] / (BS[0]['totalDebt'] + BS[0]['totalStockholdersEquity'])
      equity_to = BS[0]['totalStockholdersEquity'] / (BS[0]['totalDebt'] + BS[0]['totalStockholdersEquity'])
      
      ke = self.costofequity(company)
      
      ICRF=self.interest_coveraga_and_RF(company)
      RF = ICRF[0]
      interest_coverage_ratio = ICRF[1]
      kd = self.cost_of_debt(company, RF, interest_coverage_ratio)
      
      WACC = (kd*(1-ETR)*Debt_to) + (ke*equity_to)
      return WACC