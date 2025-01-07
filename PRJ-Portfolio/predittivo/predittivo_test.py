#teoria
#https://www.youtube.com/watch?v=siUthKPkdQk
#esempio machine learning 
#https://www.youtube.com/watch?v=7YDWaTKtCdI
#corso https://www.youtube.com/watch?v=MRm5sBfdBBQ&list=PLcFcktZ0wnNmOcf5qgqp29K4fiG3N8-ia

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import math
import yfinance as yf

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from scipy import stats
from scipy.stats import kurtosis, skew


TickerRead = 'RACE.MI'
prices = yf.download(TickerRead,progress=False)
price_data = prices['Close']
print(price_data)
print(price_data.dtypes)
#new_column_names = {'RACE.MI':'' }
price_data=price_data.dropna()


#SONO QUI
#https://www.youtube.com/watch?v=W2hXbqnrUyY&list=PLcFcktZ0wnNmOcf5qgqp29K4fiG3N8-ia&index=17




#import statsmodels.api as sm

#from sklearn.metrics import mean_squared_error
#from statsmodels.tsa.ar_model import AR
#import seaborn as sns
#import yfinance as yf

#

#leggo dati storici
#
#pricesClose = prices['Close']
#print(pricesClose)


#plt.rcParams['figure.figsize'] = [12, 9]

#df = pd.read_csv('EURUSD.csv',sep='\t', index_col='Date')

#df = pricesClose
#df.index = pd.to_datetime(df.index)
#df.sort_index(inplace=True)
#df = df.resample('W').last()
#series = df['Close']
#print(series)