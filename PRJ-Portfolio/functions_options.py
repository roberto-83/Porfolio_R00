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

##FUNZIONI APPOGGIO
# ============================================================
# FUNZIONI DI UTILITÀ
# ============================================================

def parse_number(value):

        if value is None:
            return None

        value = str(value).strip()

        if value in ["", "-", "--", "N/A", "n/a"]:
            return None

        try:

            # Caso con punto E virgola:
            # es. 1.234,56 -> 1234.56
            if "." in value and "," in value:
                if value.rfind(",") > value.rfind("."):
                    value = (
                        value
                        .replace(".", "")
                        .replace(",", ".")
                    )

                else:
                    value = (value.replace(",", ""))

            # Solo virgola: es. 2,24 -> 2.24
            elif "," in value:
                value = value.replace(",", ".")

            # Solo punto:es. 2.24 -> 2.24 NON rimuoviamo il punto.

            return float(value)
        except Exception:
            return None


def scadenza_to_yyyymm(scadenza):
        dt = pd.to_datetime(scadenza,dayfirst=True)
        return dt.strftime("%Y%m")


def parse_scadenza(scadenza):
        return pd.to_datetime(scadenza, dayfirst=True)

# ============================================================
# BLACK-SCHOLES
# ============================================================

def black_scholes_price(S,K,T,r, q,sigma,option_type):

        if T <= 0:
            if option_type == "CALL":
                return max(S - K,0)
            else:

                return max(K - S,0)

        if sigma <= 0:

            sigma = 1e-10

        d1 = (
            math.log(S / K)
            +(r - q + 0.5 * sigma ** 2) * T
        ) / (sigma * math.sqrt(T))

        d2 = (d1 - sigma * math.sqrt(T) )

        if option_type == "CALL":

            price = (
                S
                * math.exp(-q * T)
                * norm.cdf(d1)

                -

                K
                * math.exp(-r * T)
                * norm.cdf(d2)
            )

        else:

            price = (
                K
                * math.exp(-r * T)
                * norm.cdf(-d2)

                -

                S
                * math.exp(-q * T)
                * norm.cdf(-d1)
            )

        return price
### IV
def implied_volatility(market_price,S,K,T,r,q,option_type    ):

        if market_price is None:
            return np.nan

        if market_price <= 0:
            return np.nan

        if option_type == "CALL":

            intrinsic = max(
                S * math.exp(-q * T)- K * math.exp(-r * T),0)

        else:

            intrinsic = max(
                K * math.exp(-r * T) -S * math.exp(-q * T),0)

        if market_price < intrinsic:
            return np.nan

        low = 1e-6
        high = 5.0

        price_low = black_scholes_price(S,K,T,r,q,low,option_type)

        price_high = black_scholes_price(S,K,T,r,q,high,option_type)

        if market_price < price_low:
            return np.nan

        if market_price > price_high:
            return np.nan

        for _ in range(200):

            mid_sigma = (low + high) / 2

            price = black_scholes_price(S,K,T,r,q,mid_sigma,option_type)

            if abs(
                price - market_price
            ) < 1e-8:

                return mid_sigma

            if price > market_price:

                high = mid_sigma

            else:

                low = mid_sigma

        return (low + high) / 2
# ============================================================
# FAIR VALUE / BS CON HV
# ============================================================

def fair_value_from_hv(S,K,T,r,q,hv,option_type):

    if hv is None:
      return np.nan

    if np.isnan(hv):
      return np.nan

    return black_scholes_price(S,K,T,r,q,hv,option_type)

