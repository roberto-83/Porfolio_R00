from pickle import PUT
from ssl import PEM_FOOTER
from functions_sheets import read_range
from functions_sheets import write_range
from functions_sheets import delete_range,appendRow
from functions_bonds import getBtpData
from functions_bonds import getBotData,readEuronext,readEuronextREV2
from functions_stocks import getStockInfo
from functions_stocks import verifKey
from functions_etf import sectorsEtf
from functions_etf import getPriceETF
from functions_etf import getSummary
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
#from IPython.display import display


from yfinance.utils import empty_earnings_dates_df
pd.options.mode.chained_assignment = None #toglie errori quando sovrascrivo un dataframe
#import yfinance as yf


class Portfolio:
  todayDate = datetime.today().strftime('%d/%m/%Y')
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")

  #metodo costruttore
  def __init__(self):
    #tutte le transazioni fino ad oggi
    self.transact = Portfolio.readActiveIsinByDate(self,Portfolio.todayDate)
    #prima parte portafoglio con gli isin validi ad oggi
    self.actPort = Portfolio.calcDataPortREV2(self, self.transact)
    self.tabIsin = Portfolio.gtDataFromTabIsinREV2(self)
   

  def readActiveIsinByDate(self,date):
    #Prendo gli isin attivi ad oggi, poi bisognerà ragionare sulla quantità
    transact = read_range('tab_transazioni!A:P',oldPrj)
    transact['Data operazione'] = pd.to_datetime(transact['Data operazione'], format='%d/%m/%Y')
    transact = transact[transact['Data operazione'] <= date]  
    transact = transact.drop(columns=['Stato Database','SCADENZA','Dividendi','VALUTA','Chiave','Data operazione','prezzo acquisto','Spesa/incasso previsto'])
    #transact = transact.drop(columns=['Stato Database','SCADENZA','Dividendi','VALUTA','Chiave','prezzo acquisto','Spesa/incasso previsto'])
    #tolgo il punto su spesa e incasso
    transact['Spesa/incasso effettivo'] = transact['Spesa/incasso effettivo'].replace('\.','',regex=True)
    #tolgo il punto su qta
    transact['Quantità (real)'] = transact['Quantità (real)'].replace('\.','',regex=True)
    transact = transact.replace(',','.', regex=True)
    transact = transact.replace('€','', regex=True)
    transact = transact.sort_values(by=['Asset'])
    #metto 0 al posto dei valori vuoti nella colonna quantità
    transact['Quantità (real)'] = transact['Quantità (real)'].replace('',0)
    return transact

