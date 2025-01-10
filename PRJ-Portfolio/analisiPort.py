#ottimizza portafoglio
#https://www.youtube.com/watch?v=9fjs8FeLMJk

#sharpe ratio  = (rendimento del portafoglio in un periodo - tasso privo di rischio (tasso btp breve termine) )/ deviazione standard del portafoglio
#Ad esempio, se il rendimento medio del tuo portafoglio è del 10%, il tasso privo di rischio è del 2%, e la deviazione standard del portafoglio è del 5%, il calcolo sarà:
#Sharpe ratio = 0,1-0,02 / 0,05 = 1,6

####### RENDIMENTO MIO PORTAFOGLIO
import os
import pandas as pd
import numpy as np
import yfinance as yf
#from pandas_datareader import data as web
from datetime import datetime
#import matplotlib.pyplot as plt 
#plt.style.use('fivethirtyeight')
#Mio codice
from functions_sheets import read_range
from functions_stocks import getStockInfo
from settings import * #importa variabili globali
from functions_sheets import delete_range,appendRow,write_range
from settings import * #importa variabili globali
import fear_and_greed

#stockStartDate='2020-01-01'
#print(yf.download('CSSPX.MI', start='2019-08-16', end = '2024-01-01',progress=False)['Adj Close'].to_string())

#leggo ultima data
def readLastDate():
    todayDate = datetime.today().strftime('%Y-%m-%d')
    tabIsinsNew= read_range('tab_analysis!A:G',newPrj)
    numLastRow=len(tabIsinsNew)+1
    #print(tabIsinsNew.head())
    if len(tabIsinsNew) != 0: #caso in cui tabella sia vuota
      lastDate = tabIsinsNew['Data calcolo'].iloc[-1]
      #print(f" Ultima data folgio {lastDate} e data oggi {Portfolio.todayDate}")
      if lastDate == todayDate:
        #in questo caso la funzione è già stata lanciata ma aggiorno i dati di mercato
        datiMercato = getMarketData()
        vix_prev_close = datiMercato[0]
        fear_greed_idx = datiMercato[1]
        fear_greed_desc = datiMercato[2]
        listToPrint=[[vix_prev_close,fear_greed_desc,fear_greed_idx]]
        #write_range('tab_portfolio!A2:AS'+numLastRow,listToPrint,newPrj)
        write_range('tab_analysis!H'+str(numLastRow)+':J'+str(numLastRow),listToPrint,newPrj)
        return 'Aggiornamento non Necessario'
        #return 'ok'
      else:
        return 'ok'
    else:
      return 'ok'


def readMyPort(num_port):
  portfolio_0 = read_range('tab_portfolio!A:N',newPrj)
  portfolio_0 = portfolio_0[portfolio_0['Num Port'] == num_port] #solo portafoglio specifico
  #tolgo colonne che non mi interessano
  portfolio_1 = portfolio_0[['Asset','Isin','Ticker','%Composizione']]
  #tolgo il simbolo percentuale
  #portfolio_1['%Composizione'] = portfolio_1['%Composizione'].replace('%', '', regex=True)
  portfolio_1['%Composizione'].replace(to_replace='%',value='', regex=True, inplace=True)
  #cambio virgola con punto
  #portfolio_1['%Composizione'] = portfolio_1['%Composizione'].replace(',', '.', regex=True)
  portfolio_1['%Composizione'].replace(to_replace=',', value='.', regex=True, inplace=True)
  #converto in numero la colonna
  portfolio_1['%Composizione'] = pd.to_numeric(portfolio_1['%Composizione'])
  #divido 100
  portfolio_1['%Composizione'] = portfolio_1['%Composizione']/100
  return portfolio_1

def readMyPort2(num_port):
  portfolio_0 = read_range('tab_portfolio!A:N',newPrj)
  portfolio_0 = portfolio_0[portfolio_0['Num Port'] == num_port] #solo portafoglio specifico
  #tolgo colonne che non mi interessano
  portfolio_1 = portfolio_0[['Asset','Isin','Ticker','Totale Investito','Controvalore Mercato']]
  #tolgo il simbolo percentuale
  #portfolio_1['%Composizione'] = portfolio_1['%Composizione'].replace('%', '', regex=True)
  portfolio_1['Totale Investito'].replace(to_replace='€', value='', regex=True, inplace=True)
  portfolio_1['Controvalore Mercato'].replace(to_replace='€', value='', regex=True, inplace=True)
  #cambio virgola con punto
  portfolio_1['Totale Investito'].replace(to_replace='\.', value='', regex=True, inplace=True)
  portfolio_1['Controvalore Mercato'].replace(to_replace='\.', value='', regex=True, inplace=True)
  portfolio_1['Totale Investito'].replace(to_replace=',', value='.', regex=True, inplace=True)
  portfolio_1['Controvalore Mercato'].replace(to_replace=',', value='.', regex=True, inplace=True)
  #converto in numero la colonna
  portfolio_1['Totale Investito'] = pd.to_numeric(portfolio_1['Totale Investito'])
  portfolio_1['Controvalore Mercato'] = pd.to_numeric(portfolio_1['Controvalore Mercato'])

  #divido 100
  #portfolio_1['%Composizione'] = portfolio_1['%Composizione']/100
  return portfolio_1

