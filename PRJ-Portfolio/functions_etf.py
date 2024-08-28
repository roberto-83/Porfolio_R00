#uso libreria  yahooquery perchè dovrebbe avere tutti i settori
#guida qui https://yahooquery.dpguthrie.com
#https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_sector_weightings

from yahooquery import Ticker
import yfinance as yf
from functions_stocks import verifKey
import pandas as pd
import datetime
from datetime import datetime,timedelta
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pathlib import Path
import os
import shutil
from io import StringIO

#import openpyxl
#from openpyxl.styles.colors import WHITE, RGB 
#from xlrd import open_workbook
#test nuova funzione
#from functions_sheets import read_range,appendRow
#from settings import * #importa variabili globali
#import calendar
#import pytz

def getPriceETF(ticker):
  todayDate = datetime.today().strftime('%d/%m/%Y')
  fund = Ticker(ticker)
  #errore qui:
  livePriceDf = fund.history(period="1d")
  print(f"lunghezza history {len(livePriceDf)}")
  #print(livePriceDf)
  if(len(livePriceDf) > 0):
    #print(livePriceDf.head())
    #livePrice = livePriceDf.iloc[0][3] #uso prezzo cloe e non close adjusted
    livePrice = livePriceDf.iloc[0]['close'] #uso prezzo cloe e non close adjusted
    datePrice = livePriceDf.index[0][1]
    print(f"Analizzo ticker {ticker} ")
    try:
      tickInfo = fund.quotes[ticker]
      print(f"Analizzo ticker {ticker} il risultato è lungo {len(tickInfo)}")
      curre = tickInfo['currency']
      price1d = fund.quotes[ticker]['regularMarketPreviousClose']
      output=[ticker, livePrice,datePrice,curre,price1d]
    except: #MEGLIO lasciare solo yFINANCE?? anzichè Yahooquery che da sempre errori??
      stock = yf.Ticker(ticker)
      tickInfo = stock.info
      curre = verifKey(tickInfo,'currency')
      price1d=verifKey(tickInfo,'previousClose')
      output=[ticker, livePrice,datePrice,curre,price1d]

  else:
    output=[ticker, 0, todayDate, 'EUR', 0]
  return output

def getSummary(ticker):
  fund = Ticker(ticker)
  #datas = fund.quotes[ticker]
  #asset_prof = fund.asset_profile[ticker]
  #calendar = fund.calendar_events[ticker]
  #summary_detail = fund.summary_detail[ticker]
  all_modules = fund.all_modules[ticker]
  return all_modules

def sectorsEtf(ticker):
  #lista di settori di un etf
  fund = Ticker(ticker)
  try:
    fund_df = fund.fund_sector_weightings
    fund_df_desc = fund_df.sort_values(by=ticker, ascending=False)
    return fund_df_desc
  except:
    #return  pd.DataFrame() #dataframe vuoto
    return  pd.DataFrame({ticker:'0'},index=['0']) #dataframe vuoto

#########################################
####API di ETFDB
####https://pypi.org/project/etfpy/
###ha solo alcuni ETF e ritona sempre forbidden.. forse problema temporaneo
########################################
#from etfpy import ETF, load_etf, get_available_etfs_list
def testEtfPy():
  etfs = get_available_etfs_list()
  print(etfs)
  #read data
  EtfData = load_etf('SPY')
  print(EtfData.info)
  return 'ok'
#print(testEtfPy('CSSPX'))

#########################################
####API di FINANCE DATABASE
####https://pypi.org/project/financedatabase/#technical-analysis-of-biotech-etfs
### serve API da https://site.financialmodelingprep.com/pricing-plans?couponCode=jeroen
## serve per fare analisio cross diversi strumenti , quindi sono tutte chiamate di ricerca dati
#########################################
#import financedatabase as fd
def testFInance(ticker):
  etfs = fd.ETFs()
  print(etfs)  
  return 'Done'

#########################################
####API di FINANCE TOOLKIT (fratello di quello sopra)
####https://github.com/JerBouma/FinanceToolkit
###non vedo country etf.. 
## 
#########################################
#import mstarpy
import pandas as pd

