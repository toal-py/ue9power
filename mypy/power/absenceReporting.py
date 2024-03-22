#As my checking of power consumption depends on IPv6 connection, I need an alternative in case I am outside of Germany. This will just send essential info via e-mail.
from datetime import datetime, date, timedelta
import calendar
import dotenv
import psycopg
import os
import sys
import json
import cClasses

dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
sys.path.append('/var/www/python-project/ue9power/mypy')
from apiInternal import apiCall

conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'))
cur = conn.cursor()

cur.execute('SELECT date,power_consumption FROM daily_power ORDER BY id DESC LIMIT 1;')
d = cur.fetchone()

cur.execute('SELECT month_year,power_consumption FROM monthly_power ORDER BY id DESC LIMIT 1;')
m = cur.fetchone()

cur.close()
conn.close()

cm = json.loads(apiCall(mode = 'm'))

def extrapolation(x):
    meanValue = x['preliminary_power_consumption'] / len(x['result'])
    return round(((calendar.monthrange(date.today().year, date.today().month)[1] - len(x['result'])) * meanValue), 2) + x['preliminary_power_consumption']

ep = extrapolation(cm)

def adjustMPower(mp):
    daysCurrentMonth = calendar.monthrange(date.today().year, date.today().month)[1]
    daysLastMonth = calendar.monthrange(date.today().year, ((date.today().replace(day=1))-timedelta(1)).month)[1]

    if type(mp) is not float:
        mp = float(mp)

    if daysLastMonth != daysCurrentMonth:
        adjmp = (mp / daysLastMonth) * daysCurrentMonth
    else:
        adjmp = mp

    return adjmp

normMPower = adjustMPower(m[1])

clm = 1 - (normMPower / float(ep))

# clm = comparison to last month. If <0, then 'weniger'. Else 'mehr'.
# ep = extrapolation of data
compLastMonthPercent = round((abs(clm) * 100), 2)

mailContent = f'''
<p>Tag: {d[0]}<br> Verbrauch: {d[1]} kWh</p>
<p><u>Hochrechnung für den laufenden Monat</u>: {ep} kWh bei weiterhin ähnlichem Verbrauch ({compLastMonthPercent} %* {'weniger' if clm < 0 else 'mehr'} als letzten Monat).</p>
<p><small>*normalisiert an die Anzahl der Tage des Vormonats.</small></p>
'''
mailSubject = f'Abwesenheitsreport für {d[0]}'

absenceReport = cClasses.mailing(mailContent, mailSubject)
absenceReport.sendMail()