import os

# get the current working directory
#current_working_directory = os.getcwd()
# print output to the console
#print(current_working_directory)

from classes import Portfolio,caldRendimento
from functions_stocks import getStockInfo
from functions_stocks import histData
from datetime import datetime
import yfinance as yf
from functions_sheets import read_range,appendRow
from functions_etf import readHoldings,testapiFinnhub
from settings import * #importa variabili globali
from manage_logs import log_insert,log_insert1
import pytz
import time
from yahooquery import Ticker
from yahooread import readYahooSite
#from get_all_tickers import get_tickers as gt

### INIZIO PROCEDURA
port = Portfolio()
#variabile per non eseguire tutto il codice..
developerMode=1
if developerMode == 0:
  #scrivo la tabella degli Isin
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 1 - Inizio - Aggiornamento Tab Isin")
  log_insert1("Aggiornamento Tab Isin","Inizio","")
  time1s = time.time()
  print(port.writeAllIsins())
  delta1 = time.time() - time1s
  log_insert1("Aggiornamento Tab Isin","Fine",delta1)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 1 - Fine - Aggiornamento Tab Isin")
  #Crea la tabella del portafoglio
  time.sleep(5) #aspetto tempo perchè la tabella sopra sia scritta
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2 - Inizio - Aggiornamento Portafoglio")
  log_insert1("Aggiornamento Tab Portafoglio","Inizio","")
  time2s = time.time()
  print(port.writePortfolio())
  delta2 = time.time() - time2s
  log_insert1("Aggiornamento Tab Portafoglio","Fine",delta2)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2 - Fine - Aggiornamento Portafoglio")
  #creo calendar
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 3 - Inizio - Aggiornamento Calendar")
  log_insert1("Aggiornamento Tab Calendar","Inizio","")
  time3s = time.time()
  print(port.updateCalendarTab())
  delta3 = time.time() - time3s
  log_insert1("Aggiornamento Tab Calendar","Fine",delta3)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 3 - Fine - Aggiornamento Calendar")
  #aggiorno rendimento
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 4 - Inizio - Aggiornamento Rendimento")
  log_insert1("Aggiornamento Tab Rendimento","Inizio","")
  time4s = time.time()
  print(caldRendimento())
  delta4 = time.time() - time4s
  log_insert1("Aggiornamento Tab Rendimento","Fine",delta4)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 4 - Fine - Aggiornamento Rendimento")
  #aggiorno andamento
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 5 - Inizio - Aggiornamento Andamento")
  log_insert1("Aggiornamento Tab Andamento","Inizio","")
  time5s = time.time()
  print(port.calcAndamPort())
  delta5 = time.time() - time5s
  log_insert1("Aggiornamento Tab Andamento","Fine",delta5)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 5 - Fine - Aggiornamento Andamento")
  #aggiorno watchlist
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 6 - Inizio - Aggiornamento Watchlist")
  log_insert1("Aggiornamento Tab Watchlist","Inizio","")
  time6s = time.time()
  print(port.whatchlist())
  delta6 = time.time() - time6s
  log_insert1("Aggiornamento Tab Watchlist","Fine",delta6)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 6 - Fine - Aggiornamento Watchlist")
else:
  #print(f"esempio {datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')}")
  #print(port.portCompanies())
  #print(readHoldings())
  print(port.whatchlist())

  #print(port.getPriceYah('GB00BLD4ZL17.SG'))
  #print(port.getPriceYah('RACE.MI'))



  #print(port.newsStocks())

  #print(testapiFinnhub())
  #print(add_rows(newPrj,2,'566804442'))
  #appendRow('tab_1!A:A',[['1']],newPrj)
  #write_range('tab_1!A2:A10',tabellaPrint,newPrj)
#transact = read_range('tab_transazioni!A:P',newPrj,'566804442')

#tabCalTot=read_range('tab_caltot!A:A',newPrj)
#test1 = appendRow('tab_caltot!A:B',[['2','3']],newPrj)
#rowToWr = len(tabCalTot)
#print(tabCalTot)
#print(len(tabCalTot))

