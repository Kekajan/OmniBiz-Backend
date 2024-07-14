import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailService:
    @staticmethod
    def send_email(subject, body, receiver):
        sender = os.getenv('APP_EMAIL')
        password = os.getenv('APP_EMAIL_PASSWORD')
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = receiver
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message.as_string())
