from bs4 import BeautifulSoup 
from functions_sheets import delete_range,appendRow,read_range,write_range
from settings import * #importa variabili globali
import datetime
from datetime import datetime,timedelta
import time
import requests 
import pandas as pd

#leggo i dati dal sito https://www.operativetrading.it/analisi-tecnica-azioni-italia/

#Leggo lista di azioni dalle due tabelle con il relativo link
def read_stock_fts_mib():
  URL = "https://www.operativetrading.it/analisi-tecnica-azioni-italia/"
  r = requests.get(URL) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  table = soup.find('table', id='tablepress-3')
  number_of_rows = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
  #print(f"Numero di righe della tabella: {number_of_rows}")
  rows = table.find_all('tr')
  data = []
  for row in rows:
    link = row.find('a')
    if link:
      description = link.get_text()
      href = link['href']
      data.append((description, href,'AzioniFtseMib',0))
  df = pd.DataFrame(data, columns=['Descrizione','LINK','Type','Rating'])
  #print(df.to_string())
  return df

def read_stock_cap():
  URL = "https://www.operativetrading.it/analisi-tecnica-azioni-italia/"
  r = requests.get(URL) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  table = soup.find('table', id='tablepress-14')
  number_of_rows = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
  #print(f"Numero di righe della tabella: {number_of_rows}")
  rows = table.find_all('tr')
  data = []
  for row in rows:
    link = row.find('a')
    if link:
      description = link.get_text()
      href = link['href']
      data.append((description, href,'AzioniCap',0))
  df = pd.DataFrame(data, columns=['Descrizione','LINK','Type','Rating'])
  #print(df.to_string())
  return df

def read_commodities():
  URL = "https://www.operativetrading.it/materie-prime-analisi-tecnica/"
  r = requests.get(URL) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  table = soup.find('table', id='tablepress-5')
  number_of_rows = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
  #print(f"Numero di righe della tabella: {number_of_rows}")
  rows = table.find_all('tr')
  data = []
  for row in rows:
    link = row.find('a')
    rating_com = row.find('td', class_='column-2')
    if rating_com:
      rating_com = rating_com.text
    else:
      rating_com=0
    rating_com = str(rating_com).replace("\n","")
    #print(rating_com[1])
    if link:
      description = link.get_text()
      href = link['href']
      data.append((description, href,'Commodities',rating_com))
  df = pd.DataFrame(data, columns=['Descrizione','LINK','Type','Rating'])
  #print(df.to_string())
  return df
#print(read_commodities())

#leggo le 4 tabelle riportate su https://www.operativetrading.it/screener-azioni-italia/
def read_shortlist():
  URL = "https://www.operativetrading.it/screener-azioni-italia/"
  USERNAME = "robpol1983"
  PASSWORD = "Zucchetti1!"
  todayDate = datetime.today().strftime('%d/%m/%Y')
  # URL di login e pagina da scaricare
  LOGIN_URL = "https://www.operativetrading.it/area-riservata/"
  TARGET_URL = URL

  # Inizializza sessione
  session = requests.Session()

  # 1. Carica la pagina di login per prendere eventuali cookie o token (opzionale)
  login_page = session.get(LOGIN_URL)
  soup_login = BeautifulSoup(login_page.text, "html.parser")

  # 2. Prepara i dati per il login
  login_data = {
      "username": USERNAME,
      "pwd": PASSWORD,
      "submit": "Login",
      "redirect_to": TARGET_URL,
      "testcookie": "1",
      "rm_form_sub_id":"rm_login_form_1",
      "rm_form_sub_no":"",
      "rm_slug":"rm_login_form"
  }

  # 3. Fai POST per login
  response = session.post(LOGIN_URL, data=login_data)

  # 4. Accedi alla pagina con le tabelle
  page = session.get(TARGET_URL)
  
  soup = BeautifulSoup(page.text, "html.parser")
  if soup.find("table"):  # o un'altra verifica più specifica
    print("✅ Login riuscito e contenuto accessibile!")
    # 5. Trova tutte le tabelle nella pagina
    tables = soup.find_all("table")

    print(f"Trovate {len(tables)} tabelle")
    list_name_table = [
      'PNC aumento Oggi',
      'PNC diminuzione Oggi',
      'PNC aumento 5 sedute',
      'PNC diminuzione 5 sedute'
    ]

    # 6. Converti le tabelle in DataFrame pandas
    dataframes = []
    for i, table in enumerate(tables[:4]):  # prendiamo le prime 4 tabelle
        df = pd.read_html(str(table))[0]
        df['Data'] = todayDate
        df['Type'] = list_name_table[i]
        df.columns.values[0] = "Titolo"
        df = df[["Data", "Type", "Titolo"]]
        dataframes.append(df)
        # print(f"Tabella {i+1}:")
        # print(df.head())
    final_df = pd.concat(dataframes, ignore_index=True)
    #print(final_df.to_string())
    return final_df
  else:
    print("❌ Login fallito o accesso negato alla pagina.")
    return pd.DataFrame()

