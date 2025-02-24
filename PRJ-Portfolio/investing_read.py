# Esempio di indicatore - PIL
#qui c'è il valore attuale e quello previsto
#https://it.investing.com/economic-calendar/gdp-375

#link investing https://it.investing.com/economic-calendar/unemployment-rate-300
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from settings import *
from functions_sheets import read_range,write_range,appendRow
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

#LINK interessanti
#qui riporta il buy, hold etc...
#https://it.investing.com/technical/stocks-indicators

#URL PRINCIPALE
#https://it.investing.com/economic-calendar/
todayDate_f = datetime.today().strftime('%Y-%m-%d')

url_PIL = "https://it.investing.com/economic-calendar/gdp-375"
url_disoccupazione = "https://it.investing.com/economic-calendar/unemployment-rate-300"
url_PCI_inflazione="https://it.investing.com/economic-calendar/cpi-733"
url_tassi_interesse="https://it.investing.com/economic-calendar/interest-rate-decision-168"
url_fiducia_consumatori="https://it.investing.com/economic-calendar/cb-consumer-confidence-48"
url_produzione_industriale="https://it.investing.com/economic-calendar/industrial-production-161"
url_vendite_dettaglio="https://it.investing.com/economic-calendar/retail-sales-256"
#nuovi lavori
url_JOLTS="https://it.investing.com/economic-calendar/jolts-job-openings-1057"
url_scorte_petrolio="https://it.investing.com/economic-calendar/api-weekly-crude-stock-656"
url_global_pmi="https://it.investing.com/economic-calendar/s-p-global-composite-pmi-1492"

################################################################################
# LEGGO BEAUTIFIUL SOUP
################################################################################

#questa funzione usa beautifulSoup ma ha il limite che non può fare click su "contiunua a leggere e avere gli altri dati"
#andremme bene per il trimestre ma i tassi di interesse hanno righe vuote all'inizio.. li prendo tra altro sito??
def get_econ_data(url,item):
  df = pd.DataFrame()   # an empty DataFrame
  # URL della pagina con il dato del PIL USA

  # Effettua la richiesta HTTP
  response = requests.get(url)
  # Se la richiesta va a buon fine
  if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')    
      table = soup.find('table')
      headers = [th.text.strip() for th in table.find_all('th')]
      rows = []
      for row in table.find_all('tr')[1:]:  # Salta la prima riga (intestazioni)
          cols = row.find_all('td')
          cols = [ele.text.strip() for ele in cols]
          rows.append(cols)
      df = pd.DataFrame(rows, columns=headers)
      #df['Item'] = item
      df = df.drop(columns='Ora')
      df = df.drop(columns='Precedente')
      df['Data']=df['Data di rilascio'].str[0:10]
      df['Data']=df['Data'].replace(to_replace='\.',value='-',regex=True)
      df['Data']=pd.to_datetime(df['Data'],dayfirst=True) 
      df.set_index('Data', inplace=True)
      df = df[df.index <= todayDate_f]
      df = df.sort_index()
      df.rename(columns={
          "Data di rilascio": "Rilascio "+item,
          "Attuale": "Attuale "+item,
          "Previsto": "Previsto "+item
          #"Precedente": "Precedente "+item
          }, inplace=True)
      #print(item)
      #print(df)
      print(f"Item {item} letto")
  return df

################################################################################
# LEGGO SELENIUM
################################################################################

