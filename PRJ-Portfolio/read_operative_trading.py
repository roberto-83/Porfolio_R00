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
      data.append((description, href))
  df = pd.DataFrame(data, columns=['Descrizione','LINK'])
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
      data.append((description, href))
  df = pd.DataFrame(data, columns=['Descrizione','LINK'])
  #print(df.to_string())
  return df

####################################################################
####################################################################

def read_singl_stock(url):
  r = requests.get(url) 
  soup = BeautifulSoup(r.content, 'html5lib') 
  #nome stock
  name_stock = soup.find('h1',class_='entry-title').text
  name_stock = name_stock.replace("Analisi tecnica", "").strip()
  name_stock = name_stock.replace("Analisi Tecnica", "").strip()
  #print(name_stock)
  #escrizione estesa
  div = soup.find('div', class_='entry-content clear')
  if div:
    descrizione = div.find('p').text
    #print(descrizione)
  #rating
  rating_tab = soup.find('table')
  if rating_tab:
    rating = rating_tab.find('td').text.strip()
  else:
    rating='0'
  #print(rating)
  #### target price
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

  #### PNC = Posizioni nette corte
  list_id_pnc = [f"Posizioni-corte-nette-Consob-{name_stock_barrato}",
                f"Posizioni-corte-nette-{name_stock_barrato}",
                f"Posizioni-corte-su-azioni-{name_stock_barrato}",
                f"Posizioni-corte-azioni-{name_stock_barrato}"]


  for li in list_id_pnc:
    h3_pnc = soup.find('h3',id=li)
    pnc = read_data_bs(h3_pnc)
    pnc = pnc.replace("Di seguito puoi osservare la tendenza dellePNCdegli investitori professionali nel corso del mese.","").strip()
    #print(pnc)
    if pnc !='0':
      break
  if target_price == '0':
      print("controlla target price")
  if pnc == '0':
      print("controlla PNC")
  #print(testo_finale_pnc)
  df = ({'Nome' : name_stock , 'Descrizione' : descrizione, 'Rating':rating, 'TargetPrice':target_price, 'PNC':pnc})
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
    df = pd.concat([tab1, tab2], ignore_index=True)
    list_data = []
    for index,row in df.iterrows():
      print(f"Indice {index} e riga {row['Descrizione']} con link {row['LINK']}")
      val_stock = read_singl_stock(row['LINK'])
      list_data.append((todayDate,val_stock['Nome'], val_stock['Descrizione'],val_stock['Rating'],val_stock['TargetPrice'],val_stock['PNC']))
      print(list_data[index])
    #print(list_data)
    ########STAMP
    #
    appendRow('tab_op_tr!A:F',list_data,newPrj)
    return "OK"
  else:
    return "NOT NECESSARY"

#print(read_singl_stock("https://www.operativetrading.it/analisi-tecnica-amplifon/"))
#print(all_stocks())
