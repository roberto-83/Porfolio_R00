from functions_sheets import read_range
from functions_sheets import write_range
from settings import * #importa variabili globali
import datetime
import pandas as pd
from datetime import datetime,timedelta
import time
import sys
import subprocess
import importlib.util
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup 
import requests
import re
import math
import warnings
from scipy.stats import norm
warnings.filterwarnings("ignore")

# qui vado a scansionare il foglio tab_opzion_calc per le call
# se cè un prezzo strike call vado a calcolare i dati e a stamparli
#
#

#KEYS = ["ticker","strike","call_put","scadenza","giorni_scadenza","spot","bid","ask","mid","iv_bid","iv_mid","iv_ask","risk_free","dividend_yield","historical_volatility","fair_values","giudizio"]
#def process_ticker_row(row):
#    strike = row['PREZZO STRIKE CALL']
#    scad = row['SCADENZA CALL']
#    print(analyzeOptions(2.30,'CALL','20/09/2026','A2A.MI'))
#    # Controlla se il valore dello strike è vuoto, NaN, None o pari a 0
#    if pd.isna(strike) or strike == 0 or scad==0 or pd.isna(scad):
#        return dict.fromkeys(KEYS, 0)

    # Chiamata alla tua funzione con i dati della riga
#    dictOutput = analyzeOptions(row['PREZZO STRIKE CALL'], 'CALL',row['SCADENZA CALL'], row['TICKER'])
#    print("tipo di risultato da funzione richiamata in apply")
#    print(type(dictOutput))
#    print(row['PREZZO STRIKE CALL'])
#    print(row['SCADENZA CALL'])
#    print(row['TICKER'])
#    print(dictOutput)
    
#    return dictOutput

#def optionsCalc():
  #leggo i dati 
#  listTicker = read_range('tab_opzion_calc!A:F',newPrj)
  #Normalizzo dati
#  listTicker['PREZZO STRIKE CALL'] = (
 #   listTicker['PREZZO STRIKE CALL']
  #  .astype(str)
  #  .str.replace(',', '.', regex=False)
 # )
#  listTicker['PREZZO STRIKE CALL'] = pd.to_numeric(
 #     listTicker['PREZZO STRIKE CALL'], errors='coerce'
 # )
 # print(listTicker.to_string())
  #calcolo i dati per ogni ticker
# dict_series = listTicker.apply(process_ticker_row, axis=1)
  #trasformo in df
 # results_df = pd.DataFrame(dict_series.tolist())
 # print(results_df)
  #concateno i due df
 # listTicker = pd.concat([listTicker, results_df], axis=1)
  #metto timestamp aggiornato
 # listTicker['DATA'] = pd.Timestamp.now()
 # print(listTicker.to_string())
  #scrivo su google sheet


# ============================================================
# BLOCCO 1
# FUNZIONI DI APPOGGIO + ANALISI OPZIONE
# ============================================================

