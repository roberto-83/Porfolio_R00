from pickle import PUT
from ssl import PEM_FOOTER
from functions_sheets import read_range
from functions_sheets import write_range
from functions_sheets import delete_range,appendRow
from functions_bonds import getBtpData
from functions_bonds import getBotData,readEuronext,readEuronextREV2
from functions_stocks import getStockInfo
from functions_stocks import verifKey,findRowSpes
from functions_etf import sectorsEtf,sectorsMultipEtf
from functions_etf import getPriceETF
from functions_etf import getSummary,listEtfCountries,listStocksCountries
from settings import * #importa variabili globali
from currency_converter import CurrencyConverter, currency_converter
import pandas as pd
import datetime
from datetime import datetime,timedelta
import time
import pytz
import numpy as np
import yfinance as yf
import calendar
from yahooquery import Ticker
from yahooread import readYahooSite

#from IPython.display import display

from yfinance.utils import empty_earnings_dates_df
pd.options.mode.chained_assignment = None #toglie errori quando sovrascrivo un dataframe
#import yfinance as yf

class Portfolio:
  todayDate = datetime.today().strftime('%d/%m/%Y')
  todayDate_f = datetime.today().strftime('%Y-%m-%d')
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")
  todayDateHourAm  = todDateTime0.strftime("%Y-%m-%d %H:%M:%S")

  #metodo costruttore
  def __init__(self,num_port):
    self.num_port = num_port #specifico il numero del portafolgio
    #tutte le transazioni fino ad oggi
    self.transact = Portfolio.readActiveIsinByDate(self,Portfolio.todayDate_f)
    self.bankING = Portfolio.readValueBanks(self,Portfolio.todayDate_f,'Ing')
    #prima parte portafoglio con gli isin validi ad oggi
    self.actPort = Portfolio.calcDataPortREV2(self, self.transact)
    self.tabIsin = Portfolio.gtDataFromTabIsinREV2(self)
    self.totUsci = Portfolio.countUsciteSpese(self,Portfolio.todayDate_f)
   

  def readActiveIsinByDate(self,date):
    num_port = self.num_port #numero portafoglio
    #Prendo gli isin attivi ad oggi, poi bisognerà ragionare sulla quantità
    transact = read_range('tab_transazioni!A:Q',newPrj)
    transact = transact[transact['Num Portfolio'] == num_port] #solo portafoglio passato
    transact['Data operazione'] = pd.to_datetime(transact['Data operazione'], format='%d/%m/%Y')
    #print(transact[transact['Ticker'] == 'CSNDX.MI'])
    #print(transact[transact['Ticker'] == 'NKE.DE'])
    transact = transact[transact['Data operazione'] <= date ]  
    #print(transact[transact['Ticker'] == 'CSNDX.MI'])
    #print(transact[transact['Ticker'] == 'NKE.DE'])
    transact = transact.drop(columns=['Stato Database','SCADENZA','Dividendi','VALUTA','Chiave','Data operazione','prezzo acquisto','Spesa/incasso previsto'])
    #transact = transact.drop(columns=['Stato Database','SCADENZA','Dividendi','VALUTA','Chiave','prezzo acquisto','Spesa/incasso previsto'])
    #tolgo il punto su spesa e incasso
    transact['Spesa/incasso effettivo'] = transact['Spesa/incasso effettivo'].replace(to_replace='\.',value='',regex=True)
    #tolgo il punto su qta
    transact['Quantità (real)'] = transact['Quantità (real)'].replace(to_replace='\.',value='',regex=True)
    transact = transact.replace(to_replace=',',value='.', regex=True)
    transact = transact.replace(to_replace='€',value='', regex=True)
    transact = transact.sort_values(by=['Asset'])
    #metto 0 al posto dei valori vuoti nella colonna quantità
    transact['Quantità (real)'] = transact['Quantità (real)'].replace('',0)

    return transact

  def readValueBanks(self,date,bank):##################TESTARE
    #num_port = self.num_port #numero portafoglio
    #Prendo gli isin attivi ad oggi, poi bisognerà ragionare sulla quantità
    transact = read_range('tab_transazioni!A:S',newPrj)
    transact = transact[transact['Banca'] == bank] #solo banca effettiva
    transact['Data operazione'] = pd.to_datetime(transact['Data operazione'], format='%d/%m/%Y')
    #print(transact[transact['Ticker'] == 'CSNDX.MI'])
    #print(transact[transact['Ticker'] == 'NKE.DE'])
    transact = transact[transact['Data operazione'] <= date ] 
    transact['Spesa/incasso effettivo'] = transact['Spesa/incasso effettivo'].replace(to_replace='\.',value='',regex=True)
    transact['Quantità (real)'] = transact['Quantità (real)'].replace(to_replace='\.',value='',regex=True)
    transact = transact.replace(to_replace=',',value='.', regex=True)
    transact = transact.replace(to_replace='€',value='', regex=True)
    transactAcq = transact[transact['Tipo'] == 'ACQ']
    transactVen = transact[transact['Tipo'] == 'VEND']
    totAcq=transactAcq['Spesa/incasso effettivo'].astype(float).sum()
    totVen=transactVen['Spesa/incasso effettivo'].astype(float).sum()
    #print(f"Acquisti per banca {totAcq}")
    #print(f"Acquisti per banca {totVen}")
    netValPortBanca=totAcq-totVen
    rowWrit=findRowSpes()
    #scrivo il valore sul file delle uscite/entrate
    write_range('Tabella!N'+str(rowWrit),[[netValPortBanca]],spese)

   
    return netValPortBanca
  
  def countUsciteSpese(self,date):
    year = date[0:4]
    transact = read_range('Tabella!A:I',spese)
    transact = transact[transact['Anno'] == year] 
    transact['Importo'] = transact['Importo'].replace(to_replace='\.',value='',regex=True)
    transact = transact.replace(to_replace=',',value='.', regex=True)
    transact = transact.replace(to_replace='€',value='', regex=True)
    transact_out = transact[transact['Importo'].astype(float) <0]
    #uscite = transact[transact['Entrate/Uscite'] == 'USCITE']
    totUscite1 = transact_out['Importo'].astype(float).sum()
    totUscite2= totUscite1 * -1
    totUscite = round(totUscite2,2)
    #ora scrivo il dato
    rowWrit=findRowSpes()
    write_range('Tabella!M'+str(rowWrit),[[totUscite]],spese)
    ######SOMMO LE ENTRATE
    transact_in = transact[transact['Importo'].astype(float) >=0]
    #uscite = transact[transact['Entrate/Uscite'] == 'USCITE']
    totEntrate1 = transact_in['Importo'].astype(float).sum()
    totEntrate = round(totEntrate1,2)
    write_range('Tabella!L'+str(rowWrit),[[totEntrate]],spese)
    ####SCRIVO FORMULA
    write_range('Tabella!P'+str(rowWrit),[['=M'+str(rowWrit)+'-(N'+str(rowWrit)+'-O'+str(rowWrit)+')']],spese)
    write_range('Tabella!Q'+str(rowWrit),[['=L'+str(rowWrit)+'-P'+str(rowWrit)]],spese)
    return 'ok'
