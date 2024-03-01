import psycopg
from psycopg.rows import dict_row
import json
import os
import dotenv
from datetime import datetime, date, timedelta
import cClasses

dotenv.read_dotenv('../../.env')
#connection with returning a dict. Basically obsolete as I could fetch 'val' in a tuple as well
conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'), row_factory=dict_row)

cur = conn.cursor()

#execute query to fetch the string with needed values
cur.execute('SELECT ts, val FROM ts_string;')

allLines = cur.fetchall()

#today's 0:00h and yesterday's 0:00h
todayTS = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
yesterdayTS = ((datetime.now()-timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()

#create list of combination: timestamp + total_in.value
dataSetList = []

for elem in allLines:
    elemDict = json.loads(elem['val'])
    listTsVal = [(elem['ts']/1000.0), elemDict['Haus']['total_in'], elem['val']]
    dataSetList.append(listTsVal)
    
#create list of only timestamps to use in following min() function.
timestampList = []

for elem in allLines:
    listTs = (elem['ts']/1000.0)
    timestampList.append(listTs)

#find closest timestamp via function
def getClosestTimestamp (ts):
    closestTimestamp = min(timestampList, key=lambda sub: abs(sub-ts))
    return closestTimestamp

#get closest timestamps to 0:00h of today and yesterday
resClosestTimestampTD = getClosestTimestamp(todayTS)
resClosestTimestampYD = getClosestTimestamp(yesterdayTS)

#find corresponding data set to closest timestamp. True for total_in, False for original value.
def getClosestDataSet (cts,orig):
    for elem in dataSetList:
        if orig == True:
            if elem[0] == cts:
                return (elem[1])
                break
        else:
            if elem[0] == cts:
                return (elem[2])
                break
      
#get data sets to corresponding timestamps
resClosestDatasetTD = getClosestDataSet(resClosestTimestampTD,True)
resClosestDatasetYD = getClosestDataSet(resClosestTimestampYD,True)

#save daily power consumption in a variable, using the closest data sets to 0:00h of today and of yesterday
dailyPowerConsumption = resClosestDatasetTD-resClosestDatasetYD

#date corresponding to the daily power consumption, formatted to dd.mm.YYYY
refYesterday = (date.today()-timedelta(1)).strftime('%d.%m.%Y')

cur.execute(f"INSERT INTO daily_power (date, power_consumption) VALUES ('{refYesterday}', {round(dailyPowerConsumption, 2)})")
conn.commit()

#get original values for logging purposes
logClosestDatasetTD = getClosestDataSet(resClosestTimestampTD,False)
logClosestDatasetYD = getClosestDataSet(resClosestTimestampYD,False)

#logging of original values to be able to check validity of result written to database
dailylog = cClasses.logging(resClosestDatasetTD,resClosestDatasetYD,logClosestDatasetTD,logClosestDatasetYD,refYesterday)
dailylog.writeLogFile()

cur.close()
conn.close()
