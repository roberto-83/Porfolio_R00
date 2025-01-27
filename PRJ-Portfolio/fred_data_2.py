import pandas as pd
import requests
api_key='a2d856a46ea11c3c186d0935100b4994'

# Funzione per ottenere i dati dal FRED
def get_fred_data(series_id):
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df

# Esempio di indicatore - PIL
#qui c'è il valore attuale e quello previsto
#https://it.investing.com/economic-calendar/gdp-375
#ad oggi, 27/1/25 mi da 3,1 previsto 2,8
#
def get_gdp():
  #legge valore trimestrale
    gdp_data = get_fred_data('GDPC1')  # Id per il PIL reale USA
    print('GDP_DATA')
    print(gdp_data)
    return gdp_data

#link investing https://it.investing.com/economic-calendar/unemployment-rate-300
#attuale(27/1/25) 4.1 , previsto 4.2 data 10/1/2025 -> nell'api ho i dati dei primi di dicembre 2024
def get_unemployee_rate():#tasso disoccupazione
    unemployee_rate = get_fred_data('UNRATE')  # Id per il PIL reale USA
    print('UNEMPLOYE _ RATE')
    print(unemployee_rate)
    return unemployee_rate

def get_inflation():#inflazione
    inflation = get_fred_data('CPIAUCSL')  # Id per il PIL reale USA
    print('INFLATION')
    print(inflation)
    return inflation

def get_tassi():#tassi
    tassi = get_fred_data('FEDFUNDS')  # Id per il PIL reale USA
    print('TASSI')
    print(tassi)
    return tassi

def get_ind_produz():#indice della produzione indistriale
    ind_produz = get_fred_data('INDPRO')  # Id per il PIL reale USA
    print('INDICE PRODUZIONE')
    print(ind_produz)
    return ind_produz

def get_fiducia_consumatori():#indice di fiducia dei consumatori
    fiducia_consumatori = get_fred_data('UMCSENT')  # Id per il PIL reale USA
    print('FIDUCIA CONSUMATORI')
    print(fiducia_consumatori)
    return fiducia_consumatori

def get_borsa():#borsa S&P500
    borsa = get_fred_data('SP500')  # Id per il PIL reale USA
    print('BORSA')
    print(borsa)
    return borsa

# Esempio di analisi
def analyze_economy():
    gdp = get_gdp()
    unemp_get=get_unemployee_rate()
    inflation=get_inflation()
    tassi=get_tassi()
    gdp_growth = gdp['value'].pct_change().mean()  # Crescita media del PIL

    if gdp_growth > 0.02:
        return "Espansione economica"
    elif gdp_growth < -0.02:
        return "Recessione"
    else:
        return "Stagnazione"

# Esegui l'analisi
economic_regime = analyze_economy()
print(f"Attuale regime economico degli Stati Uniti: {economic_regime}")