################################################################################
##### TABELLA DATI LIVE PORTAFOGLIO
################################################################################

  def getLivePrice(row):
    print(f"Calcolo i prezzi live del ticker {row['Ticker']} e isin {row['Isin']}")
    #funzione che mi da il prezzo a mercato dei vari asset
    if row['Asset'] == 'P2P':
      liveprice = float(row['TotInvest'])+float(row['Divid'])
    elif row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      price=getBtpData(row['Isin'])
      liveprice = float(price['pric'])
    elif row['Asset'] == 'ETF-AZIONI' or row['Asset'] == 'ETC':
      price=getPriceETF(row['Ticker'])
      #print(price)
      liveprice=price[1]
    elif row['Asset'] == 'AZIONI':
      infoStock = getStockInfo(row['Ticker'])
      liveprice=infoStock['currentPrice']
    else:
      liveprice='0'
    #cambio valuta
    liveprice = Portfolio.calcCurren(liveprice,row['CURRENCY'])
    print(f"prezzo di {row['Ticker']} è {liveprice} e ha currency {row['CURRENCY']}")
    return liveprice

  def getCtvMerc(row):
    #funzione che mi calcola il controvalore a mercato
    if row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      ctvMer = (float(row['LivePrice']) * float(row['Qta']))/100
    else:
      ctvMer = float(row['LivePrice']) * float(row['Qta'])
    return ctvMer

  def getDelta(row):
    print(f"Leggo il prezzo di {row['Ticker']}, asset {row['Asset']}")
    if row['Asset'] == 'AZIONI':
      infoStock = getStockInfo(row['Ticker'])
      #price1d = infoStock['prevClose']
      price1d = infoStock['previousClose']
      price1d = Portfolio.calcCurren(price1d,row['CURRENCY'])
      delta = row['LivePrice'] - price1d
    elif row['Asset'] == 'ETF-AZIONI' or row['Asset'] == 'ETC':
      price=getPriceETF(row['Ticker'])
      price1d = price[4]
      price1d = Portfolio.calcCurren(price1d,row['CURRENCY'])
      delta = float(row['LivePrice'])- price1d
    else:
      delta = '0'
    return delta

   #METODI PRINCIPALI - tab_portafoglio
  def dFPortf(self):
    #qui voglio preparare la prima parte del DF che è il portafoglio senza i FINANZIARI!
    #Prendo dalla classe il primo DF
    orig_portIsinCalc = self.actPort
    #Prendo il tab_isin
    isins = self.tabIsin
    #unisco i due dataframe sopra
    portIsinCalc = orig_portIsinCalc.merge(isins, left_on='Isin',right_on='ISIN',how='left')
    #print(portIsinCalc.to_string())
    #cancello colonne che non mi servono 
    portIsinCalc = portIsinCalc.drop(columns=['COUNTRY','DESCRIZIONE BREVE','TICKER DATI','TICKER YAHOO','ISIN','ASSET','SITO UFFICIALE'])
    #aggiungo prezzo live
    portIsinCalc['LivePrice']=portIsinCalc.apply(Portfolio.getLivePrice,axis=1 )
    #aggiungo controvalore mercato
    portIsinCalc['CtvMercato']=portIsinCalc.apply(Portfolio.getCtvMerc,axis=1 )
    #calcolo composizione totale del portafoglio
    totCompo = sum(portIsinCalc['CtvMercato'])
    #aggiungo pL #pL = ctvMerc - part2[5] (sarebbe tot investito)
    portIsinCalc['pL'] = portIsinCalc['CtvMercato'] - portIsinCalc['TotInvest']
    #aggiungo ppL #ppL = (pL / part2[5])*100
    portIsinCalc['ppL'] = (portIsinCalc['pL'] / portIsinCalc['TotInvest'])*100
    #aggiungo peso #compo = (j[11]/totCompo) *100
    portIsinCalc['peso'] = (portIsinCalc['CtvMercato'] / totCompo)
    #duplico prezzo pond
    portIsinCalc['PrezzoPondEur'] = portIsinCalc['PrezzoPond']
    #duplico prezzo pond
    portIsinCalc['LivePriceEur'] = portIsinCalc['LivePrice']
    #aggiungo delta prezzo
    portIsinCalc['Delta']=portIsinCalc.apply(Portfolio.getDelta,axis=1 )
    #riordino
    portIsinCalc = portIsinCalc[['Asset','Isin','Ticker','DESCRIZIONE LUNGA','Qta','PrezzoPond','PrezzoPondEur','Divid','TotInvest',
    'LivePrice','LivePriceEur','CtvMercato','peso','pL','ppL','CURRENCY','Costi','SCADENZA','Delta','SETTORE','INDUSTRIA']]
    #print(portIsinCalc.to_string())
    return portIsinCalc

  def financialsPartPort(self):
    #prendo la prima parte già creata
    portaf = Portfolio.dFPortf(self)
    #print("stampo pre portafoglio")
    #print(portaf.head())
    #creo una lista con i dati finanziari
    list2d=[]
    for i in portaf['Isin']:
      #time.sleep(10) #provo ad aspettare per vedere se poi i dati finanziari sono piu completi
      tabIsinData = self.tabIsin
      #print(tabIsinData)
      #print(tabIsinData.keys())
      tabIsinData = tabIsinData[tabIsinData['ISIN'] == i]
      print(f"lunghezza del DF {len(tabIsinData)} per isin {i}")
      if len(tabIsinData) == 0: #caso in cui in tab_isin non c'è isin che mi serve
        list2d.append([i,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
      else:
        #print(tabIsinData.to_string())
        tick = tabIsinData['TICKER YAHOO'].iloc[0]
        #---------
        if(tabIsinData['ASSET'].iloc[0] == 'P2P' or tabIsinData['ASSET'].iloc[0] == 'ETF' or tabIsinData['ASSET'].iloc[0] == 'ETC'):
          list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        elif tabIsinData['ASSET'].iloc[0] == 'BTP' or tabIsinData['ASSET'].iloc[0] == 'BOT':
          dataBTP=getBtpData(i)
          datacedola = dataBTP['cedo']
          list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,datacedola,datacedola,0,0,0,0,0,0]) 
        else:
          #VAI COI FINANCIALS
          #print(tick)
          #try:
          infoStock = getSummary(tick)
          #infoStock2 = getStockInfo(tick)
          #sector = verifKey(infoStock['assetProfile'],'sector')
          #industry = verifKey(infoStock['assetProfile'],'industry')
          #print(f"Controllo se ci sono i dati {len(infoStock['summaryDetail'])}")
          try: marketCap = verifKey(infoStock['summaryDetail'],'marketCap')
          except: marketCap = 0
          try: volume = verifKey(infoStock['summaryDetail'],'volume') 
          except: volume = 0
          try: epstrailing = verifKey(infoStock['defaultKeyStatistics'],'trailingEps')
          except: epstrailing = 0
          try: epsforward = verifKey(infoStock['defaultKeyStatistics'], 'forwardEps')
          except: epsforward = 0
          try: petrailing = verifKey(infoStock['defaultKeyStatistics'],'trailingPE')
          except: petrailing = 0
          try: peforward = verifKey(infoStock['defaultKeyStatistics'],'forwardPE')
          except: peforward = 0
          try: pegratio = verifKey(infoStock['defaultKeyStatistics'],'pegRatio')
          except: pegratio = 0
          try: beta = verifKey(infoStock['defaultKeyStatistics'],'beta')
          except: beta = 0
          try: earnings = verifKey(infoStock['financialData'],'earningsGrowth')
          except: earnings = 0
          try: ptb = verifKey(infoStock['defaultKeyStatistics'],'priceToBook')
          except: ptb = 0
          try: book = verifKey(infoStock['defaultKeyStatistics'],'bookValue')
          except: book = 0
          try: shares = verifKey(infoStock['defaultKeyStatistics'],'sharesOutstanding')
          except: shares = 0
          try: divrate = verifKey(infoStock['summaryDetail'],'dividendRate')
          except: divrate = 0
          try: divyield = verifKey(infoStock['summaryDetail'],'dividendYield')
          except: divyield = 0
          try: divlastval = verifKey(infoStock['defaultKeyStatistics'],'lastDividendValue')
          except: divlastval = 0
          try: divlastdate = verifKey(infoStock['defaultKeyStatistics'],'lastDividendDate')
          except: divlastdate = 0
          try: divexdate = verifKey(infoStock['summaryDetail'],'exDividendDate')
          except: divexdate = 0
          try: payout = verifKey(infoStock['summaryDetail'],'payoutRatio')
          except: payout = 0
          try: avg52 = verifKey(infoStock['summaryDetail'],'fiftyDayAverage')
          except: avg52 = 0
          #avg52 = infoStock2['fiftyDayAverage']
          try: max52 = verifKey(infoStock['summaryDetail'],'fiftyTwoWeekHigh')
          except: max52 = 0
          #max52 = infoStock2['fiftyTwoWeekHigh']
          dist52=0
          try: avg200 = verifKey(infoStock['summaryDetail'],'twoHundredDayAverage')
          except: avg200 = 0
          #avg200 = infoStock2['twoHundredDayAverage']
          dist200=0
          #if len(divexdate) > 2:
            #divexdate=divexdate[:10]
          ###testing
          #data_chatpgpt = yf.download(tick, period="2y", interval="1d")
          #data_last_52_weeks = data_chatpgpt.tail(252)
          #max52= data_last_52_weeks['High'].max()
          #print(f"ticker {tick} con valore data {divexdate} e lunghezza {len(divexdate)}")
          #if len(divexdate) > 2: #quindi se non è 0
           # divexdate=divexdate[8:10] +'/'+divexdate[5:7]+'/'+divexdate[:4]
          #except:
          #  marketCap = 0
          #  volume = 0
          #  epstrailing = 0
          #  epsforward =0
          #  petrailing = 0
          #  peforward =0
          #  pegratio = 0
          #  beta = 0
          #  earnings = 0
          #  ptb = 0
          #  book = 0
          #  shares = 0
          #  divrate = 0
          #  divyield = 0
          #  divlastval = 0
          #  divlastdate = 0
          #  divexdate = 0
          #  payout = 0
          #  avg52 = 0
          #  dist52=0
          #  max52=0
          #  avg200 = 0
          #  dist200=0
          #  divexdate=0
          #  list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) 
        #divlastdate=
        #appendo Settore, industria
        #print(f'lavoro con TICK {tick}')
        #print(tabIsinData['ASSET'].iloc[0])
          list2d.append([i,tick,marketCap,volume,epstrailing,epsforward,petrailing,
          peforward,pegratio,beta, earnings, ptb, book, shares, divrate, divyield,divlastval,
          divlastdate,divexdate,payout,avg52,dist52,avg200,dist200,max52])

    #trasformo la lista in DF
    portaf2 = pd.DataFrame(list2d, columns =['Isin-JOIN','Ticker-JOIN','marketCap','volume','epstrailing','epsforward','petrailing',
        'peforward','pegratio','beta', 'earnings', 'ptb', 'book', 'shares', 'divrate', 'divyield','divlastval',
        'divlastdate','divexdate','payout','avg52','dist52','avg200','dist200','max52']) 

    #concateno i due DF tramite JOIN
    result = pd.concat([portaf, portaf2], axis=1,join="inner")
    #rimuovo colonne di join
    result.drop(['Isin-JOIN','Ticker-JOIN'], axis=1,  inplace=True)
    return result

  def writePortfolio(self):
    #richianmo portafoglio
    portfin = Portfolio.financialsPartPort(self)
    #print('Stampa 01')
    #print(portfin.to_string())
    #ggiungo data
    portfin['DataUpdate'] = Portfolio.todayDateHourAm
    #aggiungo colonna con numero portafoglio
    portfin['Num Port'] = self.num_port
    #numport esporto colonna
    numport=portfin.pop('Num Port')
    #riaggiongo colonna all'inizio
    portfin.insert(0, 'Num Port', numport) 
    #stampo tutto il dataframe
    #print('Stampa 02')
    #print(portfin.to_string())
    myColumns = portfin.columns.tolist()
    #print(myColumns)
    ################# A questo punto inizio a gestire la casistica dei due o piu portafogli
    oldPortRead = read_range('tab_portfolio!A1:AT100',newPrj)
    if oldPortRead.empty:
      portfin0 = portfin
    else:
      #print(oldPortRead.to_string())
      #salvare solo id portafolgio che non sto scrivendo
      deltPort = oldPortRead[(oldPortRead.iloc[:,0] != self.num_port)] 
      #print(deltPort.columns)
      deltPort.columns = myColumns
      #print(deltPort.to_string())
      #unisco i due dataframe
      #deltPort.reset_index(inplace=True,drop=True)
      frames = [portfin, deltPort]
      portfin0 = pd.concat(frames, ignore_index=True)
    #ordino dataframe per id portaf e asset e composizione
    portFinal = portfin0.sort_values(by=['Num Port', 'Asset', 'peso'])
    #print('Stampa 03')
    #print(portFinal.to_string())
    ################# End multiple portfolio
    #trasformo in lista
    listPrint = portFinal.values.tolist()
    #print(listPrint)
    #lunghezza lista
    lastRowSt=str(len(listPrint)+1)
    #print("stampo il portafoglio prima di scriverlo")
    #print(listPrint)

    #cancello tutto l'esistente
    deleteOldRows = delete_range('tab_portfolio!A2:AT100',newPrj)
    #scrivo portafolgio
    write_range('tab_portfolio!A2:AT'+lastRowSt,listPrint,newPrj)
    #print(portfin.head())

    return 'Ho completato aggiornamento del portafoglio'


