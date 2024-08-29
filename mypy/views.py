# here, we render html

from django.http import HttpResponse
import json
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime, date, timedelta
import calendar
import dotenv
import psycopg
from psycopg import sql
import pandas as pd
import math
import os
import redis
from multiprocessing import Pool
from django.views.decorators.cache import cache_page

from mypy.apiInternal import apiCall
from mypy.plotView import plotMonthlyOverview, plotComparison, getShareValues, plotMonthlyShare
from mypy.createDataForPlotPage import createDataForPlotPage

def homeView(request):
    htmlString = "<h1>Hello World</h1><p><a href='/power'>Hier geht es zum letzten Stromverbrauch</a></p>" 
    return HttpResponse(htmlString)
#caching
@cache_page(21600)
@ensure_csrf_cookie
def powerOverview (request):
    dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
    #different connect info in .env because of render_to_string which results in multiple quotes (""host")
    conn = psycopg.connect(os.environ.get('POSTGRES_VIEWS'))
    cur = conn.cursor()
    cur.execute('SELECT date,power_consumption FROM daily_power ORDER BY id DESC LIMIT 1;')
    d = cur.fetchone()
    cur.execute('SELECT week,power_consumption FROM weekly_power ORDER BY id DESC LIMIT 1;')
    w = cur.fetchone()
    cur.execute('SELECT month_year,power_consumption FROM monthly_power ORDER BY id DESC LIMIT 1;')
    m = cur.fetchone()
    month = m[0] if (m) else 'Bisher kein Monat in der DB'
    mPower = m[1] if (m) else 'Bisher keine Daten in der DB'
    cur.execute('SELECT power_consumption FROM daily_power ORDER BY power_consumption DESC LIMIT 1;')
    ceiling = cur.fetchone()
    cur.close()
    conn.close()

    #check for first of month. Extrapolation doesn't work on that day.
    dayOfMonth = date.today().day

    #current month data
    cm = json.loads(apiCall(mode = 'm', dates = ((date.today()-timedelta(1)).strftime('%d.%m.%Y'))))

    #plot
    if dayOfMonth != 1:
        shortFormatDays = {elem[0][-10:-8]:elem[1] for elem in cm['result'].items()}
       
        plot = plotMonthlyOverview(shortFormatDays, math.ceil(ceiling[0]))

        shareValues = getShareValues(data = cm['result'], fullMonth = False, altLength = len(cm['result']))

        sharePlot = plotMonthlyShare(shareValues)
    else:
        pass

    

    def extrapolation(x):
        try:
            meanValue = x['preliminary_power_consumption'] / len(x['result'])
            return round(((calendar.monthrange(date.today().year, date.today().month)[1] - len(x['result'])) * meanValue), 2) + x['preliminary_power_consumption']
        except Exception:
            return 1
    
    ep = extrapolation(cm)

    # normalization of monthly power according to the number of days of both months. E.g.: February 2024 had 29 days, two less than following March. So the power consumption of February is extrapolated to 31 Days.
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
    
    normMPower = adjustMPower(mPower)

    clm = 1 - (normMPower / float(ep))

    def getCurrentMeanValue():        
        apiData = json.loads(apiCall(mode = 'm', dates = str(date.today().month), expand = True))
        numberOfDays = len(apiData['result'])

        mean = 0.0
        for day in apiData['result'].values():
            mean += day

        meanValue = mean / numberOfDays
        return round(meanValue,2)


    #save mean value to Redis. 2 days = 172800 seconds

    def saveMeanValueToRedis(url, date):
        r = redis.from_url(url)

        value = getCurrentMeanValue()

        if not r.get(date):
            r.set(name = date, value = value if dayOfMonth != 1 else None, ex = 172800)
        else:
            print (f'Mean value ({value}) for date {date} already stored. Will expire in {timedelta(seconds=r.ttl(date))}.')

        r.quit()
    
    def getMeanValueYesterdayFromRedis(url, date):
        r = redis.from_url(url)
        
        valueB = r.get(date)

        if valueB:
            value = float(valueB.decode('utf8'))
        else:
            value = None
            print (f'Could not find value for date {date} in Redis.')

        r.quit()

        return value
    
    if os.name == 'nt':
        redisUrl = 'redis://192.168.178.61:6379'
    else:
        redisUrl = 'redis://redis:6379'

    saveMeanValueToRedis(redisUrl, date.today().strftime('%d.%m.%Y'))

    #current month for title of visualization

    monthList = ['dummy', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']


    contextPower={
        'day':d[0],
        'dPower':d[1],
        'week':w[0],
        'wPower':w[1],
        'month':month,
        'mPower':mPower,
        'extrapolationCurrentMonth':'{:.2f}'.format(ep),
        'currentMeanValue': getCurrentMeanValue() if dayOfMonth != 1 else None,
        'meanValueYesterday': getMeanValueYesterdayFromRedis(redisUrl, (date.today()-timedelta(1)).strftime('%d.%m.%Y')),
        'compLastMonthPercent':round((abs(clm) * 100), 2),
        'compLastMonth':clm,
        'plot':plot if dayOfMonth != 1 else None,
        'sharePlot': sharePlot if dayOfMonth != 1 else None,
        'dayOfMonth':dayOfMonth,
        'currentMonthName': monthList[date.today().month]
    }
    return render(request, 'powerOverview.html', context = contextPower)

@cache_page(82800)
def plotPage (request):
    #different connect info in .env because of render_to_string which results in multiple quotes (""host")
    conn = psycopg.connect(os.environ.get('POSTGRES_VIEWS'))
    cur = conn.cursor()

    cur.execute('SELECT month_year FROM monthly_power;')
    range = cur.fetchall()
    cur.execute('SELECT power_consumption FROM daily_power ORDER BY power_consumption DESC LIMIT 1;')
    ceiling = cur.fetchone()
    cur.close()
    conn.close()
    range = [(elem[0], ceiling[0]) for elem in range]

    p = Pool()

    result = p.starmap(createDataForPlotPage, range)

    p.close()
        
    context = {
        'plots': result
    }
    return render(request, 'plotPage.html', context = context)

@ensure_csrf_cookie
def comparisonPage (request):
    #dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
    #different connect info in .env because of render_to_string which results in multiple quotes (""host")
    conn = psycopg.connect(os.environ.get('POSTGRES_VIEWS'))
    cur = conn.cursor()

    cur.execute('SELECT month_year FROM monthly_power;')
    global allMonths 
    allMonths = cur.fetchall()

    cur.close()
    conn.close()
    """function to get the json value for the dropdowns like this:

    var subjectObject = {
    "2023": ["Januar", "Februar", "März", "April"], 
    "2024": ["Januar", "Februar", "März"]
    }"""
    #input data like [(01.2023,), (02.2023,), (01.2024,), (02.2024,)]
    def getDropdowns (data):
        monthNames = ['dummy', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        #get all the years
        years = []
        for x in data:
            for y in x:
                monthandyear = y.split('.')
                years.append(monthandyear[1])        
        uniqueYears = list(set(years))
        #get dicts of month corresponding to the years
        dataMonthsandYears = []
        for elem in uniqueYears:
            months = []
            for e in data:
                if elem == e[0][-4:]:
                    months.append(monthNames[int(e[0][0:2])])
            dictyear = {elem: months}        
            dataMonthsandYears.append(dictyear)
        dropdowns = {}	
        for elem in dataMonthsandYears:
            dropdowns.update(elem)
        return json.dumps(dict(sorted(dropdowns.items())))
    
    dropdowns = getDropdowns(allMonths)
    
    return render(request, 'monthComparisonFrame.html', context={'dropdowns': dropdowns})

def comparisonAPI (request):
    postData = json.loads(json.loads((request.body).decode('utf-8')))
    mappingMonths = {'Januar': 1, 'Februar': 2, 'März': 3, 'April': 4, 'Mai': 5, 'Juni': 6, 'Juli': 7, 'August': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Dezember': 12}

    def getTotalConsumption(month, year):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), year = year))

        return apiData['result']['power_consumption']

    #expects month in this format: 'Februar'.
    def getMeanValue(month, year):
        numberOfDays = calendar.monthrange(int(year), mappingMonths[month])[1]
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), year = year, expand = True))
        
        mean = 0.0
        for day in apiData['result']['days'].values():
            mean += day

        meanValue = mean / numberOfDays
        return round(meanValue,2)

    def getAboveAndBelowAverage(month, year):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), year = year, expand = True))
        numberOfDays = calendar.monthrange(int(year), mappingMonths[month])[1]

        countAbove = 0
        countBelow = 0
        for elem in apiData['result']['days'].values():
            if elem >= 8.0:
                countAbove += 1
            elif elem < 6.0:
                countBelow += 1
        
        shareAbove = round((countAbove / numberOfDays * 100), 2)
        shareBelow = round((countBelow / numberOfDays * 100), 2)

        return shareAbove, shareBelow
    
    def getHighestAndLowestConsumptionDays(month, year):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), year = year, expand = True))

        highestConsumptionValue = max(apiData['result']['days'].values())
        highestConsumptionDay = list(apiData['result']['days'].keys())[list(apiData['result']['days'].values()).index(highestConsumptionValue)]

        lowestConsumptionValue = min(apiData['result']['days'].values())
        lowestConsumptionDay = list(apiData['result']['days'].keys())[list(apiData['result']['days'].values()).index(lowestConsumptionValue)]

        return highestConsumptionValue, highestConsumptionDay, lowestConsumptionValue, lowestConsumptionDay

    def getCumulativeMovingAverage(month, year):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), year = year, expand = True))
        rawData = list(apiData['result']['days'].values())
        number_series = pd.Series(rawData)
        windows = number_series.expanding(7)
        moving_averages = windows.mean()

        return moving_averages.round(2).tolist()
    
    def buildPlotDataSet(combinedPlotList, month1, month2, year1, year2):
        monthList = []
        monthList.append(month1 + ' ' + year1)
        monthList.append(month2 + ' ' + year2)
        dataSet = {}
        i = 0
        for elem in combinedPlotList:
            dataSet.update({monthList[i]: elem})
            i += 1

        return dataSet


    combinedPlotList = [] 
    
    combinedPlotList.append(getCumulativeMovingAverage(postData['month1'], postData['year1']))
    combinedPlotList.append(getCumulativeMovingAverage(postData['month2'], postData['year2']))

    context = {'month1': postData['month1'],
               'year1': postData['year1'],
               'month2': postData['month2'],
               'year2': postData['year2'],
               'totalConsumption1': getTotalConsumption(postData['month1'], postData['year1']),
               'totalConsumption2': getTotalConsumption(postData['month2'], postData['year2']),
               'meanValue1': getMeanValue(postData['month1'], postData['year1']),
               'meanValue2': getMeanValue(postData['month2'], postData['year2']),
               'shareAboveAverageMonth1': getAboveAndBelowAverage(postData['month1'], postData['year1'])[0],
               'shareAboveAverageMonth2': getAboveAndBelowAverage(postData['month2'], postData['year2'])[0],
               'shareBelowAverageMonth1': getAboveAndBelowAverage(postData['month1'], postData['year1'])[1],
               'shareBelowAverageMonth2': getAboveAndBelowAverage(postData['month2'], postData['year2'])[1],
               'testday1': getHighestAndLowestConsumptionDays(postData['month1'], postData['year1']),
               'testday2': getHighestAndLowestConsumptionDays(postData['month2'], postData['year2']),
               'plot': plotComparison(buildPlotDataSet(combinedPlotList, postData['month1'], postData['month2'], postData['year1'], postData['year2'])),
               'highestConsumptionValue1': getHighestAndLowestConsumptionDays(postData['month1'], postData['year1'])[0],
               'highestConsumptionDay1': getHighestAndLowestConsumptionDays(postData['month1'], postData['year1'])[1],
               'lowestConsumptionValue1': getHighestAndLowestConsumptionDays(postData['month1'], postData['year1'])[2],
               'lowestConsumptionDay1': getHighestAndLowestConsumptionDays(postData['month1'], postData['year1'])[3],
               'highestConsumptionValue2': getHighestAndLowestConsumptionDays(postData['month2'], postData['year2'])[0],
               'highestConsumptionDay2': getHighestAndLowestConsumptionDays(postData['month2'], postData['year2'])[1],
               'lowestConsumptionValue2': getHighestAndLowestConsumptionDays(postData['month2'], postData['year2'])[2],
               'lowestConsumptionDay2': getHighestAndLowestConsumptionDays(postData['month2'], postData['year2'])[3]
            }
    return render(request, 'monthComparisonResult.html', context=context)

