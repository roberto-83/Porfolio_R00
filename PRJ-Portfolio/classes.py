from pickle import PUT
from ssl import PEM_FOOTER
from functions_sheets import read_range
from functions_sheets import write_range
from functions_sheets import delete_range
from functions_bonds import getBtpData
from functions_bonds import getBotData
from functions_stocks import getStockInfo
from functions_stocks import verifKey
from functions_etf import sectorsEtf
from functions_etf import getPriceETF
from functions_etf import getSummary
from settings import * #importa variabili globali
from currency_converter import CurrencyConverter, currency_converter
import pandas as pd
import datetime
from datetime import datetime
from datetime import timedelta
import time
import pytz
import numpy as np

from yfinance.utils import empty_earnings_dates_df
pd.options.mode.chained_assignment = None #toglie errori quando sovrascrivo un dataframe
#import yfinance as yf


class Portfolio:
  todayDate = datetime.today().strftime('%d/%m/%Y')
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")

  #todayDateHour = datetime.today().strftime('%d/%m/%Y %H:%M')
  #metodo costruttore
  def __init__(self):
    #todayDate = datetime.today().strftime('%d/%m/%Y')
    #tutte le transazioni fino ad oggi
    self.transact = Portfolio.readActiveIsinByDate(self,Portfolio.todayDate)
    #prima parte portafoglio con gli isin validi ad oggi
    self.actPort = Portfolio.calcDataPortREV2(self, self.transact)
    self.tabIsin = Portfolio.gtDataFromTabIsinREV2(self)
    #tutti i dati da tab_isin originale
    #self.allIsins = Portfolio.readListIsin(self)#occhio che è il VECCHIO !! NON LO USO!
    

  def readActiveIsinByDate(self,date):
    #Prendo gli isin attivi ad oggi, poi bisognerà ragionare sulla quantità
    transact = read_range('tab_transazioni!A:P',oldPrj)
    transact['Data operazione'] = pd.to_datetime(transact['Data operazione'], format='%d/%m/%Y')
    transact = transact[transact['Data operazione'] <= date]  
    transact = transact.drop(columns=['Stato Database','SCADENZA','Dividendi','VALUTA','Chiave','Data operazione','prezzo acquisto','Spesa/incasso previsto'])
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
    
  def getLivePrice(row):
    #funzione che mi da il prezzo a mercato dei vari asset
    #print(f'Funzione chiamata per {row}')
    if row['Asset'] == 'P2P':
      liveprice = float(row['TotInvest'])+float(row['Divid'])
    elif row['Asset'] == 'BTP' or row['Asset'] == 'BOT':
      price=getBtpData(row['Isin'])
      liveprice = float(price['pric'])
    elif row['Asset'] == 'ETF-AZIONI':
      price=getPriceETF(row['Ticker'])
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
        #appendo Settore, industria
        list2d.append([i,tick,marketCap,volume,epstrailing,epsforward,petrailing,
        peforward,pegratio,beta, earnings, ptb, book, shares, divrate, divyield,divlastval,
        divlastdate,divexdate,payout,avg52,dist52,avg200,dist200])

    #trasformo la lista in DF
    portaf2 = pd.DataFrame(list2d, columns =['Isin-JOIN','Ticker-JOIN','marketCap','volume','epstrailing','epsforward','petrailing',
        'peforward','pegratio','beta', 'earnings', 'ptb', 'book', 'shares', 'divrate', 'divyield','divlastval',
        'divlastdate','divexdate','payout','avg52','dist52','avg200','dist200']) 

    #tolgo prima riga
    #portaf2.drop(index=portaf2.index[0], axis=0, inplace=True)
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
    return 'Scritto il Portafoglio'