################################################################################
##### TABELLA DATI STORICI
################################################################################

  def getHistPrice(row):

    print(f"Recupero prezzo storico di {row['Ticker']} alla data {row['dataHist']}")
    #print(row)
    #funzione che mi da il prezzo a mercato dei vari asset
    dateRead = row['dataHist']
    if row['Asset'] == 'P2P':
      histPrice = float(row['TotInvest'])+float(row['Divid'])
      #d = {'Ticker':}
      #histPrice = pd.Series( [histPrice1], index=[row['Ticker']])
    elif row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      histTot = readEuronextREV2(row['Isin'],dateRead)
      histPriceDf = histTot[histTot['Date'] == dateRead]
      if len(histPriceDf) >0 :
        histPrice = histPriceDf['Close'].values[0]
      else:
        #se ci sono festività e non posso filtrare il giorno giusto prendo l'ultimo valore disponibile
        histPrice = histTot['Close'].iloc[-1] 

    elif row['Asset'] == 'AZIONI' or row['Asset'] == 'ETF-AZIONI' or row['Asset'] == 'ETC':
      #converto la data di lettura
      #dateRead1 = datetime.strptime(dateRead, '%d/%m/%Y').strftime('%Y-%m-%d')
      dateRead1 = datetime.strptime(dateRead, '%Y-%m-%d').strftime('%Y-%m-%d')
      #per gestire i giorni mancanti devo avere un range di date prima della data reale
      #dataInizio = (datetime.strptime(dateRead, '%d/%m/%Y')+timedelta(days=-5)).strftime('%Y-%m-%d')
      dataInizio = (datetime.strptime(dateRead, '%Y-%m-%d')+timedelta(days=-5)).strftime('%Y-%m-%d')
      #converto la data di oggi
      todayCon = datetime.strptime(Portfolio.todayDate, '%d/%m/%Y').strftime('%Y-%m-%d')
      #prendo anche due giorni dopo perchè se è lunedi yahoo mi da i dati di venerdi..
      dataFine = (datetime.strptime(todayCon, '%Y-%m-%d')+timedelta(days=3)).strftime('%Y-%m-%d')
      #trovo i prezzi
      prices = yf.download(row['Ticker'],dataInizio,dataFine,progress=False) 
      #print(prices)  
      #aggiungo le date vuote
      prices1 = prices.asfreq('D')
      #copio i valori delle righe vuote dalla riga sopra
      #prices2 = prices1.fillna(method='ffill')
      prices2 = prices1.ffill()
      #print(f"leggo ticker {row['Ticker']} alla data reale {dateRead1} e data inizio {dataInizio} fino a {dataFine}")
      #print(prices2)
      prices3 = prices2.filter(items=[dateRead1], axis=0)
      #print(f"lunghezza {len(prices3)}")
      if len(prices3) >0 :
        histPrice = prices3['Close'].values[0]
      else:
        #se ci sono festività e non posso filtrare il giorno giusto prendo l'ultimo valore disponibile
        histPrice = prices2['Close'].iloc[-1].values[0]
       
      #trovo valuta
      infoStock = getStockInfo(row['Ticker'])
      currency=infoStock['currency']
      #cambio valuta
      #print('PRE CONVERSION')
      #print(type(histPrice))
      histPrice = Portfolio.calcCurren(histPrice,currency)
      #print('POST CONVERSION')
      #print(type(histPrice))
      #print('---')
      #histPrice = histPrice1[0]

    else:
      histPrice='0'
    #print('TIPO DATO')
    #print(type(histPrice))
    #print('STAMPO DATO')
    #print(histPrice)
    #print('STAMPO VALORE')
    #print(histPrice[0])
    #print('--------')

    return histPrice

  def getHistctvMerc(row):
    #print(row)
    #print(row['Qta'])
    #print(row['HistPrice'])
    ctvMerc = float(row['Qta'])*float(row['HistPrice'])
    if row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      ctvMerc=ctvMerc/100      
    return ctvMerc

 #Tabella tab_calendar
  def histDf(self, histdate):
    #mi prendo gli isin attivi alla data interessata
    isins = Portfolio.readActiveIsinByDate(self,histdate)
    #prendo i dati calcolati
    portHist = Portfolio.calcDataPortREV2(self, isins)
    #print(histdate)
    #print(portHist)
    #aggiungo la data
    portHist['dataHist'] = histdate
    #print(portHist.to_string())
    #aggiungo prezzo storico
    portHist['HistPrice']=portHist.apply(Portfolio.getHistPrice,axis=1 )
    #portHist['HistPrice']=0
    #portHist['HistPrice']=portHist['HistPrice'].apply(Portfolio.getHistPrice )
    #portHist['HistPrice']=Portfolio.getHistPrice
    portHist['HistPriceEur']=portHist['HistPrice']
    #calcolo controvalore mercato
    portHist['ctvMerc']=portHist.apply(Portfolio.getHistctvMerc,axis=1 )

    #tolgo currency
    #portHist.drop(['CURRENCY','ISIN-JOIN'], axis=1,  inplace=True)
    #riordino
    portHist = portHist[['dataHist','Ticker','Qta','PrezzoPond','HistPrice','HistPriceEur','Divid','TotInvest','ctvMerc']]
    return portHist  
  
   #Tabella tab_calendar
  def updateCalendarTab(self):
    #leggo il calendar e prendo ultima data
    lastDateDf=read_range('tab_calendar!A:K',newPrj)
    lastDate = lastDateDf['Data'].iloc[-1]
    #lunghezza DF = righe compilate nel foglio+1 perchè c'è intestazione+1perch
    numRows = len(lastDateDf) + 1 
    #oggi e ieri
    today = Portfolio.todayDate
    yesterday = (datetime.now()+timedelta(days=-1)).strftime('%Y-%m-%d')
    #differenza tra ultima data e ieri
    diffdate = (datetime.strptime(yesterday, "%Y-%m-%d") - datetime.strptime(lastDate, "%Y-%m-%d")).days
    print(f"differenza tra ultima data {lastDate} e ieri {yesterday} è {diffdate} condizione {lastDate < yesterday}")
    ### Foglio tab_caltot , mi prendo ultima riga###
    tabCalTot=read_range('tab_caltot!A:A',newPrj)
    rowToWr = len(tabCalTot)
    #if(lastDate < yesterday):
    if(diffdate>0):
      print('Procedo')
      #loop da 0 a diffdate 
      i=1
      startRow = numRows+1
      while i <= diffdate:
        #dateSearch = (datetime.strptime(lastDate, "%d/%m/%Y")+timedelta(days=i)).strftime('%d/%m/%Y')
        dateSearch = (datetime.strptime(lastDate, "%Y-%m-%d")+timedelta(days=i)).strftime('%Y-%m-%d')
        histDf = Portfolio.histDf(self,dateSearch)
        #print(histDf)
        numRowsHistDf = len(histDf)
        endRow = startRow+numRowsHistDf
        #trasformo in lista
        histList = histDf.values.tolist()
        ######Cambio funzione perchè la prima si blocca alla fine del file se non ci sono piu righe..
        #write_range('tab_calendar!A'+str(startRow)+':I'+str(endRow),histList,newPrj)
        appendRow('tab_calendar!A:I',histList,newPrj)
        ########## TAB_TOTALI #########
        totTab = Portfolio.totalhistory(self,histDf,int(i+rowToWr))
        #aggiorno nuova startRow
        startRow = startRow+numRowsHistDf
        i += 1
    else:
      print('aggiornamento non necessario')
    return 'Terminato aggiornamento calendar'

  def totalhistory(self,histDf,i):
    histDf.loc['total']= histDf.sum()
    histDf.loc[histDf.index[-1], 'dataHist'] = ''
    histDf.loc[histDf.index[-1], 'Ticker'] = ''
    #mercato
    dataDelta = (datetime.strptime(histDf['dataHist'].iloc[0], '%Y-%m-%d')+timedelta(days=5)).strftime('%Y-%m-%d')
    prezzoMerc1 = yf.download('CSSPX.MI',histDf['dataHist'].iloc[0],dataDelta,progress=False) 
    prezzoMerc2 = prezzoMerc1.asfreq('D')
    #prezzoMerc = prezzoMerc2.fillna(method='ffill')
    prezzoMerc = prezzoMerc2.ffill()
    rendim=histDf.loc['total']['ctvMerc'] - histDf.loc['total']['TotInvest']
    rendimperc= (rendim * 100) / histDf.loc['total']['TotInvest']
    mercato_df = prezzoMerc['Close'].iloc[0]
    mercato = mercato_df['CSSPX.MI']
    rendimMerc=100*(float(mercato)-257.01)/257.01
    delta = rendimMerc - rendimperc
    arrTot = [[histDf['dataHist'].iloc[0],
      histDf.loc['total']['TotInvest'],
      histDf.loc['total']['ctvMerc'],
      rendim,
      rendimperc,
      histDf.loc['total']['Divid'],
      rendimMerc,
      mercato,
      delta]]
    print(f'Array totale del giorno {arrTot}')
    appendRow('tab_caltot!A:I',arrTot,newPrj)
    #write_range('tab_caltot!A'+str(i)+':I'+str(i),arrTot,newPrj)
    
    return 'ok'

  def transactActive(self,df):
    #tolgo i valori vuoti e metto 0
    df["Quantità (real)"] = df["Quantità (real)"].replace(to_replace='',value=0)
    df2 = df
    isins = df["ISIN"].drop_duplicates()
    #loop sulla lista degli isin singoli
    for j in isins:
      #creto df con solo quell'isin
      tab = df[df["ISIN"] == j]
      #trovo qta totale
      qta = sum(pd.to_numeric(tab["Quantità (real)"]))
      #se la quantità è zero tolgo qull'isin da DF
      if qta < 0.001:
        #rimuovo le righe con isin che ha qta=0
        df2 = df2.loc[df2["ISIN"] != j]
    return df2

  def calcCurren(importo , currency):
    if str(currency).upper() == 'GBP':
      c = CurrencyConverter()
      priceConv = c.convert(importo, 'GBP', 'EUR')/100
      return priceConv
    elif str(currency).upper() == 'CHF':
      c = CurrencyConverter()
      priceConv = c.convert(importo, 'CHF', 'EUR')
      return priceConv
    else:
      return importo

  def calcDataPortREV2(self, df):
    #prendo solo gli isin
    dfUnique = df['ISIN'] 
    #cancello duplicati
    dfUnique.drop_duplicates(inplace=True)
    listAll=[[]]
    #dfUnique = dfUnique.to_frame()
    #loop per ogni isin
    for i in dfUnique:
      #ho il dataframe filtrato
      tab = df[df["ISIN"] == i]
      #print(tab)
      if i== 'IE00B53SZB19':
        #print(tab)
        print(sum(pd.to_numeric(tab["Quantità (real)"])))
      
      #calcolo qta e costi
      qta = sum(pd.to_numeric(tab["Quantità (real)"]))
      #print(f"Isin {i} e quantità {qta}")
      costi = sum(pd.to_numeric(tab["Costi"]))
      #filtro per dividendi
      dfDivi = tab[tab['Tipo'] == 'DIVID']
      divid = sum(pd.to_numeric(dfDivi['Spesa/incasso effettivo']))
      #filtro per acq
      dfAcq = tab[tab['Tipo'] == 'ACQ'] 
      spesAcq = sum(pd.to_numeric(dfAcq['Spesa/incasso effettivo']))
      qtaAcq = sum(pd.to_numeric(dfAcq['Quantità (real)']))
      print(f"calcolo valori per {i} che ha qta: {qta} acquisti: {spesAcq} e qta acq:{qtaAcq}")
      #calcolo prezzo ponderatp e totale investito
      prezPond = spesAcq/qtaAcq
      totInv = qta*prezPond 
      #recupero ticker e asset type che mi servirà per il prezzo 
      #aggiungo nella lista solo se la quantità è diversa da zero
      if qta > 0.01:
        listAll.append([i,tab['Ticker'].iloc[0],tab['Asset'].iloc[0],round(qta,4),round(prezPond,4),round(divid,4),round(totInv,4),costi])
        #print(listAll)
    #tolgo prima riga vuota
    listAll.pop(0)
    #trasformo in dataframe la lista
    dfFinal = pd.DataFrame(listAll,columns =['Isin', 'Ticker' ,'Asset','Qta','PrezzoPond','Divid','TotInvest', 'Costi'])
    return dfFinal

