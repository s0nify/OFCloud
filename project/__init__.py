#!/usr/bin/env python
# init.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from flask_mail import Mail
from flask_recaptcha import ReCaptcha
from flask_caching import Cache
import logging
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
mail = Mail()
recaptcha = ReCaptcha()
cache = Cache()

class Config:
    DEBUG = True
    MAIL_SERVER = 'fapbox.cloud'
    MAIL_PORT = 25
    MAIL_USERNAME = 'no-reply@fapbox.cloud'
    MAIL_PASSWORD = 'iAfXE7JeFh'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = 'no-reply@fapbox.cloud'
    SECRET_KEY = 'Njnh#a+:KY5k3D03kv~GWY|?`%+dtGO:bm3[rWwsCrS phQ9,q6UrQ(Ar? ;Ok3Z'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = 'pizdaizhopa'
    RECAPTCHA_ENABLED = True
    RECAPTCHA_SITE_KEY = "6LdoOoIaAAAAALid0RSuJ1Mauhp-6pkj5_DWnXDo"
    RECAPTCHA_SECRET_KEY = "6LdoOoIaAAAAABXXAIqSciBicwECpRqN-hNeyO_h"
    RECAPTCHA_TYPE = "image"
    RECAPTCHA_RTABINDEX = 10
    STATIC_CDN_BACKEND = "//cdn.fapbox.cloud"
    CACHE_TYPE = "SimpleCache"  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 300


def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    mail.init_app(app)
    db.init_app(app)
    recaptcha.init_app(app)
    cache.init_app(app)

    login_manager = LoginManager()
    ## Понять как сюда подставлять суффикс правильным образом
    login_manager.login_view = '/user/login'
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from . import auth
    app.register_blueprint(auth.auth, url_prefix="/user")

    # Страницы с контентом
    from .content.content import content as content
    app.register_blueprint(content)

    # Защита страниц с авторизацией и логином
    csrf = CSRFProtect(app)

    # Кэш
    cache.init_app(app)
    return app

if __name__ != '__main__':
    app = create_app()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':

    create_app()
