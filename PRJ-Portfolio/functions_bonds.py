
import requests 
from bs4 import BeautifulSoup 
import pandas as pd
import time
from datetime import datetime,timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib3.poolmanager import _DEFAULT_BLOCKSIZE
from io import StringIO
import os
#import investpy fuori uso


#Leggo i dati dei BTP dal sito https://www.simpletoolsforinvestors.eu/monitors.shtml
#ad oggi prendo solo dati generici e fornisco i link per andare in profondità e avere cedole

#su qeusto sito però non ho i prezzi storici, solo grafici
#provo ad usare pip install investpy che legge da investing
#documentazione https://investpy.readthedocs.io/_info/installation.html oppure https://pypi.org/project/investpy/#:~:text=investpy%20is%20a%20Python%20package,250%20certificates%2C%20and%204697%20cryptocurrencies.

def fillDatesDFrame(df):
  #print(df.keys)
  #converto la colonna in data col formato che uso io
  df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
  #ordino crescente le date
  df.sort_values(by='Date',  ascending = True, inplace = True) 
  #estraggo la prima data
  start = df['Date'].iloc[0]
  #estraggo l'ultima data
  end   = df['Date'].iloc[len(df)-1]
  #sommo un padio di giorni per non avere errori nei weekend
  end1 =end+timedelta(days=3)
  #print(f"data inizio {end} data fine {end1}")
  #print(f'Data inizio {start} e data fine {end}')
  #trovo tutte le date nel periodo
  new_date = pd.date_range(start=start,end=end1,freq='D')
  #converto in dataframe al posto di dataframe index
  new_dates = pd.DataFrame(new_date, columns=['Date'])
  #print(new_dates)
  #cro nuovo df
  df_new = (
    pd.concat([df, new_dates], sort=False)
    .drop_duplicates(subset='Date',keep="first")
    .sort_values("Date")
  )
  #riempio i valori con quelli della riga sopra
  #df_new = df_new.fillna(method='ffill')
  df_new = df_new.ffill()
  return df_new

def readEuronext(isin):
  #OLDDDDURL="https://live.euronext.com/it/popout-page/getHistoricalPrice/IT0005580003-MOTX"
  #https://live.euronext.com/en/product/bonds/IT0005580003-MOTX
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
  #---
  #id del campo data from datetimepickerFrom
  #https://www.scaler.com/topics/selenium-tutorial/how-to-handle-date-picker-in-selenium/
  #date_input = driver.find_element_by_id("date-input")
  #date_input.click()
  #calendar = driver.find_element_by_class_name("datepicker-calendar")
  #date_element = driver.find_element_by_xpath("//div[@class='date'][text()='25']")

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