def getMarketData():
  vix_prev_close = getStockInfo('^VIX')['previousClose']
  fear_greed = fear_and_greed.get()
  #fear_greed_idx = str(fear_greed[1]).upper() + " ("+str(round(fear_greed[0],2))+")"
  fear_greed_idx = round(fear_greed[0],2)
  fear_greed_desc = fear_greed[1].upper()
  return [vix_prev_close,fear_greed_idx,fear_greed_desc]

def analisiPort(stockStartDate,num_port):
    readLastDateVar = readLastDate()
    if readLastDateVar == 'ok':
      #-----------------------
      #voglio calcolare rendimento e sharp ratio
      #per farlo mi serve il portafolgio di oggi ma con tutti i dati storici possibili
      #per azioni e etf non è un problema ma per i btp  e bot e p2p si quindi:
      #-Prendo il mio portafolgio con i pesi
      #-Lo divido in due subpart per avere distinzione con i btp
      #-per i btp prendo il foglio "calendar con i prezzi storici"
      #-Alla fine metto tutto insieme su un unica matrice
      #---------------------------

      #----------------------------------------------------
      # Leggo portafoglio
      #----------------------------------------------------
      portfolio_1 = readMyPort(num_port)
      today = datetime.today().strftime('%Y-%m-%d')
      #test profondità storica ticker
      #print(yf.download('SWDA.MI', start=stockStartDate, end = today,progress=False)['Adj Close'])
      #print(yf.download('GOOG', start=stockStartDate, end = today,progress=False)['Adj Close'])
      
      #sostituisco RCP
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["RCPL.XC"], "RCP.L")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["LCWD.MI"], "SWDA.MI")
      #portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["BITC.SW"], "WBIT")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["BITC.SW"], "BTC-EUR")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["5Q5.DE"], "SNOW")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["BOOK.VI"], "BKNG")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["GOOA.VI"], "GOOG")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["EMAE.MI"], "CSEMAS.MI")
      

      
      #print(portfolio_1)
      #quindi variabili che serviranno per analisi sono
      assets_1 = portfolio_1['Ticker'].tolist()
      #pos = assets_1.index('RCPL.XC')
      #assets_1 = list(map(lambda x: x.replace('RCPL.XC', 'RCP.L'), assets_2))
      #assets_1 = list(map(lambda x: x.replace('RCPL.XC', '1IH.F'), assets_2))
      weights_1 = np.array(portfolio_1['%Composizione'].tolist())
      #print(weights_1)
      #altre variabili data

      

      #----------------------------------------------------
      # Divido in due parti
      #----------------------------------------------------

      #divido il dataframe - prendo solo btp, bot
      subport_1 = portfolio_1[portfolio_1['Asset'].isin(["BOT","BTP"])]
      #subport_1 = portfolio_1[portfolio_1['Tipologia'].isin(["BOT","BTP"])]
      subassets_1 = subport_1['Ticker'].tolist()
      #print(subport_1)

      #divido il dataframe - prendo solo p2p
      subport_3 = portfolio_1[portfolio_1['Asset'].isin(["P2P"])]
      #subport_1 = portfolio_1[portfolio_1['Tipologia'].isin(["BOT","BTP"])]
      subassets_3 = subport_3['Ticker'].tolist()
      #print(subport_1)

      #azioni
      subport_2 = portfolio_1[portfolio_1['Asset'].isin(["AZIONI","ETF-AZIONI","ETC"])]
      subassets_2 = subport_2['Ticker'].tolist()
      
      #print(subport_2)

      #----------------------------------------------------
      # Calcolo i prezzi storici di BTP e altro che non posso trovare in yf
      #----------------------------------------------------
      #tutto il calendar
      calend_tot_0 = read_range('tab_calendar!A:I',newPrj)
      #solo colonne che mi servono
      calend_tot_1 = calend_tot_0[['Data','Ticker','Prezzo mercato']]
      #filtro solo per BTP, BOT e P2P
      calend_tot_2 = calend_tot_1[calend_tot_1['Ticker'].isin(subassets_1)]
      #imposto la data come indice
      calend_tot_2.set_index('Data',inplace=True)
      #indice in formato datetime
      calend_tot_2.index = pd.to_datetime(calend_tot_2.index)
      calend_tot_2['Prezzo mercato'] = calend_tot_2['Prezzo mercato'].replace(to_replace=',', value='.', regex=True)
      calend_tot_2['Prezzo mercato'] = pd.to_numeric(calend_tot_2['Prezzo mercato'])

      #per Criptalia devo fare un lavoro diverso
      calend_tot_3 = calend_tot_0[['Data','Ticker','Dividendo']]
      calend_tot_3 = calend_tot_3[calend_tot_1['Ticker'].isin(subassets_3)]
      calend_tot_3.set_index('Data',inplace=True)
      calend_tot_3.index = pd.to_datetime(calend_tot_3.index)
      calend_tot_3['Dividendo'] = calend_tot_3['Dividendo'].replace(to_replace=',', value='.', regex=True)
      calend_tot_3['Dividendo'] = pd.to_numeric(calend_tot_3['Dividendo'])

      #print(calend_tot_2)
      #print(calend_tot_2.dtypes)
      #print(calend_tot_2.index)
      
     

      #----------------------------------------------------
      # Costruisico la matrice
      #----------------------------------------------------
      df = pd.DataFrame()
      #print(assets_1)
      #print(yf.download('SNOW', start=stockStartDate, end = today,progress=False)['Adj Close'])
      #print(yf.download('BTCE.SW', start=stockStartDate, end = today,progress=False)['Adj Close'])
      #print(subassets_2)
      for stock in assets_1:
        if stock in subassets_2:   #quindi se è un etf o azione
          df[stock] = yf.download(stock, start=stockStartDate, end = today,progress=False)['Adj Close']
          #print(stock)
          #print(yf.download(stock, start=stockStartDate, end = today,progress=False)['Adj Close'])
        elif stock in subassets_1:  #quindi se è bot o btp
          priceItem = calend_tot_2[calend_tot_2['Ticker'] == stock]
          df[stock] = priceItem.drop('Ticker', axis=1)
        elif stock in subassets_3: #quindi se è p2p
          priceItem = calend_tot_3[calend_tot_3['Ticker'] == stock]
          df[stock] = priceItem.drop('Ticker', axis=1)
        else:
          df[stock] = 0 

      #riempio i missing al massimo a una settimana e sostituisco NaN con 0
      df.ffill(limit=5, inplace=True)
      df=df.fillna(0)
      print('Stampo la matrice del mio portafoglio da usare per le prossime analisi')
      #print(df)
      #print('Tabella dei prezzi storici')
      print(df.to_string())

      #----------------------------------------------------
      # Drop qualche colonna
      #----------------------------------------------------
      #Trovo il numero di colonna del dato che voglio togliere (parte da zero)
      ##tick1='BOT-01G25'
      ##col_index01 = df.columns.get_loc(tick1)
      #Tolgo colonna anche da array dei pesi
      ##weights_2 = np.delete(weights_1, col_index01)
      #tolgo anche da dataframe dei prezzi
      ##df.drop([tick1], axis=1,inplace=True)
      #print(weights_f)
      ##tick2='BTP-VALORE'
      ##col_index02 = df.columns.get_loc(tick2)
      ##weights_3 = np.delete(weights_2, col_index02)
      ##df.drop([tick2], axis=1,inplace=True)

      ##tick3='BTP-MZ48'
      ##col_index03 = df.columns.get_loc(tick3)
      ##weights_4 = np.delete(weights_3, col_index03)
      ##df.drop([tick3], axis=1,inplace=True)

      ##tick4='BTP-OT53'
      ##col_index04 = df.columns.get_loc(tick4)
      ##weights_5 = np.delete(weights_4, col_index04)
      ##df.drop([tick4], axis=1,inplace=True)

      ##tick5='CRIPTALIA'
      ##col_index05 = df.columns.get_loc(tick5)
      ##weights_f = np.delete(weights_5, col_index05)
      ##df.drop([tick5], axis=1,inplace=True)
      weights_f=weights_1

      #----------------------------------------------------
      # Calcolo la data piu vecchia
      #----------------------------------------------------
      mask = (df != 0).all(axis=1)
      data = df.index[mask]
      earliestDate = str(data[0])[0:10]
      #print(earliestDate)

     

      #----------------------------------------------------
      # Salvo Grafico su tmpFiles
      #----------------------------------------------------
      #title = 'Portfolio history'
      #my_stocks = df 
      #plt.figure(figsize=(18,8), dpi=100)

      #for c in my_stocks.columns.values:
      #  plt.plot(my_stocks[c], label = c)

      #plt.title(title)
      #plt.xlabel('Date', fontsize = 6)
      #plt.ylabel('Price', fontsize = 6)
      #plt.legend(my_stocks.columns.values, loc='upper left')
      #plt.legend(my_stocks.columns.values, loc='upper center',ncol=len(my_stocks.columns))
      #plt.legend(my_stocks.columns.values, loc='upper center',mode = "expand", ncol = 3)
      #plt.tight_layout()
      #script_dir = os.path.dirname(__file__)+'/tmpFiles'
      #plt.savefig(script_dir+'/portfolio.png',  bbox_inches=0, orientation='landscape', pad_inches=0.1, dpi=100)
      #plt.show()

      #----------------------------------------------------
      # Mostro i ritorni giornalieri
      #----------------------------------------------------
      #returns = df.pct_change()
      log_returns = np.log(1+df.pct_change())
      returns = log_returns
      #tolgo i valori "inf" che sta per infinito per divisione con 0
      returns.replace([np.inf, -np.inf], 0, inplace=True)
      #print('###################### MATRICE RITORNI ##################')
      #print(returns.to_string())

      #----------------------------------------------------
      # Matrice covarianza annualizzata
      #----------------------------------------------------
      #252 sono i trading days
      cov_matrix_annual = returns.cov()*252
      #print(cov_matrix_annual)

      #----------------------------------------------------
      # Varianza del portafoglio
      #----------------------------------------------------
      #.T serve per transporre
      port_variance = np.dot(weights_f.T, np.dot(cov_matrix_annual,weights_f))
      print(f"La variaza del portafolgio è {port_variance}")

      #----------------------------------------------------
      # Volatilità del portafoglio = deviazione standard - rischio
      #----------------------------------------------------
      port_volatility = np.sqrt(port_variance)
      #print(f"La volatilità del portafolgio è {port_volatility}")

      #----------------------------------------------------
      # Ritorno annuale del portafoglio
      #----------------------------------------------------
      portAnnualReturn = np.sum(returns.mean() * weights_f) * 252
      #print(f"Il ritorno annualizzato del portafoglio è {portAnnualReturn}")

      #----------------------------------------------------
      # Sharpe Ratio
      #----------------------------------------------------
      #qui mancherebbe il risk free rate da aggiungere...
      risk_free=0.02 #considero risk free 1%
      print(f"faccio {portAnnualReturn} meno {risk_free} e poi diviso {port_volatility}")
      sharpe_ratio_calc = (portAnnualReturn - risk_free) / port_volatility
      #----------------------------------------------------
      # Risultato
      #----------------------------------------------------
      percent_var = str(round(port_variance,2)*100)+'%'
      percent_vols = str(round(port_volatility,2)*100)+'%'
      percent_ret = str(round(portAnnualReturn,2)*100)+'%'
      sharpe_ratio = round(sharpe_ratio_calc,2)
      

      print("---- Dati mio portafoglio ----")

      print(f"Ritorno Annuo atteso {percent_ret}")
      print(f"Rischio/Volatilità Annuale {percent_vols}")
      print(f"Varianza Annuale {percent_var}")
      print(f"Sharpe Ratio {sharpe_ratio}")
      #CAGR??? (compound annual growth rate)
      #----------------------------------------------------
      # Leggo altri indici
      #----------------------------------------------------
    
      datiMercato = getMarketData()
      vix_prev_close = datiMercato[0]
      fear_greed_idx = datiMercato[1]
      fear_greed_desc = datiMercato[2]

      #----------------------------------------------------
      # Scrivo su Sheet
      #----------------------------------------------------
      listToPrint=[[today,earliestDate,percent_ret,percent_vols,percent_ret,sharpe_ratio, risk_free,vix_prev_close,fear_greed_desc,fear_greed_idx]]
      appendRow('tab_analysis!A:J',listToPrint,newPrj)
      return 'Done Analisi Portafolgio'
    else:
      return 'Aggiornamento non necessario'

