import psycopg
import calendar
from datetime import timedelta,date
import dotenv
import os
#connection to DB 'power'
dotenv.read_dotenv('/env/.env')
#dotenv.read_dotenv()
conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'))
cur = conn.cursor()
cur.execute('SELECT * FROM daily_power;')
allData = cur.fetchall()
dateList = calendar.Calendar().monthdatescalendar((date.today().year),(date.today().month)) if date.today().day != 1 else calendar.Calendar().monthdatescalendar((date.today().year),(date.today() - timedelta (1)).month)
#dateListLM = calendar.Calendar().monthdatescalendar(2023,12)
dateListFormatted = [[elem.strftime('%d.%m.%Y') for elem in list] for list in dateList]
#
listVal=[]
for elem in dateListFormatted:
    weekList=[]
    for v in elem:
        for e in allData:
            if v in e:
                weekList.append([e[2], e[1]])
    if len(weekList) == 7:
        listVal.append(weekList)
#
def weeklyPowerConsumption(x):
    weeklyPowerConsumption = 0.0
    weekList={}
    if len(x) != 0:
        for elem in x:      
            for e in elem:
                weeklyPowerConsumption += e[0]       
            weekList.update({f'{elem[0][1]}-{elem[-1][1]}': round(weeklyPowerConsumption,2)})
            weeklyPowerConsumption = 0.0
        return weekList
    else:
        pass

def writeValToDb(dict):
    if dict != None: #else: pass or write something to a log file when I adjusted my logging class
        for elem in list(dict.items()):
            try:
                cur.execute(f"INSERT INTO weekly_power(week, power_consumption) VALUES ('{elem[0]}', {elem[1]});")
                conn.commit()
            except psycopg.errors.UniqueViolation:
                cur.execute('ROLLBACK;')
                continue
    else:
        pass
            
writeValToDb(weeklyPowerConsumption(listVal))

cur.close()
conn.close()