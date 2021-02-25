import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication





class Mailer():
    def set_server(self, username, password, server, port):
        try:
            smtp=smtplib.SMTP_SSL(server, int(port))
            smtp.ehlo()
            smtp.login(username, password)
            
            return smtp
        except BaseException as e: 
            print("[-] Error connecting to server [-]")
            sys.exit()

    def __init__(self, username, password, server, port, mail_path, atch_path):
        self.smtp=self.set_server(username, password, server, port)
        self.mail_path=mail_path
        self.atch_path=atch_path
        self.username=username

    def get_text(self):
        with open(self.mail_path,"r") as mail:
            lines=mail.readlines()
        return lines

    def get_address(self):
            
        try:
            with open('../emails.txt', 'r') as inp:
                with open('emails_sended,txt', 'a') as out:
                    for line in inp:
                        out.write(line)

        except IOError:
            pass

        with open("../emails.txt", "r") as f:
            to_addrs=f.readlines()
        return to_addrs

    def send_mails(self):
        msg=MIMEMultipart()
        body=MIMEText(self.get_text())
        recivers=self.get_address()
        msg['Subject']='Curriculum'
        msg['From']=self.username

        with open(self.atch_path, 'rb') as f:
            atch=MIMEApplication(f.read(), Name=os.path.basename(cv))
        atch['Content-Disposition']='attachment; filename="{}"'.format(os.path.basename(cv))

        msg.attach(body)
        msg.attach(atch)

        for dest in recivers:
            msg['To']=dest
            self.smtp.sendmail(self.username, dest, msg.as_string())

        self.smtp.close()
        pritn('[+] Email sent to every address in emails.txt [+]') 