def testapi():
  response = mstarpy.search_funds(term="technology", field=["Name", "fundShareClassId", "GBRReturnM12"], country="us", pageSize=40, currency ="USD")

  df = pd.DataFrame(response)
  print(df.head())

#print(testapi())

#########################################
####LEGGO da ExtraETF
####https://extraetf.com/it/stock-profile/US79466L3024
#########################################

def listEtfCountries(isin):
  URL="https://extraetf.com/it/etf-profile/"+isin+"?tab=components"
  #print(URL)
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("enable-automation")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--dns-prefetch-disable")
  chrome_options.add_argument("--disable-gpu")

  driverExt = webdriver.Chrome( options=chrome_options)
  driverExt.get(URL)
  #print("5 sec wait")
  time.sleep(5)
  listCountry=[]
  i = 1
  while i < 30:
    try:
      country = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-etf-profile/div[2]/div/app-blur-wrapper/div/div/div/app-tab-components/div/app-top-data-table[2]/div/div[2]/div/div[2]/div/div['+str(i)+']/div[2]/div[1]/div/div/span').get_attribute("innerText")
      weight = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-etf-profile/div[2]/div/app-blur-wrapper/div/div/div/app-tab-components/div/app-top-data-table[2]/div/div[2]/div/div[2]/div/div['+str(i)+']/div[3]').get_attribute("innerText")
      weight = weight.replace('%','').strip()
      weight = weight.replace(',','.')
      #print(f"Stato: '{country1}' con il peso di {weight1}")
      if(len(country) > 0):
        listCountry.append([isin,country,weight])
      else:
        break
    except:
      #end loop
      break
    i+=1
  #converto in dataframe
  #print(len(listCountry))
  countries = pd.DataFrame(listCountry, columns=['isin','Country','Peso_country'])
  #print(len(countries))
  #print(countries.to_string())
  return countries




#print(listEtfCountries('IE00B466KX20'))

#############################################
#Sempre da extraEtf prendo il paese delle azioni
#############################################

def listStocksCountries(isin):
  if(isin =='US29355A1079_1'):
    isin = 'US29355A1079'

  URL="https://extraetf.com/it/stock-profile/"+isin
  #print(URL)
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("enable-automation")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--dns-prefetch-disable")
  chrome_options.add_argument("--disable-gpu")

  if(isin == 'GB0007366395'):
    return [isin, 'REGNO UNITO', 100]
  else:
    driverExt = webdriver.Chrome( options=chrome_options)
    driverExt.get(URL)
    time.sleep(5)
    country = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-stock-profile/div[1]/div[1]/div[2]/span[1]/img').get_attribute("title")
    #print(country)
    return [isin, country, 100]


#print(listStocksCountries('GB0007366395'))
      ##########################################
  #lista di settori di un etf
  #etf = yf.Ticker(ticker)

  # Ottieni la composizione dell'ETF
  #holdings = etf.fund_holdings
  #print(holdings)
  # Filtra i paesi
  #countries = holdings['Country'].value_counts()
  #print(countries)

  ##fund = Ticker(ticker)
  ##try:
    #fund_df = fund.fund_sector_weightings
    #fund_df_desc = fund_df.sort_values(by=ticker, ascending=False)
    ##fund_df = fund.fund_holding_info
    ##print(fund_df[ticker]['holdings'])
    ##return fund_df
  ##except:
    #return  pd.DataFrame() #dataframe vuoto
    ##return  pd.DataFrame({ticker:'0'},index=['0']) #dataframe vuoto


#print(sectorsEtf('RACE.MI'))#risulta 0