def readEuronextREV2(isin, data):
  print(f"#############Leggo i dati di {isin}")
  #URl singola mi da alcune info
  #se vado in URL_ESTESO ho piu storico da leggere
  URL="https://live.euronext.com/en/product/bonds/"+isin+"-MOTX"
  URL_ESTESO = "https://live.euronext.com/en/product/bonds/"+isin+"-MOTX#historical-price"
  URL_det="https://live.euronext.com/en/product/bonds/"+isin+"-MOTX/market-information"
  print(f"url che sto leggendo {URL_ESTESO}")
  # Configura le opzioni del browser Chrome
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("enable-automation")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--dns-prefetch-disable")
  chrome_options.add_argument("--disable-gpu")
  
  #leggo dati comuni
  #driver = webdriver.Chrome( options=chrome_options)
  #driver.get(URL)
  #time.sleep(5)

  #todayDate = datetime.today().strftime('%d/%m/%Y')
  todayDate = datetime.today().strftime('%Y-%m-%d')
  #diffdate = ( datetime.strptime(todayDate, "%d/%m/%Y") - datetime.strptime(data, "%d/%m/%Y")).days
  diffdate = ( datetime.strptime(todayDate, "%Y-%m-%d") - datetime.strptime(data, "%Y-%m-%d")).days
  #print(f"Differenza date {diffdate}")
  #Se la diff date è <=0 allor anon devo fare nulla
  #se è minore di 5 uso primo metodo (+ veloce)
  #altrimenti metodo esteso
  if(diffdate <= 0):
    print('Aggiornamento non necessario')
    histprice = 0 
  else:
    # print("inizia driver")
    # driverExt = webdriver.Chrome( options=chrome_options)
    # driverExt.get(URL_ESTESO)
    # print("10 sec wait")
    # time.sleep(10)
    
    # #leggo i dati
    # dfsExt = pd.read_html(StringIO(driverExt.page_source))
    # time.sleep(5)
    
    # #prendo la tabella

    # histBtpExt = dfsExt[22]
    # histBtpExt['Date'] = pd.to_datetime(histBtpExt['Date'], format='%d/%m/%Y')
    # #print("stampo quello che leggo")##########################################################
    # histpriceExt = fillDatesDFrame(histBtpExt)
    #CHAT GRP 
    try:
        print("inizia driver")
        driverExt = webdriver.Chrome(options=chrome_options)
        driverExt.set_page_load_timeout(60)

        print("Caricamento URL ESTESO...")
        driverExt.get(URL_ESTESO)

        # Attendi che la tabella o il pulsante "Load more" sia presente
        WebDriverWait(driverExt, 20).until(
            EC.presence_of_element_located((By.ID, "AwlHistoricalPrice"))
        )

        print("Tabella caricata, parsing HTML...")
        time.sleep(5)  # piccolo delay extra
        dfsExt = pd.read_html(StringIO(driverExt.page_source))
        print("stampo output")
        # Cerca tabella con colonna 'Date'
        histBtpExt = None
        for df in dfsExt:
            if 'Date' in df.columns:
                histBtpExt = df
                break
        if histBtpExt is None:
            raise ValueError("Tabella con 'Date' non trovata.")

    except TimeoutException as te:
        print("Errore: Timeout nel caricamento della pagina o elementi.")
        driverExt.quit()
        return None

    except Exception as e:
        print(f"Errore imprevisto: {e}")
        driverExt.quit()
        return None


    #loop per cercare la data nel sito
    i=0
    while i <= 12:
      print(f"Loop numero {i}")
      #verifico se la data è presente
      #if len(histpriceExt[histpriceExt['Date'] == datetime.strptime(data, "%d/%m/%Y").strftime('%Y-%m-%d')]) == 1:
      print(f"cerco data {datetime.strptime(data, '%Y-%m-%d').strftime('%Y-%m-%d')}")
      if len(histpriceExt[histpriceExt['Date'] == datetime.strptime(data, "%Y-%m-%d").strftime('%Y-%m-%d')]) == 1:
        #print('Presente')
        break
      else:
        #print('manca')
        #premo tasto per aumentare lo storico
        time.sleep(5)
        buttonLoad = driverExt.find_element(By.XPATH,'//*[@id="historical-price-load-more"]')
        time.sleep(5)
        driverExt.execute_script("arguments[0].click();", buttonLoad)
        time.sleep(5)
        #leggo i dati
        #dfsExt = pd.read_html(driverExt.page_source)
        dfsExt = pd.read_html(StringIO(driverExt.page_source))
        histBtpExt = dfsExt[22]
        #print(histBtpExt)
        histpriceExt = fillDatesDFrame(histBtpExt)
        histpriceExt.Date = pd.to_datetime(histpriceExt.Date)

      i += 1
    print('Output funzione:')
    print(histpriceExt)
    driverExt.quit()
    if driverExt.service.process.poll() is None:
      print("Driver attivo")
    else:
        print("Driver terminato")
    #os.system("pkill chromedriver")
    #os.system("pkill chrome")
    #cerco di chiudere il driver..
    if driverExt:
      try:
          driverExt.quit()
      except Exception as e:
          print("Errore durante quit:", e)
      finally:
          del driverExt
    #provo  a dare tempo dopo la chiusura per vedere che chiusa tutto e non rimanga appeso
    time.sleep(5)

  return histpriceExt
#print(readEuronextREV2('IT0005580003','08/05/2024'))

