from functions_sheets import write_range,appendRow
import datetime
from datetime import datetime,timedelta
import time
from settings import * #importa variabili globali
import pytz

def log_insert(message,stato):
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")
  arrLog=[[todayDateHour,message,stato]]
  appendRow('tab_log!A:C',arrLog,newPrj)
  return 'ok'
def log_insert1(message,stato,delta):
  if delta != '':
    deltaMin = delta/60
  else:
    deltaMin=''
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")
  arrLog=[[todayDateHour,message,stato,deltaMin]]
  appendRow('tab_log!A:D',arrLog,newPrj)
  return 'ok'