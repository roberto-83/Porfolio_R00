#usa i dati del sito https://site.financialmodelingprep.com
#mia key e8031887778ab76659fbf1423e804a29

import json
import pandas as pd
import requests

skey='e8031887778ab76659fbf1423e804a29'

#with open('/content/drive/MyDrive/Programmazione-COLAB/PRJ-Portfolio/predittivo/settings.json', 'r') as j:
 # skey=json.load(j)["fml_secretkey"]

#1 - Lista di tutti ETF e AZIONI 
# all_stocks=requests.get(f'https://financialmodelingprep.com/api/v3/stock/list?apikey={skey}').json()
# #all_stocks_df = pd.json_normalize(all_stocks, meta=['symbol','name','price','type','exchangeShortName'])
# print(json.dumps(all_stocks, indent=1))
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
#https://financialmodelingprep.com/api/v3/stock-screener

#search isin https://financialmodelingprep.com/api/v4/search/isin?isin=US0378331005

#5 - dati economici 
# tresury_rate= requests.get('https://financialmodelingprep.com/api/v4/treasury?apikey={skey}&from=2023-08-10&to=2025-01-30').json()
# print(json.dumps(tresury_rate, indent=1))
# gdp = requests.get('https://financialmodelingprep.com/api/v4/economic?apikey={skey}&name=GDP').json()
# print(json.dumps(gdp, indent=1))

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


##EUROPA
#link https://data.ecb.europa.eu
#link https://medium.com/@lucamingarelli/easy-access-to-ecb-data-in-python-6015b65dcc0e


from ecbdata import ecbdata
# inflation rate measured by the Harmonised Index of Consumer Prices (HICP) in Euro area
inflation = ecbdata.get_series('ICP.M.U2.N.000000.4.ANR', start='2024-10')
print(inflation.to_string())
#GDP volume growth
real_gbp = ecbdata.get_series('MNA.Q.Y.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.GY',start='2024-10')
print(real_gbp.to_string())

unemployment=ecbdata.get_series('LFSI.M.I9.S.UNEHRT.TOTAL0.15_74.T',start='2024-10')
print(unemployment.to_string())

us_dollar = ecbdata.get_series('EXR.D.USD.EUR.SP00.A',start='2024-10')
print(us_dollar.to_string())

gov_debt = ecbdata.get_series('GFS.Q.N.I9.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T',start='2024-10')
print(gov_debt.to_string())







