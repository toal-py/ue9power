import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg
from psycopg import sql
import os
import dotenv

dotenv.read_dotenv('/var/www/python-project/ue9power/.env')

class logging:
    def __init__(self, absTD, absYD, origTD, origYD, refDate):
        self.absTD = absTD
        self.absYD = absYD
        self.origTD = origTD
        self.origYD = origYD
        self.refDate = refDate
        
    def writeLogFile(self):
        with open('logValues.txt', 'a') as f:
            f.write(f"Day: {self.refDate}\n\nAbsolute value YD: {self.absYD}\nAbsolute value TD: {self.absTD}\n\nOriginal value YD: {self.origYD}\nOriginal value TD: {self.origTD}\n\n")

class mailing:

    login = 'log@toal.wtf'
    password = os.environ.get('MAILING_PASSWORD')
    sender = 'log@toal.wtf'

    def __init__(self, messageContent, subjectContent, receiver='albertztobias@web.de'):
        self.messageContent = messageContent
        self.subjectContent = subjectContent
        self.receiver = receiver
        
    def sendMail(self):
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subjectContent
        message["From"] = self.sender
        message["To"] = self.receiver
        message.attach(MIMEText(self.messageContent, 'html'))
        with smtplib.SMTP_SSL("smtp.strato.de", 465) as server:
            server.login(self.login, self.password)
            server.sendmail(self.sender, self.receiver, message.as_string())

class error_log:

    def __init__(self, type, description, level, time):
        self.type = type
        self.description = description
        self.level = level
        self.time = time

    def log(self):
        query = (sql.SQL('INSERT INTO error_log (type, description, level, time) VALUES ({type}, {description}, {level}, {time}) ;').format(
            type = sql.Literal(self.type), 
            description = sql.Literal(self.description), 
            level = sql.Literal(self.level),
            time = sql.Literal(self.time)
            )
        )
        return query