################################################################################
##### TABELLA COMPOSIZIONE - AZIENDE
################################################################################
  #provo a usare API alpha vantage https://www.alphavantage.co/documentation/
  #//limiti uso
  #//We are pleased to provide free stock API service covering the majority of our datasets 
  #//for up to 5 API requests per minute and 100 requests per day. 
  #//If you would like to target a larger API call volume, please visit premium membership.

  def getLinkTabIsin(ticker):
    fulldata = read_range('tab_isin!A:M',newPrj)
    partData = fulldata[(fulldata['TICKER YAHOO'] == ticker)]
    link = partData['SITO UFFICIALE'].iloc[0]
    return link

  def getCompany(row):
    #print(i)
    #"i" arriva come tupla, converto in df
    #row = pd.DataFrame(i, columns=['Asset','Ticker','DESCRIZIONE LUNGA'])
    oggiData = datetime.today().strftime('%d/%m/%Y')
    if row['Asset'] == 'ETF-AZIONI' or row['Asset'] == 'ETC':
      print(f"cerco dati del ticker {row['Ticker']}")
      fund = Ticker(row['Ticker'])
      outpList = fund.fund_holding_info[row['Ticker']]['holdings']
      stocks = pd.DataFrame(outpList)
      stocks['Ticker']=row['Ticker']
      stocks['Asset']=row['Asset']
      stocks['Data']=oggiData
      if len(outpList) < 2:
        stocks['symbol']=row['Ticker']
        stocks['holdingName']=row['DESCRIZIONE LUNGA']
        stocks['holdingPercent']=1
        stocks['PercPort']=1
        stocks['PercPort']=row['peso']
      else:
        stocks['PercPort']=row['peso']*stocks['holdingPercent']
      #print(stocks)
      #metto ticker all'inizio
      stocks=stocks[['Data','Asset','Ticker','symbol','holdingName','holdingPercent','PercPort']]
      #print(stocks)
      #print(stocks.head())
      #print(f"lunghezza array {len(stocks)}")
      link = Portfolio.getLinkTabIsin(row['Ticker'])
      print(f"il link del ticker {row['Ticker']} è {link}")

      #dataIsin = self.tabIsin()
      #dataIsin = dataIsin[dataIsin['TICKER YAHOO'] == row['Ticker']]  
      #print(dataIsin)
      #fund_ticker = "IVV" # IShares Core S&P 500 ETF
      #holdings_date =  "2024-06-17" # or None to query the latest holdings
      #etf_scraper = ETFScraper()
      #holdings_df = etf_scraper.query_holdings(row['Ticker'], holdings_date)
      #print(holdings_df)

    else:
      percPort = row['peso']
      dict1 = {'Data':oggiData,'Asset':row['Asset'], 'Ticker':row['Ticker'],'symbol':row['Ticker'], 'holdingName':row['DESCRIZIONE LUNGA'],'holdingPercent':1,'PercPort':percPort}
      #trasformo in dataframe
      stocks = pd.DataFrame(dict1, index=[0])
    return stocks

  def portCompanies(self):
    if Portfolio.readlastDate(self,'tab_aziende') == 1:
      print('Continuo')
      #prima mi prendo i dati del portafoglio ad oggi
      port = Portfolio.dFPortf(self)
      #print(port.keys())
      portShort = port[['Asset','Ticker','DESCRIZIONE LUNGA','peso']].copy()
      #portShort['Azienda']=portShort.apply(Portfolio.getCompany,axis=1 )
      #for i in portShort.iterrows():
      stocksGlobal = pd.DataFrame()
      for i in range(len(portShort)):
        #print(f'vai {i}')
        stocksDF = Portfolio.getCompany(portShort.loc[i])
        #print(type(stocksDF))
        #stocksGlobal = pd.concat(stocksDF,ignore_index=True)
        stocksGlobal = pd.concat([stocksGlobal,stocksDF],axis=0)
        #print(stocksDF)
      #print(stocksGlobal)
      #scrivo i dati
      listPrint = stocksGlobal.values.tolist()
      lastRowSt=str(len(listPrint)+1)
      deleteOldRows = delete_range('tab_aziende!A2:G200',newPrj)
      write_range('tab_aziende!A2:G'+lastRowSt,listPrint,newPrj)
    else:
      print("Aggiornamento non necessario")
    return 'Done'

