#test per DCF da video   https://www.youtube.com/watch?v=2dmIWDeRIyo&t=608s
#usa i dati del sito https://site.financialmodelingprep.com
#mia key e8031887778ab76659fbf1423e804a29

import yfinance as yf
import pandas as pd
import datetime
import json
from wacc import Wacc
from dcf import getFreeCashFlow, dcf_calc, linear_regression_prediction, linear_regression_model, extract_fcf


#in pratica la domanda che si sta facendo è:
#quale deve essere il valore dell'azione perchè io in 5 anni guadagno 10000 euro?
#è la formula inversa dell'interesse composto

company='RACE'
skey=''

with open('/content/drive/MyDrive/Programmazione-COLAB/PRJ-Portfolio/predittivo/settings.json', 'r') as j:
  skey=json.load(j)["fml_secretkey"]

fcf = getFreeCashFlow(company, skey)
stock = yf.Ticker(company)
stock_info=stock.info
curr =stock.info["currency"]
title =stock.info["shortName"]
#print(stock.info)
previous_close=stock.info["regularMarketPreviousClose"]
sharesOutstanding = stock_info["sharesOutstanding"]

#Wacc - media pesata del costo del debito e dell'equity

wacc = Wacc(skey, start="2019-01-01")
wacc_company = wacc.calc_wacc(company)
#print('wacc of '+company +' is '+ str((wacc_company*100))+'%')

#DCF
model = linear_regression_model(fcf)
fcf_pred = linear_regression_prediction(model, 1, 5)

print(f"Free cash flow extracted {fcf}")
print(f"Free cash flow predicted for the next 5 years {fcf_pred}")

dcf = dcf_calc(fcf_pred, wacc_company, len(fcf_pred), multiplier =1)
fair_price = dcf/ sharesOutstanding

print(f'\n\n--> The fair price calculated for {title} is {fair_price:0.2f} {curr}. Current price is {previous_close:0.2f} {curr}.')



print('ok fin qua')