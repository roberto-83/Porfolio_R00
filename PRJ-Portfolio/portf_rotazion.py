#test di copilot
#dovrebbe misurare le performance di ogni settore rispetto a s&P500
#un aumento della performance può indicare  una rotazione su quel settore, una diminuzione una rotazione fuori dal settore

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime,timedelta

print("---------- PRIMO --------")
print("Creo un immagine con la performance relativa dei vari settori a confronto con qualle dell'SP500")
# Lista di ETF settoriali (esempio per il mercato USA)
sector_etfs = {
    'Technology': 'XLK',
    'Healthcare': 'XLV',
    'Financials': 'XLF',
    'Consumer Discretionary': 'XLY',
    'Consumer Staples': 'XLP',
    'Energy': 'XLE',
    'Industrials': 'XLI',
    'Materials': 'XLB',
    'Utilities': 'XLU',
    'Real Estate': 'XLRE',
    'Bond 10 Y':'US10.MI',
    'Bond 1-3Y':'US13.MI',
    'Bond 3-7' :'US37.MI'
}

# Scarica i dati storici
data = {sector: yf.download(ticker, start='2020-01-01',progress=False)['Adj Close'] for sector, ticker in sector_etfs.items()}
data = pd.DataFrame(data)

# Scarica i dati dell'indice di riferimento (S&P 500)
sp500 = yf.download('^GSPC', start='2024-01-01',progress=False)['Adj Close']

# Calcola la performance relativa
relative_performance = data.divide(sp500, axis=0)

# Plot della performance relativa
relative_performance.plot(figsize=(14, 7))
plt.title('Performance Relativa dei Settori rispetto all\'S&P 500')
plt.xlabel('Data')
plt.ylabel('Performance Relativa')
plt.legend(loc='upper left')
script_dir = os.path.dirname(__file__)+'/tmpFiles'
plt.savefig(script_dir+'/portfolio_rotazionale.png',  bbox_inches=0, orientation='landscape', pad_inches=0.1, dpi=100)
plt.show()

#print("---------- SECONDO --------")

# Lista di ticker rappresentativi di vari settori economici
deltadays = 60
tickers = ['XLF', 'XLK', 'XLE', 'XLY', 'XLI', 'XLV', 'XLP', 'XLU', 'XLB', 'XLRE','US10.MI','US37.MI','US13.MI']
today = datetime.today().strftime('%Y-%m-%d')
startTime = (datetime.strptime(today, '%Y-%m-%d')-timedelta(days=deltadays)).strftime('%Y-%m-%d')

# Scarica i dati storici
data = yf.download(tickers, start=startTime, end=today, group_by='ticker',progress=False)
#data['OBV'] = (data['Volume'] * ((data['Close'] - data['Open']) / data['Open'])).cumsum()

#riempio i missing al massimo a una settimana e sostituisco NaN con 0
data.ffill(limit=5, inplace=True)
data=data.fillna(0)
#print(data['XLK'].to_string())
# Funzione per calcolare il volume medio
def calculate_average_volume(ticker_data):
  return ticker_data['Volume'].mean()

def calculate_delta_volume(ticker_data):
  return ticker_data['Volume'].iloc[-1] - ticker_data['Volume'].iloc[0]

# Funzione per calcolare il rate of change (ROC) dei volumi
def calculate_volume_roc(ticker_data):
  return ticker_data['Volume'].pct_change().mean() * 100

#Calcolo  Volume On-Balance (OBV) come indicazione del titpo di volume
#se negativo significa che siamo ribassisti mentre se è positivo rialzisti
def calculate_obv(ticker_data):
  ticker_data['OBV'] = (ticker_data['Volume'] * ((ticker_data['Close'] - ticker_data['Open']) / ticker_data['Open'])).cumsum()
  return ticker_data['OBV'].mean()

def getShortNameTicker(ticker):
  tic = yf.Ticker(ticker)
  info1 = tic.info
  return info1.get('longName')

# Calcola il volume medio e il ROC per ogni settore
results = {}
for ticker in tickers:
    descr = getShortNameTicker(ticker)
    obv = calculate_obv(data[ticker])
    delta_volume = calculate_delta_volume(data[ticker])
    avg_volume = calculate_average_volume(data[ticker])
    volume_roc = calculate_volume_roc(data[ticker])
    results[ticker] = {'average_volume': avg_volume, 'volume_roc': volume_roc, 'descr':descr, 'delta_volume':delta_volume, 'on_balance_volume':obv}

# Ordina i settori per volume medio
sorted_results = sorted(results.items(), key=lambda x: x[1]['on_balance_volume'], reverse=True)

# Stampa i risultati
for sector, metrics in sorted_results:
    print(f"Settore: {sector} - {metrics['descr']}, Volume medio: {metrics['average_volume']}, Delta Volume: {metrics['delta_volume']}, ROC dei volumi: {metrics['volume_roc']:.2f}%, OBV: {metrics['on_balance_volume']:.2f}%")


#ticker1 = 'US10.MI'
#data = yf.download(ticker1, start=startTime, end=today,progress=False)

# Calcola l'OBV
#data['OBV'] = (data['Volume'] * ((data['Close'] - data['Open']) / data['Open'])).cumsum()
#print(data.to_string())
#print(data['OBV'].mean())
# Stampa i risultati
#print(data[['Close', 'Volume', 'OBV']].tail())

