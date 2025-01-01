import psycopg
import calendar
from datetime import date,timedelta
import dotenv
import os
import cClasses

#connection to DB 'power'
dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
#dotenv.read_dotenv()
conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'))
cur = conn.cursor()
regexMonth = (str(((date.today().replace(day=1))-timedelta(1)).month)).zfill(2)
regexYear = str(((date.today().replace(day=1))-timedelta(1)).year)
cur.execute(f"SELECT date, power_consumption FROM daily_power WHERE REGEXP_LIKE(date,'^(3[01]|[12][0-9]|0[1-9]).{regexMonth}.{regexYear}$');")
allData = cur.fetchall()
#get number of days of the last month like this: (calendar.MONDAY, 31)
#calendar.monthrange((date.today().year),(((date.today().replace(day=1))-timedelta(1)).month))

def getMonthlyPowerConsumption(data,month_days=calendar.monthrange((date.today().year),(((date.today().replace(day=1))-timedelta(1)).month))[1]):
    if len(data) == month_days:
        mpc=0.0
        for elem in data:
            mpc+=elem[1]
        cur.execute(f"INSERT INTO monthly_power (month_year, month_short_name, power_consumption) VALUES ('{(str(((date.today().replace(day=1))-timedelta(1)).month)).zfill(2)}.{((date.today().replace(day=1))-timedelta(1)).year}', '{(calendar.month_abbr[(((date.today().replace(day=1))-timedelta(1)).month)]).upper()}', {mpc});")
        conn.commit() 
    else:
        errMessage=f'Couldn\'t write monthly power consumption to database due to invalid amount of values. Got {len(data)}, needed {month_days}.'
        errSubject='Error when writing monthly power consumption'
        err=cClasses.mailing(errMessage,errSubject)
        err.sendMail()

getMonthlyPowerConsumption(allData)

cur.close()
conn.close()