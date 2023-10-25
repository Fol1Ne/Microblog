from app import cli
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel
from elasticsearch import Elasticsearch
import logging
import os


bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
moment = Moment()
babel = Babel()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = "Please log in to access this page."


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    app.elasticsearch = Elasticsearch([app.config["ELASTICSEARCH_URL"]]) \
        if app.config["ELASTICSEARCH_URL"] else None

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp, url_prefix="/errors")

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix="/main")

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL.PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_hander = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMINS"], subject="Microblog Failure",
                credentials=auth, secure=secure)
            mail_hander.setLevel(logging.ERROR)
            app.logger.addHandler(mail_hander)

        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_hander = RotatingFileHandler("logs/microblog.log", maxBytes=10240, backupCount=10)
        file_hander.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
        app.logger.addHandler(file_hander)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Microblog startup")

    return app

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': models.User, 'Post': models.Post, 'Message': models.Message, 'Notification': models.Notification}

@babel.localeselector()
def get_locale():
    return request.accept_languages.best_match(app.config["LANGUAGES"])

from app import models