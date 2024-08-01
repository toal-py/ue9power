def createDataForPlotPage(elem, ceiling):
    import math
    import calendar
    import json
    from mypy.apiInternal import apiCall
    from mypy.plotView import plotMonthlyOverview, plotMonthlyShare, getShareValues
    monthNames = ['dummy', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    singlePlot = json.loads(apiCall(mode = 'm', dates = elem[0:2], year = elem[3:], expand = True))
    dom = calendar.monthrange(int(elem[3:]), int(elem[0:2]))[1]
    shareValues = getShareValues(data = singlePlot, month = int(elem[0:2]), year = int(elem[3:]))
    sharesList = plotMonthlyShare(shareValues)
    #plot monthly overview
    shortFormatDays = {elem[0][-10:-8] : elem[1] for elem in singlePlot['result']['days'].items()}
    plotList = plotMonthlyOverview(shortFormatDays, math.ceil(ceiling))

    #titles for individual month
    monthList = monthNames[int(elem[0:2])]

    #total usage per month

    totalUsage = singlePlot['result']['month']['power_consumption']

    #average usage per month
    avg = 0.0
    for day in singlePlot['result']['days'].values():
        avg += day
    
    avgM = avg / dom
    
    averageUsage = round(avgM,2)

    return plotList, monthList, totalUsage, averageUsage, sharesList