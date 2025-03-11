#uso libreria  yahooquery perchè dovrebbe avere tutti i settori
#guida qui https://yahooquery.dpguthrie.com
#https://yahooquery.dpguthrie.com/guide/ticker/modules/#fund_sector_weightings

from yahooquery import Ticker
import yfinance as yf
from functions_stocks import verifKey
import requests 
from bs4 import BeautifulSoup 
import pandas as pd
import datetime
from datetime import datetime,timedelta
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from pathlib import Path
import os
import shutil
from io import StringIO
import subprocess



#import openpyxl
#from openpyxl.styles.colors import WHITE, RGB 
#from xlrd import open_workbook
#test nuova funzione
#from functions_sheets import read_range,appendRow
#from settings import * #importa variabili globali
#import calendar
#import pytz

def getPriceETF_OLD(ticker):#provo a riscriverla..
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

def getPriceETF(ticker):
  todayDate = datetime.today().strftime('%d/%m/%Y')
  #fund = Ticker(ticker)
  #try:
  #livePriceDf = fund.history(period="1d")
  #print(livePriceDf)
  #    print(f"Yahooquery, lunghezza history {len(livePriceDf)}")
  #    if(len(livePriceDf) > 0): #se ho uno storico
  #livePrice = livePriceDf.iloc[0]['close'] #uso prezzo close e non close adjusted
  #datePrice = livePriceDf.index[0][1]
  #      tickInfo = fund.quotes[ticker]
  #      print(f"Analizzo ticker {ticker} il risultato è lungo {len(tickInfo)}")
  #      curre = tickInfo['currency']
  #      price1d = fund.quotes[ticker]['regularMarketPreviousClose']
  #      output=[ticker, livePrice,datePrice,curre,price1d]
  #    else: #se non ho uno storico
  #      output=[ticker, 0, todayDate, 'EUR', 0]
  #except: #MEGLIO lasciare solo yFINANCE?? anzichè Yahooquery che da sempre errori??
  stock = yf.Ticker(ticker)
  tickInfo = stock.info
  #print(tickInfo)
  curre = verifKey(tickInfo,'currency')
  price1d = verifKey(tickInfo,'previousClose')
  #livePrice = verifKey(tickInfo, 'currentPrice')
  livePrice = verifKey(tickInfo, 'bid')
  datePrice = datetime.today().strftime('%Y-%m-%d')
  output = [ticker, livePrice,datePrice,curre,price1d]
    
  return output
#print(getPriceETF('XDWS.MI'))

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
  #print(fund)
  try:
    fund_df = fund.fund_sector_weightings
    fund_df_desc = fund_df.sort_values(by=ticker, ascending=False)
    #print(fund_df_desc.to_string())
    return fund_df_desc
  except:
    #return  pd.DataFrame() #dataframe vuoto
    #return  pd.DataFrame({ticker:[0,0]},index=[0,'Other']) #dataframe vuoto
    return  pd.DataFrame({ticker:[0]},index=[0]) #dataframe vuoto

def sectorsMultipEtf(tickers):
  #fund = Ticker(['XDEQ.MI','XDWS.MI','CSSPX.MI','CSNDX.MI','GLUX.MI','EMAE.MI','LCWD.MI'])
  fund = Ticker(tickers)
  #print(fund)
  fund_df = fund.fund_sector_weightings
  #print(fund_df)
  return fund_df

#print(sectorsEtf('GLUX.MI'))
#print(sectorsEtf('CSSPX.MIT'))
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
  print("inizio lettura dati per listEtfCountries")
  if isin == 'IE00B579F325':#gold
    return pd.DataFrame([isin,'GOLD REGION',100], columns=['isin','Country','Peso_country']) 
  elif isin == 'GB00BLD4ZL17':#bitcoin
    return pd.DataFrame([isin,'BITCOIN REGION',100], columns=['isin','Country','Peso_country'])  
  else:
    # Chiamata alla funzione
    #sessions = count_chromium_sessions()
    #print(f"Numero di sessioni Chromium (headless) aperte: {sessions}")
    URL="https://extraetf.com/it/etf-profile/"+isin+"?tab=components"
    print(URL)
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
        #print('inizia')
        #country_old = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-etf-profile/div[2]/div/app-blur-wrapper/div/div/div/app-tab-components/div/app-top-data-table[2]/div/div[2]/div/div[2]/div/div['+str(i)+']/div[2]/div[1]/div/div/span').get_attribute("innerText")
        country = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-etf-profile/div[2]/div/app-blur-wrapper/div/div/div/app-tab-components/div/div[2]/app-top-data-table[2]/div/div[2]/div/div[2]/div/div['+str(i)+']/div[2]/div[1]/div/div/span').get_attribute("innerText")
        #print(country)                             
        #weight = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-etf-profile/div[2]/div/app-blur-wrapper/div/div/div/app-tab-components/div/app-top-data-table[2]/div/div[2]/div/div[2]/div/div['+str(i)+']/div[3]').get_attribute("innerText")
        weight = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-etf-profile/div[2]/div/app-blur-wrapper/div/div/div/app-tab-components/div/div[2]/app-top-data-table[2]/div/div[2]/div/div[2]/div/div['+str(i)+']/div[3]').get_attribute("innerText")     
        weight = weight.replace('%','').strip()
        weight = weight.replace(',','.')
        print(f"Stato: '{country}' con il peso di {weight}")
        driverExt.quit()
        if(len(country) > 0):
          listCountry.append([isin,country,weight])
        else:
          break
      except:
        #end loop
        break
      i+=1
    driverExt.quit()
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
  print(f"inizio lettura dati per listStocksCountries per isin {isin}")
  if(isin =='US29355A1079_1'):
    isin = 'US29355A1079'
