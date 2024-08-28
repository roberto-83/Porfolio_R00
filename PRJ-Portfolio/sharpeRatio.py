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

stockStartDate='2020-01-01'


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
title = 'Portfolio history'
my_stocks = df 
plt.figure(figsize=(18,8), dpi=100)

for c in my_stocks.columns.values:
  plt.plot(my_stocks[c], label = c)

plt.title(title)
plt.xlabel('Date', fontsize = 6)
plt.ylabel('Price', fontsize = 6)
#plt.legend(my_stocks.columns.values, loc='upper left')
#plt.legend(my_stocks.columns.values, loc='upper center',ncol=len(my_stocks.columns))
plt.legend(my_stocks.columns.values, loc='upper center',mode = "expand", ncol = 3)
plt.tight_layout()
script_dir = os.path.dirname(__file__)+'/tmpFiles'
plt.savefig(script_dir+'/portfolio.png',  bbox_inches=0, orientation='landscape', pad_inches=0.1, dpi=100)
plt.show()

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
listToPrint=[[today]]

#----------------------------------------------------
# Ottimizza portafolgio
#----------------------------------------------------

#installa PyPortfolioOpt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
print("---- Ottimizzazione Primo metodo ----")
#----------------------------------------------------
# calcolo ritorni attesi e matrice covarianza annualizzata dei ritorni
#----------------------------------------------------

#tolgo i piu recenti
df_full = df
df = df.drop(['BOT-01G25', 'CRIPTALIA','BTP-OT53','BTP-MZ48','BTP-VALORE','RCPL.XC','5Q5.DE'], axis=1)
#print(df.to_string())
mu = expected_returns.mean_historical_return(df)
S = risk_models.sample_cov(df)

#----------------------------------------------------
# ottimizzazione per max sharp ratio
#----------------------------------------------------

ef = EfficientFrontier(mu,S)
weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()
#print(cleaned_weights)
for key, value in cleaned_weights.items():
    print(key, value)
    
results = ef.portfolio_performance(verbose = True)
#print(type(results))

#----------------------------------------------------
# 2° metodo  ottimizzazione - sharp ratio
#----------------------------------------------------
print("---- Ottimizzazione Secondo metodo ----")

from scipy.optimize import minimize

#tickers = portfolio_1['TICKER'].tolist()
weights_orig = np.array(portfolio_1['%Composizione'].tolist())

adj_close_df = df #tolto i dati non completi
#adj_close_df = df_full #compressi i btp e p2p e azioni a mercato da poco
#lista di ticker dai nomi delle colonne del DF
tickers = adj_close_df.columns.tolist()
#print("Stampo dataframe dei prezzi")
#print(adj_close_df)
#calcolo lognormal returns
log_returns = np.log(adj_close_df / adj_close_df.shift(1))
#drop missing value
log_returns = log_returns.dropna()
#print("Stampo dataframe dei ritorni")
#print(log_returns)
#matrice covarianza
cov_matrix = log_returns.cov()*252
#print(cov_matrix)
#standard deviation
def standard_deviation(weights, cov_matrix):
  variance = weights.T @ cov_matrix @ weights
  return np.sqrt(variance)

#expected return
def expected_return(weights, log_returns):
  return np.sum(log_returns.mean()*weights)*252

#sharpe ratio
def sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
  return(expected_return(weights, log_returns) - risk_free_rate) / standard_deviation(weights, cov_matrix)

#sarebbe il tasso di interesse dei bond a 10 anni
risk_free_rate = 0.02  #suppongo sia il 2%

#definisco la funzione da minimizzare
def neg_sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
  return -sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate)

constraints = {'type': 'eq', 'fun': lambda weights: np.sum(weights) -1}
bounds = [(0, 0.5) for _ in range(len(tickers))]
#metto come pesi tutto equal weighted
initial_weights = np.array([1/len(tickers)]*len(tickers))

#Ottimizzo i pesi 
optimized_results = minimize(neg_sharpe_ratio, initial_weights, args=(log_returns, cov_matrix, risk_free_rate), method='SLSQP', constraints=constraints, bounds=bounds)
optimal_weights = optimized_results.x

#display
print('Optimal weights:')
for ticker, weight in zip(tickers, optimal_weights):
  print(f"{ticker}: {weight:.4f}")

print()

optimal_portfolio_return = expected_return(optimal_weights, log_returns)
optimal_portfolio_volatility = standard_deviation(optimal_weights, cov_matrix)
optimal_sharpe_ratio = sharpe_ratio(optimal_weights, log_returns, cov_matrix, risk_free_rate)

print(f"Expected Annual Return: {optimal_portfolio_return:.4f}")
print(f"Expected Volatility: {optimal_portfolio_volatility:.4f}")
print(f"Sharpe Ratio: {optimal_sharpe_ratio:.4f}")

#----------------------------------------------------
# 3° metodo  Coletti
#----------------------------------------------------
import seaborn
print("---- Ottimizzazione Terzo metodo ----")
print(returns.to_string())
#stampo rendimenti annualizzati
#print((returns.mean()+1)**253-1)
#Correlazione
plt.figure(figsize=(23,18))
seaborn.heatmap(returns.corr(),cmap='Reds',annot=True, annot_kws={'size':12})
seaborn.set(font_scale=1.5)
script_dir = os.path.dirname(__file__)+'/tmpFiles'
plt.savefig(script_dir+'/portfolio_correlation.png',  bbox_inches=0, orientation='landscape', pad_inches=0.1, dpi=100)
plt.show()

#comincio la simulazione
quante=10000
rendimenti=returns
nomi=assets_1
dati=df_full
cov = rendimenti.cov()*100*253
medie = ((rendimenti.mean()+1)**253-1)*100
#tabella che conterrà i portafogli con piu item
tabella = pd.DataFrame(columns=["rendimento","varianza","quasi Sharpe"]+nomi)
#tabella che conterrà solo i portafogli con un solo item
tabella1 = pd.DataFrame(columns=["rendimento","varianza","quasi Sharpe"]+nomi)
for k in range(len(dati.columns)):
  w = np.zeros(len(dati.columns))
  w[k]=1.00
  w = w/sum(w)
  rend = np.dot(medie,w)
  vol = np.dot(w,np.dot(cov,w))
  tabella1.loc[k]=[rend,vol,rend/vol]+list(w*100)
for k in range(quante):
#  w = np.random.random(len(dati.columns))
  w=np.random.normal(1,0.2,len(dati.columns))
  w[w>1]=w[w>1]-1
  w = w/sum(w)
  rend = np.dot(medie,w)
  vol = np.dot(w,np.dot(cov,w))
  tabella.loc[k]=[rend,vol,rend/vol]+list(w*100)
  #if k%1000==0:
    #print(k)

#print('Tabella che contiene tutti i portafogli')
#print(tabella1.to_string())
#print(tabella.to_string())
print('Portafoglio con piu rendimento')
print(tabella["rendimento"].idxmax(),tabella.loc[tabella["rendimento"].idxmax()])

#varianza è misura della volatilità

















