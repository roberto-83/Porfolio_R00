import os

# get the current working directory
current_working_directory = os.getcwd()
# print output to the console
print(current_working_directory)

from classes import Portfolio,caldRendimento
from functions_stocks import getStockInfo
from functions_stocks import histData
from datetime import datetime
import yfinance as yf
from functions_sheets import read_range,appendRow
from settings import * #importa variabili globali
from manage_logs import log_insert
import pytz
from yahooquery import Ticker
#from get_all_tickers import get_tickers as gt

### INIZIO PROCEDURA
port = Portfolio()
#variabile per non eseguire tutto il codice..
developerMode=0
if developerMode == 0:
  #scrivo la tabella degli Isin
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 1 - Inizio - Aggiornamento Tab Isin")
  log_insert("Aggiornamento Tab Isin","Inizio")
  print(port.writeAllIsins())
  log_insert("Aggiornamento Tab Isin","Fine")
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 1 - Fine - Aggiornamento Tab Isin")
  #Crea la tabella del portafoglio
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2 - Inizio - Aggiornamento Portafoglio")
  log_insert("Aggiornamento Tab Portafoglio","Inizio")
  print(port.writePortfolio())
  log_insert("Aggiornamento Tab Portafoglio","Fine")
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2 - Fine - Aggiornamento Portafoglio")
  #creo calendar
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 3 - Inizio - Aggiornamento Calendar")
  log_insert("Aggiornamento Tab Calendar","Inizio")
  print(port.updateCalendarTab())
  log_insert("Aggiornamento Tab Calendar","Fine")
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 3 - Fine - Aggiornamento Calendar")
  #aggiorno rendimento
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 4 - Inizio - Aggiornamento Rendimento")
  log_insert("Aggiornamento Tab Rendimento","Inizio")
  print(caldRendimento())
  log_insert("Aggiornamento Tab Rendimento","Fine")
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 4 - Fine - Aggiornamento Rendimento")
  #aggiorno andamento
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 5 - Inizio - Aggiornamento Andamento")
  log_insert("Aggiornamento Tab Andamento","Inizio")
  print(port.calcAndamPort())
  log_insert("Aggiornamento Tab Andamento","Fine")
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 5 - Fine - Aggiornamento Andamento")
else:
  print(f"esempio {datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')}")
  print(port.portCompanies())


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