def readHoldings():
  #EMAE.MI
  #CSNDX.MI
  #CSSPX.MI
  #XDWS.MI
  #EPRA.MI
  #GLUX.MI
  #LCWD.MI
  link='https://www.amundietf.it/it/privati/products/equity/amundi-index-ftse-epra-nareit-global-ucits-etf-dr-c/lu1437018838'
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')
  #CARTELLA DOWNLOAD
  #nome file corrente
  #print('File name :    ', os.path.basename(__file__))
  #percorso cartella attuale
  #print('Directory Name:     ', os.path.dirname(__file__))
  actualPath = os.path.dirname(__file__)
  prefs = {"download.default_directory" :actualPath+"/tmpFiles/"}
  chrome_options.add_experimental_option("prefs",prefs)
  driver = webdriver.Chrome( options=chrome_options)
  driver.get(link)
  #massimizzo la finestra
  driver.maximize_window()
  #time.sleep(5)
  #dfs = pd.read_html(driver.page_source)
  #nome ETF
  #print('Nome ETF')
  #print(driver.find_element(By.XPATH,'/html/body/main/div/amundi-product-page-widget/div/product-page-component/div/amundi-product-page-header-section/div/section[2]/div[2]/div[1]/div[1]/div[1]/div[2]/h1').text)
  #time.sleep(5)
  #ckick su "investitore privato"
  ##print('investitore privato click')
  ##print(driver.find_element(By.XPATH,'/html/body/div[2]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[2]/div[2]/button').click())
  ##time.sleep(2)
  ##print('investitore privato click conferma')
  ##print(driver.find_element(By.XPATH,'/html/body/div[2]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div[3]/div/div[2]/div/button[2]').click())
  ##time.sleep(10)
  ##print('testo2')
  ##print(driver.find_element(By.XPATH,'/html/body/main/div/amundi-product-page-widget/div/product-page-component/div/amundi-product-page-holding-section/section/section/div[1]/div/div[2]/p').text)
  time.sleep(5)
  pathLink='/html/body/main/div/amundi-product-page-widget/div/product-page-component/div/amundi-product-page-holding-section/section/section/div[1]/div/div[3]/div/a/span'
  #scarico file
  linkETF = driver.find_element(By.XPATH,pathLink)
  driver.execute_script("arguments[0].click();", linkETF)
  time.sleep(5)  
  #linkETF.click()
  driver.close()
  openFileDF = openFile()
  print(openFileDF)
  #print(linkETF)
  #histBtpExt = dfsExt[22]



def openFile():
  Initial_path=os.path.dirname(__file__)+"/tmpFiles/"
  filename = max([Initial_path + f for f in os.listdir(Initial_path)],key=os.path.getctime)
  #print(filename)
  #import xlrd
  #workbook = xlrd.open_workbook(filename)
  #import logging
  #logging.basicConfig(level=logging.DEBUG)
  #logger = logging.getLogger(__name__)
  #rb = open_workbook(filename)
  #wb = xlsxwriter.Workbook(filename)
  #import  asposecells  
  #import  jpype 
  #from asposecells.api import Workbook
  #jpype.startJVM() 
  #RGB.__set__ = custom_rgb_set
  #workbook = Workbook(filename)
  #workbook.save(Initial_path+"test.xls")  
  #jpype.shutdownJVM()
  #workbook = openpyxl.load_workbook(filename)
  #print(workbook)

  #dezippo il file excel
  import zipfile
  with zipfile.ZipFile(filename, 'r') as zip_ref:
    zip_ref.extractall(Initial_path)
  #ora devo aprire due file
  #xl/worksheets/sheet1.xml per le celle
  #xl/sharedStrings.xml per i valori
  from bs4 import BeautifulSoup
  #with open(Initial_path+'xl/worksheets/sheet1.xml', 'r') as f:
   # data = f.read()
  #Bs_data = BeautifulSoup(data, "lxml")
  #b_unique = Bs_data.find_all('unique')
  with open(Initial_path+'xl/worksheets/sheet1.xml', 'r') as f:
    data = f.read()
  Bs_data = BeautifulSoup(data, "xml")
  b_unique = Bs_data.find_all('sheetData')
  #loop per ogni row
  #offset=5
  #i=1
  #while i < offset:
    #b_name = Bs_data.find('row', {'r':i})
    #print(b_name)
    #print(f"Riga : {i} valore stampo {b_name.get_text()}")
    #i=i+1
  #block = [row.get_text() for row in Bs_data.find_all(row)]
  for i in Bs_data.find_all('sheetData'):
    rows = i.find_all('row')
    #print(rows)
    for a in rows:
      righe = a.find_all('c')
      print(righe)#riga intera
      #print(righe[0])#primo elemento
      #print(righe[0]['r'])#primo attributo
        #for b in righe:
          #values = b.find_all('v')
          #print(values)
      #print(righe['r'])
      #print(a.find_all('c').attrs)

