#utente con collegamento gmail robpol1983@gmail.com
#api-key a2d856a46ea11c3c186d0935100b4994 
#documentazione della fred qui  https://fred.stlouisfed.org/docs/api/fred/
#doc della documentazione python https://pypi.org/project/fredapi/
from fredapi import Fred
from datetime import datetime,timedelta
import time
from settings import * #importa variabili globali
from functions_sheets import delete_range,appendRow,read_range

def readDateTabUS():
  #tabIsinsNew = read_range('tab_us!A:E',newPrj)
  todayDate = datetime.today().strftime('%Y-%m-%d')
  statusReadDf = read_range('tab_us!A:E',newPrj)
  lastDate=statusReadDf["Update"].iloc[-1]
  if(lastDate == todayDate):
    return 'Non Necessario'
  else:
    return 'ok'

#print(readDateTabUS())
def writeMacroData():
  action= readDateTabUS()
  if action == 'ok':
    todayDate = datetime.today().strftime('%Y-%m-%d')
    fred = Fred(api_key='a2d856a46ea11c3c186d0935100b4994')
    #ten year treasutry rate
    treasury10 = fred.get_series_latest_release('GS10')
    treasury10_val = round(treasury10.iloc[-1] , 3)
    treasury10_data = str(treasury10.index[-1])[0:10]
    print(f"Treasury rate 10 Y {treasury10_val} alla data {treasury10_data}")
    # Gross Domestic Product = prodotto interno lordo
    gdp = fred.get_series('GDP')
    gdp_val = gdp.iloc[-1]
    gdp_data = str(gdp.index[-1])[0:10]
    print(f"valore GDP {gdp_val} alla data  {gdp_data}")
    # Median Consumer Price Index (MEDCPIM158SFRBCLE)	
    cpi = fred.get_series_latest_release('MEDCPIM158SFRBCLE')
    cpi_val = cpi.iloc[-1]
    cpi_data = str(cpi.index[-1])[0:10]
    #Effective Federal Funds Rate
    tax_rate = fred.get_series_latest_release('EFFR')
    tax_rate_val = tax_rate.iloc[-1]
    tax_rate_data = str(tax_rate.index[-1])[0:10]

    list2write=[[todayDate,treasury10_data,treasury10_val,gdp_data,gdp_val,cpi_data,cpi_val,tax_rate_data,tax_rate_val]]
    appendRow('tab_us!A:I',list2write,newPrj)
  else:
    return 'Aggiornamento non necessario'
  return 'Done'
#print(writeMacroData())

def test1():
  fred = Fred(api_key='a2d856a46ea11c3c186d0935100b4994')

  #print(tax_rate.tail())
  #Consumer Price Index for All Urban Consumers: All Items Less Food and Energy in U.S. City Average
  #pmi = fred.get_series_latest_release('CPILFESL')
  #pmi = fred.get_series_latest_release('NAPM')
  #print(pmi.tail())
  #Inflation, consumer prices for the United States
  #inflation = fred.get_series_latest_release('FPCPITOTLZGUSA')
  #print(inflation.tail())
  
  return 'ok'
#print(test1())