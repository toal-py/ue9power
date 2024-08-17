import requests
import dotenv
import os
import sys

sys.path.append('/var/www/python-project/ue9power/mypy/power')
dotenv.read_dotenv('/var/www/python-project/ue9power/.env')

import cClasses

def getCurrentIPv6():
    try:
        return requests.get('https://api6.ipify.org', timeout=5).text
    except requests.exceptions.ConnectionError:
        return None

def updateIPv6(ipv6,token):
    if ipv6 is not None:
        r = requests.get(f'https://dynv6.com/api/update?hostname=web.toal.wtf&token={token}&ipv6={ipv6}')
        print ('Success!')
        if r.status_code != 200:
            errMessage = f'Could\'nt update IPv6 address. \n HTTP Error Code: {r.status_code}. \n Error Message: {r.text}.'
            errSubject = 'Error: Could\'nt update IPv6 address'
            err = cClasses.mailing(errMessage,errSubject)
            err.sendMail()
            print (f'That didn\'t work. \n HTTP Error Code: {r.status_code}. \n Error Message: {r.text}.')
    else:
        errMessage = 'Could\'nt update IPv6 address. No connection to online service.'
        errSubject = 'Error: Could\'nt update IPv6 address'    
        err = cClasses.mailing(errMessage,errSubject)
        err.sendMail()
        print (f'That didn\'t work. {errMessage}')

updateIPv6(getCurrentIPv6(),os.environ.get('DYNV6_TOKEN'))