# Chiamata alla funzione
  #sessions = count_chromium_sessions()
  #print(f"Numero di sessioni Chromium (headless) aperte: {sessions}")

  URL="https://extraetf.com/it/stock-profile/"+isin
  print(f"Link partenza {URL}")
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
  chrome_options.add_argument("--remote-debugging-pipe")


  if(isin == 'GB0007366395'):
    return [isin, 'REGNO UNITO', 100]
  elif isin == 'IE00B579F325':#gold
    return [isin, 'GOLD REGION', 100]
  elif isin == 'GB00BLD4ZL17':#bitcoin
    return [isin, 'BITCOIN REGION', 100]
  else:
    driverExt = webdriver.Chrome( options=chrome_options)
    # Impostazione del timeout di connessione globale
    driverExt.set_page_load_timeout(30)  # Timeout per il caricamento della pagina
    driverExt.get(URL)
    time.sleep(10)
    print('Inizio il test di lettura per isin {isin} al link {URL} :')
    try:
      testvalue = WebDriverWait(driverExt, 20).until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/app-page-template/main/app-stock-profile/div[1]/div[1]/div[1]/div/div[1]/h1'))).get_attribute("innerText")
      print(f'Test lettura da pagina: {testvalue}')
      #country = driverExt.find_element(By.XPATH,'/html/body/app-root/app-page-template/main/app-stock-profile/div[1]/div[1]/div[2]/span[1]/img').get_attribute("title")
      country = WebDriverWait(driverExt, 20).until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/app-page-template/main/app-stock-profile/div[1]/div[1]/div[2]/span[1]/img'))).get_attribute("title")
      print(f"Leggo il dato del paese: {country}")
      driverExt.quit()
      return [isin, country, 100]
    #except TimeoutException:
    except:
      print("Errore timeout")
      driverExt.quit()
      return[isin,'',100]
    # except urllib3.exceptions.ReadTimeoutError as e:
    #   print("Errore timeout di lettura (ReadTimeoutError): La richiesta è scaduta a causa di problemi di rete")
    #   driverExt.quit()
    #   return[isin,'',100]
   
#####Con selenium ho problemi, provo con beautiful soup
def stockCountr(isin):
  if(isin ='US29355A1079_1'): isin='US29355A1079'
  URL="https://extraetf.com/it/stock-profile/"+isin
  r = requests.get(URL) 
  soup = BeautifulSoup(r.content, 'html5lib')
  
  card=soup.find('div', class_='card-body')
  country_0=card.find_all('img')
  #print(country_0[0])
  country = country_0[1]['title']
  return country
#print(stockCountr('US79466L3024'))
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

# def count_chromium_sessions():
#     print("----------------Conto le sessioni aperte: ----------------")
#     # Esegui il comando ps per ottenere i processi Chromium (o Chrome)
#     result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
#     chromium_processes = 0
    
#     # Verifica ogni riga per trovare processi Chromium in modalità headless
#     for line in result.stdout.splitlines():
#         if 'chromium' in line.lower() or 'chrome' in line.lower():
#             if '--headless' in line:
#                 chromium_processes += 1
                
#     return chromium_processes



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
 
################################################################################
##### ALPHA VANTAGE
################################################################################

 #provo a usare API alpha vantage https://www.alphavantage.co/documentation/
  #//limiti uso
  #//We are pleased to provide free stock API service covering the majority of our datasets 
  #//for up to 5 API requests per minute and 100 requests per day. 
  #//If you would like to target a larger API call volume, please visit premium membership.
  #pikey=DH1RD4VL3WSY8SK4
#import requests
#ma che isin usa? lo spy sarebbe qyello con i dividendi... e per gli altri etf dove li trovo?
#url = 'https://www.alphavantage.co/query?function=ETF_PROFILE&symbol=SPY&apikey=DH1RD4VL3WSY8SK4'
#r = requests.get(url)
#data = r.json()
#print(data)
#MIEI ETF
#XDEQ.MI	Xtrackers MSCI World Quality UCITS ETF 1C
#XDWS.MI	Xtrackers MSCI World Consumer Staples UCITS ETF 1C
#GLUX.MI	Amundi Index Solutions - Amundi S&P Global Luxury
#EMAE.MI	SPDR MSCI EM Asia UCITS ETF
#LCWD.MI	Amundi MSCI World V UCITS ETF
#CSSPX.MI-> SPY
#CSNDX.MI-> QQQ

#ricerca ticker
#api_key = 'DH1RD4VL3WSY8SK4'


# Parola chiave per la ricerca del ticker
#keyword = 'staples'

# URL per la ricerca del ticker
#url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keyword}&apikey={api_key}'

# Richiesta dei dati
#response = requests.get(url)
#dataread = response.json()

# Visualizza i risultati della ricerca
#print(dataread)
