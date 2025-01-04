import json
from datetime import date,timedelta
import calendar
import psycopg
from psycopg import sql
import os
import re
    
def apiCall(mode:str, dates:str = ((date.today()-timedelta(1)).strftime('%d.%m.%Y')), year = (date.today().year), expand:bool = False):

    if len(dates) == 10 and bool(re.match('^(3[01]|[12][0-9]|0[1-9]).(0[1-9]|1[012]).(202[0-9]|203[0-9])$', dates)):
        year = dates[-4:]
    else:
        year = year

    def checkDateValidity(m,d):
        if m == 'm':
            if any([(bool(re.match('^(3[01]|[12][0-9]|0[1-9]).(0[1-9]|1[012]).(202[0-9]|203[0-9])$', d))), (bool(re.match('^(0[1-9]|1[012])$', d))), (bool(re.match('^([1-9]|1[012])$', d)))]):
                return True
            else:
                return False
        elif m == 'd' or 'w':
            if bool(re.match('^(3[01]|[12][0-9]|0[1-9]).(0[1-9]|1[012]).(202[0-9]|203[0-9])$', d)):
                return True
            else:
                return False
        else:
            return False
        
    def checkIsFutureDate(d,y):
        if len(d) == 10 and bool(re.match('^(3[01]|[12][0-9]|0[1-9]).(0[1-9]|1[012]).(202[0-9]|203[0-9])$', d)):
            if int(y) > date.today().year:
                return True
            elif int(y) == date.today().year and int(d[-7:-5]) > date.today().month:
                return True
            elif int(y) == date.today().year and int(d[-7:-5]) == date.today().month and int(d[-10:-8]) > date.today().day:
                return True
        elif len(d) == 2 and bool(re.match('^(0[1-9]|1[012])$', d)) and int(d) > date.today().month and int(y) >= date.today().year:
            return True
        elif len(d) == 1 and bool(re.match('^([1-9]|1[012])$', d)) and int(d) > date.today().month and int(y) >= date.today().year:
            return True
        else:
            return False
        
    def checkIsPastDate(m,d,y):
        if int(y) < 2024:
            if any([(len(d) == 10 and bool(re.match('^(3[01]|[12][0-9]|0[1-9]).(0[1-9]|1[012]).(202[0-9]|203[0-9])$', d)) and int(d[-7:-5]) < 12), (len(d) == 2 and bool(re.match('^(0[1-9]|1[012])$', d)) and int(d) < 12), (len(d) == 1 and bool(re.match('^([1-9]|1[012])$', d)) and int(d) < 12)]):
                return True
            elif m == 'd' and bool(re.match('^(3[01]|[12][0-9]|0[1-9]).(0[1-9]|1[012]).(202[0-9]|203[0-9])$', d)) and int(d[-10:-8]) < 11:
                return True
            else:
                return False
        else:
            return False

    try:
        #check validity of input
        if mode not in ['d','w','m']:
            raise Exception('Invalid mode. Please select d for day, w for week or m for month.')
        
        elif mode == 'd' and dates == date.today().strftime('%d.%m.%Y'):
            raise Exception("Date cannot be today in mode 'd' as this value will only be available the next day.")

        elif checkDateValidity(mode,dates) == False:
            raise Exception('Invalid date format. Must be dd.mm.yyyy for all modes or just single-digit/two-digit month (m or mm) for mode=m.')
        
        elif checkIsPastDate(mode,dates,year):
            raise Exception('Date cannot be too far in the past.')

        elif checkIsFutureDate(dates,year):
            raise Exception('Date cannot be in the future.')
        
        else:
            #different connect info in .env because of render_to_string which results in multiple quotes (""host")
            conn = psycopg.connect(os.environ.get('POSTGRES_VIEWS'))
            cur = conn.cursor()
            #this happens if input is valid.
            #daily: just a single day, no partial days.
            if mode == 'd':                    
                cur.execute(sql.SQL('SELECT date,power_consumption,comment FROM daily_power WHERE date = {dates};').format(dates=sql.Literal(dates)))
                res = cur.fetchone()
                jsonRes = {'success': 'true', 'result': {'date': res[0], 'power_consumption': res[1], 'comment': res[2] if res[2] is not None else ''}}
            #weekly: multiple steps.
            elif mode == 'w':
                #general preparation: get week lists like in wpc.
                month = dates[-7:-5]
                year = dates[-4:]
                dateList = calendar.Calendar().monthdatescalendar(int(year),int(month.lstrip('0')))
                dateListFormatted = [[elem.strftime('%d.%m.%Y') for elem in list] for list in dateList]
                for elem in dateListFormatted:
                    if dates in elem:
                        weekStart = elem[0]
                        fullWeek = elem
                #full week: if resWeek = None because there is no result for the SQL query, this returns a TypeError (NoneType object is not subscriptable).
                try:
                    cur.execute(sql.SQL("SELECT week,power_consumption FROM weekly_power WHERE week LIKE {weekStart};").format(weekStart=sql.Literal(weekStart + '%')))
                    resWeek = cur.fetchone()
                    cur.execute(sql.SQL(f"SELECT date,power_consumption FROM daily_power WHERE date = '{fullWeek[0]}' OR date = '{fullWeek[1]}' OR date = '{fullWeek[2]}' OR date = '{fullWeek[3]}' OR date = '{fullWeek[4]}' OR date = '{fullWeek[5]}' OR date = '{fullWeek[6]}' ORDER BY id ASC;"))
                    resDays = cur.fetchall()
                    jsonRes = {'success': 'true', 'full_week': 'true', 'result': {'week': resWeek[0], 'power_consumption': resWeek[1], 'days': {resDays[0][0]: resDays[0][1], resDays[1][0]: resDays[1][1], resDays[2][0]: resDays[2][1], resDays[3][0]: resDays[3][1], resDays[4][0]: resDays[4][1], resDays[5][0]: resDays[5][1], resDays[6][0]: resDays[6][1]}}}
                #partial week: this TypeError is caught to return a different format. Includes power consumption up to the last available day.
                except TypeError:
                    cur.execute(sql.SQL(f"SELECT date,power_consumption FROM daily_power ORDER BY id DESC LIMIT 10;"))
                    resDays = cur.fetchall()
                    result = {}
                    prelimPC = 0.0
                    for elem in fullWeek:
                        for x in resDays:
                            if elem == x[0]:
                                result.update({f'{x[0]}': x[1]})
                                prelimPC += x[1]
                    jsonRes = {'success': 'true', 'full_week': 'false', 'preliminary_power_consumption': round(prelimPC,2), 'result': result}        
            #monthly: multiple steps
            elif mode == 'm':
                #general preparation: get 'month' in needed format mm depending on input.
                if len(dates) == 10 and bool(re.match('^(3[01]|[12][0-9]|0[1-9]).(0[1-9]|1[012]).(202[0-9]|203[0-9])$', dates)):
                    month = dates[-7:-5]
                elif len(dates) == 2 and bool(re.match('^(0[1-9]|1[012])$', dates)):
                    month = dates
                elif len(dates) == 1 and bool(re.match('^([1-9]|1[012])$', dates)):
                    month = dates.zfill(2)
                else:
                    raise Exception('Invalid input. Please consult the documentation.')
                #full month: only works if resMonth is not None. Otherwise TypeError is thrown and caught for partial month.
                try:
                    #expand: via expand == True you can add all days of the month and their values. Otherwise, only monthly value is returned.
                    if bool(expand) == True:
                        cur.execute(sql.SQL('SELECT month_year,month_short_name,power_consumption,comment FROM monthly_power WHERE month_year = {month_year};').format(month_year=sql.Literal(str(month) + '.' + str(year))))
                        resMonth = cur.fetchone()
                        cur.execute(sql.SQL(f"SELECT date, power_consumption FROM daily_power WHERE REGEXP_LIKE(date,'^(3[01]|[12][0-9]|0[1-9]).{month}.{year}$') ORDER BY id ASC;"))
                        resDays = cur.fetchall()
                        result = {}
                        for elem in resDays:
                            result.update({f'{elem[0]}': elem[1]})
                        jsonRes = {'success': 'true', 'full_month': 'true', 'expand': 'true', 'result': {'month': {'month_year': resMonth[0], 'month_short_name': resMonth[1], 'power_consumption': resMonth[2], 'comment': resMonth[3] if resMonth[3] is not None else ''}, 'days': result}}
                    else:                
                        cur.execute(sql.SQL('SELECT month_year,month_short_name,power_consumption,comment FROM monthly_power WHERE month_year = {month_year};').format(month_year=sql.Literal(str(month) + '.' + str(year))))
                        res = cur.fetchone()
                        jsonRes = {'success': 'true', 'full_month': 'true', 'expand': 'false', 'result': {'month_year': res[0], 'month_short_name': res[1], 'power_consumption': res[2], 'comment': res[3] if res[3] is not None else ''}}
                #partial month: TypeError is caught to return a different format. Includes power consumption up to the last available day.
                except TypeError:
                    cur.execute(sql.SQL(f"SELECT date, power_consumption FROM daily_power WHERE REGEXP_LIKE(date,'^(3[01]|[12][0-9]|0[1-9]).{month}.{year}$') ORDER BY id ASC;"))
                    res = cur.fetchall()
                    result = {}
                    prelimPC = 0.0
                    for elem in res:
                        result.update({f'{elem[0]}': elem[1]})               
                        prelimPC += elem[1]
                    jsonRes = {'success': 'true', 'full_month': 'false', 'preliminary_power_consumption': round(prelimPC, 2), 'result': result}
            cur.close()
            conn.close()
    except Exception as e:
        jsonRes = {'success': 'false', 'error_message': f'{e}'}
    
    return json.dumps(jsonRes)