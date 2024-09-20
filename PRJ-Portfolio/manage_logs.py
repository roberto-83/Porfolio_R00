from functions_sheets import write_range,appendRow
import datetime
from datetime import datetime,timedelta
import time
from settings import * #importa variabili globali
import pytz
import platform


def log_insert(message,stato):
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")
  arrLog=[[todayDateHour,message,stato]]
  appendRow('tab_log!A:C',arrLog,newPrj)
  return 'ok'
def log_insert1(message,stato,delta):
  #hostname = platform.node()
  hostname = platform.node()
  if delta != '':
    deltaMin = delta/60
  else:
    deltaMin=''
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")
  arrLog=[[todayDateHour,message,stato,deltaMin,hostname]]
  appendRow('tab_log!A:E',arrLog,newPrj)
  return 'ok'