# init.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
mail = Mail()


class Config:
    DEBUG = True
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '23e6ab069203c2'
    MAIL_PASSWORD = 'fdc75497d1430e'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = 'from@example.com'
    SECRET_KEY = '9OLWxND4o83j4K4iuopO'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SECURITY_PASSWORD_SALT = 'pizdaizhopa'


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)
    db.init_app(app)

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
    return app


if __name__ == '__main__':
    create_app()
