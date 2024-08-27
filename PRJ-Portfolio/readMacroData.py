#Qui volgio provare a leggere dei dati macro per capire in che fase del ciclo economico ci si trova
#il codice scritto da chatgpt usa solo il PIL per il momento, ma è un inizio..
#qui perà i vari GDP sono stati messi a mano, forse bisogna leggere i dati da qualche parte

import pandas as pd
import numpy as np

# Supponiamo di avere un DataFrame con i dati del PIL
data = {'year': [2018, 2019, 2020, 2021, 2022],
        'gdp': [2.8, 2.9, -3.5, 5.7, 2.3]}
df = pd.DataFrame(data)

# Calcolo della variazione percentuale del PIL
df['gdp_change'] = df['gdp'].pct_change() * 100

# Funzione per determinare la fase del ciclo economico
def economic_cycle_phase(change):
    if change > 0:
        return 'Espansione'
    elif change < 0:
        return 'Recessione'
    else:
        return 'Stagnazione'

# Applicazione della funzione alla colonna delle variazioni del PIL
df['cycle_phase'] = df['gdp_change'].apply(economic_cycle_phase)

print(df)