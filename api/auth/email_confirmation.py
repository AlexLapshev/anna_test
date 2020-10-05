import smtplib
import os

from loguru import logger

from api.auth.jwt_work import create_access_token

SENDER = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

message = """From: From company <ANNA>
To: To Person <{}>
Subject: [ANNA confirm email] Please confirm your email address

http://0.0.0.0:1984/api/v1/users/confirm/{}
"""


def connect_to_server() -> smtplib.SMTP:
    logger.debug(f'connecting to smpt server with e: {SENDER}, p: {SENDER_PASSWORD}')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(SENDER, SENDER_PASSWORD)
    return server


def send_email_confirm(email: str) -> None:
    logger.debug('sending email')
    hashed_email = create_access_token({'email': email})
    server = connect_to_server()
    server.sendmail(SENDER, email, message.format(email, hashed_email))
    server.close()
