#calcolo DCF
#analizzo i cashflow storici
#Required rate è il rate che voglio avere come crescita
#perpetual rate-> non sarà mai piu altro del gradi di crescita di una nazione
#->è il tasso di crescita che avrà l'azienda
#-> perchè non cresca all'infinito si mette una media tra tasso inflazione e pil mondiale
#FCF growth rate -> crescita del cashflow
#required rate 7%
#perpetual rate 2%
#FCF growth rate = 3%

#video https://www.youtube.com/watch?v=Vi-BQx4gE3k

#NOTE
#si usa solo per cashflow POSITIVI
#non si usa per le aziende hyper growth o cmq flussi di cassa molto diversi
#nazioni devono dare POCHI o nessun DIVIDENDO


#PASSI: https://www.youtube.com/watch?v=7B-QnNWJ7EA
#1-prima mi trovo le percentuali di crescita dei flussi anno su anno
#2-faccio la media delle percentuali 
#stima
#il terminal value sarà il valore alla fine dei 10 anni
#la stima si ottiene facendo l'ultimo cashfow*(1 + tasso medio trovato prima) idem per tutti gli altri fino al terminal value
#terminal value = ultimo anno0 stimato * (1+perpetual growrth rate)/(tasso rendim atteso - perpetua growth rate)

#stima valore presente dei flussi di cassa
#terminal value / (1+tasso rendimento)^num anni
#idem per tutti gli altri valori stimati per attualizzarli

#sommo i flussi di cassa
#aggiungo il cash e tolgo il debito (da yahho finance) bilancio "liquidità toale"= CASH e "debito corrente+"Debito a lungo termine" per DEBITO

#Ora equity value = cash+flussi di cassa - devito
#azioni in circolazione
#quindi prezzo per azione = fair value = equity/num azioni circolazione

#prendo prezzo di mercato
#delta = prezzo per azione / prezzo corrente -1


import yfinance as yf

def calcFairValue(tick):
  # Assumptions:
  required_rate = 0.07
  perpetual_rate = 0.02
  cashflowgrowthrate = 0.03

  ticker = yf.Ticker(tick)
  #trovo numero di azioni
  ourstandingshares = ticker.info['sharesOutstanding']
  symbol = ticker.info['symbol']
  #leggo i cashflow degli ultimi 4 anni
  cashDataFrame = ticker.get_cashflow()#leggo cashflow
  freecashflowYF = ticker.get_cashflow().loc['FreeCashFlow']#prendo solo la riga del cashflow totale
  freecashflowList=freecashflowYF.to_list()#trasformo in lista 
  freecashflowList.pop()#e tolgo ultimo valroe che è sempre NaN
  print(freecashflowList)
  freecashflow=[]
  years=[]
  contat=0
  #divido per 1000 e creo lista degli anni di storico 
  for i in freecashflowList:
    contat = contat+1
    freecashflow.append(i/1000)
    years.append(contat)

  futurefreecashflow = []
  discountfactor=[]
  discountedfuturefreecashflow=[]

  #calcolo terminal value
  terminalvalue = freecashflow[-1]*(1+perpetual_rate)/(required_rate-perpetual_rate)
  print(f"Il Terminal Value per il ticker {symbol} sarà: {terminalvalue}")

  #attualizzo i prezzi
  for year in years:
    cashflow = freecashflow[-1]*(1+cashflowgrowthrate)**year
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
  fairvalue0 = round(fairvalue,2)
  print("Il fair value di {symbol} è {fairvalue0}")

  return fairvalue0

print(calcFairValue("RACE.MI"))

#######################################################
# formula valore intrinseco con graham
# V = EPS x (8.5 + 2g) x 4.4 /Y
#dove
#V = intrinsic value
#EPS earning per share
#8.5 = P/E base per una azienda non growth
#g= tasso di crescita per i prossimi 5 anni
#4.4 =  rendimento medio dei corporate bonds rating AAA
#Y=attuale rendimento dei corporate bond rating AAA




#def fairvalueGraham(tic):