################################################################################
##### TABELLA COMPOSIZIONE - SETTORI
################################################################################
  
  def readDateTabSettori(self):
    tabIsinsNew = read_range('tab_sectors!A:M',newPrj)
    statusReadDf = read_range('tab_sectors!O2:O2',newPrj)
    statusRead = statusReadDf.columns[0]
    print(statusRead)
    if(statusRead == 'INCOMPLETE'):
      return 'ok'
    else:
      #print(tabIsinsNew.head())
      if len(tabIsinsNew) != 0: #xaso in cui tabella sia vuota
        lastDate = tabIsinsNew['DATA'].iloc[0]
        print(f" Ultima data foglio {lastDate} e data oggi {datetime.today().strftime('%Y-%m-%d')}")
        if lastDate == datetime.today().strftime('%Y-%m-%d'):
          return 'Aggiornamento non Necessario'
        else:
          return 'ok'
      else:
        return 'ok'

  def portafSettori(self):
    if Portfolio.readDateTabSettori(self) == 'ok':
      port = Portfolio.dFPortf(self)
      portShort = port[['Asset','Ticker','DESCRIZIONE LUNGA','peso','SETTORE']].copy()
      #portShort['Azienda']=portShort.apply(Portfolio.getCompany,axis=1 )
      #for i in portShort.iterrows():
      allSectors = pd.DataFrame()
      AllData='Ok'
      
      #voglio lista di etf perchè la funzione massiva di raccoglimento settori funziona meglio della singola..
      etfs = port[port['Asset'] == "ETF-AZIONI"]
      etfsList = etfs['Ticker'].tolist()
      allSectorsEtf = sectorsMultipEtf(etfsList)
      #primo = allSectorsEtf['XDEQ.MI']
      #print(primo)
  
      for i in range(len(portShort)):
        if(portShort['Asset'].loc[i] == "ETF-AZIONI"):

          #leggo i settori dell'etf
          #settori = sectorsEtf(portShort['Ticker'].loc[i]) #####QUI capire se posso usare il massivo..
          #print(allSectorsEtf['GLUX.MI'])
          print(portShort['Ticker'].loc[i])
          settori1 = allSectorsEtf[portShort['Ticker'].loc[i]]
          #print(settori)
          settori = settori1.to_frame()
          #print(sectors)
          #print('---------------')
          #print(type(settori))
          #print(settori.index)
          #print('stampo columns')
          #print(settori.columns)
          #time.sleep(20) #aspetto un po perchè vedo che non mi da sempre i valori
          #dato che la funzione di prima riporta i settori come chiavi li riporto come colonna
          settori['Settore_ETF'] = settori.index
      
          #print('creo colonna')
          #cambio l'index che conteneva il settore
          #print(settori)
          #print('resetto indice')
          settori=settori.reset_index()
          #print(settori)
          #costruisco il DF
          settori['Data'] = Portfolio.todayDate_f
          settori['Asset'] = portShort['Asset'].loc[i]
          settori['Ticker'] = portShort['Ticker'].loc[i]
          settori['Descrizione'] = portShort['DESCRIZIONE LUNGA'].loc[i]
          settori['Peso_Tick'] = portShort['peso'].loc[i]
          if len(settori[portShort['Ticker'].loc[i]]) > 1:
            settori['Settore'] = settori['Settore_ETF'].str.upper()
            settori['Settore'] = settori['Settore'].str.replace('_',' ')
            settori['Peso_singolo'] = settori[portShort['Ticker'].loc[i]]       
            settori['Peso'] = portShort['peso'].loc[i]*settori[portShort['Ticker'].loc[i]]
            #tolgo la colonna che si chiama come il ticker
            settori = settori.drop([portShort['Ticker'].loc[i],'Settore_ETF',0], axis =1)
            
            #print(settori.to_string())
          else : #caso in cui la funzione non mi torna i settori
            settori['Settore'] = 'Other'
            settori['Peso_singolo'] =0 
            settori['Peso'] = portShort['peso'].loc[i]
            settori = settori.drop([portShort['Ticker'].loc[i],'Settore_ETF','index'], axis =1)
            AllData='INCOMPLETE'

          #print(settori.to_string())
   
        else: #azione o bond
          d = {'Data' :Portfolio.todayDate_f,
              'Asset':portShort['Asset'].loc[i],
              'Ticker':portShort['Ticker'].loc[i],
              'Descrizione':portShort['DESCRIZIONE LUNGA'].loc[i],
              'Settore':portShort['SETTORE'].loc[i].upper(),
              'Peso_Tick':portShort['peso'].loc[i],
              'Peso_singolo':portShort['peso'].loc[i],
              'Peso':portShort['peso'].loc[i]}
          settori = pd.DataFrame(d, index =[0])
          
        
        #concateno su un unico DF i vari dati
        allSectors = pd.concat([allSectors,settori], ignore_index=True)
      #calcolo il peso totale che dovrà essere 1
      totalWeight= allSectors['Peso'].sum()
      #print(allSectors.to_string())

      #Ora mi serve un nuovo dataframe con solo i settori singoli e la somma dei pesi
      #copio il df
      sectorsUnique=allSectors[['Settore','Peso']].copy()
      #scrivo i totali dei pesi
      sectorsUnique['Total'] = allSectors.groupby(['Settore'])['Peso'].transform('sum')
      #tolgo la colonna peso originale
      sectorsUnique = sectorsUnique.drop('Peso', axis =1)
      #tolgo i duplicati
      sectorsUnique1 = sectorsUnique.drop_duplicates(inplace=False)
      #ordino DF
      sectorsUnique1=sectorsUnique1.sort_values(by=['Total'], ascending=[False])
      #print(sectorsUnique1)

      #scrivo i dati su spreadsheet
      listPrint = allSectors.values.tolist()
      lastRowSt=str(len(listPrint)+1)
      listPrintWeights = sectorsUnique1.values.tolist()
      lastRowWeights=str(len(listPrintWeights)+1)
      deleteOldRows = delete_range('tab_sectors!A2:M600',newPrj)
      write_range('tab_sectors!A2:H'+lastRowSt,listPrint,newPrj)
      write_range('tab_sectors!J2:J2',[[totalWeight]],newPrj)
      write_range('tab_sectors!L2:M'+lastRowWeights,listPrintWeights,newPrj)
      write_range('tab_sectors!O2:O2',[[AllData]],newPrj)
      
      return 'Done writing sectors'
    else:
      return 'Aggiornamento non necessario'

################################################################################
##### TABELLA COMPOSIZIONE - PAESI
################################################################################

  def readDateTabPaesi(self):
    tabIsinsNew= read_range('tab_country!A:M',newPrj)
    #print(tabIsinsNew.head())
    if len(tabIsinsNew) != 0: #xaso in cui tabella sia vuota
      lastDate = tabIsinsNew['DATA'].iloc[0]
      print(f" Ultima data folgio {lastDate} e data oggi {datetime.today().strftime('%Y-%m-%d')}")
      if lastDate == datetime.today().strftime('%Y-%m-%d'):
        return 'Aggiornamento non Necessario'
      else:
        return 'ok'
    else:
      return 'ok'

  def portafPaesi(self):
    if Portfolio.readDateTabPaesi(self) == 'ok':
      port = Portfolio.dFPortf(self)
      portShort = port[['Asset','Isin','Ticker','DESCRIZIONE LUNGA','peso']].copy()
      #print(portShort.to_string)
      allCountries = pd.DataFrame()
      for i in range(len(portShort)):
        print(f"Lavoro con {portShort['Isin'].loc[i]}" )
        if(portShort['Asset'].loc[i] == "ETF-AZIONI" or portShort['Asset'].loc[i] == "ETC"):  #se è etf
          #leggo i settori dell'etf
          print('################################ETF COUNTRY################################')
          paesidF = listEtfCountries(portShort['Isin'].loc[i])
          print(paesidF)
          paesidF.dropna(inplace=True)
          #print(paesidF)
          paesidF['Data'] = Portfolio.todayDate_f
          paesidF['Asset'] = portShort['Asset'].loc[i]
          paesidF['Ticker'] = portShort['Ticker'].loc[i]
          paesidF['Descrizione'] = portShort['DESCRIZIONE LUNGA'].loc[i]
          paesidF['Paese'] = paesidF['Country'].str.upper()
          paesidF['Peso_Tick'] = portShort['peso'].loc[i]
          paesidF['Peso_singolo'] = paesidF['Peso_country']
          paesidF['Peso'] = portShort['peso'].loc[i].astype(float)*paesidF['Peso_country'].astype(float)
          paesidF = paesidF.drop(['isin','Country','Peso_country'], axis =1)

        elif(portShort['Asset'].loc[i] == "AZIONI"): #e è azione
          paese = listStocksCountries(portShort['Isin'].loc[i])
          d = {'Data' :Portfolio.todayDate_f,
              'Asset':portShort['Asset'].loc[i],
              'Ticker':portShort['Ticker'].loc[i],
              'Descrizione':portShort['DESCRIZIONE LUNGA'].loc[i],
              'Paese':paese[1].upper(),
              'Peso_Tick':portShort['peso'].loc[i],
              'Peso_singolo':100,
              'Peso':portShort['peso'].loc[i].astype(float)*100}
          paesidF = pd.DataFrame(d, index =[0])

        else:   #se è btp o bpt o p2p
          d = {'Data' :Portfolio.todayDate_f,
              'Asset':portShort['Asset'].loc[i],
              'Ticker':portShort['Ticker'].loc[i],
              'Descrizione':portShort['DESCRIZIONE LUNGA'].loc[i],
              'Paese':'ITALIA',
              'Peso_Tick':portShort['peso'].loc[i],
              'Peso_singolo':100,
              'Peso':portShort['peso'].loc[i].astype(float)*100}
          paesidF = pd.DataFrame(d, index =[0])

        #concateno su un unico DF i vari dati
        allCountries = pd.concat([allCountries,paesidF], ignore_index=True)
        #print(allCountries)
      #calcolo il peso totale che dovrà essere 1
      totalWeight= allCountries['Peso'].sum()
      allCountries['Peso_singolo']=allCountries['Peso_singolo'].apply(replace_dot_with_comma)
      #print(allCountries.to_string())
      
      #trovo singoli
      countryUnique=allCountries[['Paese','Peso']].copy()
      #scrivo i totali dei pesi
      countryUnique['Total'] = allCountries.groupby(['Paese'])['Peso'].transform('sum')
      #tolgo la colonna peso originale
      countryUnique = countryUnique.drop('Peso', axis =1)
      #tolgo i duplicati
      countryUnique1 = countryUnique.drop_duplicates(inplace=False)
      #ordino DF
      countryUnique1=countryUnique1.sort_values(by=['Total'], ascending=[False])
      #print(countryUnique1.to_string)

      #scrivo i dati su spreadsheet
      listPrint = allCountries.values.tolist()
      lastRowSt=str(len(listPrint)+1)
      listPrintWeights = countryUnique1.values.tolist()
      lastRowWeights=str(len(listPrintWeights)+1)
      deleteOldRows = delete_range('tab_country!A2:M600',newPrj)
      write_range('tab_country!A2:H'+lastRowSt,listPrint,newPrj)
      write_range('tab_country!J2:J2',[[totalWeight]],newPrj)
      write_range('tab_country!L2:M'+lastRowWeights,listPrintWeights,newPrj)

      return 'Done writing countries'
    else:
      return 'Aggiornamento non necessario'
