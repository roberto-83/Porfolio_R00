import yfinance as yf
from stock_functions import verifKey 
from stock_functions import getStockInfo


test1=getStockInfo('RACE.MI')
#print
for key,value in test1.items():
  print(key, ":",value )