################################################################################
##### TABELLA DATI LIVE PORTAFOGLIO
################################################################################

  def getLivePrice(row):
    #print(f"Calcolo i prezzi live del ticker {row['Ticker']} e isin {row['Isin']}")
    #funzione che mi da il prezzo a mercato dei vari asset
    if row['Asset'] == 'P2P':
      liveprice = float(row['TotInvest'])+float(row['Divid'])
    elif row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      price=getBtpData(row['Isin'])
      liveprice = float(price['pric'])
    elif row['Asset'] == 'ETF-AZIONI':
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
    return liveprice

  def getCtvMerc(row):
    #funzione che mi calcola il controvalore a mercato
    if row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      ctvMer = (float(row['LivePrice']) * float(row['Qta']))/100
    else:
      ctvMer = float(row['LivePrice']) * float(row['Qta'])
    return ctvMer

  def getDelta(row):
    if row['Asset'] == 'AZIONI':
      infoStock = getStockInfo(row['Ticker'])
      price1d = infoStock['prevClose']
      price1d = Portfolio.calcCurren(price1d,row['CURRENCY'])
      delta = row['LivePrice'] - price1d
    elif row['Asset'] == 'ETF-AZIONI':
      price=getPriceETF(row['Ticker'])
      price1d = price[4]
      price1d = Portfolio.calcCurren(price1d,row['CURRENCY'])
      delta = row['LivePrice'] - price1d
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
    #cancello colonne che non mi servono 
    portIsinCalc = portIsinCalc.drop(columns=['COUNTRY','DESCRIZIONE BREVE','TICKER DATI','TICKER YAHOO','ISIN','ASSET'])
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

    return portIsinCalc

  def financialsPartPort(self):
    #prendo la prima parte già creata
    portaf = Portfolio.dFPortf(self)
    #creo una lista con i dati finanziari
    list2d=[]
    for i in portaf['Isin']:
      tabIsinData = self.tabIsin
      #print(tabIsinData.keys())
      tabIsinData = tabIsinData[tabIsinData['ISIN'] == i]
      tick = tabIsinData['TICKER YAHOO'].iloc[0]
      if(tabIsinData['ASSET'].iloc[0] == 'P2P' or tabIsinData['ASSET'].iloc[0] == 'ETF'):
        list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
      elif tabIsinData['ASSET'].iloc[0] == 'BTP' or tabIsinData['ASSET'].iloc[0] == 'BOT':
        list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) 
      else:
        #VAI COI FINANCIALS
        #print(tick)
        infoStock = getSummary(tick)
        #sector = verifKey(infoStock['assetProfile'],'sector')
        #industry = verifKey(infoStock['assetProfile'],'industry')
        marketCap = verifKey(infoStock['summaryDetail'],'marketCap')
        volume = verifKey(infoStock['summaryDetail'],'volume')
        epstrailing = verifKey(infoStock['defaultKeyStatistics'],'trailingEps')
        epsforward = verifKey(infoStock['defaultKeyStatistics'], 'forwardEps')
        petrailing = verifKey(infoStock['defaultKeyStatistics'],'trailingPE')
        peforward = verifKey(infoStock['defaultKeyStatistics'],'forwardPE')
        pegratio = verifKey(infoStock['defaultKeyStatistics'],'pegRatio')
        beta = verifKey(infoStock['defaultKeyStatistics'],'beta')
        earnings = verifKey(infoStock['financialData'],'earningsGrowth')
        ptb = verifKey(infoStock['defaultKeyStatistics'],'priceToBook')
        book = verifKey(infoStock['defaultKeyStatistics'],'bookValue')
        shares = verifKey(infoStock['defaultKeyStatistics'],'sharesOutstanding')
        divrate = verifKey(infoStock['summaryDetail'],'dividendRate')
        divyield = verifKey(infoStock['summaryDetail'],'dividendYield')
        divlastval = verifKey(infoStock['defaultKeyStatistics'],'lastDividendValue')
        divlastdate = verifKey(infoStock['defaultKeyStatistics'],'lastDividendDate')
        divexdate = verifKey(infoStock['summaryDetail'],'exDividendDate')
        payout = verifKey(infoStock['summaryDetail'],'payoutRatio')
        avg52 = verifKey(infoStock['summaryDetail'],'fiftyDayAverage')
        dist52=0
        avg200 = verifKey(infoStock['summaryDetail'],'twoHundredDayAverage')
        dist200=0
        divexdate=divexdate[:10]
        print(f"ticker {tick} con valore data {divexdate} e lunghezza {len(divexdate)}")
        if len(divexdate) > 2: #quindi se non è 0
          divexdate=divexdate[8:10] +'/'+divexdate[5:7]+'/'+divexdate[:4]
        #divlastdate=
        #appendo Settore, industria
        list2d.append([i,tick,marketCap,volume,epstrailing,epsforward,petrailing,
        peforward,pegratio,beta, earnings, ptb, book, shares, divrate, divyield,divlastval,
        divlastdate,divexdate,payout,avg52,dist52,avg200,dist200])

    #trasformo la lista in DF
    portaf2 = pd.DataFrame(list2d, columns =['Isin-JOIN','Ticker-JOIN','marketCap','volume','epstrailing','epsforward','petrailing',
        'peforward','pegratio','beta', 'earnings', 'ptb', 'book', 'shares', 'divrate', 'divyield','divlastval',
        'divlastdate','divexdate','payout','avg52','dist52','avg200','dist200']) 

    #concateno i due DF tramite JOIN
    result = pd.concat([portaf, portaf2], axis=1,join="inner")
    #rimuovo colonne di join
    result.drop(['Isin-JOIN','Ticker-JOIN'], axis=1,  inplace=True)
    return result

  def writePortfolio(self):
    #richianmo portafoglio
    portfin = Portfolio.financialsPartPort(self)
    #ggiungo data
    portfin['DataUpdate'] = Portfolio.todayDateHour
    #trasformo in lista
    listPrint = portfin.values.tolist()
    #lunghezza lista
    lastRowSt=str(len(listPrint)+1)
    #cancello esistente
    deleteOldRows = delete_range('tab_portfolio!A2:AR100',newPrj)
    #scrivo portafolgio
    write_range('tab_portfolio!A2:AR'+lastRowSt,listPrint,newPrj)
    #print(portfin.head())
    return 'Ho completato aggiornamento del portafoglio'


