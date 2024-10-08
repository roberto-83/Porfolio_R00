from functions_sheets import write_range,appendRow
import datetime
from datetime import datetime,timedelta
import time
from settings import * #importa variabili globali
import pytz
#import platform
import os

def log_insert(message,stato):
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")
  arrLog=[[todayDateHour,message,stato]]
  appendRow('tab_log!A:C',arrLog,newPrj)
  return 'ok'
def log_insert1(message,stato,delta,initialTime):
  #hostname = platform.node()
  hostname = f"Sysname: {os.uname()[0]}, release: {os.uname()[2]}, version: {os.uname()[3]}, machine: {os.uname()[4]}, nodename: {os.uname()[1]}"
 #scrivo il delta della singola fase
  if delta != '':
    deltaMin = delta/60
  else:
    deltaMin=''
  #data di oggi
  rome = pytz.timezone("Europe/Rome")
  todDateTime0 = datetime.now(rome)
  todayDateHour  = todDateTime0.strftime("%d/%m/%Y %H:%M:%S")
  #calcolo delta di tutto lo script
  if initialTime != '':
    print(f"initial time {initialTime}")
    timeNow = time.time()
    totTime = (timeNow-initialTime)/60
  else:
    totTime =''
  arrLog=[[todayDateHour,message,stato,deltaMin,totTime,hostname]]
  appendRow('tab_log!A:F',arrLog,newPrj)
  return 'ok'