def investing_Selenium(url, item):
  print(f"Inizio lettura sito investing per item {item}")
  #url="https://it.investing.com/economic-calendar/interest-rate-decision-168"
  # Configura le opzioni del browser Chrome
  chrome_options = Options()
  chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument("--enable-javascript")
  chrome_options.add_argument('--disable-dev-shm-usage')
  
  page_load_timeout = 60  # Timeout per il caricamento della pagina
  element_timeout = 10    # Timeout per l'attesa di un elemento
  print('Inizio primo try')
  try:
    # Inizializza il driver di Chrome
    driver = webdriver.Chrome( options=chrome_options)
    driver.set_page_load_timeout(page_load_timeout)
    #driver.maximize_window()
    #Get URL
    driver.get(url)
 
    print('Inizio secondo try')
    # Aspetta che l'elemento si carichi (modifica il timeout a seconda del caso)
    try:
        buttonLoad = WebDriverWait(driver, element_timeout).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/section/div[12]/div[1]/a'))
        )
        driver.execute_script("arguments[0].click();", buttonLoad)
        print('Bottone premuto')
    except TimeoutException:
        print("Timeout: il bottone non è stato trovato in tempo.")
        driver.quit()
        return pd.DataFrame()  # Restituisci un DataFrame vuoto in caso di errore
    print('fine secondo try')
    time.sleep(5)
    #faccio click per espandere tabella
    #buttonLoad = driver.find_element(By.XPATH,'/html/body/div[7]/section/div[12]/div[1]')
    #driver.execute_script("arguments[0].click();", buttonLoad)
    #time.sleep(5)

    #Esporto tutte le tabelle della pagina web
    dfs = pd.read_html(driver.page_source)
    driver.quit() 
    output=dfs[0]
    output = output.drop(columns=['Ora','Unnamed: 5'])
    output['Data']=output['Data di rilascio'].str[0:10]
    output['Data']=output['Data'].replace(to_replace='\.',value='-',regex=True)
    output['Data']=pd.to_datetime(output['Data'],dayfirst=True) 
    output.set_index('Data', inplace=True)
    output = output[output.index <= todayDate_f]
    output = output.sort_index()
    output.rename(columns={
            "Data di rilascio": "Rilascio "+item,
            "Attuale": "Attuale "+item,
            "Previsto": "Previsto "+item,
            "Precedente": "Precedente "+item
            }, inplace=True)
    print(f"Item {item} letto") 
  except TimeoutException:
    print("Errore di Timeout")
    output = pd.DataFrame()
    # output_1= {'Rilascio TASSI': [0], 'Attuale TASSI': [0],'Previsto TASSI': [0]}
    # output = pd.DataFrame.from_dict(output_1)
    # output['Data']=todayDate_f
    # output.set_index('2024-01-01', inplace=True)
    # #output['Data']=todayDate_f
    #print(output)
  return output
#print(investing_Selenium(url_tassi_interesse,'TASSI'))

################################################################################
# MERGE DATAFRAME
################################################################################

def merge_dataframe():
  #print('PIL')
  pil = get_econ_data(url_PIL,'PIL')
  #print('Disoccupazione')
  disoccup = get_econ_data(url_disoccupazione,'DISOCCUPAZ')
  #print('PCI Inflazione')
  inflaz = get_econ_data(url_PCI_inflazione,'PCI')
  #print('Tassi Interesse')
  tassi = investing_Selenium(url_tassi_interesse,'TASSI')
  #print('Fiducia Consumatori')
  consuma = get_econ_data(url_fiducia_consumatori,'FIDUC_CONS')
  #print('Produzione industriale')
  produz = get_econ_data(url_produzione_industriale,'PRODUZIONE')
  #print('Vendite dettaglio')
  vendite = get_econ_data(url_vendite_dettaglio,'VENDITE')
  #unisco i df
  if not tassi.empty:
    df_finale = pil.merge(disoccup, left_index=True, right_index=True, how='outer')
    df_finale = df_finale.drop(columns='_x')
    df_finale = df_finale.drop(df_finale.columns[-1], axis=1)
    df_finale = df_finale.merge(inflaz, left_index=True, right_index=True, how='outer')
    df_finale = df_finale.drop(df_finale.columns[-1], axis=1)
    df_finale = df_finale.merge(tassi, left_index=True, right_index=True, how='outer') 
    df_finale = df_finale.drop(df_finale.columns[-1], axis=1)
    df_finale = df_finale.merge(consuma, left_index=True, right_index=True, how='outer')
    df_finale = df_finale.drop(df_finale.columns[-1], axis=1)
    df_finale = df_finale.merge(produz, left_index=True, right_index=True, how='outer')
    df_finale = df_finale.drop(df_finale.columns[-1], axis=1)
    df_finale = df_finale.merge(vendite, left_index=True, right_index=True, how='outer')
    df_finale = df_finale.drop(df_finale.columns[-1], axis=1)
    #fill NaN values
    df_finale = df_finale.fillna(method='ffill')
    # Trova  la prima riga che non contiene NaN
    df_finale = df_finale[df_finale.notna().all(axis=1)]#.reset_index(drop=True)
    #df_finale['Data'] = df_finale.index
    df_finale.insert(0, "Data", df_finale.index)
    #print('primo check')
    #print(df_finale.columns)
    #print(df_finale.to_string())
    return df_finale
  df_finale = pd.DataFrame()
  return df_finale

