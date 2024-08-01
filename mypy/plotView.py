import seaborn as sns
from io import BytesIO
import base64
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import calendar
from datetime import date


def plotMonthlyOverview(data, ceiling):
    matplotlib.use('agg')
    colorPal = ['tab:red' if elem >= 10.0 else 'tab:orange' if elem >= 8.0 else 'yellow' if elem >= 6.0 else 'tab:green' if elem >= 4.0 else 'lightgreen' for elem in data.values()]
    power = [float(elem) for elem in data.values()]
    plotFigure = plt.figure()

    sns.set_style('darkgrid')

    plot = sns.barplot(data=data, x = list(data.keys()), y = power, palette=colorPal, saturation=0.75, hue=list(data.keys()), legend=False)

    plt.ylim(0, ceiling)

    for bar in plot.containers:
        plot.bar_label(bar, fontsize=8)
    plotFile = BytesIO()
    plotFigure.set_figwidth(10)    
    plotFigure.savefig(plotFile, format='png', bbox_inches='tight')
    plt.close(plotFigure)
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')

def plotMonthlyShare(data):
    matplotlib.use('agg')
    plotFigure = plt.figure()
    percentageData = {'lightGreen': data['lightGreen'],
                      'green': data['green'] + data['lightGreen'],
                      'yellow': (sum(data.values()) - data['red'] - data['orange']), 
                      'orange': (sum(data.values()) - data['red']), 
                      'red': sum(data.values())}
    dframe = pd.DataFrame(percentageData, index = [0])

    sns.set_style('darkgrid')

    bar1 = sns.barplot(data = dframe, x = 'red', y = 'red', hue = 'red', orient = 'h', width = 0.4, palette = ['tab:red'], legend = False, label = f'{data['red']}%')
    bar1.set(yticklabels=[])
    bar1.set(ylabel=None)
    bar1.tick_params(left=False)
    bar1.set(xlabel=None)
    
    bar2 = sns.barplot(data = dframe, x = 'orange', y = 'red', hue = 'orange', orient = 'h', width = 0.4, palette = ['tab:orange'], legend = False, label = f'{data['orange']}%')
    bar2.set(yticklabels=[])
    bar2.set(ylabel=None)
    bar2.tick_params(left=False)
    bar2.set(xlabel=None)

    bar3 = sns.barplot(data = dframe, x = 'yellow', y = 'red', hue = 'yellow', orient = 'h', width = 0.4, palette = ['yellow'], legend = False, label = f'{data['yellow']}%')
    bar3.set(yticklabels=[])
    bar3.set(ylabel=None)
    bar3.tick_params(left=False)
    bar3.set(xlabel=None)

    bar4 = sns.barplot(data = dframe, x = 'green', y = 'red', hue = 'green', orient = 'h', width = 0.4, palette = ['tab:green'], legend = False, label = f'{data['green']}%')
    bar4.set(yticklabels=[])
    bar4.set(ylabel=None)
    bar4.tick_params(left=False)
    bar4.set(xlabel=None)
    
    bar5 = sns.barplot(data = dframe, x = 'lightGreen', y = 'red', hue = 'lightGreen', orient = 'h', width = 0.4, palette = ['lightgreen'], legend = False, label = f'{data['lightGreen']}%')
    bar5.set(yticklabels=[])
    bar5.set(ylabel=None)
    bar5.tick_params(left=False)
    bar5.set(xlabel=None)

    plt.xlim(0, 100)   

    plt.figlegend(loc = 'upper center', ncol = len(percentageData), reverse = True)

    plotFile = BytesIO()
    plotFigure.set_figheight(2.0)
    plotFigure.set_figwidth(10)    
    plotFigure.savefig(plotFile, format='png', bbox_inches='tight')
    plt.close(plotFigure)
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')

#get share of green, orange or red days. Input is the result of an API call like this: data = json.loads(apiCall(mode='m', dates='2', expand=True))
def getShareValues(data, month = None, year = None, fullMonth = True, altLength = None):
    countRed = []
    countOrange = []
    countYellow = []
    countGreen = []
    countLightGreen = []
        
    if fullMonth:

        for elem in data['result']['days'].values():
            if elem >= 10.0:
                countRed.append(elem)
            elif elem < 10.0 and elem >= 8.0:
                countOrange.append(elem)
            elif elem < 8.0 and elem >= 6.0:
                countYellow.append(elem)
            elif elem < 6.0 and elem >= 4.0:
                countGreen.append(elem)
            else:
                countLightGreen.append(elem)
        
        daysOfMonth = calendar.monthrange(year, month)[1]
        shares = {'lightGreen': round(((len(countLightGreen) / daysOfMonth) * 100), 2), 
                'green': round(((len(countGreen) / daysOfMonth) * 100), 2), 
                'yellow': round(((len(countYellow) / daysOfMonth) * 100), 2), 
                'orange': round(((len(countOrange) / daysOfMonth) * 100), 2), 
                'red': round(((len(countRed) / daysOfMonth) * 100), 2)}
    else:
        for elem in data.values():
            if elem >= 10.0:
                countRed.append(elem)
            elif elem < 10.0 and elem >= 8.0:
                countOrange.append(elem)
            elif elem < 8.0 and elem >= 6.0:
                countYellow.append(elem)
            elif elem < 6.0 and elem >= 4.0:
                countGreen.append(elem)
            else:
                countLightGreen.append(elem)
        
        shares = {'lightGreen': round(((len(countLightGreen) / altLength) * 100), 2), 
                'green': round(((len(countGreen) / altLength) * 100), 2), 
                'yellow': round(((len(countYellow) / altLength) * 100), 2), 
                'orange': round(((len(countOrange) / altLength) * 100), 2), 
                'red': round(((len(countRed) / altLength) * 100), 2)}
    
    return shares
    
def plotComparison(data):
    matplotlib.use('agg')
    plotFigure = plt.figure()
    
    sns.set_style('darkgrid')
    sns.lineplot(data = data, palette = ['lightsalmon', 'lightsteelblue'], markers = False, dashes = False)#.set(yticklabels = [], xticklabels = [])
    #plt.ylim(5, 8)

    plotFigure.set_figwidth(10)
    plotFile = BytesIO()   
    plotFigure.savefig(plotFile, format='png', bbox_inches='tight')
    plt.close(plotFigure)
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')

#CURRENTLY NOT IN USE
def plotLast4Weeks(data):
    plotFigure = plt.figure()
    
    sns.set_style('darkgrid')
    sns.lineplot(data = data, palette = ['lightsteelblue'], markers = True, dashes = False, legend = True)
    #plt.ylim(5, 8)

    plotFigure.set_figwidth(10)
    plotFile = BytesIO()   
    plotFigure.savefig(plotFile, format='png', bbox_inches='tight')
    plt.close(plotFigure)
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}