#print(read_shortlist())
 



####################################################################
####################################################################

def remove_phrase_at_end(phrase, num_car, text_remove):
  #Divido le frasi
  frasi = phrase.split(".")
  # Rimuovi eventuali spazi vuoti o stringhe vuote dovute alla divisione
  frasi = [frase.strip() for frase in frasi if frase.strip()]
  # Prendi l'ultima frase
  ultima_frase = frasi[-1]
  #print(f"Ulitma frase è :{ultima_frase}")
  #Tolgo la frase se 
  if ultima_frase[:num_car]==text_remove:
    descr = ". ".join(frasi[:-1])
  else: 
    descr=phrase
  return descr

def read_singl_stock(url,type_stock):
  r = requests.get(url) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  #nome stock
  name_stock = soup.find('h1',class_='entry-title').text
  name_stock = name_stock.replace("Analisi tecnica", "").strip()
  name_stock = name_stock.replace("Analisi Tecnica", "").strip()
  #print(name_stock)
  #### LEGGO la descrizione estesa
  if type_stock=='Commodities':
    descrizione=''
  else:
    div = soup.find('div', class_='entry-content clear')
    if div:
      descrizione = div.find('p').text
      #print(descrizione)
    #Tolgo la prima frase
    if descrizione[:9]=='In questa':
      posizione_punto = descrizione.find(".")
      if posizione_punto != -1:
        descrizione = descrizione[posizione_punto +1:].lstrip()
    descrizione = remove_phrase_at_end(descrizione, 13, "Infine potrai")
    descrizione = remove_phrase_at_end(descrizione, 13, "A seguire pot")
    descrizione = remove_phrase_at_end(descrizione, 13, "In seguito po")
    descrizione = remove_phrase_at_end(descrizione, 13, "Potrai quindi")
    descrizione = remove_phrase_at_end(descrizione, 13, "Lo studio ini")
    descrizione = remove_phrase_at_end(descrizione, 13, "In questa pag")

 

  #### LEGGO il rating
  rating_tab = soup.find('table')
  if rating_tab:
    rating = rating_tab.find('td').text.strip()
  else:
    rating='0'
  rating = str(rating).replace("%”>     ","").strip()
  rating = str(rating).replace("%”>     ","").strip()
  #print(rating)
  #### LEGGO rating numero
  rating_num = rating[-3:]
  try:
    rating_num = float(rating_num)
  except ValueError:
    rating_num = 0
  #### LEGGO target price
  name_stock_barrato = name_stock.replace(" ","-")
  print(name_stock_barrato)

  if name_stock_barrato=='Fineco-Bank':name_stock_barrato='Fineco'
  
  list_id = [f"Target-price-{name_stock_barrato}",
            f"Target-Price-{name_stock_barrato}"]
  #i=0
  for li in list_id:
    #print(f"indice {i}")
    h3 = soup.find('h3',id=li)
    #print(h3)
    target_price = read_data_bs(h3)
    #print(target_price)
    #i=i+1
    if target_price !='0':
      break
  target_price = str(target_price).replace("Di seguito riportiamo il consensus di prezzo ottenuto attraverso la media dei giudizi di differenti analisti. ","").strip()
  target_price = str(target_price).replace("Le raccomandazioni delle banche d’affari si basano su fonti ritenute attendibili ma non possiamo garantirne la correttezza.","").strip()
  #modifico struttura per mettere le diciture a capo
  frasi_trg = target_price.split(" . ")
  target_price_mod = " .\n".join(frase.strip() for frase in frasi_trg)

  #### PNC = Posizioni nette corte
  list_id_pnc = [f"Posizioni-corte-nette-Consob-{name_stock_barrato}",
                f"Posizioni-corte-nette-{name_stock_barrato}",
                f"Posizioni-corte-su-azioni-{name_stock_barrato}",
                f"Posizioni-corte-azioni-{name_stock_barrato}"]


  for li in list_id_pnc:
    h3_pnc = soup.find('h3',id=li)
    pnc = read_data_bs(h3_pnc)
    pnc = pnc.replace("Di seguito puoi osservare la tendenza dellePNCdegli investitori professionali nel corso del mese.","").strip()
    pnc = pnc.replace("  Nota che l’unica fonte ufficiale delle PNC è il sito della Consob.  I dati del sito hanno solo scopo di informazione. Il loro utilizzo come supporto alle scelte di trading è a completo rischio dell’utente che se ne assume la piena responsabilità.","").strip()
    percentuale_num=0
    #print(pnc)
    if pnc !='0':
      pnc = remove_phrase_at_end(pnc, 26, "Approfondisci lePNC Consob")
      pnc = remove_phrase_at_end(pnc, 26, "Nota che l’unica fonte uff")
      pnc = remove_phrase_at_end(pnc, 26, "Approfondisci lePNC Consob")
      pnc = remove_phrase_at_end(pnc, 26, "Approfondisci le PNC Conso")
      pnc = remove_phrase_at_end(pnc, 26, "ApprofondisciPNC Consob – ")
      pnc = remove_phrase_at_end(pnc, 26, "Appfofondisci lePNC Consob")
      pnc = remove_phrase_at_end(pnc, 26, "Il loro utilizzo come supp")
      pnc = remove_phrase_at_end(pnc, 26, "I dati del sito hanno solo")
      pnc = remove_phrase_at_end(pnc, 26, "Nota che l’unica fonte uff")
      #tolgo la prima frase
      pnc_indice = pnc.find("sono pari al") #stringa lunga 12 piu uno di spazio..
      pnc = pnc[pnc_indice+13:]#estraggo tutto ciò che è dopo il testo 
      pnc=pnc.replace(" del capitale sociale, ","")
      #tolgo "rispetto alla seduta precedente"
      pnc=pnc.replace("rispetto alla seduta precedente","")
      #sistemo la percentuale
      pos_perc = pnc.find("%")
      percentuale = pnc[:pos_perc]
      try:
        percentuale=percentuale.replace(" ","")
        percentuale_num = float(percentuale)
      except ValueError:
        percentuale_num = 0
      #print(percentuale)
      break
 
  if target_price == '0':
      print("controlla target price")
  if pnc == '0':
      print("controlla PNC")
  #print(testo_finale_pnc)
  df = ({'Nome' : name_stock , 'Descrizione' : descrizione, 'Rating':rating, 'Rating_Num':rating_num,\
   'TargetPrice':target_price_mod, 'PNC':pnc ,'PERC_PNC':percentuale_num,"URL":url,"prova":''})
  return df