def analyzeOptions(
    STRIKE_PRICE=2.30,
    C_P='CALL',
    SCADENZA='"18/11/2026"',
    TICKER_YAHOO="A2A.MI"
):

    # ============================================================
    # ANALISI VOLATILITÀ IMPLICITA OPZIONI
    # Borsa Italiana + Yahoo Finance
    # ============================================================

    URL_BORSA = ("https://www.borsaitaliana.it/borsa/derivati/result/stock-options/lista.html")
    HV_WINDOWS = [30, 60, 120, 252]
    RISK_FREE_RATE = 0.02
    DIVIDEND_YIELD = None
    TRADING_DAYS = 252

    # ============================================================
    # FUNZIONI DI UTILITÀ
    # ============================================================

    def parse_number(value):

        if value is None:
            return None

        value = str(value).strip()

        if value in ["", "-", "--", "N/A", "n/a"]:
            return None

        value = value.replace(".", "").replace(",", ".")

        try:
            return float(value)
        except:
            return None


    def scadenza_to_yyyymm(scadenza):

        dt = pd.to_datetime(
            scadenza,
            dayfirst=True
        )

        return dt.strftime("%Y%m")


    def parse_scadenza(scadenza):

        return pd.to_datetime(
            scadenza,
            dayfirst=True
        )

    #FUnzione per reinterpretare il giudizio
    def get_hv_riferimento(hv, giorni):
    
        punti = [
            (30, hv.get(30)),
            (60, hv.get(60)),
            (120, hv.get(120)),
            (252, hv.get(252))
        ]

        # Tengo solo valori validi
        punti_validi = [
            (giorni_hv, valore)
            for giorni_hv, valore in punti
            if valore is not None and not np.isnan(valore)
        ]

        if not punti_validi:
            return np.nan

        # Se siamo prima della prima finestra disponibile
        if giorni <= punti_validi[0][0]:
            return punti_validi[0][1]

        # Se siamo dopo l'ultima finestra disponibile
        if giorni >= punti_validi[-1][0]:
            return punti_validi[-1][1]

        # Interpolazione
        for i in range(len(punti_validi) - 1):

            giorni_1, hv_1 = punti_validi[i]
            giorni_2, hv_2 = punti_validi[i + 1]

            if giorni_1 <= giorni <= giorni_2:

                peso = (
                    giorni - giorni_1
                ) / (
                    giorni_2 - giorni_1
                )

                hv_riferimento = (
                    hv_1
                    +
                    (hv_2 - hv_1) * peso
                )

                return hv_riferimento

        return np.nan
    # ============================================================
    # SCARICA LA CATENA DA BORSA ITALIANA
    # ============================================================

    def scarica_option_chain(
        url,
        ticker,
        scadenza
    ):

        yyyymm = scadenza_to_yyyymm(
            scadenza
        )

        params = {
            "deliveryDate": yyyymm,
            "underlyingId": ticker,
            "grp": "stockoption",
            "lang": "it"
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/131.0 Safari/537.36"
            ),
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.8"
        }

        #print()
        #print("=" * 70)
        #print("BORSA ITALIANA")
        #print("=" * 70)

        r = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        #print(r)
        #print("HTTP:", r.status_code)
        print("URL finale:", r.url)
        r.raise_for_status()

        return r.text


    # ============================================================
    # PARSER DELLA CATENA
    # ============================================================
    
    def trova_riga_strike(html, strike_target):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        #print()
        #print("=" * 70)
        #print("RICERCA STRIKE")
        #print("=" * 70)
        print("Strike cercato:", strike_target)

        for table in soup.find_all("table"):

            for tr in table.find_all("tr"):

                cells = tr.find_all("td")

                if len(cells) < 5:
                    continue

                # Testo delle celle
                values = [
                    c.get_text(" ", strip=True)
                    for c in cells
                ]

                # --------------------------------------------------------
                # CERCO LO STRIKE
                # --------------------------------------------------------

                strike_index = None

                for i, value in enumerate(values):

                    n = parse_number(value)

                    #print(
                    #    f"valore {value!r} -> numero {n}"
                    #)

                    if (
                        n is not None
                        and abs(n - strike_target) < 1e-9
                    ):

                        #print()
                        #print(">>> STRIKE TROVATO <<<")
                        #print("Strike target :", strike_target)
                        #print("Valore pagina :", value)
                        #print("Numero        :", n)
                        #print("Indice        :", i)
                        #print("Riga completa :", values)
                        #print()

                        strike_index = i
                        break

                # Nessuno strike in questa riga
                if strike_index is None:
                    continue

                # --------------------------------------------------------
                # IMPORTANTE:
                # LO STRIKE È STATO TROVATO.
                #
                # Anche se i prezzi sono tutti vuoti, NON dobbiamo
                # scartare la riga.
                # --------------------------------------------------------

                left = values[:strike_index]
                right = values[strike_index + 1:]

                #print("LEFT :", left)
                #print("RIGHT:", right)

                # --------------------------------------------------------
                # ESTRAIAMO I NUMERI A SINISTRA
                # --------------------------------------------------------

                left_numbers = []

                for x in left:

                    n = parse_number(x)

                    if n is not None:
                        left_numbers.append(n)

                # --------------------------------------------------------
                # ESTRAIAMO I NUMERI A DESTRA
                # --------------------------------------------------------

                right_numbers = []

                for x in right:

                    n = parse_number(x)

                    if n is not None:
                        right_numbers.append(n)

                #print("Numeri LEFT :", left_numbers)
                #print("Numeri RIGHT:", right_numbers)

                # --------------------------------------------------------
                # PREZZI CALL
                #
                # Se non ci sono almeno 2 valori numerici, significa
                # che BID/ASK non sono disponibili.
                # --------------------------------------------------------

                if len(left_numbers) >= 2:

                    call_bid = left_numbers[-2]
                    call_ask = left_numbers[-1]

                else:

                    call_bid = None
                    call_ask = None

                # --------------------------------------------------------
                # PREZZI PUT
                # --------------------------------------------------------

                if len(right_numbers) >= 2:

                    put_bid = right_numbers[-2]
                    put_ask = right_numbers[-1]

                else:

                    put_bid = None
                    put_ask = None

                #print("RISULTATO STRIKE")
                #print("Strike   :", strike_target)
                #print("CALL BID :", call_bid)
                #print("CALL ASK :", call_ask)
                #print("PUT BID  :", put_bid)
                #print("PUT ASK  :", put_ask)

                # --------------------------------------------------------
                # LO STRIKE È STATO TROVATO.
                #
                # Restituisco comunque la riga anche se i prezzi sono
                # None.
                # --------------------------------------------------------

                return {
                    "strike": strike_target,
                    "call_bid": call_bid,
                    "call_ask": call_ask,
                    "put_bid": put_bid,
                    "put_ask": put_ask,
                    "raw_row": values
                }

        # ------------------------------------------------------------
        # STRIKE NON PRESENTE NELLA PAGINA
        # ------------------------------------------------------------
        print("!!! STRIKE NON TROVATO !!!")
        print("Strike cercato:", strike_target)
        return None
    
    def trova_strike_sotto_spot(html, spot):

        strike_disponibili = []
        tutti_i_numeri = []

        soup = BeautifulSoup(html, "html.parser")

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                for cell in row.find_all(["td", "th"]):

                    testo = cell.get_text(" ", strip=True)

                    n = parse_number(testo)

                    if n is not None:
                        tutti_i_numeri.append(n)

                        if n < spot:
                            strike_disponibili.append(n)

        print(f"SPOT: {spot}")
        print(f"TUTTI I NUMERI LETTI: {tutti_i_numeri}")
        print(f"NUMERI SOTTO LO SPOT: {strike_disponibili}")

        if not strike_disponibili:
            print(f"!!! NESSUNO STRIKE SOTTO LO SPOT {spot} !!!")
            return None

        strike = max(strike_disponibili)

        print(f"STRIKE AUTOMATICO SELEZIONATO: {strike}")

        return strike

    def trova_strike_sotto_spot_OLD(html, spot):
          strike_disponibili = []
          tutti_i_numeri = []
          soup = BeautifulSoup(
              html,
              "html.parser"
          )

          strike_disponibili = []

          for table in soup.find_all("table"):

              for tr in table.find_all("tr"):

                  cells = tr.find_all("td")

                  if len(cells) < 5:
                      continue

                  values = [
                      c.get_text(" ", strip=True)
                      for c in cells
                  ]

                  # Cerco tutti i numeri presenti nella riga
                  for value in values:

                      n = parse_number(value)

                      if n is None:
                          continue

                      # Considero solo strike sotto lo spot
                      if n < spot:
                          strike_disponibili.append(n)

          print(f"SPOT: {spot}")
          print(f"TUTTI I NUMERI LETTI: {tutti_i_numeri}")
          print(f"NUMERI SOTTO LO SPOT: {strike_disponibili}")
          if not strike_disponibili:

              print(
                  f"!!! NESSUNO STRIKE SOTTO LO SPOT {spot} !!!"
              )

              return None

          # Il più grande tra quelli inferiori allo spot
          strike = max(strike_disponibili)

          print(
              f"Spot: {spot} -> Strike selezionato: {strike}"
          )

          return strike

    # ============================================================
    # PREZZO OPZIONE
    # ============================================================

    def scegli_prezzo_opzione(
        chain,
        call_put
    ):

        if call_put.upper() == "CALL":

            bid = chain["call_bid"]
            ask = chain["call_ask"]

        elif call_put.upper() == "PUT":

            bid = chain["put_bid"]
            ask = chain["put_ask"]

        else:

            raise ValueError(
                "C_P deve essere 'CALL' oppure 'PUT'"
            )

        mid = None

        if bid is not None and ask is not None:

            mid = (
                bid + ask
            ) / 2

        return {
            "bid": bid,
            "ask": ask,
            "mid": mid
        }


    # ============================================================
    # YAHOO FINANCE
    # ============================================================

    def scarica_storico_yahoo(
        ticker
    ):

        #print()
        #print("=" * 70)
        #print("YAHOO FINANCE")
        #print("=" * 70)

        #print("Ticker:", ticker)

        stock = yf.Ticker(
            ticker
        )

        hist = stock.history(
            period="2y",
            auto_adjust=False
        )

        if hist.empty:

            raise ValueError(
                f"Nessun dato Yahoo trovato per {ticker}"
            )

        hist = hist.copy()

        hist = hist[
            hist["Close"].notna()
        ]

        return stock, hist


    # ============================================================
    # SPOT
    # ============================================================

    def get_spot(hist):

        return float(
            hist["Close"].iloc[-1]
        )


    # ============================================================
    # VOLATILITÀ STORICA
    # ============================================================

    def calcola_historical_volatility(
        hist,
        windows
    ):

        prices = hist["Close"].dropna()

        log_returns = np.log(
            prices / prices.shift(1)
        ).dropna()

        result = {}

        for window in windows:

            if len(log_returns) < window:

                result[window] = np.nan

                continue

            vol = (
                log_returns
                .tail(window)
                .std()
                * np.sqrt(TRADING_DAYS)
            )

            result[window] = float(
                vol
            )

        return result
    def get_hv_riferimento(hv, giorni):
        """
        Calcola la volatilità storica di riferimento in funzione
        dei giorni mancanti alla scadenza.

        Usa interpolazione lineare tra le finestre HV disponibili:
        30 -> 60 -> 120 -> 252 giorni.
        """

        punti = [
            (30, hv.get(30)),
            (60, hv.get(60)),
            (120, hv.get(120)),
            (252, hv.get(252))
        ]

        # Mantiene solo i valori validi
        punti_validi = [
            (giorni_hv, valore)
            for giorni_hv, valore in punti
            if valore is not None and not np.isnan(valore)
        ]

        if not punti_validi:
            return np.nan

        # Se la scadenza è prima del primo punto disponibile
        if giorni <= punti_validi[0][0]:
            return punti_validi[0][1]

        # Se la scadenza è oltre l'ultimo punto disponibile
        if giorni >= punti_validi[-1][0]:
            return punti_validi[-1][1]

        # Interpolazione lineare tra i due punti più vicini
        for i in range(len(punti_validi) - 1):

            giorni_1, hv_1 = punti_validi[i]
            giorni_2, hv_2 = punti_validi[i + 1]

            if giorni_1 <= giorni <= giorni_2:

                peso = (giorni - giorni_1) / (giorni_2 - giorni_1)

                hv_riferimento = (
                    hv_1 +
                    (hv_2 - hv_1) * peso
                )

                return hv_riferimento

        return np.nan

    # ============================================================
    # BLACK-SCHOLES
    # ============================================================

    def black_scholes_price(
        S,
        K,
        T,
        r,
        q,
        sigma,
        option_type
    ):

        if T <= 0:

            if option_type == "CALL":

                return max(
                    S - K,
                    0
                )

            else:

                return max(
                    K - S,
                    0
                )

        if sigma <= 0:
            sigma = 1e-10

        d1 = (
            math.log(S / K)
            + (r - q + 0.5 * sigma ** 2) * T
        ) / (
            sigma * math.sqrt(T)
        )

        d2 = d1 - sigma * math.sqrt(T)

        if option_type == "CALL":

            price = (
                S * math.exp(-q * T)
                * norm.cdf(d1)
                -
                K * math.exp(-r * T)
                * norm.cdf(d2)
            )

        else:

            price = (
                K * math.exp(-r * T)
                * norm.cdf(-d2)
                -
                S * math.exp(-q * T)
                * norm.cdf(-d1)
            )

        return price


    # ============================================================
    # IV
    # ============================================================

    def implied_volatility(
        market_price,
        S,
        K,
        T,
        r,
        q,
        option_type
    ):

        if market_price is None:
            return np.nan

        if market_price <= 0:
            return np.nan

        if option_type == "CALL":

            intrinsic = max(
                S * math.exp(-q * T)
                -
                K * math.exp(-r * T),
                0
            )

        else:

            intrinsic = max(
                K * math.exp(-r * T)
                -
                S * math.exp(-q * T),
                0
            )

        if market_price < intrinsic:
            return np.nan

        low = 1e-6
        high = 5.0

        price_low = black_scholes_price(
            S,
            K,
            T,
            r,
            q,
            low,
            option_type
        )

        price_high = black_scholes_price(
            S,
            K,
            T,
            r,
            q,
            high,
            option_type
        )

        if market_price < price_low:
            return np.nan

        if market_price > price_high:
            return np.nan

        for _ in range(200):

            mid = (
                low + high
            ) / 2

            price = black_scholes_price(
                S,
                K,
                T,
                r,
                q,
                mid,
                option_type
            )

            if abs(
                price - market_price
            ) < 1e-8:

                return mid

            if price > market_price:

                high = mid

            else:

                low = mid

        return (
            low + high
        ) / 2


    # ============================================================
    # DIVIDEND YIELD
    # ============================================================

    def get_dividend_yield(
        stock
    ):

        if DIVIDEND_YIELD is not None:
            return DIVIDEND_YIELD

        try:
            info = stock.info

            dy = info.get(
                "dividendYield"
            )

            if dy is not None:

                if dy > 1:
                    dy = dy / 100

                return float(dy)

        except Exception:

            pass

        return 0.0


    # ============================================================
    # FAIR VALUE
    # ============================================================

    def fair_value_from_hv(
        S,
        K,
        T,
        r,
        q,
        hv,
        option_type
    ):

        if np.isnan(hv):
            return np.nan

        return black_scholes_price(
            S,
            K,
            T,
            r,
            q,
            hv,
            option_type
        )


    # ============================================================
    # ANALISI PRINCIPALE
    # ============================================================
    
    def analizza_opzione():

        cp = C_P.upper()

        if cp not in ["CALL", "PUT"]:
            raise ValueError(
                "C_P deve essere CALL oppure PUT"
            )

        # ============================================================
        # SCADENZA
        # ============================================================

        expiry = parse_scadenza(
            SCADENZA
        )

        today = pd.Timestamp.now(
            tz="Europe/Rome"
        ).tz_localize(None)

        T_days = (
            expiry - today
        ).days

        if T_days <= 0:
            raise ValueError(
                "La scadenza è nel passato."
            )

        T = T_days / 365.25

        # ============================================================
        # STRIKE
        #
        # Mantengo STRIKE_PRICE come parametro originale.
        # strike_effettivo sarà lo strike realmente utilizzato
        # nell'analisi.
        # ============================================================

        strike_effettivo = STRIKE_PRICE

        # ============================================================
        # YAHOO FINANCE
        # Recupero SPOT prima di determinare lo strike
        # ============================================================

        stock, hist = scarica_storico_yahoo(
            TICKER_YAHOO
        )

        S = get_spot(
            hist
        )

        print()
        print("=" * 70)
        print("ANALISI OPZIONE")
        print("=" * 70)

        print(
            f"Ticker : {TICKER_YAHOO}"
        )

        print(
            f"Spot   : {S}"
        )

        print(
            f"Strike iniziale : {strike_effettivo}"
        )

        # ============================================================
        # DIVIDEND YIELD
        # ============================================================

        q = get_dividend_yield(
            stock
        )

        # ============================================================
        # BORSA ITALIANA
        # Scarico la catena delle opzioni
        # ============================================================

        html = scarica_option_chain(
            URL_BORSA,
            TICKER_YAHOO.replace(".MI", ""),
            SCADENZA
        )

        # ============================================================
        # DETERMINAZIONE STRIKE
        # ============================================================

        strike_automatico = (
            strike_effettivo is None
            or pd.isna(strike_effettivo)
            or strike_effettivo == 0
        )

        if strike_automatico:

            print()
            print(
                "Strike non specificato."
            )

            print(
                f"Cerco il primo strike sotto lo spot {S}..."
            )

            strike_effettivo = trova_strike_sotto_spot(
                html,
                S
            )

            if strike_effettivo is None:
                print(
                    f"!!! Nessuno strike disponibile sotto lo spot {S} "
                    f"per {TICKER_YAHOO} con scadenza {expiry} !!!"
                )

                return {
                    "ticker": TICKER_YAHOO,
                    "strike": 0,
                    "call_put": cp,
                    "scadenza": expiry,
                    "giorni_scadenza": 0,
                    "spot": 0,
                    "bid": 0,
                    "ask": 0,
                    "mid": 0,
                    "iv_bid": 0,
                    "iv_mid": 0,
                    "iv_ask": 0,
                    "risk_free": 0,
                    "dividend_yield": 0,
                    "historical_volatility": {
                        30: 0,
                        60: 0,
                        120: 0,
                        252: 0
                    },
                    "fair_values": {
                        30: 0,
                        60: 0,
                        120: 0,
                        252: 0
                    },
                    "giudizio": 0,
                    "hv_riferimento": 0
                }

            print(
                f"Strike automatico selezionato: "
                f"{strike_effettivo}"
            )

        else:

            print()
            print(
                f"Strike inserito manualmente: "
                f"{strike_effettivo}"
            )

        # ============================================================
        # RICERCA DELLA RIGA DELLO STRIKE
        # ============================================================

        chain = trova_riga_strike(
            html,
            strike_effettivo
        )

        if chain is None:

          print(
                f"Strike {strike_effettivo} non trovato per "
                f"{TICKER_YAHOO}. Restituisco tutti i valori a 0."
          )

          return {
                "ticker": TICKER_YAHOO,
                "strike": strike_effettivo,
                "call_put": cp,
                "scadenza": expiry,
                "giorni_scadenza": 0,

                "spot": 0,

                "bid": 0,
                "ask": 0,
                "mid": 0,

                "iv_bid": 0,
                "iv_mid": 0,
                "iv_ask": 0,

                "risk_free": 0,
                "dividend_yield": 0,

                "historical_volatility": {
                    30: 0,
                    60: 0,
                    120: 0,
                    252: 0
                },

                "fair_values": {
                    30: 0,
                    60: 0,
                    120: 0,
                    252: 0
                },

                "giudizio": 0
            }

        # ============================================================
        # PREZZI OPZIONE
        # ============================================================

        option_prices = scegli_prezzo_opzione(
            chain,
            cp
        )

        bid = option_prices["bid"]

        ask = option_prices["ask"]

        mid = option_prices["mid"]

        # ============================================================
        # VOLATILITÀ STORICA
        # ============================================================

        hv = calcola_historical_volatility(
            hist,
            HV_WINDOWS
        )

        # ============================================================
        # VOLATILITÀ IMPLICITA
        # ============================================================

        iv_bid = implied_volatility(
            bid,
            S,
            strike_effettivo,
            T,
            RISK_FREE_RATE,
            q,
            cp
        )

        iv_mid = implied_volatility(
            mid,
            S,
            strike_effettivo,
            T,
            RISK_FREE_RATE,
            q,
            cp
        )

        iv_ask = implied_volatility(
            ask,
            S,
            strike_effettivo,
            T,
            RISK_FREE_RATE,
            q,
            cp
        )

        # ============================================================
        # FAIR VALUE
        # ============================================================

        fair_values = {}

        for window, value in hv.items():

            fair = fair_value_from_hv(
                S,
                strike_effettivo,
                T,
                RISK_FREE_RATE,
                q,
                value,
                cp
            )

            fair_values[window] = fair

        # ---------------------------------------------------------
        # HV DI RIFERIMENTO IN FUNZIONE DEI GIORNI ALLA SCADENZA
        # ---------------------------------------------------------

        hv_riferimento = get_hv_riferimento(hv, T_days)

        # ---------------------------------------------------------
        # GIUDIZIO IV vs HV DI RIFERIMENTO
        # ---------------------------------------------------------

        if (
            not np.isnan(hv_riferimento)
            and not np.isnan(iv_mid)
        ):

            difference = iv_mid - hv_riferimento

            if difference > 0.10:
                giudizio = "IV MOLTO superiore alla volatilità storica."

            elif difference > 0.05:
                giudizio = "IV superiore alla volatilità storica."

            elif difference < -0.10:
                giudizio = "IV MOLTO inferiore alla volatilità storica."

            elif difference < -0.05:
                giudizio = "IV inferiore alla volatilità storica."

            else:
                giudizio = "IV abbastanza vicina alla volatilità storica."

        else:

            giudizio = "Dati insufficienti per il confronto."
        

        # ============================================================
        # RISULTATO
        # ============================================================

        risultato = {

            "ticker":TICKER_YAHOO,
            "strike":strike_effettivo,
            "call_put":cp,
            "scadenza":expiry,
            "giorni_scadenza":T_days,
            "spot":S,
            "bid":bid,
            "ask":ask,
            "mid":mid,
            "iv_bid":iv_bid,
            "iv_mid":iv_mid,
            "iv_ask":iv_ask,
            "risk_free":RISK_FREE_RATE,
            "dividend_yield":q,
            "historical_volatility": hv,
            "fair_values":fair_values,
            "giudizio": giudizio,
            "hv_riferimento": hv_riferimento
        }

        # ============================================================
        # DEBUG FINALE
        # ============================================================

        print()
        print("=" * 70)
        print("RISULTATO ANALISI")
        print("=" * 70)

        print(
            f"Ticker : {TICKER_YAHOO}"
        )

        print(
            f"Spot   : {S}"
        )

        print(
            f"Strike : {strike_effettivo}"
        )

        print(
            f"Tipo   : {cp}"
        )

        print(
            f"Scad.  : {expiry}"
        )

        print(
            f"BID    : {bid}"
        )

        print(
            f"ASK    : {ask}"
        )

        print(
            f"MID    : {mid}"
        )

        print(
            f"IV MID : {iv_mid}"
        )

        print(
            f"Giudizio : {giudizio}"
        )

        return risultato
    return analizza_opzione()



