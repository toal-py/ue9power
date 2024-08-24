import psycopg
from psycopg.rows import dict_row
import json
import os
import dotenv
from datetime import datetime, date, timedelta
import cClasses

dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
#connection with returning a dict. Basically obsolete as I could fetch 'val' in a tuple as well
conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'), row_factory=dict_row)

cur = conn.cursor()

def checkTimestampValidity (databaseResultList):
    for elem in databaseResultList:
        print (elem['val'])
        print (type(elem['val']))
        dictElem = json.loads(elem['val'])
        print (type(dictElem))
        print (dictElem['Time'])
        datetimeObject = datetime.strptime(dictElem['Time'], '%Y-%m-%dT%H:%M:%S')
        print (datetimeObject)
        print ((datetime.now()).day)
        print (((datetime.now()).day - datetimeObject.day) > 1)
        if ((datetime.now()).day - datetimeObject.day) > 1:
            databaseResultList.remove(elem)

    return databaseResultList

#today's 0:00h and yesterday's 0:00h
todayTS = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
yesterdayTS = ((datetime.now()-timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()

print (f'Today\'s timestamp: {todayTS}\n')
print (f'Yesterday\'s timestamp: {yesterdayTS - 360}\n')

#execute query to fetch the string with needed values. Limit to 6 results with timestamp range.
cur.execute(f'(SELECT ts,val FROM ts_string WHERE ts BETWEEN {((int(yesterdayTS)) - 360)*1000} AND {((int(todayTS))+360)*1000} ORDER BY ts ASC LIMIT 6) UNION (SELECT ts,val FROM ts_string WHERE ts BETWEEN {((int(yesterdayTS)) - 360)*1000} AND {((int(todayTS))+360)*1000} ORDER BY ts DESC LIMIT 6);')

print (f'SELECT query: (SELECT ts,val FROM ts_string WHERE ts BETWEEN {((int(yesterdayTS)) - 360)*1000} AND {((int(todayTS))+360)*1000} ORDER BY ts ASC LIMIT 6) UNION (SELECT ts,val FROM ts_string WHERE ts BETWEEN {((int(yesterdayTS)) - 360)*1000} AND {((int(todayTS))+360)*1000} ORDER BY ts DESC LIMIT 6);\n')

allLines = cur.fetchall()

print (f'Result from database: {allLines}\n')



print (f'Result of cleaned list: {checkTimestampValidity(allLines)}')

print ()

#create list of combination: timestamp + total_in.value
dataSetList = []

for elem in allLines:
    elemDict = json.loads(elem['val'])
    listTsVal = [(elem['ts']/1000.0), elemDict['Haus']['total_in'], elem['val']]
    dataSetList.append(listTsVal)

print (f'List of datasets: {dataSetList}\n')
    
#create list of only timestamps to use in following min() function.
timestampList = []

for elem in allLines:
    listTs = (elem['ts']/1000.0)
    timestampList.append(listTs)

print (f'List of timestamps: {timestampList}\n')

#find closest timestamp via function
def getClosestTimestamp (list,ts):
    closestTimestamp = min(list, key=lambda sub: abs(sub-ts))
    return closestTimestamp

#get closest timestamps to 0:00h of today and yesterday
resClosestTimestampTD = getClosestTimestamp(timestampList,todayTS)
resClosestTimestampYD = getClosestTimestamp(timestampList,yesterdayTS)

print (f'Closest timestamp to today\'s 0:00h: {resClosestTimestampTD}\n')
print (f'Closest timestamp to yesterday\'s 0:00h: {resClosestTimestampYD}\n')

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

print (f'Closest dataset to today\'s 0:00h timestamp: {resClosestDatasetTD}\n')
print (f'Closest dataset to yesterday\'s 0:00h timestamp: {resClosestDatasetYD}\n')

#date corresponding to the daily power consumption, formatted to dd.mm.YYYY
refYesterday = (date.today()-timedelta(1)).strftime('%d.%m.%Y')

print (f'Reference date: {refYesterday}\n')

print (f'SQL query: INSERT INTO daily_power (date, power_consumption) VALUES ({refYesterday}, {round((resClosestDatasetTD-resClosestDatasetYD), 2)}))')
#cur.execute(f"INSERT INTO daily_power (date, power_consumption) VALUES ('{refYesterday}', {round((resClosestDatasetTD-resClosestDatasetYD), 2)})")
#conn.commit()

#get original values for logging purposes
#logClosestDatasetTD = getClosestDataSet(dataSetList,resClosestTimestampTD,False)
#logClosestDatasetYD = getClosestDataSet(dataSetList,resClosestTimestampYD,False)

#logging of original values to be able to check validity of result written to database
#dailylog = cClasses.logging(resClosestDatasetTD,resClosestDatasetYD,logClosestDatasetTD,logClosestDatasetYD,refYesterday)
#dailylog.writeLogFile()

cur.close()
conn.close()
