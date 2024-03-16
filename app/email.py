from threading import Thread
from typing import List

from flask import render_template
from flask_mail import Message

from . import flask_app, mail
from .models import PasswordResetTokens, User


def _send_async_email(app, msg: Message):
    with app.app_context():
        mail.send(msg)


def send_password_reset_email(user: User):
    token = PasswordResetTokens.generate(user = user, expires_in = 600)

    email = Message(
        '[Microblog] Reset Your Password',
        sender = flask_app.config['ADMINS'][0],
        recipients = [user.email],
        body = render_template('email/reset_password.txt.j2', user=user, token=token),
        html = render_template('email/reset_password.html.j2', user=user, token=token)
    )
    Thread(target=_send_async_email, args=(flask_app, email)).start()
