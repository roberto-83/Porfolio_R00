from bs4 import BeautifulSoup 
from functions_sheets import delete_range,appendRow,read_range
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
  fulldata = read_range('tab_op_tr!A:A',newPrj)
  if(len(fulldata) == 0):
    status = 1 #proseguo
  else:
    dateSheet = fulldata['Data'].iloc[-1]
    print(f"ultima data del foglio {dateSheet} e oggi è {todayDate}")
    if dateSheet == todayDate :
      status = 0 #non faccio nulla
    else:
      status = 1 #proseguo
  return status

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
      val_stock['Rating_Num'],val_stock['TargetPrice'],val_stock['PNC'],val_stock['PERC_PNC'],val_stock['URL'],val_stock['prova']))
      print(list_data[index])
    #print(list_data)
    ########STAMP
    #
    appendRow('tab_op_tr!A:I',list_data,newPrj)
    return "OK"
  else:
    return "NOT NECESSARY"

#print(read_singl_stock("https://www.operativetrading.it/analisi-tecnica-A2A/"))
#print(read_singl_stock("https://www.operativetrading.it/analisi-tecnica-brunello-cucinelli/"))
print(all_stocks())











