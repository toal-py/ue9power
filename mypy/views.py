# here, we render html

from django.http import HttpResponse
import json
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt, csrf_protect
from django.template.loader import render_to_string
from datetime import date, timedelta
import calendar
import dotenv
import psycopg
import pandas as pd
import math
import os
from django.views.decorators.cache import cache_page

from mypy.apiInternal import apiCall
from mypy.plotView import plotMonthlyOverview, plotMonthlyShare, getShareValues, plotComparison

def homeView(request):
    htmlString = "<h1>Hello World</h1><p><a href='/power'>Hier geht es zum letzten Stromverbrauch</a></p>" 
    return HttpResponse(htmlString)

@cache_page(21600)
def powerOverview (request):
    dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
    #different connect info in .env because of render_to_string which results in multiple quotes (""host")
    conn = psycopg.connect(os.environ.get('POSTGRES_VIEWS'))
    cur=conn.cursor()
    cur.execute('SELECT date,power_consumption FROM daily_power ORDER BY id DESC LIMIT 1;')
    d=cur.fetchone()
    cur.execute('SELECT week,power_consumption FROM weekly_power ORDER BY id DESC LIMIT 1;')
    w=cur.fetchone()
    cur.execute('SELECT month_year,power_consumption FROM monthly_power ORDER BY id DESC LIMIT 1;')
    m=cur.fetchone()
    month = m[0] if (m) else 'Bisher kein Monat in der DB'
    mPower = m[1] if (m) else 'Bisher keine Daten in der DB'
    cur.execute('SELECT power_consumption FROM daily_power ORDER BY power_consumption DESC LIMIT 1;')
    ceiling = cur.fetchone()
    cur.close()
    conn.close()

    #extrapolation
    cm = json.loads(apiCall(mode = 'm'))

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

    #check for first of month. Extrapolation doesn't work on that day.
    dayOfMonth = date.today().day

    #plot
    if dayOfMonth != 1:
        shortFormatDays = {elem[0][-10:-8]:elem[1] for elem in cm['result'].items()}
        
        plot = plotMonthlyOverview(shortFormatDays, math.ceil(ceiling[0]))
    else:
        pass

    #current month for title of visualization

    monthList = ['dummy', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

    contextPower={
        'day':d[0],
        'dPower':d[1],
        'week':w[0],
        'wPower':w[1],
        'month':month,
        'mPower':mPower,
        'extrapolationCurrentMonth':ep,
        'compLastMonthPercent':round((abs(clm) * 100), 2),
        'compLastMonth':clm,
        'plot':plot if dayOfMonth != 1 else None,
        'dayOfMonth':dayOfMonth,
        'currentMonthName': monthList[date.today().month]
    }
    return (HttpResponse(render_to_string('powerOverview.html', context=contextPower)))

@cache_page(82800)
def plotPage (request):
    dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
    #different connect info in .env because of render_to_string which results in multiple quotes (""host")
    conn = psycopg.connect(os.environ.get('POSTGRES_VIEWS'))
    cur = conn.cursor()

    cur.execute('SELECT month_year FROM monthly_power;')
    range = cur.fetchall()

    cur.execute('SELECT power_consumption FROM daily_power ORDER BY power_consumption DESC LIMIT 1;')
    ceiling = cur.fetchone()

    cur.close()
    conn.close()

    monthNames = ['dummy', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    plotList = []
    monthList = []
    averageUsage = []
    countRed = []
    countOrange = []
    countYellow = []
    countGreen = []
    countLightGreen = []
    sharesList = []

    #elem in this case is a single month.
    for elem in range:
        singlePlot = json.loads(apiCall(mode = 'm', dates = elem[0][-6], expand = True))

        dom = calendar.monthrange(date.today().year, int(elem[0][-6]))[1]

        shareValues = getShareValues(singlePlot, month = int(elem[0][-6]))
        sharesList.append(plotMonthlyShare(shareValues))
        #plot monthly overview
        shortFormatDays = {elem[0][-10:-8] : elem[1] for elem in singlePlot['result']['days'].items()}
        plotList.append(plotMonthlyOverview(shortFormatDays, math.ceil(ceiling[0])))

        #titles for individual month
        monthList.append(monthNames[int(elem[0][-6])])

        #average usage per month
        avg = 0.0
        for day in singlePlot['result']['days'].values():
            avg += day
        
        avgM = avg / dom
        
        averageUsage.append(round(avgM,2))

        #number of 'colored' days
        cr = 0
        co = 0
        cy = 0
        cg = 0
        clg = 0
        for elm in singlePlot['result']['days'].values():
            if elm >= 10.0:
                cr += 1
            elif elm < 10.0 and elm >= 8.0:
                co += 1
            elif elm < 8.0 and elm >= 6.0:
                cy += 1
            elif elm < 6.0 and elm >= 4.0:
                cg += 1
            else:
                clg += 1
        
        countRed.append(cr)
        countOrange.append(co)
        countYellow.append(cy)
        countGreen.append(cg)
        countLightGreen.append(clg)
        
    #one list for all variables of the template
    completeList = zip(plotList, monthList, averageUsage, countRed, countOrange, countYellow, countGreen, countLightGreen, sharesList)

    context = {
        'plots': completeList
    }
    return (HttpResponse(render_to_string('plotPage.html', context=context)))

@ensure_csrf_cookie
def comparisonPage (request):
    #get list of months from database
    dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
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

    def getTotalConsumption(month):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month])))

        return apiData['result']['power_consumption']

    #expects month in this format: 'Februar'.
    def getMeanValue(month):
        numberOfDays = calendar.monthrange(date.today().year, mappingMonths[month])[1]
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), expand = True))
        
        mean = 0.0
        for day in apiData['result']['days'].values():
            mean += day

        meanValue = mean / numberOfDays
        return round(meanValue,2)

    def getAboveAndBelowAverage(month):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), expand = True))
        numberOfDays = calendar.monthrange(date.today().year, mappingMonths[month])[1]

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
    
    def getHighestAndLowestConsumptionDays(month):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), expand = True))

        highestConsumptionValue = max(apiData['result']['days'].values())
        highestConsumptionDay = list(apiData['result']['days'].keys())[list(apiData['result']['days'].values()).index(highestConsumptionValue)]

        lowestConsumptionValue = min(apiData['result']['days'].values())
        lowestConsumptionDay = list(apiData['result']['days'].keys())[list(apiData['result']['days'].values()).index(lowestConsumptionValue)]

        return highestConsumptionValue, highestConsumptionDay, lowestConsumptionValue, lowestConsumptionDay

    def getCumulativeMovingAverage(month):
        apiData = json.loads(apiCall(mode = 'm', dates = str(mappingMonths[month]), expand = True))
        rawData = list(apiData['result']['days'].values())
        number_series = pd.Series(rawData)
        windows = number_series.expanding(7)
        moving_averages = windows.mean()

        return moving_averages.round(2).tolist()
    
    def buildPlotDataSet(combinedPlotList, month1, month2):
        monthList = []
        monthList.append(month1)
        monthList.append(month2)
        dataSet = {}
        i = 0
        for elem in combinedPlotList:
            dataSet.update({monthList[i]: elem})
            i += 1

        return dataSet


    combinedPlotList = [] 
    
    combinedPlotList.append(getCumulativeMovingAverage(postData['month1']))
    combinedPlotList.append(getCumulativeMovingAverage(postData['month2']))

    context = {'month1': postData['month1'],
               'year1': postData['year1'],
               'month2': postData['month2'],
               'year2': postData['year2'],
               'totalConsumption1': getTotalConsumption(postData['month1']),
               'totalConsumption2': getTotalConsumption(postData['month2']),
               'meanValue1': getMeanValue(postData['month1']),
               'meanValue2': getMeanValue(postData['month2']),
               'shareAboveAverageMonth1': getAboveAndBelowAverage(postData['month1'])[0],
               'shareAboveAverageMonth2': getAboveAndBelowAverage(postData['month2'])[0],
               'shareBelowAverageMonth1': getAboveAndBelowAverage(postData['month1'])[1],
               'shareBelowAverageMonth2': getAboveAndBelowAverage(postData['month2'])[1],
               'testday1': getHighestAndLowestConsumptionDays(postData['month1']),
               'testday2': getHighestAndLowestConsumptionDays(postData['month2']),
               'plot': plotComparison(buildPlotDataSet(combinedPlotList, postData['month1'], postData['month2'])),
               'highestConsumptionValue1': getHighestAndLowestConsumptionDays(postData['month1'])[0],
               'highestConsumptionDay1': getHighestAndLowestConsumptionDays(postData['month1'])[1],
               'lowestConsumptionValue1': getHighestAndLowestConsumptionDays(postData['month1'])[2],
               'lowestConsumptionDay1': getHighestAndLowestConsumptionDays(postData['month1'])[3],
               'highestConsumptionValue2': getHighestAndLowestConsumptionDays(postData['month2'])[0],
               'highestConsumptionDay2': getHighestAndLowestConsumptionDays(postData['month2'])[1],
               'lowestConsumptionValue2': getHighestAndLowestConsumptionDays(postData['month2'])[2],
               'lowestConsumptionDay2': getHighestAndLowestConsumptionDays(postData['month2'])[3]
            }
    return render(request, 'monthComparisonResult.html', context=context)