
import requests 
from bs4 import BeautifulSoup 
import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib3.poolmanager import _DEFAULT_BLOCKSIZE
#import investpy fuori uso


#Leggo i dati dei BTP dal sito https://www.simpletoolsforinvestors.eu/monitors.shtml
#ad oggi prendo solo dati generici e fornisco i link per andare in profondità e avere cedole

#su qeusto sito però non ho i prezzi storici, solo grafici
#provo ad usare pip install investpy che legge da investing
#documentazione https://investpy.readthedocs.io/_info/installation.html oppure https://pypi.org/project/investpy/#:~:text=investpy%20is%20a%20Python%20package,250%20certificates%2C%20and%204697%20cryptocurrencies.

def fillDatesDFrame(df):
  #ordino crescente le date
  df.sort_values(by='Date',  ascending = True, inplace = True) 
  #converto la colonna in data col formato che uso io
  df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
  #estraggo la prima data
  start = df['Date'].iloc[0]
  #estraggo l'ultima data
  end   = df['Date'].iloc[len(df)-1]
  #trovo tutte le date nel periodo
  new_date = pd.date_range(start=start,end=end,freq='D')
  #converto in dataframe al posto di dataframe index
  new_dates = pd.DataFrame(new_date, columns=['Date'])
  #cro nuovo df
  df_new = (
    pd.concat([df, new_dates], sort=False)
    .drop_duplicates(subset='Date',keep="first")
    .sort_values("Date")
  )
  #riempio i valori con quelli della riga sopra
  df_new = df_new.fillna(method='ffill')
  return df_new

def readEuronext(isin):
  #URL="https://live.euronext.com/it/popout-page/getHistoricalPrice/IT0005580003-MOTX"
  URL="https://live.euronext.com/en/product/bonds/"+isin+"-MOTX"
  URL_det="https://live.euronext.com/en/product/bonds/"+isin+"-MOTX/market-information"

  # Configura le opzioni del browser Chrome
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')

  # Inizializza il driver di Chrome
  driver = webdriver.Chrome( options=chrome_options)
  #Get URL
  driver.get(URL)
  #wait 5 secondi
  time.sleep(5)
  #----------------Dati storici
  #Esporto tutte le tabelle della pagina web
  dfs = pd.read_html(driver.page_source)
  #prendo la tabella che interessa (sono 5 giorni indietro rispetto ad oggi senza oggi)
  histBtp = dfs[20]
  #aggiungo i dati mancanti
  histprice = fillDatesDFrame(histBtp)
  #----------------Dati live
  nameBtp = driver.find_element(By.XPATH,'/html/body/div[2]/div[1]/div/div/div[1]/section/div[2]/div/div/div/div/div/div[1]/div[1]/h1/strong').text
  pricBtp = driver.find_element(By.XPATH,'//*[@id="header-instrument-price"]').text
  dateBtp = driver.find_element(By.XPATH,'/html/body/div[2]/div[1]/div/div/div[1]/section/div[2]/div/div/div/div/div/div[2]/div/div[1]/div[1]/div[2]/div/div[2]').text
  liveDate = datetime.strptime(dateBtp[0:10], '%d/%m/%Y') 
  #aggiungo riga su df con i dati di oggi
  histprice.loc[len(histprice.index)] = [liveDate, pricBtp, 0]
  #riformatto le date
  histprice['Date'] = pd.to_datetime(histprice['Date'], format='%d/%m/%Y')
  #aggiungo nome btp
  histprice['Name'] = nameBtp
  histprice['Isin'] = isin
  return histprice
#print(readEuronext('IT0005580003'))


def getBtpData(isin_val):
  URL = "https://www.simpletoolsforinvestors.eu/monitor_info.php?monitor=italia&yieldtype=G&timescale=DUR" 
  r = requests.get(URL) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  table = soup.find('table', id='YieldTable')
  #number_of_rows = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
  #print(number_of_rows)
 
  df = ({'isin' : '' , 'info' : '', 'stor' : '', 'desc':'', 'curr' : '', 'pric' : '', 'yeld' : '', 'scad' : '2999-12-31'})
  for row in table.tbody.find_all('tr'):    
      # Find all data for each column
      columns = row.find_all('td')
      if(columns != []):
        isin = columns[0].text.strip()
        if (isin == isin_val):
          #info = columns[1].text.strip()
          info = 'https://www.simpletoolsforinvestors.eu/'+columns[1].find('a').get('href')
          stor = 'https://www.simpletoolsforinvestors.eu/'+columns[2].find('a').get('href')
          desc = columns[3].text.strip()
          curr = columns[4].text.strip()
          scad = columns[5].text.strip()
          pric = columns[9].text.strip()
          pric = pric.replace(',','.')
          yeld = columns[13].text.strip()
          
          df = ({'isin' : isin , 'info' : info, 'stor' : stor, 'desc':desc, 'curr' : curr, 'pric' : pric, 'yeld' :yeld, 'scad' : scad})
          break
  return df

def getBotData(isin_val):
  URL = "https://www.simpletoolsforinvestors.eu/monitor_info.php?monitor=bot&yieldtype=G&timescale=DUR" 
  r = requests.get(URL) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  table = soup.find('table', id='YieldTable')
  #number_of_rows = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
  #print(number_of_rows)
  #print(table)
 
  df = ({'isin' : '' , 'info' : '', 'stor' : '', 'desc':'', 'curr' : '', 'pric' : '', 'yeld' : '', 'scad' : '2999-12-31'})
  for row in table.tbody.find_all('tr'):    
      # Find all data for each column
      columns = row.find_all('td')
      if(columns != []):
        isin = columns[0].text.strip()
        if (isin == isin_val):
          info = 'https://www.simpletoolsforinvestors.eu/'+columns[1].find('a').get('href')
          stor = 'https://www.simpletoolsforinvestors.eu/'+columns[2].find('a').get('href')
          desc = columns[3].text.strip()
          curr = columns[4].text.strip()
          scad = columns[5].text.strip()
          pric = columns[9].text.strip()
          yeld = columns[13].text.strip()
          df = ({'isin' : isin , 'info' : info, 'stor' : stor, 'desc':desc, 'curr' : curr, 'pric' : pric, 'yeld' :yeld, 'scad' : scad})
          break
  return df


#print(getBotData('IT0005571960'))
#test = getBtpData('IT0005273013')
#print(test)