#print(merge_dataframe())

################################################################################
# SCRIVO SHEET
################################################################################

def write_economin_data():
  #fase 1, controllo che non abbia già eseguito
  lastDateWrite = read_range('tab_investing!W2',newPrj)
  lastDateWrite1 = lastDateWrite.columns[0]
  delta_dates = pd.to_datetime(todayDate_f) - pd.to_datetime(lastDateWrite1)
  print(f"Dalta date {delta_dates.days}")
  numdays = delta_dates.days
  if numdays != 0:
    #carico i dati che dovrei scrivere
    alldataframe = merge_dataframe()
    if not alldataframe.empty:
      #print(alldataframe.dtypes)
      alldataframe['Data'] = alldataframe['Data'].dt.strftime('%Y-%m-%d')

      actualdata = read_range('tab_investing!A:V',newPrj)
      actualdata.set_index('Data', inplace=True)
      actualdata.insert(0, "Data", actualdata.index)

      #CONFRONTO
      #prendo la data piu vecchia del nuovo DF
      #filtro l'attuale a quella data in modo da salvare i vecchi dati
      #unisco i due dataframe e poi stampo
      oldDateNewData = alldataframe.first_valid_index()
      oldDateOldData = actualdata.first_valid_index()
      print(f'Nei dati che sto scrivendo la data piu vecchia è {oldDateNewData}')
      print(f'Nel mio database ho come data piu vecchia {oldDateOldData}')
  
      #Dataframe con il delta dei dati
      actualdata.index = pd.to_datetime(actualdata.index)
      delta_Df = actualdata[actualdata.index < pd.to_datetime(oldDateNewData)]  #voglio salvare i dati attuali vecchi..

      #Ora voglio unire i nuovi dati 
      df_to_print = pd.concat([delta_Df, alldataframe], axis=0)
      print('Dataframe da stampare')
      #print(df_to_print)
      
      listToPrint = df_to_print.values.tolist()
      lastRowSt=str(len(df_to_print)+1)
      write_range('tab_investing!A2:V'+lastRowSt,listToPrint,newPrj)
      write_range('tab_investing!W2',[[todayDate_f]],newPrj)
      return 'OK'
    else:
      print('Non sono riuscito a leggere i dati da investing')
      return 'KO'
  else:
    print('Funzione già eseguita oggi')
    return 'UNNECESSARY'
    

#print(write_economin_data())

#def print_df(df,col_start):
  #voglio leggere l'ultima data della colonna passata
  #diffirenza con dataframe, se ci sono nuovo dati scrivo solo quelli
#  return 'ok'


################################################################################
# ALGORITMO CALCOLO CICLO ECONOMICO
################################################################################


# Funzione per determinare il ciclo economico
def analizza_ciclo(dati):
    # Determina il ciclo economico basato sui dati
    if dati['PIL'] > 2.0 and dati['Disoccupazione'] < 5.0 and dati['Inflazione (CPI)'] < 3.5 and dati['Fiducia Consumatori'] > 90:
        return 'Espansione'
    elif dati['PIL'] > 0 and dati['Disoccupazione'] <= 3.5 and dati['Inflazione (CPI)'] > 3.5 and dati['Fiducia Consumatori'] > 100:
        return 'Picco'
    elif dati['PIL'] < 0 and dati['Disoccupazione'] > 5.0 and dati['Inflazione (CPI)'] < 1.0:
        return 'Recessione'
    elif dati['PIL'] > 1.0 and dati['Disoccupazione'] < 5.0 and dati['Fiducia Consumatori'] > 80:
        return 'Ripresa'
    else:
        return 'Stagnazione o incertezza'

# Determina il regime economico attuale
#regime = analizza_ciclo(dati_indici)

#print(f"Il regime economico attuale è: {regime}")



