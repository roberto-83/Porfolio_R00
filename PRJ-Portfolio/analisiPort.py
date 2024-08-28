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
from pandas_datareader import data as web
from datetime import datetime
import matplotlib.pyplot as plt 
plt.style.use('fivethirtyeight')
#Mio codice
from functions_sheets import read_range
from settings import * #importa variabili globali
from functions_sheets import delete_range,appendRow
from settings import * #importa variabili globali

#stockStartDate='2020-01-01'

def analisiPort(stockStartDate):
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
    portfolio_0 = read_range('tab_portfolio!A:M',newPrj)
    #tolgo colonne che non mi interessano
    portfolio_1 = portfolio_0[['Tipologia','ISIN','TICKER','%Composizione']]
    #tolgo il simbolo percentuale
    portfolio_1['%Composizione'] = portfolio_1['%Composizione'].replace('%', '', regex=True)
    #cambio virgola con punto
    portfolio_1['%Composizione'] = portfolio_1['%Composizione'].replace(',', '.', regex=True)
    #converto in numero la colonna
    portfolio_1['%Composizione'] = pd.to_numeric(portfolio_1['%Composizione'])
    #divido 100
    portfolio_1['%Composizione'] = portfolio_1['%Composizione']/100
    #print(portfolio_1)
    #quindi variabili che serviranno per analisi sono
    assets_1 = portfolio_1['TICKER'].tolist()
    weights_1 = np.array(portfolio_1['%Composizione'].tolist())
    #altre variabili data

    today = datetime.today().strftime('%Y-%m-%d')

    #----------------------------------------------------
    # Divido in due parti
    #----------------------------------------------------

    #divido il dataframe - prendo solo btp, bot
    subport_1 = portfolio_1[portfolio_1['Tipologia'].isin(["BOT","BTP"])]
    #subport_1 = portfolio_1[portfolio_1['Tipologia'].isin(["BOT","BTP"])]
    subassets_1 = subport_1['TICKER'].tolist()
    #print(subport_1)

    #divido il dataframe - prendo solo p2p
    subport_3 = portfolio_1[portfolio_1['Tipologia'].isin(["P2P"])]
    #subport_1 = portfolio_1[portfolio_1['Tipologia'].isin(["BOT","BTP"])]
    subassets_3 = subport_3['TICKER'].tolist()
    #print(subport_1)

    #azioni
    subport_2 = portfolio_1[portfolio_1['Tipologia'].isin(["AZIONI","ETF-AZIONI"])]
    subassets_2 = subport_2['TICKER'].tolist()
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
    calend_tot_2['Prezzo mercato'] = calend_tot_2['Prezzo mercato'].replace(',', '.', regex=True)
    calend_tot_2['Prezzo mercato'] = pd.to_numeric(calend_tot_2['Prezzo mercato'])

    #per Criptalia devo fare un lavoro diverso
    calend_tot_3 = calend_tot_0[['Data','Ticker','Dividendo']]
    calend_tot_3 = calend_tot_3[calend_tot_1['Ticker'].isin(subassets_3)]
    calend_tot_3.set_index('Data',inplace=True)
    calend_tot_3.index = pd.to_datetime(calend_tot_3.index)
    calend_tot_3['Dividendo'] = calend_tot_3['Dividendo'].replace(',', '.', regex=True)
    calend_tot_3['Dividendo'] = pd.to_numeric(calend_tot_3['Dividendo'])

    #print(calend_tot_2)
    #print(calend_tot_2.dtypes)
    #print(calend_tot_2.index)
    #print(yf.download('RACE.MI', start=stockStartDate, end = today,progress=False)['Adj Close'])

    #----------------------------------------------------
    # Costruisico la matrice
    #----------------------------------------------------
    df = pd.DataFrame()

    #print(subassets_2)
    for stock in assets_1:
      if stock in subassets_2:   #quindi se è un etf o azione
        df[stock] = yf.download(stock, start=stockStartDate, end = today,progress=False)['Adj Close']
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
    print('Tabella dei prezzi storici')
    print(df.to_string())

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
    returns = df.pct_change()
    #tolgo i valori "inf" che sta per infinito per divisione con 0
    returns.replace([np.inf, -np.inf], 0, inplace=True)
    #print(returns)

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
    port_variance = np.dot(weights_1.T, np.dot(cov_matrix_annual,weights_1))
    print(f"La variaza del portafolgio è {port_variance}")

    #----------------------------------------------------
    # Volatilità del portafoglio = deviazione standard - rischio
    #----------------------------------------------------
    port_volatility = np.sqrt(port_variance)
    #print(f"La volatilità del portafolgio è {port_volatility}")

    #----------------------------------------------------
    # Ritorno annuale del portafoglio
    #----------------------------------------------------
    portAnnualReturn = np.sum(returns.mean() * weights_1) * 252
    #print(f"Il ritorno annualizzato del portafoglio è {portAnnualReturn}")

    #----------------------------------------------------
    # Risultato
    #----------------------------------------------------
    percent_var = str (round(port_variance,2)*100)+'%'
    percent_vols = str (round(port_volatility,2)*100)+'%'
    percent_ret = str (round(portAnnualReturn,2)*100)+'%'

    print("---- Dati mio portafoglio ----")

    print(f"Ritorno Annuo atteso {percent_ret}")
    print(f"Rischio/Volatilità Annuale {percent_vols}")
    print(f"Varianza Annuale {percent_var}")

    #----------------------------------------------------
    # Scrivo su Sheet
    #----------------------------------------------------
    listToPrint=[[today,stockStartDate,percent_ret,percent_vols,percent_ret]]
    appendRow('tab_analysis!A:E',listToPrint,newPrj)
    return 'Done Analisi Portafolgio'