###FUNZIONE PRINCIPALE
def analyzeOptions(
    STRIKE_PRICE=2.30,
    C_P='CALL',
    SCADENZA="18/11/2026",
    TICKER_YAHOO="A2A.MI"
):

    # ============================================================
    # ANALISI VOLATILITÀ IMPLICITA OPZIONI
    # Borsa Italiana + Yahoo Finance
    # ============================================================

    URL_BORSA = (
        "https://www.borsaitaliana.it/"
        "borsa/derivati/result/stock-options/lista.html"
    )

    HV_WINDOWS = [30, 60, 120, 252]
    RISK_FREE_RATE = 0.02
    DIVIDEND_YIELD = None
    TRADING_DAYS = 252

    # ============================================================
    # HV DI RIFERIMENTO
    # ============================================================

    def get_hv_riferimento(hv, giorni):

        punti = [
            (30, hv.get(30)),
            (60, hv.get(60)),
            (120, hv.get(120)),
            (252, hv.get(252))
        ]

        punti_validi = [
            (giorni_hv, valore)
            for giorni_hv, valore in punti
            if (
                valore is not None
                and not np.isnan(valore)
            )
        ]

        if not punti_validi:
            return np.nan

        if giorni <= punti_validi[0][0]:
            return punti_validi[0][1]

        if giorni >= punti_validi[-1][0]:
            return punti_validi[-1][1]

        for i in range(
            len(punti_validi) - 1
        ):

            giorni_1, hv_1 = punti_validi[i]

            giorni_2, hv_2 = punti_validi[i + 1]

            if (
                giorni_1
                <= giorni
                <= giorni_2
            ):

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
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/131.0 Safari/537.36"
            ),

            "Accept-Language":
                "it-IT,it;q=0.9,en;q=0.8"
        }

        r = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )

        print(
            "URL finale:",
            r.url
        )

        r.raise_for_status()

        return r.text


    # ============================================================
    # PARSER DELLA CATENA
    # ============================================================

    def trova_riga_strike(
        html,
        strike_target
    ):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        print(
            "Strike cercato:",
            strike_target
        )

        # --------------------------------------------------------
        # TOLLERANZA
        # --------------------------------------------------------

        tolleranza = 1e-6

        for table in soup.find_all("table"):

            for tr in table.find_all("tr"):

                cells = tr.find_all("td")

                if len(cells) < 5:
                    continue

                values = [
                    c.get_text(
                        " ",
                        strip=True
                    )
                    for c in cells
                ]

                # ------------------------------------------------
                # DEBUG
                # ------------------------------------------------

                # print("RIGA:", values)

                # ------------------------------------------------
                # CERCO LO STRIKE
                # ------------------------------------------------

                strike_index = None

                for i, value in enumerate(values):

                    n = parse_number(value)

                    if n is None:
                        continue

                    if abs(
                        n - float(strike_target)
                    ) < tolleranza:

                        strike_index = i

                        break

                if strike_index is None:
                    continue

                print(
                    "STRIKE TROVATO:",
                    values[strike_index],
                    "indice:",
                    strike_index
                )

                # ------------------------------------------------
                # VALORI A SINISTRA / DESTRA
                # ------------------------------------------------

                left = values[:strike_index]

                right = values[
                    strike_index + 1:
                ]

                left_numbers = []

                for x in left:

                    n = parse_number(x)

                    if n is not None:

                        left_numbers.append(n)

                right_numbers = []

                for x in right:

                    n = parse_number(x)

                    if n is not None:

                        right_numbers.append(n)

                # ------------------------------------------------
                # CALL
                # ------------------------------------------------

                if len(left_numbers) >= 2:

                    call_bid = (
                        left_numbers[-2]
                    )

                    call_ask = (
                        left_numbers[-1]
                    )

                else:

                    call_bid = None

                    call_ask = None

                # ------------------------------------------------
                # PUT
                # ------------------------------------------------

                if len(right_numbers) >= 2:

                    put_bid = (right_numbers[-2])

                    put_ask = (right_numbers[-1])

                else:
                    put_bid = None
                    put_ask = None

                print(
                    "CALL BID:",call_bid,
                    "CALL ASK:",call_ask
                )

                print(
                    "PUT BID:",put_bid,
                    "PUT ASK:",put_ask
                )

                return {

                    "strike":float(strike_target),
                    "call_bid": call_bid,
                    "call_ask":call_ask,
                    "put_bid": put_bid,
                    "put_ask":put_ask,
                    "raw_row":values
                }

        print("!!! STRIKE NON TROVATO !!!")
        print("Strike cercato:",strike_target)

        return None


    # ============================================================
    # TROVA STRIKE SOTTO SPOT
    # ============================================================

    def trova_strike_sotto_spot(
        html,
        spot
    ):

        strike_disponibili = []

        tutti_i_numeri = []

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for table in soup.find_all("table"):

            for row in table.find_all("tr"):

                for cell in row.find_all(
                    ["td", "th"]
                ):

                    testo = cell.get_text(
                        " ",
                        strip=True
                    )

                    n = parse_number(testo)

                    if n is not None:

                        tutti_i_numeri.append(n)

                        if n < spot:

                            strike_disponibili.append(n)

        print(
            f"SPOT: {spot}"
        )

        print(
            "TUTTI I NUMERI LETTI:",
            tutti_i_numeri
        )

        print(
            "NUMERI SOTTO LO SPOT:",
            strike_disponibili
        )

        if not strike_disponibili:

            print(
                f"!!! NESSUNO STRIKE "
                f"SOTTO LO SPOT {spot} !!!"
            )

            return None

        strike = max(
            strike_disponibili
        )

        print(
            "STRIKE AUTOMATICO "
            f"SELEZIONATO: {strike}"
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
                "C_P deve essere "
                "'CALL' oppure 'PUT'"
            )

        mid = None

        if (
            bid is not None
            and ask is not None
        ):

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

        stock = yf.Ticker(
            ticker
        )

        hist = stock.history(
            period="2y",
            auto_adjust=False
        )

        if hist.empty:

            raise ValueError(
                f"Nessun dato Yahoo "
                f"trovato per {ticker}"
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

        prices = (
            hist["Close"]
            .dropna()
        )

        log_returns = (
            np.log(
                prices
                / prices.shift(1)
            )
            .dropna()
        )

        result = {}

        for window in windows:

            if len(log_returns) < window:

                result[window] = np.nan

                continue

            vol = (
                log_returns
                .tail(window)
                .std()
                * np.sqrt(
                    TRADING_DAYS
                )
            )

            result[window] = float(
                vol
            )

        return result
  

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
    # NUOVI INDICATORI
    # ============================================================

    def calcola_indicatori_opzione(
        S,
        K,
        T,
        bid,
        ask,
        mid,
        iv_mid,
        hv_riferimento,
        r,
        q,
        option_type
    ):

        indicatori = {

            "iv_hv_diff":
                np.nan,

            # ALIAS ESPLICITO:
            # vol_edge = IV - HV
            "vol_edge":
                np.nan,

            "iv_hv_ratio":
                np.nan,

            "spread":
                np.nan,

            "spread_pct":
                np.nan,

            "log_moneyness":
                np.nan,

            "bs_price_hv":
                np.nan,

            "price_edge_pct":
                np.nan,

            "expected_move_hv":
                np.nan,

            "expected_move_iv":
                np.nan,

            "long_edge_pct":
                np.nan,

            "short_edge_pct":
                np.nan,

            "opportunity_score":
                np.nan
        }


        # ========================================================
        # IV - HV
        # ========================================================

        if (
            iv_mid is not None
            and not np.isnan(iv_mid)

            and hv_riferimento is not None
            and not np.isnan(hv_riferimento)

            and hv_riferimento > 0
        ):

            indicatori["iv_hv_diff"] = (
                iv_mid
                - hv_riferimento
            )

            # ----------------------------------------------------
            # VOL EDGE
            #
            # È esattamente la differenza IV - HV.
            # ----------------------------------------------------

            indicatori["vol_edge"] = (
                iv_mid
                - hv_riferimento
            )

            indicatori["iv_hv_ratio"] = (
                iv_mid
                / hv_riferimento
            )


        # ========================================================
        # BID / ASK SPREAD
        # ========================================================

        if (
            bid is not None
            and ask is not None
            and not np.isnan(bid)
            and not np.isnan(ask)
        ):

            indicatori["spread"] = (
                ask - bid
            )

            if (
                mid is not None
                and not np.isnan(mid)
                and mid > 0
            ):

                indicatori["spread_pct"] = (
                    (ask - bid)
                    / mid
                )


        # ========================================================
        # LOG MONEYNESS
        # ========================================================

        if (
            S is not None
            and K is not None
            and S > 0
            and K > 0
        ):

            indicatori["log_moneyness"] = (
                math.log(K / S)
            )


        # ========================================================
        # BS PRICE CON HV
        # ========================================================

        bs_price_hv = np.nan

        if (
            hv_riferimento is not None
            and not np.isnan(hv_riferimento)
            and hv_riferimento > 0
        ):

            bs_price_hv = (
                fair_value_from_hv(
                    S,
                    K,
                    T,
                    r,
                    q,
                    hv_riferimento,
                    option_type
                )
            )

            indicatori["bs_price_hv"] = (
                bs_price_hv
            )


        # ========================================================
        # PRICE EDGE
        # ========================================================

        if (
            mid is not None
            and not np.isnan(mid)
            and not np.isnan(bs_price_hv)
            and bs_price_hv > 0
        ):

            indicatori["price_edge_pct"] = (
                (mid - bs_price_hv)
                / bs_price_hv
            )


        # ========================================================
        # EXPECTED MOVE CON HV
        # ========================================================

        if (
            hv_riferimento is not None
            and not np.isnan(hv_riferimento)
            and hv_riferimento > 0
        ):

            indicatori["expected_move_hv"] = (
                S
                * hv_riferimento
                * math.sqrt(T)
            )


        # ========================================================
        # EXPECTED MOVE CON IV
        # ========================================================

        if (
            iv_mid is not None
            and not np.isnan(iv_mid)
            and iv_mid > 0
        ):

            indicatori["expected_move_iv"] = (
                S
                * iv_mid
                * math.sqrt(T)
            )


        # ========================================================
        # LONG EDGE
        # ========================================================

        if (
            ask is not None
            and not np.isnan(ask)
            and not np.isnan(bs_price_hv)
            and bs_price_hv > 0
        ):

            indicatori["long_edge_pct"] = (
                (bs_price_hv - ask)
                / bs_price_hv
            )


        # ========================================================
        # SHORT EDGE
        # ========================================================

        if (
            bid is not None
            and not np.isnan(bid)
            and not np.isnan(bs_price_hv)
            and bs_price_hv > 0
        ):

            indicatori["short_edge_pct"] = (
                (bid - bs_price_hv)
                / bs_price_hv
            )


        # ========================================================
        # OPPORTUNITY SCORE - LONG CALL
        # 40% -> Convenienza IV rispetto HV
        # 30% -> Prezzo rispetto Fair Value HV
        # 15% -> Liquidità
        # 15% -> Potenziale movimento
        # ========================================================

        score_components = []

        # --------------------------------------------------------
        # CONVENIENZA VOLATILITÀ
        # IV < HV = positivo
        # IV > HV = negativo
        # --------------------------------------------------------

        if not np.isnan(indicatori["iv_hv_diff"]):

            vol_score = max(
                0,
                min(
                    1 - indicatori["iv_hv_diff"] / 0.20,
                    1
                )
            )

            score_components.append(vol_score * 40)

        # --------------------------------------------------------
        # CONVENIENZA PREZZO
        # prezzo sotto Fair Value = positivo
        # prezzo sopra Fair Value = negativo
        # --------------------------------------------------------

        if not np.isnan(indicatori["price_edge_pct"]):

            price_score = max(
                0,
                min(
                    1 - indicatori["price_edge_pct"] / 0.30,
                    1
                )
            )

            score_components.append(price_score * 30)

        # --------------------------------------------------------
        # LIQUIDITÀ
        # --------------------------------------------------------

        if not np.isnan(indicatori["spread_pct"]):

            liquidity_score = max(
                0,
                1 - indicatori["spread_pct"] / 0.10
            )

            score_components.append(liquidity_score * 15)

        # --------------------------------------------------------
        # POTENZIALE MOVIMENTO
        # --------------------------------------------------------

        if (
            not np.isnan(indicatori["expected_move_hv"])
            and S > 0
        ):

            move_pct = (
                indicatori["expected_move_hv"] / S
            )

            move_score = min(
                move_pct / 0.30,
                1
            )

            score_components.append(move_score * 15)

        if score_components:
            indicatori["opportunity_score"] = round(
                min(sum(score_components), 100),
                1
            )

        return indicatori


    # ============================================================
    # ANALISI PRINCIPALE
    # ============================================================

    def analizza_opzione():

        cp = C_P.upper()

        if cp not in [
            "CALL",
            "PUT"
        ]:

            raise ValueError(
                "C_P deve essere "
                "CALL oppure PUT"
            )


        # ========================================================
        # SCADENZA
        # ========================================================

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

        T = (
            T_days
            / 365.25
        )


        # ========================================================
        # STRIKE
        # ========================================================

        strike_effettivo = (
            STRIKE_PRICE
        )


        # ========================================================
        # YAHOO FINANCE
        # ========================================================

        stock, hist = (
            scarica_storico_yahoo(
                TICKER_YAHOO
            )
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
            f"Strike iniziale : "
            f"{strike_effettivo}"
        )


        # ========================================================
        # DIVIDEND YIELD
        # ========================================================

        q = get_dividend_yield(
            stock
        )


        # ========================================================
        # BORSA ITALIANA
        # ========================================================

        html = scarica_option_chain(
            URL_BORSA,
            TICKER_YAHOO.replace(
                ".MI",
                ""
            ),
            SCADENZA
        )


        # ========================================================
        # DETERMINAZIONE STRIKE
        # ========================================================

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
                f"Cerco il primo strike "
                f"sotto lo spot {S}..."
            )

            strike_effettivo = (
                trova_strike_sotto_spot(
                    html,
                    S
                )
            )


            if strike_effettivo is None:

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
                    "hv_riferimento": 0,
                    "iv_hv_diff": 0,
                    "vol_edge": 0,
                    "iv_hv_ratio": 0,
                    "spread": 0,
                    "spread_pct": 0,
                    "log_moneyness": 0,
                    "bs_price_hv": 0,
                    "price_edge_pct": 0,
                    "expected_move_hv": 0,
                    "expected_move_iv": 0,
                    "long_edge_pct": 0,
                    "short_edge_pct": 0,
                    "opportunity_score": 0
                }


            print("Strike automatico selezionato: {strike_effettivo}")
        else:
            print("Strike inserito manualmente: {strike_effettivo}")


        # ========================================================
        # RICERCA RIGA STRIKE
        # ========================================================

        chain = trova_riga_strike(
            html,
            strike_effettivo
        )


        if chain is None:

            print(f"Strike {strike_effettivo} non trovato per {TICKER_YAHOO}.")

            return {
                "ticker": TICKER_YAHOO,
                "strike":strike_effettivo,
                "call_put":cp,
                "scadenza":expiry,
                "giorni_scadenza":0,
                "spot":0,
                "bid":0,
                "ask":0,
                "mid":0,
                "iv_bid":0,
                "iv_mid":0,
                "iv_ask":0,
                "risk_free":0,
                "dividend_yield":0,
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

                "giudizio":0,
                "hv_riferimento":0,
                "iv_hv_diff":0,
                "vol_edge":0,
                "iv_hv_ratio":0,
                "spread":0,
                "spread_pct":0,
                "log_moneyness":0,
                "bs_price_hv":0,
                "price_edge_pct":0,
                "expected_move_hv":0,
                "expected_move_iv":0,
                "long_edge_pct":0,
                "short_edge_pct":0,
                "opportunity_score": 0
            }


        # ========================================================
        # PREZZI OPZIONE
        # ========================================================

        option_prices = (
            scegli_prezzo_opzione(chain,cp)
        )

        bid = option_prices["bid"]
        ask = option_prices["ask"]
        mid = option_prices["mid"]


        # ========================================================
        # VOLATILITÀ STORICA
        # ========================================================

        hv = (
            calcola_historical_volatility( hist, HV_WINDOWS)
        )


        # ========================================================
        # VOLATILITÀ IMPLICITA
        # ========================================================

        iv_bid = implied_volatility(bid, S, strike_effettivo, T, RISK_FREE_RATE, q, cp)

        iv_mid = implied_volatility(mid,S,strike_effettivo,T,RISK_FREE_RATE,q,cp)

        iv_ask = implied_volatility(ask,S, strike_effettivo,T,RISK_FREE_RATE,q,cp)

        # ========================================================
        # FAIR VALUE PER LE VARIE HV
        # ========================================================

        fair_values = {}

        for window, value in hv.items():

            fair = (
                fair_value_from_hv(S,strike_effettivo,T,RISK_FREE_RATE,q,value,cp)
            )

            fair_values[window] = fair


        # ========================================================
        # HV DI RIFERIMENTO
        # ========================================================

        hv_riferimento = (
            get_hv_riferimento(
                hv,
                T_days
            )
        )


        # ========================================================
        # NUOVI INDICATORI
        # ========================================================

        indicatori = (
            calcola_indicatori_opzione(
                S=S,
                K=strike_effettivo,
                T=T,
                bid=bid,
                ask=ask,
                mid=mid,
                iv_mid=iv_mid,
                hv_riferimento=hv_riferimento,
                r=RISK_FREE_RATE,
                q=q,
                option_type=cp
            )
        )

        # ========================================================
        # GIUDIZIO IV VS HV
        # ========================================================

        if (
            not np.isnan(hv_riferimento)
            and not np.isnan(iv_mid)
        ):

            difference = (iv_mid- hv_riferimento)
            if difference > 0.10:
                giudizio = ("IV MOLTO superiore alla volatilità storica.")
            elif difference > 0.05:
                giudizio = ("IV superiore alla volatilità storica.")
            elif difference < -0.10:
                giudizio = ("IV MOLTO inferiore alla volatilità storica.")
            elif difference < -0.05:
                giudizio = ("IV inferiore alla volatilità storica.")
            else:
                giudizio = ("IV abbastanza vicina alla volatilità storica.")
        else:
            giudizio = ("Dati insufficienti per il confronto.")


        # ========================================================
        # RISULTATO
        # ========================================================

        risultato = {

            "ticker": TICKER_YAHOO,
            "strike": strike_effettivo,
            "call_put": cp,
            "scadenza": expiry,
            "giorni_scadenza": T_days,
            "spot": S,
            "bid": bid,
            "ask": ask,
            "mid":mid,
            "iv_bid":iv_bid,
            "iv_mid": iv_mid,
            "iv_ask":iv_ask,
            "risk_free":RISK_FREE_RATE,
            "dividend_yield": q,
            "historical_volatility": hv,
            "fair_values":fair_values,
            "giudizio":giudizio,

            # ====================================================
            # INDICATORI
            # ====================================================

            "hv_riferimento":
                indicatori[
                    "hv_riferimento"
                ] if "hv_riferimento"
                in indicatori
                else hv_riferimento,

            "bs_price_hv":indicatori["bs_price_hv"],
            "vol_edge":indicatori["vol_edge"],
            "iv_hv_diff":indicatori["iv_hv_diff"],
            "iv_hv_ratio":indicatori["iv_hv_ratio"],
            "price_edge_pct":indicatori["price_edge_pct"],
            "spread":indicatori["spread"],
            "spread_pct":indicatori["spread_pct"],
            "log_moneyness":indicatori["log_moneyness"],
            "expected_move_hv":indicatori["expected_move_hv"],
            "expected_move_iv":indicatori["expected_move_iv"],
            "long_edge_pct":indicatori["long_edge_pct"],
            "short_edge_pct":indicatori["short_edge_pct"],
            "opportunity_score":indicatori["opportunity_score"]
        }


        # ========================================================
        # DEBUG FINALE
        # ========================================================

        print()
        print("=" * 70)
        print("RISULTATO ANALISI")
        print("=" * 70)

        print(f"Ticker : {TICKER_YAHOO}")
        print(f"Spot : {S}" )
        print(f"Strike : {strike_effettivo}")
        print(f"Tipo   : {cp}")
        print(f"Scad.  : {expiry}")
        print(f"BID    : {bid}")
        print(f"ASK    : {ask}")
        print(f"MID    : {mid}")
        print(f"IV MID : {iv_mid}")
        print(f"HV RIF : {hv_riferimento}")
        print(f"VOL EDGE : {indicatori['vol_edge']}")
        print(f"IV-HV  : {indicatori['iv_hv_diff']}")
        print(f"IV/HV  :{indicatori['iv_hv_ratio']}")
        print(f"Spread % : {indicatori['spread_pct']}")
        print(f"BS HV : {indicatori['bs_price_hv']}")
        print(f"Price Edge % : {indicatori['price_edge_pct']}")
        print(f"Long Edge % : {indicatori['long_edge_pct']}")
        print(f"Short Edge % : {indicatori['short_edge_pct']}")
        print(f"Expected Move HV : {indicatori['expected_move_hv']}")
        print(f"Expected Move IV : {indicatori['expected_move_iv']}")
        print(f"Opportunity Score :{indicatori['opportunity_score']}")
        print(f"Giudizio :{giudizio}")

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

    if (pd.isna(scad) or scad == 0):

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
            "GIUDIZIO": 0,
            "HV_RIFERIMENTO": 0,
            "BS_PRICE_HV": 0,
            "VOL_EDGE": 0,
            "PRICE_EDGE_PCT": 0,
            "SPREAD": 0,
            "SPREAD_PCT": 0,
            "LOG_MONEYNESS": 0,
            "EXPECTED_MOVE_HV": 0,
            "EXPECTED_MOVE_IV": 0,
            "LONG_EDGE_PCT": 0,
            "SHORT_EDGE_PCT": 0,
            "OPPORTUNITY_SCORE": 0

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
        "HV_30":result["historical_volatility"].get(30),
        "HV_60":result["historical_volatility"].get(60),
        "HV_120":result["historical_volatility"].get(120),
        "HV_252": result["historical_volatility"].get(252),
        "FAIR_VALUE_30":result["fair_values"].get(30),
        "FAIR_VALUE_60":result["fair_values"].get(60),
        "FAIR_VALUE_120": result["fair_values"].get(120),
        "FAIR_VALUE_252": result["fair_values"].get(252),
        "GIUDIZIO":result["giudizio"],
        "HV_RIFERIMENTO": result["hv_riferimento"],
        "BS_PRICE_HV": result["bs_price_hv"],
        "VOL_EDGE": result["vol_edge"],
        "PRICE_EDGE_PCT": result["price_edge_pct"],
        "SPREAD": result["spread"],
        "SPREAD_PCT": result["spread_pct"],
        "LOG_MONEYNESS": result["log_moneyness"],
        "EXPECTED_MOVE_HV": result["expected_move_hv"],
        "EXPECTED_MOVE_IV": result["expected_move_iv"],
        "LONG_EDGE_PCT": result["long_edge_pct"],
        "SHORT_EDGE_PCT": result["short_edge_pct"],
        "OPPORTUNITY_SCORE": result["opportunity_score"]
    }

    return output

