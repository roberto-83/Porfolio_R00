from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def changeFormatNumber(numb):
  #print(f"Controllo punto {numb.find('.')}")
  if(numb.find('.') != -1):
  #if(len(numb) > 6):
    numb2 = numb.replace('.','')
    numb1 = numb2.replace(',','.')
  else:
    numb1 = numb.replace(',','.')
  return numb1


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
  chrome_options.add_argument("--disable-gpu")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("enable-automation")
  chrome_options.add_argument("--dns-prefetch-disable")
  chrome_options.add_argument("--disable-gpu")
  #chrome_options.add_argument("--ignore-certificate-errors")
  #chrome_options.add_argument("--ignore-ssl-errors")
  #chrome_options.add_argument("--log-level=3")
  #chrome_options.add_argument("enable-features=NetworkServiceInProcess")
  #chrome_options.add_argument("disable-features=NetworkService")

  driverExt = webdriver.Chrome( options=chrome_options)
  #driverExt.set_page_load_timeout(10)
  #driverExt.implicitly_wait(10) # attendi fino a 10 secondi per gli elementi
  driverExt.get(URL)
  driverExt.maximize_window()
  #prendo il bottone "accetta tutto"
  button=driverExt.find_element(By.XPATH,'/html/body/div/div/div/div/form/div[2]/div[2]/button[1]')
  #print(button)
  driverExt.execute_script("arguments[0].click();", button)
  time.sleep(5)
  #print('fin qui tutto bene')
  #leggo i dati
  #print(driverExt.page_source)

  try:
    msg = driverExt.find_element(By.XPATH,'/html/body/table/tbody/tr/td/h1').text
  except:
    msg = 0

  #msg = driverExt.find_element(By.XPATH,'/html/body/table/tbody/tr/td/h1').text
  #print(f"Messaggio {msg}")
  if(msg == 'Will be right back...'):
    print('Server non disponibile')
    arr=[tick,'',0,0,0,0,0]
  else:
    #prezzo
    price1 = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div/fin-streamer[1]').text
    price = changeFormatNumber(price1)

    #price = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div').text
    #descrizione titolo
    title = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[2]/div[1]/div[1]/h1').text
    pos1 = title.find("(")
    title = title[0:pos1]
    #prezzo chiusura precedente
    price1d1 = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/div/div[2]/div[1]/table/tbody/tr[1]/td[2]').text
    price1d = changeFormatNumber(price1d1)
    #currency
    currency0 = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[2]/div[1]/div[2]/span').text
    currency1 = currency0[-4:]
    currency2 = currency1[0:3]
    #52Week
    try:
      fiftyTwoWeekRange1 = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/div/div[2]/div[1]/table/tbody/tr[6]/td[2]').text
    except:
      fiftyTwoWeekRange1 = driverExt.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[1]/div/div/div/div[2]/div[2]/table/tbody/tr[2]/td[2]').text

    if (fiftyTwoWeekRange1 == 'N/D'):
      fiftyTwoWeek_low = 0
      fiftyTwoWeek_high = 0
    else:
      pos52_1 = fiftyTwoWeekRange1.find("-")
      #print(f"Posizione del trattino {pos52_1}")
      print(f"Range low {fiftyTwoWeekRange1[0:pos52_1]} e Range high {fiftyTwoWeekRange1[pos52_1+2:]}")
      fiftyTwoWeek_low1 = fiftyTwoWeekRange1[0:pos52_1]
      fiftyTwoWeek_high1 = fiftyTwoWeekRange1[pos52_1+2:]
      fiftyTwoWeek_low = changeFormatNumber(fiftyTwoWeek_low1)
      fiftyTwoWeek_high = changeFormatNumber(fiftyTwoWeek_high1)

    arr = [tick,title,price,price1d,currency2,fiftyTwoWeek_low,fiftyTwoWeek_high]
    driverExt.quit()
  return arr

#print(readYahooSite('GB00BLD4ZL17.SG'))
#print(readYahooSite('ICGA.DE'))

#2 proviamo con le api di yahoo finance
#guida qui https://cryptocointracker.com/yahoo-finance/yahoo-finance-api