################################################################################
def analisiPortWithBTP(stockStartDate,num_port):
  portfolio_1 = readMyPort(num_port)
  today = datetime.today().strftime('%Y-%m-%d')
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["RCPL.XC"], "RCP.L")
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["LCWD.MI"], "SWDA.MI")
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["BITC.SW"], "BTC-EUR")
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["5Q5.DE"], "SNOW")
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["BOOK.VI"], "BKNG")
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["GOOA.VI"], "GOOG")
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["EMAE.MI"], "CSEMAS.MI")
  portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["1BLK.MI"], "BLK")
  assets_1 = portfolio_1['Ticker'].tolist()
  weights_1 = np.array(portfolio_1['%Composizione'].tolist())
  #----------------------------------------------------
  # Divido in due parti
  #----------------------------------------------------

  #divido il dataframe - prendo solo btp, bot
  subport_1 = portfolio_1[portfolio_1['Asset'].isin(["BOT","BTP"])]
  subassets_1 = subport_1['Ticker'].tolist()

  #azioni
  subport_2 = portfolio_1[portfolio_1['Asset'].isin(["AZIONI","ETF-AZIONI","ETC"])]
  subassets_2 = subport_2['Ticker'].tolist()

  #divido il dataframe - prendo solo p2p
  subport_3 = portfolio_1[portfolio_1['Asset'].isin(["P2P"])]
  subassets_3 = subport_3['Ticker'].tolist()

  #----------------------------------------------------
  # Calcolo i prezzi storici di BTP e altro che non posso trovare in yf
  #----------------------------------------------------
  #tutto il calendar
  calend_tot_0 = read_range('tab_calendar!A:I',newPrj)
  #solo colonne che mi servono
  calend_tot_1 = calend_tot_0[['Data','Ticker','Prezzo mercato']]
  #filtro solo per BTP, BOT e P2P
  calend_tot_2 = calend_tot_1[calend_tot_1['Ticker'].isin(subassets_1)]
  #imposto la data come indice
  calend_tot_2.set_index('Data',inplace=True)
  #indice in formato datetime
  calend_tot_2.index = pd.to_datetime(calend_tot_2.index)
  calend_tot_2['Prezzo mercato'] = calend_tot_2['Prezzo mercato'].replace(to_replace=',', value='.', regex=True)
  calend_tot_2['Prezzo mercato'] = pd.to_numeric(calend_tot_2['Prezzo mercato'])

  #INTEGRO i prezzi con i dati storici che mi sono salvato 
  #leggo dati storici
  storicData= read_range('tab_storici_btp!A:C',newPrj)
  storicData.set_index('Data',inplace=True)
  storicData.index = pd.to_datetime(storicData.index+' 00:00:00+00:00', utc=True))
  storicData['Prezzo mercato'] = storicData['Prezzo mercato'].replace(to_replace=',',value='.',regex=True)
  storicData['Prezzo mercato'] = pd.to_numeric(storicData['Prezzo mercato'])
  
  #print(storicData)

  #unisco i due dataframe
  result = pd.concat([calend_tot_2, storicData])
  result.index = pd.to_datetime(result.index+' 00:00:00+00:00', utc=True))
  result=result.sort_index()#riordino indice
  result=result.drop_duplicates(subset=['Ticker', 'Prezzo mercato'], keep='last')
  #result = pd.merge(calend_tot_2, storicData, how="outer", on=["Data","Ticker"])
  #print(result.to_string())



  #----------------------------------------------------
  # Calcolo i prezzi storici di Criptalia
  #----------------------------------------------------
  calend_tot_3 = calend_tot_0[['Data','Ticker','Dividendo']]
  calend_tot_3 = calend_tot_3[calend_tot_1['Ticker'].isin(subassets_3)]
  calend_tot_3.set_index('Data',inplace=True)
  calend_tot_3.index = pd.to_datetime(calend_tot_3.index+' 00:00:00+00:00', utc=True)
  calend_tot_3['Dividendo'] = calend_tot_3['Dividendo'].replace(to_replace=',', value='.', regex=True)
  calend_tot_3['Dividendo'] = pd.to_numeric(calend_tot_3['Dividendo'])
  calend_tot_3=calend_tot_3.rename(columns={"Dividendo": "Prezzo mercato"})
  print('stampo criptalia')
  print(calend_tot_3)
  #----------------------------------------------------
  # Costruisico la matrice
  #----------------------------------------------------
  df = pd.DataFrame()
  #print(assets_1)
  #print(yf.download('SNOW', start=stockStartDate, end = today,progress=False)['Adj Close'])
  #print(yf.download('BTCE.SW', start=stockStartDate, end = today,progress=False)['Adj Close'])
  #print(subassets_2)
  for stock in assets_1:
    if stock in subassets_2:   #quindi se è un etf o azione
      df[stock] = yf.download(stock, start=stockStartDate, end = today,progress=False)['Close']
    elif stock in subassets_1:  #quindi se è bot o btp
      priceItem = result[result['Ticker'] == stock]
      df[stock] = priceItem.drop('Ticker', axis=1)
    elif stock in subassets_3: #quindi se è p2p
      priceItem = calend_tot_3[calend_tot_3['Ticker'] == stock]
      print('############ priceItem di P2P')
      priceItem = priceItem.drop('Ticker', axis=1)
      print(priceItem)
      print('------------- colonne')
      print(priceItem.dtypes)
      print('------------- Indice')
      print(priceItem.index)
      #df[stock] = priceItem.drop('Ticker', axis=1)
      df[stock] = priceItem
      print('df[stock] P2P')
      print(df[stock])
      print(df.index)
    else:
      df[stock] = 0 
  dfsfgdsffdg
  #riempio i missing al massimo a una settimana e sostituisco NaN con 0
  df.ffill(limit=5, inplace=True)
  df=df.fillna(0)
  print('Stampo la matrice del mio portafoglio CON BTP')
  print(df)
  #print('Tabella dei prezzi storici')
  #print(df.to_string())
  weights_f=weights_1
  #----------------------------------------------------
  # Calcolo la data piu vecchia
  #----------------------------------------------------
  #axis 0 è riga mentre axis 1 è colonna
  mask = (df != 0).all(axis=1)
  print('stampo mask')
  print(mask)
  data = df.index[mask]
  print("controllo questo errore... data[0] è")
  print(data[0])
  earliestDate = str(data[0])[0:10]
  
  #----------------------------------------------------
  # Mostro i ritorni giornalieri
  #----------------------------------------------------
  log_returns = np.log(1+df.pct_change())
  returns = log_returns
  #tolgo i valori "inf" che sta per infinito per divisione con 0
  returns.replace([np.inf, -np.inf], 0, inplace=True)
  cov_matrix_annual = returns.cov()*252
  port_variance = np.dot(weights_f.T, np.dot(cov_matrix_annual,weights_f))
  port_volatility = np.sqrt(port_variance)
  portAnnualReturn = np.sum(returns.mean() * weights_f) * 252
  #----------------------------------------------------
  # Sharpe Ratio
  #----------------------------------------------------
  #qui mancherebbe il risk free rate da aggiungere...
  risk_free=0.02 #considero risk free 1%
  print(f"faccio {portAnnualReturn} meno {risk_free} e poi diviso {port_volatility}")
  sharpe_ratio_calc = (portAnnualReturn - risk_free) / port_volatility
  #----------------------------------------------------
  # Risultato
  #----------------------------------------------------
  percent_var = str(round(port_variance,2)*100)+'%'
  percent_vols = str(round(port_volatility,2)*100)+'%'
  percent_ret = str(round(portAnnualReturn,2)*100)+'%'
  sharpe_ratio = round(sharpe_ratio_calc,2)

  return [earliestDate,percent_var,percent_vols,percent_ret,sharpe_ratio]

