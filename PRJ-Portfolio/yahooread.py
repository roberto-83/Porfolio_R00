from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

#1-funzione che legge dal sito web ma funziona poco..
def readYahooSite(tick):
  #tick='GB00BLD4ZL17.SG'
  URL="https://it.finance.yahoo.com/quote/"+tick+"/"
  print(f"richiamo il link {URL}")
  # Configura le opzioni del browser Chrome
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')

  driverExt = webdriver.Chrome( options=chrome_options)
  driverExt.get(URL)
  driverExt.maximize_window()
  #prendo il bottone "acetta tutto"
  button=driverExt.find_element(By.XPATH,'/html/body/div/div/div/div/form/div[2]/div[2]/button[1]')
  #print(button)
  driverExt.execute_script("arguments[0].click();", button)
  time.sleep(5)
  #leggo i dati
  #print(driverExt.page_source)
  msg = driverExt.find_element(By.XPATH,'/html/body/table/tbody/tr/td/h1').text
  if(msg == 'Will be right back...'):
    print('Server non disponibile')
    arr=[tick,'',0,0]
  else:

    price = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div/fin-streamer[1]').text
    #price = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div').text
    title = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[2]/div[1]/div[1]/h1').text
    pos1 = title.find("(")
    title = title[0:pos1]
    price1d = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/div/div[2]/div[1]/table/tbody/tr[1]/td[2]').text

    print(f"Leggo ticker {tick}, titolo {title}, prezzo {price}, chiusura ieri {price1d}")
    arr = [tick,title,price,price1d]
  return arr
#print(readYahooSite('GB00BLD4ZL17.SG'))

#2 proviamo con le api di yahoo finance
#guida qui https://cryptocointracker.com/yahoo-finance/yahoo-finance-api