################################################################################
##### TABELLA ANDAMENTO
################################################################################
  
  def readlastDate(self,tab):
    fulldata = read_range(tab+'!A:A',newPrj)
    if(len(fulldata) == 0):
      status = 1 #proseguo
    else:
      dateSheet = fulldata['Data'].iloc[-1]
      print(f"ultima data del foglio {dateSheet} e oggi è {Portfolio.todayDate}")
      if dateSheet == Portfolio.todayDate :
        status = 0 #non faccio nulla
      else:
        status = 1 #proseguo
    return status

  def readCalendar(self,dateRead):
    #cambio formato data
    dateRead=datetime.strptime(dateRead ,'%d/%m/%Y').strftime('%Y-%m-%d')
    #Leggo i dati dal calendar
    fulldata = read_range('tab_calendar!A:I',newPrj)
    #imposto filtro
    partData = fulldata[(fulldata['Data'] == dateRead)]
    partData = partData.drop(columns=['Q.ta Incrementata','Prezzo pagato','Prezzo mercato (EUR)','Dividendo','Valore Investito','Valore Mercato'])
    #print(f'Leggo il celandar alla data {dateRead}')
    #print(partData)
    return partData

  def calcAndamPort(self):
    #########################
    #E' da rifare, non posso leggere da calendar, devo leggere da yahho finance.. solo criptalia e i btp magari..
    #########################
    if Portfolio.readlastDate(self,'tab_and_port') == 1:
      #prima mi prendo i dati del portafoglio ad oggi
      port = Portfolio.dFPortf(self)
      #prendo solo le colonne che mi interessano
      portShort = port[['Asset','Ticker','DESCRIZIONE LUNGA','LivePrice']].copy()
      #inserisco come prima colonna la data
      portShort.insert(0,'Data',Portfolio.todayDate)
      #calcolo date a cui leggere le variaizoni
      firstY = '01/01/'+ datetime.strptime(Portfolio.todayDate, '%d/%m/%Y').strftime('%Y')
      twoWeeksAgo = Portfolio.subDayToDate(Portfolio.todayDate,15)
      fourWeeksAgo = Portfolio.subDayToDate(Portfolio.todayDate,30)
      twoHundredAgo = Portfolio.subDayToDate(Portfolio.todayDate,200)
      print(f"Primo anno {firstY}, due settimane fa {twoWeeksAgo}, un mese fa {fourWeeksAgo}, duecento giorni fa {twoHundredAgo}")
      #ottengo i dataframe con i prezzi
      firstYDF = Portfolio.readCalendar(self,firstY)
      twoWeeksAgoDF = Portfolio.readCalendar(self,twoWeeksAgo)
      fourWeeksAgoDF =Portfolio.readCalendar(self,fourWeeksAgo)
      twoHundredAgoDF =Portfolio.readCalendar(self,twoHundredAgo)
      #costruisco dataframe come join dei precedenti
      finalDF = portShort.merge(firstYDF, on='Ticker', how='left')
      finalDF = finalDF.drop(columns=['Data_y'])
      finalDF = finalDF.rename(columns={"DESCRIZIONE LUNGA":"Descrizione","LivePrice":"Prezzo Oggi","Prezzo mercato":"Prezzo YTD"})
      #seconda join
      finalDF1 = finalDF.merge(twoWeeksAgoDF, on='Ticker', how='left')
      finalDF1 = finalDF1.drop(columns=['Data'])
      finalDF1 = finalDF1.rename(columns={"Prezzo mercato":"Prezzo 15gg"})
      #terza join
      finalDF2 = finalDF1.merge(fourWeeksAgoDF, on='Ticker', how='left')
      finalDF2 = finalDF2.drop(columns=['Data'])
      finalDF2 = finalDF2.rename(columns={"Prezzo mercato":"Prezzo 30gg","Data_x":"Data"})
      #quarta join
      finalDF3 = finalDF2.merge(fourWeeksAgoDF, on='Ticker', how='left')
      finalDF3 = finalDF3.drop(columns=['Data_y'])
      finalDF3 = finalDF3.rename(columns={"Prezzo mercato":"Prezzo 200gg","Data_x":"Data"})
      #print(finalDF3.to_string())
      #sostituisco i NaN
      finalDF3['Prezzo Oggi'] = finalDF3['Prezzo Oggi'].fillna(0)
      finalDF3['Prezzo YTD'] = finalDF3['Prezzo YTD'].fillna(0)
      finalDF3['Prezzo 15gg'] = finalDF3['Prezzo 15gg'].fillna(0)
      finalDF3['Prezzo 30gg'] = finalDF3['Prezzo 30gg'].fillna(0)
      finalDF3['Prezzo 200gg'] = finalDF3['Prezzo 200gg'].fillna(0)
      #conversione colonne
      finalDF3['Prezzo Oggi'] = finalDF3['Prezzo Oggi'].replace(to_replace=',',value='.',regex=True).astype(float)
      finalDF3['Prezzo YTD'] = finalDF3['Prezzo YTD'].replace(to_replace=',',value='.',regex=True).astype(float)
      finalDF3['Prezzo 15gg'] = finalDF3['Prezzo 15gg'].replace(to_replace=',',value='.',regex=True).astype(float)
      finalDF3['Prezzo 30gg'] = finalDF3['Prezzo 30gg'].replace(to_replace=',',value='.',regex=True).astype(float)
      finalDF3['Prezzo 200gg'] = finalDF3['Prezzo 200gg'].replace(to_replace=',',value='.',regex=True).astype(float)

      #calcolo GAP in percentuale
      finalDF3['Gap YTD']  = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo YTD'] )*100 / finalDF3['Prezzo Oggi']
      finalDF3['Gap 15gg'] = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo 15gg'])*100 / finalDF3['Prezzo Oggi']
      finalDF3['Gap 30gg'] = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo 30gg'])*100 / finalDF3['Prezzo Oggi']
      finalDF3['Gap 200gg'] = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo 200gg'])*100 / finalDF3['Prezzo Oggi']
      #print(finalDF3.to_string())
      #stampo dataframe su foglio
      numRows = len(finalDF3)+1
      arr = finalDF3.values.tolist()
      delete_range('tab_and_port!A2:M100',newPrj)
      write_range('tab_and_port!A2:M'+str(numRows),arr,newPrj) 
    else:
      print("Aggiornamento non necessario")
    return 'Done'

    
################################################################################
##### TABELLA ISIN
################################################################################

  def readDateTabIsin(self):
    tabIsinsNew= read_range('tab_isin!A:M',newPrj)
    #print(tabIsinsNew.head())
    if len(tabIsinsNew) != 0: #xaso in cui tabella sia vuota
      lastDate = tabIsinsNew['UPDATE'].iloc[0]
      #print(f" Ultima data folgio {lastDate} e data oggi {Portfolio.todayDate}")
      if lastDate == Portfolio.todayDate:
        return 'Aggiornamento non Necessario'
      else:
        return 'ok'
    else:
      return 'ok'

  def writeAllIsins(self):   
    if Portfolio.readDateTabIsin(self) == 'ok':
      tabellaDF = Portfolio.readListIsin(self)
      print(f"ho letto {len(tabellaDF)} righe dal vecchio tab_isin")
      tabella = tabellaDF.values.tolist()
      tabellaPrint=[]
      lastRow=str(len(tabellaDF)+1)
      for i in tabella:
        if i[5] == 'P2P':
          link = i[4]
          i.pop()
          i.pop()
          tabellaPrint.append(i + ['P2P',i[0],i[0],'Bond','Bond','Italy',link,'EUR',Portfolio.todayDate])
        elif i[5] == 'CRYPTO':
          link = i[4]
          i.pop()
          i.pop()
          tabellaPrint.append(i + ['CRYPTO',i[0],i[0],'Crypto','Crypto','Italy',link,'EUR',Portfolio.todayDate])
        elif i[5] == 'CURRENCY': 
          link = i[4]
          i.pop()
          i.pop()
          tabellaPrint.append(i + ['CURRENCY',i[0],i[0],'Currency','Currency','Italy',link,'EUR',Portfolio.todayDate])
        elif i[5] == 'BTP':
          link = i[4]
          btpData = getBtpData(i[0])
          i.pop()#tolgo asset
          i.pop()#tolgo link
          i.pop()#tolgo scadenza
          tabellaPrint.append(i + [btpData['scad'],'BTP',btpData['desc'],btpData['desc'],'Bond','Bond','Italy',link,btpData['curr'],Portfolio.todayDate])
        elif i[5] == 'BOT':
          link = i[4]
          botData = getBotData(i[0])
          i.pop()#tolgo asset
          i.pop()#tolgo link
          i.pop()#tolgo scadenza
          tabellaPrint.append(i + [botData['scad'],'BOT',botData['desc'],botData['desc'],'Bond','Bond','Italy',link,botData['curr'],Portfolio.todayDate])
        else:
          link = i[4]
          i.pop()
          i.pop()
          genData = Portfolio.getNameStock(i[1],link)
          tabellaPrint.append(i + genData)
      print("cancello vecchie righe")
      deleteOldRows = delete_range('tab_isin!A2:M250',newPrj)
      #scrivo le nuove
      write_range('tab_isin!A2:M'+lastRow,tabellaPrint,newPrj)
      return "Ho completato l'aggiornamento della tabella tab_isin"
    else:
      return "aggiornamento non necessario"

