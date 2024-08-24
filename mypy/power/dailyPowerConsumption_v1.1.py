import psycopg
from psycopg.rows import dict_row
import json
import os
import dotenv
from datetime import datetime, date, timedelta
import cClasses

dotenv.read_dotenv('/var/www/python-project/ue9power/.env')

def checkTimestampValidity (databaseResultList):
    for elem in databaseResultList:
        dictElem = json.loads(elem['val'])
        datetimeObject = datetime.strptime(dictElem['Time'], '%Y-%m-%dT%H:%M:%S')
        if ((datetime.now()).day - datetimeObject.day) > 1:
            databaseResultList.remove(elem)

    return databaseResultList

#connection with returning a dict. Basically obsolete as I could fetch 'val' in a tuple as well
conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'), row_factory=dict_row)

cur = conn.cursor()

#today's 0:00h and yesterday's 0:00h
todayTS = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
yesterdayTS = ((datetime.now()-timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()

#execute query to fetch the string with needed values.
cur.execute(f'SELECT ts,val FROM ts_string WHERE ts BETWEEN {((int(yesterdayTS))-300)*1000} AND {((int(todayTS))+300)*1000};')

allLines = cur.fetchall()

checkTimestampValidity(allLines)

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
def getClosestTimestamp (list,ts):
    closestTimestamp = min(list, key=lambda sub: abs(sub-ts))
    return closestTimestamp

#get closest timestamps to 0:00h of today and yesterday
resClosestTimestampTD = getClosestTimestamp(timestampList,todayTS)
resClosestTimestampYD = getClosestTimestamp(timestampList,yesterdayTS)

#find corresponding data set to closest timestamp. True for total_in, False for original value.
def getClosestDataSet (set,cts,orig):
    for elem in set:
        if orig == True:
            if elem[0] == cts:
                return (elem[1])
        else:
            if elem[0] == cts:
                return (elem[2])
      
#get data sets to corresponding timestamps
resClosestDatasetTD = getClosestDataSet(dataSetList,resClosestTimestampTD,True)
resClosestDatasetYD = getClosestDataSet(dataSetList,resClosestTimestampYD,True)

#date corresponding to the daily power consumption, formatted to dd.mm.YYYY
refYesterday = (date.today()-timedelta(1)).strftime('%d.%m.%Y')

cur.execute(f"INSERT INTO daily_power (date, power_consumption) VALUES ('{refYesterday}', {round((resClosestDatasetTD-resClosestDatasetYD), 2)})")
conn.commit()

#get original values for logging purposes
logClosestDatasetTD = getClosestDataSet(dataSetList,resClosestTimestampTD,False)
logClosestDatasetYD = getClosestDataSet(dataSetList,resClosestTimestampYD,False)

#logging of original values to be able to check validity of result written to database
dailylog = cClasses.logging(resClosestDatasetTD,resClosestDatasetYD,logClosestDatasetTD,logClosestDatasetYD,refYesterday)
dailylog.writeLogFile()

cur.close()
conn.close()