def numero_a_colonna_excel(n):
    risultato = ""

    while n > 0:
        n, resto = divmod(n - 1, 26)
        risultato = chr(65 + resto) + risultato

    return risultato

def optionsCalc():
    #Leggo dati da Google Sheet
    listTicker = read_range("tab_opzion_calc!A:F",newPrj)
    #Normalizzo
    listTicker["PREZZO STRIKE CALL"] = (
        listTicker["PREZZO STRIKE CALL"]
        .astype(str)
        .str.replace(",",".",regex=False
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

    print()
    print("=" * 70)
    print("DATAFRAME FINALE")
    print("=" * 70)

    print(listTicker.to_string())
    #Rimuovo i NaN mettendoli a zero
    listTicker.fillna(0, inplace=True)
    #cambio formato data
    listTicker['DATA'] = listTicker['DATA'].astype(str)
    #Converto in lista
    listPrint = listTicker.values.tolist()
    lastRowSt=str(len(listPrint)+1)
    ultima_colonna = numero_a_colonna_excel(len(listTicker.columns))
    #stampo df
    #write_range('tab_opzion_calc!A2:AM'+lastRowSt,listPrint,newPrj)
    write_range(
      f'tab_opzion_calc!A2:{ultima_colonna}{lastRowSt}',
      listPrint,
      newPrj
    )

    #return listTicker
    return "OK"


#df_finale = optionsCalc()
#print(df_finale)





















