#DESCRIZIONE:
#Leggo i pdf che salvo manualmente in MF-EasyPortfolio
#prendo solo quelli degli ultimi 6 mesi
#faccio parsing per avere le tabelle dei portafogli misti
#stampo i dataframe su google sheet come database
#trovo le variazioni (se serve)

PDF_FOLDER = '/content/drive/MyDrive/Programmazione-COLAB/PRJ-Portfolio/MF-EasyPortfolio' 
import os
import re
import pandas as pd
from datetime import datetime
import camelot
import fitz # PyMuPDF
from functions_sheets import delete_range,appendRow,read_range
from settings import * #importa variabili globali


def extract_content_under_low_risk_portfolio_extended(folder_path):
    """
    Identifica il PDF più recente, cerca la pagina con il percorso titoli:
    "Portafogli Misti" -> "Portafoglio Basso Rischio"
    e tenta di estrarre tutte le tabelle da quel punto fino alla fine della pagina
    o dalle pagine successive.

    Args:
        folder_path (str): Il percorso della cartella contenente i PDF.

    Returns:
        tuple: Un tuple contenente (data_pdf_piu_recente, DataFrame_combinato)
               o (None, None) se il file o la sezione non vengono trovati.
    """
    latest_pdf_info = None
    
    print(f"Ricerca del PDF più recente nella cartella: {folder_path}")

    # 1. Trova il PDF più recente
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf") and re.match(r'^\d{2}-\d{2}-\d{2}', filename):
            try:
                date_str = filename[:8]
                file_date = datetime.strptime(date_str, '%y-%m-%d').date()

                if latest_pdf_info is None or file_date > latest_pdf_info['date']:
                    latest_pdf_info = {'filename': filename, 'date': file_date}
            except ValueError:
                print(f"Errore nel parsing della data dal file '{filename}'. Skippo.")
                continue

    if latest_pdf_info is None:
        print("Nessun PDF valido trovato nella cartella con il formato 'AA-MM-GG-nomefile.pdf'.")
        return None, None

    latest_file_path = os.path.join(folder_path, latest_pdf_info['filename'])
    print(f"Processando il file più recente: '{latest_pdf_info['filename']}' (Data: {latest_pdf_info['date'].strftime('%Y-%m-%d')})")

    all_extracted_dfs = []
    start_page_to_search = -1
    y_start_on_first_page = -1

    try:
        doc = fitz.open(latest_file_path)
        
        # PRIMA PASSATA: Trova la pagina e la posizione del titolo di partenza
        for p_num in range(len(doc)):
            page = doc.load_page(p_num)
            text_on_page = page.get_text("text")

            if "Portafogli Misti" in text_on_page:
                #print(f"  Trovato 'Portafogli Misti' a pagina {p_num + 1}.")
                #low_risk_title_instances = page.search_for("Portafoglio Basso Rischio")
                low_risk_title_instances = page.search_for("Portafogli Misti")
                # print('TEST 01')
                # print(page.search_for("CONTROVALORE COMPLESSIVO"))
                # print('TEST 02')
                # print(page.search_for("COMPOSIZIONE DEL PORTAFOGLIO"))
                # print('TEST 03')
                # print(page.search_for("Rischio"))
                # print('TEST 04')
                # print(page.search_for("Banca Generali"))

                
                if low_risk_title_instances:
                    #print(f"    Trovato 'Portafoglio Basso Rischio' a pagina {p_num + 1}.")
                    #print(f"Trovato 'Portafogli Misti' a pagina {p_num + 1}.")
                    start_page_to_search = p_num
                    y_start_on_first_page = low_risk_title_instances[0].y1 + 5 # Inizia appena sotto il titolo
                    # --- AGGIUNGI QUESTE TRE RIGHE PER IL DEBUG ---
                    # pix = page.get_pixmap()
                    # output_image_path = f"/content/drive/MyDrive/Programmazione-COLAB/PRJ-Portfolio/debug_page_{p_num + 1}.png"
                    # pix.save(output_image_path)
                    # print(f"      Pagina di debug salvata come '{output_image_path}'.")
                    # --- FINE RIGHE DEBUG ---
                    # Puoi aggiungere un offset maggiore qui se la tabella è MOLTO più in basso nella stessa pagina
                    # Esempio: y_start_on_first_page = low_risk_title_instances[0].y1 + 150 
                    #print(f"L'estrazione inizierà da pagina {start_page_to_search + 1}, Y: {y_start_on_first_page}")
                    break
        
        if start_page_to_search == -1:
            print("'Portafoglio Basso Rischio' non trovato nel PDF sotto 'Portafogli Misti'.")
            doc.close()
            return None, None

        # SECONDA PASSATA: Estrai tabelle dalle pagine rilevanti
        # Cercheremo da 'start_page_to_search' fino a un certo numero di pagine successive (es. 2 o 3 pagine)
        # o fino alla fine del documento, a seconda di dove si aspetta la tabella.
        # Regola 'max_pages_to_check' in base a quanto la tua tabella potrebbe estendersi.
        max_pages_to_check = 5 # Controlla la pagina di partenza + 4 pagine successive
        
        for current_page_idx in range(start_page_to_search, min(len(doc), start_page_to_search + max_pages_to_check)):
            current_page = doc.load_page(current_page_idx)
            
            y0_area = 0 # Default: dall'alto della pagina
            
            if current_page_idx == start_page_to_search:
                y0_area = y_start_on_first_page # Inizia dal punto calcolato sulla prima pagina
            
            # Area di estrazione: dal bordo sinistro, da y0_area, al bordo destro, fino al fondo della pagina
            table_area_str = f"0,{y0_area},{current_page.rect.width},{current_page.rect.height}" 
            
            #print(f"Processando Pagina {current_page_idx + 1}: Tentativo di estrazione da area: {table_area_str}")

            try:
                tables = camelot.read_pdf(latest_file_path, 
                                          flavor='stream', # Prova 'lattice' se 'stream' non funziona stream
                                          pages=str(current_page_idx + 1), 
                                          table_areas=[table_area_str])
                
                #print(f"Camelot ha trovato {len(tables)} tabelle a pagina {current_page_idx + 1} nell'area definita.")
                
                for table_idx, table in enumerate(tables):
                    df = table.df
                    # Criterio base per considerare la tabella valida (almeno 2 righe di dati e 3 colonne)
                    if not df.empty and df.shape[0] > 1 and df.shape[1] > 2:
                        all_extracted_dfs.append(df)
                        #print(f"Tabella {table_idx + 1} estratta con successo da pagina {current_page_idx + 1}.")
                    else:
                        print(f"Tabella {table_idx + 1} estratta da pagina {current_page_idx + 1} ma vuota o non valida.")

            except Exception as e:
                print(f"Errore durante l'estrazione tabelle da pagina {current_page_idx + 1}: {e}")

        doc.close()
        
        if all_extracted_dfs:
            # Concatena tutti i DataFrames estratti
            combined_df = pd.concat(all_extracted_dfs, ignore_index=True)
            print("\n--- Tutte le tabelle estratte e combinate con successo. ---")
            return latest_pdf_info['date'], combined_df
        else:
            print("\nNessuna tabella valida trovata sotto 'Portafoglio Basso Rischio' nelle pagine esaminate.")
            return None, None

    except Exception as e:
        print(f"Errore generale durante l'elaborazione del PDF '{latest_pdf_info['filename']}': {e}")
        return None, None

