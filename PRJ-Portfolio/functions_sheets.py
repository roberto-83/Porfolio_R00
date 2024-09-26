#sito https://blog.coupler.io/python-to-google-sheets/
from __future__ import print_function
from auth import spreadsheet_service
from auth import drive_service
from settings import *
import pandas as pd
import time

########################################
############# CREATE SHEET #############
########################################

def create():
    spreadsheet_details = {
    'properties': {
        'title': 'Python-google-sheets-demo'
        }
    }
    sheet = spreadsheet_service.spreadsheets().create(body=spreadsheet_details,
                                    fields='spreadsheetId').execute()
    sheetId = sheet.get('spreadsheetId')
    print('Spreadsheet ID: {0}'.format(sheetId))
    permission1 = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': 'godwinekuma@gmail.com'
    }
    drive_service.permissions().create(fileId=sheetId, body=permission1).execute()
    return sheetId

######################################
############# READ DATA #############
######################################

#def read_range():
    #range_name = 'Sheet1!A2:B5'
    #spreadsheet_id = newPrj
    #result = spreadsheet_service.spreadsheets().values().get(
    #spreadsheetId=spreadsheet_id, range=range_name).execute()
    #rows = result.get('values', [])
    #print('{0} rows retrieved.'.format(len(rows)))
    #print('{0} rows retrieved.'.format(rows))
    #return rows
def read_range(range_name,spreadsheet_id):
    #range_name = 'Sheet1!A2:D30'
    num_retries=3
    for attempt_no in range (num_retries):
      try:
          result = spreadsheet_service.spreadsheets().values().get(
          spreadsheetId=spreadsheet_id, range=range_name).execute()
          rows = result.get('values', [])
          #converto in dataframe per riempire i dati vuoti
          #questo perchè se ci sono celle vuote alla fine del range il metodo non le esporta
          df = pd.DataFrame(rows[0:])
          df.columns = df.iloc[0]
          df = df.drop(axis=0, index=0)
          #print('{0} rows retrieved.'.format(len(rows)))
          #print('{0} rows retrieved.'.format(rows))
      except ValueError as error:
        if(attempt_no <= num_retries):
          print("Error, retry")
          time.sleep(10)
        else:
          raise error
    return df

######################################
############# WRITE DATA #############
######################################

def write_range(range_name,values,spreadsheet_id):
    #range_name = 'Sheet1!A1:B1'
    #values = read_range()
    #values=[["1","2"]]
    value_input_option = 'USER_ENTERED'
    body = {
        'values': values
    }
    result = spreadsheet_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

def appendRow(range_name,values,spreadsheet_id):
    #range_name = 'Sheet1!A1:B1'
    #values = read_range()
    #values=[["1","2"]]
    value_input_option = 'USER_ENTERED'
    body = {
        'values': values
    }
    result = spreadsheet_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    print('cells updated.'.format(result.get('updatedCells')))

######################################
############# DELETE DATA #############
######################################

def delete_range(range_name,spreadsheet_id):
  result = spreadsheet_service.spreadsheets().values().clear(
  spreadsheetId=spreadsheet_id, range=range_name).execute()
  print("Deleted")


#########INFO
#https://developers.google.com/sheets/api/reference/rest?hl=it
#su questo link ci sono le funzioni che si possono usare con i google sheet
#nel caso mio devo guardare le funzioni che si applicano al foglio e non al contenuto
#uso quindi batchUpdate



#write_range()
#read_range()