##################################################
  #def livePrices(ticker, asset, date):
    #prices=[]
    #if asset == 'P2P':
        #livprice = part2[4] + part2[5] #valore totale+dividendi
        #ctvMerc = part2[1] * livprice
      #elif asset == 'BTP':
        #part3 = getBtpData(portfDf.iloc[i][0])
        #livprice = float(part3['pric'])
        #ctvMerc = part2[1] * livprice /100
      #elif asset == 'ETF':
        #part3 = getPriceETF(tick)
        #livprice = part3[1]
        #ctvMerc = part2[1] * livprice
      #else:
      #live
        #test2 = histData('RACE.MI','1do')
        #fino a ieri
        #data32 = yf.download('RACE.MI','2024-05-07','2024-05-08')
        #infoStock = getStockInfo(ticker)
        #price = infoStock['currentPrice']
        #curre = infoStock['currency']
        #price1d = infoStock['prevClose']

     #return prices
######################################################
 #Tabella tab_calendar
  def updateCalendarTab(self):
    #fase 1 - leggere ultima data del foglio
    calend =  read_range('tab_calendar!A:K',newPrj)
    lastDate = calend.iloc[-1]["Data"] #get last row
    newDate = Portfolio.sumDayToDate(lastDate) #giorno che andrò a scrivere
    print(f"Sto lavorando i dati di {newDate}")
    #fase 2 - prendere le info a quella data dalle trabsazioni
    isinsDate = Portfolio.readActiveIsinByDate(self,newDate)
    #prendo solo valori attivi e unici
    isinDefin = Portfolio.transactActive(self,isinsDate)
    #DF con dati calcolati da transazioni
    portf = Portfolio.calcDataPortREV2(self,isinDefin)
    print(portf)

    ###################################################
    # per adesso non è univoco
    #mi serve avere:
    

    #forse mi conviene prendere la funzione già pronta del portafoglio e usarla qui
    #quella però ha
    #-piu dati economici che non mi servono -> snellire senza ricopiare
    #-non guarda la data-> impostare



    #print(isinsDate)
    #tolgo 
    #fase 3 - prendere tutti i dati necessari
    #fase 4 - mettere i prezzi
    #fase 5 - chiamare la funzione che scrive sui totali-> meglio fare funzione separata
    return 'updated'  
  
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

  #def calcDataPort(self, isin):   # CANCELLAAAAAAA.......................
    #calcolo i dati calcolabili da transaction come quantità, costi etc dei vari asset
    #rawData = self.transact[self.transact['ISIN']==isin]
    #inizializzo
    #qtaAcqui=0
    #spesAcqu=0
    #qtaVendi=0
    #divTotal=0
    #costiTot=0
    #Loop su dataframe
    #for i in rawData.index:
      #costiTot = costiTot + float(rawData['Costi'][i])
      #if rawData['Tipo'][i] == 'ACQ':
        #qtaAcqui = qtaAcqui + float(rawData['Quantità (real)'][i])
        #spesAcqu = spesAcqu + float(rawData['Spesa/incasso effettivo'][i])
      #elif rawData['Tipo'][i] == 'VEND':
        #qtaVendi = qtaVendi + float(rawData['Quantità (real)'][i])
      #else:
        #divTotal = divTotal + float(rawData['Spesa/incasso effettivo'][i])
    #Preparo i calcoli
    #qtaTot = (qtaAcqui+qtaVendi)
    #print(f" Quanittà toale {qtaTot}")
    #prezPond = spesAcqu/qtaAcqui
    #totInv = qtaTot*prezPond
    #return [isin,qtaTot,prezPond,prezPond,divTotal,totInv,costiTot]


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





  ################################
  #METODI PRINCIPALI - tab_isin###
  ################################
  
  def writeAllIsins(self):
    tabellaDF = Portfolio.readListIsin(self)
    tabella = tabellaDF.values.tolist()
    tabellaPrint=[]
    lastRow=str(len(tabellaDF)+1)
    for i in tabella:
      if i[4] == 'P2P':
        i.pop()
        tabellaPrint.append(i + ['P2P',i[0],i[0],'Bond','Bond','Italy','EUR'])
      elif i[4] == 'CRYPTO':
        i.pop()
        tabellaPrint.append(i + ['CRYPTO',i[0],i[0],'Crypto','Crypto','Italy','EUR'])
      elif i[4] == 'CURRENCY': 
        i.pop()
        tabellaPrint.append(i + ['CURRENCY',i[0],i[0],'Currency','Currency','Italy','EUR'])
      elif i[4] == 'BTP':
        btpData = getBtpData(i[0])
        i.pop()#tolgo asset
        i.pop()#tolgo scadenza
        tabellaPrint.append(i + [btpData['scad'],'BTP',btpData['desc'],btpData['desc'],'Bond','Bond','Italy',btpData['curr']])
      elif i[4] == 'BOT':
        botData = getBotData(i[0])
        i.pop()#tolgo asset
        i.pop()#tolgo scadenza
        tabellaPrint.append(i + [botData['scad'],'BOT',botData['desc'],botData['desc'],'Bond','Bond','Italy',botData['curr']])
      else:
        i.pop()
        genData = Portfolio.getNameStock(i[1])
        tabellaPrint.append(i + genData)
    #cancello vecchie righe
    deleteOldRows = delete_range('tab_isin!A2:K250',newPrj)
    #scrivo le nuove
    return write_range('tab_isin!A2:K'+lastRow,tabellaPrint,newPrj)

  ################################
  #METODI AGGIUNTIVI           ###
  ################################
  
  def readListIsin(self):
    tabIsins = read_range('tab_isin!A:K',oldPrj)
    tabIsinsFilt = tabIsins[tabIsins['MORNINGSTAR'] != 'INATTIVO']
    return tabIsinsFilt.filter(items=['ISIN','TICKER_YAHOO','TICKER_DATI','SCADENZA','ASSET'])
    

    ######################################QUESTA LAVORA CONSINGOLO ISIN, devo leggerre tutti gli isin che matchano il mio portafolgio.. come fare?
    #ma cosi vado anche a leggere prima tutta la tabella..
    #se lascio cosi leggo i dati uno alla volta e quindi ho meno call da fare
    #fare una funzione che legga i dati una sola volta
  #def gtDataFromTabIsin(isin):
    #estraggo i dati da tab_isin dato un isin di partenza
    #assetData = read_range('tab_isin!A:K',newPrj)
    #assetDataVal = assetData.loc[assetData['ISIN'] == isin]
    #return assetDataVal

  def gtDataFromTabIsinREV2(self):
    actPortf = self.actPort
    #estraggo i dati da tab_isin dato un isin di partenza
    assetData = read_range('tab_isin!A:K',newPrj)
    #prendo lista sin
    isintab = actPortf['Isin'].values.tolist()
    #filtro DF letto da google per avere solo gli isin attivi
    assetData[assetData.ISIN.isin(isintab)]
    return assetData
   

  #FUNZIONI AGGIUNTIVE
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
          Portfolio.verifKey(info,'currency')]
    else:
        output = [
          Portfolio.verifKey(info,'quoteType'), 
          Portfolio.verifKey(info,'shortName'),
          Portfolio.verifKey(info,'longName'),
          Portfolio.verifKey(info,'sector'),
          Portfolio.verifKey(info,'industry'),
          Portfolio.verifKey(info,'country'),
          Portfolio.verifKey(info,'currency')]
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


#MIGLIORIE
#1 - valutare se prendere il nome del titolo per il portafoglio (sulla funzione   def getTitle(row):) da  API e non da tab_isin, solo per gestire le variazioni
#2 - la funzione che sto usando sugli etf può essere usata anche per le azioni? perchè ha piu campi!
#3 - calcolo del delta price sulle obbligazioni.. ora l'ho messo fisso a 0
#4 - readListIsin va usata solo nel costruttore e salvata per poi essre richiamata. così diminuosco le chiamate  



    


