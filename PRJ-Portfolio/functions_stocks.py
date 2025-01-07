import yfinance as yf #dettaglio https://aroussi.com/post/python-yahoo-finance
import datetime
from datetime import datetime,timedelta
from settings import * #importa variabili globali
from functions_sheets import read_range

#yfinance
def testReadDataYf(tick):
  ticker = yf.Ticker(tick)
  #analysisData = ticker.get_analysis()
  print('get_calendar()')
  FutureDates = ticker.get_calendar()
  print(FutureDates)
  print('get_actions()')
  DividensSplit = ticker.get_actions()
  print(DividensSplit)
  print('get_news()')
  News = ticker.get_news()
  print(News)
  print('get_recommendations()')
  reccomand = ticker.get_recommendations()
  print(reccomand)
  print('get_balance_sheet()')
  balance_sheet = ticker.get_balance_sheet()
  print(balance_sheet)
  print('get_cashflow()')
  cashflow = ticker.get_cashflow()
  print(cashflow)
  print('get_info()')
  info = ticker.get_info()
  print(info)
  print('get_institutional_holders()')
  institutional_holders = ticker.get_institutional_holders()
  print(institutional_holders)
  print('dati storici')
  todayCon = datetime.today().strftime('%Y-%m-%d')
  dataInizio = (datetime.strptime(todayCon, '%Y-%m-%d')+timedelta(days=-20)).strftime('%Y-%m-%d')
  print(f"data inizio {dataInizio} e data fine {todayCon}")
  prices = yf.download(tick,dataInizio,todayCon,progress=False)  
  print(prices)
  #analisi non mi va..
  print('get_analysis()')
  analysis = ticker.get_analysis()
  print(analysis)
  return 'ok0'

#def getcurrencyEtc(tick,price):
  #cerco currency
  #ticker = yf.Ticker(tick)
  #info = ticker.get_info()
  #currency=info['currency']
  #prendo il cambio
  #if(currency == 'CHF'):
  #elif(currency == 'GBP'):
  #else:
  #'EURCHF=X'
  #calcolo il prezzo
  #if currency == 'EUR':
    #priceConv = price
  #else:

  #print(currency)
  #return currency

#print(getcurrencyEtc('BITC.SW',52))
#print(testReadDataYf('EURCHF=X'))


#FUNZIONI COMPLETE
def getStockInfo(ticker):
  stock = yf.Ticker(ticker)
  #print(stock)
  #get all stock info
  info = stock.info
  #print(info)
  #Creo dizionario filtrato
  qType = verifKey(info,'quoteType')
  if qType == "CRYPTOCURRENCY" : qType = "CRYPTO"
  stockInfo = {
  #GENERIC
  "quoteType": qType,
  "country": verifKey(info,'country'),
  "sector": verifKey(info,'sector'),
  "industry": verifKey(info,'industry'),
  "shortName": verifKey(info,'shortName'),
  "longName": verifKey(info,'longName'),
  "currency": verifKey(info,'currency'),
  #INDICATORI
  "beta": verifKey(info,'beta'),
  "trailingPE": verifKey(info,'trailingPE'),
  "forwardPE":   verifKey(info,'forwardPE'),
  "priceToSalesTrailing12Months": verifKey(info,'priceToSalesTrailing12Months'),
  "bookValue": verifKey(info,'bookValue'),
  "priceToBook": verifKey(info,'priceToBook'),
  "trailingEps": verifKey(info,'trailingEps'),
  "forwardEps": verifKey(info,'forwardEps'),
  "pegRatio": verifKey(info,'pegRatio'),
  "trailingPegRatio": verifKey(info,'trailingPegRatio'),
  #PRICE
  "previousClose": verifKey(info,'previousClose'),
  "currentPrice": verifKey(info,'currentPrice'),
  "bid": verifKey(info,'bid'),
  "open": verifKey(info,'regularMarketOpen'),
  #DIVIDEND
  "dividRate": verifKey(info,'dividRate'),
  "dividYield": verifKey(info,'dividYield'),
  "lastDividendValue": verifKey(info,'lastDividendValue'),
  "lastDividendDate": verifKey(info,'lastDividendDate'),
  "exdividDate": verifKey(info,'exdividDate'),
  "payoutratio": verifKey(info,'payoutratio'),
  #ANDAM PREZZO
  "fiftyTwoWeekLow": verifKey(info,'fiftyTwoWeekLow'),
  "fiftyTwoWeekHigh": verifKey(info,'fiftyTwoWeekHigh'),
  "fiftyDayAverage": verifKey(info,'fiftyDayAverage'),
  "52WeekChange": verifKey(info,'52WeekChange'),
  "twoHundredDayAverage": verifKey(info,'twoHundredDayAverage'),
  #FINANCIALS
  "ebitda": verifKey(info,'ebitda'),
  "freeCashflow": verifKey(info,'freeCashflow'),
  "operatingCashflow": verifKey(info,'operatingCashflow'),
  "enterpriseValue": verifKey(info,'enterpriseValue'),
  "profitMargins": verifKey(info,'profitMargins'),
  "grossMargins": verifKey(info,'grossMargins'),
  "ebitdaMargins": verifKey(info,'ebitdaMargins'),
  "totalCashPerShare": verifKey(info,'totalCashPerShare'),
  "revenuePerShare": verifKey(info,'revenuePerShare'),
  "debtToEquity": verifKey(info,'debtToEquity'),
  "returnOnAssets": verifKey(info,'returnOnAssets'),
  "returnOnEquity": verifKey(info,'returnOnEquity'),
  "earningsGrowth": verifKey(info,'earningsGrowth'),
  "revenueGrowth": verifKey(info,'revenueGrowth'),
  "enterpriseToRevenue": verifKey(info,'enterpriseToRevenue'),
  "enterpriseToEbitda": verifKey(info,'enterpriseToEbitda'),
  "earningsQuarterlyGrowth": verifKey(info,'earningsQuarterlyGrowth'),
  "quickRatio": verifKey(info,'quickRatio'),
  "currentRatio": verifKey(info,'currentRatio'),
  #TARGET
  "targetHighPrice": verifKey(info,'targetHighPrice'),
  "targetLowPrice": verifKey(info,'targetLowPrice'),
  "targetMeanPrice": verifKey(info,'targetMeanPrice'),
  "targetMedianPrice": verifKey(info,'targetMedianPrice'),
  "recommendationMean": verifKey(info,'recommendationMean'),
  "recommendationKey": verifKey(info,'recommendationKey'),
  "marketCap": verifKey(info,'marketCap'),
  "numberOfAnalystOpinions": verifKey(info,'numberOfAnalystOpinions')
  }
  return stockInfo