#funzione principale
def analisiPort2(stockStartDate,num_port):
    #TODO
    #prima faccio sharpe ratio con i pesi iniziali, poi con i pesi attuali e poi duplico considerando anche i btp e p2p
    readLastDateVar = readLastDate()
    if readLastDateVar == 'ok':
      
      #----------------------------------------------------
      # Leggo portafoglio
      #----------------------------------------------------
      portfolio_1 = readMyPort2(num_port)
      today = datetime.today().strftime('%Y-%m-%d')

      ##TOLGO BTP e P2P  (~è il negato..)
      list1 = ['BOT', 'BTP','P2P']
      portfolio_1=portfolio_1[~portfolio_1['Asset'].isin(list1)]

      #sostituisco valori per avere piu storico..
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["RCPL.XC"], "RCP.L")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["LCWD.MI"], "SWDA.MI")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["BITC.SW"], "BTC-EUR")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["5Q5.DE"], "SNOW")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["BOOK.VI"], "BKNG")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["GOOA.VI"], "GOOG")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["EMAE.MI"], "CSEMAS.MI")
      portfolio_1["Ticker"] = portfolio_1["Ticker"].replace(["1BLK.MI"], "BLK")

      #calcolo il totale investito    
      sum_investito = portfolio_1['Totale Investito'].sum()
      sum_controvalore = portfolio_1['Controvalore Mercato'].sum()
      print(f"Totale investito {sum_investito} e totale controvalore {sum_controvalore}")
      #aggiungo i pesi corretti in base al valore investito (da provare anche con valore di mercato.. perchè le pesature cambiano... FASE 2)
      portfolio_1['Composizione_iniz'] = portfolio_1['Totale Investito']/sum_investito
      portfolio_1['Composizione_oggi'] = portfolio_1['Controvalore Mercato']/sum_controvalore
      print(f"Somma pesatura totale inizio {portfolio_1['Composizione_iniz'].sum()}")
      print(f"Somma pesatura totale fine {portfolio_1['Composizione_oggi'].sum()}")
      #print(portfolio_1)
      
      #LISTA DI ASSET
      assets_1 = portfolio_1['Ticker'].tolist()
      #LISTA DI PESI
      weights_iniz = np.array(portfolio_1['Composizione_iniz'].tolist())
      weights_oggi = np.array(portfolio_1['Composizione_oggi'].tolist())
      #print(weights_1)
          

      #----------------------------------------------------
      # Costruisico la matrice
      #----------------------------------------------------
      df = pd.DataFrame()
      #scarico dati storici
      for stock in assets_1:
        #print(f'aggiungo al df la stock {stock}')
        df[stock] = yf.download(stock, start=stockStartDate, end = today,progress=False)['Close']
        #cerco gli split
        stockSplitsVariable = yf.Ticker(stock).actions #mi da dividend e stock split
        #tolgo la colonna dei dividendi
        stockSplitsVariable = stockSplitsVariable.drop(['Dividends'], axis=1)
        #tolgo i valori a zero
        stockSplitsVariable=stockSplitsVariable[stockSplitsVariable['Stock Splits'] !=0]
        #print(f"Lo stock {stock} ha avuto uno stock split:")
        #print(stockSplitsVariable)
        if not stockSplitsVariable.empty:
          print(f"Lo stock {stock} ha avuto uno stock split:")
          print(stockSplitsVariable)
        #else:
         #print(f"Lo stock {stock} non ha avuto stock split nei dati storici disponibili.")
      #print(df)
      
      #riempio i missing al massimo a una settimana e sostituisco NaN con 0
      df.ffill(limit=5, inplace=True)
      df=df.fillna(0)
    
      #cerco la data in cui tutte le colonne sono diverse da zero
      first_valid_date = df[(df != 0).all(axis=1)].index.min()
      print(f'Data in cui filtro il dataframne {first_valid_date}')
      df=df[df.index>first_valid_date]
      print('Stampo la matrice del mio portafoglio da usare per le prossime analisi')
      print(df.to_string())
      
    

      #----------------------------------------------------
      # Calcolo la data piu vecchia
      #----------------------------------------------------
      mask = (df != 0).all(axis=1)
      data = df.index[mask]
      earliestDate = str(data[0])[0:10]
      #print(earliestDate)

     

      #----------------------------------------------------
      # Salvo Grafico su tmpFiles
      #----------------------------------------------------
      #title = 'Portfolio history'
      #my_stocks = df 
      #plt.figure(figsize=(18,8), dpi=100)

      #for c in my_stocks.columns.values:
      #  plt.plot(my_stocks[c], label = c)

      #plt.title(title)
      #plt.xlabel('Date', fontsize = 6)
      #plt.ylabel('Price', fontsize = 6)
      #plt.legend(my_stocks.columns.values, loc='upper left')
      #plt.legend(my_stocks.columns.values, loc='upper center',ncol=len(my_stocks.columns))
      #plt.legend(my_stocks.columns.values, loc='upper center',mode = "expand", ncol = 3)
      #plt.tight_layout()
      #script_dir = os.path.dirname(__file__)+'/tmpFiles'
      #plt.savefig(script_dir+'/portfolio2.png',  bbox_inches=0, orientation='landscape', pad_inches=0.1, dpi=100)
      #plt.show()
    
      #----------------------------------------------------
      # Mostro i ritorni giornalieri
      #----------------------------------------------------
      #returns = df.pct_change()
      log_returns = np.log(1+df.pct_change())
      returns = log_returns
      #tolgo i valori "inf" che sta per infinito per divisione con 0
      returns.replace([np.inf, -np.inf], 0, inplace=True)
      #print('###################### MATRICE RITORNI ##################')
      #print(returns.to_string())

      #----------------------------------------------------
      # Matrice covarianza annualizzata
      #----------------------------------------------------
      #252 sono i trading days
      cov_matrix_annual = returns.cov()*252
      #print(cov_matrix_annual)
 
      #----------------------------------------------------
      # Varianza del portafoglio     
      #----------------------------------------------------
      #.T serve per transporre weights_iniz
      port_variance_iniz = np.dot(weights_iniz.T, np.dot(cov_matrix_annual,weights_iniz))
      port_variance_oggi = np.dot(weights_oggi.T, np.dot(cov_matrix_annual,weights_oggi))
      print(f"La variaza del portafolgio iniziale è {port_variance_iniz} mentre oggi è {port_variance_oggi}")

      #----------------------------------------------------
      # Volatilità del portafoglio = deviazione standard - rischio
      #----------------------------------------------------
      port_volatility_iniz = np.sqrt(port_variance_iniz)
      port_volatility_oggi = np.sqrt(port_variance_oggi)
      #print(f"La volatilità del portafolgio è {port_volatility}")

      #----------------------------------------------------
      # Ritorno annuale del portafoglio
      #----------------------------------------------------
      portAnnualReturn_iniz = np.sum(returns.mean() * weights_iniz) * 252
      portAnnualReturn_oggi = np.sum(returns.mean() * weights_oggi) * 252
      #print(f"Il ritorno annualizzato del portafoglio è {portAnnualReturn}")

      #----------------------------------------------------
      # Sharpe Ratio
      #----------------------------------------------------
      #qui mancherebbe il risk free rate da aggiungere...
      risk_free=0.02 #considero risk free 1%
      print(f"faccio {portAnnualReturn_iniz} meno {risk_free} e poi diviso {port_volatility_iniz}")
      print(f"faccio {portAnnualReturn_oggi} meno {risk_free} e poi diviso {port_volatility_oggi}")
      sharpe_ratio_calc_iniz = (portAnnualReturn_iniz - risk_free) / port_volatility_iniz
      sharpe_ratio_calc_oggi = (portAnnualReturn_oggi - risk_free) / port_volatility_oggi
      #----------------------------------------------------
      # Risultato
      #----------------------------------------------------
      percent_var_iniz = str(round(port_variance_iniz,2)*100)+'%'
      percent_vols_iniz = str(round(port_volatility_iniz,2)*100)+'%'
      percent_ret_iniz = str(round(portAnnualReturn_iniz,2)*100)+'%'
      sharpe_ratio_iniz = round(sharpe_ratio_calc_iniz,2)

      percent_var_oggi = str(round(port_variance_oggi,2)*100)+'%'
      percent_vols_oggi = str(round(port_volatility_oggi,2)*100)+'%'
      percent_ret_oggi = str(round(portAnnualReturn_oggi,2)*100)+'%'
      sharpe_ratio_oggi = round(sharpe_ratio_calc_oggi,2)
      

      print("---- Dati mio portafoglio ----")

      print(f"Ritorno Annuo atteso inizio {percent_ret_iniz} mentre ad oggi {percent_ret_oggi}")
      print(f"Rischio/Volatilità Annuale inizio {percent_vols_iniz} mentre ad oggi {percent_vols_oggi}")
      print(f"Varianza Annuale inizio {percent_var_iniz} mentre ad oggi {percent_var_oggi}")
      print(f"Sharpe Ratio inizio {sharpe_ratio_iniz} mentre ad oggi {sharpe_ratio_oggi}")
      #CAGR??? (compound annual growth rate)
      #----------------------------------------------------
      # Leggo altri indici
      #----------------------------------------------------
    
      datiMercato = getMarketData()
      vix_prev_close = datiMercato[0]
      fear_greed_idx = datiMercato[1]
      fear_greed_desc = datiMercato[2]

      #----------------------------------------------------
      # Scrivo su Sheet
      #----------------------------------------------------
      #Leggo i dati del portafoglio con anche i btp
      valueFullPort = analisiPortWithBTP(stockStartDate,num_port)

      listToPrint=[[today,earliestDate,percent_ret_iniz,percent_vols_iniz,
      percent_ret_iniz,sharpe_ratio_iniz, risk_free,
      vix_prev_close,fear_greed_desc,fear_greed_idx,
      percent_ret_oggi,percent_vols_oggi,percent_ret_oggi,sharpe_ratio_oggi,
      valueFullPort[0],valueFullPort[1],valueFullPort[2],valueFullPort[3],valueFullPort[4]]]

      appendRow('tab_analysis!A:S',listToPrint,newPrj)
      return 'Done Analisi Portafoglio'
    else:
      return 'Aggiornamento non necessario'
