#uso libreria  yahooquery perchè dovrebbe avere tutti i settori
#guida qui https://yahooquery.dpguthrie.com
#https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_sector_weightings

from yahooquery import Ticker
from functions_stocks import verifKey
import pandas as pd
import datetime
from datetime import datetime,timedelta
import time
#test nuova funzione
from functions_sheets import read_range,appendRow
from settings import * #importa variabili globali
import calendar

def getPriceETF(ticker):
  todayDate = datetime.today().strftime('%d/%m/%Y')
  fund = Ticker(ticker)
  livePriceDf = fund.history(period="1d")
  #print(f"lunghezza {len(livePriceDf)}")
  if(len(livePriceDf) > 0):
    livePrice = livePriceDf.iloc[0][3] #uso prezzo cloe e non close adjusted
    datePrice = livePriceDf.index[0][1]
    curre = fund.quotes[ticker]['currency']
    price1d = fund.quotes[ticker]['regularMarketPreviousClose']
    output=[ticker, livePrice,datePrice,curre,price1d]
  else:
    output=[ticker, 0, todayDate, 'EUR', 0]
  return output

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
 
#df3 = getSummary('5Q5.DE')
#print(f" Settore: {df3['assetProfile']['sector']}")
#print(f" Industria: {df3['assetProfile']['industry']}")
#print(f" MarketCap: {df3['summaryDetail']['marketCap']}")
#df = sectorsEtf('EMBE.MI')
#df1 = sectorsEtf('LCWD.MI')
#df1 = getPriceETF('GLUX.MI')
#print(df.keys())
#print(df.index)
#print(df)
#print(df3)
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


#PERFORMANCE
#fase 1 leggere che giorno che mese e che anno siamo
#leggere l'esistente sul nuovo foglio e capire a che mese siamo
#estrarre i dati da calendar totali

#prendo i dati da calendar totali filtrando mese e anno di interesse
#di questo df prtendo solo prima e ultima riga

def diff_month(d1, d2):  
  #quindi (anno d1 - anno d2)*12+mesi d1-mesi d2
  return (int(datetime.strptime(d1, '%d/%m/%Y').strftime('%Y')) - int(datetime.strptime(d2, '%d/%m/%Y').strftime('%Y'))) * 12 + int(datetime.strptime(d1, '%d/%m/%Y').strftime('%m')) - int(datetime.strptime(d2, '%d/%m/%Y').strftime('%m'))

def first():
  todayDate = datetime.today().strftime('%d/%m/%Y')
  todayMonth = datetime.today().strftime('%m')
  todayYear = datetime.today().strftime('%Y')
  print(f"Mese corrente {todayMonth} e anno corrente {todayYear}")
  #READ ACTUAL
  actualPerf = read_range('tab_performance!A:L',newPrj)

 #ultimo anno 
  lastYear = actualPerf['Anno'].iloc[-1]
  lastMonth = actualPerf['Mese'].iloc[-1]
  lastDatelastday = actualPerf['Last day month'].iloc[-1]
  #calcolo ultima data
  lastDate = datetime(int(lastYear), int(lastMonth), 1).strftime('%d/%m/%Y')
  deltaMonth = diff_month(todayDate,lastDate)
  print(f"Ultima data del foglio è mese: {lastMonth} dell'anno: {lastYear} quindi siamo {lastDate}, mentre oggi {todayDate} quindi differenza mesi è {diff_month(todayDate,lastDate)}")
  if(deltaMonth >= 1):
    i=1
    while i <= deltaMonth:
      #leggo ultimo giorno del mese dal foglio
      newYear = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=1)).strftime('%Y')
      newMonth = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=1)).strftime('%m')
      firstDayMon = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=1)).strftime('%d/%m/%Y')
      numdaysNewMonth = calendar.monthrange(int(newYear), int(newMonth))[1]
      lastDayMon = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=numdaysNewMonth)).strftime('%d/%m/%Y')
      print(f"primo del mese {firstDayMon} ultimo del mese {lastDayMon}")


      ####################INSERIRE I DATI#############################


      #preparo array
      arr = [[newYear,newMonth,firstDayMon,lastDayMon]]
      #scrivo array
      appendRow('tab_performance!A:D',arr,newPrj)
      #aggiorno l'ultima data 
      lastDatelastday = lastDayMon
      #proseguo con il loop
      i += 1
  else:
    print("Aggiornamento non necessario")
  return 'Done'

  #if lastYear <= todayYear:
   #if lastMonth <=todayMonth:
      #inizio i calcoli
      #if lastMonth == 12:
        #diffMonth = 12 - todayMonth
      #else:
        #diffMonth = todayMonth-lastMonth
      #for loop
      #i=0 
      #while i < diffMonth:
        #########################
        #fulldata = read_range('tab_caltot!A:I',newPrj)
        #monthtoWrite=lastMonth+1+i
        #arr = [[test1, test2]]
        #appendRow('tab_tabperformance!A:B',arr,newPrj)
        #devo prendere tutti i dati dal primo del mese che manca fino ad oggi
        
        #datafiltr = fulldata[fulldata['Data'] <= date] 
      #i += 1

  #else:
    #print("Aggiornamento non necessario")



#print(first())
