#SITO 1 https://www.quiverquant.com/congresstrading/politician/Nancy%20Pelosi-P000197
#SITO 2 https://www.capitoltrades.com/trades?politician=P000197

#https://financialmodelingprep.com/stable/senate-latest?page=0&limit=25&apikey=e8031887778ab76659fbf1423e804a29
#https://financialmodelingprep.com/stable/house-latest?page=0&limit=25&apikey=e8031887778ab76659fbf1423e804a29
#fino a 25 funziona

import pandas as pd
import requests
from functions_sheets import delete_range,appendRow,read_range,write_range
from settings import * #importa variabili globali
import datetime
from datetime import datetime,timedelta
import time

def readactual():
  
  if(len(fulldata) == 0):
    status = 1 #proseguo
  else:
    dateSheet = fulldata['Data'].iloc[-1]
    print(f"ultima data del foglio {tab} è {dateSheet} mentre oggi è {todayDate}")
    if dateSheet == todayDate :
      status = 0 #non faccio nulla
    else:
      status = 1 #proseguo
  return status

def get_all_senate_data():
    API_KEY = "e8031887778ab76659fbf1423e804a29"
    #base_url = "https://financialmodelingprep.com/api/v4/stable/house-latest" # Verifica la versione esatta dell'endpoint (v4 o stable)
    url = "https://financialmodelingprep.com/stable/senate-latest?page=0&limit=25&apikey=e8031887778ab76659fbf1423e804a29"
    #base_url = "https://financialmodelingprep.com/stable/senate-latest"
    base_url = "https://financialmodelingprep.com/stable/house-latest"
    params = {
      "page": 0,
      "limit": 25,
      "apikey": API_KEY
    }

    # 4. Mascheriamo lo User-Agent per farlo sembrare una richiesta da browser (risolve il 401/403 di sicurezza)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    print("[*] Esecuzione richiesta mascherata...")
    response = requests.get(base_url, params=params, headers=headers, timeout=15)

    print(f"Stato della risposta: {response.status_code}")
    print(response)
    if response.status_code == 200:
      dati = response.json()
      print(f"[+] Connessione riuscita! Scaricati {len(dati)} record.")
      # Mostra il primo record per verifica
      if dati:
          #print("Esempio dati:", dati[0])
          df = pd.DataFrame(dati)
          print(df.head())
          
          #ora leggo quello che è già scritto 
          fulldata = read_range('tab_politici!A:P',newPrj)
          print(fulldata)
          #--confronta con df
          #--trova delta
          #--appendi solo delta
          list_data = df.values.tolist()
          #print('Scrivi da qui')
          #print(list_data)
          appendRow('tab_politici!A:P',list_data,newPrj)
    else:
        print(f"[!] Errore: {response.status_code}")
        print("Dettagli errore dal server:", response.text)


print(get_all_senate_data())