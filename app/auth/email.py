from flask_mail import Message
from flask import render_template, current_app
from app import mail
from threading import Thread

def sendEmail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def sendPasswordResetEmail(user):
    token = user.get_reset_password_token()
    sendEmail("[Microblog] Reset Your Password",
              sender=current_app.config["ADMINS"][0],
              recipients=[user.email],
              text_body=render_template("reset_password_message.txt", user=user, token=token),
              html_body=render_template("reset_password_message.html", user=user, token=token))

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)