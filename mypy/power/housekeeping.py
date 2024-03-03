import psycopg
from datetime import datetime
import cClasses
import os
import dotenv

dotenv.read_dotenv('/var/www/python-project/ue9power/.env')

#connection & cursor
conn = psycopg.connect(os.environ.get('POSTGRES_CONNECT_DB_POWER'))
cur = conn.cursor()

#timestamps to determine which entries to delete: all entries older than two weeks
twoWeeksUnix = 1209600
currentTs = int(datetime.now().timestamp())

deleteQuery = f'DELETE FROM ts_string WHERE ts < {(currentTs-twoWeeksUnix)*1000};'
cur.execute(deleteQuery)

#get count of deleted rows and send them via e-mail
rowsDeleted = cur.rowcount
mailContent = f'Housekeeping successfully deleted {rowsDeleted} rows.'
mailSubject = 'Result Housekeeping'
notification = cClasses.mailing(mailContent, mailSubject)
notification.sendMail()

conn.commit()

#delete all content in logValues.txt
with open('logValues.txt', 'w') as f:
    pass

cur.close()
conn.close()