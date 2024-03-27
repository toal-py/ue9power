from datetime import datetime
import psycopg
import requests
import os
import sys
import dotenv

dotenv.read_dotenv('/var/www/python-project/ue9power/.env')
sys.path.append('/var/www/python-project/ue9power/mypy/power')

import cClasses

try:
    response = requests.get('https://web.toal.wtf')

except ConnectionError as e:
    queryObj = cClasses.errorLog('connection', f'{e}', 400, datetime.now().isoformat(sep=" ", timespec="seconds"))
    query = queryObj.log()

    conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'))
    cur = conn.cursor()

    cur.execute(query)
    conn.commit()

    cur.close()
    conn.close()
    