def currentDayAPI(request):
    postData = json.loads(json.loads((request.body).decode('utf-8')))
    
    def getUsageUpToNow(timestamp):

        todayTS = ((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp() * 1000)
        conn = psycopg.connect(os.environ.get('POSTGRES_VIEWS'))
        cur = conn.cursor()
        #cur.execute(f'SELECT val FROM ts_string WHERE ts BETWEEN {(int(timestamp) - 300000)} AND {(int(timestamp) + 30000)} ORDER BY ABS(ts - {int(timestamp)}) ASC;')
        cur.execute(sql.SQL('SELECT val FROM ts_string WHERE ts BETWEEN ({timestamp} - 300000) AND ({timestamp} + 30000) ORDER BY ABS(ts - {timestamp}) ASC;').format(timestamp=sql.Literal(int(timestamp))))
        resultNow = cur.fetchone()
        cur.execute(f'SELECT val FROM ts_string WHERE ts BETWEEN {(todayTS - 300000)} AND {(todayTS + 30000)} ORDER BY ABS(ts - {todayTS}) ASC;')
        resultStartOfDay = cur.fetchone()
        cur.close()
        conn.close()
        
        dataNow = json.loads(resultNow[0])
        dataStartOfDay = json.loads(resultStartOfDay[0])

        usageUpToNow = dataNow['Haus']['total_in'] - dataStartOfDay['Haus']['total_in']
        print (dataNow)
        print (dataStartOfDay)
        return round(usageUpToNow, 2)

    context = {'currentDayUsage': getUsageUpToNow(postData['currentTimestamp'])}
    return render(request, 'currentDayUsageResult.html', context = context)