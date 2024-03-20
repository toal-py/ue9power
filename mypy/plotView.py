import seaborn as sns
from io import BytesIO
import base64

def renderPlot(data):
    power = [float(elem) for elem in data.values()]
    plot = sns.barplot(x = list(data.keys()), y = power)
    plot_file = BytesIO()
    plot.savefig(plot_file, format='png')
    encoded_file = base64.b64encode(plot_file.getvalue())
    return encoded_file

#test_dict = {'22.01.2024': 6.55, '23.01.2024': 4.75, '24.01.2024': 11.92}