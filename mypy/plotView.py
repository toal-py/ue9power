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
    #dframe.cumsum(axis=1)
    sns.barplot(data = dframe, x = 'red', y = 'red', hue = 'red', orient = 'h', palette = ['tab:red'])
    sns.barplot(data = dframe, x = 'orange', y = 'red', hue = 'orange', orient = 'h', palette = ['tab:orange'])       
    sns.barplot(data = dframe, x = 'green', y = 'red', hue = 'green', orient = 'h', palette = ['tab:green'])      
    plotFile = BytesIO()
    plotFigure.set_figheight(3.5)
    plotFigure.set_figwidth(10)    
    plotFigure.savefig(plotFile, format='png')
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')
    

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}