###################################################
################
#Analisi con quantstats che sarebbe bello ma solo per singolo ticker, non per portafoglio
#################
#import quantstats as qs 

#stock = qs.utils.download_returns('RACE.MI')
#print(stock)
#stampo i possibili metodi
#print(dir(stock))
#sharpe_ratio  = qs.stats.sharpe(stock)
#print(sharpe_ratio)

def testQuantStat():
  portfolioFull = readMyPort()
  #tolgo BTP e P2P
  subport = portfolioFull[portfolioFull['Tipologia'].isin(["AZIONI","ETF-AZIONI"])]
  portfolio = subport[['TICKER','%Composizione']]
  portfolio['%Composizione'] = portfolio['%Composizione'].round(2)
  #print(portfolio.dtypes)
  portDict = portfolio.to_dict('split')
  listDict = portDict['data']
  dicTickers=dict(listDict)
  #print(dicTickers)
  #print(type(dicTickers))
  
  #ora che ho i miei ticker (senza BTP) creo il mio index con quantstat
  #, period='10y'
  portf = qs.utils.make_index(dicTickers,rebalance=None)
  #report html comparando con LCWD
  qs.reports.html(portf, "LCWD.MI", output=os.path.dirname(__file__)+"/tmpFiles/quantstatPortReport.html")

  return 'Done'
