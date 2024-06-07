import yfinance as yf #dettaglio https://aroussi.com/post/python-yahoo-finance



#FUNZIONI COMPLETE
def getStockInfo(ticker):
  stock = yf.Ticker(ticker)
   #print(stock)
  #get all stock info
  info = stock.info
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
  #PRICE
  "prevClose": verifKey(info,'previousClose'),
  "currentPrice": verifKey(info,'currentPrice'),
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
  #TARGET
  "targetHighPrice": verifKey(info,'targetHighPrice'),
  "targetLowPrice": verifKey(info,'targetLowPrice'),
  "targetMeanPrice": verifKey(info,'targetMeanPrice'),
  "recommendationMean": verifKey(info,'recommendationMean'),
  "recommendationKey": verifKey(info,'recommendationKey'),
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



#FUNZIONI AGGIUNTIVE

def verifKey(dict,val):
  if val in dict:
    return dict[val] 
  else:
    return '0'

#print(getStockInfo('3V64.DE'))
#print(dividends('3V64.DE'))

#teststock = yf.Ticker('EPRA.MI')
  #get all stock info
#testinfo = teststock.info
#print(testinfo)

#test2 = yf.download('FOO.DE','2024-05-11','2024-05-23',progress=False)
#print(test2)
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