#test1=port.readActiveIsinByDate('2024-01-01')
#test2=port.readActiveIsinByDate('2024-01-02')
#print(test1[test1['ISIN'] == 'US7134481081'])
#print(test2[test2['ISIN'] == 'US7134481081'])


#tabella trabsazioni filtrata come dataframe
#print(port.readActiveIsin())
#print(port.readActiveIsin()['ISIN'])

#print(port.calcDataPort('IT0003828271'))
#print(port.calcDataPort00())
#print(port.readListIsin())
#Scrivo la tabella tab_isin
#print(port.writeAllIsins())
#print(port.gtDataFromTabIsin('US29355A1079'))

#PREZZI
#test1 = getStockInfo('RACE.MI')
#price = test1['currentPrice']
#price1d = test1['prevClose']
#print(f"Per Ferrari il prezzo live è {price} mentre rpezzo chiusura ieri {price1d}")

#test2 = histData('RACE.MI','1do')
#print(test2)
#test2 = histData('RACE.MI','1mo')
#print(test2.index)
#print(test2.iloc[-1])#prezzo di oggi leggendo l'ulitma riga del dataframe
#test3 = histData('RACE.MI','1mo')

#questa funzione ritorna solo i dati da ieri e indietro
#data32 = yf.download('RACE.MI','2024-05-07','2024-05-08')
#print(data32)
#print(test2['2024-05-07 00:00:00+02:00'])
#print(test2.keys())
#print(test2[test2['Close']>=datetime.strptime('06/05/2024','%d/%m/%Y')])
#print(test2[test2['Date'] >=datetime.strptime('06/05/2024','%d/%m/%Y')])


#datetime.strptime(date_string, format)


#priceH = test1['currentPrice']
#price1dH = test1['prevClose']
#print(f"Per Ferrari il prezzo live è {priceH} mentre rpezzo chiusura ieri {price1dH}")



##########TODO
#Ora bisogna:
#creare lista per portafoglio
#-isin singoli
#-gestione titolo del ticker -> cerco su tab_isin e se non c'è chiamo
#-gestione qta acq /vend, prezzi medi

#funzione che 
#opzione 1 creo tabella isin e li metot il nome che poi copio insiem al ticker 


##################Prezzi storici e live
#AZIONI ed ETF

#CASO 1 - live
#test1 = getStockInfo('RACE.MI')
#price = test1['currentPrice']
#price1d = test1['prevClose']

#CASO 2 - passo nuemro days
#test2 = histData('RACE.MI','1do')
#print(test2)
#test2 = histData('RACE.MI','1mo')
#print(test2.index)
#print(test2.iloc[-1])#prezzo di oggi leggendo l'ulitma riga del dataframe
#test3 = histData('RACE.MI','1mo')

#CASO 3 - passo range di date
#questa funzione ritorna solo i dati da ieri e indietro
#data32 = yf.download('RACE.MI','2024-05-07','2024-05-08')
#print(data32)
#print(test2['2024-05-07 00:00:00+02:00'])
#print(test2.keys())
#print(test2[test2['Close']>=datetime.strptime('06/05/2024','%d/%m/%Y')])
#print(test2[test2['Date'] >=datetime.strptime('06/05/2024','%d/%m/%Y')])



#BTP
#uso getBtpData che legge da 
#URL = "https://www.simpletoolsforinvestors.eu/monitor_info.php?monitor=italia&yieldtype=G&timescale=DUR" 
#su qeusto sito però non ho i prezzi storici, solo grafici
#provo ad usare pip install investpy che legge da investing
#documentazione https://investpy.readthedocs.io/_info/installation.html

  ##############TEST delle due API
  #ticker='XDEW.DE'
  #print("Prova Yahoo Finance")
  #stock = yf.Ticker(ticker)
  #info = stock.info
  #print(info)
  #print(f"Prezzo Yahoo Finance {info['currentPrice']}")
  #print("Prova Yahooquery")
  #fund = Ticker(ticker)
  #info2 = fund.history(period="1d")
  #print(info2)
  #print(f"Prezzo Yahooquery {info2['close'].iloc[0]}")



