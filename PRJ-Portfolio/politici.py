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
          df_storico = read_range('tab_politici!A:P',newPrj)
          print('---- Stampo dataframe attuale ----')
          print(df_storico.to_string())
          print('---- Fine Stampa dataframe attuale ----')
          #Se il foglio è vuoto, inizializziamo un DataFrame vuoto con le stesse colonne del nuovo
          if df_storico.empty:
              print("[*] Il foglio Google è vuoto. Tutto il DF scaricato verrà trattato come delta.")
              df_storico = pd.DataFrame(columns=df.columns)
          else:
              print(f"[*] Letti {len(df_storico)} record esistenti dal foglio.")
          # 3. Allineamento dei tipi e normalizzazione
          # Per sicurezza convertiamo tutto in stringhe normalizzate (senza spazi superflui)
          # in modo che il confronto non fallisca per discrepanze microscopiche di formattazione.
          df_clean = df.astype(str).apply(lambda x: x.str.strip())
          df_storico_clean = df_storico.astype(str).apply(lambda x: x.str.strip())
          # Selezioniamo le colonne chiave su cui basare l'unicità del record.
          colonne_chiave = ['transactionDate', 'representative', 'symbol', 'type']
          # Controlliamo che le colonne chiave esistano in entrambi i dataframe prima di procedere
          colonne_confronto = [col for col in colonne_chiave if col in df_clean.columns and col in df_storico_clean.columns]

          if not df_storico_clean.empty and colonne_confronto:
              # Eseguiamo un merge "left outer" tenendo traccia della provenienza delle righe
              merge_df = pd.merge(
                  df_clean, 
                  df_storico_clean[colonne_confronto], 
                  on=colonne_confronto, 
                  how='left', 
                  indicator=True
              )
              
              # Estraiamo solo le righe che esistono esclusivamente nel DataFrame appena scaricato (il delta)
              delta_df = df[merge_df['_merge'] == 'left_only'].copy()
          else:
              # Se lo storico è vuoto, tutto il df scaricato è un delta da appendere
              delta_df = df.copy()

          print(f"[*] Calcolo completato. Righe totali scaricate: {len(df)} | Nuove righe (Delta): {len(delta_df)}")

          # 4. Scrittura del solo delta su Google Sheet
          if not delta_df.empty:
              # 1. Convertiamo la colonna in formato datetime per poter effettuare un ordinamento corretto
              delta_df['transactionDate'] = pd.to_datetime(delta_df['transactionDate'], errors='coerce')
              
              # 2. Ordiniamo il delta in base alla data della transazione in modo CRESCENTE (dalla più vecchia alla più recente)
              # Le date non valide (NaT) vengono messe alla fine
              delta_df = delta_df.sort_values(by='transactionDate', ascending=True, na_position='last')
              
              # 3. Riconvertiamo la colonna nel formato stringa 'YYYY-MM-DD' per memorizzarla in modo pulito sul foglio
              delta_df['transactionDate'] = delta_df['transactionDate'].dt.strftime('%Y-%m-%d').fillna("")
              # Sostituiamo i NaN con stringhe vuote per evitare che causino errori di sintassi nell'API di Google Sheets
              delta_df = delta_df.fillna("")
              
              # Convertiamo il dataframe in lista di liste per la scrittura
              list_data = delta_df.values.tolist()
              
              print(f"[*] Tentativo di append di {len(list_data)} nuove righe...")
              appendRow('tab_politici!A:P', list_data, newPrj)
              print("[+] Append completato con successo.")
          else:
              print("[-] Nessun nuovo dato da scrivere. Il foglio è già aggiornato.")

          #--confronta con df
          #--trova delta
          #--appendi solo delta
          list_data = df.values.tolist()
          #print('Scrivi da qui')
          #print(list_data)
          #appendRow('tab_politici!A:P',list_data,newPrj)
    else:
        print(f"[!] Errore: {response.status_code}")
        print("Dettagli errore dal server:", response.text)


print(get_all_senate_data())