import psycopg
from datetime import date
import dotenv
import os
import cClasses

dotenv.read_dotenv('/env/.env')

conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'))
cur = conn.cursor()

cur.execute('SELECT month_year, power_consumption FROM monthly_power;')
allData = cur.fetchall()

lastYear = (date.today().year) - 1

def getYearlyPowerConsumption(year:int, data):
    listOfMonths = []
    for elem in data:
        if int(elem[0][-4:]) == year:
            listOfMonths.append(elem[1])

    if len(listOfMonths) != 12:
        errMessage=f'Couldn\'t write yearly power consumption to database due to insufficient amount of values. Got {len(listOfMonths)}, needed 12.'
        errSubject='Error when writing yearly power consumption'
        err=cClasses.mailing(errMessage,errSubject)
        err.sendMail()
    else:
        yearlyPowerConsumption = 0.0
        for elem in listOfMonths:
            yearlyPowerConsumption += elem
        cur.execute(f"INSERT INTO yearly_power (year, power_consumption) VALUES ('{year}', {round(yearlyPowerConsumption, 2)};")
        conn.commit()

#fakeData = [('01.2024', 210.55),('02.2024', 199.6),('03.2024', 194.06),('04.2024', 188.97),('05.2024', 195.17),('06.2024', 204.27),('07.2024', 183.9),('08.2024', 203.96),('09.2024', 169.73),('10.2024', 193.86),('11.2024', 193.86),('12.2024', 193.86)]

getYearlyPowerConsumption(lastYear, allData)

cur.close()
conn.close()
