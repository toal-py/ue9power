import seaborn as sns
from io import BytesIO
import base64


def renderPlot(data):
    colorPal = ['red' if elem > 9.0 else 'orange' if elem >= 5.0 else 'green' for elem in data.values()]
    power = [float(elem) for elem in data.values()]
    plot = sns.barplot(data=data, x = list(data.keys()), y = power, palette=colorPal)
    plot.bar_label(plot.containers[0], fontsize=8)
    plotFile = BytesIO()
    plotFigure = plot.get_figure()
    plotFigure.set_figwidth(10)
    plotFigure.savefig(plotFile, format='png')
    encodedFile = base64.b64encode(plotFile.getvalue())
    return encodedFile.decode('utf-8')

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}