################################################################################
##### TABELLA DATI STORICI
################################################################################

  def getHistPrice(row):

    print(f"Recupero prezzo storico di {row['Ticker']} alla data {row['dataHist']}")
    #funzione che mi da il prezzo a mercato dei vari asset
    dateRead = row['dataHist']
    if row['Asset'] == 'P2P':
      histPrice = float(row['TotInvest'])+float(row['Divid'])
    elif row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      histTot = readEuronextREV2(row['Isin'],dateRead)
      histPriceDf = histTot[histTot['Date'] == dateRead]
      if len(histPriceDf) >0 :
        histPrice = histPriceDf['Close'].values[0]
      else:
        #se ci sono festività e non posso filtrare il giorno giusto prendo l'ultimo valore disponibile
        histPrice = histTot['Close'].iloc[-1] 

    elif row['Asset'] == 'AZIONI' or row['Asset'] == 'ETF-AZIONI':
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
        histPrice = prices2['Close'].iloc[-1] 
      #trovo valuta
      infoStock = getStockInfo(row['Ticker'])
      currency=infoStock['currency']
      #cambio valuta
      histPrice = Portfolio.calcCurren(histPrice,currency)
    else:
      histPrice='0'
    return histPrice

  def getHistctvMerc(row):
    ctvMerc = row['Qta']*row['HistPrice']
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
    #aggiungo prezzo storico
    portHist['HistPrice']=portHist.apply(Portfolio.getHistPrice,axis=1 )
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
    yesterday = (datetime.now()+timedelta(days=-1)).strftime('%d/%m/%Y')
    #differenza tra ultima data e ieri
    diffdate = (datetime.strptime(yesterday, "%d/%m/%Y") - datetime.strptime(lastDate, "%d/%m/%Y")).days
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
        dateSearch = (datetime.strptime(lastDate, "%d/%m/%Y")+timedelta(days=i)).strftime('%Y-%m-%d')
        histDf = Portfolio.histDf(self,dateSearch)
        #print(histDf)
        numRowsHistDf = len(histDf)
        endRow = startRow+numRowsHistDf
        #trasformo in lista
        histList = histDf.values.tolist()
        write_range('tab_calendar!A'+str(startRow)+':I'+str(endRow),histList,newPrj)
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
    mercato = prezzoMerc['Close'].iloc[0]
    rendimMerc=100*(float(mercato)-287.56)/287.56
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
    df["Quantità (real)"] = df["Quantità (real)"].replace('',0)
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
      #calcolo prezzo ponderatp e totale investito
      prezPond = spesAcq/qtaAcq
      totInv = qta*prezPond 
      #recupero ticker e asset type che mi servirà per il prezzo 
      #aggiungo nella lista solo se la quantità è diversa da zero
      if qta > 0.01:
        listAll.append([i,tab['Ticker'].iloc[0],tab['Asset'].iloc[0],round(qta,4),round(prezPond,4),round(divid,4),round(totInv,4),costi])
    #tolgo prima riga vuota
    listAll.pop(0)
    #trasformo in dataframe la lista
    dfFinal = pd.DataFrame(listAll,columns =['Isin', 'Ticker' ,'Asset','Qta','PrezzoPond','Divid','TotInvest', 'Costi'])
    return dfFinal

