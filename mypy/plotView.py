import seaborn as sns
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd


def plotMonthlyOverview(data):
    colorPal = ['red' if elem > 9.0 else 'orange' if elem >= 5.0 else 'green' for elem in data.values()]
    power = [float(elem) for elem in data.values()]
    plotFigure = plt.figure()
    plot = sns.barplot(data=data, x = list(data.keys()), y = power, palette=colorPal, saturation=0.75, hue=list(data.keys()), legend=False)    
    for bar in plot.containers:
        plot.bar_label(bar, fontsize=8)
    plotFile = BytesIO()
    plotFigure.set_figwidth(10)    
    plotFigure.savefig(plotFile, format='png')
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')

def plotMonthlyShare(data):
    plotFigure = plt.figure()
    percentageData = {'green': data['green'], 'orange': (sum(data.values()) - data['red']), 'red': sum(data.values())}
    dframe = pd.DataFrame(percentageData, index = [0])

    bar1 = sns.barplot(data = dframe, x = 'red', y = 'red', hue = 'red', orient = 'h', width = 0.4, palette = ['tab:red'], legend = False)
    bar1.set(yticklabels=[])
    bar1.set(ylabel=None)
    bar1.tick_params(left=False)
    bar1.set(xlabel=None)
    for bar in bar1.containers:
        bar1.bar_label(bar, fmt = f'{data['red']}', label_type = 'center')
    
    bar2 = sns.barplot(data = dframe, x = 'orange', y = 'red', hue = 'orange', orient = 'h', width = 0.4, palette = ['tab:orange'], legend = False)
    bar2.set(yticklabels=[])
    bar2.set(ylabel=None)
    bar2.tick_params(left=False)
    bar2.set(xlabel=None)       
    
    bar3 = sns.barplot(data = dframe, x = 'green', y = 'red', hue = 'green', orient = 'h', width = 0.4, palette = ['tab:green'], legend = False)
    bar3.set(yticklabels=[])
    bar3.set(ylabel=None)
    bar3.tick_params(left=False)
    bar3.set(xlabel=None)     
    
    plotFile = BytesIO()
    plotFigure.set_figheight(2.0)
    plotFigure.set_figwidth(10)    
    plotFigure.savefig(plotFile, format='png')
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')
    

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}