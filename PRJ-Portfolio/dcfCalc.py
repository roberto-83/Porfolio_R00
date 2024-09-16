#calcolo DCF
#analizzo i cashflow storici
#Required rate è il rate che voglio avere come crescita
#perpetual rate-> non sarà mai piu altro del gradi di crescita di una nazione
#FCF growth rate -> crescita del cashflow
#required rate 7%
#perpetual rate 2%
#FCF growth rate = 3%

#video https://www.youtube.com/watch?v=Vi-BQx4gE3k

import yfinance as yf

aapl = yf.Ticker("aapl")
ourstandingshares = aapl.info ['shares0utstanding']#number of shares

# Assumptions:
required_rate = 0.07
perpetual_rate = 0.02
cashflowgrowthrate = 0.03

# Fetch number of shares
years = [1, 2, 3, 4]
freecashflow = [50803000,64121000,58896000,73365000] #Last 4 Years

futurefreecashflow = []
discountfactor=[]
discountedfuturefreecashflow=[]

terminalvalue = freecashflow[-1]*(1+perpetual_rate)/(required_rate-perpetual_rate)
print(terminalvalue)

for year in years:
  cashflow = freeCashflow[-1]*(1+cashflowgrowthrate)**year
  futurefreecashflow.append(cashflow)
  discountfactor.append((1+required_rate)**year)

print(discountfactor)
print(futurefreecashflow)

for i in range(0,len(years)):
  discountedfuturefreecashflow.append(futurefreecashflow[i]/discountfactor[i])

print(discountedfuturefreecashflow)

discountedterminalvalue = terminalvalue/(1+required_rate)**4  #4 perchè è calcolato sull'ultimo dei 4 anni

discountedfuturefreecashflow.append(discountedterminalvalue) #aggiungo il valore terminale sul array

#calcolo today value di tutto

todaysvalue = sum(discountedfuturefreecashflow)

fairvalue = todaysvalue*1000/ourstandingshares

print("The fair value of AAPL is ${}".format(round(fairvalue,2)))