#print(testQuantStat()) 
#print(analisiPort('2020-01-01',1))


#voglio preparare i dati per lanciare il colab delle analisi del portafoglio
def gcolabAnalysis():
  #voglio i ticker e il valore comprato  
  portfolio_0 = read_range('tab_portfolio!A:M',newPrj)
  #tolgo colonne che non mi interessano
  portfolio_1 = portfolio_0[['Asset','Ticker','Totale Investito']]
  #tolgo il simbolo euro
  portfolio_1['Totale Investito'] = portfolio_1['Totale Investito'].replace('€', '', regex=True)
  #cambio virgola con punto
  portfolio_1['Totale Investito'].replace('\.', '', regex=True, inplace=True)
  portfolio_1['Totale Investito'].replace(',', '.', regex=True, inplace=True)
  #converto in numero la colonna
  portfolio_1['Totale Investito'] = pd.to_numeric(portfolio_1['Totale Investito'])
  #tolgo bot, btp e p2p
  portfolio_2=portfolio_1.loc[portfolio_1['Asset'].isin(['AZIONI','ETF-AZIONI'])]
  #print(portfolio_2)
  print('Lista ticker')
  print(portfolio_2['Ticker'].to_list())
  print('Lista valori')
  print(portfolio_2['Totale Investito'].to_list())

print(gcolabAnalysis())