# ============================================================
# BLOCCO 2
# FUNZIONE EFFETTIVA
# ============================================================

def process_ticker_row(row):

    # ------------------------------------------------------------
    # Prendo i dati dalla riga del DataFrame
    # ------------------------------------------------------------

    strike = row["PREZZO STRIKE CALL"]
    scad = row["SCADENZA CALL"]
    ticker = row["TICKER"]
    print(f"Inizio con il processo per ticker {ticker}, strike {strike} e scadenza {scad}")

    # ------------------------------------------------------------
    # Controllo valori mancanti
    # ------------------------------------------------------------

    if (
        pd.isna(scad)
        or scad == 0
    ):

        return {
          # Mantengo lo strike originale 
            "PREZZO STRIKE CALL": strike,
            "SPOT": 0,
            "BID": 0,
            "ASK": 0,
            "MID": 0,

            "IV_BID": 0,
            "IV_MID": 0,
            "IV_ASK": 0,

            "RISK_FREE": 0,
            "DIVIDEND_YIELD": 0,

            "HV_30": 0,
            "HV_60": 0,
            "HV_120": 0,
            "HV_252": 0,

            "FAIR_VALUE_30": 0,
            "FAIR_VALUE_60": 0,
            "FAIR_VALUE_120": 0,
            "FAIR_VALUE_252": 0,

            "GIUDIZIO": 0
        }

    # ------------------------------------------------------------
    # Chiamo analyzeOptions()
    # ------------------------------------------------------------

    result = analyzeOptions(
        STRIKE_PRICE=strike,
        C_P="CALL",
        SCADENZA=scad,
        TICKER_YAHOO=ticker
    )

    strike_effettivo = result["strike"] 
    print( f"Strike finale per {ticker}: {strike_effettivo}" )

    # ------------------------------------------------------------
    # Creo una riga piatta
    # ------------------------------------------------------------

    output = {
        "PREZZO STRIKE CALL": strike_effettivo,
        "SPOT": result["spot"],

        "BID": result["bid"],
        "ASK": result["ask"],
        "MID": result["mid"],

        "IV_BID": result["iv_bid"],
        "IV_MID": result["iv_mid"],
        "IV_ASK": result["iv_ask"],

        "RISK_FREE": result["risk_free"],
        "DIVIDEND_YIELD": result["dividend_yield"],

        "HV_30":
            result["historical_volatility"].get(30),

        "HV_60":
            result["historical_volatility"].get(60),

        "HV_120":
            result["historical_volatility"].get(120),

        "HV_252":
            result["historical_volatility"].get(252),

        "FAIR_VALUE_30":
            result["fair_values"].get(30),

        "FAIR_VALUE_60":
            result["fair_values"].get(60),

        "FAIR_VALUE_120":
            result["fair_values"].get(120),

        "FAIR_VALUE_252":
            result["fair_values"].get(252),

        "GIUDIZIO":result["giudizio"]
    }

    return output


