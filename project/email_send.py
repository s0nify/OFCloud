from flask_mail import Message, Mail
from flask import Flask
from . import Config, mail

app = Flask(__name__)

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=Config.MAIL_DEFAULT_SENDER
    )
    mail.send(msg)