def read_data_bs(h3):
  if h3:  
    contents = []
    for sibling in h3.next_siblings:
      #print(sibling)
      if sibling.name == 'h3':
          break  # fermati se trovi il prossimo h3
      if isinstance(sibling, str):
          contents.append(sibling.strip())
      else:
          contents.append(sibling.get_text(strip=True))
    return ' '.join(contents).strip()
  else:
    return "0"


def readlastDate(tab):
  todayDate = datetime.today().strftime('%d/%m/%Y')
  fulldata = read_range(tab+'!A:A',newPrj)
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

#Funzone per scrivere la shortlist delle PNC
def write_short_list():
  print("##Scrivo i dati della shortlist")
  todayDate = datetime.today().strftime('%d/%m/%Y')
  tab1 = read_shortlist()
  #print(readlastDate('tab_op_tr'))
  if readlastDate('tab_pnc') == 1:
    if not tab1.empty:
      list_data = tab1.values.tolist()
      appendRow('tab_pnc!A:C',list_data,newPrj)
      CalcoloMediana = cal_mediana()
      return "OK"
    else:
      print("################ Errore lettura dati")
      return "KO"
  else:
    return "NOT NECESSARY"


def all_stocks():
  todayDate = datetime.today().strftime('%d/%m/%Y')
  #print(readlastDate('tab_op_tr'))
  if readlastDate('tab_op_tr') == 1:
    tab1 = read_stock_fts_mib()
    tab2 = read_stock_cap()
    tab3 = read_commodities()
    df = pd.concat([tab1, tab2, tab3], ignore_index=True)
    list_data = []
    for index,row in df.iterrows():
      print(f"Indice {index} e riga {row['Descrizione']} con link {row['LINK']}")
      val_stock = read_singl_stock(row['LINK'],row['Type'])
      list_data.append((todayDate,row['Type'],val_stock['Nome'], val_stock['Descrizione'],\
      val_stock['Rating_Num'],val_stock['TargetPrice'],val_stock['PNC'],val_stock['PERC_PNC'],val_stock['URL'],todayDate+"--"+val_stock['Nome']))
      print(list_data[index])
    #print(list_data)
    ########STAMP
    #
    appendRow('tab_op_tr!A:J',list_data,newPrj)
    return "OK"
  else:
    return "NOT NECESSARY"
