import os

# get the current working directory
#current_working_directory = os.getcwd()
# print output to the console
#print(current_working_directory)

from classes import Portfolio,caldRendimento,get_chrome_version,get_chromedriver_version
from functions_stocks import getStockInfo
from functions_stocks import histData
from datetime import datetime
from analisiPort import analisiPort,gcolabAnalysis,finalAnalysys,readMyPort
import yfinance as yf
from functions_sheets import read_range,appendRow,delete_range
from functions_etf import readHoldings,testapiFinnhub
from settings import * #importa variabili globali
from manage_logs import log_insert,log_insert1
import pytz
import time
from yahooquery import Ticker
from yahooread import readYahooSite
from fred_data import writeMacroData,writeMacroDataHistory
from investing_read import write_economin_data
from read_operative_trading import all_stocks
#from get_all_tickers import get_tickers as gt

#variabile per non eseguire tutto il codice..
developerMode=0
if developerMode == 0:
  print('Sono in modalità Normale')
  # Ottieni e stampa le versioni
  #chrome_version = get_chrome_version()
  #chromedriver_version = get_chromedriver_version()
  #print(f"Versione di Chrome: {chrome_version}")
  #print(f"Versione di ChromeDriver: {chromedriver_version}")
  port = Portfolio('1')
  port2 = Portfolio('2')
  port3 = Portfolio('3')
  #scrivo il dato sul file analisi spese
  print(port.bankING)
  print(port.totUsci)
  #scrivo la tabella degli Isin
  #print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 1 - Inizio - Aggiornamento Tab Isin")
  #log_insert1("Aggiornamento Tab Isin","Inizio","")
  #time1s = time.time()
  #print(port.writeAllIsins())
  #delta1 = time.time() - time1s
  #log_insert1("Aggiornamento Tab Isin","Fine",delta1)
  #print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 1 - Fine - Aggiornamento Tab Isin")
  #Crea la tabella del portafoglio
  #time.sleep(5) #aspetto tempo perchè la tabella sopra sia scritta
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2_a - Inizio - Aggiornamento Portafoglio 1")
  #log_insert1("Aggiornamento Tab Portafoglio","Inizio","","")
  time2s = time.time()
  initialTime=time2s   #START
  print(port.writePortfolio())
  delta2 = time.time() - time2s
  log_insert1("Aggiornamento Tab Portafoglio 1","Fine",delta2,initialTime)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2_a - Fine - Aggiornamento Portafoglio 1")

  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2_b - Inizio - Aggiornamento Portafoglio 2")
  #log_insert1("Aggiornamento Tab Portafoglio","Inizio","","")
  time2s_b = time.time()
  #initialTime=time2s   #START
  print(port2.writePortfolio())
  delta2_b = time.time() - time2s_b
  log_insert1("Aggiornamento Tab Portafoglio 2","Fine",delta2_b,initialTime)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2_b - Fine - Aggiornamento Portafoglio 2")

  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2_c - Inizio - Aggiornamento Portafoglio 3")
  #log_insert1("Aggiornamento Tab Portafoglio","Inizio","","")
  time2s_c = time.time()
  #initialTime=time2s   #START
  print(port3.writePortfolio())
  delta2_c = time.time() - time2s_c
  log_insert1("Aggiornamento Tab Portafoglio 3","Fine",delta2_c,initialTime)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 2_c - Fine - Aggiornamento Portafoglio 3")

  #creo calendar
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 3 - Inizio - Aggiornamento Calendar")
  #log_insert1("Aggiornamento Tab Calendar","Inizio","","")
  time3s = time.time()
  clTab = port.updateCalendarTab()
  print(clTab)
  delta3 = time.time() - time3s
  log_insert1("Aggiornamento Tab Calendar","Fine",delta3,initialTime,clTab)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 3 - Fine - Aggiornamento Calendar")
  #aggiorno rendimento
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 4 - Inizio - Aggiornamento Rendimento")
  #log_insert1("Aggiornamento Tab Rendimento","Inizio","","")
  time4s = time.time()
  cal_rend = caldRendimento()
  print(cal_rend)
  delta4 = time.time() - time4s
  log_insert1("Aggiornamento Tab Rendimento","Fine",delta4,initialTime,cal_rend)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 4 - Fine - Aggiornamento Rendimento")
  #aggiorno andamento
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 5 - Inizio - Aggiornamento Andamento")
  #log_insert1("Aggiornamento Tab Andamento","Inizio","","")
  time5s = time.time()
  port_and =port.calcAndamPort()
  print(port_and)
  delta5 = time.time() - time5s
  log_insert1("Aggiornamento Tab Andamento","Fine",delta5,initialTime,port_and)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 5 - Fine - Aggiornamento Andamento")
  #old watchlist

  #aggiorno settori
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 7 - Inizio - Aggiornamento Settori")
  #log_insert1("Aggiornamento Tab Settori","Inizio","","")
  time7s = time.time()
  port_set=port.portafSettori()
  print(port_set)
  delta7 = time.time() - time7s
  log_insert1("Aggiornamento Tab Settori","Fine",delta7,initialTime,port_set)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 7 - Fine - Aggiornamento Settori")
  #aggiorno paesi
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 8 - Inizio - Aggiornamento Paesi")
  #log_insert1("Aggiornamento Tab Paesi","Inizio","","")
  time8s = time.time()
  port_pae = port.portafPaesi()
  print(port_pae)
  delta8 = time.time() - time8s
  log_insert1("Aggiornamento Tab Paesi","Fine",delta8,initialTime,port_pae)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 8 - Fine - Aggiornamento Paesi")
  #analisi portafoglio
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 9 - Inizio - Analisi Portafoglio")
  #log_insert1("Analisi Portafoglio","Inizio","","")
  time9s = time.time()
  print(finalAnalysys('2010-01-01','1'))
  delta9 = time.time() - time9s
  log_insert1("Analisi Portafoglio","Fine",delta9,initialTime)
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 9 - Fine -  Analisi Portafoglio")
  #aggiorno watchlist
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 6 - Inizio - Aggiornamento Watchlist")
  #log_insert1("Aggiornamento Tab Watchlist","Inizio","","")
  time6s = time.time()
  print(port.whatchlist())
  delta6 = time.time() - time6s
  log_insert1("Aggiornamento Tab Watchlist","Fine",delta6,initialTime) 
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 6 - Fine - Aggiornamento Watchlist")

  #dati "operative trading"
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 10 - Inizio - Dati Operative Trading")
  time10s = time.time()
  #print(writeMacroDataHistory())
  output_econ = all_stocks()
  #print(write_economin_data())
  delta10 = time.time() - time10s
  log_insert1("Aggiornamento Tab Oper Trading","Fine",delta10,initialTime,output_econ) 
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 10 - Fine - Dati Operative Trading")

  #dati fed
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 11 - Inizio - Dati Economici")
  time11s = time.time()
  #print(writeMacroDataHistory())
  output_econ = write_economin_data()
  #print(write_economin_data())
  delta11 = time.time() - time11s
  log_insert1("Aggiornamento Tab Macro","Fine",delta11,initialTime,output_econ) 
  print(f"{datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')} FASE 11 - Fine - Dati Economici")