################################################################################
##### TABELLA ANDAMENTO
################################################################################
  
  def readlastDate(self):
    fulldata = read_range('tab_and_port!A:A',newPrj)
    dateSheet = fulldata['Data'].iloc[-1]
    #print(f"ultima data del foglio {dateSheet} e oggi è {Portfolio.todayDate}")
    if dateSheet == Portfolio.todayDate :
      status = 0 #non faccio nulla
    else:
      status = 1 #proseguo
    return status

  def readCalendar(self,dateRead):
    #Leggo i dati dal calendar
    fulldata = read_range('tab_calendar!A:I',newPrj)
    #imposto filtro
    partData = fulldata[(fulldata['Data'] == dateRead)]
    partData = partData.drop(columns=['Q.ta Incrementata','Prezzo pagato','Prezzo mercato (EUR)','Dividendo','Valore Investito','Valore Mercato'])
    return partData

  def calcAndamPort(self):
    if Portfolio.readlastDate(self) == 1:
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
      #ottengo i dataframe con i prezzi
      firstYDF = Portfolio.readCalendar(self,firstY)
      twoWeeksAgoDF = Portfolio.readCalendar(self,twoWeeksAgo)
      fourWeeksAgoDF =Portfolio.readCalendar(self,fourWeeksAgo)
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
      
      #sostituisco i NaN
      finalDF2['Prezzo Oggi'] = finalDF2['Prezzo Oggi'].fillna(0)
      finalDF2['Prezzo YTD'] = finalDF2['Prezzo YTD'].fillna(0)
      finalDF2['Prezzo 15gg'] = finalDF2['Prezzo 15gg'].fillna(0)
      finalDF2['Prezzo 30gg'] = finalDF2['Prezzo 30gg'].fillna(0)
      #conversione colonne
      finalDF2['Prezzo Oggi'] = finalDF2['Prezzo Oggi'].replace(',','.',regex=True).astype(float)
      finalDF2['Prezzo YTD'] = finalDF2['Prezzo YTD'].replace(',','.',regex=True).astype(float)
      finalDF2['Prezzo 15gg'] = finalDF2['Prezzo 15gg'].replace(',','.',regex=True).astype(float)
      finalDF2['Prezzo 30gg'] = finalDF2['Prezzo 30gg'].replace(',','.',regex=True).astype(float)

      #calcolo GAP in percentuale
      finalDF2['Gap YTD']  = (finalDF2['Prezzo Oggi'] - finalDF2['Prezzo YTD'] )*100 / finalDF2['Prezzo Oggi']
      finalDF2['Gap 15gg'] = (finalDF2['Prezzo Oggi'] - finalDF2['Prezzo 15gg'])*100 / finalDF2['Prezzo Oggi']
      finalDF2['Gap 30gg'] = (finalDF2['Prezzo Oggi'] - finalDF2['Prezzo 30gg'])*100 / finalDF2['Prezzo Oggi']

      #stampo dataframe su foglio
      numRows = len(finalDF2)+1
      arr = finalDF2.values.tolist()
      delete_range('tab_and_port!A2:K100',newPrj)
      write_range('tab_and_port!A2:K'+str(numRows),arr,newPrj) 
    else:
      print("Aggiornamento non necessario")
    return 'Done'

    
################################################################################
##### TABELLA ISIN
################################################################################

  def readDateTabIsin(self):
    tabIsinsNew= read_range('tab_isin!A:L',newPrj)
    lastDate = tabIsinsNew['UPDATE'].iloc[0]
    #print(f" Ultima data folgio {lastDate} e data oggi {Portfolio.todayDate}")
    if lastDate == Portfolio.todayDate:
      return 'Aggiornamento non Necessario'
    else:
      return 'ok'

  def writeAllIsins(self):   
    if Portfolio.readDateTabIsin(self) == 'ok':
      tabellaDF = Portfolio.readListIsin(self)
      tabella = tabellaDF.values.tolist()
      tabellaPrint=[]
      lastRow=str(len(tabellaDF)+1)
      for i in tabella:
        if i[4] == 'P2P':
          i.pop()
          tabellaPrint.append(i + ['P2P',i[0],i[0],'Bond','Bond','Italy','EUR',Portfolio.todayDate])
        elif i[4] == 'CRYPTO':
          i.pop()
          tabellaPrint.append(i + ['CRYPTO',i[0],i[0],'Crypto','Crypto','Italy','EUR',Portfolio.todayDate])
        elif i[4] == 'CURRENCY': 
          i.pop()
          tabellaPrint.append(i + ['CURRENCY',i[0],i[0],'Currency','Currency','Italy','EUR',Portfolio.todayDate])
        elif i[4] == 'BTP':
          btpData = getBtpData(i[0])
          i.pop()#tolgo asset
          i.pop()#tolgo scadenza
          tabellaPrint.append(i + [btpData['scad'],'BTP',btpData['desc'],btpData['desc'],'Bond','Bond','Italy',btpData['curr'],Portfolio.todayDate])
        elif i[4] == 'BOT':
          botData = getBotData(i[0])
          i.pop()#tolgo asset
          i.pop()#tolgo scadenza
          tabellaPrint.append(i + [botData['scad'],'BOT',botData['desc'],botData['desc'],'Bond','Bond','Italy',botData['curr'],Portfolio.todayDate])
        else:
          i.pop()
          genData = Portfolio.getNameStock(i[1])
          tabellaPrint.append(i + genData)
      #cancello vecchie righe
      deleteOldRows = delete_range('tab_isin!A2:L250',newPrj)
      #scrivo le nuove
      write_range('tab_isin!A2:L'+lastRow,tabellaPrint,newPrj)
      return "Ho completato l'aggiornamento della tabella tab_isin"
    else:
      return "aggiornamento non necessario"

   