####################################################
# ANALISI DATO
####################################################
def cal_mediana():#calcolo i valori mediani negli ultimi 5 gg
  todayDate = datetime.today().strftime('%d/%m/%Y')
  all_range = read_range('tab_op_tr!A:E',newPrj)
  all_range = all_range.drop('Descrizione', axis=1)
  all_range['Rating']=all_range['Rating'].str.replace(",",".")
  #print(all_range.to_string())
  #voglio un dataframe che riporti le prime azioni che hanno una mediana alta
  #negli ultimi n giorni
  n_giorni = 7
  mediana_df = all_range
  mediana_df['Data'] = pd.to_datetime(mediana_df['Data'])
  mediana_df = mediana_df.sort_values(by=['Stock', 'Data'], ascending=True)
  mediana_df['Mediana_5gg'] = mediana_df.groupby('Stock')['Rating'].rolling(window=n_giorni, min_periods=1).median().reset_index(level=0, drop=True)
  #print(mediana_df.to_string())
  df_azioni_uniche_con_mediana = mediana_df.groupby('Stock').tail(1).reset_index(drop=True)
  df_azioni_uniche_con_mediana = df_azioni_uniche_con_mediana.sort_values(by=['Mediana_5gg'], ascending=False)
  #print(df_azioni_uniche_con_mediana.to_string())
  df_to_print=prime_10_righe = df_azioni_uniche_con_mediana.head(10)
  df_to_print['Data'] = todayDate
  list_data = df_to_print.values.tolist()
  write_range('tab_op_tr!M2:Q11',list_data,newPrj)
  return'OK'


print(cal_mediana())
#print(read_singl_stock("https://www.operativetrading.it/analisi-tecnica-A2A/"))
#print(read_singl_stock("https://www.operativetrading.it/analisi-tecnica-brunello-cucinelli/"))
#print(all_stocks())













