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
    plotFigure = plt.figure()
    dframe = pd.DataFrame(data, index = [0])
    dframe.cumsum(axis=1)
    sns.barplot(data = dframe, x = 'red', y = 'red', hue = 'red', estimator = 'sum', color = sns.color_palette("Set2", 10)[0]) 
    sns.barplot(data = dframe, x = 'yellow', y = 'yellow', hue = 'red', estimator = 'sum', color=sns.color_palette("Set2", 10)[1])
    #sns.barplot(data = dframe, x = 100, hue = 100, estimator = 'sum', color=sns.color_palette("Set2", 10)[2])      
    plotFile = BytesIO()    
    plotFigure.savefig(plotFile, format='png')
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')
    

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}