################################################################################
##### WHATCHLIST
################################################################################
  
  def getPriceYah(ticker):
    print('Leggo i dati del ticker')
    stock = yf.Ticker(ticker)
    tickInfo = stock.info
    curre = verifKey(tickInfo,'currency')
    price1d = verifKey(tickInfo,'previousClose')
    livePrice = verifKey(tickInfo, 'currentPrice')
    title = verifKey(tickInfo, 'longName')
    if title == 0: 
      title = verifKey(tickInfo, 'shortName')
    
    #datePrice = datetime.today().strftime('%Y-%m-%d')
    #arr = [ticker, '',livePrice,price1d]
    print(f"API - Per il ticker {ticker} il prezzo live è {livePrice} mentre il prezzo di ieri {price1d}")

    #if(livePrice == '0'):
      #print('Leggo il prezzo e i vari dati da yahoo finance')

      #arr = [tick,title,price,price1d]
      #yInfo = readYahooSite(ticker)
      #curre = yInfo[4]
      #price1d = yInfo[3]
      #livePrice = yInfo[2]
      #title = yInfo[1]
      #print(f"SITO - Per il ticker {ticker} il prezzo live è {livePrice} mentre il prezzo di ieri {price1d}")
    datePrice = datetime.today().strftime('%Y-%m-%d')
    arr = [ticker, '',livePrice,price1d,title]

    
    return arr

  def getDescr(asset,isin,tick):
    infoTick=[]
    #isin, ticker, descrizione, currency, prezzo, rendimen, scadenza , settore, industria, beta, pe,eps, price1D
    if(asset == 'BTP' or asset == 'BOT'):
      print('Leggo la descrizione')
      price=getBtpData(isin)
      #print(tick)
      #print(price)
      infoTick = [price['isin'],tick,price['desc'],price['curr'],price['pric'],price['yeld'],price['scad'],
      'Bond','Bond','','','',price['pric'],'','','','','','','','','','','','','','','','','','','','','','','','']
    #elif( ):
      #infoTick = ['',tick,'','','','','',
      #'Bond','Bond','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
    elif(asset == 'AZIONI' or asset == 'ETF' or asset == 'ETC' or asset == 'CURRENCY' or asset == 'CRYPTO'):
      
      #livePrice = Portfolio.getPriceYah(tick)     #yahoo query 
      infoStock = getStockInfo(tick)

      titleStock = infoStock['longName']
      if(len(titleStock)<2):
        titleStock = infoStock['shortName'] #prendo il titolo dal sito web

      if tick == 'BITC.DU': #devo cablare sta cosa perchè su yahoo non c'è..
        titleStock='CoinShares Physical Bitcoin'
        
      livePrice =infoStock['currentPrice']
      if(livePrice == '0' or livePrice == 0):
        livePrice = float(infoStock['bid']) #per gli ETF devo usare il bid perchè manca prezzo su api
      if(livePrice =='0' or livePrice == 0):
        livePrice = float(infoStock['open'])#per le cripto manca prezzo attuale, devo usare quello di apertura

      #infoTick = [isin,tick,infoStock['longName'],infoStock['currency'],livePrice[2],'','',
      #infoStock['sector'],infoStock['industry'],infoStock['beta'],infoStock['trailingPE'],infoStock['trailingEps'],livePrice[3],
      #Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekLow'),Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekHigh'),Portfolio.verifKey(infoStockYQ,'trailingPE')]
      infoTick = [isin,tick,titleStock,infoStock['currency'],livePrice,'','',
      infoStock['sector'],infoStock['industry'],infoStock['beta'],infoStock['trailingPE'],infoStock['forwardPE'],
      infoStock['trailingEps'],infoStock['forwardEps'],infoStock['previousClose'],
      infoStock['fiftyTwoWeekLow'],infoStock['fiftyTwoWeekHigh'],infoStock['trailingPE'],infoStock['pegRatio'],infoStock['trailingPegRatio'],
      infoStock['bookValue'],infoStock['priceToBook'],
      infoStock['earningsQuarterlyGrowth'],infoStock['enterpriseToRevenue'],infoStock['enterpriseToEbitda'],infoStock['quickRatio'],infoStock['currentRatio'],infoStock['debtToEquity'],
      infoStock['revenuePerShare'],infoStock['returnOnAssets'],infoStock['returnOnEquity'],infoStock['earningsGrowth'],
      infoStock['revenueGrowth'],infoStock['targetHighPrice'],infoStock['targetLowPrice'],infoStock['targetMeanPrice'],infoStock['targetMedianPrice']]


      #print(infoTick)
      #infoTick = [isin,tick,infoStock['longName'],infoStock['currency'],infoStock['currentPrice'],'','',
      #infoStock['sector'],infoStock['industry'],infoStock['beta'],infoStock['trailingPE'],infoStock['trailingEps'],infoStock['prevClose'],
      #Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekLow'),Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekHigh'),Portfolio.verifKey(infoStockYQ,'trailingPE')]

    else:
      infoTick=[isin,tick,'','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','']
    return infoTick

  def whatchlist(self):
    #loop sulla pagina tab_whatchlist
    tab_watch = read_range('tab_watchlist!A:R',newPrj)
    #modifico il dataframe mettendo i dati aggiornati
    listPrin =[]
    #loop sui ticker
    for i in tab_watch.index:
      asset = tab_watch['Asset'][i]
      isin = tab_watch['ISIN'][i]
      tick = tab_watch['Ticker'][i]
      ordin = tab_watch['Ordine'][i]
      av = tab_watch['A/V'][i]
      qta = tab_watch['QTA'][i]
      tot = tab_watch['TOT'][i]
      dOrdine = tab_watch['Data Ordine'][i]
      #print(f"Lunghezza dell'ordine {len(str(ordin))}")
      #print(f"Tipo dell'ordine {type(ordin)}")
      #print(f"Ordine è {ordin}")

      if str(ordin) != 'None':
      #if ordin is not None or ordin !='' or len(ordin)>1 or not ordin:
        ordin = ordin.replace(',','.')
      else:
        ordin = 0

      print(f"Read info of {tick} che è un {asset} con isin {isin}")
      tickInfo = Portfolio.getDescr(asset,isin,tick)
      print(f"stampo ordin {ordin} per {tick} e prezzo {tickInfo[4]} , chiusura precedente {tickInfo[14]} per tick {tickInfo[2]}, valori 52 week {tickInfo[15]} e {tickInfo[16]}")
      if tickInfo[4] != '':
        if float(tickInfo[4]) != 0:
          percPrezz = (float(ordin) - float(tickInfo[4]))/float(tickInfo[4])
        else:
          percPrezz = 0
      else:
          percPrezz = 0
      #Calcolo 52 WEEK
      if asset == 'BTP' or asset == 'CRYPTO' or asset == 'CURRENCY':
        fiftyTwoWeek=''
        fiftyTwoWeekPerc=''
        deltaIeri=0
      elif float(tickInfo[15]) > 0 and float(tickInfo[16]) > 0 and float(tickInfo[4]) > 0:
          fiftyTwoWeek = str(tickInfo[15]) + ' - ' +str(tickInfo[16]) + '( '+str(round(((float(tickInfo[15])+float(tickInfo[16]))/2),2))+ ' )'
          fiftyTwoWeekPerc = (float(tickInfo[4])-float(tickInfo[15]))/(float(tickInfo[16]) - float(tickInfo[15]))
          deltaIeri = round( (float(tickInfo[4]) - float(tickInfo[14])) / float(tickInfo[14]),2)
      else:
        fiftyTwoWeek=''
        fiftyTwoWeekPerc=''
        deltaIeri=0
      priceLiveWatch = changeFormatNumberPrint(tickInfo[4])
      priceYestWatch = changeFormatNumberPrint(tickInfo[14])
      priceOrder = changeFormatNumberPrint(ordin)
      listPrin.append([Portfolio.todayDateHour,asset,isin,tick,tickInfo[2],priceLiveWatch,priceYestWatch,priceOrder
      ,percPrezz,av,qta,tot,dOrdine,fiftyTwoWeek,fiftyTwoWeekPerc,deltaIeri,tab_watch['NOTE'][i],tickInfo[3],
      tickInfo[5],tickInfo[6],tickInfo[7],tickInfo[8],tickInfo[9],tickInfo[10],tickInfo[11],tickInfo[12],tickInfo[13],
      tickInfo[18],tickInfo[19],tickInfo[20],tickInfo[21],tickInfo[22],tickInfo[23],tickInfo[24],tickInfo[25],
      tickInfo[26],tickInfo[27],tickInfo[28],tickInfo[29],tickInfo[30],tickInfo[31],tickInfo[32],tickInfo[33],tickInfo[34],tickInfo[35] ])
      #portIsinCalc['LivePrice']=portIsinCalc.apply(Portfolio.getLivePrice,axis=1 )
    #print(len(listPrin))
    numRow = len(listPrin)+1

    #cancello vecchie righe
    deleteOldRowsWat = delete_range('tab_watchlist!A2:AS250',newPrj)
    #scrivo le nuove
    write_range('tab_watchlist!A2:AS'+str(numRow),listPrin,newPrj)
    return 'ok'

################################################################################
##### NEWS VARIE
################################################################################


    
  def loop_row(row):
    print(f"Loop per ticker {row['Ticker']}")
    #ticSto = 'FOO.DE'
    stock = Ticker(row['Ticker'])
    df1 = stock.corporate_events #ritorna df con eventi dell'azienda
    #df2 = stock.news
    #df3 = stock.recommendations
    #df4 = stock.technical_insights
    #print("Corporate events")
    df_filter = df1.tail(5)
    df_filter['Date'] = df_filter.index.get_level_values('date').strftime("%Y-%m-%d %H:%M:%S") 
    df_filter['Ticker'] = row['Ticker']
    df_filter['API'] = 'Corporate Events'
    df_filter = df_filter[['Ticker','API','Date','id','significance','parentTopics','headline','description']]
    df_fil_list=df_filter.values.tolist()
    appendRow('tab_news!A:I',df_fil_list,newPrj)
    #print(df_filter)
    #print("News")
    #print(df2)
    #print("Reccomendations")
    #print(df3)
    #print("Technical insight")
    #print(df4)
    
    
    
    #print(df.head())
    #portNew = orig_port.filter(not in ('BOT','BTP'), axis=0)
    #print(portNew)

  def newsStocks(self):
    #Prendo dalla classe il primo DF
    orig_port = self.actPort
    #filtro portafoglio
    portNew = orig_port[(orig_port.Asset == 'AZIONI')]['Ticker']
    #converto in DF
    portNewDf = portNew.to_frame()
    #loopDf = portNew.to_frame().apply(Portfolio.loop_row,axis=1)
    df_final = pd.DataFrame()
    #inizio loop
    for ind in portNewDf.index:
      print(f"Loop su {portNewDf['Ticker'][ind]}")
      stock = Ticker(portNewDf['Ticker'][ind])
      #CORPORATE EVENTS
      df1 = stock.corporate_events #ritorna df con eventi dell'azienda
      df_filter = df1.tail(5)
      df_filter['Date'] = df_filter.index.get_level_values('date').strftime("%Y-%m-%d %H:%M:%S") 
      df_filter['Ticker'] = portNewDf['Ticker'][ind]
      df_filter['API'] = 'Corporate Events'
      df_filter = df_filter[['Date','Ticker','API','id','significance','parentTopics','headline','description']]
      #df_fil_list=df_filter.values.tolist()
      #listToAppend.append(df_fil_list)
      df_final = df_final._append(df_filter, ignore_index = True)
      #NEWS
      df2 = stock.news
      print(df2)
      #listToAppend.append()
    #ordino dataframe
    df_final=df_final.sort_values(by=['Date'])
    #prendo le ultime 20 righe
    df_final = df_final.tail(20)
    #trasformo lista
    df_final_list=df_final.values.tolist()
    #scrivo
    appendRow('tab_news!A:I',df_final_list,newPrj)
    print(df_final.head())

