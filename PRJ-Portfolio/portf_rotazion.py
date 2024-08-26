#test di copilot
#dovrebbe misurare le performance di ogni settore rispetto a s&P500
#un aumento della performance può indicare  una rotazione su quel settore, una diminuzione una rotazione fuori dal settore

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

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
    'Real Estate': 'XLRE'
}

# Scarica i dati storici
data = {sector: yf.download(ticker, start='2020-01-01')['Adj Close'] for sector, ticker in sector_etfs.items()}
data = pd.DataFrame(data)

# Scarica i dati dell'indice di riferimento (S&P 500)
sp500 = yf.download('^GSPC', start='2020-01-01')['Adj Close']

# Calcola la performance relativa
relative_performance = data.divide(sp500, axis=0)

# Plot della performance relativa
relative_performance.plot(figsize=(14, 7))
plt.title('Performance Relativa dei Settori rispetto all\'S&P 500')
plt.xlabel('Data')
plt.ylabel('Performance Relativa')
plt.legend(loc='upper left')
plt.show()