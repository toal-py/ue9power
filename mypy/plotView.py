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
    colorPal = ['tab:green', 'tab:orange', 'tab:red']
    counter = 0
    plotFigure = plt.figure()
    for bar in data.items():
        dframe = pd.DataFrame({bar[0]: bar[1]}, index=[0])
        sns.barplot(data = dframe, x = bar[1], hue = bar[0], color = colorPal[counter])
        counter += 1
    plotFile = BytesIO()    
    plotFigure.savefig(plotFile, format='png')
    plotFile.seek(0)
    encodedFile = base64.b64encode(plotFile.getbuffer())
    plotFile.close()
    return encodedFile.decode('utf-8')
    

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}