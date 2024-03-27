import seaborn as sns
from io import BytesIO
import base64


def renderPlot(data):
    power = [float(elem) for elem in data.values()]
    plot = sns.barplot(data=data, x = list(data.keys()), y = power)
    plot.bar_label(plot.containers[0], fontsize=6)
    plotFile = BytesIO()
    plotFigure = plot.get_figure()
    plotFigure.set_figwidth(10)
    plotFigure.savefig(plotFile, format='png')
    encodedFile = base64.b64encode(plotFile.getvalue())
    return encodedFile.decode('utf-8')

#td = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}