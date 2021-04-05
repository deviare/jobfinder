import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import sys
import os

class Mailer():
    
    def set_server(self, username, password, server, port):
        try:
            smtp=smtplib.SMTP_SSL(server, port)
            smtp.ehlo()
            smtp.login(username, password)
            
            return smtp
        except BaseException as e: 
            print(e) 
            print("[-] Error connecting to server [-]")
            sys.exit()


    def __init__(username, password, server, port, mail_path, atach_path):
        self.smtp=set_server(username, passowrd, server, port)
        self.conn = sqlite3.connect('jobs.db')
        self.mail_path=mail_path
        self.atach_path = atach_path
        self.username=username

    def get_text(self):
        with open(self.mail_path,"r") as mail:
            message=""
            lines=mail.readlines()
            for line in lines:
                message=message+line 
        return message

    def get_address(self):
        cur = self.conn.cursor()
        query = "select email from offerts where email is not null and email != 'unknown' and apply != 1;"
        emails = [  email[0] for email in cur.execute(query) ]
        return emails




    def send_mails(self):
        recivers = self.get_address()
        body = MIMEText( self.get_text() )
        file_name = os.path.basename(self.atach_path)

        with open(self.atach_path, 'rb') as f:
            atach = MIMEApplication( f.read(), Name=file_name )
        atach['Content-Disposition'] = 'atachmnent; filename="{}"'.format(file_name)
        

        msg = MIMEMultipart()
        msg['Subject'] = 'Curriculum'
        msg['From'] = self.username
        msg.attach(body)
        msg.attach(atach)

        cur = self.conn.cursor()
        query_update = 'update offerts set apply = 1 where email = ?;'

        for dest in recivers:
            msg['To'] = dest
            self.smpt.sendmail(sent_from, dest, msg.as_string())
            cur.execute(query_update, dest)


        self.smtp.close()
        self.conn.close()
