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

  #metodo costruttore
  def __init__(self):
    #tutte le transazioni fino ad oggi
    self.transact = Portfolio.readActiveIsinByDate(self,Portfolio.todayDate_f)
    #prima parte portafoglio con gli isin validi ad oggi
    self.actPort = Portfolio.calcDataPortREV2(self, self.transact)
    self.tabIsin = Portfolio.gtDataFromTabIsinREV2(self)
   

  def readActiveIsinByDate(self,date):
    #Prendo gli isin attivi ad oggi, poi bisognerà ragionare sulla quantità
    transact = read_range('tab_transazioni!A:P',oldPrj)
    transact['Data operazione'] = pd.to_datetime(transact['Data operazione'], format='%d/%m/%Y')
    #print(transact[transact['Ticker'] == 'CSNDX.MI'])
    #print(transact[transact['Ticker'] == 'NKE.DE'])
    transact = transact[transact['Data operazione'] <= date]  
    #print(transact[transact['Ticker'] == 'CSNDX.MI'])
    #print(transact[transact['Ticker'] == 'NKE.DE'])
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
    print(f"Leggo il prezzo di {row['Ticker']}, asset {row['Asset']}")
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

    return portIsinCalc

  def financialsPartPort(self):
    #prendo la prima parte già creata
    portaf = Portfolio.dFPortf(self)
    #print("stampo pre portafoglio")
    #print(portaf.head())
    #creo una lista con i dati finanziari
    list2d=[]
    for i in portaf['Isin']:
      tabIsinData = self.tabIsin
      #print(tabIsinData.keys())
      tabIsinData = tabIsinData[tabIsinData['ISIN'] == i]
      print(f"lunghezza del DF {len(tabIsinData)} per isin {i}")
      if len(tabIsinData) == 0:
        list2d.append([i,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
      else:
        #print(tabIsinData)
        tick = tabIsinData['TICKER YAHOO'].iloc[0]
        #---------
        if(tabIsinData['ASSET'].iloc[0] == 'P2P' or tabIsinData['ASSET'].iloc[0] == 'ETF'):
          list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        elif tabIsinData['ASSET'].iloc[0] == 'BTP' or tabIsinData['ASSET'].iloc[0] == 'BOT':
          list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) 
        else:
          #VAI COI FINANCIALS
          #print(tick)
          try:
            infoStock = getSummary(tick)
            #sector = verifKey(infoStock['assetProfile'],'sector')
            #industry = verifKey(infoStock['assetProfile'],'industry')
            print(f"Controllo se ci sono i dati {len(infoStock['summaryDetail'])}")
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
          except:
            list2d.append([i,tick,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) 
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
    #stampo tutto il dataframe
    #print(portfin.to_string())
    #trasformo in lista
    listPrint = portfin.values.tolist()
    #lunghezza lista
    lastRowSt=str(len(listPrint)+1)
    print("stampo il portafoglio prima di scriverlo")
    print(listPrint)
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
    if row['Asset'] == 'ETF-AZIONI':
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
  def portafSettori(self):
    port = Portfolio.dFPortf(self)
    portShort = port[['Asset','Ticker','DESCRIZIONE LUNGA','peso','SETTORE']].copy()
    #portShort['Azienda']=portShort.apply(Portfolio.getCompany,axis=1 )
    #for i in portShort.iterrows():
    allSectors = pd.DataFrame()
    for i in range(len(portShort)):
      if(portShort['Asset'].loc[i] == "ETF-AZIONI"):
        #leggo i settori dell'etf
        settori = sectorsEtf(portShort['Ticker'].loc[i])
        #dato che la funzione di prima riporta i settori come chiavi li riporto come colonna
        settori['Settore_ETF'] = settori.index
        #cambio l'index che conteneva il settore
        settori=settori.reset_index()

        #costruisco il DF
        settori['Data'] = Portfolio.todayDate_f
        settori['Asset'] = portShort['Asset'].loc[i]
        settori['Ticker'] = portShort['Ticker'].loc[i]
        settori['Descrizione'] = portShort['DESCRIZIONE LUNGA'].loc[i]
        settori['Settore'] = settori['Settore_ETF'].str.upper()
        settori['Peso_Tick'] = portShort['peso'].loc[i]
        settori['Peso_singolo'] = settori[portShort['Ticker'].loc[i]]
        settori['Peso'] = portShort['peso'].loc[i]*settori[portShort['Ticker'].loc[i]]
        
        #tolgo la colonna che si chiama come il ticker
        settori = settori.drop([portShort['Ticker'].loc[i],'Settore_ETF',0], axis =1)
        #tolgo trattino
        settori['Settore']=settori['Settore'].str.replace('_',' ')
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
    return 'Done writing sectors'

################################################################################
##### TABELLA COMPOSIZIONE - PAESI
################################################################################
  def portafPaesi(self):
    port = Portfolio.dFPortf(self)
    portShort = port[['Asset','Isin','Ticker','DESCRIZIONE LUNGA','peso']].copy()
    #print(portShort.to_string)
    allCountries = pd.DataFrame()
    for i in range(len(portShort)):
      print(f"Lavoro con {portShort['Isin'].loc[i]}" )
      if(portShort['Asset'].loc[i] == "ETF-AZIONI"):  #se è etf
        #leggo i settori dell'etf
        paesidF = listEtfCountries(portShort['Isin'].loc[i])
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
################################################################################
##### TABELLA ANDAMENTO
################################################################################
  
  def readlastDate(self,tab):
    fulldata = read_range(tab+'!A:A',newPrj)
    dateSheet = fulldata['Data'].iloc[-1]
    print(f"ultima data del foglio {dateSheet} e oggi è {Portfolio.todayDate}")
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

      #sostituisco i NaN
      finalDF3['Prezzo Oggi'] = finalDF3['Prezzo Oggi'].fillna(0)
      finalDF3['Prezzo YTD'] = finalDF3['Prezzo YTD'].fillna(0)
      finalDF3['Prezzo 15gg'] = finalDF3['Prezzo 15gg'].fillna(0)
      finalDF3['Prezzo 30gg'] = finalDF3['Prezzo 30gg'].fillna(0)
      finalDF3['Prezzo 200gg'] = finalDF3['Prezzo 200gg'].fillna(0)
      #conversione colonne
      finalDF3['Prezzo Oggi'] = finalDF3['Prezzo Oggi'].replace(',','.',regex=True).astype(float)
      finalDF3['Prezzo YTD'] = finalDF3['Prezzo YTD'].replace(',','.',regex=True).astype(float)
      finalDF3['Prezzo 15gg'] = finalDF3['Prezzo 15gg'].replace(',','.',regex=True).astype(float)
      finalDF3['Prezzo 30gg'] = finalDF3['Prezzo 30gg'].replace(',','.',regex=True).astype(float)
      finalDF3['Prezzo 200gg'] = finalDF3['Prezzo 200gg'].replace(',','.',regex=True).astype(float)

      #calcolo GAP in percentuale
      finalDF3['Gap YTD']  = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo YTD'] )*100 / finalDF3['Prezzo Oggi']
      finalDF3['Gap 15gg'] = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo 15gg'])*100 / finalDF3['Prezzo Oggi']
      finalDF3['Gap 30gg'] = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo 30gg'])*100 / finalDF3['Prezzo Oggi']
      finalDF3['Gap 200gg'] = (finalDF3['Prezzo Oggi'] - finalDF3['Prezzo 200gg'])*100 / finalDF3['Prezzo Oggi']

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
  
  def getPriceYah(tick):
    #trovo i prezzi con Yahooquery
    print(f"trovo prezzo per {tick}")
    arr =[]
    fund = Ticker(tick)
    info = fund.history(period="5d")
    print(info)
    #e fallisce prendo i dati letti dal sito
    if info.empty:
      print('Leggo dati da sito yahoo')
      info = readYahooSite(tick)
      #['GB00BLD4ZL17.SG', 'CoinShares Physical Bitcoin ', '58,73', '58,22']
      arr = info
    else:
      #print(info.to_string())
      arr = [tick,'',info['close'].iloc[0],info['close'].iloc[1]]
    print(arr)

    #prezzo = info['close'].iloc[0]
    #if prezzo == 0:
      #prezzoNew = readYahooSite(tick)
      #prezzo = prezzoNew[2]
    return arr

  def getDescr(asset,isin,tick):
    #isin='IT0005273013'
    #asset='BTP'
    infoTick=[]
    #isin, ticker, descrizione, currency, prezzo, rendimen, scadenza , settore, industria, beta, pe,eps, price1D
    if(asset == 'BTP' or asset == 'BOT'):
      price=getBtpData(isin)
      #print(tick)
      #print(price)
      infoTick = [price['isin'],tick,price['desc'],price['curr'],price['pric'],price['yeld'],price['scad'],
      'Bond','Bond','','','',price['pric'],'','','']
    elif(asset == 'AZIONI' or asset == 'ETF'):
      
      stock = Ticker(tick)
      #prezzo live
      #fund = Ticker(tick)
      #info = fund.history(period="1d")
      #priceItem=info['close'].iloc[0]
      livePrice = Portfolio.getPriceYah(tick)
      #print(stock)
      #get all stock info
      #######questa va in errrore ogn tanto.. metti try catch?
      print(f"leggo dati per {tick}")
      try:
        infoStockYQ = stock.quotes[tick]
      except:
        print("ci sono problemi su chiamata API")
        infoStockYQ = {'fullExchangeName':'','trailingPE':''}
      ##################################Prendi alcuni campi da qui!!!
      infoStock = getStockInfo(tick)
      #print(infoStockYQ)
      print(f"trovo trailing PE {Portfolio.verifKey(infoStockYQ,'trailingPE')}")
      print(f"trovo 52low {Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekLow')}")
      print(f"trovo 52high {Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekHigh')}")
      infoTick = [isin,tick,infoStock['longName'],infoStock['currency'],livePrice[2],'','',
      infoStock['sector'],infoStock['industry'],infoStock['beta'],infoStock['trailingPE'],infoStock['trailingEps'],livePrice[3],
      Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekLow'),Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekHigh'),Portfolio.verifKey(infoStockYQ,'trailingPE')]
      #infoTick = [isin,tick,infoStock['longName'],infoStock['currency'],infoStock['currentPrice'],'','',
      #infoStock['sector'],infoStock['industry'],infoStock['beta'],infoStock['trailingPE'],infoStock['trailingEps'],infoStock['prevClose'],
      #Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekLow'),Portfolio.verifKey(infoStockYQ,'fiftyTwoWeekHigh'),Portfolio.verifKey(infoStockYQ,'trailingPE')]
    else:
      infoTick=[isin,tick,'','','','','','','','','','','','','','']
    return infoTick

  def whatchlist(self):
    #loop sulla pagina tab_whatchlist
    tab_watch = read_range('tab_watchlist!A:R',newPrj)
    print(tab_watch.keys())
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
      if ordin is not None:
        ordin = ordin.replace(',','.')
      else:
        ordin = 0
      print(f"Read info of {tick}")
      tickInfo = Portfolio.getDescr(asset,isin,tick)
      print(f"stampo ordin {ordin} per {tick} e prezzo {tickInfo[4]} per tick {tickInfo[2]}, valori 52 week {tickInfo[13]} e {tickInfo[14]}")
      if float(tickInfo[4]) != 0:
        percPrezz = (float(ordin) - float(tickInfo[4]))/float(tickInfo[4])
      else:
        percPrezz = 0
      #Calcolo 52 WEEK
      if asset == 'BTP':
        fiftyTwoWeek=''
        fiftyTwoWeekPerc=''
      elif float(tickInfo[13]) > 0 and float(tickInfo[14]) > 0 and float(tickInfo[4]) > 0:
          fiftyTwoWeek = str(tickInfo[13]) + ' - ' +str(tickInfo[14]) + '( '+str(round((float(tickInfo[13])+float(tickInfo[14])/2),2))+ ' )'
          fiftyTwoWeekPerc = (float(tickInfo[4])-float(tickInfo[13]))/(float(tickInfo[14]) - float(tickInfo[13]))
          deltaIeri = round( (float(tickInfo[4]) - float(tickInfo[12])) / float(tickInfo[12]),2)
      else:
        fiftyTwoWeek=''
        fiftyTwoWeekPerc=''
        deltaIeri=0
      listPrin.append([Portfolio.todayDateHour,asset,isin,tick,tickInfo[2],tickInfo[4],tickInfo[12],
      ordin,percPrezz,av,qta,tot,dOrdine,fiftyTwoWeek,fiftyTwoWeekPerc,deltaIeri,tab_watch['NOTE'][i],tickInfo[3],
      tickInfo[5],tickInfo[6],tickInfo[7],tickInfo[8],tickInfo[9],tickInfo[10],tickInfo[11] ])
      #portIsinCalc['LivePrice']=portIsinCalc.apply(Portfolio.getLivePrice,axis=1 )
    #print(len(listPrin))
    numRow = len(listPrin)+1
    #cancello vecchie righe
    deleteOldRowsWat = delete_range('tab_watchlist!A2:Y250',newPrj)
    #scrivo le nuove
    write_range('tab_watchlist!A2:Y'+str(numRow),listPrin,newPrj)
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


def replace_dot_with_comma(x):
  if '.' in str(x):
      return str(x).replace('.', ',')
  return x

#print(caldRendimento())
