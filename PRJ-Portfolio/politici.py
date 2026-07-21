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
import re
def extract_max_amount(val):
    if not isinstance(val, str) or not val.strip():
        return None
    # Se il valore contiene un intervallo (es. "$1,001 - $15,000")
    if '-' in val:
        right_part = val.split('-')[-1]
    else:
        # Gestisce casi senza intervallo (es. "> $50,000,000")
        right_part = val
    
    # Rimuove tutto ciò che non è un numero
    clean_num = re.sub(r'[^\d]', '', right_part)
    return float(clean_num) if clean_num else None

def get_all_house_data():
    print(" ----- Inizio a leggere i dati delle transazioni della camera americana ----")
    API_KEY = "e8031887778ab76659fbf1423e804a29"
    #base_url = "https://financialmodelingprep.com/api/v4/stable/house-latest" # Verifica la versione esatta dell'endpoint (v4 o stable)
    #url = "https://financialmodelingprep.com/stable/senate-latest?page=0&limit=25&apikey=e8031887778ab76659fbf1423e804a29"
    #base_url = "https://financialmodelingprep.com/stable/senate-latest"
    base_url = "https://financialmodelingprep.com/stable/house-latest"
    #params = {
    #  "page": 0,
    #  "limit": 25,
    #  "apikey": API_KEY
    #}
    params = {
      "apikey": API_KEY
    }

    # 4. Mascheriamo lo User-Agent per farlo sembrare una richiesta da browser (risolve il 401/403 di sicurezza)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    #print("[*] Esecuzione richiesta mascherata...")
    response = requests.get(base_url, params=params, headers=headers, timeout=15)

    print(f"Stato della risposta: {response.status_code}")
    #print(response)
    if response.status_code == 200:
      dati = response.json()
      print(f"[+] Connessione riuscita! Scaricati {len(dati)} record.")
      # Mostra il primo record per verifica
    if dati:
          # 1. Creiamo il DataFrame dai nuovi dati API
          df_nuovo = pd.DataFrame(dati)
          
          # 2. Leggiamo lo storico esistente dal Google Sheet
          df_storico = read_range('tab_politici!A:P', newPrj)
          print('---- Stampo dataframe attuale ----')
          print(df_storico.to_string())
          print('---- Fine Stampa dataframe attuale ----')
          
          # Gestiamo il caso in cui il foglio sia vuoto
          if df_storico.empty:
              print("[*] Il foglio Google è vuoto. Procedo con i soli dati scaricati.")
              df_unificato = df_nuovo.copy()
          else:
              print(f"[*] Letti {len(df_storico)} record esistenti dal foglio. Unifico i dati...")
              # Concateniamo lo storico e il nuovo df
              df_unificato = pd.concat([df_storico, df_nuovo], ignore_index=True)

          # 3. Pulizia e normalizzazione delle date per un ordinamento preciso
          # Convertiamo temporaneamente in datetime per ordinare cronologicamente
          df_unificato['transactionDate'] = pd.to_datetime(df_unificato['transactionDate'], errors='coerce')
          
          # Ordiniamo l'intero set in base alla data della transazione in modo CRESCENTE (dal più vecchio al più recente)
          df_unificato = df_unificato.sort_values(by='transactionDate', ascending=True, na_position='last')
          
          # Ripristiniamo la data in formato stringa standard YYYY-MM-DD
          df_unificato['transactionDate'] = df_unificato['transactionDate'].dt.strftime('%Y-%m-%d').fillna("")

          # 4. Rimozione dei duplicati
          # Definiamo le colonne chiave. Se un politico fa la stessa identica operazione (tipo) sullo stesso titolo (symbol) lo stesso giorno, è un duplicato.
          colonne_chiave = ['transactionDate', 'representative', 'symbol', 'type','amount']
          # Verifichiamo quali colonne chiave sono effettivamente presenti nel DF unificato
          colonne_confronto = [col for col in colonne_chiave if col in df_unificato.columns]
          
          # Rimuoviamo i duplicati mantenendo solo la prima occorrenza (che ora è ordinata cronologicamente)
          righe_prima = len(df_unificato)
          df_unificato = df_unificato.drop_duplicates(subset=colonne_confronto, keep='first')
          righe_dopo = len(df_unificato)
          
          print(f"[*] Rimozione duplicati completata: rimosse {righe_prima - righe_dopo} righe duplicate.")
          
          # Sostituiamo i NaN rimanenti con stringhe vuote per evitare conflitti con le API di Google
          df_unificato = df_unificato.fillna("")
          print('---- Stampo dataframe da scrivere ----')
          print(df_unificato.to_string())
          print('---- Fine Stampa dataframe da scrivere ----')
          #Aggiungo la colonna
          df_unificato['AMOUNT MAX'] = df_unificato['amount'].apply(extract_max_amount)
          # 5. Sovrascrittura su Google Sheet
          # Convertiamo l'intero DataFrame unificato, ordinato e pulito in una lista di liste
          listPrint = df_unificato.values.tolist()
          
          # Calcoliamo l'indice dell'ultima riga per definire l'intervallo di scrittura
          # (+2 perché gli indici delle righe di Google Sheets partono da 1 e la riga 1 è riservata alle intestazioni)
          lastRowSt = str(len(listPrint) + 1)
          dest_range = f'tab_politici!A2:Q{lastRowSt}'
          
          print(f"[*] Scrittura di {len(listPrint)} righe totali sull'intervallo {dest_range}...")
          # Utilizziamo write_range per sovrascrivere l'intera tabella a partire dalla riga 2
          write_range(dest_range, listPrint, newPrj)
          print("[+] Scrittura e riordinamento completati con successo.")
    else:
        print(f"[!] Errore: {response.status_code}")
        print("Dettagli errore dal server:", response.text)


#print(get_all_house_data())