def optionsCalc():
    #Leggo dati da Google Sheet
    listTicker = read_range("tab_opzion_calc!A:F",newPrj)
    #Normalizzo
    listTicker["PREZZO STRIKE CALL"] = (
        listTicker["PREZZO STRIKE CALL"]
        .astype(str)
        .str.replace(
            ",",
            ".",
            regex=False
        )
    )

    listTicker["PREZZO STRIKE CALL"] = pd.to_numeric(
        listTicker["PREZZO STRIKE CALL"],
        errors="coerce"
    )
    print("STEP 01 - Stampo DF Iniziale Normalizzato")
    print(listTicker.to_string())
    # ============================================================
    # 3. ANALIZZO OGNI RIGA
    # ============================================================

    dict_series = listTicker.apply(
        process_ticker_row,
        axis=1
    )
   
    # ============================================================
    # 4. TRASFORMO I RISULTATI IN DATAFRAME
    # ============================================================

    results_df = pd.DataFrame(
        dict_series.tolist(),
        index=listTicker.index
    )
    #metto lo strike price che ha calcolato lui
    listTicker["PREZZO STRIKE CALL"] = (
      results_df["PREZZO STRIKE CALL"]
    )
    #tolgo la colonna dai risultati per non averla doppia
    results_df = results_df.drop(
    columns=["PREZZO STRIKE CALL"]
    )
    print(results_df.to_string())
    # ============================================================
    # 5. UNISCO I DUE DATAFRAME
    # ============================================================

    listTicker = pd.concat(
        [
            listTicker,
            results_df
        ],
        axis=1
    )

    # ============================================================
    # 6. AGGIUNGO DATA/ORA
    # ============================================================

    listTicker["DATA"] = pd.Timestamp.now(tz="Europe/Rome")

    # ============================================================
    # 7. STAMPO IL RISULTATO FINALE
    # ============================================================

    print()
    print("=" * 70)
    print("DATAFRAME FINALE")
    print("=" * 70)

    print(
        listTicker.to_string()
    )
    #Rimuovo i NaN mettendoli a zero
    listTicker.fillna(0, inplace=True)
    #cambio formato data
    listTicker['DATA'] = listTicker['DATA'].astype(str)
    #Converto in lista
    listPrint = listTicker.values.tolist()
    lastRowSt=str(len(listPrint)+1)
    #stampo df
    write_range('tab_opzion_calc!A2:AA'+lastRowSt,listPrint,newPrj)

    # ============================================================
    # 8. RESTITUISCO IL DATAFRAME
    # ============================================================

    #return listTicker
    return "OK"


#df_finale = optionsCalc()
#print(df_finale)





















