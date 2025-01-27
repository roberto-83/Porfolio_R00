#usa i dati del sito https://site.financialmodelingprep.com
#mia key e8031887778ab76659fbf1423e804a29

import json
import pandas as pd
import requests

skey='e8031887778ab76659fbf1423e804a29'

#with open('/content/drive/MyDrive/Programmazione-COLAB/PRJ-Portfolio/predittivo/settings.json', 'r') as j:
 # skey=json.load(j)["fml_secretkey"]

#1 - Lista di tutti ETF e AZIONI 
#all_stocks=requests.get(f'https://financialmodelingprep.com/api/v3/stock/list?apikey={skey}').json()
#all_stocks_df = pd.json_normalize(all_stocks, meta=['symbol','name','price','type','exchangeShortName'])
###print(json.dumps(all_stocks, indent=1))
#print(all_stocks_df)

#all_etf=requests.get(f'https://financialmodelingprep.com/api/v3/etf/list?apikey={skey}').json()
#all_etf_df = pd.json_normalize(all_etf, meta=['symbol','name','price','type','exchangeShortName'])
##print(json.dumps(all_etf, indent=1))
#print(all_etf_df)

#tutte le aziende con dati economici presenti
#https://financialmodelingprep.com/api/v3/financial-statement-symbol-lists

#list cot report commodities-->PAGAMENTO
#cot_rep= requests.get(f'https://financialmodelingprep.com/api/v4/commitment_of_traders_report/list?apikey={skey}').json()
#print(json.dumps(cot_rep, indent=1))


#2 - Info base stock 
#ticker='RACE.MI'
#stock_search= requests.get(f'https://financialmodelingprep.com/api/v3/search?apikey={skey}&query={ticker}').json()
#print(json.dumps(stock_search, indent=1))

#3 - COMPANY PROFILE (gratuito solo per azioni americane..)
#ticker='BRK'
#stock_profile= requests.get(f'https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={skey}').json()
#print(json.dumps(stock_profile, indent=1))

#4 - screener 
https://financialmodelingprep.com/api/v3/stock-screener

#search isin https://financialmodelingprep.com/api/v4/search/isin?isin=US0378331005

####STOCK LIST
#https://financialmodelingprep.com/api/v3/stock/list

####ETF LIST 
#https://financialmodelingprep.com/api/v3/etf/list

####COT REPORT
#https://financialmodelingprep.com/api/v4/commitment_of_traders_report/list


####STOCK GRADE - non disponibile purtroppo nella versione gratuita
#https://financialmodelingprep.com/api/v3/grade/AAPL
#stock_grade= requests.get(f'https://financialmodelingprep.com/api/v3/grade/{ticker}?apikey={skey}').json()
#print(json.dumps(stock_grade, indent=1))


####STOCK ESTIMATES ####STOCK GRADE 
#stock_grade= requests.get(f'https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?apikey={skey}').json()
#print(json.dumps(stock_grade, indent=1))

####STOCK ESTIMATES ####STOCK GRADE 
#stock_grade= requests.get(f'https://financialmodelingprep.com/api/v3/analyst-stock-recommendations/{ticker}?apikey={skey}').json()
#print(json.dumps(stock_grade, indent=1))

####STOCK LOGO   -- prova a scaricare..
#ttps://financialmodelingprep.com/image-stock/EURUSD.png
#stock_grade= requests.get(f'https://financialmodelingprep.com/image-stock/{ticker}.png?apikey={skey}').json()
#print(json.dumps(stock_grade, indent=1))
####STOCK


#EBIT= IS[0]['ebitda'] - IS[0]['depreciationAndAmortization'] 
#interest_expense = IS[0]['interestExpense']