##############################################################################
##############################################################################
def read_write_MF_portfolio():
    if __name__ == "__main__":
      pdf_date, low_risk_section_df = extract_content_under_low_risk_portfolio_extended(PDF_FOLDER)
      fulldata = read_range('tab_mf_port!A:A',newPrj)
      dateSheet = fulldata['Data'].iloc[-1]
      datePDF = pdf_date.strftime('%Y-%m-%d')
      print(f"ultima data foglio {dateSheet} data da scrivere {datePDF}")
      if(dateSheet != datePDF):
        if low_risk_section_df is not None:
            print(f"\n--- Contenuto estratto sotto 'Portafoglio Basso Rischio' dal PDF del {pdf_date.strftime('%Y-%m-%d')} ---")
            
            #Portafoglio Basso Rischio
            #cerco la parola "COMPOSIZIONE DEL PORTAFOGLIO" per eliminare le prime righe
            indice_inizio = low_risk_section_df[low_risk_section_df[0].astype(str).str.contains("COMPOSIZIONE DEL PORTAFOGLIO", na=False)].index
            #print(f"Indice da cancellare {indice_inizio}")
            #cerco la parola "COMPOSIZIONE DEL PORTAFOGLIO" per eliminare le prime righe
            indice_fine = low_risk_section_df[low_risk_section_df[0].astype(str).str.contains("Portafoglio Medio Rischio", na=False)].index
            #print(f"Indice da cancellare {indice_fine}")
            df_port_basso_risch = low_risk_section_df.iloc[indice_inizio[0]+1:indice_fine[0]-1]
            # 1. Ottieni i nomi delle colonne dalla prima riga
            nuovi_nomi_colonne = df_port_basso_risch.iloc[0]
            # 2. Assegna questi nomi al DataFrame
            df_port_basso_risch.columns = nuovi_nomi_colonne
            # 3. Rimuovi la prima riga (che ora è diventata l'header)
            df_port_basso_risch = df_port_basso_risch[1:].reset_index(drop=True)
            #Devo togliere le ultime righe fino a che l'elemento sulla colonna 3 ha lunghezza 12
            indice_da_cancellare = []
            for i in range(df_port_basso_risch.index.max(), -1, -1):
              # Ottieni il valore della Colonna 3 per la riga corrente
              valore_colonna3 = df_port_basso_risch.iloc[i, 5]
              if not isinstance(valore_colonna3, str) or len(valore_colonna3) != 12:
                  indice_da_cancellare.append(i)
              else:
                  break
            df_port_basso_risch = df_port_basso_risch.drop(index=indice_da_cancellare)
            #Cancello colonne vuote
            df_port_basso_risch = df_port_basso_risch.drop(columns='Rischio')
            df_port_basso_risch = df_port_basso_risch.drop(columns='')
            #print("Nomi delle colonne (con columns):", df_port_basso_risch.columns.tolist())
            #print(df_port_basso_risch.to_string())
            
            #Portafoglio Medio Rischio
            #indice di fine
            indice_fine_1 = low_risk_section_df[low_risk_section_df[0].astype(str).str.contains("Portafoglio Alto Rischio", na=False)].index
            #filtro dataframe
            df_port_medio_risch = low_risk_section_df.iloc[indice_inizio[1]+1:indice_fine_1[0]-1]
            #imposto i nomi colonne
            nuovi_nomi_colonne_1 = df_port_medio_risch.iloc[0]
            df_port_medio_risch.columns = nuovi_nomi_colonne_1
            df_port_medio_risch = df_port_medio_risch[1:].reset_index(drop=True)
            #tolgo eventuali righe sotto
            indice_da_cancellare = []
            for i in range(df_port_medio_risch.index.max(), -1, -1):
              # Ottieni il valore della Colonna 3 per la riga corrente
              valore_colonna3 = df_port_medio_risch.iloc[i, 5]
              if not isinstance(valore_colonna3, str) or len(valore_colonna3) != 12:
                  indice_da_cancellare.append(i)
              else:
                  break
            df_port_medio_risch = df_port_medio_risch.drop(index=indice_da_cancellare)
            #Cancello colonne vuote
            df_port_medio_risch = df_port_medio_risch.drop(columns='Rischio')
            df_port_medio_risch = df_port_medio_risch.drop(columns='')
            #print("Nomi delle colonne (con columns):", df_port_medio_risch.columns.tolist())
            #print(df_port_medio_risch.to_string())


            #Portafoglio Alto Rischio
            #indice di fine
            indice_fine_3 = low_risk_section_df[low_risk_section_df[1].astype(str).str.contains("Lettura portafogli", na=False)].index
            #filtro dataframe
            df_port_alto_risch = low_risk_section_df.iloc[indice_inizio[2]+1:indice_fine_3[0]-1]
            #imposto i nomi colonne
            nuovi_nomi_colonne_2 = df_port_alto_risch.iloc[0]
            df_port_alto_risch.columns = nuovi_nomi_colonne_2
            df_port_alto_risch = df_port_alto_risch[1:].reset_index(drop=True)
            #tolgo eventuali righe sotto
            indice_da_cancellare = []
            for i in range(df_port_alto_risch.index.max(), -1, -1):
              # Ottieni il valore della Colonna 3 per la riga corrente
              valore_colonna3 = df_port_alto_risch.iloc[i, 5]
              if not isinstance(valore_colonna3, str) or len(valore_colonna3) != 12:
                  indice_da_cancellare.append(i)
              else:
                  break
            df_port_alto_risch = df_port_alto_risch.drop(index=indice_da_cancellare)
            #Cancello colonne vuote
            df_port_alto_risch = df_port_alto_risch.drop(columns='Rischio')
            df_port_alto_risch = df_port_alto_risch.drop(columns='')
            #print("Nomi delle colonne (con columns):", df_port_medio_risch.columns.tolist())
            #print(df_port_alto_risch.to_string())

            #Aggiungo due colonne

            todayDate = datetime.today().strftime('%d/%m/%Y')
          
            df_port_basso_risch.insert(loc=0, column="Type", value="Basse")
            df_port_medio_risch.insert(loc=0, column="Type", value="Medio")
            df_port_alto_risch.insert(loc=0, column="Type", value="Alto")
            df_port_basso_risch.insert(loc=0, column="Date", value=pdf_date.strftime('%Y-%m-%d'))
            df_port_medio_risch.insert(loc=0, column="Date", value=pdf_date.strftime('%Y-%m-%d'))
            df_port_alto_risch.insert(loc=0, column="Date", value=pdf_date.strftime('%Y-%m-%d'))

            print("###Portafoglio Basso Rischio")
            print(df_port_basso_risch.to_string())
            print("###Portafoglio Medio Rischio")
            print(df_port_medio_risch.to_string())
            print("###Portafoglio Alto Rischio")
            print(df_port_alto_risch.to_string())

            #inserisco su foglio tab_mf_port
            list_data_01 = df_port_basso_risch.values.tolist()
            list_data_02 = df_port_medio_risch.values.tolist()
            list_data_03 = df_port_alto_risch.values.tolist()

            appendRow('tab_mf_port!A:I',list_data_01,newPrj)
            appendRow('tab_mf_port!A:I',list_data_02,newPrj)
            appendRow('tab_mf_port!A:I',list_data_03,newPrj)
            return "OK"
      else:
        return "NOT NECESSARY"    
              
    else:
        print("\nImpossibile estrarre la sezione desiderata. Controlla i log sopra per i dettagli.")
        return 'KO'

print(read_write_MF_portfolio())