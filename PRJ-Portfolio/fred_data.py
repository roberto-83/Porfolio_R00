#utente con collegamento gmail robpol1983@gmail.com
#api-key a2d856a46ea11c3c186d0935100b4994 
#documentazione della fred qui  https://fred.stlouisfed.org/docs/api/fred/
#doc della documentazione python https://pypi.org/project/fredapi/
from fredapi import Fred
from datetime import datetime,timedelta
import time
from settings import * #importa variabili globali
from functions_sheets import delete_range,appendRow,read_range,write_range

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
    # Personal Consumption Expenditures (PCE) Excluding Food and Energy (Chain-Type Price Index)
    pce = fred.get_series_latest_release('DPCCRV1Q225SBEA')
    pce_val = pce.iloc[-1]
    pce_data = str(pce.index[-1])[0:10]
    

    list2write=[[todayDate,treasury10_data,treasury10_val,gdp_data,gdp_val,cpi_data,cpi_val,tax_rate_data,tax_rate_val,pce_data, pce_val]]
    appendRow('tab_us!A:K',list2write,newPrj)
  else:
    return 'Aggiornamento non necessario'
  return 'Done'
#print(writeMacroData())

def transfDataf(series,firstDate):
  df_1=series[series.index > firstDate]
  df = df_1.to_frame()
  #df=df.reset_index()
  df['index']=df.index
  df=df.rename(columns={0:"Val", 'index':'Date_val'})
  df=df[["Date_val","Val"]]
  df['Change']=df['Val'].pct_change().fillna(0)
  df['Date_val']=df['Date_val'].astype(str)
  return df

def writeMacroDataHistory():
  firstDate='2023-01-01'
  todayDate = datetime.today().strftime('%Y-%m-%d')
  fred = Fred(api_key='a2d856a46ea11c3c186d0935100b4994')

  #ten year treasury rate
  treasury10 = fred.get_series_latest_release('GS10')
  treasury10_DF = transfDataf(treasury10,firstDate)
  treasury10_DF=treasury10_DF.fillna(method='ffill')
  print('treasury10_DF')
  print(treasury10_DF)
  len_treasury10_DF = str(len(treasury10_DF)+1)
  listPrint01 = treasury10_DF.values.tolist()
  write_range('tab_us!B2:D'+len_treasury10_DF,listPrint01,newPrj)

  # Gross Domestic Product = prodotto interno lordo
  gdp = fred.get_series('GDP')
  gdp_DF = transfDataf(gdp,firstDate)
  gdp_DF=gdp_DF.fillna(method='ffill')
  print('gdp_DF')
  print(gdp_DF)
  len_gdp_DF = str(len(gdp_DF)+1)
  listPrint02 = gdp_DF.values.tolist()
  write_range('tab_us!E2:G'+len_gdp_DF,listPrint02,newPrj)

  # Median Consumer Price Index (MEDCPIM158SFRBCLE)	
  cpi = fred.get_series_latest_release('MEDCPIM158SFRBCLE')
  cpi_DF = transfDataf(cpi,firstDate)
  cpi_DF=cpi_DF.fillna(method='ffill')
  print('cpi_DF')
  print(cpi_DF)
  len_cpi_DF = str(len(cpi_DF)+1)
  listPrint03 = cpi_DF.values.tolist()
  write_range('tab_us!H2:J'+len_cpi_DF,listPrint03,newPrj)

  #Effective Federal Funds Rate
  tax_rate = fred.get_series_latest_release('EFFR')
  tax_rate_DF = transfDataf(tax_rate,firstDate)
  tax_rate_DF=tax_rate_DF.fillna(method='ffill')
  tax_rate_DF=tax_rate_DF.fillna(0)
  #cancello change = 0
  tax_rate_DF =tax_rate_DF[tax_rate_DF['Change'] !=0]
  print('tax_rate_DF')
  print(tax_rate_DF)
  len_tax_rate_DF = str(len(tax_rate_DF)+1)
  listPrint04 = tax_rate_DF.values.tolist()
  write_range('tab_us!K2:M'+len_tax_rate_DF,listPrint04,newPrj)

  # Personal Consumption Expenditures (PCE) Excluding Food and Energy (Chain-Type Price Index)
  pce = fred.get_series_latest_release('DPCCRV1Q225SBEA')
  pce_DF = transfDataf(pce,firstDate)
  pce_DF=pce_DF.fillna(method='ffill')
  print('pce_DF')
  print(pce_DF)
  len_pce_DF = str(len(pce_DF)+1)
  listPrint05 = pce_DF.values.tolist()
  write_range('tab_us!N2:P'+len_pce_DF,listPrint05,newPrj)

  #list2write=[[todayDate,treasury10_data,treasury10_val,gdp_data,gdp_val,cpi_data,cpi_val,tax_rate_data,tax_rate_val,pce_data, pce_val]]
  #print(list2write)
  #appendRow('tab_us!A:K',list2write,newPrj)

  return 'Done'
print(writeMacroDataHistory())

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