def readEuronextREV2_BACKUP(isin, data):
  print(f"#############Leggo i dati di {isin}")
  #URl singola mi da alcune info
  #se vado in URL_ESTESO ho piu storico da leggere
  URL="https://live.euronext.com/en/product/bonds/"+isin+"-MOTX"
  URL_ESTESO = "https://live.euronext.com/en/product/bonds/"+isin+"-MOTX#historical-price"
  URL_det="https://live.euronext.com/en/product/bonds/"+isin+"-MOTX/market-information"
  print(f"url che sto leggendo {URL_ESTESO}")
  # Configura le opzioni del browser Chrome
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("enable-automation")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--dns-prefetch-disable")
  chrome_options.add_argument("--disable-gpu")
  
  #leggo dati comuni
  #driver = webdriver.Chrome( options=chrome_options)
  #driver.get(URL)
  #time.sleep(5)

  #todayDate = datetime.today().strftime('%d/%m/%Y')
  todayDate = datetime.today().strftime('%Y-%m-%d')
  #diffdate = ( datetime.strptime(todayDate, "%d/%m/%Y") - datetime.strptime(data, "%d/%m/%Y")).days
  diffdate = ( datetime.strptime(todayDate, "%Y-%m-%d") - datetime.strptime(data, "%Y-%m-%d")).days
  #print(f"Differenza date {diffdate}")
  #Se la diff date è <=0 allor anon devo fare nulla
  #se è minore di 5 uso primo metodo (+ veloce)
  #altrimenti metodo esteso
  if(diffdate <= 0):
    print('Aggiornamento non necessario')
    histprice = 0 
  else:
    print("inizia driver")
    driverExt = webdriver.Chrome( options=chrome_options)
    #driverExt.set_page_load_timeout(30)
    #Get URL
    driverExt.get(URL_ESTESO)
    print("10 sec wait")
    time.sleep(10)
    
    #leggo i dati
    #dfsExt = pd.read_html(driverExt.page_source)
    dfsExt = pd.read_html(StringIO(driverExt.page_source))
    #print(dfsExt)
    time.sleep(5)
    
    #prendo la tabella
    ####METTO UN TRY CATCH?? vediamo se mi si blocca ancora..

    histBtpExt = dfsExt[22]
    #print(histBtpExt)
    histBtpExt['Date'] = pd.to_datetime(histBtpExt['Date'], format='%d/%m/%Y')
    #print("stampo quello che leggo")##########################################################
    #riempio le date vuote
    histpriceExt = fillDatesDFrame(histBtpExt)
    #print(histpriceExt)
    #loop per cercare la data nel sito
    i=0
    while i <= 12:
      print(f"Loop numero {i}")
      #verifico se la data è presente
      #if len(histpriceExt[histpriceExt['Date'] == datetime.strptime(data, "%d/%m/%Y").strftime('%Y-%m-%d')]) == 1:
      print(f"cerco data {datetime.strptime(data, '%Y-%m-%d').strftime('%Y-%m-%d')}")
      if len(histpriceExt[histpriceExt['Date'] == datetime.strptime(data, "%Y-%m-%d").strftime('%Y-%m-%d')]) == 1:
        #print('Presente')
        break
      else:
        #print('manca')
        #premo tasto per aumentare lo storico
        time.sleep(5)
        buttonLoad = driverExt.find_element(By.XPATH,'//*[@id="historical-price-load-more"]')
        time.sleep(5)
        driverExt.execute_script("arguments[0].click();", buttonLoad)
        time.sleep(5)
        #leggo i dati
        #dfsExt = pd.read_html(driverExt.page_source)
        dfsExt = pd.read_html(StringIO(driverExt.page_source))
        histBtpExt = dfsExt[22]
        #print(histBtpExt)
        histpriceExt = fillDatesDFrame(histBtpExt)
        histpriceExt.Date = pd.to_datetime(histpriceExt.Date)

      i += 1
    print('Output funzione:')
    print(histpriceExt)
    driverExt.quit()
    if driverExt.service.process.poll() is None:
      print("Driver attivo")
    else:
        print("Driver terminato")
    #os.system("pkill chromedriver")
    #os.system("pkill chrome")
    #cerco di chiudere il driver..
    if driverExt:
      try:
          driverExt.quit()
      except Exception as e:
          print("Errore durante quit:", e)
      finally:
          del driverExt
    #provo  a dare tempo dopo la chiusura per vedere che chiusa tutto e non rimanga appeso
    time.sleep(5)

  return histpriceExt

def getBtpData(isin_val):
  if(isin_val == 'IT0005580003'):#non è piu disponibile..
    df = ({'isin' : isin_val , 'info' : 'info', 'stor' : 'stor', 'desc':'BOT 14/01/2025 ZC', 'curr' : 'EUR', 'pric' : 100, 'yeld' :'0', 'scad' : '', 'cedo':''})
  else:    
    print(f'Inizio a utilizzare BEAUTIFUL SOUP per isin {isin_val}')
    if isin_val[0:2] == 'IT':  #se è un bond italiano
      URL = "https://www.simpletoolsforinvestors.eu/monitor_info.php?monitor=italia&yieldtype=G&timescale=DUR" 
    elif isin_val[0:2] == 'XS': #se è un bond rumeno
      URL = "https://www.simpletoolsforinvestors.eu/monitor_info.php?monitor=romania&yieldtype=G&timescale=DUR"
    else: # se non è come sopra do per scontato che sia europeo..
      URL = "https://www.simpletoolsforinvestors.eu/monitor_info.php?monitor=europa&yieldtype=G&timescale=DUR"
    print(URL)
    
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
            dataCedola = getDividBtp(info,scad)
            df = ({'isin' : isin , 'info' : info, 'stor' : stor, 'desc':desc, 'curr' : curr, 'pric' : pric, 'yeld' :yeld, 'scad' : scad, 'cedo':dataCedola})
            break
  return df

def getDividBtp(URL,scad):
  #df = getBtpData(isin_val)
  #URL = df['info']
  #print(URL)
  r = requests.get(URL) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  table = soup.find('table')
  dataCedola = scad
  for row in table.tbody.find_all('tr'):    
    columns = row.find_all('td')
    if(columns != []): 
        if(columns[1].text.strip() == 'Incasso cedola lorda'):
          dataCedola = columns[0].text.strip()
          #print(f" colonna 0 {columns[0].text.strip()} , colonna 1 {columns[1].text.strip()} , colonna 2 {columns[2].text.strip()}")
          break
  return dataCedola

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
          dataCedola = scad
          df = ({'isin' : isin , 'info' : info, 'stor' : stor, 'desc':desc, 'curr' : curr, 'pric' : pric, 'yeld' :yeld, 'scad' : scad, 'cedo':dataCedola})

          break
  return df


#print(getBotData('IT0005580003'))
#test = getBtpData('IT0005273013')#btp
#test = getBtpData('IT0005580003')#bot
#print(test)

#print(getDividBtp('IT0005273013'))
