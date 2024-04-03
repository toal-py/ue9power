import seaborn as sns
from io import BytesIO
import base64
from PIL import Image


def renderPlot(data):
    colorPal = ['red' if elem > 9.0 else 'orange' if elem >= 5.0 else 'green' for elem in data.values()]
    power = [float(elem) for elem in data.values()]
    plot = sns.barplot(data=data, x = list(data.keys()), y = power, palette=colorPal, saturation=0.75, hue=list(data.keys()), legend=False)    
    for bar in plot.containers:
        plot.bar_label(bar, fontsize=8)
    plotFile = BytesIO()
    plotFigure = plot.get_figure()
    plotFigure.set_figwidth(10)
    plotFigure.savefig(plotFile, format='png')
    plotFile.seek(0)
    img = Image.open(plotFile)
    encodedFile = base64.b64encode(img)
    return encodedFile
    

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}