def histData(ticker,periodo):
  stock = yf.Ticker(ticker)
  return stock.history(period=periodo)

def raccomand(ticker):
  stock = yf.Ticker(ticker)
  return stock.upgrades_downgrades

def earnings(ticker):
  stock = yf.Ticker(ticker)
  return stock.earnings_dates

def news(ticker):
  stock = yf.Ticker(ticker)
  return stock.news

def dividends(ticker):
  stock = yf.Ticker(ticker)
  return stock.get_dividends()

#TROVO RIGA ESATTA SU FOGLIO ANALSI SPESE..
def findRowSpes():
  #capisco in che anno siamo
  currYear = datetime.today().strftime('%Y')
  #leggo il file dell'analisi spese
  allRows = read_range('Tabella!F:G',spese)
  allRows = allRows[allRows['Anno'] == currYear]
  #print(allRows.index[0])
  riga = int(allRows.index[1])
  #print(type(riga))
  return riga
#print(findRowSpes())

#FUNZIONI AGGIUNTIVE

def verifKey(dict,val):
  if val in dict:
    return dict[val] 
  else:
    return '0'

#print(getStockInfo('21BC.DE'))
#print(getStockInfo('^VIX'))
#g = getStockInfo('^VIX')
#print(g['previousClose'])

#print(getStockInfo('^VIX1D'))
#print(getStockInfo('3V64.DE'))
#print(dividends('3V64.DE'))

#teststock = yf.Ticker('EPRA.MI')
  #get all stock info
#testinfo = teststock.info
#print(testinfo)

#test2 = yf.download('RCPL.XC','2020-01-01','2024-10-14',progress=False)
#print(test2)
#test3 = yf.download('RCP.L','2000-01-01','2024-10-14',progress=False)
#print(test3)
#test3 = test2.asfreq('D')
#print(test3)
#test4 = test3.fillna(method='ffill')
#print(test4)
#print(test4.head())
#print(test4.keys())

#print(fillDatesDFrame(test2))
#print(test2['Close'].iloc[0])
#stock = yf.Ticker('FOO.DE')
#test3 = yf.download('FOO.DE','2024-05-18','2024-05-23',progress=False)
#print(stock.history(period="1mo"))
#print(test2['Close'].iloc[0])

# Stampa le percentuali di settore
#print(teststock.sectorPercentage)

#spy = yf.Ticker("SPY")

# Stampa le percentuali di settore
#print(spy.sectorPercentage)

#import pandas_datareader as pdr

# Ottieni i dati sull'ETF SPY
#data = pdr.DataReader("SPY", data_source="yahoo")
#print(data)
# Stampa le percentuali di settore
#print(data["Sector"].value_counts(normalize=True))