#Script che legge tutta la tabella dei BTP sul sito 
#"https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html"
#ora riporta solo la prima riga, capire se serve che esporti tutti 
# tenere presente che sono piu pagine di tabella..

import sys
import time

sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

# Importa le librerie necessarie
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configura le opzioni del browser Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')  # Esegui Chrome in modalità headless
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--enable-javascript")
chrome_options.add_argument('--disable-dev-shm-usage')

# Inizializza il driver di Chrome
driver = webdriver.Chrome( options=chrome_options)

search_url = "https://www.borsaitaliana.it/borsa/obbligazioni/mot/obbligazioni-euro/lista.html"
driver.get(search_url)
#google_finder = driver.find_element(By.TAG_NAME, "table")
isin = driver.find_element(By.XPATH, '//*[@id="fullcontainer"]/main/section/div[4]/article[1]/div[2]/table/tbody/tr[3]/td[1]/a/span').text
desc = driver.find_element(By.XPATH, '//*[@id="fullcontainer"]/main/section/div[4]/article[1]/div[2]/table/tbody/tr[3]/td[2]/span').text
last = driver.find_element(By.XPATH, '//*[@id="fullcontainer"]/main/section/div[4]/article[1]/div[2]/table/tbody/tr[3]/td[3]/span').text
cedo = driver.find_element(By.XPATH, '//*[@id="fullcontainer"]/main/section/div[4]/article[1]/div[2]/table/tbody/tr[3]/td[4]/span').text
scad = driver.find_element(By.XPATH, '//*[@id="fullcontainer"]/main/section/div[4]/article[1]/div[2]/table/tbody/tr[3]/td[5]/span').text
link = driver.find_element(By.XPATH, '//*[@id="fullcontainer"]/main/section/div[4]/article[1]/div[2]/table/tbody/tr[3]/td[1]/a').get_attribute("href")
print(link)

print(f"ISIN: {isin} DESC: {desc} LAST: {last} CEDOLA: {cedo} SCAD: {scad}")


#print(type(google_finder))
#result_text = google_finder.text
#print(result_text)

driver.quit()
