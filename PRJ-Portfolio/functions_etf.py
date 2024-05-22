#uso libreria  yahooquery perchè dovrebbe avere tutti i settori
#guida qui https://yahooquery.dpguthrie.com
#https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_sector_weightings

from yahooquery import Ticker
from functions_stocks import verifKey
import pandas as pd

def getPriceETF(ticker):
  fund = Ticker(ticker)
  livePriceDf = fund.history(period="1d")
  #print(livePriceDf)
  livePrice = livePriceDf.iloc[0][3] #uso prezzo cloe e non close adjusted
  datePrice = livePriceDf.index[0][1]
  curre = fund.quotes[ticker]['currency']
  price1d = fund.quotes[ticker]['regularMarketPreviousClose']
  return [ticker, livePrice,datePrice,curre,price1d]

def getSummary(ticker):
  fund = Ticker(ticker)
  #datas = fund.quotes[ticker]
  #asset_prof = fund.asset_profile[ticker]
  #calendar = fund.calendar_events[ticker]
  #summary_detail = fund.summary_detail[ticker]
  all_modules = fund.all_modules[ticker]
  return all_modules

def sectorsEtf(ticker):
  #lista di settori di un etf
  fund = Ticker(ticker)
  try:
    fund_df = fund.fund_sector_weightings
    fund_df_desc = fund_df.sort_values(by=ticker, ascending=False)
    return fund_df_desc
  except:
    #return  pd.DataFrame() #dataframe vuoto
    return  pd.DataFrame({ticker:'0'},index=['0']) #dataframe vuoto
 
#df3 = getSummary('RACE.MI')
#print(f" Settore: {df3['assetProfile']['sector']}")
#print(f" Industria: {df3['assetProfile']['industry']}")
#print(f" MarketCap: {df3['summaryDetail']['marketCap']}")
#df = sectorsEtf('EMBE.MI')
#df1 = sectorsEtf('LCWD.MI')
#df1 = getPriceETF('LCWD.MI')
#print(df.keys())
#print(df.index)
#print(df)
#print(df1)
#percentuale
#print(df['XDWS.MI'].iloc[0])
#print(df.index[0])
#dfList = df.values.tolist()
#print(dfList)


#print(type(sectorsEtf('GLUX.MI')))
#print(sectorsEtf('GLUX.MI').keys())
#chiavi sono il ticker e "Name" per il nome del settore
#estraggo la prima percentuale
#print(sectorsEtf('GLUX.MI')['GLUX.MI'].iloc[0])
#print(sectorsEtf('GLUX.MI')['GLUX.MI'].iloc[1:1])
#estraggo il primo settore
#print(sectorsEtf('GLUX.MI')[0].iloc[0])

#print(sectorsEtf('GLUX.MI')['GLUX.MI'].head(1))

#Prendo n_esimo campo
#print(fund.fund_sector_weightings.iloc[0])
#print(fund.fund_sector_weightings.iloc[1])
#chiavi
#print(fund.fund_sector_weightings.keys())
