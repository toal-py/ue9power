from datetime import datetime
import psycopg
from psycopg import sql
import requests

try:
    response = requests.get('https://web.toal.wtf')
    if response.status_code == 200:
        pass
    elif response.status_code != 200:
        description = f'HTTP error: {response.status_code}'
except Exception as e:
    type = 'connection'
    description = ''
    degree = 400
    time = datetime.now().isoformat(sep=" ", timespec="seconds")


dates = '12.02.2024'
print((sql.SQL('SELECT date,power_consumption,comment FROM daily_power WHERE date = {dates};').format(dates=sql.Literal(dates))))