#####  https://saturncloud.io/blog/converting-xml-to-python-dataframe-a-comprehensive-guide/

    #print(f"Riga nuova: {i}")
  #rows = Bs_data.find('row')
  #print(rows)
  #import xml.etree.ElementTree as ET
  #print(Initial_path+'xl/worksheets/sheet1.xml')
  #mytree = ET.parse(Initial_path+'xl/worksheets/sheet1.xml')
  #myroot = mytree.getroot()
  #print(myroot[5].tag)
  #print(myroot[5].tag)
 
  #for x in mytree.findall('row'):
    #item =x.find('item').text
    #price = x.find('price').text
    #print(x)

  #try:
  #book = openpyxl.load_workbook(filename, read_only=True)
  #except ValueError as e:
       # if e.args[0] == 'Colors must be aRGB hex values':
        #    __old_rgb_set__(self, instance, WHITE)  # Change color here

  #except Exception as e:
    #logger.exception(e)
    #print(f"{type(e)}: {e}")
  #book = openpyxl.load_workbook(filename, keep_xml_links=True)
  #sheet=book['Titoli detenuti dal fondo']
  #print(f"Maximum rows: {shhet.max_row}")
  #pd.read_excel(filename, engine='openpyxl')
  #import xlrd
  #book = xlrd.open_workbook(filename)
  #df = pd.read_excel(filename,sheet_name='Titoli detenuti dal fondo',skiprows=range(1,17), usecols="H:H")
  #print(df)


#df3 = getSummary('5Q5.DE')
#print(f" Settore: {df3['assetProfile']['sector']}")
#print(f" Industria: {df3['assetProfile']['industry']}")
#print(f" MarketCap: {df3['summaryDetail']['marketCap']}")
#df = sectorsEtf('EMBE.MI')
#df1 = sectorsEtf('LCWD.MI')
#df1 = getPriceETF('GLUX.MI')
#print(df.keys())
#print(df.index)
#print(df)
#print(df3)
#percentuale
#print(df['XDWS.MI'].iloc[0])
#print(df.index[0])
#dfList = df.values.tolist()
#print(dfList)


#print(type(sectorsEtf('GLUX.MI')))
#print(sectorsEtf('GLUX.MI').keys())
#chiavi sono il ticker e "Name" per il nome del settore
#estraggo la prima percentuale
#print(sectorsEtf('GLUX.MI')['GLUX.MI'].iloc[0])
#print(sectorsEtf('GLUX.MI')['GLUX.MI'].iloc[1:1])
#estraggo il primo settore
#print(sectorsEtf('GLUX.MI')[0].iloc[0])

#print(sectorsEtf('GLUX.MI')['GLUX.MI'].head(1))

#Prendo n_esimo campo
#print(fund.fund_sector_weightings.iloc[0])
#print(fund.fund_sector_weightings.iloc[1])
#chiavi
#print(fund.fund_sector_weightings.keys())


#TEST API
#https://finnhub.io/docs/api/authentication
#roberto, robpol1983#gmail.com e Zucchetti1!
#API KEY cpule6pr01qj8qq19rs0cpule6pr01qj8qq19rsg
#limit 60 al minuto??, in caso da uno specifico errore 429
def testapiFinnhub():
  #da valutare ma cmq ETF Holdings
  import finnhub
  #descrizione qui https://github.com/Finnhub-Stock-API/finnhub-python
  # Setup client
  finnhub_client = finnhub.Client(api_key="cpule6pr01qj8qq19rs0cpule6pr01qj8qq19rsg")
  print(finnhub_client.etfs_holdings('SPY'))
 

