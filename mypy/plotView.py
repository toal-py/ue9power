import seaborn as sns
from io import BytesIO
import base64
import matplotlib.pyplot as plt
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
    colorPal = {'green': '#74c69d','yellow': '#f48c06','red': '#d00000'}
    fig, ax = plt.subplots()
    sns.barplot(data = pd.DataFrame({'red': [sum(data.values())]}, index = [0]), x = 100, palette = 'dark:red')
    sns.barplot(data = pd.DataFrame({'yellow': [sum(data.values()) - data['red']]}, index = [0]), x = 100, palette = 'dark:yellow')
    sns.barplot(data = pd.DataFrame({'green': [data['green']]}, index = 0), x = 100, palette = 'dark:green')
    plotFile = BytesIO()
    fig.savefig(plotFile, format='png')
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')
    

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}