################################################################################
##### FUNZIONI AGGIUNTIVE
################################################################################

  def readListIsin(self):
    tabIsins = read_range('tab_isin!A:L',oldPrj)
    tabIsinsFilt = tabIsins[tabIsins['MORNINGSTAR'] != 'INATTIVO']
    return tabIsinsFilt.filter(items=['ISIN','TICKER_YAHOO','TICKER_DATI','SCADENZA','ASSET'])
    
  def gtDataFromTabIsinREV2(self):
    actPortf = self.actPort
    #estraggo i dati da tab_isin dato un isin di partenza
    assetData = read_range('tab_isin!A:K',newPrj)
    #prendo lista sin
    isintab = actPortf['Isin'].values.tolist()
    #filtro DF letto da google per avere solo gli isin attivi
    assetData[assetData.ISIN.isin(isintab)]
    return assetData

  def getNameStock(ticker):
    #prendo i dati di azioni e etf per tab_isin
    #stock = yf.Ticker(tikcer)
    info = getStockInfo(ticker)
    if (Portfolio.verifKey(info,'quoteType') == 'ETF'):
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
          Portfolio.verifKey(info,'currency'),Portfolio.todayDate]
    else:
        output = [
          Portfolio.verifKey(info,'quoteType'), 
          Portfolio.verifKey(info,'shortName'),
          Portfolio.verifKey(info,'longName'),
          Portfolio.verifKey(info,'sector'),
          Portfolio.verifKey(info,'industry'),
          Portfolio.verifKey(info,'country'),
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
    newString = string.replace('_',' ').capitalize()
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
      
      ####### Leggo i dati da CALTOT
      valEstremi = readCalTot(int(newYear) , int(newMonth))
      valInvFirsyM = valEstremi[0]
      valInvLastM = valEstremi[1]

      ####### Leggo i dati da TRANSAZIONI

      valTransact = readTransTot(int(newYear) , int(newMonth))
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

        valTranYear = readTransTot(int(newYear) , '0')
        depositY=valTranYear[0]
        dividenY=valTranYear[1]
        venditeY=valTranYear[2]
        rendimY = ((float(valFinYear) - float(valIniYear) - depositY + dividenY + venditeY)/float(valIniYear))*100

      #preparo array finale
      arr = [[newYear,newMonth,firstDayMon,lastDayMon,valInvFirsyM.replace('.',','),valInvLastM.replace('.',','),deposit,dividen,vendite,rendim,rendimY,todayDateHour]]
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

  valInvFirsyM = partData['Valore Mercato'].iloc[0].replace(',','.')
  valInvLastM = partData['Valore Mercato'].iloc[-1].replace(',','.')
  arr=[valInvFirsyM,valInvLastM]
  return arr

def readTransTot(anno,mese):
  transact = read_range('tab_transazioni!A:P',oldPrj) 
  transact['Data operazione'] = pd.to_datetime(transact['Data operazione'], format='%d/%m/%Y')
  transact['Month'] = transact['Data operazione'].dt.month
  transact['Year'] = transact['Data operazione'].dt.year
  transact = transact.drop(columns=['Stato Database','SCADENZA','Dividendi','VALUTA','Chiave','Data operazione','prezzo acquisto','Spesa/incasso previsto'])
  transact['Spesa/incasso effettivo'] = transact['Spesa/incasso effettivo'].replace('\.','',regex=True)
  transact = transact.replace(',','.', regex=True)
  transact = transact.replace('€','', regex=True)

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


#print(caldRendimento())