else:
  print('Sono in modalità Developer')
  #VOGLIO LE LISTE DA PASSARE A GOOGLE COLB PER ANALISI
  #print(gcolabAnalysis())
  #print(analisiPort('2010-01-01','1'))
  #day_of_week0 = datetime.today().weekday()
  #0 lunedi 1 martedi 2 mercoledi 3 giovedi 4 venerdi 5 sabato 6 domenica
  #print(day_of_week0)
  #port = Portfolio('1')
  #print(analisiPort2('2010-01-01','1'))
  #print('##########################')
  #print(port.bankING)
  #print(port.totUsci)
  #print(port.portafSettori())
  #print(port.writePortfolio())
  #appendRow('tab_performance!A:L',arr,newPrj)
  #delete_range('tab_performance!A63:L63',newPrj)
  #print(port.portafSettori())
   #print(port.whatchlist())
  #print(f"esempio {datetime.now(pytz.timezone('Europe/Rome')).strftime('%d/%m/%Y %H:%M:%S')}")
  #print(port.portCompanies())
  #print(readHoldings())
  #print(port.portafPaesi())
  #print(port.whatchlist())

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


#SITI UTILI
#sito che ha una lista di librerie per python legate all afinanza https://wilsonfreitas.github.io/awesome-quant/
#calcolo valore intrinseco https://github.com/akashaero/Intrinsic-Value-Calculator
#video per dashboard



#STOCK LIST
 #https://eoddata.com/stocklist/LSE.htm
 #su file excel https://investexcel.net/all-yahoo-finance-stock-tickers/

#https://public.acho.io/embed/9bffe75f11a5a99349359c98c74b9b0ba41cf563b351ffbb7ecc19614706f827861e5171a35b6f8296aa1d43a7558cfb978ae74ac969094d1c991bf7d8c8ca9f