################################################################################
##### FUNZIONI AGGIUNTIVE
################################################################################

  def readListIsin(self):
    tabIsins = read_range('tab_isin!A:L',oldPrj)
    tabIsinsFilt = tabIsins[tabIsins['MORNINGSTAR'] != 'INATTIVO']
    return tabIsinsFilt.filter(items=['ISIN','TICKER_YAHOO','TICKER_DATI','SCADENZA','SITO UFFICIALE','ASSET'])
    
  def gtDataFromTabIsinREV2(self):
    actPortf = self.actPort
    #estraggo i dati da tab_isin dato un isin di partenza
    assetData = read_range('tab_isin!A:L',newPrj)
    #prendo lista sin
    isintab = actPortf['Isin'].values.tolist()
    #filtro DF letto da google per avere solo gli isin attivi
    assetData[assetData.ISIN.isin(isintab)]
    return assetData

  def getNameStock(ticker,link):
    #prendo i dati di azioni e etf per tab_isin
    #stock = yf.Ticker(tikcer)
    info = getStockInfo(ticker)
    if (Portfolio.verifKey(info,'quoteType') == 'ETF' or Portfolio.verifKey(info,'quoteType') == 'ETC'):
       #print(f"scrivo dati ETF {ticker}")
       sector = sectorsEtf(ticker)
       sectName = Portfolio.beautyString(sector.index[0])
       sectPerc = sector.iloc[0]
       output = [
          Portfolio.verifKey(info,'quoteType'), 
          Portfolio.verifKey(info,'shortName'),
          Portfolio.verifKey(info,'longName'),
          sectName,
          sectName,
          Portfolio.verifKey(info,'country'),
          link,
          Portfolio.verifKey(info,'currency'),Portfolio.todayDate]
    else:
        output = [
          Portfolio.verifKey(info,'quoteType'), 
          Portfolio.verifKey(info,'shortName'),
          Portfolio.verifKey(info,'longName'),
          Portfolio.verifKey(info,'sector'),
          Portfolio.verifKey(info,'industry'),
          Portfolio.verifKey(info,'country'),
          link,
          Portfolio.verifKey(info,'currency'),Portfolio.todayDate]
    return output

  def verifKey(dict,val):
    #controllo che il valore esista nel dizionario
    if val in dict:
      return dict[val] 
    else:
      return 0

  def beautyString(string):
    #tolgo underscore e metto prima lettera maiuscola
    newString = string.replace(to_replace='_',value=' ').capitalize()
    if newString == "Realestate" : newString = "Real Estate"
    return newString
  
  #FUNZIONI SULLE DATE
  def sumDayToDate(dateInput):
    origDate = datetime.strptime(dateInput, "%d/%m/%Y")
    newDate = origDate + timedelta(days=1)
    return newDate.strftime("%d/%m/%Y")

  def subDayToDate(dateInput,days):
    origDate = datetime.strptime(dateInput, "%d/%m/%Y")
    daysSub = int(days)*(-1)
    newDate = origDate + timedelta(days=daysSub)
    return newDate.strftime("%d/%m/%Y")

################################################################################
##### CALCOLO RENDIMENTO (fuori da classe)
################################################################################

def diff_month(d1, d2):  
  #quindi (anno d1 - anno d2)*12+mesi d1-mesi d2
  return (int(datetime.strptime(d1, '%d/%m/%Y').strftime('%Y')) - int(datetime.strptime(d2, '%d/%m/%Y').strftime('%Y'))) * 12 + int(datetime.strptime(d1, '%d/%m/%Y').strftime('%m')) - int(datetime.strptime(d2, '%d/%m/%Y').strftime('%m'))

def caldRendimento():
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")

  todayDate = datetime.today().strftime('%d/%m/%Y')
  todayMonth = datetime.today().strftime('%m')
  todayYear = datetime.today().strftime('%Y')
  print(f"Mese corrente {todayMonth} e anno corrente {todayYear}")
  #dopo aver calcolato la data di oggi da confrontare con ultima riga del foglio.
  actualPerf = read_range('tab_performance!A:L',newPrj)

 #ultimo anno del foglio
  lastYear = actualPerf['Anno'].iloc[-1]
  lastMonth = actualPerf['Mese'].iloc[-1]
  lastDatelastday = actualPerf['Last day month'].iloc[-1]
  #calcolo ultima data
  lastDate = datetime(int(lastYear), int(lastMonth), 1).strftime('%d/%m/%Y')
  deltaMonth = diff_month(todayDate,lastDate)
  print(f"Ultima data del foglio è mese: {lastMonth} dell'anno: {lastYear} quindi siamo {lastDate}, mentre oggi {todayDate} quindi differenza mesi è {diff_month(todayDate,lastDate)}")
  #if(deltaMonth >= 1 and datetime.today().strftime('%d') != '01' ): #tolgo se sono al primo del mese perchè mi serve avere il primo giorno completo nel calendar
  if(deltaMonth > 1 ): #voglio che scriva il mese precedente e non quello in corso. quindi se deve scrivere ottobre dobbiamo essere in novembre.. proviamo
    
    ####Cancello ultima riga  delete_range('tab_performance!A63:L63',newPrj)
    
    i=1
    while i <= deltaMonth:
      #leggo ultimo giorno del mese dal foglio
      newYear = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=1)).strftime('%Y')
      newMonth = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=1)).strftime('%m')
      firstDayMon = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=1)).strftime('%d/%m/%Y')
      numdaysNewMonth = calendar.monthrange(int(newYear), int(newMonth))[1]
      lastDayMon = (datetime.strptime(lastDatelastday, '%d/%m/%Y')+timedelta(days=numdaysNewMonth)).strftime('%d/%m/%Y')
      print(f"primo del mese {firstDayMon} ultimo del mese {lastDayMon}")
      
      ####### Leggo i dati da CALTOT
      valEstremi = readCalTot(int(newYear) , int(newMonth))
      valInvFirsyM = valEstremi[0]
      valInvLastM = valEstremi[1]

      ####### Leggo i dati da TRANSAZIONI

      valTransact = readTransTot(int(newYear) , int(newMonth),'1')
      deposit=valTransact[0]
      dividen=valTransact[1]
      vendite=valTransact[2]
      rendim = ((float(valInvLastM) - float(valInvFirsyM) - deposit + dividen + vendite)/float(valInvFirsyM))*100
      rendimY=''

      #se siamo a dicembre devo calcolare la performance dell'anno scorso
      if int(newMonth) == 12:
        valYear = readCalTot(int(newYear) , '0')
        valIniYear = valYear[0]
        valFinYear = valYear[1]

        valTranYear = readTransTot(int(newYear) , '0','1')
        depositY=valTranYear[0]
        dividenY=valTranYear[1]
        venditeY=valTranYear[2]
        rendimY = ((float(valFinYear) - float(valIniYear) - depositY + dividenY + venditeY)/float(valIniYear))*100

      #preparo array finale
      arr = [[newYear,newMonth,firstDayMon,lastDayMon,valInvFirsyM.replace(to_replace='.',value=','),valInvLastM.replace(to_replace='.',value=','),deposit,dividen,vendite,rendim,rendimY,todayDateHour]]
      print(arr)
      #scrivo array
      appendRow('tab_performance!A:L',arr,newPrj)
      #aggiorno l'ultima data 
      lastDatelastday = lastDayMon
      #proseguo con il loop
      i += 1
  else:
    print("Aggiornamento non necessario")
  return 'Done'

#def calcRendAnn():
  #actualPerf = read_range('tab_performance!A:L',newPrj)
  #return 'ok'
  
def readCalTot(anno, mese):
  #Leggo il valore di mercatro del primo e dell'ultimo giorno del mese
  fulldata = read_range('tab_caltot!A:I',newPrj)
  #converto data in data
  fulldata['Data'] = pd.to_datetime(fulldata['Data'])
  #creo campi mese e anno
  fulldata['Month'] = fulldata['Data'].dt.month
  fulldata['Year'] = fulldata['Data'].dt.year
  #filtro calendar totali per il mese e anno che interessa

  if mese == '0':
    partData = fulldata[(fulldata['Year'] == anno)]
  else:
    partData = fulldata[(fulldata['Year'] == anno) & (fulldata['Month'] == mese)]

  valInvFirsyM = partData['Valore Mercato'].iloc[0].replace(to_replace=',',value='.')
  valInvLastM = partData['Valore Mercato'].iloc[-1].replace(to_replace=',',value='.')
  arr=[valInvFirsyM,valInvLastM]
  return arr

def readTransTot(anno,mese,num_port):
  transact = read_range('tab_transazioni!A:Q',newPrj) 
  transact = transact[transact['Num Portfolio'] == num_port] #solo portafoglio passato
  transact['Data operazione'] = pd.to_datetime(transact['Data operazione'], format='%d/%m/%Y')
  transact['Month'] = transact['Data operazione'].dt.month
  transact['Year'] = transact['Data operazione'].dt.year
  transact = transact.drop(columns=['Stato Database','SCADENZA','Dividendi','VALUTA','Chiave','Data operazione','prezzo acquisto','Spesa/incasso previsto'])
  transact['Spesa/incasso effettivo'] = transact['Spesa/incasso effettivo'].replace(to_replace='\.',value='',regex=True)
  transact = transact.replace(to_replace=',',value='.', regex=True)
  transact = transact.replace(to_replace='€',value='', regex=True)

  if mese == '0':
    depositDF = transact[(transact['Year'] == anno) & (transact['Tipo'] == 'ACQ')]
    dividenDF = transact[(transact['Year'] == anno) & (transact['Tipo'] == 'DIVID')]
    venditeDF = transact[(transact['Year'] == anno) & (transact['Tipo'] == 'VEND')]
  else:
    depositDF = transact[(transact['Year'] == anno) & (transact['Month'] == mese) & (transact['Tipo'] == 'ACQ')]
    dividenDF = transact[(transact['Year'] == anno) & (transact['Month'] == mese) & (transact['Tipo'] == 'DIVID')]
    venditeDF = transact[(transact['Year'] == anno) & (transact['Month'] == mese) & (transact['Tipo'] == 'VEND')]

  deposit = depositDF['Spesa/incasso effettivo'].astype(float)
  dividen = dividenDF['Spesa/incasso effettivo'].astype(float)
  vendite = venditeDF['Spesa/incasso effettivo'].astype(float)
  arr = [deposit.sum(),dividen.sum(),vendite.sum()]
  return arr


def replace_dot_with_comma(x):
  if '.' in str(x):
      return str(x).replace(to_replace='.', value=',')
  return x

#print(caldRendimento())

def changeFormatNumberPrint(numb):
  #per stampare su google sheet serve la virgola
  if(str(numb).find('.') != -1):
    numb1 = str(numb).replace('.',',')
  else:
    numb1 = numb
  return numb1
