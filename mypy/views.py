# here, we render html

from django.http import HttpResponse
import requests
import json
from django.template.loader import render_to_string
from datetime import datetime, date, timedelta
import calendar
import dotenv
import psycopg
import os
from django.views.decorators.cache import cache_page

from mypy.apiInternal import apiCall
from mypy.plotView import renderPlot

def homeView(request):
    htmlString = "<h1>Hello World</h1><p><a href='/power'>Hier geht es zum letzten Stromverbrauch</a></p><p><a href='/current-weather'>Hier geht es zur aktuellen Temperatur</a></p><p><a href='/preg'>Hier geht es zum Schwangerschaftsüberblick</a></p>" 
    return HttpResponse(htmlString)

# GET current weather

def getCurrentWeather(request):
    id = os.environ.get('WEATHER_API_ID')
    currentWeatherRaw = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat=51.3482056&lon=7.1160019&appid={id}&units=metric&lang=de')
    currentWeather = currentWeatherRaw.json()
    htmlOutput = (f"<p>Es sind gerade: {str(currentWeather['main']['temp']).replace('.', ',')}°C</p><p><a href='/'>Zurück</a></p>")
    return HttpResponse(htmlOutput)

def site_pregOverview(request):

    # calculation of pregnancy week
    startPregnancy = date(2023, 8, 11)
    now = date.today()
    delta = now - startPregnancy

    def weeks(x):
        weeks = x.days / 7
        days = x.days % 7
        return (f"Wir sind in der {int(weeks) + 1}. Woche, genauer gesagt bei {int(weeks)} + {days}.")
    
    progressDelta = weeks(delta)

    # countdown to birth
    calcBirth = date(2024, 5, 17)
    timeToBirth = calcBirth - now
    

    context_preg = {
        "pregProgress": progressDelta,
        "countdown": timeToBirth.days
    } 
    pregOverview = render_to_string('preg_overview.html', context=context_preg)
    return HttpResponse(pregOverview)

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
    cur.close()
    conn.close()

    #extrapolation
    cm = json.loads(apiCall(mode = 'm'))

    def extrapolation(x):
        try:
            meanValue = x['preliminary_power_consumption'] / len(x['result'])
            return round(((calendar.monthrange(date.today().year, date.today().month)[1] - len(x['result'])) * meanValue), 2) + x['preliminary_power_consumption']
        except Exception:
            return 0
    
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
    
    normMPower = adjustMPower(mPower)

    clm = 1 - (normMPower / float(ep))

    #check for first of month. Extrapolation doesn't work on that day.
    dayOfMonth = date.today().day

    #plot
    shortFormatDays = {elem[0][-10:-8]:elem[1] for elem in cm['result'].items()}
    
    plot = renderPlot(shortFormatDays)

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
        'plot':plot,
        'dayOfMonth':dayOfMonth,
        'currentMonthName': monthList[date.today().month]
    }
    return (HttpResponse(render_to_string('powerOverview.html', context=contextPower)))

def powerApiDoc (request):
    return (HttpResponse(render_to_string('powerApiDoc.html')))